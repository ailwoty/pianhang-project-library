#!/usr/bin/env python3
"""只读词面检查。无法识别未知实体、谎言语义、所有知情越界或时间线矛盾。"""
import argparse,csv,json,sys
from 校验公共 import read,body_text,collect

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--body',required=True);ap.add_argument('--registry',required=True)
    ap.add_argument('--forbidden',default='');ap.add_argument('--recursive',action='store_true')
    args=ap.parse_args()
    try:
        files=collect(args.body,args.recursive)
        with open(args.registry,encoding='utf-8-sig',newline='') as f:
            dr=csv.DictReader(f)
            if not dr.fieldnames or not {'实体ID','类别','现名'}.issubset(dr.fieldnames):raise ValueError('注册表缺少实体ID/类别/现名列')
            rows=list(dr)
        if not rows:raise ValueError('注册表为空，未完成注册，不能判PASS')
        ids=set();names=set()
        for r in rows:
            if not r['实体ID'] or not r['现名'] or '【' in r['现名']:raise ValueError('注册表有空值/模板名')
            if r['实体ID'] in ids or r['现名'] in names:raise ValueError('注册表实体ID/现名重复')
            ids.add(r['实体ID']);names.add(r['现名'])
        texts=[(str(f),body_text(read(f))[0]) for f in files]
        hits=[]
        for word in (x.strip() for x in args.forbidden.split(',')):
            if word:
                for p,text in texts:
                    if word in text:hits.append({'path':p,'term':word,'count':text.count(word)})
        counts=[{'id':r['实体ID'],'name':r['现名'],'mentions':sum(t.count(r['现名']) for p,t in texts)} for r in rows]
        print(json.dumps({'status':'FAIL' if hits else 'PASS','registered_mentions':counts,'forbidden_hits':hits,
                          'semantic_consistency':'NOT_TESTED','unknown_entities':'NOT_TESTED','forbidden_check':'CHECKED' if args.forbidden else 'SKIPPED_NOT_CONFIGURED'},ensure_ascii=False,indent=2))
        return 1 if hits else 0
    except (ValueError,OSError,csv.Error) as e:
        print(json.dumps({'status':'ERROR','error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
