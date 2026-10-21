#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬规则校验器（只读，不做任何修改）
===================================
检查正文文件的硬规则：字数 / 中文引号配对 / ASCII 引号 / 破折号 / 禁字 / 段落纪律 / 段首代词。

用法:
    python 硬规则校验器.py <正文文件或目录> [选项]

选项:
    --min-words 2700 --max-words 3300   字数区间（去空白；默认 0-100000）
    --banned "衡,聆,宁,常,邵"            禁字表（逗号分隔）
    --no-start-pronoun "她,他"          段首禁用单字代词（逗号分隔）
    --recursive                          目录模式递归扫描 .md

输出: 每项 PASS/FAIL + 计数与位置；退出码 0=全过, 1=有 FAIL。
仅标准库，python 3.8+。
"""

import argparse
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def read_text(path):
    """读取文本文件，兼容 UTF-8 有/无 BOM。"""
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    # 兜底：按本地码页尝试（GBK）
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


def check_file(path, args):
    text = read_text(path)
    lines = text.splitlines()
    results = []

    def add(item, ok, detail):
        results.append((item, ok, detail))

    # 1. 字数（去空白）
    body = re.sub(r"\s", "", text)
    wc = len(body)
    ok = (args.min_words <= wc <= args.max_words) if args.max_words > 0 else wc >= args.min_words
    add("字数", ok, f"{wc} 字（区间 {args.min_words}-{args.max_words or '∞'}）")

    # 2. 中文引号配对（双引号“” 与 单引号‘’）
    dq_open = text.count("“")
    dq_close = text.count("”")
    sq_open = text.count("‘")
    sq_close = text.count("’")
    ok = (dq_open == dq_close) and (sq_open == sq_close)
    add("中文引号配对", ok, f"“{dq_open} / ”{dq_close}；‘{sq_open} / ’{sq_close}")

    # 3. ASCII 直引号
    ascii_dq = text.count('"')
    ascii_sq = text.count("'")
    ok = (ascii_dq == 0 and ascii_sq == 0)
    add("ASCII引号清零", ok, f'直双引号 {ascii_dq} 处；直单引号 {ascii_sq} 处')

    # 4. 破折号
    dash = sum(text.count(p) for p in ["——", "—", "--", "–"])
    ok = dash == 0
    add("破折号清零", ok, f"{dash} 处")

    # 5. 禁字
    banned = [b for b in args.banned if b]
    hits = []
    if banned:
        for i, line in enumerate(lines, 1):
            for b in banned:
                if b in line:
                    hits.append((i, b))
    ok = len(hits) == 0
    detail = "无" if not hits else "; ".join(f"行{i}:{b}" for i, b in hits[:10])
    add("禁字", ok, detail or "（未配置禁字表）")

    # 6. 段落纪律
    #   一般叙述段 30-80 字、单段上限 150；对话（含引号行）豁免下限；连续短段(>=3 段均<20 且非对话)告警
    over_long = []
    short_run = 0
    max_short_run = 0
    total_short = 0
    for i, line in enumerate(lines, 1):
        stripped = re.sub(r"\s", "", line)
        if not stripped:
            continue
        if len(stripped) > 150:
            over_long.append((i, len(stripped)))
        is_dialog = ("“" in line or "”" in line)
        if len(stripped) < 20 and not is_dialog:
            total_short += 1
            short_run += 1
            max_short_run = max(max_short_run, short_run)
        else:
            short_run = 0
    ok = (len(over_long) == 0) and (max_short_run < 3)
    detail = f"超150字段落 {len(over_long)} 处；最长连续短段 {max_short_run} 段；短段总数 {total_short}"
    if over_long:
        detail += "；超长示例 " + "; ".join(f"行{i}:{n}字" for i, n in over_long[:5])
    add("段落纪律", ok, detail)

    # 7. 段首禁用单字代词
    starters = [p for p in args.no_start_pronoun if p]
    pron_hits = []
    if starters:
        for i, line in enumerate(lines, 1):
            s = line.lstrip()
            if s and s[0] in starters:
                pron_hits.append((i, s[0]))
    ok = len(pron_hits) == 0
    detail = "无" if not pron_hits else "; ".join(f"行{i}:‘{p}’" for i, p in pron_hits[:10])
    add("段首代词规范", ok, detail or "（未配置）")

    return results


def main():
    ap = argparse.ArgumentParser(description="正文硬规则校验器（只读）")
    ap.add_argument("target", help="正文文件或目录")
    ap.add_argument("--min-words", type=int, default=0)
    ap.add_argument("--max-words", type=int, default=0, help="0=不设上限")
    ap.add_argument("--banned", default="", help="禁字表，逗号分隔")
    ap.add_argument("--no-start-pronoun", default="", help="段首禁用单字代词，逗号分隔")
    ap.add_argument("--recursive", action="store_true", help="目录模式递归")
    args = ap.parse_args()

    args.banned = [b.strip() for b in args.banned.split(",")]
    args.no_start_pronoun = [p.strip() for p in args.no_start_pronoun.split(",")]

    files = []
    if os.path.isfile(args.target):
        files = [args.target]
    else:
        for root, _, names in os.walk(args.target):
            for n in names:
                if n.lower().endswith(".md"):
                    files.append(os.path.join(root, n))
            if not args.recursive:
                break

    if not files:
        print("未找到任何 .md 文件")
        sys.exit(1)

    overall = True
    for fp in sorted(files):
        print(f"\n===== {fp} =====")
        for item, ok, detail in check_file(fp, args):
            flag = "PASS" if ok else "FAIL"
            if not ok:
                overall = False
            print(f"[{flag}] {item}: {detail}")

    print("\n===== 汇总 =====")
    print("全部通过" if overall else "存在 FAIL，请修正后重跑")
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
