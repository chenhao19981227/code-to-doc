# 合成场景（Synthetic Scenarios）

本目录存放**自建的最小合成模块**，用于在真实大系统（Kill Bill）之前快速迭代 `code-to-doc` 的 scan → extract → synthesize → verify 链路。

## 为什么需要合成场景

真实项目里，「业务规则应该是什么」往往无人能完整说清——没有稳定标准答案，就很难判断 tool 提取得好不好。
合成场景由**我们自己编写业务规则**，因此 ground truth 100% 已知，可以：

- 快速定位 prompt / skill 的提取缺陷（漏规则、幻觉、引用错位）；
- 用确定的期望输出做 diff，而不是靠人工感觉；
- 在不污染真实 benchmark 的前提下反复试错。

## 场景清单

| 场景 | 领域 | 规模 | 说明 |
|---|---|---|---|
| `synthetic-springboot/` | 电商中台（会员/定价/优惠券/运费/订单/退款/权限） | 19 个 Java 文件、约 30 条业务知识 | 覆盖数值型定价、免运费门槛、券叠加互斥、退款窗口与部分退款、状态机、角色权限，以及 3 条隐藏规则 |

## synthetic-springboot 结构

```
synthetic-springboot/
├── src/main/java/com/acme/mall/
│   ├── MallApplication.java              # 开启方法级安全
│   ├── common/AmountUtils.java           # 隐藏规则：金额取整 + 最低 0.01 元
│   ├── loyalty/                          # 会员等级、会员实体、活跃会员 SQL（隐藏规则）
│   ├── pricing/                          # 分层折扣、试算编排、Controller、DTO
│   ├── coupon/                           # 券类型、券实体、选券与互斥（隐藏规则）
│   ├── shipping/                         # 运费与免运费门槛、偏远附加费
│   ├── order/                            # 订单状态枚举、订单实体、状态机、Repository
│   └── refund/                           # 退款窗口与金额、Controller（角色权限）
├── GROUND-TRUTH.md                       # 权威业务事实 + 精确 file:line
└── expected-cards.md                     # 按 FORMATS.md §1 卡片格式写好的期望知识卡
```

**注意**：源码仅作格式载体，**不需要、也不应**参与编译（无 Maven/Gradle 构建）。请勿为其添加构建脚本或依赖。

## Ground truth 的可信度

- `GROUND-TRUTH.md` 由出题者手写，独立于任何 tool 生成的知识库（满足盲化前提）。
- 每条规则都给出实现的精确 `file:line`，且行号已对照写入后的源码逐行复核。
- 代码标识符**故意不等于**业务术语（如 `vipLvl` = 会员等级、`shippingFee` = 运费、`usableFlag` = 券可用标志），用于检验同义词检索能力；映射表见 `GROUND-TRUTH.md` §1。

## 如何校验行号

`GROUND-TRUTH.md` 中所有引用均为相对本场景根目录的路径。复核方式示例：

```powershell
# 查看某规则对应源码片段（行号前缀即实际行号）
Get-Content -LiteralPath "scenarios\synthetic-springboot\src\main\java\com\acme\mall\coupon\CouponService.java" | Select-Object -Skip 27 -First 6
```

## 如何使用

```bash
# 1) 生成知识库（在项目根目录执行）
/biz-doc scenarios/synthetic-springboot

# 2) 校验引用有效性 + 覆盖率
python eval/mechanical.py --kb docs/biz --root scenarios/synthetic-springboot --json

# 3) 对照期望卡片做 diff（人工或脚本）
#    生成产物的卡片 vs scenarios/synthetic-springboot/expected-cards.md
```

## 隐藏规则（检验提取深度）

| ID | 规则 | 隐藏方式 |
|---|---|---|
| BR-006 | 券与会员折扣互斥、取更优者 | 类名 `CouponService` 看不出与会员折扣的关系 |
| BR-012 | 最低收取 0.01 元 | 埋在通用工具 `AmountUtils` |
| BR-013 | 活跃会员 = 近 365 天有下单 | 阈值写在原生 SQL 字符串里 |
