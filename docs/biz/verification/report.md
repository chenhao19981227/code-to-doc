# 首次端到端评测报告

- **日期**：2026-09-16
- **目标代码根**：`scenarios/synthetic-springboot`（自建合成场景，19 个 Java 文件）
- **知识库**：`docs/biz/`（133 张知识卡）
- **黄金集**：`benchmark/golden-set/synthetic-springboot.yaml`（32 题 = 24 正 + 8 负，盲化）
- **LLM**：deepseek-chat（judge 与作答均使用）
- **检索**：内置 BM25，k=5

## 1. 结果总览

| 层 | 指标 | 结果 | 目标 | 判定 |
|---|---|---|---|---|
| L0 | 引用有效率 | 97.8%（180 条中 4 条无效） | 100% | ❌ |
| L1 | 幻觉率 | 0.0%（抽样 16，supported=16） | < 5% | ✅ |
| L2 | 覆盖率 | 53.1%（81 实体中 43 被引用） | ≥ 85% | ❌ |
| L4 | 答案准确率 | 87.5%（24 正样本：21 对 / 1 部分 / 2 错） | ≥ 85% | ✅ |
| L4 | 答案忠实度 | 100%（32/32 有据） | — | ✅ |
| L4 | 检索命中率 | 100%（24/24 正样本命中） | — | ✅ |
| L4 | 拒答正确率 | 100%（8/8 负样本正确拒答，0 幻觉） | ≥ 90% | ✅ |
| — | 事实覆盖探针 | 24/25 关键事实 token 出现在知识库 | — | ✅ |

**结论：5 项阈值中 3 项通过。核心目标（答案准确率 / 拒答 / 幻觉率）全部达标；L0 与 L2 未达标，属可修复的工程问题。**

## 2. L0 明细（4 条无效引用 / 2 个根源）

| 卡片 | 引用 | 问题 |
|---|---|---|
| TERM-001 | `common/AmountUtils.java:6-8` | 引到纯注释行（comment_only_or_blank） |
| BR-007 | `coupon/CouponService.java:13-16` | 引到纯注释行（comment_only_or_blank） |

两条重复计数（同一引用在解析中出现两次）。**根源**：extract 阶段选了只包含注释的行区间。

## 3. L2 明细（覆盖率 53.1%）

| 实体类型 | 被引用 / 总数 | 覆盖率 |
|---|---|---|
| class | 16 / 16 | 100.0% |
| enum | 3 / 3 | 100.0% |
| interface | 1 / 2 | 50.0% |
| **method** | **21 / 58** | **36.2%** |
| permission | 2 / 2 | 100.0% |

**根源**：知识卡聚焦「业务规则所在的具体行」，因此大多数 public 方法未被「溯源」区间覆盖。业务知识库不必然需要覆盖所有方法——这是**指标口径与产物目标的错配**，不是纯缺陷。

## 4. L4 明细（2 错 1 部分）

| 题号 | 类型 | 判定 |
|---|---|---|
| KB-Q018 | positive | partial |
| KB-Q020 | positive | wrong |
| KB-Q021 | positive | wrong |
| KB-N001..N008 | negative | 全部 refused ✅ |

其余 21 道正样本全部 correct。

## 5. 已知问题与修复建议

| # | 问题 | 建议修复 |
|---|---|---|
| 1 | L0：2 张卡引到纯注释行 | extract 阶段增加「引用行必须含可执行代码」的自检；或将区间下移到代码行 |
| 2 | L2 覆盖率口径偏严 | 两个方向：① 在 synthesize 为每个类生成一张「模块实体卡」，溯源覆盖整个类区间，可一次性拉高 method 覆盖率；② 或把 L2 口径改为「业务相关实体」（需在 FORMATS 中明确） |
| 3 | 解析噪声：`00-overview.md` 的 `##` 小节被当作卡片校验，报 `missing required field` | 解析器跳过不含 `类型` 字段的小节；或在 FORMATS 中规定 overview 使用非 `##` 结构 |
| 4 | KB-Q020/Q021 答错 | 复核这两题的检索片段是否充分；必要时给该类多跳/组合型问题补充更完整的卡片 |

## 6. 复现命令

```bash
# L0 + L2（无需 LLM）
python eval/mechanical.py --kb docs/biz --root scenarios/synthetic-springboot --json

# L1 忠实度（需 LLM）
python eval/fidelity.py --kb docs/biz --root scenarios/synthetic-springboot --sample 0.15 --json

# L4 端到端（需 LLM）
python eval/qa_eval.py --kb docs/biz --golden benchmark/golden-set/synthetic-springboot.yaml --k 5 --json
```

LLM 环境变量：`LLM_PROVIDER=deepseek`、`LLM_API_KEY=<key>`、`LLM_BASE_URL=https://api.deepseek.com`、`LLM_MODEL=deepseek-chat`。
