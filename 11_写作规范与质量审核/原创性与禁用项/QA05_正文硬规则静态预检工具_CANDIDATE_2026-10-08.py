#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《偏航》QA-05 正文硬规则静态预检工具。STATUS: CANDIDATE / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT
文件用途：只读扫描禁用词、句长、单句行、数字、破折号的疑点，给Q09/Q21复核。
新增原因：人工审核无法稳定检出所有词面违规，须加入可复现的只读机器候选。
内容边界：脚本不更改原文，不裁决真实正史、不签发PASS、不触碰V12。
依赖与上游：2026-10-08根级前置指令、11目录QA总规和Q01—Q22矩阵。
后续使用方法：python 此脚本 正文.md --out 输出.json；无--out时输出JSON至标准输出。
与其他文件关系：给QA04及工单提供位置，不取代人工审核与QA凭证。
禁止误用：数字索引与语言禁令需语境复核；空扫描不等于PASS。
更新记录：2026-10-08建立只读工具，不改变任何正文。
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
BANNED = ['指尖','冷笑','这就够了','丰富','细腻','高级','专业']
CUT = re.compile(r'[。！？!?]+')
STRIP = re.compile(r'[\s，。！？!?,.;；：“”‘’（）()『』「」、…—\-\d]+')
def scan(source: str) -> dict:
    m = re.search(r'^# 第[一二三四五六七八九十百千0-9]+章[｜|].*$',source,flags=re.M)
    offset=m.start() if m else 0
    body=source[offset:]
    out={'status':'REVIEW_REQUIRED','read_only':True,'sha256_full':hashlib.sha256(source.encode()).hexdigest(),
         'sha256_body_section':hashlib.sha256(body.encode()).hexdigest(),'ignored_metadata':bool(m),'items':[]}
    def record(code,line,text,**kw):out['items'].append({'code':code,'line':line,'text':text,'human_review':True,**kw})
    for line_no,line in enumerate(body.splitlines(),source[:offset].count('\n')+1):
        s=line.strip()
        if not s or s.startswith('#') or s=='---':continue
        for word in BANNED:
            for p in re.finditer(re.escape(word),s):record('Q21_BANNED_LEXEME',line_no,word,position=p.start())
        for p in re.finditer('——',s):record('Q21_EM_DASH',line_no,'——',position=p.start())
        for part in CUT.split(s):
            q=part.strip(' \t“”‘’'); count=len(STRIP.sub('',q))
            if 0<count<=5:record('Q21_SHORT_SENTENCE_CANDIDATE',line_no,q[:80],count=count)
        if CUT.search(s) and sum(bool(x.strip()) for x in CUT.split(s))==1:
            record('Q21_ONE_SENTENCE_LINE_CANDIDATE',line_no,s[:80])
        for p in re.finditer(r'\d+',s):record('Q21_DIGIT_REVIEW',line_no,p.group())
    counts={}
    for i in out['items']:counts[i['code']]=counts.get(i['code'],0)+1
    out['counts']=counts
    out['final_verdict']='UNDECIDED_REQUIRES_INDEPENDENT_HUMAN_QA'
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('path',type=Path);ap.add_argument('--out',type=Path)
    a=ap.parse_args(); d=scan(a.path.read_text(encoding='utf8'));d['subject_path']=str(a.path)
    txt=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(txt,encoding='utf8')
    else:print(txt)
