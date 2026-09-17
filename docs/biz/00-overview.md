# 业务知识库总览

本知识库由代码逆向生成，覆盖目标代码根 `scenarios/synthetic-springboot`（Java / Spring Boot，包根 `com.acme.mall`）。业务域为「电商订单 / 计价 / 会员 / 优惠 / 售后」。

## 代码规模

- 模块：8（app, common, coupon, loyalty, order, pricing, refund, shipping）
- 类/接口：18，枚举：3，公开方法：65，HTTP 端点：3，数据库实体（表）：3
- 状态型枚举：1（`OrderState`）

## 业务能力清单（按模块）

### app — 应用入口
- 启用方法级安全，使 `@PreAuthorize` 生效（ROLE-001）。

### common — 金额基础设施
- 金额归一化为两位小数、四舍五入（BR-001）。
- 最低可收取金额 0.01 元，不接受零元/负价订单（BR-002）。

### coupon — 优惠券
- 券类型：满减 / 折扣 / 现金（TERM-002~005，ENT-001）。
- 单券抵扣计算（BR-003 满减、BR-004 折扣、BR-005 现金）。
- 可用性过滤：冻结、过期、`expireAt` 为空均不可用（BR-006）。
- 一单一券，取抵扣最多者（BR-007）。
- 券与会员折扣互斥取向（BR-008）；其叠加口径存疑（BR-009）。

### loyalty — 会员
- 用户分层 NORMAL / SILVER / GOLD / PLATINUM（TERM-006，TERM-007）。
- 会员属性与关系（ENT-002）。
- 活跃会员口径：启用且 365 天内有下单（BR-010）。
- 累计消费/最近下单时间更新规则缺失（BR-011）。

### order — 订单
- 订单状态七态（TERM-008，ENT-003，SM-001）。
- 状态流转守卫（BR-015）、支付超时 30 分钟（BR-012）、已支付不可直接取消（BR-013）、退款仅限 SHIPPED/COMPLETED（BR-014）。
- 订单履约流程（WF-001）。
- 实付金额赋值规则缺失（BR-016）。

### pricing — 计价/试算
- 会员分层折扣率（BR-017）、活动商品不折扣（BR-018）。
- 试算顺序：净额 → 券 → 运费 → 应付（BR-019），试算流程（WF-002）。
- 试算结果与入参（ENT-004，ENT-005）。

### refund — 售后
- 售后 7 天窗口（BR-020）、退款金额计算（BR-021）、退款触发退款中状态（BR-022）。
- 整单/部分由 `itemIds` 判定（BR-023）、退款须主管审批（BR-024）。
- 退款流程（WF-003）；审批后出款/完成衔接缺失（WF-004）；发起退款未解析订单（BR-025）。
- 权限：CS 发起（ROLE-002）、CS_LEAD 审批（ROLE-003）。

### shipping — 运费
- 基础运费 12 元、满 99 免邮、白金免邮（BR-026）、偏远地区加收 15 元（BR-027）。

## 关键业务对象关系（文字）

- 会员 `Member`（t_member）——分层决定结算系数（BR-017）与免邮（BR-026）；`Order.memberId` 逻辑引用会员（ENT-003）。
- 订单 `Order`（t_order）——状态机 SM-001；承载商品净额 `goodsAmt` 与运费 `shipFee`，用于退款金额计算（BR-021）。
- 优惠券 `Coupon`（t_coupon）——在试算中抵扣商品净额（BR-003~BR-009）。
- 试算 `Quote`——由 `PriceCalculator` 汇总三域（会员折扣、券、运费）产出（WF-002）。

## 置信度概览

- 🟢 confirmed：50 张（89.3%）
- 🟡 inferred：2 张（3.6%）
- 🔴 gap：4 张（7.1%）
- 合计：56 张

详见 [confidence-report.md](confidence-report.md)；待确认项见 [gaps.md](gaps.md) 与 [questions.md](questions.md)。
