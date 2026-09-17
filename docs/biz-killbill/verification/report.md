# Kill Bill 实跑评测报告（真实规模）

- **日期**：2026-09-16
- **目标代码根**：`benchmark/killbill`（浅克隆，16 个 Maven 模块，HEAD `cb60779`）
- **提取范围**：仅 `invoice` + `overdue` 两个模块（成本裁剪）
- **知识库**：`docs/biz-killbill/`（172 张卡）
- **黄金集**：`benchmark/golden-set/killbill-invoice.yaml`（40 题，盲化，跨 6 个业务域）
- **LLM**：deepseek-chat；检索：内置 BM25，k=5

## 1. 结果

### 全量黄金集（40 题，跨 6 域）

| 指标 | 结果 | 目标 | 判定 |
|---|---|---|---|
| L0 引用有效率 | **100.0%**（268 条，0 无效） | 100% | ✅ |
| L1 幻觉率 | **0.0%**（抽样 16，supported=16） | < 5% | ✅ |
| L2 覆盖率 | 1.3%（109/8135） | ≥ 85% | ❌ 口径失配 |
| L4 答案准确率 | 9.7%（31 正样本：3 对 / 6 部分 / 22 错） | ≥ 85% | ❌ |
| L4 忠实度 | 100%（40/40 有据） | — | ✅ |
| L4 检索命中率 | 67.7%（21/31） | — | ⚠️ |
| L4 拒答正确率 | **100.0%**（9/9 负样本，0 幻觉） | ≥ 90% | ✅ |

### 提取范围内子集（27 题，仅 invoice + overdue）

| 指标 | 结果 |
|---|---|
| 答案准确率 | 20.0%（20 正样本：4 对 / 6 部分 / 10 错） |
| 检索命中率 | 80.0%（16/20） |
| 忠实度 / 拒答正确率 | 100% / 100% |

## 2. 与合成场景对比

| | 合成场景 | Kill Bill |
|---|---|---|
| 规模 | 19 个文件 | 2 / 16 模块（仓库 8135 实体） |
| 提取预算 | 读全部文件 | 有"scale control"（按信号优先，非全读） |
| 卡片数 | 133 | 172 |
| L0 | 97.8% | **100%** |
| L1 | 0.0% | 0.0% |
| L4 准确率 | **87.5%** | 9.7%（范围内 20.0%） |

## 3. 诊断

**流程机制在大规模下依然完好**：0 无效引用、0 幻觉、拒答 100%、忠实度 100%、检索命中 80%。
唯一失效的是**深度**。

按"症状 → 根因"拆解：

| 症状 | 根因 | 证据 |
|---|---|---|
| L4 准确率 20% 但检索命中 80% | 检索能捞到相关卡，但**卡里没有那道题要的具体事实** | 忠实度 100% 说明模型没有编造，而是"手上没有料" |
| 答对的集中在简单/概念题 | 组合题、阈值题（如 tier 策略、回溯周期、402 语义、Janitor）在卡中缺失 | 大量 `wrong` 集中在这些题 |
| 卡片仅 172 张覆盖 2 个模块 | 提取时施加了 "scale control"（不读每个文件）+ 只提 2/16 模块 | 卡片数与领域密度不匹配 |
| L2 覆盖率 1.3% | **口径失配**：扫描器盘点整仓 8135 实体，却只提取 2 个模块 | class 913、method 6961 为分母 |

**结论：管线（scan→extract→synthesize→retrieve→answer）是正确的；瓶颈在 extract 的深度预算，以及 L2 的分母口径。**

## 4. 修复建议（按优先级）

1. **L2 口径修正（必须）**：`mechanical.py` 的 `--root` 应与提取范围一致，或新增按模块白名单盘点。否则子集提取永远显示 1% 覆盖率，指标无意义。
2. **提高 extract 深度预算**：去掉"不必读每个文件"的裁剪；对每个目标模块，穷尽读取所有含业务规则的文件（service/calculator/规则类），这才是质量的来源。合成场景之所以 87.5%，正是因为读了全部 19 个文件。
3. **按模块并行提取**：command 已设计为逐模块并行 `run_in_background=true`；实跑时因无法委派被串行化。真正使用时（opencode 内）并行能大幅提速。
4. **提升检索粒度**：当前以"卡"为 chunk。对超长卡（如 `modules/invoice.md` 35 KB）应做次级切分，否则单卡内容过多、命中后有效信息被稀释。
5. **问题类型分层**：把黄金集按 `easy/medium/hard` 分层看指标，能更早发现"难题系统性失败"。

## 5. 复现命令

```bash
python eval/mechanical.py --kb docs/biz-killbill --root benchmark/killbill --json
python eval/fidelity.py   --kb docs/biz-killbill --root benchmark/killbill --sample 0.1 --json
python eval/qa_eval.py    --kb docs/biz-killbill --golden benchmark/golden-set/killbill-invoice.yaml --k 5 --json
python eval/qa_eval.py    --kb docs/biz-killbill --golden benchmark/golden-set/killbill-invoice-overdue-subset.yaml --k 5 --json
```

生成命令（如需重跑，先删除 `docs/biz-killbill` 与 `.bizdoc-killbill`）：

```
/biz-doc benchmark/killbill --modules invoice,overdue --out docs/biz-killbill --golden benchmark/golden-set/killbill-invoice.yaml
```
