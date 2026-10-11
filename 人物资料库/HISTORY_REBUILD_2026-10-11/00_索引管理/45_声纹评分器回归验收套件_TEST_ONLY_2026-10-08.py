"""偏航声纹工具回归测试套件｜TEST_ONLY。

文件使用说明
用途：独立检验既有V150/C18冻结资产与管理员评分器的安全边界、缺失值、分母和防泄露路径。
新增原因：第64—73项实测发现旧管理员计分器放行错误版本号与无首选的异常次选数据；需要可重复防退化测试。
内容边界：全部答卷为SYNTHETIC模拟，绝非真实读者数据；不评估角色文学声纹，也不接触V12正文事务。
权威及状态：TEST_ONLY / QA_EXECUTABLE / NOT_CANON / NOT_READER_DATA。
依赖：38管理员答案档、41与42无答案冻结卷、43管理员计分器、44读者ZIP。
使用：在外部将上述文件备份到本地并运行 python3 本脚本.py --admin 38.md --scorer 43.py --reader-zip 44.zip --v-file 41.md --c-file 42.md。
与其他文件关系：本文件是43评分工具的回归测试伴随脚本，不替代43，不拥有第二份作者答案。
禁止误用：19/19 PASS仅说明程序测试通过，不能代表15男主读者声纹验收通过。
变更记录：2026-10-08首次建立第64—73项，测试脚本不生成正式项目故事事实。
"""
from pathlib import Path
from argparse import ArgumentParser
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from collections import Counter
import csv,hashlib,importlib.util,json
parser=ArgumentParser(description='偏航TEST_ONLY声纹执行回归检查，不计算真实人测评分')
parser.add_argument('--admin',required=True)
parser.add_argument('--scorer',required=True)
parser.add_argument('--reader-zip',required=True)
parser.add_argument('--v-file',required=True)
parser.add_argument('--c-file',required=True)
a=parser.parse_args()
admin=Path(a.admin)
modified=Path(a.scorer)
zippath=Path(a.reader_zip)
original_v=Path(a.v_file)
original_c=Path(a.c_file)
spec=importlib.util.spec_from_file_location('scorer_corrected',modified)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
K={t:m.keys_from_admin(admin,t) for t in 'VC'}
steps=[]
def check(name, cond):
 steps.append((name,bool(cond)))
 if not cond:raise AssertionError(name)
with ZipFile(zippath) as z:
 files=z.namelist()
 check('AT01 ZIP安全与完整CRC',z.testzip() is None and len(files)==7 and all('..' not in n and not n.startswith('/') for n in files))
 manifest=json.loads(z.read('01_包内文件SHA256清单.json'))
 check('AT02 内容指纹全部一致',all(hashlib.sha256(z.read(x['file'])).hexdigest()==x['sha256'] for x in manifest) and len(manifest)==6)
 check('AT03 冻结题面逐字节未改',z.read('41_十五男主声纹_150句匿名题面_无答案.md')==original_v.read_bytes() and z.read('42_十五男主声纹_18组多话轮题面_无答案.md')==original_c.read_bytes())
 check('AT04 密钥隔离和配额',len(K['V'])==150 and len(K['C'])==18 and all(n==10 for n in Counter(K['V'].values()).values()) and not any(n.startswith(('38_','43_')) for n in files))
 templates={}
 for kind,template in [('V','V150_首见个人答卷_空白.csv'),('C','C18_首见个人答卷_空白.csv')]:
  t=list(csv.DictReader(z.read(template).decode('utf-8-sig').splitlines()));templates[kind]=t
 check('AT05 空白卷题数版本匹配',len(templates['V'])==150 and len(templates['C'])==18 and all(row['set_version']==m.EXPECTED_VERSION[k] and row['item_id'] in K[k] for k in 'VC' for row in templates[k]))

def validrow(kind,item,reader='TEST_USER_001'):
 row=next(v.copy() for v in templates[kind] if v['item_id']==item)
 row.update(tester_id=reader,reader_group='synthetic_only',order_id='ORDER_A',top1=K[kind][item],top2='',confidence='5',seen_before='false',cue_leak_flag='false',reason='SYNTHETIC')
 return row

def parse_rows(rows,kind='V'):
 with TemporaryDirectory() as d:
  p=Path(d)/'responses.csv'
  with p.open('w',encoding='utf-8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(templates[kind][0]));w.writeheader();w.writerows(rows)
  return m.read_responses(p,kind,K[kind])

def rejects(rows,kind='V'):
 try:parse_rows(rows,kind);return False
 except ValueError:return True
x=validrow('V','V001')
check('AT06 正常首见记录可读取',len(parse_rows([x]))==1)
for title,change in [
 ('AT07 不接受伪卷版本',dict(set_version='BOGUS')),
 ('AT08 无首选但有次选拒绝',dict(top1='',top2='谢闻铎',confidence='')),
 ('AT09 无首选但有信心拒绝',dict(top1='',top2='',confidence='4')),
 ('AT10 缺少题序拒绝',dict(order_id='')),
 ('AT11 非法人物拒绝',dict(top1='无名氏')),
 ('AT12 跨卷题号拒绝',dict(item_id='C01')),
]:
 check(title,rejects([dict(x,**change)]))
y=validrow('V','V002')
check('AT13 同一读者跨组拒绝',rejects([x,dict(y,reader_group='different')]))
check('AT14 同一读者多题序拒绝',rejects([x,dict(y,order_id='ORDER_B')]))
check('AT15 重复题目拒绝',rejects([x,x]))
# Cases with synthetically marked exposure are counted as exclusions, with the honest denominator.
u=validrow('V','V003');u['top1']='无法判断';u['confidence']='2'
s=validrow('V','V004');s['seen_before']='true'
l=validrow('V','V005');l['cue_leak_flag']='true'
result=m.score(parse_rows([x,u,s,l]),'V')
check('AT16 合成评分分母与排除量',result['valid_first_exposure_responses']==2 and result['excluded']=={'seen_before':1,'cue_leak':1} and result['num_rows']==4 and result['by_character'][K['V']['V004']]['denominator']<=1)
check('AT17 无法判断保留独立预测类别',sum(row['无法判断'] for row in result['confusion_matrix_expected_rows_prediction_columns'].values())==1)
check('AT18 C卷接入成功',len(parse_rows([validrow('C','C01')],'C'))==1)
check('AT19 合成结果不声明正式通过',result['status']=='OBSERVED_FIRST_EXPOSURE_DATA_ONLY' and 'VOICE_QA_PASS' not in result)
print('SUMMARY',len(steps),'/',len(steps),'PASS')
for name,ok in steps:print(('PASS ' if ok else 'FAIL ')+name)
print('NOTE ALL SCORING INPUTS WERE SYNTHETIC FIXTURES; NO HUMAN RESPONSES WERE PROVIDED')
