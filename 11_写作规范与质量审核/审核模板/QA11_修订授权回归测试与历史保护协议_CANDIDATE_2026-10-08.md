# 《偏航》独立正文质量审核｜第11项｜QA11_修订授权回归测试与历史保护协议_CANDIDATE_2026-10-08

STATUS: CANDIDATE / QA_WORKFLOW / NOT_STORY_CANON / NOT_V12_STABLE_OBJECT
DATE: 2026-10-08
DESIGNATED_PATH: `/偏航/11_写作规范与质量审核/审核模板/QA11_修订授权回归测试与历史保护协议_CANDIDATE_2026-10-08.md`
TASK_NUMBER: QA-11

## 文件使用说明

- **文件用途**：规定收到缺陷后谁能修、最多能修多少、怎样证明修复未造成新的剧情/事务错误。
- **新增原因**：质量审核如果拿到直接改正文的权力，会破坏约500字确认、既有不可变R003和V12提交链。
- **内容边界**：仅为QA方法或审计材料；不新增正史、事实账与事务记录，不修改既有COMMITTED正文。
- **权威级别与状态**：CANDIDATE / QA_WORKFLOW；低于用户最新要求、根级前置指令、故事CURRENT、V12事务。
- **依赖与上游**：根级前置指令、11目录独立QA总规、Q01—Q22矩阵、QA工单模板、第一章R003有效正文与DELTA；需要写作时再按章节加载人物CURRENT与INFO/FACT/REL。
- **后续使用方法**：先核对审核对象fingerprint与真正CURRENT；只允许对候选或只读历史对象给出缺陷及修复建议；若规则发生调整，审计文件保留历史证据、方法文件需要审议后更新。
- **与其他文件关系**：承接11目录三份CURRENT总规、Q01—Q22矩阵与工单模板；服从根级前置指令和V12唯一生产入口。
- **禁止误用**：不得把本文件当QA放行凭证、故事真相或V12正式机器闸；不得以审稿结果未经授权改写R003。

---

## 1. 四种修订入口

| 对象状态 | 审稿权力 | 写作者可采取的路径 | 明确禁止 |
|---|---|---|---|
| PREVIEW/WORKING未确认 | 开QA单并建议改稿 | 按当前正文约500字范围重新做八轮内检 | 不得宣称进入正式BODY |
| USER_APPROVED_SEGMENT | 只读指出当前或衔接缺陷 | 用户指定回改范围后单段修复并再次确认 | 不得擅自回改已批准相邻片段 |
| CHAPTER_CANDIDATE | 审整章、冻结hash、发REVISE | 分授权500字段复核+全章重审 | 不得以评分掩盖P0/P1 |
| COMMITTED_CURRENT R003 | `POST_COMMIT_FINDING` | 用户授权后走合法CHAPTER_REVISION或RETCON事务链 | 绝不原位改R003 BODY/DELTA |

## 2. 最小安全修订原则

每条工单至少明确`EDIT_SCOPE / ALLOWED_FACTS / FROZEN_NEIGHBORS / SENSITIVE_INFO / EXPECTED_DELTA / NON_GOALS`。例如替换“指尖”若只改一处触碰动作，不得顺带改变黎栖雾是否签字、是否获知09-A、容既白是否有权回复；“句子太短”可通过动作合句修复，但不改变视角权限。

## 3. 回归测试清单

- 字符检查：所有禁词、句长、段落及破折号再次扫描；保留扫描前后两版结果。
- 章节检查：开章/结章的FACT/INFO/REL/PROC变化一致，09-A仍只可证明节点存在。
- 关系检查：修改中不可把专业权限偷换成私人亲密/复合授权。
- 结构检查：若合并段落，前后情绪转折与钩子是否仍成立。
- 程序检查：已COMMITTED样本必须重新走所需事务，不能用QA文档代替。

## 4. 回归结果矩阵

`DEFECT_ID | OLD_SHA256 | NEW_SHA256 | USER_AUTH_REF | EDITED_CHAR_WINDOW | REGRESSION_Q01_22 | STORY_DELTA_EQUAL_OR_AUTHORIZED | RESULT`。

`NEW_SHA256 != OLD_SHA256`时，先认定旧凭证失效；若属于核心INFO/REL/FACT改动，无论改动几个字都强制整章重审。非核心局部替换至少复核当前片段加前后衔接。

## 5. 失败态

`HOLD_NO_PERMISSION`、`HOLD_SOURCE_STALE`、`REVISE_REQUIRED`、`RETEST_FAILED`、`READY_FOR_QA_REVIEW`、`POST_COMMIT_REVISION_REQUIRED`。不能自称“修改过所以PASS”。

## 6. R003本轮决策

已发现的语言缺陷进入`POST_COMMIT_FINDING`；本轮用户命令是继续QA十项，不是授权改第一章正文。因此不产生任何`R004`、候选BODY、DELTA、事务记录。

---

## 变更记录

2026-10-08：完成本项初版。核验限定当前样本与方法边界，未修改正文、DELTA、人物主档或V12事务。
