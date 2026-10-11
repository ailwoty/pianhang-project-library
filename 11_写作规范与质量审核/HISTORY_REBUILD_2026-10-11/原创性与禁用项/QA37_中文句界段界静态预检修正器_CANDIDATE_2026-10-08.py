#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《偏航》QA37 中文句界/段界预检 v2；零三方依赖。
文件使用说明：用途=改进QA05把单行误当一段、句界误切的问题；新增原因=QA05产生多项待人工复核的物理行候选；内容边界=静态疑点不是P0裁决，不判断章节文学质量或故事真值；状态=CANDIDATE/NOT_STORY_CANON/NOT_V12_STABLE_OBJECT；依赖=根级写作规范/QA05/QA04；后续使用=python 本脚本 BODY.md --out out.json；关系=QA05非破坏性后继实验，不覆盖QA05；禁止=直接据此COMMIT、自动判PASS或自改正文。
变更记录：2026-10-08建立实验扫描器与固定测试，R003只读。
"""
import re,argparse,hashlib,json
from pathlib import Path
BANNED=('指尖','冷笑','这就够了','丰富','细腻','高级','专业')
# 以句号、叹号和问号为候选句尾；引号闭合不单独算新句。
END=re.compile(r'[。！？!?]+[”’」』]*')
HAN=re.compile(r'[\u4e00-\u9fff]')
HEADER=re.compile(r'^# 第[一二三四五六七八九十百千0-9]+章[｜|].*$',re.M)

def extract(text):
    m=HEADER.search(text)
    return (text[m.start():],text[:m.start()].count('\n')+1,True) if m else (text,1,False)

def scan(text):
    body,base,removed=extract(text)
    items=[]; paras=[]; cur=[]; start=None
    def emit():
        nonlocal cur,start
        if cur:paras.append((start,' '.join(cur)));cur=[];start=None
    for n,s in enumerate(body.splitlines(),base):
        st=s.strip()
        if not st or st=='---':emit();continue
        if st.startswith('#'):emit();continue
        if start is None:start=n
        cur.append(st)
    emit()
    sentence_total=0
    for line,p in paras:
        for word in BANNED:
            for m in re.finditer(re.escape(word),p):items.append({'kind':'BANNED_LEXEME','line':line,'anchor':word,'offset':m.start(),'review':'CONFIRM_CONTEXT'})
        for m in re.finditer('——',p):items.append({'kind':'EM_DASH','line':line,'anchor':'——','offset':m.start(),'review':'CONFIRM_RULE'})
        parts=[q.strip(' \t“”‘’') for q in END.split(p)];ends=list(END.finditer(p));chunks=[];pos=0
        for m in ends:
            c=p[pos:m.start()].strip(' \t“”‘’');pos=m.end()
            if c:chunks.append(c)
        tail=p[pos:].strip(' \t“”‘’')
        if tail:chunks.append(tail)
        sentence_total+=len(chunks)
        for c in chunks:
            # 中文字数供预检，英文、标号和数字句依然需要人工判断是否适用根级限制。
            count=len(HAN.findall(c))
            if 0<count<=5:items.append({'kind':'SHORT_HAN_SENTENCE_CANDIDATE','line':line,'anchor':c[:75],'han_count':count,'review':'HUMAN_ADJUDICATION'})
        if len(chunks)==1 and ends:
            items.append({'kind':'ONE_SENTENCE_PARAGRAPH_CANDIDATE','line':line,'anchor':p[:75],'review':'HUMAN_ADJUDICATION'})
        if len(chunks)==0:items.append({'kind':'NO_SENTENCE_TERMINATOR_CANDIDATE','line':line,'anchor':p[:75],'review':'HUMAN_ADJUDICATION'})
    counts={k:sum(1 for x in items if x['kind']==k) for k in sorted(set(x['kind'] for x in items))}
    return {'read_only':True,'full_sha256':hashlib.sha256(text.encode()).hexdigest(),
            'chapter_section_detected':removed,'paragraphs_by_blank_lines':len(paras),
            'sentence_candidates':sentence_total,'counts':counts,'items':items,
            'verdict':'REVIEW_REQUIRED_NOT_PASS','false_positive_warning':'Line anchors indicate paragraph start; quotation and embedded speech require semantic review.'}
def self_test():
    tests=[('joined_lines','甲乙丙丁戊己，\n庚辛壬癸子丑。',{'ONE_SENTENCE_PARAGRAPH_CANDIDATE':1}),
           ('two_sentences','甲乙丙丁戊己。甲乙丙丁戊己。',{}),
           ('banned','她的指尖停住。',{'BANNED_LEXEME':1}),
           ('dash','他答应——又否认。',{'EM_DASH':1}),
           ('short','够了。',{'SHORT_HAN_SENTENCE_CANDIDATE':1}),
           ('metadata_ignored','CHINESE_CHAR_COUNT: 专业\n# 第一章｜标题\n这是正常句子的内容。',{}),
           ('double_quote','“这是一个完整句子。”',{'ONE_SENTENCE_PARAGRAPH_CANDIDATE':1}),
           ('separate_paragraph','甲乙丙丁戊己。\n\n庚辛壬癸子丑。',{'ONE_SENTENCE_PARAGRAPH_CANDIDATE':2})]
    results=[]
    for name,s,expected in tests:
        c=scan(s)['counts'];ok=all(c.get(k,0)==v for k,v in expected.items())
        if name=='two_sentences':ok &= c.get('ONE_SENTENCE_PARAGRAPH_CANDIDATE',0)==0
        if name=='metadata_ignored':ok &= c.get('BANNED_LEXEME',0)==0
        if name=='joined_lines':ok &= scan(s)['paragraphs_by_blank_lines']==1
        results.append({'case':name,'expected_subset':expected,'actual':c,'pass':ok})
    return {'pass_count':sum(x['pass'] for x in results),'total':len(results),'cases':results}
def main():
    p=argparse.ArgumentParser();p.add_argument('path',nargs='?',type=Path);p.add_argument('--self-test',action='store_true');p.add_argument('--out',type=Path);a=p.parse_args()
    if a.self_test:r=self_test()
    else:
        if not a.path:p.error('source required')
        r=scan(a.path.read_text(encoding='utf8'))
    s=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(s,encoding='utf8')
    else:print(s,end='')
    return 0 if a.self_test and r['pass_count']==r['total'] else (0 if not a.self_test else 3)
if __name__=='__main__':raise SystemExit(main())
