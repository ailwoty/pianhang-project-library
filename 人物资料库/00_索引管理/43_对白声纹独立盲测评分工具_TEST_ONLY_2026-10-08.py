#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《偏航》对白声纹独立盲测计分工具。TEST_ONLY, NOT_CANON.

文件使用说明
用途：在作者端从38号管理员档读取冻结V150或C18答案，校验匿名读者答卷，
      分别输出首见人测的混淆矩阵、逐角色召回、两两错认、TOP2覆盖与排除原因。
新增原因：此前第01—43项仅规定人工验收方法，没有可重复执行的真实数据计分。
边界：不产生人测数据、不招募受试者、不更改任何题目/答案/人物/正文/V12。
权威：TEST_ONLY / ADMIN_SCORER / NOT_CHARACTER_CANON / NOT_STORY_CANON。
依赖：38号作者档第25项V密钥、第37项C密钥；41/42号匿名读者卷。
用法：
 python3 本文件.py --admin /path/38_....md --validate-only
 python3 本文件.py --admin /path/38_....md --set V --responses /path/responses.csv --out report.json
 python3 本文件.py --self-test
回收CSV最小列：tester_id,reader_group,item_id,set_version,top1,top2,confidence,
               seen_before,cue_leak_flag,reason,order_id
注意：reader_group可用匿名分组，tester_id只可用匿名随机代号。不要收集姓名。
      每行只属于V或C其中一卷；任何测试原题泄露或见过答案的记录不可算首见。
      两卷要分别执行，不可合并总体准确率。UNSURE/无法判断计入有效分母。
      受试者一套冻结卷内必须使用同一reader_group、order_id和set_version。
      top2可留空，不可重复top1。置信度为1..5。凡有错误字段默认拒绝整次评分。
版本关系：新增独立计算工具，38号仍是唯一答案与方法源；本工具不是第二CURRENT。
禁止误用：--self-test只检验程序，不提供现实识别率；无responses不得宣布PASS。
变更记录：2026-10-08，首建第44—53项执行工具，未碰人物/剧情资产。
第64—73项补丁：锁定V/C冻结版本号、拒绝无首选却填写次选/信心、校验order_id及每名匿名受试者分组/题序一致性。对原密钥、评分分母及结果结构不改。
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROLES = [
    '谢闻铎','秦照野','裴沉川','容既白','周妄生',
    '陆知衡','闻淮止','顾晏深','祁慎修','沈稷',
    '霍岑','江叙澄','梁暮寒','许泊言','段祈舟',
]
UNSURE = '无法判断'
ACCEPTED = set(ROLES) | {UNSURE}
EXPECTED_SIZE = {'V':150, 'C':18}
EXPECTED_VERSION = {'V':'V150_FROZEN_20261008', 'C':'C18_FROZEN_20261008'}
MIN_COLS = {'tester_id','reader_group','item_id','set_version','top1','top2','confidence',
            'seen_before','cue_leak_flag','reason','order_id'}


def split_section(src, left, right):
    a = src.find(left)
    if a < 0: raise ValueError('没有找到答案段落：' + left)
    b = src.find(right,a+len(left))
    if b < 0: raise ValueError('没有找到答案区间结尾：' + right)
    return src[a:b]


def keys_from_admin(path, kind):
    s = Path(path).read_text(encoding='utf-8-sig')
    if kind == 'V':
        section = split_section(s,'## 25｜','## 26｜')
        regex = r'^\|\s*(V\d{3})\s*\|\s*([^|]+?)\s*\|\s*([A-J])\s*\|'
    else:
        section = split_section(s,'## 37｜','## 38｜')
        regex = r'^\|\s*(C\d{2})\s*\|\s*([^|]+?)\s*\|'
    answer = {}
    for match in re.finditer(regex,section,re.M):
        item, name = match.group(1), match.group(2).strip()
        if item in answer: raise ValueError('管理员密钥有重复题号：'+item)
        if name not in ROLES: raise ValueError('管理员密钥存在未知男主：'+name)
        answer[item] = name
    expected = EXPECTED_SIZE[kind]
    expected_ids = {f'{kind}{i:03d}' if kind == 'V' else f'{kind}{i:02d}'
                    for i in range(1,expected+1)}
    if set(answer) != expected_ids:
        missing = sorted(expected_ids - set(answer))
        extras = sorted(set(answer) - expected_ids)
        raise ValueError(f'题库未冻结完好，找到{len(answer)}个，缺失{missing[:6]}，多余{extras[:6]}')
    if kind == 'V':
        counts = Counter(answer.values())
        if any(counts[role] != 10 for role in ROLES):
            raise ValueError('V题库角色配额非每人10句：'+repr(dict(counts)))
    return answer


def parse_bool(s, name, line):
    value = (s or '').strip().lower()
    if value in {'true','1','yes','y','是'}: return True
    if value in {'false','0','no','n','否'}: return False
    raise ValueError(f'{line}行{name}必须为true或false，实际为{s!r}')


def read_responses(path, kind, keys):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        reader = csv.DictReader(f)
        absent = MIN_COLS - set(reader.fieldnames or [])
        if absent: raise ValueError('回收表缺少字段：'+','.join(sorted(absent)))
        rows = []
        unique = set()
        tester_metadata = {}
        for n,row in enumerate(reader,2):
            item = (row['item_id'] or '').strip()
            if not item.startswith(kind):
                raise ValueError(f'{n}行混入另一题库：{item}；V/C不得合并')
            if item not in keys: raise ValueError(f'{n}行未知题号：{item}')
            tester = (row['tester_id'] or '').strip()
            group = (row['reader_group'] or '').strip()
            version = (row['set_version'] or '').strip()
            if not tester or not group or not version: raise ValueError(f'{n}行缺匿名读者/分组/卷版本')
            if version != EXPECTED_VERSION[kind]:
                raise ValueError(f'{n}行set_version与已冻结{kind}卷不一致：{version!r}')
            order_id = (row['order_id'] or '').strip()
            if not order_id: raise ValueError(f'{n}行缺少题序order_id')
            if tester in tester_metadata and tester_metadata[tester] != (group, order_id):
                raise ValueError(f'{n}行同一匿名读者的reader_group/order_id不一致：{tester}')
            tester_metadata[tester] = (group, order_id)
            identity = (tester,item,version)
            if identity in unique: raise ValueError(f'{n}行出现重复提交：{identity}')
            unique.add(identity)
            first = (row['top1'] or '').strip()
            second = (row['top2'] or '').strip()
            first = UNSURE if first in {'UNSURE','不确定'} else first
            second = UNSURE if second in {'UNSURE','不确定'} else second
            if first and first not in ACCEPTED: raise ValueError(f'{n}行首选非法：{first}')
            if second and second not in ACCEPTED: raise ValueError(f'{n}行次选非法：{second}')
            if first and second and first == second: raise ValueError(f'{n}行首选/次选相同')
            conf_raw=(row['confidence'] or '').strip()
            if not first and (second or conf_raw):
                raise ValueError(f'{n}行首选为空时不得单独填写第二选择或置信度')
            if conf_raw and (not conf_raw.isdigit() or not 1 <= int(conf_raw) <= 5):
                raise ValueError(f'{n}行confidence应为1至5')
            seen = parse_bool(row['seen_before'],'seen_before',n)
            leaked = parse_bool(row['cue_leak_flag'],'cue_leak_flag',n)
            if first and not (seen or leaked) and not conf_raw:
                raise ValueError(f'{n}行有效答题缺置信度')
            rows.append(dict(tester_id=tester,reader_group=group,version=version,item_id=item,
                             top1=first,top2=second,confidence=int(conf_raw) if conf_raw else None,
                             seen=seen,leaked=leaked,reason=(row['reason'] or '').strip(),
                             order_id=order_id,expected=keys[item]))
        return rows


def rate(n, den):
    return round(n/den,4) if den else None


def score(rows, kind):
    versions = {r['version'] for r in rows}
    if len(versions)>1:
        raise ValueError('不得混合不同set_version；请按版本分别评分：'+repr(sorted(versions)))
    valid, excluded = [],Counter()
    for row in rows:
        if row['seen']: excluded['seen_before']+=1
        elif row['leaked']: excluded['cue_leak']+=1
        elif not row['top1']: excluded['missing_answer']+=1
        else: valid.append(row)
    matrix = {name:{choice:0 for choice in ROLES+[UNSURE]} for name in ROLES}
    byrole = {role:Counter() for role in ROLES}
    bygroup = defaultdict(Counter)
    bytester = defaultdict(Counter)
    correct = 0
    top2_hit = 0
    for row in valid:
        true, picked = row['expected'],row['top1']
        matrix[true][picked]+=1
        byrole[true]['total']+=1
        bygroup[row['reader_group']]['total']+=1
        bytester[row['tester_id']]['total']+=1
        if picked == true:
            correct += 1
            byrole[true]['correct']+=1
            bygroup[row['reader_group']]['correct']+=1
            bytester[row['tester_id']]['correct']+=1
        if true in (picked,row['top2']): top2_hit += 1
        if picked == UNSURE: byrole[true]['unsure']+=1
        if picked != true and row['confidence']>=4:
            byrole[true]['high_conf_wrong']+=1
    pair_errors = [dict(expected=a,guessed=b,count=matrix[a][b],
                        fraction_of_true_a=rate(matrix[a][b],byrole[a]['total']))
                   for a in ROLES for b in ROLES if a!=b and matrix[a][b]]
    pair_errors.sort(key=lambda x:(-x['count'],-x['fraction_of_true_a'],x['expected'],x['guessed']))
    result = {
        'status':'OBSERVED_FIRST_EXPOSURE_DATA_ONLY' if valid else 'NO_VALID_HUMAN_RESPONSES',
        'dataset': kind, 'version':next(iter(versions)) if versions else None,
        'num_rows':len(rows),'valid_first_exposure_responses':len(valid),'excluded':dict(excluded),
        'number_of_readers_in_valid_rows':len(bytester),
        'top1':{'correct':correct,'denominator':len(valid),'rate':rate(correct,len(valid))},
        'top2_inclusive':{'correct':top2_hit,'denominator':len(valid),'rate':rate(top2_hit,len(valid))},
        'by_character':{name:{'correct':byrole[name]['correct'], 'denominator':byrole[name]['total'],
                              'recall':rate(byrole[name]['correct'],byrole[name]['total']),
                              'unsure':byrole[name]['unsure'],
                              'high_confidence_wrong':byrole[name]['high_conf_wrong']} for name in ROLES},
        'by_reader_group':{name:{'correct':v['correct'],'denominator':v['total'],
                                 'top1_rate':rate(v['correct'],v['total'])} for name,v in bygroup.items()},
        'per_reader_rates':{name:{'correct':v['correct'],'denominator':v['total'],
                                   'top1_rate':rate(v['correct'],v['total'])} for name,v in bytester.items()},
        'confusion_matrix_expected_rows_prediction_columns':matrix,
        'top_confusions':pair_errors[:30],
        'limits':['作者原题归属不等于客观唯一语音真值。','相关回答共用同一读者，不应当作独立观测个体。',
                  '本脚本仅做描述统计，未自动检验样本独立性、时间泄漏或人工评价员一致性。',
                  '若某角色分母为零，recall=null，不能赋零或宣布通过。',
                  '实际质量闸需外部首见读者、人工语境审计、改写后独立复测。']
    }
    return result


def self_test():
    # 合成样本仅检验数学，不能当实际项目读者分数。
    rows=[
        dict(tester_id='SYN_A',reader_group='synthetic',version='SYNTHETIC',item_id='V001',
             top1='秦照野',top2='',confidence=3,seen=False,leaked=False,reason='',order_id='',expected='秦照野'),
        dict(tester_id='SYN_A',reader_group='synthetic',version='SYNTHETIC',item_id='V002',
             top1=UNSURE,top2='祁慎修',confidence=2,seen=False,leaked=False,reason='',order_id='',expected='祁慎修'),
        dict(tester_id='SYN_A',reader_group='synthetic',version='SYNTHETIC',item_id='V003',
             top1='祁慎修',top2='',confidence=5,seen=True,leaked=False,reason='',order_id='',expected='祁慎修'),
    ]
    s=score(rows,'V')
    assert s['valid_first_exposure_responses']==2
    assert s['top1']['rate']==0.5
    assert s['top2_inclusive']['rate']==1.0
    assert s['excluded']['seen_before']==1
    assert s['confusion_matrix_expected_rows_prediction_columns']['祁慎修'][UNSURE]==1
    print('SELF_TEST_OK (synthetic fixture only; NOT real reader scores)')


def main():
    p=argparse.ArgumentParser(description='偏航TEST_ONLY盲测首见计分，不接收姓名。')
    p.add_argument('--admin',help='38号唯一作者管理员档Markdown路径')
    p.add_argument('--set',choices=['V','C'],default='V',help='V=150句单句卷,C=18段三话轮卷')
    p.add_argument('--responses',help='首见读者匿名CSV；省略时只检查管理员密钥')
    p.add_argument('--out',help='可选：写出JSON汇总路径')
    p.add_argument('--validate-only',action='store_true')
    p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.self_test: self_test();return
    if not a.admin:p.error('除--self-test外必须提供--admin')
    key=keys_from_admin(a.admin,a.set)
    print(f'ANSWER_KEY_VALIDATED set={a.set}, unique_items={len(key)}, status=AUTHOR_INTENDED_ONLY')
    if a.validate_only or not a.responses:
        print('READER_RESULTS=NONE | VOICE_QA_PASS=NOT_ASSESSED')
        return
    rows=read_responses(a.responses,a.set,key)
    result=score(rows,a.set)
    result_text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.out:
        Path(a.out).write_text(result_text+'\n',encoding='utf-8')
        print(f'WROTE_SUMMARY {a.out}')
    else: print(result_text)

if __name__=='__main__':
    try: main()
    except (ValueError, OSError) as exc:
        print('VALIDATION_ERROR '+str(exc),file=sys.stderr)
        sys.exit(2)
