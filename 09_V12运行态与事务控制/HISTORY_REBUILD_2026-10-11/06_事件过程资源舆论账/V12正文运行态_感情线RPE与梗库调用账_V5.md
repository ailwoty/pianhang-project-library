# V12正文运行态｜感情线RPE与梗库调用账 V5

状态：ACTIVE
SCHEMA_VERSION：5

## 文件使用说明｜2026-10-07 第20项迁移更新

- **修改原因**：感情梗库两个CURRENT资产已迁入`/偏航`，调用账必须指向新生产路径。
- **具体变化**：仅更新两条内部梗库CURRENT路径。
- **未修改内容**：不修改任何HOOK_CALL记录、RPE评分规则、关系事实或历史调用记录。
- **影响范围**：7K/RPE资产路由。
- **兼容与冲突**：旧`/wowoty`梗库副本保留为迁移来源，不默认调用。
- **后续调用提醒**：后续候选召回只使用`/偏航/06_人物关系与感情体系/CURRENT/感情梗库/`。

来源：V12 7K.8—7K.10
内部资产：
- `/偏航/06_人物关系与感情体系/CURRENT/感情梗库/所有人都在为她偏航_V12_感情梗主梗库_内部调用.md`（702主梗）
- `/偏航/06_人物关系与感情体系/CURRENT/感情梗库/所有人都在为她偏航_V12_感情梗完整变体库_内部调用.md`（6223变体）

## 1. RPE十维
每次真正落地的关系机制评估：
1. RELATION_NET_CHANGE：关系状态净变化
2. EMOTIONAL_GAIN：情绪收益
3. CHARACTER_SPECIFICITY：人物专属性
4. NATURAL_TRIGGER：自然触发度
5. CONSEQUENCE_LENGTH：后果长度
6. POLY_COUPLING_GAIN：多角耦合收益
7. NOVELTY：新鲜度
8. INTIMACY_COMPLIANCE：亲密边界/合规
9. CAUSAL_COMPLETENESS：因果完整度
10. FUTURE_CONFLICT_SUSTAINABILITY：后续可持续冲突

RPE不是“越甜越高”。
靠近、后撤、信任下降、误会加深、边界重建、退出、占有升级、秘密权限变化等只要有真实因果净变化，都可高RPE。

## 2. 调用记录
HOOK_CALL_ID / CHAPTER_UID / COMMIT_ID / REL_EDGE_IDS / MAIN_FUNCTION / VARIANT_ID / SOURCE_TYPE / PRE_STATE / PRE_STATE_REFS / TRIGGER / TRIGGER_REFS / CHARACTER_CHOICE / IMMEDIATE_EMOTION / RELATION_DELTA / RELATION_CHANGE_REFS / WORLD_RIPPLE / WORLD_RIPPLE_REFS / UNSETTLED_ITEM / UNSETTLED_REFS / RPE_10D / REPETITION_FINGERPRINT / RECORD_STATUS

HOOK_CALL_ID格式：`HOOK_######`。7K候选召回/DRAFT阶段只使用`TMP_HOOK_*`本地引用，不占正式号；只有章节PREPARED日志已成功取得写租约后，才把实际落地机制映射为HOOK ID并先登记到该COMMIT的`ID_ALLOCATION_MANIFEST`。已登记HOOK若事务ABORT则永久烧号，PARTIAL_FAILURE继续由原COMMIT占有。
CHAPTER_UID必须引用章节永久身份，不使用DISPLAY_NO/旧CHAPTER_ID。
`COMMIT_ID`必须等于产生该调用的章节事务。`RECORD_STATUS`只描述记录形态（通常`DECLARED_WITH_COMMIT`）；该HOOK是否进入正史只由事务日志中对应COMMIT是否`COMMITTED`决定，禁止另设一套HOOK“已提交”真值。
`PRE_STATE/TRIGGER/RELATION_DELTA/WORLD_RIPPLE/UNSETTLED_ITEM`允许保留分析性文字，但不承担客观事实源；只要对应变化已经持久化，必须通过`*_REFS`回指具体`FACT/REL/EVT/CAUS/INFO/PROC/FSW`等稳定节点。
HOOK账是关系机制审计账，不得凭文字描述单独制造关系权限、世界后果或未偿事实。

## 3. 最小充分召回
只有出现自然关系窗口时：
- 先按人物、关系阶段、场景、世界事件、权限边界筛选；
- 主梗候选通常0—3个；
- 再从变体库找差异化实现；
- 不为“必须用梗”制造事件。

## 4. 三重防贬值
追踪：
- 同类主梗重复
- 同底层情绪意义重复
- 同触发方式/动作/公开度/后果重复

高张力但低RPE = 空转刺激。
优先换“关系意义”，不是加尺度。

长期低效的只休眠：
- 某个梗变体资产
- 某种表现方式
绝不休眠V10规则、六专项或人物基底。

## 5. 当前
正式第1章尚未提交，所以HOOK_CALL记录=NONE。
第一章若容既白线形成自然关系窗口，可最小召回；不能预先锁定必须发生暧昧/触碰/吃醋。

REVISION_NOTE：2026-10-05 P245/P246，RPE章节外键统一为`CHAPTER_UID`，并为关系机制调用登记稳定`HOOK_######`命名空间。

REVISION_NOTE：2026-10-05 P287，HOOK调用增加COMMIT_ID；RPE记录自身不维护第二套正史开关，生效状态派生自事务日志。

REVISION_NOTE：2026-10-05 P321，RPE调用增加PRE/TRIGGER/RELATION/WORLD/UNSETTLED稳定引用字段；文字分析不再充当关系或世界事实的第二来源。

REVISION_NOTE：2026-10-05 P402，HOOK稳定ID的分配时机收口到PREPARED租约之后；候选召回只用TMP_HOOK，ABORT已登记HOOK永久烧号。
