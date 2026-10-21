#!/usr/bin/env python3
"""精确路径全量核对：不跳过模板文件，不以通配符隐藏漏项。"""
import argparse,json,sys
from pathlib import Path
from 校验公共 import asset_check
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',required=True)
    ap.add_argument('--root');ap.add_argument('--strict',action='store_true',help='兼容旧命令；现默认严格')
    a=ap.parse_args()
    try:
        r=asset_check(a.root or Path(a.manifest).resolve().parent,a.manifest)
        r['status']='FAIL' if r['failures'] else 'PASS';print(json.dumps(r,ensure_ascii=False,indent=2));return int(bool(r['failures']))
    except (ValueError,OSError) as e:print(json.dumps({'status':'ERROR','error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
