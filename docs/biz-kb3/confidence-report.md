# 置信度统计（Confidence Report）

> 统计口径：按输出文件与 ID 前缀统计 🟢 confirmed / 🟡 inferred / 🔴 gap 数量。

---

### 1. 按输出文件

| 文件 | 卡片总数 | 🟢 confirmed | 🟡 inferred | 🔴 gap |
|---|---|---|---|---|
| glossary.md | 98 | 93 | 5 | 0 |
| entities.md | 72 | 72 | 0 | 0 |
| rules.md | 319 | 318 | 1 | 0 |
| workflows.md | 40 | 40 | 0 | 0 |
| state-machines.md | 15 | 15 | 0 | 0 |
| roles-permissions.md | 11 | 4 | 5 | 2 |
| modules/invoice.md | 143 | 142 | 0 | 1 |
| modules/overdue.md | 118 | 115 | 3 | 0 |
| modules/catalog.md | 117 | 112 | 5 | 0 |
| modules/payment.md | 91 | 88 | 2 | 1 |
| modules/usage.md | 86 | 85 | 1 | 0 |
| **合计** | **555** | **542** | **11** | **2** |

### 2. 按 ID 前缀 / 类型

| 前缀 | 类型 | 卡片总数 | 🟢 | 🟡 | 🔴 |
|---|---|---|---|---|---|
| BR | 业务规则 | 319 | 318 | 1 | 0 |
| TERM | 术语 | 98 | 93 | 5 | 0 |
| ENT | 业务实体 | 72 | 72 | 0 | 0 |
| WF | 业务流程 | 40 | 40 | 0 | 0 |
| SM | 状态机 | 15 | 15 | 0 | 0 |
| ROLE | 角色/权限 | 11 | 4 | 5 | 2 |

### 3. 总体占比

- 🟢 confirmed: 542（97.7%）
- 🟡 inferred: 11（2.0%）
- 🔴 gap: 2（0.4%）
- 合计: 555 张卡（合并前 562 张，去重合并 7 处）