#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""《偏航》QA39 信息权限声明（非原文抽取）只读检查器。
文件使用说明：用途=验证审稿员提交的四方信息披露事件中是否有上游证据、可见性和角色知情权限；新增原因=QA07/QA18/QA27是人工方法，尚缺可跑的声明一致性负例；内容边界=不从正文判断心智状态，不推断真实秘密，不创建运行INFO事实；状态=CANDIDATE/SHADOW_ONLY/NOT_STORY_CANON/NOT_V12_STABLE_OBJECT；依赖=根前置、QA07/QA18/QA27、R003 committed info及第二章WORKING限制；后续使用=--self-test或--input 结构化json；关系=供人工工单辅助检测，不代替QA16、V12和事实审查；禁止=对任意情节自动放行或把虚构测试变正史。
变更记录：2026-10-08初建，人工输入的声明可能造假，所有匹配仍不是事实认证。
"""
import json,argparse
from pathlib import Path
ACTORS={'READER','LQW','RJB','OTHERS'}
SENSITIVE={'09A_CONTENT','09A_HOLDER','09A_MISSING_REASON','Q_EQUALS_LQW','WHITENOISE_EQUALS_LQW','SIX_YEARS_FULL','NANJIA_AB_DECISION','DONGFU_AUTO_KNOWLEDGE'}
KNOWN={'09A_NODE_EXISTS','IDENTITY_VERIFIED','NO_AUTOMATIC_GOVERNANCE_RESTORATION'}
CHANNELS={'ONSCREEN','VERBAL_DISCLOSURE','LAWFUL_RECORD','DIRECT_OBSERVATION','INFERENCE','RUMOR'}
def check(doc):
    holds=[]; seen=set()
    if not isinstance(doc,dict) or not isinstance(doc.get('events'),list):return {'verdict':'HOLD_SCHEMA','holds':['INVALID_SCHEMA'],'production_authorized':False}
    for idx,x in enumerate(doc['events']):
        prefix=f'E{idx+1}'
        if not isinstance(x,dict) or any(k not in x for k in ('id','actor','claim','mode','channel','source_ref','text_anchor','source_status')):
            holds.append(prefix+':MISSING_FIELDS');continue
        if x['id'] in seen:holds.append(prefix+':DUPLICATE_ID')
        seen.add(x['id'])
        actor,claim,mode,channel=x['actor'],x['claim'],x['mode'],x['channel']
        if actor not in ACTORS or channel not in CHANNELS or mode not in {'FACT','INFERENCE','BELIEF','UNOBSERVED'}:
            holds.append(prefix+':BAD_ENUM');continue
        if not isinstance(x['source_ref'],str) or not x['source_ref'].strip() or x['source_ref'] in ('UNKNOWN','NONE'):
            holds.append(prefix+':NO_SOURCE')
        if not isinstance(x['text_anchor'],str) or not x['text_anchor'].strip():holds.append(prefix+':NO_TEXT_ANCHOR')
        if x['source_status'] not in {'COMMITTED_R003','CH2_WORKING_PROPOSAL','AUTHOR_HYPOTHESIS','UNKNOWN'}:
            holds.append(prefix+':SOURCE_STATE_UNRECOGNIZED')
        # 已知的旧章限知：未来真实另有COMMITTED升级后须使用另一版source、不能靠本工具推断。
        if claim in SENSITIVE and mode=='FACT' and x['source_status']!='COMMITTED_NEWER_VERIFIED':
            holds.append(prefix+':SENSITIVE_FACT_WITHOUT_NEWER_COMMITTED_AUTHORITY')
        if mode=='FACT' and channel in ('INFERENCE','RUMOR'):holds.append(prefix+':INFERENCE_OR_RUMOR_CLAIMED_AS_FACT')
        if x['source_status']=='CH2_WORKING_PROPOSAL' and mode=='FACT':holds.append(prefix+':WORKING_PROMOTED_TO_FACT')
        if x['source_status']=='AUTHOR_HYPOTHESIS' and mode=='FACT':holds.append(prefix+':HYPOTHESIS_PROMOTED_TO_FACT')
        if claim=='DONGFU_AUTO_KNOWLEDGE' and actor!='READER' and mode in ('FACT','BELIEF'):
            holds.append(prefix+':UNJUSTIFIED_AUTO_CHARACTER_KNOWLEDGE')
    return {'verdict':'CLAIM_CHECK_ONLY' if not holds else 'HOLD_CLAIM_CHAIN','holds':holds,'event_count':len(doc['events']),
            'identity_or_actual_narrative_verified':False,'production_authorized':False}
def self_test():
    base={'events':[{'id':'T1','actor':'LQW','claim':'09A_NODE_EXISTS','mode':'FACT','channel':'LAWFUL_RECORD','source_ref':'EVID_000002','text_anchor':'09-A索引节点','source_status':'COMMITTED_R003'}]}
    import copy
    cases=[]
    def t(n,mut,exp):
        x=copy.deepcopy(base);mut(x);a=check(x)['verdict'];cases.append({'case':n,'expected':exp,'actual':a,'pass':exp==a})
    t('R003_NODE',lambda x:None,'CLAIM_CHECK_ONLY')
    t('INFO_CONTENT_OVERCLAIM',lambda x:x['events'][0].update(claim='09A_CONTENT'),'HOLD_CLAIM_CHAIN')
    t('UNKNOWN_SOURCE',lambda x:x['events'][0].update(source_ref='UNKNOWN'),'HOLD_CLAIM_CHAIN')
    t('RUMOR_AS_FACT',lambda x:x['events'][0].update(channel='RUMOR'),'HOLD_CLAIM_CHAIN')
    t('CH2_PLAN_AS_FACT',lambda x:x['events'][0].update(source_status='CH2_WORKING_PROPOSAL'),'HOLD_CLAIM_CHAIN')
    t('AUTHOR_HYPOTHESIS',lambda x:x['events'][0].update(source_status='AUTHOR_HYPOTHESIS'),'HOLD_CLAIM_CHAIN')
    t('NO_ANCHOR',lambda x:x['events'][0].update(text_anchor=''),'HOLD_CLAIM_CHAIN')
    t('Q_EQUALS_LQW',lambda x:x['events'][0].update(claim='Q_EQUALS_LQW'),'HOLD_CLAIM_CHAIN')
    t('DONGFU_CHARACTER_ASSUMPTION',lambda x:x['events'][0].update(actor='OTHERS',claim='DONGFU_AUTO_KNOWLEDGE',mode='BELIEF'),'HOLD_CLAIM_CHAIN')
    t('READER_INFERENCE',lambda x:x['events'][0].update(actor='READER',mode='INFERENCE',channel='INFERENCE'),'CLAIM_CHECK_ONLY')
    t('DUPLICATE',lambda x:x['events'].append(x['events'][0].copy()),'HOLD_CLAIM_CHAIN')
    t('WRONG_ACTOR',lambda x:x['events'][0].update(actor='BOSS'),'HOLD_CLAIM_CHAIN')
    return {'passed':sum(x['pass'] for x in cases),'total':len(cases),'cases':cases,'caveat':'Statements and claimed source refs are user supplied, not independently verified.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--input',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.self_test:d=self_test()
    else:
        if not a.input:p.error('--input required')
        try:d=check(json.loads(a.input.read_text(encoding='utf8')))
        except (OSError,ValueError):d={'verdict':'HOLD_INPUT','holds':['INVALID_OR_UNREADABLE_INPUT'],'production_authorized':False}
    s=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if a.out:a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(s,encoding='utf8')
    else:print(s,end='')
    return 0 if a.self_test and d['passed']==d['total'] else (0 if not a.self_test else 3)
if __name__=='__main__':raise SystemExit(main())
