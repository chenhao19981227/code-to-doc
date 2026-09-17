# Kill Bill v2 评测报告（深度修复后）

- **日期**：2026-09-16
- **目标代码根**：`benchmark/killbill`
- **提取范围**：`invoice` + `overdue` + `catalog` + `payment` + `usage`（5 个模块）
- **知识库**：`docs/biz-kb2/`（675 张卡，v1 为 172）
- **黄金集**：`benchmark/golden-set/killbill-invoice.yaml`（40 题，盲化）
- **LLM**：deepseek-chat；检索：内置 BM25，k=5

## 1. v1 → v2 对比

| 指标 | v1（浅提取，2 模块，172 卡） | v2（深提取，5 模块，675 卡） | 变化 |
|---|---|---|---|
| L0 引用有效率 | 100.0%（268 条） | **100.0%（1204 条）** | 持平 |
| L1 幻觉率 | 0.0% | **0.0%**（33 抽样） | 持平 |
| L2 覆盖率（范围对齐后） | 7.9% | 13.7% | ↑ |
| L4 答案准确率 | 9.7% | **29.0% ~ 32.3%** | **≈3.1×** |
| L4 答案准 + 部分（加权） | ~19% | **~45%** | ≈2.4× |
| L4 检索命中率 | 67.7% | **87.1%** | ↑ |
| L4 忠实度 | 100% | 100% | 持平 |
| L4 拒答正确率 | 100% | **100%** | 持平 |

> L4 两次运行分别为 32.3% / 29.0%，差异来自 LLM 判分抖动，**区间 29%–32%**。据此对比时应看区间而非单点。

## 2. 结论：深度是决定性变量

- 去掉"不必读每个文件"的裁剪 + 从 2 个模块扩到 5 个模块 → 卡片 172→675，**准确率约 3 倍**。
- 机制层始终健康：**0 幻觉、0 无效引用、拒答 100%、忠实度 100%**。
- 检索命中率 87.1% 但准确率仅 ~30% → **检索捞得到相关卡，但卡里的具体事实仍不足**。这与 L2 覆盖率 13.7%（方法仅 11.4% 被引用）一致：**覆盖缺口仍在**。

**因此下一阶段的杠杆依然是"提取深度/覆盖"，而非检索或 prompt。** 但已进入收益递减区：v1→v2 卡片增长 3.9 倍换来准确率 3 倍；再往上需要更细的模块拆分与更大预算。

## 3. 本次一并修复的工程问题

| 问题 | 修复 | 验证 |
|---|---|---|
| L2 分母口径失配（子集提取时覆盖率失真，显示 1.3%） | `mechanical.py` 新增 `--scope <p1,p2>` 限定盘点范围（已写入 FORMATS.md §3.3 与 eval/README.md） | 覆盖率 1.3% → 7.9%（v1）→ 13.7%（v2） |
| 解析噪声：`00-overview.md` 的非卡片 `##` 小节被当作卡片报 `missing required field` | `retrieval.py` 仅对带卡片 ID 或含「类型」字段的块做字段校验；纯散文小节仍作为可检索 chunk | 警告数 → 0 |

## 4. 已知问题 / 后续

1. **准确率仍 ~30%，远低于 85% 目标**。根因是覆盖缺口（L2 13.7%）。下一步建议：按子系统（而非模块）粒度拆分提取，例如 invoice 再拆 `calculator` / `generator` / `usage` 三份，各自独立 agent，逼近全量覆盖。
2. **L4 判分有抖动**（同一 KB 两次 29%/32%）。建议：固定 judge 的 temperature=0（`llm.py` 默认已 0，但答案生成也可能抖动），或对每题为多次判分取多数。
3. **`--json` 经 PowerShell 管道会乱码**（UTF-8 → GBK 重编码破坏 JSON）。请用 `--write-report` 或重定向到文件后读取；直接管道会报 `Invalid control character`。
4. **提取任务存在超时中断风险**。大模块单次任务约 3.5 分钟即被中止；本次通过「增量落盘」策略保全（先建文件再逐张追加），缺模块已重试成功。建议 command 中显式要求增量落盘。

## 5. 产物

- `docs/biz-kb2/`：00-overview / glossary / entities / rules / workflows / state-machines / roles-permissions / modules×5 / gaps / questions / confidence-report
- `docs/biz-kb2/verification/L4-qa.md`：本题级判分明细
- `.bizdoc-kb2/cards/`：5 份原始卡（invoice 97 / catalog 74 / overdue 73 / payment 49 / usage 47）

## 6. 复现命令

```bash
python eval/mechanical.py --kb docs/biz-kb2 --root benchmark/killbill --scope invoice,overdue,catalog,payment,usage --json
python eval/fidelity.py   --kb docs/biz-kb2 --root benchmark/killbill --sample 0.05 --json
python eval/qa_eval.py    --kb docs/biz-kb2 --golden benchmark/golden-set/killbill-invoice.yaml --k 5 --write-report
```
