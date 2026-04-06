"""微信聊天记录解析工具 - 解析 WeChatMsg 导出和手动复制的聊天记录。

支持 WeChatMsg 导出的 txt 格式和纯文本粘贴格式，提取目标人物的对话记录。
自动过滤系统消息、表情包提示、红包提示等无关内容。

Usage:
    python3 tools/wechat_parser.py --file chat.txt --target "张三" --output parsed.md
    python3 tools/wechat_parser.py --file chat.txt --output parsed.md  # 保留所有消息
"""

from __future__ import annotations

import argparse
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
    re.compile(r"加入了群聊"),
    re.compile(r"修改群名为"),
    re.compile(r"^---+$"),
    re.compile(r"^===+$"),
    re.compile(r"^…+$"),
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


def parse_timestamp(line: str) -> tuple[str | None, str | None]:
    """尝试从行中解析时间戳和发送者。

    Returns:
        (timestamp, sender) 元组，如果无法解析则返回 (None, None)
    """
    for pattern in TIMESTAMP_PATTERNS:
        m = pattern.match(line.strip())
        if m:
            return m.group(1), m.group(2).strip()
    return None, None


def parse_messages(lines: list[str]) -> list[dict]:
    """解析聊天记录行列表，返回消息列表。

    每条消息格式：{"timestamp": str, "sender": str, "content": str}
    """
    messages: list[dict] = []
    current_msg: dict | None = None

    for line in lines:
        line = line.rstrip("\n\r")
        stripped = line.strip()

        # 跳过空行（但保留消息内容中的空行）
        if not stripped:
            if current_msg and current_msg["content"]:
                current_msg["content"] += "\n"
            continue

        # 尝试解析时间戳行
        ts, sender = parse_timestamp(stripped)

        if ts and sender:
            # 保存上一条消息
            if current_msg and current_msg["content"].strip():
                current_msg["content"] = current_msg["content"].strip()
                messages.append(current_msg)

            current_msg = {
                "timestamp": ts,
                "sender": sender,
                "content": "",
            }
        elif ts:
            # 只有时间戳没有发送者，可能是系统消息行
            if current_msg and current_msg["content"].strip():
                current_msg["content"] = current_msg["content"].strip()
                messages.append(current_msg)
            current_msg = None
        else:
            # 消息内容行
            if current_msg is not None:
                current_msg["content"] += stripped + "\n"
            else:
                # 没有前置时间戳的行，可能是格式不标准的记录
                # 尝试作为独立系统消息忽略
                pass

    # 保存最后一条消息
    if current_msg and current_msg["content"].strip():
        current_msg["content"] = current_msg["content"].strip()
        messages.append(current_msg)

    return messages


def filter_messages(messages: list[dict], target: str) -> list[dict]:
    """过滤消息，保留目标人物相关的对话上下文。

    如果 target 为空，保留所有消息。
    否则保留目标人物发送的消息及其上下文（前后相邻的用户消息）。
    """
    if not target:
        return [m for m in messages if not is_system_message(m["content"])]

    # 标记目标消息的索引
    target_indices: set[int] = set()
    for i, msg in enumerate(messages):
        if target in msg["sender"]:
            target_indices.add(i)

    # 收集目标消息及其上下文（前后各 1 条）
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
        "# 微信聊天记录解析结果",
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
        description="微信聊天记录解析工具 - 解析 WeChatMsg 导出和手动复制的聊天记录"
    )
    parser.add_argument("--file", required=True, help="聊天记录文件路径")
    parser.add_argument("--target", default="", help="目标人物名称（为空则保留所有消息）")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    try:
        if not os.path.isfile(args.file):
            error_exit(f"File not found: {args.file}")

        # 读取文件
        with open(args.file, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        # 如果 UTF-8 失败，尝试 GBK
        if not raw_lines:
            with open(args.file, "r", encoding="gbk", errors="replace") as f:
                raw_lines = f.readlines()

        # 解析消息
        messages = parse_messages(raw_lines)

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
