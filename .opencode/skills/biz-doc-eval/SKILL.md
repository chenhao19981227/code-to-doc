---
name: biz-doc-eval
description: 说明业务知识库评测体系 L0引用有效性 / L1引用忠实度 / L2覆盖率 / L4 QA端到端 的口径与调用方式，以及如何构建「盲化 + 异源」黄金集（防自证循环）。不直接面向用户，供 biz-doc / biz-doc-verify command 的 subAgent 调用。
---

# Biz Doc Eval - 评测体系与黄金集构建 Skill

本 skill 只做一件事：**解释 `eval/` 评测工具链（L0/L1/L2/L4）的口径、调用方式与成功阈值，并说明如何构建合格的盲化黄金集。** 它本身不实现评测脚本、不跑评测（跑评测由 `biz-doc-verify` 负责）。

## 输入

调用方（subAgent）会提供：
- `kb_dir`：知识库目录（默认 `docs/biz`）
- `code_root`：代码根目录
- `golden`：黄金集 YAML 路径（可为空）
- `workdir`：工作目录（= 项目根 `code-to-doc`）

## 执行步骤

### 1. 分层总览（FORMATS.md §3.2）

| 层 | 脚本 | 需要 LLM | 主要指标 |
|---|---|---|---|
| L0 引用有效性 | `eval/mechanical.py` | 否 | `invalid_citation_rate`, `total_citations` |
| L2 覆盖率 | `eval/mechanical.py` | 否 | `coverage_rate`, `missing_entities[]` |
| L1 引用忠实度 | `eval/fidelity.py` | 是 | `hallucination_rate`, `verdicts{}` |
| L4 QA 端到端 | `eval/qa_eval.py` | 是 | `answer_accuracy`, `faithfulness`, `retrieval_hit_rate`, `refusal_correctness` |

### 2. 各层口径（FORMATS.md §3.4，照抄，不得改写）

- **L0 引用有效性**：`[file:line]` 指向的文件存在、行号在范围内、且该行非空、非纯注释。
- **L1 忠实度**：judge 独立回读被引代码，判定 `supported` / `contradicted` / `unclear`；`hallucination_rate = contradicted / 抽样总数`。
- **L2 覆盖率**：先机械抽取代码实体清单（类 / 枚举 / 公开方法 / 权限注解），统计被至少一张卡「溯源」引用的比例。
- **L4 答案准确率**：judge 对比 `expected_answer` 与模型答案，判定 `correct` / `partial` / `wrong`。
- **L4 答案忠实度**：模型答案是否完全由检索到的 KB 片段支撑（无外部知识/编造）。
- **L4 检索命中率**：`answer_source` 对应的文件是否出现在 top-k 检索结果中。
- **L4 拒答正确率**：negative 题中，模型是否表达「不确定 / 未覆盖」。

### 3. 调用签名（FORMATS.md §3.3）

```bash
# L0 + L2（无需 LLM）
python eval/mechanical.py --kb docs/biz --root <代码根> --json

# L1 忠实度（抽样）
python eval/fidelity.py --kb docs/biz --root <代码根> --sample 0.3 --json

# L4 端到端问答
python eval/qa_eval.py --kb docs/biz --golden <黄金集目录>/killbill-invoice.yaml --k 5 --json
```

LLM 配置（环境变量，FORMATS.md §3.1）：

```
LLM_PROVIDER = deepseek | openai | none    (默认 deepseek)
LLM_API_KEY  = ...
LLM_BASE_URL = https://api.deepseek.com    (默认)
LLM_MODEL    = deepseek-chat               (默认)
```

`LLM_PROVIDER=none` 时只跑不依赖 LLM 的检查（L0、检索）。

### 4. 成功阈值（FORMATS.md §3.5）

| 指标 | 目标 |
|---|---|
| 引用有效率 | 100% |
| 幻觉率 | < 5% |
| 覆盖率 | ≥ 85% |
| 答案准确率 | ≥ 85% |
| 拒答正确率 | ≥ 90% |

### 5. 黄金集格式（FORMATS.md §2）

位置：`<黄金集目录>/<project>-<module>.yaml`

```yaml
meta:
  project: killbill
  module: invoice
  domain: subscription-billing
  created_by: synthetic        # synthetic | manual
  blinded: true                # 出题者是否对生成的知识库盲化（必须 true）
  version: 1
  notes: ""

questions:
  - id: KB-Q001
    question: "发票什么时候生成？"
    type: positive             # positive=可答 | negative=应拒答
    difficulty: medium         # easy | medium | hard
    module: invoice
    expected_answer: "……"
    answer_source: "docs:userguide_invoice.md"    # 独立信源，不得来自生成的知识库
    synonyms: ["发票生成时间", "invoice generation timing"]
    notes: ""

  - id: KB-N001
    question: "系统支持加密货币支付吗？"
    type: negative
    expected_behavior: refuse  # 助手应表达「不确定 / 未覆盖」
    module: payment
    notes: "系统未覆盖"
```

### 6. 构建盲化黄金集——硬性规则（FORMATS.md §2 硬性规则）

1. **盲化**：出题者不得读取生成的知识库（`meta.blinded` 必须为 `true`）。
2. **答案独立**：`expected_answer` 必须来自官方文档 / 源码 / 测试，不得来自生成的知识库。
3. **负样本比例 20%~30%**：`type: negative` 用于检测幻觉与拒答能力。
4. 每题必须可追溯到 `answer_source`。

### 7. 构建流程（防自证循环）

1. **选信源**：官方文档、源码 itself、测试、Issue（如 `<官方文档目录>/`、`<代码根>/**/src/test`）。**绝不打开 `kb_dir`。**
2. **出题**：按模块合成问题，写 `expected_answer` 并绑定 `answer_source`。
3. **正负配比**：positive 占 70%~80%，negative 占 20%~30%；negative 的 `expected_behavior: refuse`。
4. **难度分布**：标注 `easy` / `medium` / `hard`。
5. **自查**：逐题确认「答案不依赖生成的知识库」「`answer_source` 真实存在」；在 `meta.notes` 记录信源版本。
6. **冻结**：`meta.version` 递增，后续调 prompt 不得改题（改了要新建版本，避免指标漂移）。

### 8. 产出与交接

- 本 skill 的产出是**说明与清单**，通常不直接落盘。
- 若调用方要求生成黄金集骨架：在 `<黄金集目录>/<project>-<module>.yaml` 写出符合 §2 格式的文件，`meta.blinded: true`，题目必须来自独立信源。
- 生成的黄金集路径作为后续 `biz-doc-verify` 的 `golden` 输入（**文件路径交接**，不内联内容）。

## 输出格式

- **主产出（无落盘）**：被测知识库 `kb_dir`、代码根 `code_root`、黄金集 `golden` 的路径清单，供 `biz-doc-verify` 调用。
- **可选落盘**：`<黄金集目录>/<project>-<module>.yaml`，格式严格照 `docs/FORMATS.md` §2（`meta` 含 `project/module/domain/created_by/blinded/version/notes`；`questions[]` 含 `id/question/type/difficulty/module/expected_answer/answer_source/synonyms/notes`）。
- **口径清单**：L0/L1/L2/L4 的脚本、LLM 依赖、指标名，以及 §3.5 成功阈值，按本 skill §1~§4 表格原样引用。
- 任何情况下都不产出评测指标数值——数值只能来自 `eval/` 脚本的真实运行。

## 约束

- **不得读取生成的知识库来出题**（盲化是评测有效性的前提）。
- **不得实现评测脚本**：`eval/` 由独立模块负责，本 skill 只引用其 CLI 与口径。
- **不得发明指标名**：一律使用 FORMATS.md §3.2/§3.4 的原始指标名。
- **不改动 `docs/FORMATS.md` / `README.md`**；不修改源码。
- 一切写作仅限 `<黄金集目录>/` 与 `.bizdoc/`。
