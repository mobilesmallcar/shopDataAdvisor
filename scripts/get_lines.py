#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Tuple
from datetime import datetime


def is_import_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return (
            stripped.startswith("import ")
            or (stripped.startswith("from ") and " import " in stripped)
    ) and not stripped.startswith("#")


def count_code_lines(file_path: Path) -> Tuple[int, int, int, int, int]:
    total = blank = comment = imports = core = 0
    in_multiline = False
    multi_delimiter = None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                total += 1
                stripped = line.strip()

                if not stripped:
                    blank += 1
                    continue

                if in_multiline:
                    comment += 1
                    if multi_delimiter in stripped and stripped.endswith(multi_delimiter):
                        in_multiline = False
                    continue

                if stripped.startswith(('"""', "'''")):
                    in_multiline = True
                    multi_delimiter = stripped[:3]
                    comment += 1
                    if stripped.count(multi_delimiter) == 2:
                        in_multiline = False
                    continue

                if stripped.startswith("#"):
                    comment += 1
                    continue

                if is_import_line(line):
                    imports += 1
                    continue

                core += 1

    except Exception as e:
        print(f"  读取失败 {file_path}: {e}", file=sys.stderr)
        return 0, 0, 0, 0, 0

    return total, blank, comment, imports, core


def should_skip_dir(path: Path) -> bool:
    skip_dirs = {".git", "__pycache__", ".idea", ".vscode", "venv", "env", "node_modules"}
    return any(part in skip_dirs for part in path.parts)


def get_last_record(record_path: Path) -> tuple | None:
    if not record_path.exists() or record_path.stat().st_size == 0:
        return None

    last_core = None
    last_date = None

    with open(record_path, "r", encoding="utf-8") as f:
        for line in reversed(f.readlines()):
            if line.strip() and not line.startswith("#"):
                parts = line.strip().split("|")
                if len(parts) >= 7:
                    date_str = parts[0].strip()
                    try:
                        last_date = datetime.strptime(date_str, "%Y-%m-%d")
                        last_core_str = parts[6].strip().split()[0].replace(',', '')
                        last_core = int(last_core_str)
                        break
                    except:
                        continue
    return (last_core, last_date) if last_core is not None else None


def save_record(stats: dict, record_path: Path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"{timestamp} | "
        f"文件数: {stats['files']:4d} | "
        f"总行: {stats['total']:6,d} | "
        f"空行: {stats['blank']:6,d} ({stats['blank_pct']:5.1f}%) | "
        f"注释: {stats['comment']:6,d} ({stats['comment_pct']:5.1f}%) | "
        f"导入: {stats['imports']:6,d} ({stats['import_pct']:5.1f}%) | "
        f"核心: {stats['core']:6,d} ({stats['core_pct']:5.1f}%)\n"
    )
    with open(record_path, "a", encoding="utf-8") as f:
        f.write(line)


def main(root_dir: Path, record_dir_name: str, record_file_name: str, allow_duplicate_today: bool):
    # 如果统计目录不存在 → 自动创建
    if not root_dir.exists():
        try:
            root_dir.mkdir(parents=True, exist_ok=True)
            print(f"已自动创建统计目录：{root_dir}")
        except Exception as e:
            print(f"创建目录失败 {root_dir}：{e}", file=sys.stderr)
            sys.exit(1)

    if not root_dir.is_dir():
        print(f"\n错误：{root_dir} 不是一个目录", file=sys.stderr)
        sys.exit(1)

    print(f"\n正在统计目录：{root_dir}")
    print("（跳过常见隐藏/虚拟环境目录）\n")

    total_files = 0
    grand_total = grand_blank = grand_comment = grand_import = grand_core = 0

    print(f"{'相对路径':<60} {'总':>5} {'空':>5} {'注':>5} {'导':>5} {'核':>5}")
    print("-" * 85)

    for file_path in root_dir.rglob("*.py"):
        if should_skip_dir(file_path.parent):
            continue
        total_files += 1
        t, b, c, i, core = count_code_lines(file_path)

        grand_total += t
        grand_blank += b
        grand_comment += c
        grand_import += i
        grand_core += core

        rel_path = file_path.relative_to(root_dir)
        print(f"{str(rel_path):<60} {t:>5} {b:>5} {c:>5} {i:>5} {core:>5}")

    print("-" * 85)

    if total_files == 0:
        print("未找到任何 .py 文件（可能是新创建的空目录）")
        # 可以选择是否继续记录空统计，这里默认继续
        # 如果你不想记录空目录的统计，可以在这里 return

    if grand_total > 0:
        blank_pct = grand_blank / grand_total * 100
        comment_pct = grand_comment / grand_total * 100
        import_pct = grand_import / grand_total * 100
        core_pct = grand_core / grand_total * 100
    else:
        blank_pct = comment_pct = import_pct = core_pct = 0.0

    stats = {
        "files": total_files,
        "total": grand_total,
        "blank": grand_blank,
        "blank_pct": blank_pct,
        "comment": grand_comment,
        "comment_pct": comment_pct,
        "imports": grand_import,
        "import_pct": import_pct,
        "core": grand_core,
        "core_pct": core_pct
    }

    print(f"共扫描 {total_files} 个 Python 文件")
    print("\n汇总：")
    print(f"  总行数     : {grand_total:>6,}")
    print(f"  空行       : {grand_blank:>6,}  ({blank_pct:5.1f}%)")
    print(f"  注释行     : {grand_comment:>6,}  ({comment_pct:5.1f}%)")
    print(f"  纯导入行   : {grand_import:>6,}  ({import_pct:5.1f}%)")
    print(f"  核心代码行 : {grand_core:>6,}  ({core_pct:5.1f}%)")

    # 记录文件夹（脚本所在目录下）
    script_dir = Path(__file__).parent.resolve()
    record_dir = script_dir / record_dir_name
    record_dir.mkdir(exist_ok=True)  # 自动创建 records 文件夹
    record_path = record_dir / record_file_name

    today = datetime.now().date()
    last_record = get_last_record(record_path)

    should_record = True

    if not allow_duplicate_today and last_record:
        _, last_date = last_record
        if last_date and last_date.date() == today:
            should_record = False
            print(f"\n今天 ({today}) 已记录过，跳过本次记录。")

    if should_record:
        save_record(stats, record_path)
        print(f"\n已记录到：{record_path}")

        if last_record and last_record[0] is not None and last_record[0] > 0:
            prev_core, prev_date = last_record
            growth = (grand_core - prev_core) / prev_core * 100
            sign = "+" if growth >= 0 else ""
            print(f"核心代码行 与 {prev_date.strftime('%Y-%m-%d')} 相比："
                  f" {sign}{growth:+.1f}% "
                  f"（{prev_core:,} → {grand_core:,}）")
        elif last_record and last_record[0] == 0:
            print("上次记录核心代码为 0，无法计算增长率")
        else:
            print("首次记录，无同比数据")


if __name__ == "__main__":
    # ── 配置区 ──
    TARGET_DIR = Path(__file__).parents[1] / 'app'
    RECORD_DIR_NAME = "records"
    RECORD_FILE_NAME = "line_record.log"
    ALLOW_DUPLICATE_TODAY = True
    # ─────────────

    root_dir = Path(TARGET_DIR).resolve()

    try:
        main(
            root_dir=root_dir,
            record_dir_name=RECORD_DIR_NAME,
            record_file_name=RECORD_FILE_NAME,
            allow_duplicate_today=ALLOW_DUPLICATE_TODAY
        )
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n发生错误：{e}", file=sys.stderr)
        sys.exit(1)
