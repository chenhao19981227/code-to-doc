# eval/ — 评测工具链

对生成的知识库（KB）做分层评测。**所有脚本的接口、指标名、判定口径以
[`docs/FORMATS.md`](../docs/FORMATS.md) §3 为唯一契约。** 本 README 只解释用法与口径实现。

## 依赖

仅 Python 3（3.10+）标准库 + **PyYAML**（黄金集解析）。BM25 与 LLM 传输均为手写/标准库实现，
不依赖 `requests` / `numpy` / `rank_bm25`。

```bash
python -m pip install -r eval/requirements.txt
```

## 目录

| 文件 | 作用 |
|---|---|
| `llm.py` | 共享 LLM 客户端（OpenAI 兼容 `/chat/completions`，`urllib` 实现） |
| `retrieval.py` | 卡片/溯源解析 + 手写 BM25 检索器（可单独跑查询） |
| `mechanical.py` | **L0** 引用有效性 + **L2** 覆盖率（无需 LLM） |
| `fidelity.py` | **L1** 引用忠实度（LLM judge，抽样） |
| `qa_eval.py` | **L4** 端到端问答（检索 → 回答 → 判分） |
| `requirements.txt` | 依赖 |

## 快速开始

```bash
# L0 + L2（无需 LLM）
python eval/mechanical.py --kb docs/biz --root benchmark/killbill --json

# L1 忠实度（抽样 30%，需要 LLM）
python eval/fidelity.py --kb docs/biz --root benchmark/killbill --sample 0.3 --json

# L4 端到端问答（需要 LLM 与黄金集）
python eval/qa_eval.py --kb docs/biz --golden benchmark/golden-set/killbill-invoice.yaml --k 5 --json

# 检索器单独调试
python eval/retrieval.py --kb docs/biz "发票什么时候生成" --k 5
```

每个脚本都支持 `--write-report`，会把该层的 markdown 报告写到 `<kb>/verification/`：

| 脚本 | 报告文件 |
|---|---|
| `mechanical.py` | `verification/L0-L2-mechanical.md` |
| `fidelity.py` | `verification/L1-fidelity.md` |
| `qa_eval.py` | `verification/L4-qa.md` |

**退出码**：正常完成一律 `0`（即使指标不达标、KB 为空、黄金集缺失——此时会 `skipped: true`
并打印明确信息）。参数错误返回 `2`。

## LLM 配置（FORMATS.md §3.1）

环境变量：

| 变量 | 取值 | 默认 |
|---|---|---|
| `LLM_PROVIDER` | `deepseek` \| `openai` \| `none` | `deepseek` |
| `LLM_API_KEY` | API Key | — |
| `LLM_BASE_URL` | OpenAI 兼容 base URL | `https://api.deepseek.com` / `https://api.openai.com/v1` |
| `LLM_MODEL` | 模型名 | `deepseek-chat` / `gpt-4o-mini` |

```powershell
$env:LLM_PROVIDER = "deepseek"
$env:LLM_API_KEY  = "sk-..."
$env:LLM_MODEL    = "deepseek-chat"
python eval/fidelity.py --kb docs/biz --root benchmark/killbill --sample 0.3 --json
```

`LLM_PROVIDER=none`（或未设置 key）时：

* `mechanical.py` 与 `retrieval.py` 完全可用；
* `fidelity.py`、`qa_eval.py` 会**跳过** LLM 层，输出 `skipped: true` 与原因，退出码仍为 `0`。

> `llm.py` **导入时不发起任何网络请求**；只有真正调用 `chat()` 才会联网。

## 指标口径

### L0 引用有效性（`mechanical.py`）

对每张卡 `溯源` 里的每个 `path:起行-止行`（也接受单行 `path:line`，相对 `--root` 解析）：

1. 文件存在；
2. `1 ≤ 起行 ≤ 止行 ≤ 文件行数`；
3. 被引行区间内**至少有一行非空、非纯注释**。

| 指标 | 定义 |
|---|---|
| `total_citations` | 解析出的引用总数 |
| `invalid_citation_rate` | 无效引用 / 总数（无引用时为 `0.0`） |

无效明细见 `invalid_citations[]`，`reason` ∈ `file_not_found` / `unreadable` / `invalid_range` /
`line_out_of_range` / `comment_only_or_blank`。

### L2 覆盖率（`mechanical.py`）

机械盘点 `--root` 下 **Java 源码**（跳过 `target`/`build`/`out`/`.git`/`.idea`/`.gradle`/
`node_modules`/`test`/`tests`）：

> **范围对齐**：可选参数 `--scope <p1,p2>`（逗号分隔、相对 `--root` 的路径前缀）限定盘点范围。
> 只提取了部分模块时**必须**传，否则覆盖率分母是整仓实体、指标失真（如 2/16 模块时只有 1%）。
> 不传时盘点整个 `--root`。

* 类声明：`public class` / `interface` / `enum` / `record` / `@interface`；
* 公开方法：显式 `public` 方法（按花括号配对确定方法体范围；构造函数不计）；
* 权限注解：`@PreAuthorize` / `@PostAuthorize` / `@RolesAllowed` / `@Secured` / `@PermitAll` / `@DenyAll`。

实体行范围用花括号配对（忽略字符串 / 字符 / 注释 / 文本块中的花括号）。

| 指标 | 定义 |
|---|---|
| `coverage_rate` | 被至少一张卡「溯源」命中的实体 / 实体总数（无实体时 `0.0`） |
| `missing_entities[]` | 未被任何引用命中的实体清单 |

命中判定：某条引用的文件路径（POSIX 规范化后）与实体文件相同，且行区间与实体行范围**有交集**；
对带模块前缀的引用额外做后缀匹配。以上为**确定性、已文档化**的启发式。

### L1 引用忠实度（`fidelity.py`）

候选 = 置信度为 🟢 `confirmed` / 🟡 `inferred` 且**带引用**的卡片。按 `--sample` 比例
（确定性随机，seed 固定）抽样，把「卡片断言正文 + 被引源码行」交给 judge 独立回读，判定
`supported` / `contradicted` / `unclear`。

| 指标 | 定义 |
|---|---|
| `hallucination_rate` | `contradicted / 抽样数`（抽样为 0 时为 `null`） |
| `verdicts{}` | `supported` / `contradicted` / `unclear` 计数 |

逐条判定与理由见 `details[]`。

### L4 端到端问答（`qa_eval.py`）

读取黄金集 YAML，对每题：BM25 取 top-k → **只用检索片段**构造 prompt → LLM 回答 → judge 判分。

* positive 题：`expected_answer` 对比，判 `correct` / `partial` / `wrong`；
* negative 题：判 `refused` / `hallucinated` / `other`；
* 另判 answer 是否**完全由检索片段支撑**（faithfulness yes/no）。

| 指标 | 定义 |
|---|---|
| `answer_accuracy` | `correct / positive 题数`（严格；无 positive 时为 `null`） |
| `faithfulness` | 判定为「完全被支撑」的答案 / 已判定答案数 |
| `retrieval_hit_rate` | `answer_source` 命中 top-k 的 positive 题 / positive 题数 |
| `refusal_correctness` | `refused / negative 题数`（无 negative 时为 `null`） |

附带 `answer_score_weighted`（`correct + 0.5×partial` / positive 题数）、`verdicts{}`、`counts{}`。

**检索命中判定是启发式**：`answer_source` 是独立信源（FORMATS.md §2.3），而检索结果来自生成的
KB 卡片，两者无法机械一一对应。实现为：

* `answer_source` 以 `kb:<path>` 开头时，与片段的 `source_path` 精确/后缀匹配；
* 否则取 `answer_source` 中长度 ≥4 的显著 token（去掉 `docs:`/`code:` 等前缀与停用词），
  命中 top-k 任一片段的 `source_path`/`title`/`text` 即算命中；
* `answer_source` 为空时回退用该题的 `module`。

需要更精确时可让黄金集使用 `kb:` 前缀。

## 检索实现

* 检索单元 = `^## ` 切分的二级标题块（`docs/FORMATS.md` §1.2）；`verification/` 目录被排除。
  文件若完全没有 `## ` 块，则整文件作为一个片段（标题取首个 `# ` 或文件名）。
* 分词：拉丁/数字串（≥2 字符）+ CJK 单字与二元组（bigram）。
* 评分：Okapi BM25，`k1=1.5`、`b=0.75`。

返回结构：`{chunk_id, title, text, score, source_path}`，`chunk_id = "<相对路径>#<块序号>"`。

## 健壮性

* 卡片/引用格式错误**不崩溃**：记录到 `warnings[]` 并跳过，脚本继续。
* KB / 源码根 / 黄金集缺失或为空：打印明确提示，输出空指标，退出码 `0`。
* 输出使用 UTF-8（脚本启动时重配置 stdout），中文与 emoji 不炸码。

## 空目录冒烟测试

```powershell
python eval/retrieval.py --kb docs\biz --k 3 "test"
python eval/mechanical.py --kb docs\biz --root benchmark\killbill --json
$env:LLM_PROVIDER="none"; python eval/fidelity.py --kb docs\biz --root benchmark\killbill --sample 0.3 --json
python eval/qa_eval.py --kb docs\biz --golden benchmark\golden-set\none.yaml --k 5 --json
```
