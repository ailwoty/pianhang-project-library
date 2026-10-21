#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资产核对（只读）
===============
核对《项目资产清单 MANIFEST》与磁盘实际文件是否一致：
  A. MANIFEST 中登记的具体路径是否都存在；
  B. 磁盘上未被 MANIFEST 登记的 .md 文件（漏登）提示。

用法:
    python 资产核对.py --manifest <MANIFEST.md 路径> [--root <项目根目录>] [--strict]

规则: 路径中含【】占位符的行跳过（模板占位，无法判定存在性）；未登记的 .md 仅在 --strict 下报 FAIL。
"""

import argparse
import glob
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


def main():
    ap = argparse.ArgumentParser(description="MANIFEST 与磁盘核对（只读）")
    ap.add_argument("--manifest", required=True, help="MANIFEST.md 路径")
    ap.add_argument("--root", default=None, help="项目根目录（缺省用 MANIFEST 所在目录）")
    ap.add_argument("--strict", action="store_true", help="未登记文件也报 FAIL")
    args = ap.parse_args()

    root = args.root or os.path.dirname(os.path.abspath(args.manifest))
    text = read_text(args.manifest)

    # 提取反引号中的 .md / .py / .csv 路径
    paths = re.findall(r"`([^`]+\.(?:md|py|csv))`", text)
    # 通配/占位：含 *（glob）或 XXXX（模板占位）或【】（占位）
    concrete = [p for p in paths if "*" not in p and "XXXX" not in p and "【" not in p and "]" not in p]
    placeholders = [p for p in paths if p not in concrete]

    missing = []
    for p in concrete:
        full = os.path.normpath(os.path.join(root, p))
        if not os.path.exists(full):
            missing.append(p)

    # 通配路径用 glob 校验
    for p in [x for x in paths if "*" in x]:
        hits = glob.glob(os.path.join(root, p))
        if not hits:
            missing.append(p + "（通配无匹配）")

    # 扫描磁盘 .md 清单，找未登记项
    registered = set(os.path.normpath(p) for p in concrete)
    for p in [x for x in paths if "*" in x]:
        for hit in glob.glob(os.path.join(root, p)):
            rel = os.path.normpath(os.path.relpath(hit, root))
            registered.add(rel)
    # 占位路径（含【】）若磁盘真实存在则视为已登记
    for p in [x for x in paths if "【" in x]:
        if os.path.exists(os.path.join(root, p)):
            registered.add(os.path.normpath(p))
    disk = set()
    for r, _, names in os.walk(root):
        for n in names:
            if n.lower().endswith((".md", ".py", ".csv")):
                rel = os.path.normpath(os.path.relpath(os.path.join(r, n), root))
                disk.add(rel)
    unregistered = sorted(disk - registered)

    print(f"===== 资产核对（root={root}）=====")
    print(f"MANIFEST 登记具体路径: {len(concrete)}；占位路径（跳过）: {len(placeholders)}")
    if missing:
        print(f"\n[FAIL] MANIFEST 中登记但磁盘不存在的文件（{len(missing)}）:")
        for p in missing:
            print(f"  - {p}")
    else:
        print("\n[PASS] MANIFEST 登记路径全部存在")

    if unregistered:
        flag = "FAIL" if args.strict else "WARN"
        print(f"\n[{flag}] 磁盘存在但 MANIFEST 未登记的文件（{len(unregistered)}）:")
        for p in unregistered[:30]:
            print(f"  - {p}")
        if len(unregistered) > 30:
            print(f"  … 其余 {len(unregistered) - 30} 个略")
    else:
        print("\n[PASS] 磁盘文件全部已登记")

    failed = bool(missing) or (args.strict and bool(unregistered))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
