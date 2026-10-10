#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""《偏航》QA41 第二章作者级WORKING合同的声明结构验收器。
文件使用说明：用途=读取候选章节（仅测试fixture）和4项合同见证记录，找出缺项或证据锚不在正文；新增原因=QA28表格不能自动防止空锚/假锚；内容边界=只测文本锚与填表逻辑，不验证合法审批、不创建CH2真实正文；状态=CANDIDATE/SHADOW_ONLY/NOT_STORY_CANON/NOT_V12_STABLE_OBJECT；依赖=第二章WORKING单章合同第13节、QA15/QA28/QA33；后续使用=--self-test或--body file --witness JSON；关系=补充QA28的前置结构检验；禁止=直接签发真实章节PASS或从fixture创造正史。
变更记录：2026-10-08初建，任何自报材料仍需独立语义与上游审核。
"""
import json, argparse
from pathlib import Path
REQUIRED={'AUTHORITY_TRIPLE_SPLIT','WRITTEN_REVIEW_SCOPE','NARROW_PARTICIPATION','OBJECTIVE_VERSION_DIFFERENCE'}
FORBIDDEN=('她恢复了董事席位','容既白替她恢复了全部权限','09-A正文揭晓')
def check(body,witness):
    problems=[]
    if not isinstance(witness,dict) or not isinstance(witness.get('claims'),list):return {'verdict':'HOLD_SCHEMA','problems':['MISSING_CLAIMS'],'production_authorized':False}
    statuses={}
    for i,x in enumerate(witness['claims']):
        if not isinstance(x,dict) or any(k not in x for k in ('code','anchor','evidence_type','cost_anchor','status')):
            problems.append(f'C{i+1}:BAD_ENTRY');continue
        code=x['code']
        if code in statuses:problems.append(code+':DUPLICATE')
        statuses[code]=True
        if code not in REQUIRED:problems.append(code+':UNKNOWN_CLAIM')
        if x['status']!='CANDIDATE_OBSERVED':problems.append(code+':NOT_OBSERVED')
        if x['evidence_type'] not in ('DIALOGUE_AND_PROCEDURE','WRITTEN_RECORD','LAWFUL_ACCESS_ACTION','DOCUMENT_COMPARISON'):
            problems.append(code+':BAD_EVIDENCE_TYPE')
        for k in ('anchor','cost_anchor'):
            if not isinstance(x[k],str) or len(x[k].strip())<3 or x[k] not in body:
                problems.append(code+':MISSING_'+k.upper())
    for code in REQUIRED-statuses.keys():problems.append(code+':MISSING_REQUIRED')
    for p in FORBIDDEN:
        if p in body:problems.append('FORBIDDEN_PROPOSED_OUTCOME:'+p)
    return {'verdict':'WITNESS_ANCHORS_MATCH_ONLY' if not problems else 'HOLD_CONTRACT_WITNESS',
            'problems':problems,'claim_count':len(witness['claims']),
            'body_authenticity_or_literary_quality_verified':False,'production_authorized':False}
def self_test():
    anchors={'AUTHORITY_TRIPLE_SPLIT':('历史授权已被终止','她接受旧便利失效'),
             'WRITTEN_REVIEW_SCOPE':('复核范围写入表格','责任岗增加留痕'),
             'NARROW_PARTICIPATION':('获准提交审计意见','仍不得进入核心治理层'),
             'OBJECTIVE_VERSION_DIFFERENCE':('形成时间出现不一致','必须申请形成链原件')}
    body='。'.join(a+'，'+b for a,b in anchors.values())+'。'
    def base():return {'claims':[{'code':k,'anchor':a,'cost_anchor':c,'evidence_type':'WRITTEN_RECORD','status':'CANDIDATE_OBSERVED'} for k,(a,c) in anchors.items()]}
    import copy
    cases=[]
    def test(name,b,w,expected):
        z=check(b,w)['verdict'];cases.append({'case':name,'actual':z,'expected':expected,'pass':z==expected})
    test('all_four_synthetic_witnesses',body,base(),'WITNESS_ANCHORS_MATCH_ONLY')
    t=base();t['claims'].pop();test('missing_fourth',body,t,'HOLD_CONTRACT_WITNESS')
    t=base();t['claims'][0]['anchor']='并不存在的段落';test('invented_anchor',body,t,'HOLD_CONTRACT_WITNESS')
    t=base();t['claims'][1]['cost_anchor']='';test('cost_missing',body,t,'HOLD_CONTRACT_WITNESS')
    test('forbidden_power_restoration',body+'她恢复了董事席位',base(),'HOLD_CONTRACT_WITNESS')
    t=base();t['claims'].append(copy.deepcopy(t['claims'][0]));test('duplicate',body,t,'HOLD_CONTRACT_WITNESS')
    t=base();t['claims'][0]['status']='PLANNED';test('plan_as_observed',body,t,'HOLD_CONTRACT_WITNESS')
    t=base();t['claims'][0]['evidence_type']='INTUITION';test('intuition_as_record',body,t,'HOLD_CONTRACT_WITNESS')
    test('empty_claims',body,{'claims':[]},'HOLD_CONTRACT_WITNESS')
    test('not_object',body,[],'HOLD_SCHEMA')
    return {'pass_count':sum(c['pass'] for c in cases),'total':len(cases),'cases':cases,
            'note':'Matching an anchor is not a substitute for verifying its meaning or its true source.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--body',type=Path);p.add_argument('--witness',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.self_test:d=self_test()
    else:
        if not a.body or not a.witness:p.error('need --body and --witness')
        try:d=check(a.body.read_text(encoding='utf8'),json.loads(a.witness.read_text(encoding='utf8')))
        except (OSError,ValueError):d={'verdict':'HOLD_INPUT','problems':['UNREADABLE_INPUT'],'production_authorized':False}
    s=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(s,encoding='utf8')
    else:print(s,end='')
    return 0 if a.self_test and d['pass_count']==d['total'] else (0 if not a.self_test else 3)
if __name__=='__main__':raise SystemExit(main())
