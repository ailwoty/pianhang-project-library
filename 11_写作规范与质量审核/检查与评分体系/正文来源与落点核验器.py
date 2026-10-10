#!/usr/bin/env python3
"""离线证据核验，不替代文学审核、来源权威裁决或 V12 放行。
用法：python3 本文件 --self-test
      python3 本文件 --check task.json
输入结构参见 example()；运行前需实际读取当前来源并生成独立的来源摘录与读取记录。
current_sources 必须由当次来源读取结果填写；手写表不能证明真实调用。
任务文件内路径均相对于任务文件目录。目录快照模块数不是永久常量。
"""
import argparse,copy,hashlib,json,pathlib,sys,tempfile

def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def valid_text(x):return isinstance(x,str) and bool(x.strip()) and x.strip() not in {'TODO','UNKNOWN','PASS','无','待填'}
def validate(task,base):
    errors=[]
    def fail(code,detail):errors.append({'code':code,'detail':detail})
    def read(path):
        try:return (base/path).read_text(encoding='utf-8')
        except (OSError,TypeError,UnicodeError):fail('FILE_UNREADABLE',str(path));return ''
    body=read(task.get('body_path',''))
    if not body.strip():fail('EMPTY_BODY','正文为空')
    if task.get('body_sha256')!=digest(body):fail('STALE_BODY','正文变化后旧审核失效')
    if task.get('mode') not in {'FIRST_DRAFT','WORKING_REVISION','CHAPTER_REVISION'}:fail('MODE','缺少合法任务模式')
    catalogue=json.loads(read(task.get('route_path','')) or '{}')
    if not valid_text(task.get('catalogue_refresh_evidence')):fail('STALE_CATALOGUE','未记录当次目录差分检查')
    expected={m['module_id'] for m in catalogue.get('modules',[])}
    if not expected:fail('EMPTY_MODULE_CATALOGUE','规则目录为空')
    entries=task.get('module_screen',[]);actual=[x.get('module_id') for x in entries]
    if len(actual)!=len(set(actual)) or set(actual)!=expected:fail('MODULE_COVERAGE','模块漏项、重复或未知项')
    current=task.get('current_sources',{});receipts=task.get('read_receipts',{});checked={}
    def source(sid):
        if sid in checked:return checked[sid]
        cur=current.get(sid,{});rec=receipts.get(sid,{})
        if not cur or not rec:fail('MISSING_SOURCE',sid);checked[sid]=False;return False
        before=len(errors)
        if str(rec.get('version'))!=str(cur.get('version')):fail('SOURCE_VERSION_CHANGED',sid)
        if not valid_text(cur.get('retrieval_evidence')):fail('UNVERIFIED_SOURCE',sid)
        txt=read(cur.get('excerpt_path',''))
        if not txt or digest(txt)!=cur.get('sha256') or cur.get('sha256')!=rec.get('sha256'):fail('SOURCE_HASH_CHANGED',sid)
        quote=rec.get('quote','')
        if not valid_text(rec.get('locator')) or not valid_text(quote) or quote not in txt:fail('READ_RECEIPT_INVALID',sid)
        if cur.get('authority') in {'HISTORY','QUARANTINE','HANDOFF','UNRESOLVED','CONFLICT'}:fail('INELIGIBLE_SOURCE',sid)
        if cur.get('authority') not in {'CURRENT','CANDIDATE','WORKING','HISTORY','QUARANTINE','HANDOFF','UNRESOLVED','CONFLICT'}:fail('UNKNOWN_AUTHORITY',sid)
        if cur.get('authority') in {'CANDIDATE','WORKING'} and (rec.get('use_as')!='AUTHOR_CANDIDATE' or not valid_text(rec.get('authorization_evidence'))):fail('CANDIDATE_PROMOTION',sid)
        checked[sid]=before==len(errors);return checked[sid]
    for e in entries:
        mid=e.get('module_id');status=e.get('status')
        if status not in {'REQUIRED','CONDITIONAL_INACTIVE','NOT_APPLICABLE'} or not valid_text(e.get('reason')):fail('MODULE_REASON',str(mid))
        if status=='REQUIRED':
            if not e.get('source_ids'):fail('MODULE_UNREAD',str(mid))
            for sid in e.get('source_ids',[]):source(sid)
            if not valid_text(e.get('rule_locator')) or not valid_text(e.get('rule_quote')):fail('RULE_UNREAD',str(mid))
            elif not any(e['rule_quote'] in read(current.get(sid,{}).get('excerpt_path','')) for sid in e.get('source_ids',[]) if sid in current):fail('RULE_QUOTE_ABSENT',str(mid))
    required=task.get('required_sources',[])
    if not required:fail('EMPTY_SOURCE_PLAN','来源计划为空')
    for sid in required:source(sid)
    bindings=task.get('bindings',[]);bound=set()
    for b in bindings:
        sid=b.get('source_id','');source(sid);bound.add(sid)
        if b.get('module_id') not in expected:fail('BINDING_MODULE',str(b.get('module_id')))
        src=current.get(sid,{});excerpt=read(src.get('excerpt_path','')) if src else ''
        if not valid_text(b.get('source_quote')) or b.get('source_quote') not in excerpt:fail('BINDING_SOURCE_QUOTE',sid)
        if b.get('kind')=='TEXT':
            if not valid_text(b.get('body_quote')) or b.get('body_quote') not in body:fail('NOT_REALIZED',sid)
            if not valid_text(b.get('effect')):fail('NO_SCENE_EFFECT',sid)
        elif b.get('kind')=='CONSTRAINT':
            if not valid_text(b.get('checked_scope')) or not valid_text(b.get('finding')):fail('UNVERIFIED_CONSTRAINT',sid)
        else:fail('BINDING_KIND',sid)
    for sid in required:
        if sid not in bound:fail('SOURCE_LIST_ONLY',sid)
    dimensions={'proper_names','place','environment','elite_life','charm','danger','tone','causality','psychology','payoff','pacing','information','scale','continuity'}
    reviews=task.get('editorial_review',{})
    if set(reviews)!=dimensions:fail('REVIEW_COVERAGE','十四项阅读检查漏项或多出未知项')
    for name,r in reviews.items():
        if r.get('status')=='EVIDENCE_PRESENT':
            if not valid_text(r.get('body_quote')) or r.get('body_quote') not in body or not valid_text(r.get('effect')):fail('REVIEW_NO_EVIDENCE',name)
        elif r.get('status')=='NOT_APPLICABLE':
            if not valid_text(r.get('reason')):fail('REVIEW_NO_REASON',name)
        elif r.get('status')=='DEFERRED':
            if name not in {'payoff','scale'} or not valid_text(r.get('due')) or not valid_text(r.get('reason')):fail('UNBOUNDED_DEFER',name)
        else:fail('EDITORIAL_UNRESOLVED',name)
    for n in task.get('name_requirements',[]):
        if n.get('required'):
            scope=body.split('\n\n')[0] if n.get('scope')=='FIRST_PARAGRAPH' else body
            if not n.get('accepted') or not any(x in scope for x in n['accepted']):fail('MISSING_PROPER_NAME',n.get('entity',''))
            if n.get('source_id') not in required:fail('NAME_SOURCE_MISSING',n.get('entity',''))
    if task.get('mode')!='FIRST_DRAFT':
        revision=task.get('revision',{})
        for field in ['base_sha256','changed_scope','dependency_recheck','retained_evidence','adjacent_context_review']:
            if not valid_text(revision.get(field)):fail('REVISION_RECHECK_MISSING',field)
        if revision.get('base_sha256')==digest(body):fail('NO_REVISION_DELTA','改后稿与基准相同，不能虚报修改')
    return {'status':'HOLD' if errors else 'EVIDENCE_CHECK_PASS_EDITORIAL_REVIEW_REQUIRED','errors':errors,'scope':'仅核验证据结构、版本与字符串落点；不证明真实阅读、文学质量、事实正确或正式提交资格。'}

def example(directory):
    """只生成独立的合成测试输入，不能当作真实章节审核。"""
    (directory/'body.txt').write_text('曜京的灯落在鼎峻控股门前。她笑着收起签字页，决定先问清是谁替她做主。\n\n黎氏家族的来客仍在交谈，这座首都的夜色并不替任何人回答。')
    (directory/'source.txt').write_text('公司候选名称为鼎峻控股。城市名为曜京。人物应以自己的选择回应阻力。')
    (directory/'route.json').write_text(json.dumps({'modules':[{'module_id':'7C.1'}]}))
    body=(directory/'body.txt').read_text();src=(directory/'source.txt').read_text()
    review={k:{'status':'EVIDENCE_PRESENT','body_quote':'她笑着收起签字页','effect':'仅为结构测试，不是文学结论'} for k in ['proper_names','place','environment','elite_life','charm','danger','tone','causality','psychology','payoff','pacing','information','scale','continuity']}
    return dict(body_path='body.txt',body_sha256=digest(body),mode='WORKING_REVISION',route_path='route.json',catalogue_refresh_evidence='SYNTHETIC_FIXTURE',module_screen=[dict(module_id='7C.1',status='REQUIRED',reason='合成用例',source_ids=['S1'],rule_locator='第一行',rule_quote='人物应以自己的选择回应阻力。')],current_sources={'S1':dict(version='1',authority='CANDIDATE',excerpt_path='source.txt',sha256=digest(src),retrieval_evidence='SYNTHETIC_FIXTURE')},read_receipts={'S1':dict(version='1',sha256=digest(src),locator='第一行',quote='城市名为曜京。',use_as='AUTHOR_CANDIDATE',authorization_evidence='合成授权，不代表项目批准')},required_sources=['S1'],bindings=[dict(source_id='S1',module_id='7C.1',source_quote='城市名为曜京。',kind='TEXT',body_quote='曜京的灯',effect='合成地点落点')],editorial_review=review,name_requirements=[dict(entity='城市',required=True,scope='FIRST_PARAGRAPH',accepted=['曜京'],source_id='S1'),dict(entity='公司',required=True,scope='FIRST_PARAGRAPH',accepted=['鼎峻控股'],source_id='S1')],revision=dict(base_sha256='old-fixture-hash',changed_scope='第一段',dependency_recheck='人物和信息边界',retained_evidence='保留主动选择',adjacent_context_review='检查前后连接'))

def selftest():
    cases=[]
    with tempfile.TemporaryDirectory() as tmp:
        d=pathlib.Path(tmp);base=example(d)
        def run(name,change,expected=None):
            t=copy.deepcopy(base);change(t);r=validate(t,d)
            ok=(r['status']!='HOLD') if expected is None else expected in {e['code'] for e in r['errors']}
            cases.append({'case':name,'passed':ok,'expected':expected or 'EVIDENCE_CHECK_PASS_EDITORIAL_REVIEW_REQUIRED'})
        run('完整合成证据可进入文学审核',lambda t:None)
        run('正文变动使旧审核失效',lambda t:t.update(body_sha256='old'),'STALE_BODY')
        run('来源版本变更',lambda t:t['current_sources']['S1'].update(version='2'),'SOURCE_VERSION_CHANGED')
        run('来源内容变更',lambda t:t['current_sources']['S1'].update(sha256='bad'),'SOURCE_HASH_CHANGED')
        run('未取得来源',lambda t:t['read_receipts'].clear(),'MISSING_SOURCE')
        run('没有读取定位',lambda t:t['read_receipts']['S1'].update(locator=''),'READ_RECEIPT_INVALID')
        run('搜索命中不能代替读取',lambda t:t['current_sources']['S1'].update(retrieval_evidence=''),'UNVERIFIED_SOURCE')
        run('只有来源列表没有落点',lambda t:t.update(bindings=[]),'SOURCE_LIST_ONLY')
        run('正文缺少实际落点',lambda t:t['bindings'][0].update(body_quote='不存在的段落'),'NOT_REALIZED')
        run('只有关键词没有场景作用',lambda t:t['bindings'][0].update(effect=''),'NO_SCENE_EFFECT')
        run('来源引文伪造',lambda t:t['bindings'][0].update(source_quote='来源无此句'),'BINDING_SOURCE_QUOTE')
        run('漏筛模块',lambda t:t.update(module_screen=[]),'MODULE_COVERAGE')
        run('重复模块',lambda t:t['module_screen'].append(t['module_screen'][0]),'MODULE_COVERAGE')
        run('模块规则未读',lambda t:t['module_screen'][0].update(rule_quote=''),'RULE_UNREAD')
        run('历史文件误作有效来源',lambda t:t['current_sources']['S1'].update(authority='HISTORY'),'INELIGIBLE_SOURCE')
        run('隔离文件误入正文',lambda t:t['current_sources']['S1'].update(authority='QUARANTINE'),'INELIGIBLE_SOURCE')
        run('候选擅自升正史',lambda t:t['read_receipts']['S1'].update(use_as='CANON'),'CANDIDATE_PROMOTION')
        run('阅读检查缺项',lambda t:t['editorial_review'].pop('elite_life'),'REVIEW_COVERAGE')
        run('效果未实现',lambda t:t['editorial_review']['danger'].update(status='NOT_REALIZED'),'EDITORIAL_UNRESOLVED')
        run('首次出现缺公司专名',lambda t:t['name_requirements'][1].update(accepted=['并未出现的公司名']),'MISSING_PROPER_NAME')
        run('缺地点专名',lambda t:t['name_requirements'][0].update(accepted=['错误城市']),'MISSING_PROPER_NAME')
        run('改后未核上下文',lambda t:t['revision'].pop('adjacent_context_review'),'REVISION_RECHECK_MISSING')
        run('目录未刷新',lambda t:t.update(catalogue_refresh_evidence=''),'STALE_CATALOGUE')
        run('宏大场面无限延期',lambda t:t['editorial_review']['scale'].update(status='DEFERRED',reason='当前仅铺垫',due=''),'UNBOUNDED_DEFER')
        run('允许家族简称与后文首都称呼',lambda t:None)
        run('非顶层场景不强加奢华',lambda t:t['editorial_review'].update(elite_life={'status':'NOT_APPLICABLE','reason':'合成普通劳动场景，仍需环境与人物尊严'}))
        run('悲痛场景不强塞笑点',lambda t:t['editorial_review'].update(tone={'status':'NOT_APPLICABLE','reason':'合成哀伤场景；整体轻快不要求此处抖包袱'}))
        run('局部高潮有明确后续兑现位置',lambda t:t['editorial_review'].update(payoff={'status':'DEFERRED','reason':'合成片段只负责启动','due':'本章第二场'}))
        run('未触发模块允许有理由停用',lambda t:t['module_screen'][0].update(status='CONDITIONAL_INACTIVE',reason='未发生对应事件'))
    return {'test_scope':'SYNTHETIC_REGRESSION_NOT_CHAPTER_QA','passed':sum(c['passed'] for c in cases),'total':len(cases),'cases':cases}

def main():
    ap=argparse.ArgumentParser(description=__doc__);g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--self-test',action='store_true');g.add_argument('--check',type=pathlib.Path);g.add_argument('--example',type=pathlib.Path);args=ap.parse_args()
    if args.self_test:r=selftest();code=0 if r['passed']==r['total'] else 1
    elif args.example:
        args.example.mkdir(parents=True,exist_ok=True);t=example(args.example);(args.example/'task.json').write_text(json.dumps(t,ensure_ascii=False,indent=2));r={'status':'SYNTHETIC_EXAMPLE_ONLY','path':str(args.example/'task.json')};code=0
    else:
        try:r=validate(json.loads(args.check.read_text()),args.check.resolve().parent);code=1 if r['status']=='HOLD' else 0
        except (ValueError,TypeError,KeyError,OSError) as ex:r={'status':'HOLD','error':'INVALID_INPUT','detail':str(ex)};code=1
    print(json.dumps(r,ensure_ascii=False,indent=2));return code
if __name__=='__main__':sys.exit(main())
