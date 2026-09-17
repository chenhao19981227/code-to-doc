# code-to-doc

从已有项目代码**逆向生成业务知识库**，作为 AI 助手的检索输入。

> 注意：产物是**业务知识库**（领域概念 / 业务规则 / 流程 / 角色权限），
> 不是技术文档（类图 / API 参考 / 部署架构）。

## 为什么

老系统没有文档 → AI 助手没有知识可检索 → 答不好用户问题。
本项目从代码反向提取「业务语言」的知识库，喂给助手。
验证标准不是「文档好不好看」，而是**端到端问答准确率**。

## 组成

| 目录 | 作用 |
|---|---|
| `.opencode/` | skill 套件 + 编排命令（scan → extract → synthesize → verify） |
| `eval/` | 评测工具链：L0 引用有效性 / L1 忠实度 / L2 覆盖率 / L4 QA 端到端 |
| `benchmark/` | 验证基准：Kill Bill 源码 + 官方文档（当标准答案）+ 黄金集 |
| `scenarios/` | 自建合成模块，业务规则已知，用于快速迭代 |
| `docs/biz/` | 生成的知识库输出位置 |
| `docs/FORMATS.md` | **格式契约**（所有实现必须遵守） |

## 快速开始

```powershell
git clone https://github.com/chenhao19981227/code-to-doc.git
cd code-to-doc

# 依赖（仅 PyYAML；BM25 与 LLM 传输均为标准库手写实现）
python -m pip install -r eval/requirements.txt

# 拉取基准：Kill Bill 源码 + 官方文档（~164 MB 浅克隆；仓库【不】包含它们）
pwsh -File scripts/clone-benchmark.ps1 -NoProxy        # 可直连时
pwsh -File scripts/clone-benchmark.ps1 -Proxy http://127.0.0.1:7897   # 需走本地代理时（默认值）
```

LLM 评测（L1/L4）需要密钥；L0/L2 与检索不需要：

```powershell
$env:LLM_PROVIDER = "deepseek"
$env:LLM_API_KEY  = "<your key>"
```

## 使用

在**本项目根目录**下启动 opencode，然后：

```
/biz-doc scenarios/synthetic-springboot     # 生成业务知识库
/biz-doc-verify docs/biz                    # 重跑验证（换题/调 prompt 后）
```

命令行直跑评测：

```bash
python eval/mechanical.py --kb docs/biz --root <代码根> --json
python eval/fidelity.py   --kb docs/biz --root <代码根> --sample 0.3 --json
python eval/qa_eval.py    --kb docs/biz --golden benchmark/golden-set/<x>.yaml --k 5 --json
```

## 验证路线

```
① 合成场景（ground truth 100% 确定）→ 打通链路、调 prompt
        ↓
② Kill Bill 单模块 → 用官方文档当答案、测试/Issue 当考题 → 校准真实指标
        ↓
③ 目标老系统 → 合成问题 + 后续真实用户问题
```

成功阈值见 `docs/FORMATS.md` §3.5。

## 设计要点（踩坑备忘）

- **盲化出题**：出题者不得读取生成的知识库，否则指标自证循环、毫无意义。
- **异源出题**：问题从官方文档 / 测试 / Issue 合成，不从生成的知识库。
- **引用优先**：每条规则带 `[file:line]`，无引用不得标 🟢。
- **负样本**：20%~30% 的问题应「答不上来」，用来测拒答与幻觉。
- **同义词必填**：用户说「会员」、代码里叫 `Member`/`vip_user`，不建同义词检索必挂。

## 状态

- [x] 目录骨架 + 格式契约（`docs/FORMATS.md`）
- [x] skill 套件（scan / extract / synthesize / verify / eval + 2 命令）
- [x] 评测工具链（`eval/`：L0/L1/L2/L4，纯标准库 + PyYAML）
- [x] 合成场景 + ground truth（19 个 Java 文件，104 条引用 0 失效）
- [x] Kill Bill 基准（浅克隆源码 + 官方 `.adoc` 文档）
- [x] 两份盲化黄金集（合成 32 题 / Kill Bill 40 题）
- [x] 端到端跑通（合成场景）

## 首次评测结果（合成场景，详见 `docs/biz/verification/report.md`）

| 指标 | 结果 | 目标 | 判定 |
|---|---|---|---|
| L1 幻觉率 | 0.0% | < 5% | ✅ |
| L4 答案准确率 | 87.5% | ≥ 85% | ✅ |
| L4 拒答正确率 | 100%（8/8，0 幻觉） | ≥ 90% | ✅ |
| L4 忠实度 / 检索命中 | 100% / 100% | — | ✅ |
| L0 引用有效率 | 97.8% | 100% | ❌ |
| L2 覆盖率 | 53.1% | ≥ 85% | ❌ |

**核心目标（答准 / 不编 / 会拒答）已达标；L0、L2 为待修的工程项，见报告第 5 节。**

## 已知问题

1. L0：2 张卡引到纯注释行 → extract 需增加「引用行必须是代码」自检。
2. L2：业务卡只覆盖规则所在行，58 个 public 方法仅 21 个被引用 → 建议 synthesize 为每个类生成「模块实体卡」覆盖整类区间，或调整 L2 口径。
3. 解析噪声：`00-overview.md` 的非卡片 `##` 小节被校验并报 `missing required field` → 解析器应跳过无 `类型` 字段的小节。
4. KB-Q020 / KB-Q021 答错 → 复核检索片段充分性。

## Kill Bill 实跑结果（真实规模）

| 指标 | v1 浅提取<br>(2 模块/172 卡) | v2 深提取<br>(5 模块/675 卡) | v2+检索去重 | 目标 |
|---|---|---|---|---|
| L0 引用有效率 | 100.0% | **100.0%**（1204 条） | 100.0% | 100% ✅ |
| L1 幻觉率 | 0.0% | **0.0%** | 0.0% | <5% ✅ |
| L2 覆盖率（范围对齐后） | 7.9% | 13.7% | 13.7% | ≥85% ❌ |
| **L4 答案准确率** | 9.7% | 29%–32% | **41.9%** | ≥85% ❌ |
| L4 准+部分（加权） | ~19% | ~45% | **53.2%** | — |
| L4 检索命中率 | 67.7% | 87.1% | 87.1% | — |
| L4 忠实度 / 拒答正确率 | 100% / 100% | 100% / 100% | 100% / **100%** | — / ≥90% ✅ |

**自主优化链（Kill Bill）**：9.7% → ~30%（深提取）→ 41.9%（检索去重）→ 48.4%（k=20）
→ 61.3%（作答 prompt 强化）→ 64.5%（LLM rerank）→ 71.0%（refine 自省补全），净提升 **7.3×**。

**可信基线（85 题 + 3 次判分）**：

| 子集 | 准确率 | 加权 | 拒答 |
|---|---|---|---|
| 原 40 题（较易） | 67.7% | 80.6% | 100.0% |
| 新 45 题（加难） | 39.4% | 59.1% | 91.7% |
| **全部 85 题** | **53.1%** | **69.5%** | 95.2% |

注：上表 71.0% 是**较易 40 题上的单次跑分**；扩到 85 题并 3 次判分后，可信数字为 **53.1%**。
`faithfulness=100%`、`retrieval_hit_rate=92.2%`、L1 幻觉 0%、L0 引用 0% 无效。

**细节补全实验（KB v3，1111 卡）**：补出 222 张细节卡后准确率 53.1% → **56.2%（+3.1pt）**，
但 **faithfulness 100% → 98.8%（破红线）**、拒答 95.2% → 90.5%、检索命中 92.2% → 89.1%。
**结论：+3.1pt 是用安全裕度换来的，故保留 v2（`docs/biz-kb2`）为发布版本**，v3（`docs/biz-kb3`）作为高覆盖/低裕度备选。
判断依据与停止优化的理由见 [`docs/OPTIMIZATION-RESULTS.md`](docs/OPTIMIZATION-RESULTS.md) §7–§8。


**平台期诊断**：检索命中已 92%（召回饱和）；`wrong & facts-absent = 0`（事实都在库里）；
失败集中于**多事实组合题**（需跨 2~3 张卡合成）。剩余差距需高成本路径（重提取提高细节密度）。
完整分析与路径对比见 [`docs/OPTIMIZATION-RESULTS.md`](docs/OPTIMIZATION-RESULTS.md)；
原始计划见 [`docs/NEXT-STEPS.md`](docs/NEXT-STEPS.md)。



详见 `docs/biz-kb2/verification/report.md`（v2）与 `docs/biz-killbill/verification/report.md`（v1）。



