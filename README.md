# code-to-doc

从已有项目代码**逆向生成业务知识库**的 opencode skill 套件。

产物是**业务知识**（领域概念 / 业务规则 / 流程 / 状态机 / 角色权限），
用于喂给 AI 助手做检索问答；**不是**技术文档（类图 / API 参考 / 部署架构）。

## 组成

| 路径 | 作用 |
|---|---|
| `.opencode/skills/biz-doc-scan/` | 机械盘点代码骨架（类/枚举/方法/权限注解/端点），零业务解释 |
| `.opencode/skills/biz-doc-extract/` | 逐模块抽取业务知识卡，**引用优先**（`file:line`），三级置信度 |
| `.opencode/skills/biz-doc-synthesize/` | 跨模块去重/消歧/合并，落盘为契约规定的知识库结构 |
| `.opencode/skills/biz-doc-verify/` | 调用 `eval/` 跑 L0/L1/L2/L4 评测并出报告 |
| `.opencode/skills/biz-doc-eval/` | 评测口径 + **盲化黄金集**构建规范 |
| `.opencode/commands/biz-doc.md` | 编排命令（scan → extract → synthesize → verify） |
| `.opencode/commands/biz-doc-verify.md` | 只重跑验证 |
| `eval/` | 评测工具链 —— `biz-doc-verify` 的执行引擎，**不是可选装饰** |
| `docs/FORMATS.md` | 格式契约：卡片语法 / 黄金集 schema / 评测接口 |

## 安装

**项目级（推荐）** —— 把 `.opencode/`、`eval/`、`docs/FORMATS.md` 放到目标项目根：

```bash
cp -r .opencode eval docs/FORMATS.md /path/to/your-project/
cd /path/to/your-project
```

**全局** —— 把 skill 与命令复制到 opencode 全局目录：

```bash
cp -r .opencode/skills/*   ~/.config/opencode/skills/
cp    .opencode/commands/*.md ~/.config/opencode/commands/
```

> 全局安装时仍需把 `eval/` 与 `docs/FORMATS.md` 放在**项目根**：skill 里的路径按项目根解析。

## 依赖

```bash
python -m pip install -r eval/requirements.txt   # 仅 PyYAML
```

## 使用

在项目根启动 opencode：

```
/biz-doc <代码根目录> [--out docs/biz] [--modules a,b] [--golden x.yaml] [--sample 0.3] [--k 5] [--skip-verify]
/biz-doc-verify docs/biz --root <代码根> --golden <yaml>
```

也可以直接跑评测脚本：

```bash
python eval/mechanical.py --kb docs/biz --root <代码根> --scope mod1,mod2 --json   # L0 引用有效性 + L2 覆盖率（无需 LLM）
python eval/fidelity.py   --kb docs/biz --root <代码根> --sample 0.3 --json        # L1 引用忠实度
python eval/qa_eval.py    --kb docs/biz --golden <yaml> --k 12 --rerank-pool 50 --refine --judge-repeats 3 --write-report  # L4 端到端
```

## LLM 配置

```
LLM_PROVIDER = deepseek | openai | none   (默认 deepseek)
LLM_API_KEY  = ...
LLM_BASE_URL = https://api.deepseek.com
LLM_MODEL    = deepseek-chat
LLM_ANSWER_MODEL = ...   # 可选：作答单独用更强的模型，判分仍用 LLM_MODEL
```

`LLM_PROVIDER=none` 时只跑不依赖 LLM 的检查（L0/L2 与检索）。

## 设计要点

- **引用优先**：每条规则带 `file:line` 溯源；无溯源的条目不得标 🟢。
- **三级置信度**：🟢 confirmed / 🟡 inferred / 🔴 gap，绝不二元化。
- **盲化黄金集**：出题者不得读取生成的知识库，答案必须来自独立信源，否则指标自证循环。
- **负样本 20%~30%**：测拒答与幻觉。
- **同义词必填**：用户说「会员」、代码里叫 `Member`/`vipLvl`，不建同义词检索必挂。

## 格式契约

卡片语法、知识库文件清单、黄金集 schema、评测指标与 CLI 签名，全部以
[`docs/FORMATS.md`](docs/FORMATS.md) 为准。
