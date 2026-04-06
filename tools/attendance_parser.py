"""考勤记录解析工具 - 解析 CSV 和纯文本格式的考勤数据。

自动检测列名，提取日期、上下班时间、状态等信息，
计算迟到/早退/缺卡/加班时长等统计数据。

Usage:
    python3 tools/attendance_parser.py --file attendance.csv --output parsed.md
    python3 tools/attendance_parser.py --file attendance.txt --output parsed.md
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
from datetime import datetime, timedelta


# 列名映射：常见列名 -> 标准字段名
COLUMN_ALIASES: dict[str, list[str]] = {
    "date": ["日期", "date", "考勤日期", "打卡日期", "时间", "time", "day"],
    "clock_in": ["上班打卡", "上班时间", "签到时间", "上班", "签到", "clock_in", "check_in", "first_punch"],
    "clock_out": ["下班打卡", "下班时间", "签退时间", "下班", "签退", "clock_out", "check_out", "last_punch"],
    "status": ["状态", "考勤状态", "打卡状态", "status", "备注", "remark"],
    "overtime": ["加班时长", "加班", "overtime", "ot", "加班时间"],
    "work_hours": ["工作时长", "工时", "work_hours", "hours"],
}

# 状态关键词
STATUS_NORMAL = {"正常", "normal", "准时", "按时", "全勤"}
STATUS_LATE = {"迟到", "late", "晚到"}
STATUS_EARLY = {"早退", "early", "早走"}
STATUS_MISSING = {"缺卡", "missing", "未打卡", "漏打卡", "漏卡"}
STATUS_REST = {"休息", "rest", "休息日", "周末", "节假日", "holiday"}
STATUS_ABSENT = {"旷工", "absent", "缺勤", "未出勤"}
STATUS_LEAVE = {"请假", "leave", "年假", "事假", "病假", "调休"}

STANDARD_WORK_END_HOUR = 18  # 标准下班时间 18:00


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
    for encoding in ("utf-8", "utf-8-sig", "gbk", "gb2312"):
        try:
            with open(filepath, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def detect_columns(header: list[str]) -> dict[str, int]:
    """自动检测列名对应的索引。"""
    result: dict[str, int] = {}
    header_lower = [h.strip().lower() for h in header]

    for field, aliases in COLUMN_ALIASES.items():
        for i, col in enumerate(header_lower):
            if col in [a.lower() for a in aliases]:
                result[field] = i
                break

    return result


def classify_status(text: str) -> str:
    """根据状态文本分类考勤状态。"""
    if not text:
        return "unknown"

    text_lower = text.strip().lower()

    for keyword in STATUS_NORMAL:
        if keyword in text_lower:
            return "normal"
    for keyword in STATUS_LATE:
        if keyword in text_lower:
            return "late"
    for keyword in STATUS_EARLY:
        if keyword in text_lower:
            return "early"
    for keyword in STATUS_MISSING:
        if keyword in text_lower:
            return "missing"
    for keyword in STATUS_REST:
        if keyword in text_lower:
            return "rest"
    for keyword in STATUS_ABSENT:
        if keyword in text_lower:
            return "absent"
    for keyword in STATUS_LEAVE:
        if keyword in text_lower:
            return "leave"

    return "unknown"


def parse_time(time_str: str) -> str:
    """标准化时间格式，返回 HH:MM 格式。"""
    if not time_str or not time_str.strip():
        return ""

    time_str = time_str.strip()
    # 匹配 HH:MM 或 HH:MM:SS
    m = re.match(r"(\d{1,2}):(\d{2})(?::(\d{2}))?", time_str)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    return time_str


def parse_date(date_str: str) -> str:
    """标准化日期格式，返回 YYYY-MM-DD 格式。"""
    if not date_str or not date_str.strip():
        return ""

    date_str = date_str.strip()
    # 尝试多种格式
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return date_str


def calculate_overtime(clock_out: str) -> float:
    """计算加班时长（小时），基于标准下班时间。"""
    if not clock_out:
        return 0.0

    m = re.match(r"(\d{1,2}):(\d{2})", clock_out)
    if not m:
        return 0.0

    hour = int(m.group(1))
    minute = int(m.group(2))

    total_minutes = hour * 60 + minute
    standard_minutes = STANDARD_WORK_END_HOUR * 60

    if total_minutes > standard_minutes:
        return round((total_minutes - standard_minutes) / 60.0, 1)
    return 0.0


def parse_csv_records(content: str) -> list[dict]:
    """解析 CSV 格式的考勤记录。"""
    records: list[dict] = []

    # 检测分隔符
    try:
        dialect = csv.Sniffer().sniff(content[:4096], delimiters=",\t;|")
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(io.StringIO(content), dialect)

    header = None
    col_map: dict[str, int] = {}

    for row in reader:
        if header is None:
            header = row
            col_map = detect_columns(header)
            continue

        if not row or all(not cell.strip() for cell in row):
            continue

        def get_col(field: str) -> str:
            idx = col_map.get(field)
            if idx is not None and idx < len(row):
                return row[idx].strip()
            return ""

        date = parse_date(get_col("date"))
        clock_in = parse_time(get_col("clock_in"))
        clock_out = parse_time(get_col("clock_out"))
        status_text = get_col("status")
        overtime_str = get_col("overtime")

        if not date:
            continue

        # 从时间推断状态（如果没有明确的状态列）
        status = classify_status(status_text)
        if status == "unknown" and clock_in and clock_out:
            status = "normal"
        elif status == "unknown" and not clock_in and not clock_out:
            status = "rest"

        # 加班时长
        overtime = 0.0
        if overtime_str:
            try:
                overtime = float(re.sub(r"[^\d.]", "", overtime_str))
            except (ValueError, AttributeError):
                overtime = calculate_overtime(clock_out)
        else:
            overtime = calculate_overtime(clock_out)

        records.append({
            "date": date,
            "clock_in": clock_in,
            "clock_out": clock_out,
            "status": status,
            "status_text": status_text,
            "overtime": overtime,
        })

    return records


def parse_text_records(content: str) -> list[dict]:
    """解析纯文本表格格式的考勤记录。"""
    lines = content.strip().splitlines()
    if len(lines) < 2:
        return []

    # 尝试检测分隔符
    sep = None
    for candidate in ["|", "\t", ",", "  "]:
        if candidate in lines[0]:
            sep = candidate
            break

    if sep is None:
        return parse_csv_records(content)

    # 解析表头
    header_parts = [h.strip() for h in lines[0].split(sep) if h.strip()]
    col_map = detect_columns(header_parts)

    records: list[dict] = []
    for line in lines[1:]:
        line = line.strip()
        if not line or re.match(r"^[-=|+\s]+$", line):
            continue

        parts = [p.strip() for p in line.split(sep) if p.strip()]

        def get_col(field: str) -> str:
            idx = col_map.get(field)
            if idx is not None and idx < len(parts):
                return parts[idx]
            return ""

        date = parse_date(get_col("date"))
        clock_in = parse_time(get_col("clock_in"))
        clock_out = parse_time(get_col("clock_out"))
        status_text = get_col("status")

        if not date:
            continue

        status = classify_status(status_text)
        if status == "unknown" and clock_in and clock_out:
            status = "normal"

        overtime = calculate_overtime(clock_out)

        records.append({
            "date": date,
            "clock_in": clock_in,
            "clock_out": clock_out,
            "status": status,
            "status_text": status_text,
            "overtime": overtime,
        })

    return records


def compute_stats(records: list[dict]) -> dict:
    """计算考勤统计摘要。"""
    working_days = [r for r in records if r["status"] not in ("rest",)]
    actual_attended = [
        r for r in working_days if r["status"] in ("normal", "late", "early")
    ]
    late_count = sum(1 for r in records if r["status"] == "late")
    early_count = sum(1 for r in records if r["status"] == "early")
    missing_count = sum(1 for r in records if r["status"] == "missing")
    absent_count = sum(1 for r in records if r["status"] == "absent")
    total_overtime = sum(r["overtime"] for r in records)

    should_attend = len(working_days)
    actual_attend = len(actual_attended)
    attendance_rate = (actual_attend / should_attend * 100) if should_attend > 0 else 0.0

    return {
        "total_days": len(records),
        "should_attend": should_attend,
        "actual_attend": actual_attend,
        "late_count": late_count,
        "early_count": early_count,
        "missing_count": missing_count,
        "absent_count": absent_count,
        "total_overtime": round(total_overtime, 1),
        "attendance_rate": round(attendance_rate, 1),
    }


def get_date_range(records: list[dict]) -> tuple[str, str]:
    """获取记录的时间范围。"""
    if not records:
        return "无", "无"
    dates = [r["date"] for r in records if r["date"]]
    if not dates:
        return "无", "无"
    dates.sort()
    return dates[0], dates[-1]


STATUS_LABEL = {
    "normal": "正常",
    "late": "迟到",
    "early": "早退",
    "missing": "缺卡",
    "rest": "休息",
    "absent": "旷工",
    "leave": "请假",
    "unknown": "未知",
}


def format_output(records: list[dict], stats: dict) -> str:
    """将考勤记录格式化为 Markdown 输出。"""
    start, end = get_date_range(records)

    lines = [
        "# 考勤记录解析结果",
        "",
        f"> 统计期间：{start} ~ {end} | 总天数：{stats['total_days']} | 出勤率：{stats['attendance_rate']}%",
        "",
        "## 统计摘要",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 应出勤 | {stats['should_attend']}天 |",
        f"| 实际出勤 | {stats['actual_attend']}天 |",
        f"| 迟到 | {stats['late_count']}次 |",
        f"| 早退 | {stats['early_count']}次 |",
        f"| 缺卡 | {stats['missing_count']}次 |",
        f"| 加班时长 | {stats['total_overtime']}小时 |",
        "",
        "## 详细记录",
        "",
        "| 日期 | 上班 | 下班 | 状态 | 加班(h) |",
        "|------|------|------|------|---------|",
    ]

    for r in records:
        status_label = STATUS_LABEL.get(r["status"], r["status"])
        clock_in = r["clock_in"] or "-"
        clock_out = r["clock_out"] or "-"
        ot = f"{r['overtime']}" if r["overtime"] > 0 else "-"
        lines.append(f"| {r['date']} | {clock_in} | {clock_out} | {status_label} | {ot} |")

    # 异常记录
    anomalies = [
        r for r in records if r["status"] in ("late", "early", "missing", "absent")
    ]

    lines.append("")
    lines.append("## 异常记录")
    lines.append("")

    if anomalies:
        for r in anomalies:
            status_label = STATUS_LABEL.get(r["status"], r["status"])
            detail = f"{r['date']} - {status_label}"
            if r["clock_in"]:
                detail += f" | 上班: {r['clock_in']}"
            if r["clock_out"]:
                detail += f" | 下班: {r['clock_out']}"
            lines.append(f"- {detail}")
    else:
        lines.append("无异常记录")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="考勤记录解析工具 - 解析 CSV 和纯文本格式的考勤数据"
    )
    parser.add_argument("--file", required=True, help="考勤记录文件路径（CSV 或纯文本）")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    try:
        if not os.path.isfile(args.file):
            error_exit(f"File not found: {args.file}")

        content = read_file_with_encoding(args.file)

        # 检测文件格式
        ext = os.path.splitext(args.file)[1].lower()
        if ext == ".csv":
            records = parse_csv_records(content)
        else:
            # 尝试 CSV 格式，失败后尝试纯文本
            records = parse_csv_records(content)
            if not records:
                records = parse_text_records(content)

        if not records:
            error_exit("No valid attendance records found in the file")

        # 按日期排序
        records.sort(key=lambda r: r["date"])

        # 计算统计
        stats = compute_stats(records)

        # 格式化输出
        output_text = format_output(records, stats)

        # 写入输出文件
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)

        output_json({
            "status": "ok",
            "total_records": len(records),
            "stats": stats,
            "output": args.output,
        })
    except SystemExit:
        raise
    except Exception as e:
        error_exit(str(e))


if __name__ == "__main__":
    main()
