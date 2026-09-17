# 置信度统计 (Confidence Report)


> 指标口径遵循 docs/FORMATS.md §1.2：🟢 confirmed（有 file:line 证据）/ 🟡 inferred（命名/模式推断）/ 🔴 gap（无法确定）。

## 一、按输出文件的置信度计数

| 输出文件 | 🟢 confirmed | 🟡 inferred | 🔴 gap | 合计 |
|---|---|---|---|---|
| glossary.md | 56 | 1 | 0 | 57 |
| entities.md | 46 | 0 | 0 | 46 |
| rules.md | 177 | 0 | 0 | 177 |
| workflows.md | 24 | 0 | 0 | 24 |
| state-machines.md | 9 | 0 | 0 | 9 |
| roles-permissions.md | 4 | 5 | 2 | 11 |

## 二、按模块（modules/<name>.md）的置信度计数

| 模块 | 🟢 confirmed | 🟡 inferred | 🔴 gap | 合计 |
|---|---|---|---|---|
| catalog | 73 | 1 | 0 | 74 |
| invoice | 95 | 0 | 1 | 96 |
| overdue | 70 | 3 | 0 | 73 |
| payment | 47 | 1 | 1 | 49 |
| usage | 44 | 1 | 0 | 45 |

## 三、按类型×置信度

| 前缀 | 类型 | 🟢 confirmed | 🟡 inferred | 🔴 gap | 合计 |
|---|---|---|---|---|---|
| TERM | 术语 | 56 | 1 | 0 | 57 |
| ENT | 业务实体 | 46 | 0 | 0 | 46 |
| BR | 业务规则 | 177 | 0 | 0 | 177 |
| WF | 业务流程 | 24 | 0 | 0 | 24 |
| SM | 状态机 | 9 | 0 | 0 | 9 |
| ROLE | 角色/权限 | 4 | 5 | 2 | 11 |
| **合计** |  | **316** | **6** | **2** | **324** |

## 四、总体占比

- 卡片总数（去重后）：**324**
- 🟢 confirmed：316（97.5%）
- 🟡 inferred：6（1.9%）
- 🔴 gap：2（0.6%）

## 五、输入概况

- 原始卡：340 张（invoice 97 / catalog 74 / overdue 73 / payment 49 / usage 47）
- 去重合并：11 组，合并后卡数 324（净减少 16）