"""工具反例测试：证明已定义错误会拦住，不给文学打分。"""
import csv,importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from 校验公共 import body_text,char_count,paragraphs,quote_errors,check_body,asset_check,assets,load_config

TOOLS=Path(__file__).resolve().parents[1]

class BodyTests(unittest.TestCase):
    def test_scope_excludes_metadata(self):
        b,line=body_text('# 标题\n字数9999\n<!-- BODY_START -->\n你好。\n<!-- BODY_END -->\n修订')
        self.assertEqual(char_count(b),3);self.assertEqual(line,4)
    def test_missing_markers(self):
        with self.assertRaises(ValueError):body_text('正文')
    def test_reversed_markers(self):
        with self.assertRaises(ValueError):body_text('<!-- BODY_END -->\n文\n<!-- BODY_START -->')
    def test_duplicate_markers(self):
        with self.assertRaises(ValueError):body_text('<!-- BODY_START -->\n<!-- BODY_START -->\n文\n<!-- BODY_END -->')
    def test_empty_body(self):
        with self.assertRaises(ValueError):body_text('<!-- BODY_START -->\n \n<!-- BODY_END -->')
    def test_unmarked_opt_in(self):self.assertEqual(body_text('文',False)[0],'文')
    def test_soft_wrap_same_paragraph(self):self.assertEqual(len(paragraphs('第一行\n第二行\n\n下一段')),2)
    def test_valid_nested_quotes(self):self.assertFalse(quote_errors('“他说‘来吧’，我答应了。”'))
    def test_equal_counts_wrong_order(self):self.assertTrue(quote_errors('”错了“'))
    def test_cross_nested_quotes(self):self.assertTrue(quote_errors('“‘交叉”’'))
    def test_unclosed_quote(self):self.assertTrue(quote_errors('“没结束'))
    def test_nested_same_type(self):self.assertTrue(quote_errors('“外“内”外”'))
    def test_ascii_quote(self):self.assertTrue(check_body('"a"',{})['failures'])
    def test_allowed_term_exact(self):
        r=check_body('澄湾与澄海',{'banned_terms':['澄'],'allowed_terms':['澄湾']})
        self.assertEqual(len(r['failures']),1);self.assertEqual(r['failures'][0]['offsets'],[3])
    def test_dash_one_hit(self):
        r=check_body('他——来了',{'ban_dashes':True})
        self.assertEqual(r['failures'][0]['count'],1)
    def test_dash_optional(self):self.assertFalse(check_body('他——来了',{'ban_dashes':False})['failures'])
    def test_short_run_40_threshold(self):
        r=check_body('短一。\n\n短二。\n\n短三。',{'short_threshold':40,'max_short_run':2})
        self.assertTrue(any(x['rule']=='连续短叙述段' for x in r['failures']))
    def test_soft_wrap_not_fake_paragraphs(self):
        r=check_body('短一。\n短二。\n短三。',{'max_short_run':2})
        self.assertFalse(r['failures'])
    def test_long_soft_wrap(self):
        self.assertTrue(check_body('字'*80+'\n'+'字'*80,{'max_paragraph_chars':150})['failures'])
    def test_pronoun_configurable(self):
        self.assertTrue(check_body('她来了。',{'no_start_pronoun':['她']})['failures'])
        self.assertFalse(check_body('她来了。',{})['failures'])
    def test_title_inside_body(self):self.assertTrue(check_body('# 标题',{})['failures'])
    def test_char_boundaries(self):
        self.assertFalse(check_body('一二三',{'min_chars':3,'max_chars':3})['failures'])
        self.assertTrue(check_body('一二三四',{'max_chars':3})['failures'])

class AssetAndConfigTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_missing_placeholder_not_skipped(self):
        m=self.p/'manifest.md';m.write_text('- `【书名】.md`\n- `manifest.md`\n',encoding='utf-8')
        self.assertTrue(asset_check(self.p,m)['failures'])
    def test_real_placeholder_path_accepted(self):
        (self.p/'【书名】.md').write_text('文',encoding='utf-8')
        m=self.p/'manifest.md';m.write_text('- `【书名】.md`\n- `manifest.md`\n',encoding='utf-8')
        self.assertFalse(asset_check(self.p,m)['failures'])
    def test_json_and_html_unregistered_caught(self):
        (self.p/'a.json').write_text('{}');(self.p/'b.html').write_text('x')
        m=self.p/'manifest.md';m.write_text('- `manifest.md`\n')
        r=asset_check(self.p,m);self.assertEqual(r['failures'][0]['unregistered'],['a.json','b.html'])
    def test_duplicates(self):
        m=self.p/'manifest.md';m.write_text('- `manifest.md`\n- `manifest.md`\n')
        self.assertTrue(asset_check(self.p,m)['failures'])
    def test_manifest_traversal(self):
        m=self.p/'manifest.md';m.write_text('- `../outside.md`\n- `manifest.md`\n')
        self.assertTrue(asset_check(self.p,m)['failures'])
    def config(self,rules):
        p=self.p/'c.json';p.write_text(json.dumps({'text_rules':rules}));return p
    def test_bad_config_key(self):
        with self.assertRaises(ValueError):load_config(self.config({'min_chras':3}))
    def test_invalid_range(self):
        with self.assertRaises(ValueError):load_config(self.config({'min_chars':5,'max_chars':4}))
    def test_boolean_number_rejected(self):
        with self.assertRaises(ValueError):load_config(self.config({'min_chars':True}))
    def test_string_list_rejected(self):
        with self.assertRaises(ValueError):load_config(self.config({'banned_terms':'字'}))

class CLITests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def runcli(self,name,*args):
        r=subprocess.run([sys.executable,str(TOOLS/name),*map(str,args)],capture_output=True,text=True)
        return r.returncode,json.loads(r.stdout)
    def writebody(self,text):
        p=self.p/'chapter.md';p.write_text('<!-- BODY_START -->\n'+text+'\n<!-- BODY_END -->',encoding='utf-8');return p
    def registry(self,text='实体ID,类别,现名\nCHR001,人物,阿甲\n'):
        p=self.p/'registry.csv';p.write_text(text,encoding='utf-8');return p
    def test_valid_cli(self):self.assertEqual(self.runcli('硬规则校验器.py',self.writebody('“我来。”'))[0],0)
    def test_no_files_hard_check(self):self.assertEqual(self.runcli('硬规则校验器.py',self.p)[0],2)
    def test_wrong_quotes_cli_fail(self):self.assertEqual(self.runcli('硬规则校验器.py',self.writebody('”错了“'))[0],1)
    def test_missing_target(self):self.assertEqual(self.runcli('硬规则校验器.py',self.p/'none.md')[0],2)
    def test_no_files_consistency(self):
        folder=self.p/'empty';folder.mkdir()
        self.assertEqual(self.runcli('一致性回归检查.py','--body',folder,'--registry',self.registry())[0],2)
    def test_empty_registry_rejected(self):
        self.assertEqual(self.runcli('一致性回归检查.py','--body',self.writebody('阿甲来了。'),'--registry',self.registry('实体ID,类别,现名\n'))[0],2)
    def test_duplicate_entity_rejected(self):
        r=self.registry('实体ID,类别,现名\nA,人,阿甲\nA,人,阿乙\n')
        self.assertEqual(self.runcli('一致性回归检查.py','--body',self.writebody('阿甲'),'--registry',r)[0],2)
    def test_forbidden_word_evidence(self):
        code,data=self.runcli('一致性回归检查.py','--body',self.writebody('阿甲知道秘密。'),'--registry',self.registry(),'--forbidden','秘密')
        self.assertEqual(code,1);self.assertEqual(data['forbidden_hits'][0]['count'],1)
    def test_scope_no_meta_leak(self):
        p=self.writebody('阿甲来了。');p.write_text(p.read_text()+'\n元数据秘密',encoding='utf-8')
        code,data=self.runcli('一致性回归检查.py','--body',p,'--registry',self.registry(),'--forbidden','秘密')
        self.assertEqual(code,0);self.assertEqual(data['semantic_consistency'],'NOT_TESTED')

class FrameworkMutationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)/'package'
        shutil.copytree(TOOLS.parent,self.root,ignore=shutil.ignore_patterns('__pycache__'))
        spec=importlib.util.spec_from_file_location('health',TOOLS/'框架体检.py')
        self.health=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.health)
    def tearDown(self):self.tmp.cleanup()
    def mutate_config(self,key,value):
        p=self.root/'15_数据资产与机器可读/项目配置.json';c=json.loads(p.read_text(encoding='utf-8'))
        c['scale'][key]=value;p.write_text(json.dumps(c),encoding='utf-8')
    def test_real_package_pass(self):self.assertEqual(self.health.inspect(self.root)['status'],'PASS')
    def test_scale_arithmetic_rejected(self):
        self.mutate_config('target_average_chars',2800)
        self.assertEqual(self.health.inspect(self.root)['status'],'FAIL')
    def test_volume_multiplication_rejected(self):
        self.mutate_config('chapters_per_volume',100)
        self.assertEqual(self.health.inspect(self.root)['status'],'FAIL')
    def test_missing_core_rejected(self):
        (self.root/'22_读者验证与证据/00_试读实验与留存口径.md').unlink()
        self.assertEqual(self.health.inspect(self.root)['status'],'FAIL')
    def test_fake_finalized_rejected(self):
        p=self.root/'15_数据资产与机器可读/00_章节进度表.csv'
        p.write_text(p.read_text(encoding='utf-8').replace('计划,0','已定稿,3000'),encoding='utf-8')
        self.assertEqual(self.health.inspect(self.root)['status'],'FAIL')
    def test_unregistered_file_rejected(self):
        (self.root/'leaked.json').write_text('{}')
        self.assertEqual(self.health.inspect(self.root)['status'],'FAIL')

if __name__=='__main__':unittest.main()
