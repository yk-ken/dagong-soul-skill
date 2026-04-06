"""Skill 文件管理工具 - 案件目录的创建、列表和元数据更新。

用于管理打工魂·不灭 skill 的案件目录结构，支持创建案件、列出所有案件、
更新案件元数据等操作。所有输入输出均为 JSON 格式。

Usage:
    python3 tools/skill_writer.py --action list --base-dir ./cases
    python3 tools/skill_writer.py --action create --slug my-case --base-dir ./cases
    python3 tools/skill_writer.py --action update-meta --slug my-case --key dispute.current_phase --value negotiating --base-dir ./cases
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone


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


def load_meta(case_dir: str) -> dict:
    """读取案件目录下的 meta.json。"""
    meta_path = os.path.join(case_dir, "meta.json")
    if not os.path.isfile(meta_path):
        error_exit(f"meta.json not found in {case_dir}")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_meta(case_dir: str, meta: dict) -> None:
    """写入 meta.json 到案件目录。"""
    meta_path = os.path.join(case_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")


def action_list(base_dir: str) -> None:
    """列出所有案件。"""
    if not os.path.isdir(base_dir):
        output_json([])
        return

    cases = []
    for entry in sorted(os.listdir(base_dir)):
        case_dir = os.path.join(base_dir, entry)
        if not os.path.isdir(case_dir):
            continue
        meta_path = os.path.join(case_dir, "meta.json")
        if not os.path.isfile(meta_path):
            continue
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            cases.append({
                "slug": meta.get("slug", entry),
                "company": meta.get("company", ""),
                "phase": meta.get("dispute", {}).get("current_phase", ""),
                "created_at": meta.get("created_at", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue

    output_json(cases)


def action_create(slug: str, base_dir: str) -> None:
    """创建案件目录结构。"""
    if not slug:
        error_exit("--slug is required for create action")

    case_dir = os.path.join(base_dir, slug)
    if os.path.exists(case_dir):
        error_exit(f"Case directory already exists: {case_dir}")

    # 创建目录结构
    subdirs = [
        os.path.join("evidence", "contracts"),
        os.path.join("evidence", "chats"),
        os.path.join("evidence", "emails"),
        os.path.join("evidence", "attendance"),
        os.path.join("evidence", "performance"),
        os.path.join("evidence", "work-products"),
        os.path.join("evidence", "disputes"),
        os.path.join("versions"),
    ]
    for sub in subdirs:
        os.makedirs(os.path.join(case_dir, sub), exist_ok=True)

    # 创建初始 meta.json
    ts = now_iso()
    meta = {
        "slug": slug,
        "company": "",
        "created_at": ts,
        "updated_at": ts,
        "version": "v1",
        "profile": {},
        "dispute": {
            "current_phase": "negotiating",
            "user_intention": "undecided",
            "phase_history": [],
        },
        "tags": {"evidence_types": [], "legal_basis": []},
        "emotion": {"milestones": 0, "pressure_incidents": 0, "last_emotion": "neutral"},
        "evidence_count": 0,
        "knowledge_sources": [],
        "corrections_count": 0,
    }
    save_meta(case_dir, meta)

    output_json({
        "status": "created",
        "slug": slug,
        "path": os.path.join(base_dir, slug).replace("\\", "/"),
    })


def action_update_meta(slug: str, key: str, value: str, base_dir: str) -> None:
    """更新 meta.json 中的指定字段。"""
    if not slug:
        error_exit("--slug is required for update-meta action")
    if not key:
        error_exit("--key is required for update-meta action")

    case_dir = os.path.join(base_dir, slug)
    if not os.path.isdir(case_dir):
        error_exit(f"Case directory not found: {case_dir}")

    meta = load_meta(case_dir)

    # 支持嵌套 key（用点号分隔）
    keys = key.split(".")
    obj = meta
    for k in keys[:-1]:
        if k not in obj or not isinstance(obj[k], dict):
            obj[k] = {}
        obj = obj[k]

    # 尝试解析 value 为 JSON 类型（int, float, bool, list, dict）
    parsed_value: object = value
    try:
        parsed_value = json.loads(value)
    except (json.JSONDecodeError, ValueError):
        pass  # 保持原始字符串

    obj[keys[-1]] = parsed_value
    meta["updated_at"] = now_iso()
    save_meta(case_dir, meta)

    output_json(meta)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Skill 文件管理工具 - 案件目录的创建、列表和元数据更新"
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["list", "create", "update-meta"],
        help="操作类型：list(列出案件), create(创建案件), update-meta(更新元数据)",
    )
    parser.add_argument("--slug", help="案件标识符")
    parser.add_argument("--key", help="要更新的 meta.json 字段名（支持点号分隔嵌套）")
    parser.add_argument("--value", help="字段的新值")
    parser.add_argument("--base-dir", default="./cases", help="案件根目录（默认: ./cases）")

    args = parser.parse_args()

    try:
        if args.action == "list":
            action_list(args.base_dir)
        elif args.action == "create":
            action_create(args.slug, args.base_dir)
        elif args.action == "update-meta":
            if args.value is None:
                error_exit("--value is required for update-meta action")
            action_update_meta(args.slug, args.key, args.value, args.base_dir)
    except Exception as e:
        error_exit(str(e))


if __name__ == "__main__":
    main()
