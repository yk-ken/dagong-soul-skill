"""钉钉聊天记录解析工具 - 解析钉钉导出的聊天记录。

支持钉钉导出的 txt、CSV 格式和纯文本粘贴格式。
可识别已读/未读状态标记和 DING 消息。

Usage:
    python3 tools/dingtalk_parser.py --file chat.txt --target "张三" --output parsed.md
    python3 tools/dingtalk_parser.py --file chat.csv --target "张三" --output parsed.md
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
from datetime import datetime


# 时间戳模式
TIMESTAMP_PATTERNS = [
    re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+)$"),
    re.compile(r"^(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+)$"),
    re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s+(.+)$"),
    re.compile(r"^(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})\s+(.+)$"),
]

# 系统消息过滤模式
SYSTEM_PATTERNS = [
    re.compile(r"以下是新消息"),
    re.compile(r"撤回了一条消息"),
    re.compile(r"\[表情\]"),
    re.compile(r"\[图片\]"),
    re.compile(r"\[红包\]"),
    re.compile(r"领取了红包"),
    re.compile(r"^---+$"),
    re.compile(r"^===+$"),
    re.compile(r"已读"),
    re.compile(r"未读"),
]


def error_exit(message: str) -> None:
    """输出 JSON 错误信息到 stderr 并退出。"""
    json.dump({"error": message}, sys.stderr, ensure_ascii=False)
    sys.stderr.write("\n")
    sys.exit(1)


def output_json(data: object) -> None:
    """输出 JSON 到 stdout。"""
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def is_system_message(text: str) -> bool:
    """判断是否为系统消息。"""
    stripped = text.strip()
    if not stripped:
        return True
    for pattern in SYSTEM_PATTERNS:
        if pattern.search(stripped):
            return True
    return False


def detect_ding_message(text: str) -> bool:
    """检测是否为 DING 消息。"""
    return bool(re.search(r"\[DING\]|\[钉\]|DING:", text, re.IGNORECASE))


def parse_timestamp(line: str) -> tuple[str | None, str | None]:
    """尝试从行中解析时间戳和发送者。"""
    for pattern in TIMESTAMP_PATTERNS:
        m = pattern.match(line.strip())
        if m:
            return m.group(1), m.group(2).strip()
    return None, None


def read_file_with_encoding(filepath: str) -> str:
    """尝试多种编码读取文件。"""
    for encoding in ("utf-8", "gbk", "gb2312", "utf-8-sig"):
        try:
            with open(filepath, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    # 最终 fallback
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_txt_messages(lines: list[str]) -> list[dict]:
    """解析文本格式的聊天记录。"""
    messages: list[dict] = []
    current_msg: dict | None = None

    for line in lines:
        line = line.rstrip("\n\r")
        stripped = line.strip()

        if not stripped:
            if current_msg and current_msg["content"]:
                current_msg["content"] += "\n"
            continue

        ts, sender = parse_timestamp(stripped)

        if ts and sender:
            if current_msg and current_msg["content"].strip():
                current_msg["content"] = current_msg["content"].strip()
                messages.append(current_msg)

            current_msg = {
                "timestamp": ts,
                "sender": sender,
                "content": "",
                "is_ding": False,
            }
        elif ts:
            if current_msg and current_msg["content"].strip():
                current_msg["content"] = current_msg["content"].strip()
                messages.append(current_msg)
            current_msg = None
        else:
            if current_msg is not None:
                current_msg["content"] += stripped + "\n"

    if current_msg and current_msg["content"].strip():
        current_msg["content"] = current_msg["content"].strip()
        messages.append(current_msg)

    # 标记 DING 消息
    for msg in messages:
        msg["is_ding"] = detect_ding_message(msg["content"])

    return messages


def parse_csv_messages(content: str) -> list[dict]:
    """解析 CSV 格式的聊天记录。"""
    messages: list[dict] = []

    # 尝试检测分隔符
    dialect = csv.Sniffer().sniff(content[:4096], delimiters=",\t;")
    reader = csv.reader(io.StringIO(content), dialect)

    header = None
    for row in reader:
        if header is None:
            header = [h.strip().lower() for h in row]
            continue

        if len(row) < 3:
            continue

        # 自动检测列名
        ts_col = _find_col(header, ["时间", "time", "timestamp", "date", "日期"])
        sender_col = _find_col(header, ["发送者", "sender", "name", "名字", "发言人"])
        content_col = _find_col(header, ["内容", "content", "message", "消息", "text"])

        if ts_col is None or sender_col is None or content_col is None:
            # 默认：前三列
            ts_col, sender_col, content_col = 0, 1, 2

        try:
            ts = row[ts_col].strip()
            sender = row[sender_col].strip()
            text = row[content_col].strip()
        except IndexError:
            continue

        if ts and sender and text:
            messages.append({
                "timestamp": ts,
                "sender": sender,
                "content": text,
                "is_ding": detect_ding_message(text),
            })

    return messages


def _find_col(header: list[str], candidates: list[str]) -> int | None:
    """在表头中查找匹配的列索引。"""
    for i, h in enumerate(header):
        if h in candidates:
            return i
    return None


def filter_messages(messages: list[dict], target: str) -> list[dict]:
    """过滤消息，保留目标人物相关的对话。"""
    if not target:
        return [m for m in messages if not is_system_message(m["content"])]

    target_indices: set[int] = set()
    for i, msg in enumerate(messages):
        if target in msg["sender"]:
            target_indices.add(i)

    keep_indices: set[int] = set()
    for idx in target_indices:
        keep_indices.add(idx)
        if idx > 0:
            keep_indices.add(idx - 1)
        if idx < len(messages) - 1:
            keep_indices.add(idx + 1)

    result = []
    for i in sorted(keep_indices):
        msg = messages[i]
        if not is_system_message(msg["content"]):
            result.append(msg)

    return result


def format_output(messages: list[dict], target: str) -> str:
    """将消息列表格式化为 Markdown 输出。"""
    if not messages:
        timestamps = []
    else:
        timestamps = [m["timestamp"] for m in messages]

    time_range = "无"
    if timestamps:
        time_range = f"{timestamps[0]} ~ {timestamps[-1]}"

    target_display = target if target else "全部"

    lines = [
        "# 钉钉聊天记录解析结果",
        "",
        f"> 目标人物：{target_display} | 时间范围：{time_range} | 消息数：{len(messages)}",
        "",
        "---",
        "",
    ]

    for msg in messages:
        ding_marker = " [DING]" if msg.get("is_ding") else ""
        lines.append(
            f"[{msg['timestamp']}] **{msg['sender']}**{ding_marker}: {msg['content']}"
        )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="钉钉聊天记录解析工具 - 解析钉钉导出的聊天记录"
    )
    parser.add_argument("--file", required=True, help="聊天记录文件路径")
    parser.add_argument("--target", default="", help="目标人物名称（为空则保留所有消息）")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    try:
        if not os.path.isfile(args.file):
            error_exit(f"File not found: {args.file}")

        content = read_file_with_encoding(args.file)

        # 检测文件格式
        ext = os.path.splitext(args.file)[1].lower()
        if ext == ".csv":
            messages = parse_csv_messages(content)
        else:
            # 尝试检测是否为 CSV
            first_line = content.split("\n", 1)[0]
            if "," in first_line and _looks_like_csv_header(first_line):
                messages = parse_csv_messages(content)
            else:
                messages = parse_txt_messages(content.splitlines())

        # 过滤消息
        filtered = filter_messages(messages, args.target)

        # 格式化输出
        output_text = format_output(filtered, args.target)

        # 写入输出文件
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)

        output_json({
            "status": "ok",
            "total_messages": len(messages),
            "filtered_messages": len(filtered),
            "target": args.target or "all",
            "output": args.output,
        })
    except SystemExit:
        raise
    except Exception as e:
        error_exit(str(e))


def _looks_like_csv_header(line: str) -> bool:
    """检测行是否像 CSV 表头。"""
    keywords = ["时间", "发送者", "内容", "time", "sender", "content", "message"]
    lower = line.lower()
    return any(kw in lower for kw in keywords)


if __name__ == "__main__":
    main()
