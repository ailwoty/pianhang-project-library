# 《偏航》正文质量审核工单与放行凭证模板｜CURRENT

## 第八-C节｜来源实读、落点与改后回归（所有正文任务必填）

新增原因：绑定文件不等于调用，读过设定不等于成稿兑现。执行依据为QA总规PROSE_SOURCE_GUARD_V1；本节适用片段/整章及一切改写。本节空白或未实现不能放行。

- TASK_MODE：FIRST_DRAFT / WORKING_REVISION / CHAPTER_REVISION
- BASE_TEXT_VERSION / BASE_SHA256：
- REVIEW_TEXT_SHA256 / CHANGED_SCOPE / ADJACENT_CONTEXT：
- CATALOGUE_REFRESH_EVIDENCE / MODULE_CATALOGUE_VERSION：
- MODULE_SCREEN：当前所有编号与非编号条目逐项列出必需/条件未触发/不适用及理由（当前206条）；必需条目记录规则原段和关联来源。不得预填全部PASS。
- SOURCE_READ_RECEIPTS：stable ID、当前版本、有效段/后置修订、摘录、摘录指纹、权威裁决、候选调用依据。

|模块|来源ID/版本/原段|权威与实际输入|场景作用或约束|正文原句/检查范围|结果与缺口|
|---|---|---|---|---|---|
|待填写|待实读|待裁决|待编译|待核对|未完成|

- EDITORIAL_REALIZATION：公司专名、地点、环境、A13生活、魅力、危险感、语气/幽默、因果、心理行为、高潮爽点、节奏、信息差、宏大/生活尺度、连续性，共十四项。逐项引用正文并说明作用；不适用需理由，只有高潮/规模铺垫可标受控延期并给出兑现窗口。
- REVISION_DEPENDENCY_RECHECK：本次改动影响的人物/事实/地点/时间/信息/关系/伏笔；修改前已成立落点是否保留；前后文是否连贯；是否扩大到全章/跨章。
- REGRESSION_CASES：八类首章失败逐项检查；重复故障次数与根因修复。
- EVIDENCE_CHECK_RESULT：HOLD / EVIDENCE_CHECK_PASS_EDITORIAL_REVIEW_REQUIRED；附实际运行结果与输入指纹，self-test不得代填。
- EDITORIAL_REVIEW_RESULT：按原矩阵填写；同模型标AI_EDITORIAL。此字段不能由脚本自动推定。
- V12_SUBMISSION_STATUS：沿用原接口状态；本工单不改变PREWRITE与事务资格。

修改记录：2026-10-10，模板补充全书来源实读、十四项成稿证据和改后依赖复核，模板版本升为QA-REPORT-1.3。


STATUS: ACTIVE / QA_TEMPLATE_CURRENT / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT
VERSION: QA-REPORT-1.3
DATE: 2026-10-08
DESIGNATED_PATH: `/偏航/11_写作规范与质量审核/审核模板/00_正文质量审核工单模板_CURRENT.md`

## 文件使用说明

- **文件用途**：为片段/章节/跨章/卷级QA提供统一输入、发现、证据、修订、复核和放行凭证字段，供后续按单章复制实例使用。
- **新增原因**：无固定报告结构时，审核容易停留于“有AI腔”“需要更虐”的主观评语；本文件要求每项发现有证据并能复验。
- **内容边界**：仅为空白模板与填写规范；模板中的`UNKNOWN/TODO`不是故事事实，未填写不表示通过。任何填好后的审计实例为AUDIT/WORKING，不自动升成CURRENT或正史。
- **权威级别与状态**：审核模板 CURRENT；不是V12 stable object，不得替代事务日志、正文索引或DELTA。
- **依赖与上游**：《独立正文质量审核总规_CURRENT》《正文缺陷分类判定与否决矩阵_CURRENT》、根级前置指令、具体章节合法CURRENT上下文。
- **后续使用方法**：每次QA从下面正文模版创建审计记录；重要版本可在审核目录下另存为带UID与日期的AUDIT，须合法路由并进索引；仅在结果完成且回读验证后颁发QA放行凭证。凡本片段/本章有十五男主对白，还须填写第八-A节声纹辅助预验收字段；所有正文片段/整章/跨章/卷级质量审核一律检查第八-B节去通胀编辑核验字段。
- **与其他文件关系**：模板管证据格式，总规管流程，矩阵管判错；写作者修订仍服从约500字确认及V12正文流程。
- **禁止误用**：不要复制空白模板并把`PASS`预填；不要把模拟样例当真实审计；不要用本模板绕过PREWRITE或正式事务。`AI_VOICE_PRECHECK_PASS`、`PASS_AI_EDITORIAL`均不等于人类试读通过；去通胀缺源/漏验必须HOLD。
- **本次修改原因**：2026-10-08在原有声纹二-B字段基础上，响应用户担心遗忘高潮去通胀核验的问题，将根级新生效的二-C触发器转为第八-B节强制证据字段；本模板不改变原有QA硬闸、V12提交机制或任何故事事实。

---

## 一、实例报告必填封面（复制填写）

```yaml
QA_REPORT_ID: QA-CHUID-XXXXXX-RXXX-YYYYMMDD-01
QA_STATUS: WORKING                # WORKING/COMPLETE/HOLD
QA_SCOPE: CHAPTER_QA              # SEGMENT_QA/CHAPTER_QA/ARC_QA/VOLUME_QA/POST_COMMIT_AUDIT
SUBJECT_CHAPTER_UID: UNKNOWN
SUBJECT_SOURCE_PATH: UNKNOWN
SUBJECT_STORY_STATUS: CANDIDATE   # CANDIDATE/USER_APPROVED_SEGMENT/COMMITTED_CURRENT/UNKNOWN
SUBJECT_FINGERPRINT: UNKNOWN      # 哈希算法+摘要；无指纹不能放行
SUBJECT_REVISION: UNKNOWN
WORLD_CLOCK_BOUNDARY: UNKNOWN
POV_BOUNDARY: UNKNOWN
CONTRACT_SOURCE: UNKNOWN
UPSTREAM_SOURCE_VECTOR: []        # 人物CURRENT、运行态、上一章BODY/DELTA、章节合同等路径及版本
ROOT_PRETASK_READ: NOT_VERIFIED
V12_READ_GUARD: NOT_APPLICABLE    # PASS/HOLD/NOT_APPLICABLE；不做正式生产时有理由
PREWRITE_FRESHNESS: NOT_VERIFIED  # PASS/STALE/HOLD/NOT_APPLICABLE
USER_SEGMENT_APPROVAL: UNKNOWN    # 约500字已确认边界，整章汇总时强制检查
QA_RULE_VERSION: QA-1.0
QA_MATRIX_VERSION: QA-MATRIX-1.0
AUDITOR_ID: INDEPENDENT_QA
AUDIT_TIMESTAMP: UNKNOWN
```

## 二、章节事件与状态变化表

| 场景ID/位置 | 场景进入时状态 | 人物当场想要什么 | 关键行动/交易/揭露 | 真实付出的代价 | 场景结束时哪个状态改变 | 下一场因此必须怎样不同 |
|---|---|---|---|---|---|---|
| S01 | TODO | TODO | TODO | TODO | TODO | TODO |

状态变化仅允许填写具体 `FACT/INFO/REL/PROC/RESOURCE/PUBLIC_VERSION/SELF_BELIEF` 类别及文本证据；**若尚未提交，只是候选变化，不能伪写“运行账已更新”。**

## 三、四视角信息权限核验

| 敏感信息ID | 读者何时知道 | 黎栖雾何时知道 | 对位男主何时知道 | 其他人何时知道/误信 | 获得渠道与上游依据 | 风险 |
|---|---|---|---|---|---|---|
| INFO-X | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | NEEDS_SOURCE |

对六年经历、Q、白噪、南岬撤离、旧爱和雾港等高密度秘密优先使用本表；不保证这些字段每章出现，不允许据模板自动假定任何角色知情。

## 四、每条缺陷工单（可重复）

```yaml
DEFECT_ID: QA-XXXX-D001
RULE_ID: Q07                       # 矩阵Q01-Q22之一，可有secondary_rule_ids
SEVERITY: P1                       # P0/P1/P2/P3/P4
CONFIDENCE: CONFIRMED              # CONFIRMED/LIKELY/NEEDS_SOURCE/INTENTIONAL_AND_SUPPORTED
LOCATION: "场景/段落/句序"
TEXT_EVIDENCE: "≤30字短引，必须真实出现在冻结稿中"
SOURCE_EVIDENCE: "上游CURRENT/已提交章节或硬规则的可核验定位"
DEFECT_MECHANISM: "具体是因果、权限、人物动机或读者体验在哪里断裂"
READER_IMPACT: "读者在这一位置如何被误导/失去紧张/感到降智"
MINIMUM_SAFE_FIX: "在不破坏已确认文本和CURRENT的前提下，最小可行修复范围"
OWNER: WRITER
STATUS: OPEN                       # OPEN/FIXED/WAIVED/BLOCKED/CLOSED_FALSE_POSITIVE
FIXED_IN_FINGERPRINT: NONE
RETEST_EVIDENCE: NONE
```

一个缺陷不能仅写“需要更疯/更痛/更爽”；必须指出**改变哪一次选择、增加哪一种不可逆成本、补哪条信息路径、删除哪种套话**。

## 五、逐项矩阵裁决

| 规则编号 | 检查结果（PASS/FAIL/NEEDS_SOURCE/NOT_RELEVANT） | 关键证据位置 | 工单ID/排除理由 |
|---|---|---|---|
| Q01-Q10 | TODO：逐条展开 | TODO | TODO |
| Q11-Q22 | TODO：逐条展开 | TODO | TODO |

不得把一行`Q01-Q10全过`替代实际逐条检查。与本章完全无关者写`NOT_RELEVANT`并说明无关原因。

## 六、整章100分诊断（SEGMENT_QA禁用）

| 维度 | 满分 | 得分 | 位置证据与理由 |
|---|---:|---:|---|
| 人物可信与分化 | 20 | TODO | TODO |
| 信息差与认知有效 | 15 | TODO | TODO |
| 因果与成本 | 15 | TODO | TODO |
| 情绪与节奏 | 15 | TODO | TODO |
| 对白辨识 | 12 | TODO | TODO |
| 场景与社会回声 | 8 | TODO | TODO |
| 语言自然度 | 10 | TODO | TODO |
| 章节有效变化 | 5 | TODO | TODO |
| **合计** | **100** | **TODO** | 分数只是诊断，不能抵消P0/P1 |

## 七、修订与回归测试记录

| 轮次 | 旧稿指纹 | 新稿指纹 | 只修了哪些明确授权片段 | 消除了哪些缺陷 | 引入新风险否 | 是否全章/局部重审 | 结论 |
|---|---|---|---|---|---|---|---|
| R01 | TODO | TODO | TODO | TODO | TODO | TODO | HOLD |

如果修订涉及已COMMITTED正文，停止普通改稿流程，转 `POST_COMMIT_FINDING` 与合法CHAPTER_REVISION/RETCON路径。未经用户确认，不得修改已确认约500字正文基线。

## 八、质量结论与提交接口

```yaml
TOTAL_P0: UNKNOWN
TOTAL_P1: UNKNOWN
TOTAL_P2_OPEN: UNKNOWN
TOTAL_P3_OPEN: UNKNOWN
WAIVER_IDS: []
SCORE: NOT_SCORED
STORY_FACTS_ADDED_BY_QA: 0
SOURCE_FINGERPRINT_STILL_CURRENT: UNKNOWN
UPSTREAM_SOURCE_VECTOR_VALID: UNKNOWN
QA_VERDICT: HOLD                    # PASS/PASS_WITH_WAIVER/REVISE/REJECT/HOLD
QA_RELEASE_TOKEN: NONE
NEXT_ACTION: "核验缺失来源/返修候选/局部复核/进入正式V12事务前检查"
```

只有源稿与上游仍为审核时相同版本，P0/P1均为0，P2无未批准例外，报告证据完整且整章评分达到当前标准时，可设置：

```yaml
QA_VERDICT: PASS
QA_RELEASE_TOKEN: "QA_REPORT_ID@SUBJECT_FINGERPRINT"
```

这个凭证仅表示**独立质量审核放行**，绝不代表`COMMITTED`、`PREWRITE_PASS`、`CURRENT_BODY`或事务租约已取得。若生产控制尚未真正接线核验此字段，必须单独标注 `V12_QA_INTERFACE_STATUS: NOT_INTEGRATED`。

## 八-A、十五男主对白声纹AI辅助预验收｜有男主对白时必填

此节执行根级前置指令`二-B`；无涉十五男主对白时只记`NOT_APPLICABLE`并说明范围，不得杜撰读者成绩。模型内部换人测试不能冒充独立真人试读。**本节属于文学诊断，不能单独释放V12 BODY**。

```yaml
VOICE_PRECHECK_TRIGGER: UNKNOWN      # YES/NO
VOICE_PRECHECK_SCOPE: UNKNOWN        # SEGMENT/CHAPTER/POST_COMMIT_AUDIT
VOICE_PRESENT_CHARACTERS: []        # 实际开口的十五男主，不含黎长聿
VOICE_SOURCE_REFERENCES: []         # 角色CURRENT、17/30矩阵、已发生关系/正文
VOICE_SWAP_COMPARISONS: []          # 原角色 -> 最易撞型的另一角色；证据位置
VOICE_AI_TONE_DEFECTS: []           # 口语不自然、心理病灶自述、全员过度正确等
VOICE_AUTHORITY_VIOLATIONS: []      # 职业/关系/同意越权
VOICE_PRECHECK_VERDICT: HOLD         # AI_PRECHECK_PASS/REVISE/HOLD/NOT_APPLICABLE
HUMAN_READER_VERDICT: NOT_TESTED     # 有真实首见证据才更新
REAL_READER_DATA: NONE
VOICE_QA_RELEASE_EFFECT: NONE        # 不替代QA_RELEASE_TOKEN/PREWRITE/V12事务
```

| 角色与位置证据 | 第一反射/句法顺序 | 换人测试对位者 | 换人后为何必须重写或为何无风险 | 口语与情绪瑕疵 | 结论与修订动作 |
|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | HOLD |

**判定**：能在当前来源下具体核对且无严重串型/越权/AI腔问题才写`AI_PRECHECK_PASS`；有缺陷写`REVISE`并建立第四节缺陷工单；关键主档/已发生关系来源缺失写`HOLD`；不相关写`NOT_APPLICABLE`。低信息句无需角色专属化。独立质量总规原P0/P1/P2及已有100分对白辨识维度照常有效。已COMMITTED仅记录只读发现，不擅自修订。

## 八-B、高潮去通胀自动核验｜每个正文QA均须填写

执行根级前置`二-C`，其专项作者级来源是`libfile_5475c9710f488191b646827ca158e16f`的**最新同一stable对象**。本节与`八-A`男主声纹检查互补，不会因正文不包含男主而免除去通胀检查。无真实正文时仅可`PLANNING_ONLY`或`HOLD_BODY_NOT_WRITTEN`，不得当作成稿PASS。

```yaml
DEFLATION_QA_TRIGGER: YES            # 正文任务默认YES；非正文对象NO需说明
DEFLATION_QA_SCOPE: UNKNOWN          # SEGMENT/CHAPTER/ARC/VOLUME/POST_COMMIT_AUDIT/PLANNING_ONLY
DEFLATION_SUBJECT_FINGERPRINT: UNKNOWN
DEFLATION_SOURCE_SPECIALTY_STABLE_ID: libfile_5475c9710f488191b646827ca158e16f
DEFLATION_SOURCE_VERSION_CHECKED: UNKNOWN
DEFLATION_STAGE_BEAT_OR_CONTRACT: UNKNOWN
DEFLATION_PRIOR_SCENE_OR_CHAPTER_ANCHOR: UNKNOWN
DEFLATION_MAIN_CURRENCY: UNKNOWN
DEFLATION_PRIOR_CURRENCY_AND_DUPLICATE_TEST: UNKNOWN
DEFLATION_BEFORE_AFTER_STATE: UNKNOWN
DEFLATION_ACTOR_PERMISSION_EVIDENCE: UNKNOWN
DEFLATION_COST_AND_LATER_PROOF: UNKNOWN
DEFLATION_INFORMATION_TIMING: UNKNOWN
DEFLATION_20_CHAPTER_PRESSURE_OR_BREATH: UNKNOWN
DEFLATION_CAST_INDEPENDENCE: UNKNOWN
DEFLATION_HOOK_AND_NEXT_QUESTION: UNKNOWN
DEFLATION_DEFECT_IDS: []
DEFLATION_VERDICT: HOLD              # PASS_AI_EDITORIAL/REVISE/HARD_FAIL/HOLD_SOURCE/HOLD_BODY_NOT_WRITTEN/NOT_APPLICABLE
REAL_READER_SAMPLE_N: 0             # 有独立可核证实测后才改
DEFLATION_QA_RELEASE_EFFECT: DEPENDS_ON_MAIN_QA     # 不独立触发QA_RELEASE_TOKEN或V12 COMMIT
```

| 本次实际场景/原句锚 | 上一场付了什么 | 本场唯一主货币与新状态 | 谁有权决定/信息从哪来 | 现实不可逆代价与后效 | 20章冷热/章尾追问 | 裁决/缺陷工单 |
|---|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | TODO | HOLD |

**最少裁决逻辑**：确有文本与当前来源支持全部适用维度、且无实质重复/越权时才能记`PASS_AI_EDITORIAL`；同币高光重复但可修则`REVISE`；违反锁定事实、S级成本或信息时序则`HARD_FAIL`；缺合法取证`HOLD_SOURCE`；未写正文`HOLD_BODY_NOT_WRITTEN`，不能假称抽样试读。若该文是已经COMMITTED章节，本节只生成`POST_COMMIT_FINDING`，并以合法事务另议修订。

**提交漏检闸**：`DEFLATION_QA_TRIGGER=YES`但第八-B节未填、主货币/差分/权源/成本缺实据、审核源指纹无法回读者，整份报告`QA_VERDICT=HOLD / QA_RELEASE_TOKEN=NONE`，即使总评分≥85或其他审核通过也不例外。每约500字段须在八轮自查中执行片段级核验，合章再跨段复验；阅读后效长窗只有真实成稿出现才开始，作者规划坐标不构成正文证据。

## 九、审后复盘字段

- 本章最有效的一次人物自主选择：TODO（具体位置）。
- 本章最大的未兑现读者承诺：TODO（能证伪的位置）。
- 本章是否存在“删掉不影响任何后续”的场景：TODO。
- 本章的败局/赢局由谁自己的性格造成：TODO。
- 本章的重要资源动作是否有社会回声，若未写，是否已记录为后续欠账：TODO。
- 与上一章最相似的一次情绪场面：TODO；不同点：TODO。
- 最值得保留的独特对白：TODO；最需要修剪的AI表达：TODO。
- 复核责任人与日期：TODO。

## 十、模板自身验收

每次实例化后检查：冻结稿可回读、上游源有效、已确认范围明确、Q01—Q22逐项记录、P0/P1为零、证据位置真实、评分有依据、返修保留指纹、PASS不冒充COMMITTED；凡出现十五男主对白，第八-A节必须已填且不得写成人类读者通过；所有正文范围均须检查第八-B节去通胀字段，漏检或者无有效源时不发放行凭证。任一关键字段缺失，状态只能为HOLD。

## 更新记录

2026-10-08：建立带冻结源、四视角信息差、缺陷工单、22项检查、100分锚点、版本回归、质量放行和提交边界的统一审核报告模板。

2026-10-08：非破坏性升级至QA-REPORT-1.1，增加第八-A节十五男主对白AI辅助预验收记录；旧1.0模板的章节/修订工单字段保持兼容，不更改独立QA放行条件、V12事务或正史。新用途是在未来相关正文任务中避免遗忘自动声纹核对；没有真实读者时`HUMAN_READER_VERDICT=NOT_TESTED`。

2026-10-08：非破坏性升级至QA-REPORT-1.2，增加第八-B节高潮去通胀自动核验与缺失即HOLD的审稿记录；与根级二-C同步，声纹八-A及早期版本字段保留，绝不将AI审稿写成人类阅读结果，不修改R003、第二章WORKING或V12事务。
