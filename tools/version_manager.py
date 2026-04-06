"""版本存档与回滚工具 - 管理案件文件的版本历史。

支持对案件文件进行版本备份、历史版本列表查看和回滚操作。
保留最近 10 个版本，自动清理更早的版本。

Usage:
    python3 tools/version_manager.py --action backup --slug my-case --base-dir ./cases
    python3 tools/version_manager.py --action list --slug my-case --base-dir ./cases
    python3 tools/version_manager.py --action rollback --slug my-case --version v1 --base-dir ./cases
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone


MAX_VERSIONS = 10

BACKUP_FILES = ["case.md", "strategy.md", "emotion_timeline.md", "meta.json"]


def error_exit(message: str) -> None:
    """输出 JSON 错误信息到 stderr 并退出。"""
    json.dump({"error": message}, sys.stderr, ensure_ascii=False)
    sys.stderr.write("\n")
    sys.exit(1)


def output_json(data: object) -> None:
    """输出 JSON 到 stdout。"""
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def now_iso() -> str:
    """返回当前 ISO 格式时间字符串。"""
    return datetime.now(timezone.utc).isoformat()


def get_case_dir(slug: str, base_dir: str) -> str:
    """获取案件目录路径并验证其存在。"""
    case_dir = os.path.join(base_dir, slug)
    if not os.path.isdir(case_dir):
        error_exit(f"Case directory not found: {case_dir}")
    return case_dir


def load_meta(case_dir: str) -> dict:
    """读取案件 meta.json。"""
    meta_path = os.path.join(case_dir, "meta.json")
    if not os.path.isfile(meta_path):
        error_exit(f"meta.json not found in {case_dir}")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_meta(case_dir: str, meta: dict) -> None:
    """写入 meta.json。"""
    meta_path = os.path.join(case_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")


def parse_version_num(version: str) -> int:
    """从版本号字符串中提取数字（如 'v3' -> 3）。"""
    m = re.match(r"v(\d+)", version)
    if not m:
        error_exit(f"Invalid version format: {version}, expected 'vN'")
    return int(m.group(1))


def action_backup(slug: str, base_dir: str) -> None:
    """备份当前案件文件到版本目录。"""
    case_dir = get_case_dir(slug, base_dir)
    meta = load_meta(case_dir)
    current_version = meta.get("version", "v1")

    # 创建版本目录
    versions_dir = os.path.join(case_dir, "versions")
    version_dir = os.path.join(versions_dir, current_version)
    os.makedirs(version_dir, exist_ok=True)

    # 复制存在的文件
    backed_up = []
    for filename in BACKUP_FILES:
        src = os.path.join(case_dir, filename)
        if os.path.isfile(src):
            dst = os.path.join(version_dir, filename)
            shutil.copy2(src, dst)
            backed_up.append(filename)

    # 更新 meta.json 版本号
    current_num = parse_version_num(current_version)
    new_version = f"v{current_num + 1}"
    meta["version"] = new_version
    meta["updated_at"] = now_iso()
    save_meta(case_dir, meta)

    # 清理旧版本，保留最近 MAX_VERSIONS 个
    _cleanup_old_versions(versions_dir)

    output_json({
        "status": "backed_up",
        "version": current_version,
        "files": backed_up,
    })


def _cleanup_old_versions(versions_dir: str) -> None:
    """保留最近 MAX_VERSIONS 个版本，删除更早的。"""
    if not os.path.isdir(versions_dir):
        return

    entries = []
    for name in os.listdir(versions_dir):
        path = os.path.join(versions_dir, name)
        if os.path.isdir(path) and re.match(r"v\d+", name):
            mtime = os.path.getmtime(path)
            entries.append((name, path, mtime))

    if len(entries) <= MAX_VERSIONS:
        return

    # 按修改时间排序，删除最旧的
    entries.sort(key=lambda x: x[2])
    to_delete = entries[: len(entries) - MAX_VERSIONS]
    for name, path, _ in to_delete:
        shutil.rmtree(path, ignore_errors=True)


def action_list(slug: str, base_dir: str) -> None:
    """列出所有历史版本。"""
    case_dir = get_case_dir(slug, base_dir)
    versions_dir = os.path.join(case_dir, "versions")

    if not os.path.isdir(versions_dir):
        output_json([])
        return

    versions = []
    for name in os.listdir(versions_dir):
        path = os.path.join(versions_dir, name)
        if os.path.isdir(path) and re.match(r"v\d+", name):
            mtime = os.path.getmtime(path)
            files = [
                f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
            ]
            versions.append({
                "version": name,
                "files": files,
                "timestamp": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
            })

    versions.sort(key=lambda x: x["timestamp"])
    output_json(versions)


def action_rollback(slug: str, version: str, base_dir: str) -> None:
    """回滚到指定版本。"""
    if not version:
        error_exit("--version is required for rollback action")

    case_dir = get_case_dir(slug, base_dir)
    versions_dir = os.path.join(case_dir, "versions")
    version_dir = os.path.join(versions_dir, version)

    if not os.path.isdir(version_dir):
        error_exit(f"Version directory not found: {version_dir}")

    # 恢复版本目录中的文件到主目录
    restored = []
    for filename in os.listdir(version_dir):
        src = os.path.join(version_dir, filename)
        if os.path.isfile(src):
            dst = os.path.join(case_dir, filename)
            shutil.copy2(src, dst)
            restored.append(filename)

    # 更新 meta.json
    meta = load_meta(case_dir)
    meta["version"] = version
    meta["updated_at"] = now_iso()
    save_meta(case_dir, meta)

    output_json({
        "status": "rolled_back",
        "version": version,
        "files": restored,
    })


def main() -> None:
    parser = argparse.ArgumentParser(
        description="版本存档与回滚工具 - 管理案件文件的版本历史"
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["backup", "list", "rollback"],
        help="操作类型：backup(备份), list(列出版本), rollback(回滚)",
    )
    parser.add_argument("--slug", required=True, help="案件标识符")
    parser.add_argument("--version", help="目标版本号（rollback 操作必需）")
    parser.add_argument("--base-dir", default="./cases", help="案件根目录（默认: ./cases）")

    args = parser.parse_args()

    try:
        if args.action == "backup":
            action_backup(args.slug, args.base_dir)
        elif args.action == "list":
            action_list(args.slug, args.base_dir)
        elif args.action == "rollback":
            action_rollback(args.slug, args.version, args.base_dir)
    except SystemExit:
        raise
    except Exception as e:
        error_exit(str(e))


if __name__ == "__main__":
    main()
