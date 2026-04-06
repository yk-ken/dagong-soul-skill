"""邮件解析工具 - 解析 .eml 和 .mbox 格式的邮件文件。

支持提取邮件元数据（From, To, Date, Subject）和正文内容，
自动处理多种字符编码（UTF-8, GBK, GB2312 等）。
记录附件名称和大小但不解析附件内容。

Usage:
    python3 tools/email_parser.py --file email.eml --target "boss@company.com" --output parsed.md
    python3 tools/email_parser.py --file archive.mbox --target "hr" --output parsed.md
"""

from __future__ import annotations

import argparse
import email
import email.header
import email.utils
import json
import mailbox
import os
import re
import sys
from email.message import EmailMessage
from email.policy import default as default_policy


def error_exit(message: str) -> None:
    """输出 JSON 错误信息到 stderr 并退出。"""
    json.dump({"error": message}, sys.stderr, ensure_ascii=False)
    sys.stderr.write("\n")
    sys.exit(1)


def output_json(data: object) -> None:
    """输出 JSON 到 stdout。"""
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def decode_header_value(value: str | None) -> str:
    """解码邮件头部字段，处理编码字符串。"""
    if not value:
        return ""
    try:
        parts = email.header.decode_header(value)
        decoded_parts = []
        for part, charset in parts:
            if isinstance(part, bytes):
                charset = charset or "utf-8"
                try:
                    decoded_parts.append(part.decode(charset))
                except (UnicodeDecodeError, LookupError):
                    decoded_parts.append(part.decode("utf-8", errors="replace"))
            else:
                decoded_parts.append(part)
        return " ".join(decoded_parts)
    except Exception:
        return str(value)


def get_body_text(msg: email.message.Message) -> str:
    """提取邮件正文，优先取 text/plain 部分。"""
    if msg.is_multipart():
        text_parts: list[str] = []
        html_parts: list[str] = []

        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            # 跳过附件
            if "attachment" in disposition:
                continue

            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset() or "utf-8"
                try:
                    text = payload.decode(charset)
                except (UnicodeDecodeError, LookupError):
                    text = payload.decode("utf-8", errors="replace")
            except Exception:
                continue

            if content_type == "text/plain":
                text_parts.append(text)
            elif content_type == "text/html":
                html_parts.append(text)

        if text_parts:
            return "\n".join(text_parts)
        elif html_parts:
            return _strip_html_tags("\n".join(html_parts))
        return ""
    else:
        # 非多部分邮件
        content_type = msg.get_content_type()
        if content_type not in ("text/plain", "text/html"):
            return ""

        try:
            payload = msg.get_payload(decode=True)
            if payload is None:
                return ""
            charset = msg.get_content_charset() or "utf-8"
            try:
                text = payload.decode(charset)
            except (UnicodeDecodeError, LookupError):
                text = payload.decode("utf-8", errors="replace")
        except Exception:
            return ""

        if content_type == "text/html":
            return _strip_html_tags(text)
        return text


def _strip_html_tags(html: str) -> str:
    """简单清理 HTML 标签。"""
    # 替换常见块级标签为换行
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</div>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</tr>", "\n", text, flags=re.IGNORECASE)
    # 移除所有 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)
    # 解码常见 HTML 实体
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    # 清理多余空白
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_attachments(msg: email.message.Message) -> list[dict]:
    """获取附件信息（名称和大小）。"""
    attachments = []
    for part in msg.walk():
        disposition = str(part.get("Content-Disposition", ""))
        if "attachment" in disposition:
            filename = part.get_filename()
            if filename:
                filename = decode_header_value(filename)
            else:
                filename = "unnamed"

            payload = part.get_payload(decode=True)
            size = len(payload) if payload else 0

            attachments.append({
                "name": filename,
                "size": _format_size(size),
            })
    return attachments


def _format_size(size_bytes: int) -> str:
    """格式化文件大小。"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"


def parse_date(date_str: str) -> tuple[str, str]:
    """解析邮件日期，返回 (格式化日期, 排序用日期)。

    Returns:
        (formatted_date, sort_key) 元组
    """
    if not date_str:
        return ("Unknown", "")
    try:
        parsed = email.utils.parsedate_to_datetime(date_str)
        formatted = parsed.strftime("%Y-%m-%d %H:%M:%S")
        return (formatted, parsed.isoformat())
    except Exception:
        return (date_str, date_str)


def parse_single_eml(filepath: str) -> list[dict]:
    """解析单个 .eml 文件。"""
    with open(filepath, "rb") as f:
        msg = email.message_from_binary_file(f)

    return [_extract_email_data(msg)]


def parse_mbox_file(filepath: str) -> list[dict]:
    """解析 .mbox 邮件归档。"""
    mbox = mailbox.mbox(filepath)
    emails = []
    for msg in mbox:
        if isinstance(msg, email.message.Message):
            emails.append(_extract_email_data(msg))
    mbox.close()
    return emails


def _extract_email_data(msg: email.message.Message) -> dict:
    """从 EmailMessage 对象中提取结构化数据。"""
    from_addr = decode_header_value(msg.get("From", ""))
    to_addr = decode_header_value(msg.get("To", ""))
    subject = decode_header_value(msg.get("Subject", ""))
    date_raw = msg.get("Date", "")
    formatted_date, sort_key = parse_date(date_raw)
    body = get_body_text(msg)
    attachments = get_attachments(msg)

    return {
        "from": from_addr,
        "to": to_addr,
        "date": formatted_date,
        "sort_key": sort_key,
        "subject": subject,
        "body": body,
        "attachments": attachments,
    }


def matches_target(email_data: dict, target: str) -> bool:
    """检查邮件是否与目标相关（From 或 To 包含 target）。"""
    if not target:
        return True
    target_lower = target.lower()
    return (
        target_lower in email_data["from"].lower()
        or target_lower in email_data["to"].lower()
    )


def format_output(emails: list[dict], target: str) -> str:
    """将邮件列表格式化为 Markdown 输出。"""
    if not emails:
        target_display = target if target else "全部"
        return (
            "# 邮件记录解析结果\n\n"
            f"> 目标人物：{target_display} | 邮件数：0 | 时间范围：无\n\n---\n"
        )

    timestamps = [e["date"] for e in emails if e["date"] != "Unknown"]
    time_range = f"{timestamps[0]} ~ {timestamps[-1]}" if timestamps else "无"
    target_display = target if target else "全部"

    lines = [
        "# 邮件记录解析结果",
        "",
        f"> 目标人物：{target_display} | 邮件数：{len(emails)} | 时间范围：{time_range}",
        "",
        "---",
        "",
    ]

    for i, em in enumerate(emails, 1):
        att_str = ", ".join(
            f"{a['name']} ({a['size']})" for a in em["attachments"]
        )
        if not att_str:
            att_str = "无"

        lines.append(f"## {i}. {em['subject']}")
        lines.append("")
        lines.append(f"- **From**: {em['from']}")
        lines.append(f"- **To**: {em['to']}")
        lines.append(f"- **Date**: {em['date']}")
        lines.append(f"- **Attachments**: {att_str}")
        lines.append("")
        if em["body"]:
            lines.append(em["body"])
        else:
            lines.append("(无正文内容)")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="邮件解析工具 - 解析 .eml 和 .mbox 格式的邮件文件"
    )
    parser.add_argument("--file", required=True, help="邮件文件路径（.eml 或 .mbox）")
    parser.add_argument("--target", default="", help="目标人物名称或邮箱（匹配 From/To）")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    try:
        if not os.path.isfile(args.file):
            error_exit(f"File not found: {args.file}")

        ext = os.path.splitext(args.file)[1].lower()

        if ext == ".eml":
            emails = parse_single_eml(args.file)
        elif ext == ".mbox":
            emails = parse_mbox_file(args.file)
        else:
            # 尝试根据内容判断
            with open(args.file, "rb") as f:
                header = f.read(100)
            if b"From " in header[:10]:
                emails = parse_mbox_file(args.file)
            else:
                emails = parse_single_eml(args.file)

        # 过滤目标
        filtered = [em for em in emails if matches_target(em, args.target)]

        # 按日期排序
        filtered.sort(key=lambda e: e["sort_key"])

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
            "total_emails": len(emails),
            "filtered_emails": len(filtered),
            "target": args.target or "all",
            "output": args.output,
        })
    except SystemExit:
        raise
    except Exception as e:
        error_exit(str(e))


if __name__ == "__main__":
    main()
