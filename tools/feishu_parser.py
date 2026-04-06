"""飞书消息导出 JSON 解析工具 - 解析飞书导出的 JSON 格式聊天记录。

兼容多种飞书导出格式，自动检测消息列表字段位置。
支持按目标人物过滤消息。

Usage:
    python3 tools/feishu_parser.py --file messages.json --target "张三" --output parsed.md
    python3 tools/feishu_parser.py --file messages.json --output parsed.md  # 保留所有消息
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


def read_file_with_encoding(filepath: str) -> str:
    """尝试多种编码读取文件。"""
    for encoding in ("utf-8", "utf-8-sig", "gbk"):
        try:
            with open(filepath, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def extract_messages_list(data: object) -> list[dict]:
    """从飞书导出 JSON 中提取消息列表。

    兼容格式：
    - {items: [...]}
    - {messages: [...]}
    - {data: {items: [...]}}
    - {data: {messages: [...]}}
    """
    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    # 直接在顶层查找
    for key in ("items", "messages"):
        if key in data and isinstance(data[key], list):
            return data[key]

    # 在 data 字段中查找
    if "data" in data and isinstance(data["data"], dict):
        for key in ("items", "messages"):
            if key in data["data"] and isinstance(data["data"][key], list):
                return data["data"][key]

    # 递归搜索第一个列表类型的字段
    for value in data.values():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value

    return []


def extract_sender_name(msg: dict) -> str:
    """从消息对象中提取发送者名称。"""
    # 直接 name 字段
    if "name" in msg:
        return str(msg["name"])

    # sender 对象
    sender = msg.get("sender", {})
    if isinstance(sender, dict):
        if "name" in sender:
            return str(sender["name"])
        if "id" in sender and isinstance(sender["id"], dict) and "name" in sender["id"]:
            return str(sender["id"]["name"])

    # sender_id 字段
    if "sender_id" in msg:
        sid = msg["sender_id"]
        if isinstance(sid, dict) and "name" in sid:
            return str(sid["name"])
        return str(sid)

    # user 字段
    if "user" in msg:
        user = msg["user"]
        if isinstance(user, dict) and "name" in user:
            return str(user["name"])
        return str(user)

    return "Unknown"


def extract_content(msg: dict) -> str:
    """从消息对象中提取消息内容。"""
    # 直接 content 字段
    if "content" in msg:
        return str(msg["content"])

    # body 对象
    body = msg.get("body", {})
    if isinstance(body, dict):
        if "content" in body:
            return str(body["content"])
        if "text" in body:
            return str(body["text"])
        # body.content 可能是 JSON 字符串
        if "content" in body:
            try:
                parsed = json.loads(body["content"])
                if isinstance(parsed, dict):
                    return parsed.get("text", str(body["content"]))
            except (json.JSONDecodeError, TypeError):
                pass

    # text 字段
    if "text" in msg:
        return str(msg["text"])

    # msg_type 为 text 时从 body.content 解析
    if msg.get("msg_type") == "text":
        raw = msg.get("body", {}).get("content", "")
        if raw:
            try:
                parsed = json.loads(raw)
                return parsed.get("text", raw)
            except (json.JSONDecodeError, TypeError):
                return raw

    return ""


def extract_timestamp(msg: dict) -> str:
    """从消息对象中提取时间戳。"""
    # create_time 字段
    if "create_time" in msg:
        val = msg["create_time"]
        if isinstance(val, (int, float)):
            return _format_timestamp(val)
        return str(val)

    # create_time_ts 字段
    if "create_time_ts" in msg:
        val = msg["create_time_ts"]
        if isinstance(val, (int, float)):
            return _format_timestamp(val)
        return str(val)

    # timestamp 字段
    if "timestamp" in msg:
        val = msg["timestamp"]
        if isinstance(val, (int, float)):
            return _format_timestamp(val)
        return str(val)

    # time 字段
    if "time" in msg:
        return str(msg["time"])

    return "Unknown"


def _format_timestamp(ts: float) -> str:
    """将时间戳（秒或毫秒）格式化为可读字符串。"""
    # 判断是秒还是毫秒
    if ts > 1e12:
        ts = ts / 1000.0
    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError):
        return str(ts)


def parse_messages(raw_list: list[dict]) -> list[dict]:
    """解析消息列表，提取关键字段。"""
    messages = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue

        content = extract_content(item)
        if not content.strip():
            continue

        messages.append({
            "timestamp": extract_timestamp(item),
            "sender": extract_sender_name(item),
            "content": content.strip(),
        })

    # 按时间排序
    messages.sort(key=lambda m: m["timestamp"])
    return messages


def filter_messages(messages: list[dict], target: str) -> list[dict]:
    """过滤消息，保留目标人物相关的对话。"""
    if not target:
        return messages

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

    return [messages[i] for i in sorted(keep_indices)]


def format_output(messages: list[dict], target: str) -> str:
    """将消息列表格式化为 Markdown 输出。"""
    timestamps = [m["timestamp"] for m in messages] if messages else []
    time_range = f"{timestamps[0]} ~ {timestamps[-1]}" if timestamps else "无"
    target_display = target if target else "全部"

    lines = [
        "# 飞书聊天记录解析结果",
        "",
        f"> 目标人物：{target_display} | 时间范围：{time_range} | 消息数：{len(messages)}",
        "",
        "---",
        "",
    ]

    for msg in messages:
        lines.append(f"[{msg['timestamp']}] **{msg['sender']}**: {msg['content']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="飞书消息导出 JSON 解析工具 - 解析飞书导出的 JSON 格式聊天记录"
    )
    parser.add_argument("--file", required=True, help="飞书导出 JSON 文件路径")
    parser.add_argument("--target", default="", help="目标人物名称（为空则保留所有消息）")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    try:
        if not os.path.isfile(args.file):
            error_exit(f"File not found: {args.file}")

        content = read_file_with_encoding(args.file)

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            error_exit(f"Invalid JSON file: {e}")

        # 提取消息列表
        raw_list = extract_messages_list(data)
        if not raw_list:
            error_exit("No messages found in the JSON file")

        # 解析消息
        messages = parse_messages(raw_list)

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


if __name__ == "__main__":
    main()
