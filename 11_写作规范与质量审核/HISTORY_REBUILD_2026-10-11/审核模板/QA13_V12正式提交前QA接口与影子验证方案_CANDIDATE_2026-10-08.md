# 《偏航》独立正文质量审核｜第13项｜QA13_V12正式提交前QA接口与影子验证方案_CANDIDATE_2026-10-08

STATUS: CANDIDATE / NOT_INTEGRATED / QA_INTERFACE_DESIGN / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT
DATE: 2026-10-08
DESIGNATED_PATH: `/偏航/11_写作规范与质量审核/审核模板/QA13_V12正式提交前QA接口与影子验证方案_CANDIDATE_2026-10-08.md`
TASK_NUMBER: QA-13

## 文件使用说明

- **文件用途**：设计QA放行凭证未来如何与V12预写入/事务链衔接，明确阴影验证、字段、拒绝逻辑和迁移边界。
- **新增原因**：QA总规存在业务质量否决，但当前V12注册表和Manifest尚不认识QA字段；不能误称已实现机器强闸。
- **内容边界**：仅为QA方法或审计材料；不新增正史、事实账与事务记录，不修改既有COMMITTED正文。
- **权威级别与状态**：CANDIDATE / NOT_INTEGRATED / QA_INTERFACE_DESIGN；低于用户最新要求、根级前置指令、故事CURRENT、V12事务。
- **依赖与上游**：根级前置指令、11目录独立QA总规、Q01—Q22矩阵、QA工单模板、第一章R003有效正文与DELTA；需要写作时再按章节加载人物CURRENT与INFO/FACT/REL。
- **后续使用方法**：先核对审核对象fingerprint与真正CURRENT；只允许对候选或只读历史对象给出缺陷及修复建议；若规则发生调整，审计文件保留历史证据、方法文件需要审议后更新。
- **与其他文件关系**：承接11目录三份CURRENT总规、Q01—Q22矩阵与工单模板；服从根级前置指令和V12唯一生产入口。
- **禁止误用**：不得把本文件当QA放行凭证、故事真相或V12正式机器闸；不得以审稿结果未经授权改写R003。

---

## 1. 现行状态与目标

当前`QA_AUTHORING_LAYER_READY / V12_QA_INTERFACE_NOT_INTEGRATED`。QA已建立三份CURRENT规范和本轮实战审计；**本任务不修改V12事务协议、Manifest、稳定注册表、运行账或PREWRITE依赖集合**。

目标是在未来合法维护事务中把`QA_RELEASE_TOKEN`作为**独立内容质量输入**，不替代事务原有`READ_GUARD / FRESH_PREWRITE / PREPARED / VERIFY / COMMITTED`序列。

## 2. 提议字段（未注册，仅候选）

```yaml
QA_SCHEMA: QA_RELEASE_V1_PROPOSED
CHAPTER_UID: CHUID_XXXXXX
QA_REPORT_STABLE_ID: UNKNOWN
QA_REPORT_CONTENT_SHA256: UNKNOWN
QA_SUBJECT_BODY_SHA256: UNKNOWN
QA_SOURCE_VECTOR_SHA256: UNKNOWN
QA_RULE_VERSION: QA-1.0
QA_MATRIX_VERSION: QA-MATRIX-1.0
USER_APPROVAL_SCOPE_REF: UNKNOWN
QA_VERDICT: UNKNOWN  # PASS / PASS_WITH_WAIVER / HOLD / REVISE / REJECT，初始必须UNKNOWN
QA_BLOCKER_COUNT: 0
QA_WAIVER_IDS: []
QA_RELEASE_AT: UNKNOWN
QA_REVIEWER_MODE: SAME_MODEL_PROCEDURAL_SEPARATION
V12_QA_INTERFACE_STATUS: NOT_INTEGRATED
```

该样例字段值`PASS`仅展示schema枚举，绝非当前任何章节的放行票。真实凭证需来自完整QA报告、有效版本和授权审稿。

## 3. 影子验证（先实施，无V12写权限）

- 在下一个合法候选章节的QA完成后，仅生成`QA_SHADOW_GATE_REPORT`，比较冻结正文hash、SOURCE_VECTOR、P0/P1/waiver、当前PREWRITE状态；不触发任何自动COMMIT。
- 修改候选一个字符后，原凭证必须因hash不匹配变`STALE`。
- 改动人物/INFO/REL/FACT来源版本后，旧凭证必须因SOURCE_VECTOR变化变`STALE`。
- 任何P0/P1、审核员来源缺失、未确认正文片段、QA报告缺失，必须`HOLD`；任何`HOLD`不允许转换成业务PASS。
- 从已COMMITTED R003生成的`POST_COMMIT_AUDIT`永远不能冒充当年预提交QA放行票。

## 4. 正式接线前必须通过的四道独立授权

1. 最新事务日志`READ_GUARD`确认无非终态占租；若冲突立即停机。
2. 明确QA凭证存储域、stable注册/Manifest变更的字段许可与依赖影响；需确认是否增加新stable object及是否令PREWRITE失效，不能本文件臆定。
3. 通过合法`MAINTENANCE`事务完成PREPARED→写入→VERIFY→COMMITTED，CAS冲突后重新语义rebase。
4. 重新执行受影响的PREWRITE新鲜度核验，影子用例全过后才允许将`V12_QA_INTERFACE_STATUS`从`NOT_INTEGRATED`改成`INTEGRATED`。

## 5. 失败/回退状态机

`ABSENT → SHADOW_ONLY → READY_FOR_MAINTENANCE_REVIEW → (AUTHORIZED & COMMITTED) INTEGRATED`。任一阶段发生`MISSING_SOURCE / STALE_HASH / BLOCKER / TXN_LEASE_BUSY / FAILED_VERIFY`，转`HOLD`；不得继续递交BODY。当前停点：`SHADOW_ONLY_SPEC_READY`（仅方案，尚未完成真章影子验收）。

## 6. 永久不变的边界

QA不创建故事事实，不发配角色权限，不决定哪名男主最终胜败，不生成COMMIT_ID、不改变世界时钟，也不绕过用户对每约500字片段的确认制度。其唯一新增作用是给现有交易链提供一个可验证的内容质量门槛。

---

## 变更记录

2026-10-08：完成本项初版。核验限定当前样本与方法边界，未修改正文、DELTA、人物主档或V12事务。
