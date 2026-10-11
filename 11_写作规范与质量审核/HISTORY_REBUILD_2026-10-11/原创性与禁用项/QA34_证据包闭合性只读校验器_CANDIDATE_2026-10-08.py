#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《偏航》QA34 离线证据包闭合性校验。
文件使用说明：用途=冻结且验证报告引用的文件是否真实存在、内容指纹是否匹配；新增原因=QA16结构匹配未验证源文件成员及路径逃逸；内容边界=文件级完整性，不验证身份、签名、CURRENT真值或PREWRITE；权威=CANDIDATE/SHADOW_ONLY/NOT_STORY_CANON/NOT_V12_STABLE_OBJECT；来源=项目根级前置指令、QA16/QA25/QA33、R003只读样本；使用=python 本脚本 --root DIR --manifest JSON 或 --self-test；关系=补充QA16而不替代它；禁止=据此颁发QA_RELEASE或持久化V12对象。
变更记录：2026-10-08初建，只读，不修改任何现有文件。
"""
from __future__ import annotations
import argparse, hashlib, json, tempfile
from pathlib import Path
VALID_ROLES={'COMMITTED_BODY','COMMITTED_DELTA','WORKING_CONTRACT','QA_CURRENT_RULE','QA_AUDIT','QA_CANDIDATE','SOURCE_VECTOR'}
def sha(b):return hashlib.sha256(b).hexdigest()
def validate(root:Path,manifest:dict)->dict:
    problems=[]; verified=[]; used=set()
    if not isinstance(manifest,dict) or manifest.get('schema')!='QA34_EVIDENCE_V1' or not isinstance(manifest.get('files'),list):
        return {'verdict':'HOLD_SCHEMA','problems':['SCHEMA_OR_FILES_INVALID'],'production_authorized':False}
    files=manifest['files']
    if not files:problems.append('EMPTY_EVIDENCE_SET')
    resolved_root=root.resolve()
    for i,x in enumerate(files):
        tag=f'entry[{i}]'
        if not isinstance(x,dict) or any(k not in x for k in ('role','path','sha256','stable_id')):
            problems.append(tag+':MISSING_FIELDS');continue
        role,path,expected,stable=x['role'],x['path'],x['sha256'],x['stable_id']
        if role not in VALID_ROLES or not isinstance(path,str) or not path or not isinstance(stable,str) or not stable.startswith('libfile_'):
            problems.append(tag+':BAD_ROLE_PATH_OR_STABLE');continue
        if (not isinstance(expected,str) or len(expected)!=64 or any(c not in '0123456789abcdef' for c in expected)):
            problems.append(tag+':BAD_SHA256');continue
        p=Path(path)
        if p.is_absolute() or '..' in p.parts or path in used:
            problems.append(tag+':UNSAFE_OR_DUPLICATE_PATH');continue
        used.add(path)
        target=(resolved_root/p).resolve()
        if not target.is_relative_to(resolved_root):
            problems.append(tag+':PATH_ESCAPE');continue
        if not target.is_file():
            problems.append(tag+':MISSING_FILE');continue
        data=target.read_bytes(); actual=sha(data)
        if actual!=expected:
            problems.append(tag+':CONTENT_CHANGED');continue
        verified.append({'role':role,'path':path,'sha256':actual,'stable_id_unverified':stable})
    return {'verdict':'EVIDENCE_BYTES_MATCH_ONLY' if not problems else 'HOLD_EVIDENCE',
            'problems':problems,'verified_count':len(verified),'supplied_count':len(files),
            'verified':verified,'authority_and_identity_verified':False,'production_authorized':False}
def self_test():
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);(root/'a.md').write_bytes(b'known'); (root/'other.md').write_bytes(b'mismatch')
        good={'schema':'QA34_EVIDENCE_V1','files':[{'role':'COMMITTED_BODY','path':'a.md','sha256':sha(b'known'),'stable_id':'libfile_test_only'}]}
        import copy
        cases=[]
        def test(name,m,expected):
            actual=validate(root,m)['verdict'];cases.append({'case':name,'expected':expected,'actual':actual,'pass':actual==expected})
        test('valid_bytes_not_authentication',good,'EVIDENCE_BYTES_MATCH_ONLY')
        m=copy.deepcopy(good);m['files'][0]['sha256']=sha(b'altered');test('changed_digest',m,'HOLD_EVIDENCE')
        m=copy.deepcopy(good);m['files'][0]['path']='other.md';test('different_bytes',m,'HOLD_EVIDENCE')
        m=copy.deepcopy(good);m['files'][0]['path']='missing.md';test('missing',m,'HOLD_EVIDENCE')
        m=copy.deepcopy(good);m['files'][0]['path']='../a.md';test('traversal',m,'HOLD_EVIDENCE')
        m=copy.deepcopy(good);m['files'].append(m['files'][0].copy());test('duplicate_path',m,'HOLD_EVIDENCE')
        m=copy.deepcopy(good);m['files'][0]['role']='SUDO_CANON';test('role_not_allowed',m,'HOLD_EVIDENCE')
        m=copy.deepcopy(good);m['files'][0]['stable_id']='fake';test('stable_shape',m,'HOLD_EVIDENCE')
        m=copy.deepcopy(good);m['files']=[];test('empty',m,'HOLD_EVIDENCE')
        m=copy.deepcopy(good);m['schema']='UNKNOWN';test('schema',m,'HOLD_SCHEMA')
        m=copy.deepcopy(good);del m['files'][0]['sha256'];test('missing_field',m,'HOLD_EVIDENCE')
        return {'pass_count':sum(x['pass'] for x in cases),'total':len(cases),'cases':cases,
            'caveat':'A fabricated, internally consistent manifest may pass; stable IDs and authority are not authenticated.'}
def main():
    a=argparse.ArgumentParser();a.add_argument('--self-test',action='store_true');a.add_argument('--root',type=Path);a.add_argument('--manifest',type=Path);a.add_argument('--out',type=Path);v=a.parse_args()
    if v.self_test:r=self_test()
    else:
        if not v.root or not v.manifest:a.error('supply --root and --manifest')
        try:r=validate(v.root,json.loads(v.manifest.read_text(encoding='utf-8')))
        except (OSError,ValueError) as e:r={'verdict':'HOLD_INPUT','problems':[type(e).__name__],'production_authorized':False}
    s=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if v.out:v.out.parent.mkdir(parents=True,exist_ok=True);v.out.write_text(s,encoding='utf-8')
    else:print(s,end='')
    return 0 if v.self_test and r['pass_count']==r['total'] else (0 if r.get('verdict')=='EVIDENCE_BYTES_MATCH_ONLY' else 2)
if __name__=='__main__':raise SystemExit(main())
