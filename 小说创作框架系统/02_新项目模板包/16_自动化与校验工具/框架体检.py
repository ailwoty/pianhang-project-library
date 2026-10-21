#!/usr/bin/env python3
"""FRAME_R5结构与配置体检，不生成文学评分或爆款概率。"""
import argparse,csv,json,sys
from pathlib import Path
from 校验公共 import read,load_config,asset_check

def inspect(root):
    root=Path(root);fail=[]
    c=load_config(root/'15_数据资产与机器可读/项目配置.json');s=c.get('scale',{})
    keys=['total_chapters','volumes','chapters_per_volume','target_average_chars','target_total_chars']
    if any(type(s.get(k)) is not int or s[k]<=0 for k in keys):fail.append('规模字段须为正整数')
    else:
        if s['volumes']*s['chapters_per_volume']!=s['total_chapters']:fail.append('卷数×每卷章数≠全书章数')
        if s['total_chapters']*s['target_average_chars']!=s['target_total_chars']:fail.append('总章数×均字≠总字数')
        rr=c['text_rules']
        if not rr.get('min_chars',0)<=s['target_average_chars']<=rr.get('max_chars',10**9):fail.append('目标均字不在字数允许范围')
    rel=c.get('relationship',{});cp=rel.get('cp_count')
    if type(cp) is not int or cp<1:fail.append('CP数量须为正整数')
    nodes=rel.get('intimacy_nodes_per_cp')
    if nodes is not None and (type(nodes) is not int or nodes<0):fail.append('节点数须为null或非负整数')
    if c.get('mode') not in {'template','project'}:fail.append('mode须为template或project')
    if c.get('mode')=='project' and (not c.get('project_name') or '【' in c['project_name']):fail.append('实际项目尚未填写书名')
    ar=asset_check(root,root/'00_项目资产清单_MANIFEST.md');fail.extend(ar['failures'])
    required=['00_入口与治理/04_任务前置执行指令_持续更新.md','00_入口与治理/05_小说本质定义_强制锁定.md',
              '19_题材包与爆款引擎/13_读者承诺与差异化设计.md',
              '06_人物关系与感情体系/CURRENT/01_吸引力声纹与关系升级工具.md',
              '07_剧情规划与章节合同/卷规划/00_中段发动机与终局预算.md',
              '07_剧情规划与章节合同/总剧情规划/03_承诺伏笔与信息释放账.md',
              '11_写作规范与质量审核/检查与评分体系/00_质量维度与9.9验收协议.md',
              '22_读者验证与证据/00_试读实验与留存口径.md','22_读者验证与证据/01_平台来源核验与断言登记.md']
    for p in required:
        if not (root/p).is_file() or not read(root/p).strip():fail.append('核心机制缺失/空文件：'+p)
    score=read(root/'11_写作规范与质量审核/检查与评分体系/00_质量维度与9.9验收协议.md')
    for i in range(1,13):
        if '| Q%02d |'%i not in score:fail.append('缺少质量维度Q%02d'%i)
    with open(root/'15_数据资产与机器可读/00_章节进度表.csv',encoding='utf-8-sig',newline='') as f:
        dr=csv.DictReader(f)
        if not dr.fieldnames or not {'章号','状态','字数'}.issubset(dr.fieldnames):raise ValueError('进度CSV列不完整')
        rows=list(dr)
    ids=[r['章号'] for r in rows]
    if len(ids)!=len(set(ids)):fail.append('章节进度章号重复')
    if any(r['状态'] not in {'计划','草稿','待审','已定稿','已发布'} for r in rows):fail.append('章节进度状态未知')
    finalized=sum(r['状态'] in {'已定稿','已发布'} for r in rows)
    if c.get('mode')=='template' and finalized:fail.append('空模板虚构定稿')
    for r in rows:
        try:
            if int(r['字数'])<0:raise ValueError()
        except ValueError:fail.append('非法章节字数：'+r['章号'])
    return {'status':'FAIL' if fail else 'PASS','framework_version':c.get('framework_version'),
            'asset_count':ar.get('actual'),'dimensions_defined':12,'finalized_chapters':finalized,
            'failures':fail,'framework_score':'NOT_CALIBRATED','book_score':'NOT_TESTED','market_result':'NOT_TESTED'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',default='.')
    a=ap.parse_args()
    try:r=inspect(a.root);print(json.dumps(r,ensure_ascii=False,indent=2));return int(bool(r['failures']))
    except (ValueError,OSError,csv.Error,KeyError,TypeError) as e:
        print(json.dumps({'status':'ERROR','error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':sys.exit(main())
