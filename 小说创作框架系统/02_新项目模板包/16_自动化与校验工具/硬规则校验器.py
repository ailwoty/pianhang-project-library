#!/usr/bin/env python3
"""只读正文校验。0=已检查范围内通过；1=规则失败；2=输入/配置错误。"""
import argparse,json,sys
from 校验公共 import read,body_text,collect,load_config,check_body

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('target');ap.add_argument('--config');ap.add_argument('--recursive',action='store_true')
    ap.add_argument('--min-words',type=int);ap.add_argument('--max-words',type=int)
    ap.add_argument('--banned');ap.add_argument('--no-start-pronoun')
    ap.add_argument('--allow-unmarked',action='store_true',help='仅为旧格式全文检查；报告明确口径')
    args=ap.parse_args()
    try:
        rules=load_config(args.config)['text_rules'].copy() if args.config else {}
        if args.min_words is not None:rules['min_chars']=args.min_words
        if args.max_words is not None:rules['max_chars']=args.max_words
        if args.banned is not None:rules['banned_terms']=[w.strip() for w in args.banned.split(',') if w.strip()]
        if args.no_start_pronoun is not None:rules['no_start_pronoun']=[w.strip() for w in args.no_start_pronoun.split(',') if w.strip()]
        if rules.get('min_chars',0)<0 or rules.get('max_chars',0)<0 or (rules.get('max_chars',0) and rules.get('min_chars',0)>rules['max_chars']):
            raise ValueError('无效字数区间')
        files=collect(args.target,args.recursive);rows=[]
        for f in files:
            try:
                body,line=body_text(read(f),not args.allow_unmarked and rules.get('body_markers_required',True))
                row=check_body(body,rules,line);row['path']=str(f);rows.append(row)
            except ValueError as e:rows.append({'path':str(f),'failures':[str(e)]})
        failed=any(r['failures'] for r in rows)
        print(json.dumps({'status':'FAIL' if failed else 'PASS','scope':'全文旧格式' if args.allow_unmarked else '标记内正文','files':rows,'literary_quality':'NOT_TESTED'},ensure_ascii=False,indent=2))
        return 1 if failed else 0
    except (ValueError,OSError) as e:
        print(json.dumps({'status':'ERROR','error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
