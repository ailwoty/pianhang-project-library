# 《偏航》独立正文质量审核｜第21项｜多卷情绪节奏与读者承诺债务量表

STATUS: CANDIDATE / QA_SPECIAL / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT
TASK_NUMBER: QA-21
DATE: 2026-10-08
DESIGNATED_PATH: `/偏航/11_写作规范与质量审核/检查与评分体系/QA21_多卷情绪节奏与读者承诺债务量表_CANDIDATE_2026-10-08.md`

## 文件使用说明

- **文件用途**：给百万字尺度提供不机械轮班的情绪反复、钩子信用、场景汇率和非爱情剧情容量监测方法。
- **新增原因**：QA10有长期疲劳提纲，但缺少固定采样口径和“刺激越大越好”式刷分的矫正机制。
- **内容边界**：只处理可复核的质量审核、候选协议或只读审计，不构造故事事实，不改R003及任何已COMMITTED运行态。
- **权威级别与状态**：`CANDIDATE / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT`；不创建第二个CURRENT规则。
- **依赖与上游**：根级前置指令；独立QA总规QA-1.0；Q01—Q22矩阵；QA04—QA13；第一章R003 BODY/DELTA；最新第二章WORKING单章合同；V12事务日志READ_GUARD。
- **后续使用方法**：QA启动时先回读源的最新physical版本；复核时绑定来源指纹与本项编号；需要正式升级时按既有CURRENT规范受控评审。
- **与其他文件关系**：作为现有3份CURRENT规范的辅助证据/候选方法，承接QA04—QA13，不替代V12事务、正文索引或人物主档。
- **禁止误用**：不可把样例当CANON；不可从本项发放QA_RELEASE_TOKEN；不可因本项形成发现擅自修改R003或第二章WORKING范围。

---

## 一、抽样粒度

以已COMMITTED完整章节为根抽样；采样窗建议`最近3章 / 10章 / 20章 / 50章 / 100章`，同一章只计一次。未写章节只输出`NOT_OBSERVED`，不能把十卷/720章S3情绪规划当已发生样本。R003目前仅一章，可做基线，不能宣称已经发生长篇疲劳。

## 二、七个连续观测变量

| 变量 | 标注方式 | 异常与解释边界 |
|---|---|---|
| EMOTION_TYPE | 羞辱、拒绝、希望、温情、后悔、赢得机会、失去主控等多选 | 连续三场同一情绪且无后果加深→`Q03`候选 |
| AGENCY_SHIFT | 角色选择权扩大/收缩/转移/无变化 | 虐点只是受害而缺自选代价时检查人物主动性 |
| COST_IRREVERSIBILITY | 可逆、延迟可逆、不可逆，附证据 | 全员永远复原→`Q13`候选 |
| PLOT_CURRENCY | 事业、关系、信息、资源、世界、职业、公众版本 | 十场都以占有宣言结尾→`Q17/Q20` |
| PROMISE_ID | 上章钩子具体承诺+当前兑现/延期/违约 | 只开新秘密不偿旧承诺→`Q19` |
| POV_PRIVILEGE | 哪个角色获知/判断，被限制什么 | 全知主角消灭秘密差→`Q02/Q18` |
| READER_RELIEF | 是否有留白、正常生活、喜悦或主动时间 | 全面高压导致峰值失效，但不能要求每章喘息 |

## 三、承诺信用账

每个钩子记录`PROMISE_ID; PROMISED_QUESTION; FIRST_RAISED_CHAPTER; EXPECTED_PAYOFF_BAND; PAYOFF_TYPE; DELAY_JUSTIFICATION; CURRENT_STATUS; READER_COST`。只有已写章节可判`PROMISE_KEPT / FAIR_DELAY / UNFAIR_DELAY / DROPPED`；作者级规划仅候选不可虚构读者行为。

R003尾部承诺：“需要有权主体回答为何09-A不可见”。第二章S3允许兑现的是**形成链的一处可核差异**，而不是立刻找回09-A内容；这不算逃票。

## 四、跨男主的失败指纹

`MAN_ID / PRIMARY_PERSONAL_VALUE / SELF_AUTHORED_MISTAKE / IRRETRIEVABLE_COST / REPAIR_ATTEMPT / FAILURE_BELONGS_TO_HIM / CAN_SWAP_WITH_OTHER_MALE`。如果把人物身份换掉其悲剧成立度依然100%，记录`Q12/Q17`。没有足量已写主场章节时只做`AUDIT_NOT_YET_POSSIBLE`。

## 五、阅读体验不伪造规则

禁止杜撰点击率、付费率、评论情绪、读者投票。若没有真实数据，报告只写文本可审证据和编辑判断等级。整卷质量不得靠中途“爆点总数”代替人物成本与承诺兑现。建议当5章钩子连锁均没有兑现时进入人工专项，但这属于预警阈值，不是项目上游不可变硬规则。

---

## 变更记录

2026-10-08：完成第21项独立审核专项初版；建立可追溯检查流程和下一步验收边界；保持故事CURRENT不变。
