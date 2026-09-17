---
name: biz-doc-verify
description: 调用 eval/ 下的评测脚本（mechanical/fidelity/qa_eval），对已生成的知识库跑 L0引用有效性 / L1忠实度 / L2覆盖率 / L4 QA端到端，并把合并报告写入 <kb_dir>/verification/。脚本缺失时如实说明，绝不编造结果。不直接面向用户，供 biz-doc / biz-doc-verify command 的 subAgent 调用。
---

# Biz Doc Verify - 知识库评测编排 Skill

本 skill 只做一件事：**按 `docs/FORMATS.md` §3 的固定 CLI 调用 `eval/` 脚本，收集 JSON 结果，对照成功阈值生成合并报告，写入 `<kb_dir>/verification/`。**

## 输入

调用方（subAgent）会提供：
- `kb_dir`：待评测知识库目录（默认 `docs/biz`）
- `code_root`：代码根目录（对应 `--root`）
- `golden`：黄金集 YAML 路径（对应 `qa_eval --golden`；可为空）
- `sample`：L1 抽样比例，默认 `0.3`
- `k`：L4 检索 top-k，默认 `5`
- `workdir`：工作目录（= 项目根 `code-to-doc`）

**下游必须通过文件交接**：调用方只传路径，subAgent 自己 Read。

## 执行步骤

### 1. 前置校验（缺一不可）

1. 校验 `kb_dir` 存在且含 `docs/FORMATS.md` §1.1 的关键文件（至少 `00-overview.md`、`rules.md`）。缺失则报错停止。
2. 校验三个脚本是否存在：
   - `eval/mechanical.py`
   - `eval/fidelity.py`
   - `eval/qa_eval.py`
3. **若任一脚本不存在**：不要臆造任何指标，直接产出"评测未就绪"报告，明确列出缺失脚本路径与所需 CLI，然后结束。报告写入 `<kb_dir>/verification/NOT-READY.md`。

### 2. 读取 LLM 配置

从环境变量或 `workdir` 读取：`LLM_PROVIDER`（默认 `deepseek`）、`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`。
- `LLM_PROVIDER=none`：只跑不依赖 LLM 的 L0/L2，**跳过 L1/L4** 并在报告中注明原因。
- 未配置 `LLM_API_KEY` 且 provider 非 `none`：提示 L1/L4 可能失败，仍尝试执行并原样记录错误。

### 3. 执行评测（串行，用 Bash 原样调用）

必须使用**下列三条固定命令**（参数按输入替换，其余签名不得改动）：

```bash
python eval/mechanical.py --kb <kb_dir> --root <code_root> --json
python eval/fidelity.py   --kb <kb_dir> --root <code_root> --sample <sample> --json
python eval/qa_eval.py    --kb <kb_dir> --golden <golden.yaml> --k <k> --json
```

规则：
- 必须逐条通过 Bash 执行，**不得用自写逻辑替代脚本**，不得改写输出。
- 每条命令的 stdout JSON 与 stderr 原样保存到 `workdir/.bizdoc/eval-raw/`（`mechanical.json` / `mechanical.stderr.txt` …），便于追溯。
- 若 `golden` 为空：**跳过 `qa_eval.py`**，在报告中标注"未提供黄金集，L4 未执行"。
- L0/L2 失败 → 记录错误并停止（基础评测不可用）。
- L1/L4 失败（如缺 key）→ 记录错误，保留已成功的层，继续生成报告。

### 4. 汇总指标（只用 FORMATS.md 口径）

从 JSON 中提取，**不得新造指标名**：

| 层 | 脚本 | 指标 |
|---|---|---|
| L0 引用有效性 | `eval/mechanical.py` | `invalid_citation_rate`、`total_citations` |
| L2 覆盖率 | `eval/mechanical.py` | `coverage_rate`、`missing_entities[]` |
| L1 引用忠实度 | `eval/fidelity.py` | `hallucination_rate`、`verdicts{}` |
| L4 QA 端到端 | `eval/qa_eval.py` | `answer_accuracy`、`faithfulness`、`retrieval_hit_rate`、`refusal_correctness` |

### 5. 对照成功阈值（FORMATS.md §3.5）

| 指标 | 目标 |
|---|---|
| 引用有效率 | 100% |
| 幻觉率 | < 5% |
| 覆盖率 | ≥ 85% |
| 答案准确率 | ≥ 85% |
| 拒答正确率 | ≥ 90% |

逐项标注 ✅ 达标 / ❌ 未达标 / ⚠️ 未执行，并给出实际值。

### 6. 写出报告

1. 确保 `<kb_dir>/verification/` 存在。
2. 写 `<kb_dir>/verification/report.md`：合并报告（分层结果、指标表、阈值对照、`missing_entities[]` 摘要、`verdicts{}` 分布、失败与跳过原因、原始 JSON 路径）。
3. 复制原始 JSON 到 `<kb_dir>/verification/`（`mechanical.json`、`fidelity.json`、`qa.json`，缺失的跳过并标注）。
4. 写 `<kb_dir>/verification/summary.json`：机器可读的合并指标 + `layers`（每层的 `status`: `ok`/`failed`/`skipped`）。

## 输出格式

```
<kb_dir>/verification/
├── report.md          # 人类可读合并报告
├── summary.json       # 机器可读合并指标 + 分层状态
├── mechanical.json    # L0+L2 原始输出（如执行）
├── fidelity.json      # L1 原始输出（如执行）
└── qa.json            # L4 原始输出（如执行且提供黄金集）
```

`summary.json` 结构（示例）：

```json
{
  "kb_dir": "docs/biz",
  "code_root": "<代码根>",
  "golden": "<黄金集目录>/x.yaml",
  "layers": {
    "L0": { "script": "eval/mechanical.py", "status": "ok" },
    "L2": { "script": "eval/mechanical.py", "status": "ok" },
    "L1": { "script": "eval/fidelity.py", "status": "skipped", "reason": "LLM_PROVIDER=none" },
    "L4": { "script": "eval/qa_eval.py", "status": "ok" }
  },
  "metrics": {
    "invalid_citation_rate": 0.0,
    "total_citations": 0,
    "coverage_rate": 0.0,
    "missing_entities": [],
    "hallucination_rate": null,
    "verdicts": {},
    "answer_accuracy": null,
    "faithfulness": null,
    "retrieval_hit_rate": null,
    "refusal_correctness": null
  },
  "thresholds_passed": { "citation_validity": true, "hallucination": null, "coverage": false, "answer_accuracy": null, "refusal_correctness": null }
}
```

## 约束

- **脚本不存在时如实说明，绝不编造评测结果**（不得 AI 自评冒充脚本指标）。
- **只用固定 CLI 签名**，不得改参数名或自写等价脚本替代 `eval/`。
- **只用 FORMATS.md §3.2/§3.4 的指标名**，不得发明新指标。
- **不修改源码、不修改 `docs/FORMATS.md` / `README.md`、不修改知识库正文**；只写 `<kb_dir>/verification/` 与 `.bizdoc/eval-raw/`。
- 失败信息必须原样保留（stderr），不得美化或掩盖。
