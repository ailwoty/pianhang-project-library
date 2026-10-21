#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一致性回归检查（只读）
=====================
跨章设定一致性快查：
  A. 实体出场登记 —— 正文中每个已注册核心实体（人物/组织/地点）的出现次数；
  B. 严禁词泄露 —— 秘密/关键词表（如"金手指真相""某身份"）是否提前出现在正文。

用法:
    python 一致性回归检查.py --body <正文文件或目录> --registry <实体图谱.csv> [--forbidden "词1,词2"]

输出: 出场统计表 + 泄露告警；退出码 0=无泄露告警, 1=有告警。
仅标准库，python 3.8+。本脚本只做"机器可判"的检查，文学判断归 QA 五视角。
"""

import argparse
import csv
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_entities(registry_path):
    """读取实体图谱 CSV，返回 (类别, 名称) 列表。要求有'类别''现名'两列（或自动探测）。"""
    entities = []
    with open(registry_path, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        cat = (r.get("类别") or r.get("category") or "其他").strip()
        name = (r.get("现名") or r.get("name") or "").strip()
        if name:
            entities.append((cat, name))
    return entities


def main():
    ap = argparse.ArgumentParser(description="设定一致性回归检查（只读）")
    ap.add_argument("--body", required=True, help="正文文件或目录")
    ap.add_argument("--registry", required=True, help="实体图谱 CSV 路径")
    ap.add_argument("--forbidden", default="", help="严禁/秘密关键词，逗号分隔")
    ap.add_argument("--recursive", action="store_true", help="目录模式递归")
    args = ap.parse_args()

    entities = load_entities(args.registry)
    if not entities:
        print("[FAIL] 实体图谱为空或列名不匹配（需要 类别/现名 列）")
        sys.exit(1)

    forbidden = [w.strip() for w in args.forbidden.split(",") if w.strip()]

    files = []
    if os.path.isfile(args.body):
        files = [args.body]
    else:
        for root, _, names in os.walk(args.body):
            for n in names:
                if n.lower().endswith(".md"):
                    files.append(os.path.join(root, n))
            if not args.recursive:
                break

    text_all = "\n".join(read_text(f) for f in files)
    counts = {}
    for cat, name in entities:
        counts[name] = text_all.count(name)

    print("===== A. 实体出场登记 =====")
    for cat, name in entities:
        n = counts[name]
        flag = "出场" if n > 0 else "本批次未出场"
        print(f"  [{cat}] {name}: {n} 次  {flag}")

    print("\n===== B. 严禁词泄露检查 =====")
    leaked = []
    if forbidden:
        for w in forbidden:
            c = text_all.count(w)
            if c > 0:
                leaked.append((w, c))
    if leaked:
        for w, c in leaked:
            print(f"  [FAIL] 严禁词/秘密词 '{w}' 出现 {c} 次 —— 检查是否提前泄露")
        sys.exit(1)
    print("  无泄露告警（未配置则跳过）")
    sys.exit(0)


if __name__ == "__main__":
    main()
