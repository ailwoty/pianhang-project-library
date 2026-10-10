# 《偏航》独立正文质量审核｜第32项｜跨章缺陷债务去重与复发审核量表

STATUS: CANDIDATE / QA_SUPPORT_ONLY / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT
TASK_NUMBER: QA-32
DATE: 2026-10-08
DESIGNATED_PATH: `/偏航/11_写作规范与质量审核/检查与评分体系/QA32_跨章缺陷债务去重与复发审核量表_CANDIDATE_2026-10-08.md`

## 文件使用说明

- **文件用途**：在每5至10章窗口建立唯一问题根与实例链接，在每20/50章聚合，不按未经确认的720章总数推导完成率。
- **新增原因**：简单累计问题条数容易把同一原始因果缺陷重复处罚，也会漏掉从未实质修复的隐性反复。
- **内容边界**：缺陷追踪指标定义与账表，不改现有QA工单字段和算法，不执行自动生产放行。；不直接改写人物CURRENT、R003 BODY/DELTA、V12事务和时间轴。
- **权威级别与状态**：`CANDIDATE / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT`；本文件不是任何三份既存QA CURRENT的竞争版本。
- **依赖与上游来源**：上游：`/偏航/00_偏航项目_任务前置执行指令_持续更新.md`，11目录三份CURRENT QA规则（QA-1.0、QA-MATRIX-1.0、QA-REPORT-1.0），QA04—QA23；V12当前事务日志 stable `libfile_4b84718c33448191bf6036bd936c77a5`，R003正文/DELTA，第二章单章合同WORKING。上游出现变化时按最新事实与版本重新回读，不缓存这一轮验收。
- **后续使用方法**：审核员冻结目标和来源、记录证据定位、逐项复核；已提交章节仅采用POST_COMMIT只读方式；在每5至10章窗口建立唯一问题根与实例链接，在每20/50章聚合，不按未经确认的720章总数推导完成率。
- **与其他文件关系**：补充QA23的八道接线前置条件，使用QA总规裁决、矩阵Q01—Q22判错、工单模板记载结果。
- **禁止误用**：不得据本文件发放正式QA_RELEASE，不得把构造样例变成已经发生的小说事实；不得跳过用户500字确认、八轮内检、V12 READ_GUARD/PREWRITE/事务。

---

## 1. 主根与出现实例拆分

缺陷主键`ROOT_DEFECT_KEY=(Q_ID, CAUSAL_MECHANISM, CHARACTER_OR_SYSTEM_SCOPE)`；实例键`INSTANCE=(CHAPTER_UID, BODY_HASH, SCENE_ANCHOR)`。同一原生弱点多次出现，保留实例逐条，不因为技术去重擦掉覆盖密度；同一语句触发Q09和Q21只按主因计一笔罚分，次级问题仍保留。

## 2. 缺陷债务表格

| 字段 | 定义 | 何时结清 |
|---|---|---|
| FIRST_SEEN | 第一次有证据的位置 | 永久保留历史 |
| LAST_REPRODUCED | 最新可复现冻结正文 | 不再出现且回归通过 |
| FIX_EVIDENCE | 授权修改范围+新版hash+结果 | 仅改字面但机制相同不得CLOSED |
| RECURRENCE_WINDOW | 近5/10章同一机制复发次数 | 窗口通过且不制造同类替代错误 |
| STORY_RISK | 影响FACT/INFO/REL、读者信任或语言 | 风险下降后更新评级 |
| OPEN_DAYS_OR_CHAPTERS | 从发现至结清的时长/章节数 | 仅在真实生产取值 |

## 3. 分层指标

`P0_BLOCKERS_OPEN`、`P1_BLOCKERS_OPEN`、`P2_BY_CAUSAL_ROOT`、`QA_FALSE_POSITIVE_REVERSAL_RATE`、`FIX_REGRESSION_RATE`、`EXPLICIT_INFO_LEAKS_PER_10K_CHARS`、`ACTUAL_CHAPTER_CHANGE_RATE`。无真实样本用N/A，不能用0代替缺数据。局部跨章重复率需要至少3章正文；仅R003不能计算趋势。

## 4. 纠错优先级

同一主因反复出现在两名以上男主主场则优先`CHARACTER_FUNCTION_REDESIGN`，比机械逐句修词更重要；同一组织权力漏洞扩散到三场则优先`WORLD_PERMISSION_FIX`；现行硬禁词可批量静态预检，但不允许拿词法通过掩盖整个章节没有变化。

---

## 变更记录

2026-10-08：第32项初次建立，保留QA-1.0三份CURRENT原样，审计及候选规则未获独立正史升级或V12机器接入。
