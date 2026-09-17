---
name: biz-doc-synthesize
description: 合并各模块原始知识卡（去重/消歧/同义词合并/引用并集），分配全局唯一编号，按 FORMATS.md §1.1 文件清单输出最终业务知识库到指定根目录。不直接面向用户，供 biz-doc command 的 subAgent 调用。
---

# Biz Doc Synthesize - 知识卡合并与知识库落盘 Skill

本 skill 只做一件事：**读取 `.bizdoc/cards/*.md` 的原始卡，去重/消歧/合并后，按 `docs/FORMATS.md` §1.1 的文件清单把最终业务知识库写到输出根目录。**

## 输入

调用方（subAgent）会提供：
- `cards_dir`：原始卡目录，约定 `.bizdoc/cards/`
- `inventory_path`：`.bizdoc/inventory.json`
- `output_root`：知识库输出根目录，默认 `docs/biz/`
- `target_root`：代码根目录（仅用于校验溯源路径可解析）
- `workdir`：工作目录（= 项目根 `code-to-doc`）

**下游必须通过文件交接**：调用方只传路径，subAgent 自己 Read。

## 执行步骤

### 1. 收集原始卡

1. Glob `cards_dir/*.md`，Read 每一份。
2. 按 `^## ` 解析为卡片对象：`id`、`title`、`类型`、`同义词[]`、`模块`、`置信度`、`溯源[]`、正文块。
3. 若 `cards_dir` 为空 → 不产出任何知识库文件，报错并说明（不要生成空壳）。

### 2. 去重（Dedupe）

判定为同一概念的卡（满足任一）：
- 溯源指向同一代码位置（`file:line` 重叠）。
- 标题/术语语义相同（中英对照、缩写与全称）。

合并策略：
- `同义词` = 各卡同义词并集，去重、保留中英文。
- `置信度` = 取最高（🟢 > 🟡 > 🔴）；若合并中丢失了 🟢 的引用依据，降级为 🟡。
- `溯源` = 各卡引用并集（去重，逗号分隔）。
- 正文 = 保留信息量最大者，可拼接互补段落。

### 3. 消歧（Disambiguate）

同一个词在不同上下文含义不同（如两个模块各有 `Order`）：
- **拆成独立卡**，标题加限定（如 `订单（计费域）` / `订单（履约域）`）。
- 在 `questions.md` 记录该歧义，供人工确认。

### 4. 分配全局唯一编号

- 按固定前缀分组：`TERM-` / `ENT-` / `BR-` / `WF-` / `SM-` / `ROLE-`。
- 每组从 `001` 连续编号，替换各模块的临时编号。
- 排序稳定（先按模块名，再按原临时编号），保证重复运行结果一致。

### 5. 按类型分派到目标文件（严格对应 FORMATS.md §1.1）

| 卡片前缀 | 目标文件 |
|---|---|
| `TERM-` | `glossary.md` |
| `ENT-` | `entities.md` |
| `BR-` | `rules.md` |
| `WF-` | `workflows.md` |
| `SM-` | `state-machines.md` |
| `ROLE-` | `roles-permissions.md` |

单模块深度知识另写入 `modules/<name>.md`：该模块的全部卡（含上述各类）+ 模块级概述段落。

### 6. 生成汇总文件

- `00-overview.md`：系统/模块概览 + 业务能力清单（按模块列出能力条目，引用相关卡 ID）。
- `gaps.md`：所有 🔴 gap 卡（列出 ID/标题/缺失点）。
- `questions.md`：待人工确认的问题（消歧项、🟡 推断待验证项、🔴 缺证据项）。
- `confidence-report.md`：按类型×置信度的计数表 + 总体 🟢/🟡/🔴 占比（**指标名严格使用 FORMATS.md 措辞**，不新造指标）。

### 7. 落盘

1. 确保 `output_root` 及 `output_root/modules/`、`output_root/verification/` 存在（`verification/` 仅供 verify 写入，此处建空目录即可）。
2. 写出 §1.1 的全部文件。**文件清单必须完整**：
   `00-overview.md`、`glossary.md`、`entities.md`、`rules.md`、`workflows.md`、`state-machines.md`、`roles-permissions.md`、`modules/<name>.md`、`gaps.md`、`questions.md`、`confidence-report.md`。
3. 若某类无卡片，仍写出该文件，正文写明"本类型无卡片"（保持清单完整、解析器稳定）。

## 输出格式

- 目录树：

```
<output_root>/
├── 00-overview.md
├── glossary.md
├── entities.md
├── rules.md
├── workflows.md
├── state-machines.md
├── roles-permissions.md
├── modules/
│   └── <name>.md
├── gaps.md
├── questions.md
├── confidence-report.md
└── verification/        # 空目录，供 biz-doc-verify 写入
```

- 每个 `.md` 内的检索单元仍是 `## <ID> <标题>` 标准卡，字段与 `docs/FORMATS.md` §1.2 完全一致。
- 同时写一份 `.bizdoc/synthesis-report.json`：`cards_in`、`cards_out`、`merged`（合并映射）、`split`（消歧拆分）、`renumber_map`（临时→全局 ID）。

## 约束

- **绝不发明新格式**：ID 前缀、必填字段、置信度三级、溯源格式严格照 `docs/FORMATS.md`。
- **绝不在无溯源时标 🟢**：合并后若 🟢 失去引用依据，必须降级。
- **文件清单完整**：即使某类型为空也要写出对应文件。
- **不修改源码、不修改 `docs/FORMATS.md` / `README.md`。**
- 只写 `output_root` 与 `.bizdoc/`，其他位置一律不动。
- 输出必须可重复：相同输入产出相同编号与排序。
