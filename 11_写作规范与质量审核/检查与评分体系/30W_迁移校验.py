"""30W migration checks. In a clone run without arguments; staging supports --source and --candidate."""
from pathlib import Path
import argparse,json,re,collections,hashlib,subprocess,copy
MACHINE='07_剧情规划与章节合同/总剧情规划/00_新基线_机器数据.json'
FREEZE='11_写作规范与质量审核/检查与评分体系/30W_冻结正文与预算清单.json'
CONTRACT='07_剧情规划与章节合同/章节合同/00_全书96章_排场与关系合同_30万字版_CURRENT.md'
NODES='06_人物关系与感情体系/CURRENT/01_102节点逐项落章_30万字_CURRENT.md'
def validate(m,f,contents,paths,tree=None,changed=None):
 checks=[]
 def ck(n,ok,details=''):checks.append(dict(check=n,passed=bool(ok),details=details))
 cs=m['chapters'];future=[x for x in cs if x['chapter']>39];nodes=m['intimacy']
 ck('96 unique chapters',sorted(x['chapter'] for x in cs)==list(range(1,97)))
 ck('39 frozen and 57 planned',len([x for x in cs if x['status']=='FROZEN_COMMITTED'])==39 and len(future)==57 and all(x['status']=='PLANNED' for x in future))
 ck('budget exact 300000',sum(x['actual'] for x in f['latest'])+sum(x['budget'] for x in future)==300000)
 ck('frozen count actual',m['frozen_chars']==f['actual_frozen']==sum(x['actual'] for x in f['latest'])==132033)
 ck('remaining budget',m['remaining_chars']==f['remaining']==167967)
 ck('future chapter limits',all(2700<=x['budget']<=3300 for x in future))
 ck('six contiguous volumes',[n for v in m['volumes'] for n in range(v['start'],v['end']+1)]==list(range(1,97)))
 ck('at most three core',all(len(set(x['core']))<=3 and '黎栖雾' in x['core'] for x in future))
 ck('one conflict hook and max one concept',all(x['conflicts']==x['new_hooks']==1 and x['new_concepts']<=1 for x in future))
 ck('102 unique intimacy functions',len(nodes)==102 and len({x['id'] for x in nodes})==102)
 ck('17 CP six functions',len(collections.Counter(x['cp'] for x in nodes))==17 and set(collections.Counter(x['cp'] for x in nodes).values())=={6})
 future_by_id={p['chapter']:p for p in future}
 ck('node scene cast',all(x['chapter']<=39 or x['name'] in future_by_id.get(x['chapter'],{}).get('core',[]) for x in nodes if 1<=x['chapter']<=96) and all(1<=x['chapter']<=96 for x in nodes))
 ck('no future node declared happened',all(x['status'].startswith('PLANNED') for x in nodes if x['chapter']>39))
 ck('no fiction completion from anchor',all(x['status']=='FROZEN_ANCHOR' and '锚点' in x['action'] for x in nodes if x['chapter']<=39))
 ck('max four nodes scene',max(collections.Counter(x['chapter'] for x in nodes).values())<=4)
 ck('51 major battle functions',len(m['wars'])==17 and sum(len(x['chapters']) for x in m['wars'])==51)
 ck('132 source functions mapped',set(m['migration'])=={str(i) for i in range(1,133)} and all(1<=v<=96 for v in m['migration'].values()))
 ck('17 endings unchanged types',collections.Counter(x['kind'] for x in m['endings'])=={'HE':9,'BE':5,'开放式':3})
 ck('permanent BE five',set(x['name'] for x in m['endings'] if x['kind']=='BE')=={'谢闻铎','顾晏深','祁慎修','段祈舟','黎长聿'})
 ck('endings assigned cast',all(e['name'] in future_by_id.get(e['chapter'],{}).get('core',[]) for e in m['endings']))
 for v in range(3,7):
  actual={p[k] for p in future if p['volume']==v for k in ['lead','support']}
  ck(f'V{v} 17 effective assignments',actual=={x['name'] for x in m['endings']})
  ck(f'V{v} at least four leads',len({p['lead'] for p in future if p['volume']==v})>=4)
 ck('Cheng never chapter lead',all(x['lead']!='程知遥' for x in future))
 ck('CH040 pays tomorrow',future[0]['chapter']==40 and future[0]['lead']=='许泊言' and '明天' in future[0]['scene'])
 ck('protected paths no edits',not (set(changed or []) & {x['path'] for x in f['protected']}))
 if tree is not None:ck('protected SHA identical',all(tree.get(x['path'])==x['blob_sha'] for x in f['protected']))
 for p in [CONTRACT,NODES,MACHINE]:ck('exists '+p,p in paths)
 con=contents(CONTRACT);led=contents(NODES)
 ck('contract 96 rows',len(re.findall(r'^\| CH\d{3} \|',con,re.M))==96)
 ck('ledger 102 rows',len(re.findall(r'^\| CP\d{2}_I[1-6] \|',led,re.M))==102)
 for p in ['07_剧情规划与章节合同/总剧情规划/03_Boss链_责任受益与卷级清算_CURRENT.md','07_剧情规划与章节合同/总剧情规划/04_440章信息释放与悔恨节点_CURRENT.md']:
  ck('no stale future coordinates '+p,all(1<=int(n)<=96 for n in re.findall(r'CH(\d{3})',contents(p))))
  ck('no active ten volume '+p,not re.search(r'\bV(?:[7-9]|10)\b',contents(p)))
 info=contents('09_V12运行态与事务控制/05_事实信息关系组织账/V12正文运行态_情报图与可见度总账_V5.md')
 ck('private public separation',all(x in info for x in ['CH045','CH073','CH081','CH082','CH086','白噪不公开']))
 ck('suspension action split',all(x in con for x in ['CH065前在岗','再停职','CH093仅私人']))
 ck('medical handoff precedes private',all(x in con for x in ['CH062先完成','CH069以后','CH091是核']))
 ck('no Meng answer', '永久UNKNOWN' in contents('07_剧情规划与章节合同/总剧情规划/04_440章信息释放与悔恨节点_CURRENT.md'))
 for p in ['00_总入口与导航/00_偏航项目_总索引_CURRENT.md','00_总入口与导航/01_偏航项目_CANON_CURRENT权威索引.md','00_偏航项目_任务前置执行指令_持续更新.md']:
  ck('authority '+p,CONTRACT in contents(p) and '96' in contents(p))
 missing=[]
 for p in changed or []:
  if not p.endswith('.md'):continue
  for ref in re.findall(r'`([^`\n]+)`',contents(p)):
   if '/' in ref and ref.endswith(('.md','.json','.py')) and ref.split('/')[0] in {'00_总入口与导航','01_总设定与权威母版','06_人物关系与感情体系','07_剧情规划与章节合同','08_正式正文与章节状态','09_V12运行态与事务控制','10_正文启动包与生产接口','11_写作规范与质量审核','人物资料库'} and ref not in paths:missing.append((p,ref))
 ck('current root-relative links',not missing,missing)
 return checks
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source');ap.add_argument('--candidate');ap.add_argument('--root');ap.add_argument('--output');args=ap.parse_args()
 if args.source:
  src=json.loads(Path(args.source).read_text());ch=json.loads(Path(args.candidate).read_text());docs=src['docs']|ch;tree={x['path']:x['sha'] for x in src['tree']['tree'] if x['type']=='blob'}
  def archivepath(p):
   head,sep,tail=p.partition('/');return head+'/HISTORY_30W_2026-10-22/'+tail if sep else '00_总入口与导航/HISTORY_30W_2026-10-22/根目录原件/'+p
  paths=set(tree)|set(ch)|{archivepath(p) for p in ch if p in tree};contents=lambda p:docs[p]
 else:
  root=Path(args.root) if args.root else Path(__file__).resolve().parents[2];paths={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()};contents=lambda p:(root/p).read_text();ch={}
  r=subprocess.run(['git','ls-tree','-r','HEAD'],cwd=root,text=True,capture_output=True,check=True);tree={x.split('\t',1)[1]:x.split()[2] for x in r.stdout.splitlines()}
 m=json.loads(contents(MACHINE));f=json.loads(contents(FREEZE));checks=validate(m,f,contents,paths,tree,list(ch))
 negative=[]
 for label,edit in [
 ('wrong budget',lambda x:x['chapters'][39].update(budget=3300)),
 ('missing chapter',lambda x:x['chapters'].pop()),
 ('four actors',lambda x:x['chapters'][39]['core'].append('第四核心')),
 ('missing intimacy',lambda x:x['intimacy'].pop()),
 ('future declared happened',lambda x:x['intimacy'][-1].update(status='COMMITTED')),
 ('duplicate ending changed',lambda x:x['endings'][0].update(kind='HE')),
 ('lost source function',lambda x:x['migration'].pop('132')),
 ('node wrong cast',lambda x:x['intimacy'][0].update(chapter=40))]:
  bad=copy.deepcopy(m);edit(bad)
  try:rs=validate(bad,f,contents,paths,tree,list(ch));caught=any(not x['passed'] for x in rs)
  except (KeyError,ValueError,StopIteration):caught=True
  negative.append(dict(case=label,rejected=caught))
 result=dict(checks=checks,positive_count=len(checks),passed=sum(x['passed'] for x in checks),failed=[x for x in checks if not x['passed']],negative_cases=negative,negative_rejected=sum(x['rejected'] for x in negative),scope='planning consistency, arithmetic, references and frozen tree; not prose or reader evaluation')
 if args.output:Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({k:v for k,v in result.items() if k not in ['checks']},ensure_ascii=False,indent=2));return 1 if result['failed'] or result['negative_rejected']!=8 else 0
if __name__=='__main__':raise SystemExit(main())
