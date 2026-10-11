# 《偏航》独立正文质量审核｜第25项｜QA放行凭证的受信来源与重放威胁模型

STATUS: CANDIDATE / QA_SUPPORT_ONLY / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT
TASK_NUMBER: QA-25
DATE: 2026-10-08
DESIGNATED_PATH: `/偏航/11_写作规范与质量审核/审核模板/QA25_QA放行凭证的受信来源与重放威胁模型_CANDIDATE_2026-10-08.md`

## 文件使用说明

- **文件用途**：对未来审批及QA令牌做威胁评审，所有要求落地前不得解除HOLD。
- **新增原因**：QA16只验证外部提供的文件相互吻合，不识别谁伪造过整套文件。
- **内容边界**：威胁建模与受信存证接口提案，不生成密钥、不执行签发、不可自行定义V12生产写权限。；不直接改写人物CURRENT、R003 BODY/DELTA、V12事务和时间轴。
- **权威级别与状态**：`CANDIDATE / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT`；本文件不是任何三份既存QA CURRENT的竞争版本。
- **依赖与上游来源**：上游：`/偏航/00_偏航项目_任务前置执行指令_持续更新.md`，11目录三份CURRENT QA规则（QA-1.0、QA-MATRIX-1.0、QA-REPORT-1.0），QA04—QA23；V12当前事务日志 stable `libfile_4b84718c33448191bf6036bd936c77a5`，R003正文/DELTA，第二章单章合同WORKING。上游出现变化时按最新事实与版本重新回读，不缓存这一轮验收。
- **后续使用方法**：审核员冻结目标和来源、记录证据定位、逐项复核；已提交章节仅采用POST_COMMIT只读方式；对未来审批及QA令牌做威胁评审，所有要求落地前不得解除HOLD。
- **与其他文件关系**：补充QA23的八道接线前置条件，使用QA总规裁决、矩阵Q01—Q22判错、工单模板记载结果。
- **禁止误用**：不得据本文件发放正式QA_RELEASE，不得把构造样例变成已经发生的小说事实；不得跳过用户500字确认、八轮内检、V12 READ_GUARD/PREWRITE/事务。

---

## 1. 攻击者能力矩阵

| 威胁 | 可实施方式 | QA16为何抓不到 | 必要外部证据 | 裁决 |
|---|---|---|---|---|
| 报告与令牌一起伪造 | 造一份score=95/P0=0的JSON，全部哈希自洽 | 结构正确不代表审稿人真实 | 可信审稿身份、签发权限和不可变提交点 | HOLD_UNTRUSTED_ISSUER |
| 用户500字确认伪造 | `user_approval_ref`填入任意非空字符串 | QA16只检查字符串 | 与真实消息及确认片段指纹关联的只读批准凭据 | HOLD_APPROVAL_UNVERIFIED |
| 旧章令牌重放 | 将合法报告用于新世界时钟或不同章节 | 若章UID/epoch没有可信绑定可能被重用 | 章UID、BASE_SNAPSHOT_ID、BODY hash、来源版本及审核epoch不可重复约束 | HOLD_REPLAY |
| 原稿同名覆盖 | path相同但物理版变化 | 未核对最新稳定版本时可能消费旧快照 | stable ID + physical版本 + SHA-256 + 回读时间 | HOLD_STALE_ARTIFACT |
| 规则替换 | 较宽松的候选QA当作CURRENT | 只比自报版本字段 | 只从权威索引取QA规则 stable 身份 | HOLD_WRONG_RULE_ROOT |
| 审稿利益冲突 | 作者自发签发审核PASS | 逻辑自洽仍可能主观失真 | 审稿角色声明、差异审查、独立复核者 | HOLD_REVIEW_INDEPENDENCE |

## 2. 信任边界

建议把`AUTHOR_SUBMISSION`、`INDEPENDENT_QA_REPORT`、`USER_APPROVAL_EVIDENCE`、`V12_TRANSACTION_CONTROL`四个角色分离：作者不能以自己生成的JWT式文本证明审核独立；审稿模型不证明用户已点确认；QA接口不代替正式事务。**纯SHA256哈希保证完整性对比，不证明签发真实性**。

## 3. 最低绑定元组（提案）

`(project_root, CHAPTER_UID, chapter_revision, BODY_SHA256, source_vector, QA_RULE_STABLE_IDs, QA_REPORT_HASH, USER_APPROVAL_EVIDENCE_REF, REVIEWER_AUTH_REF, audit_epoch, expiry_or_invalidated_by, V12_BASE_SNAPSHOT_ID)`。签名验证实现与私钥归属由正式授权控制方决定，本文件不伪造签名。

## 4. 失效条件与审计准则

稿件改变、源版本变化、根规则变更、下游拒绝、审批边界变化、原章修订、新一轮V12 `INVALIDATES`任一满足，先撤销**业务使用资格**，记录`TOKEN_STALE`。保留旧令牌为历史证据，不删除历史工单；不将一次失效等同于故事COMMIT撤销。

## 5. 本轮真实只读攻击验证

调用从Library物化的现有QA16只读源文件，保留其`self_test()` 20/20成功；然后在**合成正文与合成源向量**上将报告的审稿员字符串改为`UNVERIFIED_ATTACKER_REVIEWER`、审批引用改为`FABRICATED_USER_APPROVAL_REF`，同步计算报告hash，使攻击者自报的材料内部一致。实际`evaluate()`输出：`verdict=SHADOW_MATCH_ONLY; production_authorized=false`。这是一项**已运行的阴性安全测试**：结构校验不能识破同批伪造；正确行为是绝不发正式QA_RELEASE。测试产物为交付包的`QA25_受信链对抗实测结果.json`，不涉及任何真人审批或现实第二章正文。

---

## 变更记录

2026-10-08：第25项初次建立，保留QA-1.0三份CURRENT原样，审计及候选规则未获独立正史升级或V12机器接入。
