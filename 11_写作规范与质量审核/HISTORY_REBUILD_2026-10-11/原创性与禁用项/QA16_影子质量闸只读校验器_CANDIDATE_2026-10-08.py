#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA16 | 影子质量闸，只读离线验证器。
STATUS: CANDIDATE / SHADOW_ONLY / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT
DESIGNATED_PATH: /偏航/11_写作规范与质量审核/原创性与禁用项/QA16_影子质量闸只读校验器_CANDIDATE_2026-10-08.py
文件用途：校验候选正文、source manifest、完整QA报告、拟议release凭证的哈希及业务字段一致性。
新增原因：QA13只定义接口字段，缺乏对换稿、来源变化、阻断项、无授权或伪造事后报告的可执行检查。
内容边界：仅本地只读，绝不向V12提交、不修改正文/报告/凭证、不验证签名/用户身份的真实性。
权威状态：CANDIDATE，不属于V12 stable objects，不是正式生产闸。
依赖：根级前置指令、QA-1.0/Q01—Q22、QA13影子方案。
后续调用：python QA16_...py --body file --sources file --report report.json --token token.json；--self-test跑合成用例。
关系：补充QA13；为QA17提供可复现影子验证；无法替代正式PREWRITE和维护事务。
禁止误用：结构匹配不等于凭证签发、身份验证、合章质量真正PASS或COMMITTED。
变更：2026-10-08首次建立。
"""
import argparse
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path

RULE_VERSION = 'QA-1.0'
MATRIX_VERSION = 'QA-MATRIX-1.0'

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _positive_int(v):
    return type(v) is int and v >= 0

def evaluate(body: bytes, sources: bytes, report_bytes: bytes, token: dict) -> dict:
    """SHA256 checks only provenance-consistency, not authenticity. Pure function; no I/O."""
    defects = []
    try:
        report = json.loads(report_bytes.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return {'verdict':'HOLD_REQUIRED_FIELD','reasons':['REPORT_JSON_INVALID'], 'production_authorized':False}
    required_token = ['subject_sha256', 'source_vector_sha256', 'qa_report_sha256',
                      'chapter_uid', 'qa_verdict', 'qa_rule_version', 'qa_matrix_version',
                      'subject_story_status', 'prewrite_status', 'user_approval_ref']
    required_report = ['chapter_uid', 'qa_verdict', 'subject_sha256', 'source_vector_sha256',
                       'p0_open', 'p1_open', 'p2_open', 'waivers', 'score', 'reviewer_id',
                       'reviewer_mode', 'qa_rule_version', 'qa_matrix_version']
    if any(k not in token for k in required_token) or any(k not in report for k in required_report):
        return {'verdict':'HOLD_REQUIRED_FIELD','reasons':['MISSING_REQUIRED_KEYS'], 'production_authorized':False}
    if not all(isinstance(token[k], str) and token[k].strip() for k in required_token):
        return {'verdict':'HOLD_REQUIRED_FIELD','reasons':['EMPTY_TOKEN_FIELD'], 'production_authorized':False}
    if not all(isinstance(report[k], str) and report[k].strip() for k in
               ['chapter_uid','qa_verdict','subject_sha256','source_vector_sha256','reviewer_id','reviewer_mode','qa_rule_version','qa_matrix_version']):
        return {'verdict':'HOLD_REQUIRED_FIELD','reasons':['EMPTY_REPORT_FIELD'], 'production_authorized':False}
    if token['subject_story_status'] != 'CANDIDATE':
        return {'verdict':'HOLD_SUBJECT_STATUS','reasons':['SUBJECT_MUST_BE_PRE_COMMIT_CANDIDATE'], 'production_authorized':False}
    if (token['qa_rule_version'] != RULE_VERSION or token['qa_matrix_version'] != MATRIX_VERSION or
        report['qa_rule_version'] != RULE_VERSION or report['qa_matrix_version'] != MATRIX_VERSION):
        return {'verdict':'HOLD_RULE_VERSION','reasons':['RULE_OR_MATRIX_VERSION_MISMATCH'], 'production_authorized':False}
    if token['prewrite_status'] != 'FRESH_VERIFIED_FOR_SUBJECT':
        return {'verdict':'HOLD_PREFLIGHT','reasons':['PREWRITE_NOT_FRESH_FOR_SUBJECT'], 'production_authorized':False}
    if token['subject_sha256'] != digest(body) or report['subject_sha256'] != digest(body):
        return {'verdict':'HOLD_BODY_HASH','reasons':['BODY_CONTENT_MISMATCH'], 'production_authorized':False}
    if token['source_vector_sha256'] != digest(sources) or report['source_vector_sha256'] != digest(sources):
        return {'verdict':'HOLD_SOURCE_VECTOR','reasons':['SOURCE_VECTOR_CONTENT_MISMATCH'], 'production_authorized':False}
    if token['qa_report_sha256'] != digest(report_bytes):
        return {'verdict':'HOLD_REPORT_HASH','reasons':['REPORT_CONTENT_MISMATCH'], 'production_authorized':False}
    if token['chapter_uid'] != report['chapter_uid'] or token['qa_verdict'] != report['qa_verdict']:
        return {'verdict':'HOLD_REQUIRED_FIELD','reasons':['REPORT_TOKEN_SUBJECT_OR_VERDICT_CONFLICT'], 'production_authorized':False}
    if not all(_positive_int(report[k]) for k in ['p0_open','p1_open','p2_open']):
        return {'verdict':'HOLD_REQUIRED_FIELD','reasons':['INVALID_BLOCKER_TYPE'], 'production_authorized':False}
    if report['p0_open'] != 0 or report['p1_open'] != 0:
        return {'verdict':'HOLD_BLOCKER','reasons':['P0_OR_P1_NONZERO'], 'production_authorized':False}
    if token['qa_verdict'] not in ('PASS','PASS_WITH_WAIVER'):
        return {'verdict':'HOLD_QA_VERDICT','reasons':['QA_NOT_PASSED'], 'production_authorized':False}
    if (not isinstance(report['score'],(int,float)) or type(report['score']) is bool or
        report['score'] < 85 or report['score'] > 100):
        return {'verdict':'HOLD_SCORE','reasons':['SCORE_BELOW_THRESHOLD_OR_INVALID'], 'production_authorized':False}
    waivers=report['waivers']
    if not isinstance(waivers,list) or any(not isinstance(x,str) or not x.strip() for x in waivers):
        return {'verdict':'HOLD_WAIVER','reasons':['WAIVERS_INVALID'], 'production_authorized':False}
    if report['p2_open']>0 and (token['qa_verdict']!='PASS_WITH_WAIVER' or len(waivers)<report['p2_open']):
        return {'verdict':'HOLD_WAIVER','reasons':['UNWAIVED_P2'], 'production_authorized':False}
    if token['qa_verdict']=='PASS_WITH_WAIVER' and not waivers:
        return {'verdict':'HOLD_WAIVER','reasons':['WAIVER_ID_MISSING'], 'production_authorized':False}
    if token['user_approval_ref'] in ('UNKNOWN','NONE','N_A','UNVERIFIED'):
        return {'verdict':'HOLD_USER_APPROVAL','reasons':['NO_APPROVED_500CHAR_SCOPE'], 'production_authorized':False}
    # This passes only *internal consistency*. A forged token/report can still be structurally self-consistent.
    return {'verdict':'SHADOW_MATCH_ONLY','reasons':['STRUCTURAL_MATCH_NOT_AUTHENTICATION'],
            'production_authorized':False,'validated_body_sha256':digest(body),
            'validated_source_sha256':digest(sources)}

def fixture():
    body='【合成测试】记录版本差异须保留形成时间。'.encode('utf-8')
    sources=b'TEST_SOURCE_VECTOR_A\n'
    report={'chapter_uid':'TEST_CHUID_001','qa_verdict':'PASS','subject_sha256':digest(body),
            'source_vector_sha256':digest(sources),'p0_open':0,'p1_open':0,'p2_open':0,
            'waivers':[], 'score':90, 'reviewer_id':'SYNTHETIC_REVIEWER',
            'reviewer_mode':'SYNTHETIC_NO_AUTHENTICATION','qa_rule_version':RULE_VERSION,
            'qa_matrix_version':MATRIX_VERSION}
    payload=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    token={'subject_sha256':digest(body),'source_vector_sha256':digest(sources),
           'qa_report_sha256':digest(payload),'chapter_uid':'TEST_CHUID_001','qa_verdict':'PASS',
           'qa_rule_version':RULE_VERSION,'qa_matrix_version':MATRIX_VERSION,
           'subject_story_status':'CANDIDATE','prewrite_status':'FRESH_VERIFIED_FOR_SUBJECT',
           'user_approval_ref':'SYNTHETIC_APPROVAL_TEST_ONLY'}
    return body,sources,report,token

def self_test():
    b,s,r,t=fixture()
    cases=[]
    def run(name,expected,mutate):
        body, src, rep, tok = b, s,copy.deepcopy(r),copy.deepcopy(t)
        body,src,rep,tok = mutate(body,src,rep,tok)
        raw=json.dumps(rep,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
        # Most changes require recomputing report-hash, to isolate target validator behavior.
        if name not in ('T06_MISSING_REPORT_HASH','T12_REPORT_TAMPER'):
            tok['qa_report_sha256']=digest(raw)
        result=evaluate(body,src,raw,tok)
        cases.append((name, expected, result['verdict'], expected==result['verdict'],result['production_authorized']))
    identity=lambda b,s,r,t:(b,s,r,t)
    run('T01_GOOD_SYNTHETIC','SHADOW_MATCH_ONLY',identity)
    run('T02_BODY_CHANGED','HOLD_BODY_HASH',lambda b,s,r,t:(b+b'X',s,r,t))
    run('T03_SOURCE_CHANGED','HOLD_SOURCE_VECTOR',lambda b,s,r,t:(b,s+b'Y',r,t))
    run('T04_P0','HOLD_BLOCKER',lambda b,s,r,t:(b,s,{**r,'p0_open':1},t))
    run('T05_P1','HOLD_BLOCKER',lambda b,s,r,t:(b,s,{**r,'p1_open':1},t))
    run('T06_MISSING_REPORT_HASH','HOLD_REQUIRED_FIELD',lambda b,s,r,t:(b,s,r,{k:v for k,v in t.items() if k!='qa_report_sha256'}))
    run('T07_QA_HOLD','HOLD_QA_VERDICT',lambda b,s,r,t:(b,s,{**r,'qa_verdict':'HOLD'},{**t,'qa_verdict':'HOLD'}))
    run('T08_EMPTY_WAIVER','HOLD_WAIVER',lambda b,s,r,t:(b,s,{**r,'qa_verdict':'PASS_WITH_WAIVER'},{**t,'qa_verdict':'PASS_WITH_WAIVER'}))
    run('T09_WAIVER_CANNOT_OVERRIDE_P1','HOLD_BLOCKER',lambda b,s,r,t:(b,s,{**r,'p1_open':1,'waivers':['W-1'],'qa_verdict':'PASS_WITH_WAIVER'},{**t,'qa_verdict':'PASS_WITH_WAIVER'}))
    run('T10_POSTCOMMIT','HOLD_SUBJECT_STATUS',lambda b,s,r,t:(b,s,r,{**t,'subject_story_status':'COMMITTED_CURRENT'}))
    run('T11_NO_USER_APPROVAL','HOLD_USER_APPROVAL',lambda b,s,r,t:(b,s,r,{**t,'user_approval_ref':'UNKNOWN'}))
    run('T12_REPORT_TAMPER','HOLD_REPORT_HASH',lambda b,s,r,t:(b,s,{**r,'score':91},t))
    run('T13_LOW_SCORE','HOLD_SCORE',lambda b,s,r,t:(b,s,{**r,'score':84},t))
    run('T14_RULE_CHANGED','HOLD_RULE_VERSION',lambda b,s,r,t:(b,s,r,{**t,'qa_rule_version':'QA-2.0'}))
    run('T15_STALE_PREFLIGHT','HOLD_PREFLIGHT',lambda b,s,r,t:(b,s,r,{**t,'prewrite_status':'STALE'}))
    run('T16_PENDING_PREFLIGHT','HOLD_PREFLIGHT',lambda b,s,r,t:(b,s,r,{**t,'prewrite_status':'UNKNOWN'}))
    run('T17_MISSING_REPORT_FIELD','HOLD_REQUIRED_FIELD',lambda b,s,r,t:(b,s,{k:v for k,v in r.items() if k!='reviewer_id'},t))
    run('T18_UNWAIVED_P2','HOLD_WAIVER',lambda b,s,r,t:(b,s,{**r,'p2_open':1},t))
    run('T19_WAIVED_P2','SHADOW_MATCH_ONLY',lambda b,s,r,t:(b,s,{**r,'p2_open':1,'waivers':['W-1'],'qa_verdict':'PASS_WITH_WAIVER'},{**t,'qa_verdict':'PASS_WITH_WAIVER'}))
    run('T20_FALSE_ZERO_P0','HOLD_REQUIRED_FIELD',lambda b,s,r,t:(b,s,{**r,'p0_open':'0'},t))
    all_ok=all(x[3] and x[4] is False for x in cases)
    return {'self_test_passed':all_ok,'passed':sum(x[3] for x in cases),'total':len(cases),
            'cases':[{'id':name,'expected':e,'actual':a,'match':ok,'production_authorized':prod} for name,e,a,ok,prod in cases],
            'warning':'SHADOW_MATCH_ONLY means only structural self-consistency; token authenticity, user identity, real PREWRITE, and V12 authorization are NOT verified.'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--body',type=Path)
    p.add_argument('--sources',type=Path)
    p.add_argument('--report',type=Path)
    p.add_argument('--token',type=Path)
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    if args.self_test:
        result=self_test()
        ec=0 if result['self_test_passed'] else 3
    else:
        if any(v is None for v in (args.body,args.sources,args.report,args.token)):
            p.error('Must supply --body --sources --report --token, or --self-test')
        try:
            result=evaluate(args.body.read_bytes(),args.sources.read_bytes(),args.report.read_bytes(),
                            json.loads(args.token.read_text(encoding='utf-8')))
        except (OSError,ValueError) as exc:
            result={'verdict':'HOLD_REQUIRED_FIELD','reasons':[f'INPUT_UNAVAILABLE:{type(exc).__name__}'],
                    'production_authorized':False}
        ec=0 if result['verdict']=='SHADOW_MATCH_ONLY' else 2
    txt=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(txt,encoding='utf-8')
    else:
        print(txt)
    return ec

if __name__=='__main__':
    sys.exit(main())
