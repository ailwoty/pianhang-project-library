# 《偏航》项目治理增强层 V1

状态：WORKING / GOVERNANCE_UPGRADE / NOT_STORY_CANON
用途：在现有CURRENT、CANON、V12事务体系之上，补充任务状态机、依赖影响控制、事实生命周期控制，提升长期生产可靠性。

## 文件边界

本文件不创造人物、世界、剧情事实，不修改V12运行态，不替代任何CURRENT。
本文件只定义治理增强机制。

## 一、任务状态机 TASK_STATE_MACHINE

所有复杂任务必须具备明确生命周期：

REQUESTED
→ PRECHECKED
→ PLANNED
→ EXECUTING
→ REVIEWING
→ WAIT_CONFIRM
→ COMMITTED
→ ARCHIVED

规则：

1. 未经过PRECHECKED不得执行实质修改。
2. EXECUTING状态产生的内容默认属于WORKING，不自动成为正史。
3. WAIT_CONFIRM状态不得进入正式正文或运行态。
4. COMMITTED必须具备合法写入路径、权威来源和回读验证。

## 二、依赖影响图 DEPENDENCY_IMPACT_GRAPH

所有核心对象维护影响关系：

人物对象：
人物主档 → 关系矩阵 → 章节合同 → 正文 → 情绪曲线

组织对象：
组织CURRENT → 权限 → 项目资源 → 运行态 → 正文

时间对象：
世界时钟 → 事件 → 人物年龄 → 章节合同

任何修改核心对象时，必须执行影响扫描：

1. 直接影响对象；
2. 间接影响对象；
3. 是否触发PREWRITE失效；
4. 是否需要同步索引。

## 三、事实生命周期 FACT_LIFECYCLE

所有可进入故事的信息按照生命周期管理：

UNKNOWN
→ CANDIDATE
→ VALIDATED
→ COMMITTED
→ CANON_LOCKED
→ SUPERSEDED
→ ARCHIVED

规则：

- UNKNOWN不得由推测填充。
- CANDIDATE只能作为作者参考。
- COMMITTED必须来源明确。
- SUPERSEDED必须保留替代关系。
- ARCHIVED保留审计价值。

## 当前实施状态

第一阶段完成：

1. 任务状态机框架建立。
2. 依赖影响分析框架建立。
3. 事实生命周期框架建立。

后续阶段继续增加：

- 冲突扫描机制；
- 章节生产加载包；
- 自动风险等级判断。
