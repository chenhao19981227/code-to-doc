---
name: biz-doc-verify
description: 对已生成的业务知识库重跑验证（仅评测，不重新提取）。调用 eval/ 下的 mechanical/fidelity/qa_eval，输出 L0引用有效性 / L1忠实度 / L2覆盖率 / L4 QA端到端 合并报告到 <kb_dir>/verification/。触发词包括'重跑验证'、'验证知识库'、'biz doc verify'、'rerun eval'。用户输入格式：/biz-doc-verify <kb_dir> [--root <code_root>] [--golden <yaml>] [--sample 0.3] [--k 5]
---

# Biz Doc Verify - 知识库验证编排器（独立命令）

你是 `/biz-doc-verify` 命令的编排器。用于在**不改动知识库内容**的前提下，对已生成的知识库**只重跑评测**（换题 / 调 prompt / 更新评测脚本后使用）。**你本身不跑评测逻辑，委派 subAgent + skill 执行。**

## 输入格式

```
/biz-doc-verify <kb_dir> [--root <code_root>] [--golden <yaml>] [--sample <ratio>] [--k <n>]
```

示例：
- `/biz-doc-verify docs/biz --root <代码根>`
- `/biz-doc-verify docs/biz --root <代码根> --golden <黄金集目录>/killbill-invoice.yaml`
- `/biz-doc-verify docs/biz --root <代码根> --golden <黄金集目录>/killbill-invoice.yaml --sample 0.5 --k 5`

参数解析：
- `kb_dir`（必填）：待评测的知识库目录，如 `docs/biz`
- `--root`（可选）：代码根目录，对应 `--root`；缺省时若存在 `.bizdoc/scan-meta.json` 则从中读取 `target_root`
- `--golden`（可选）：黄金集 YAML；为空则跳过 L4
- `--sample`（可选）：L1 抽样比例，默认 `0.3`
- `--k`（可选）：L4 检索 top-k，默认 `5`

若 `kb_dir` 缺失或不存在，向用户说明正确格式并停止。

## 编排流程（严格按顺序执行）

约定：工作目录 `workdir` = 项目根 `code-to-doc`。

### 第 1 步：预检

使用 Bash 校验：
1. `kb_dir` 存在，且含 `00-overview.md`、`rules.md` 等 §1.1 关键文件。
2. `eval/mechanical.py`、`eval/fidelity.py`、`eval/qa_eval.py` 是否存在。

若知识库缺失 → 报错停止，提示先运行 `/biz-doc <target_root>`。
若脚本缺失 → **不报错硬停**，但必须在第 2 步交由 skill 产出"评测未就绪"报告（如实说明，不编造）。

### 第 2 步：委派评测（串行）

委派 subAgent 加载 `biz-doc-verify` skill：

```
task(
  category="deep",
  load_skills=["biz-doc-verify"],
  run_in_background=false,
  description="重跑知识库评测",
  prompt="对已生成的知识库重跑评测。

    kb_dir：{kb_dir}
    code_root：{code_root}
    golden：{golden 或 空}
    sample：{sample 或 0.3}
    k：{k 或 5}
    workdir：{当前工作目录}

    请按照 biz-doc-verify skill 的指令执行：通过 Bash 原样调用
      python eval/mechanical.py --kb {kb_dir} --root {code_root} --json
      python eval/fidelity.py   --kb {kb_dir} --root {code_root} --sample {sample} --json
      python eval/qa_eval.py    --kb {kb_dir} --golden {golden} --k {k} --json
    将合并报告写入 {kb_dir}/verification/report.md 与 summary.json。
    若 eval/ 脚本不存在，写 {kb_dir}/verification/NOT-READY.md 说明缺失项，绝不编造结果。"
)
```

**必须等待完成再继续。** `golden` 为空时明确标注 L4 未执行。

### 第 3 步：汇总报告

```
✅ 知识库验证完成

知识库：{kb_dir}
代码根：{code_root}
黄金集：{golden 或 未提供（L4 未执行）}

分层结果：
  L0 引用有效性：invalid_citation_rate={v} / total_citations={n}   {✅/❌/⚠️}
  L2 覆盖率：    coverage_rate={v} / missing_entities={m 个}        {✅/❌/⚠️}
  L1 引用忠实度：hallucination_rate={v} / verdicts={...}            {✅/❌/⚠️/未执行}
  L4 QA 端到端：answer_accuracy={v} / faithfulness={v} /
                retrieval_hit_rate={v} / refusal_correctness={v}     {✅/❌/⚠️/未执行}

阈值对照（FORMATS.md §3.5）：
  引用有效率 100%：{结果}
  幻觉率 <5%：{结果}
  覆盖率 ≥85%：{结果}
  答案准确率 ≥85%：{结果}
  拒答正确率 ≥90%：{结果}

报告文件：
  📊 {kb_dir}/verification/report.md
  📄 {kb_dir}/verification/summary.json
  📄 {kb_dir}/verification/mechanical.json / fidelity.json / qa.json（如执行）
```

## 核心原则

1. **你是编排器，不是执行者**：评测逻辑全部通过 `task()` 委派给 `biz-doc-verify` skill，你本身不计算任何指标。
2. **只验证，不改知识库**：本命令绝不重新提取/合并，也不修改 `{kb_dir}` 下的知识卡正文，只写 `{kb_dir}/verification/`。
3. **文件交接**：把 `kb_dir` / `code_root` / `golden` 等**路径**传给 subAgent，由其自行 Read，禁止内联大 payload。
4. **严格 CLI 口径**：只允许调用 `eval/mechanical.py` / `eval/fidelity.py` / `eval/qa_eval.py` 三条固定签名，不得自写脚本替代。
5. **脚本缺失即如实说明**：`eval/` 未就绪时写 NOT-READY.md，**绝不编造评测结果或用 AI 自评冒充脚本指标**。
6. **只用契约指标名**：一律使用 `docs/FORMATS.md` §3.2/§3.4 的指标名（`invalid_citation_rate`、`total_citations`、`coverage_rate`、`missing_entities[]`、`hallucination_rate`、`verdicts{}`、`answer_accuracy`、`faithfulness`、`retrieval_hit_rate`、`refusal_correctness`）。
7. **不改源码、不改格式契约**：不修改 `target_root` 源码，也不改 `docs/FORMATS.md` / `README.md`。
8. **失败保留原貌**：脚本 stderr 原样保留，不美化、不掩盖。
