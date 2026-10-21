"""FRAME_R5：只读校验公共函数；仅Python标准库。"""
import hashlib
import json
import re
from pathlib import Path

START = '<!-- BODY_START -->'
END = '<!-- BODY_END -->'
IGNORED = {'.git', '__pycache__', 'HISTORY', '_archive'}

def read(path):
    return Path(path).read_text(encoding='utf-8-sig')

def body_text(text, required=True):
    lines = text.splitlines()
    starts = [i for i,l in enumerate(lines) if l.strip() == START]
    ends = [i for i,l in enumerate(lines) if l.strip() == END]
    if not starts and not ends and not required:
        body = text.strip()
        if not body: raise ValueError('正文为空')
        return body, 1
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValueError('正文标记须各一处、独占一行且START在END之前')
    body = '\n'.join(lines[starts[0]+1:ends[0]])
    if not body.strip(): raise ValueError('正文为空')
    return body, starts[0]+2

def char_count(body):
    return len(re.sub(r'\s', '', body))

def body_hash(body):
    return hashlib.sha256(body.encode('utf-8')).hexdigest()

def paragraphs(body, first_line=1):
    result=[]; chunk=[]; start=first_line
    for n,line in enumerate(body.splitlines(),first_line):
        if line.strip():
            if not chunk: start=n
            chunk.append(line.strip())
        elif chunk:
            result.append((start, '\n'.join(chunk)));chunk=[]
    if chunk: result.append((start, '\n'.join(chunk)))
    return result

def quote_errors(body):
    opens={'“':'”','‘':'’'}; closes=set(opens.values()); stack=[]; errors=[]
    for i,c in enumerate(body):
        if c in opens:
            if stack and c==stack[-1][0]:
                errors.append({'offset':i,'reason':'同类引号重复开启'})
            if c=='‘' and not stack:
                errors.append({'offset':i,'reason':'内嵌单引号缺少外层双引号'})
            stack.append((c,i))
        elif c in closes:
            if not stack or opens[stack[-1][0]]!=c:
                errors.append({'offset':i,'reason':'关闭顺序或嵌套错误'})
            else:stack.pop()
    errors += [{'offset':i,'reason':'开启后未关闭'} for c,i in stack]
    return errors

def collect(target, recursive=False):
    p=Path(target)
    if not p.exists(): raise ValueError('目标不存在：'+str(p))
    if p.is_file():
        if p.suffix.lower() not in {'.md','.txt'}: raise ValueError('正文仅支持.md/.txt')
        return [p]
    candidates=p.rglob('*') if recursive else p.glob('*')
    files=sorted(f for f in candidates if f.is_file() and f.suffix.lower() in {'.md','.txt'}
                 and not f.name.startswith('README') and not any(x in IGNORED for x in f.parts))
    if not files: raise ValueError('未找到正文文件，不能判PASS')
    return files

def load_config(path):
    c=json.loads(read(path))
    if not isinstance(c,dict) or not isinstance(c.get('text_rules'),dict):
        raise ValueError('配置必须为对象且含text_rules对象')
    rules=c['text_rules']
    allowed={'min_chars','max_chars','max_paragraph_chars','ban_ascii_quotes','ban_dashes',
             'banned_terms','allowed_terms','no_start_pronoun','max_short_run','short_threshold','body_markers_required'}
    unknown=set(rules)-allowed
    if unknown: raise ValueError('未知text_rules字段：'+','.join(sorted(unknown)))
    for key in ['min_chars','max_chars','max_paragraph_chars','max_short_run','short_threshold']:
        if key in rules and (type(rules[key]) is not int or rules[key]<0):
            raise ValueError(key+'必须为非负整数')
    if rules.get('max_chars',0) and rules.get('min_chars',0)>rules['max_chars']:
        raise ValueError('字数下限大于上限')
    for key in ['ban_ascii_quotes','ban_dashes','body_markers_required']:
        if key in rules and type(rules[key]) is not bool: raise ValueError(key+'必须为布尔值')
    for key in ['banned_terms','allowed_terms','no_start_pronoun']:
        if key in rules and (not isinstance(rules[key],list) or any(not isinstance(x,str) or not x for x in rules[key])):
            raise ValueError(key+'必须为非空字符串列表（允许空列表）')
    return c

def check_body(body, rules, first_line=1):
    failures=[]; wc=char_count(body)
    lo=rules.get('min_chars',0);hi=rules.get('max_chars',0)
    if wc<lo or (hi and wc>hi): failures.append({'rule':'字数','value':wc,'range':[lo,hi]})
    qs=quote_errors(body)
    if qs:failures.append({'rule':'引号顺序与嵌套','evidence':qs[:20]})
    if rules.get('ban_ascii_quotes',True) and re.search(r"[\"']",body):
        failures.append({'rule':'ASCII引号','count':len(re.findall(r"[\"']",body))})
    if rules.get('ban_dashes',False):
        hits=list(re.finditer(r'—+|--+|–',body))
        if hits:failures.append({'rule':'破折号','count':len(hits),'offsets':[m.start() for m in hits[:20]]})
    masked=body
    for word in sorted(rules.get('allowed_terms',[]),key=len,reverse=True):
        masked=masked.replace(word,' '*len(word))
    for term in rules.get('banned_terms',[]):
        offsets=[m.start() for m in re.finditer(re.escape(term),masked)]
        if offsets: failures.append({'rule':'禁词','term':term,'offsets':offsets[:20]})
    run=0; maxrun=0
    for line,p in paragraphs(body,first_line):
        n=char_count(p);lim=rules.get('max_paragraph_chars',150)
        if lim and n>lim:failures.append({'rule':'段落上限','line':line,'value':n,'limit':lim})
        if re.search(r'^\s*(?:#{1,6}\s|```|<!--)',p,re.M):
            failures.append({'rule':'正文含标题/代码/元数据标记','line':line})
        is_dialogue='“' in p or '”' in p
        run=run+1 if not is_dialogue and n<rules.get('short_threshold',40) else 0
        maxrun=max(maxrun,run)
        for pron in rules.get('no_start_pronoun',[]):
            if p.lstrip().startswith(pron):failures.append({'rule':'段首代词','line':line,'term':pron})
    if maxrun>rules.get('max_short_run',2):
        failures.append({'rule':'连续短叙述段','value':maxrun,'limit':rules.get('max_short_run',2)})
    return {'chars':wc,'body_sha256':body_hash(body),'max_short_run':maxrun,'failures':failures}

def manifest_paths(path):
    # FRAME_R5清单仅识别独占一行的精确路径，不忽略真实存在的【书名】文件。
    return re.findall(r'^- `([^`]+)`\s*$',read(path),re.M)

def assets(root):
    root=Path(root)
    return sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
                  and not any(x in IGNORED for x in p.relative_to(root).parts)
                  and not p.name.endswith(('.pyc','.zip')))

def asset_check(root,manifest):
    paths=manifest_paths(manifest)
    if not paths:return {'failures':['资产清单无精确路径，不能判PASS']}
    invalid=[p for p in paths if Path(p).is_absolute() or '..' in Path(p).parts or '\\' in p]
    disk=set(assets(root)); registered=set(paths)
    missing=sorted(registered-disk);extra=sorted(disk-registered)
    duplicate=sorted(p for p in registered if paths.count(p)>1)
    fails=[]
    if invalid:fails.append({'invalid':invalid})
    if missing:fails.append({'missing':missing})
    if extra:fails.append({'unregistered':extra})
    if duplicate:fails.append({'duplicate':duplicate})
    return {'registered':len(paths),'actual':len(disk),'failures':fails}
