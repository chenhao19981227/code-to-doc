# 业务规则 (rules)

本文件收录可判定的业务规则卡（条件 → 结果、阈值、计算公式、校验/异常分支）。检索单元为每个 `## BR-xxx` 二级标题块。

## BR-001 金额归一化：四舍五入保留两位小数

- **类型**: 业务规则
- **同义词**: 保留两位小数, 两位小数, 四舍五入, 金额取整, 金额精度, HALF_UP, rounding, 金额归一
- **模块**: common
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/common/AmountUtils.java:20-25`

**规则**：`normalize(raw)` 使用 `raw.setScale(2, RoundingMode.HALF_UP)` 将金额保留两位小数、四舍五入。
**例外**：当 `raw` 为 `null` 时返回 `BigDecimal.ZERO.setScale(2, HALF_UP)`（即 0.00）。

## BR-002 最低可收取金额 0.01 元

- **类型**: 业务规则
- **同义词**: 最低收款, 最小金额, 最低金额, 0.01, 不接受零元订单, 不接受负价订单, minimum charge, MIN_CHARGE, chargeable
- **模块**: common
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/common/AmountUtils.java:11-12`, `src/main/java/com/acme/mall/common/AmountUtils.java:30-36`

**规则**：`chargeable(amount)` 先归一化金额；若结果小于 `MIN_CHARGE`（0.01 元），则返回 0.01。系统不接受零元或负价订单。
**例外**：该下限作用于最终可收取金额（试算中的应付金额 payableAmt），见 pricing 模块。

## BR-003 满减券：达到门槛才抵扣面额

- **类型**: 业务规则
- **同义词**: 满减规则, 满减门槛, 门槛判断, 满减计算, full-reduction rule, threshold reached
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponService.java:43-44`

**规则**：`FULL_REDUCTION` 券：当 `netAmount >= threshold` 时抵扣 `faceValue`，否则抵扣 `0`。

## BR-004 折扣券：按 (1 − rateValue) 比例抵扣

- **类型**: 业务规则
- **同义词**: 折扣券规则, 折扣计算, 打折比例, 折扣抵扣, discount computation, discount rate rule
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponService.java:41-42`

**规则**：`DISCOUNT` 券抵扣额 = `normalize(netAmount × (1 − rateValue))`。例如 rateValue=0.88 时抵扣净额的 12%。

## BR-005 现金券：直接抵扣面额

- **类型**: 业务规则
- **同义词**: 现金券规则, 代金券抵扣, 无门槛抵扣, cash coupon rule, 固定抵扣
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponService.java:45-46`

**规则**：`CASH` 券抵扣额 = `faceValue`，不做门槛判断。

## BR-006 券可用性过滤：冻结或已过期不可用

- **类型**: 业务规则
- **同义词**: 券可用性, 券是否可用, 券过期, 冻结券, 可用券, coupon validity, usableFlag, expired coupon
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponService.java:19-22`

**规则**：遍历券时跳过满足任一条件的券：`!isUsableFlag()`（已冻结）、`expireAt == null`、或 `expireAt` 早于当前时刻（已过期）。
**例外**：`expireAt` 为空的券按不可用处理。

## BR-007 一单一券：只应用抵扣最多的一张

- **类型**: 业务规则
- **同义词**: 一单一券, 单券, 只用一张券, 最优券, one coupon per order, best coupon, 取最大抵扣
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponService.java:13-16`, `src/main/java/com/acme/mall/coupon/CouponService.java:17-27`

**规则**：`bestReduction` 在所有可用券中取 `reductionOf` 最大者作为本单券抵扣。注释明确「一张订单只会应用一张券」。

## BR-008 券与会员折扣互斥：取更划算者

- **类型**: 业务规则
- **同义词**: 券折扣不可叠加, 二选一, 取更优惠, coupon vs member discount, 互斥, 不可叠加
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponService.java:28-33`

**规则**：计算会员权益值 `memberBenefit = netAmount × (1 − memberRate)`；若 `memberBenefit >= best`（最佳券抵扣）则返回 `0`（不用券，保留会员折扣）；否则返回 `best`（用券）。
**例外**：此处的 `netAmount` 由调用方传入，见 BR-009 对其口径的存疑。

## BR-009 券与会员折扣是否叠加（实现口径存疑）

- **类型**: 业务规则
- **同义词**: 叠加口径, 券折扣叠加, 会员折扣是否保留, discount stacking, 注释与实现不一致
- **模块**: coupon
- **置信度**: 🟡 inferred
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponService.java:28-33`, `src/main/java/com/acme/mall/pricing/PriceCalculator.java:33-36`

**规则（待确认）**：代码注释（CouponService 第 28 行）称「券与会员折扣不可叠加：谁更划算就用谁，用券则牺牲会员折扣」。但调用方 `PriceCalculator.quote` 传入的 `netAmount` 已是会员折后金额（`DiscountService.apply` 的结果），用券时 `afterCoupon = goodsNet − couponCut` 并未回退会员折扣。即：注释所声明的「用券牺牲会员折扣」在实现中未体现，二者是否叠加存疑。
**缺失证据**：缺少对「会员折扣基数」与「券抵扣基数」应一致的显式约束或测试。详见 questions.md。

## BR-010 活跃会员口径：启用且 365 天内有下单

- **类型**: 业务规则
- **同义词**: 活跃会员, 活跃用户, 运营触达人群, 触达人群, 365天, 一年内有下单, active members, findActives, 活跃口径
- **模块**: loyalty
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/loyalty/MemberRepository.java:12-17`

**规则**：`findActives` 选取 `status = 1` 且 `last_order_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)` 的会员。注释「拉取当前需要纳入运营触达的人群。口径写在 SQL 内，勿改」。
**例外**：口径以原生 SQL 硬编码，任何变更需改 SQL。

## BR-011 会员累计消费与最近下单时间的更新规则缺失

- **类型**: 业务规则
- **同义词**: 累计消费更新, totalSpent, lastOrderAt, 最近下单时间, 会员字段更新
- **模块**: loyalty
- **置信度**: 🔴 gap
- **溯源**: `src/main/java/com/acme/mall/loyalty/Member.java:25-29`, `src/main/java/com/acme/mall/order/OrderService.java:20-34`

**缺失点**：`Member.totalSpent` 与 `Member.lastOrderAt` 仅声明与读取，代码中未发现任何写入点（OrderService 的 pay/ship/confirm 均不更新会员）。这两个字段由谁、在何时更新无法确定，需人工确认（可能由本代码库之外的结算/会员系统负责）。

## BR-012 支付超时：待支付保留 30 分钟

- **类型**: 业务规则
- **同义词**: 订单超时, 支付超时, 待支付保留, 30分钟, 支付时限, payment timeout, expired, PAY_TIMEOUT_MINUTES
- **模块**: order
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/order/OrderService.java:13-14`, `src/main/java/com/acme/mall/order/OrderService.java:61-64`

**规则**：当订单状态为 `PENDING` 且 `createdAt + 30 分钟` 早于 `now` 时，`expired` 判定为超时（返回 true）。
**例外**：该方法只做判定，未在代码中看到超时后自动取消/流转的动作。

## BR-013 已支付订单不可直接取消

- **类型**: 业务规则
- **同义词**: 取消订单, 不可取消已支付, 支付后取消, cancel order, 走退款流程, 取消限制
- **模块**: order
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/order/OrderService.java:36-44`

**规则**：`cancel` 仅允许 `PENDING` 订单；否则抛出 `IllegalStateException("已支付订单不可直接取消，请走退款流程")`。即：只有待支付订单可直接取消，已支付订单须走退款。

## BR-014 退款仅限已发货或已完成订单

- **类型**: 业务规则
- **同义词**: 可退款状态, 退款前置条件, 退款条件, refundable, 哪些订单能退款, SHIPPED, COMPLETED
- **模块**: order
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/order/OrderService.java:16-18`, `src/main/java/com/acme/mall/order/OrderService.java:46-51`

**规则**：`beginRefund` 仅允许状态属于 `REFUNDABLE = {SHIPPED, COMPLETED}` 的订单；否则抛 `IllegalStateException("当前状态不支持退款")`。

## BR-015 状态流转守卫：必须处于期望前置状态

- **类型**: 业务规则
- **同义词**: 状态守卫, 前置状态, 非法状态流转, state guard, guard, 状态校验
- **模块**: order
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/order/OrderService.java:66-70`

**规则**：私有 `guard(o, expected)` 校验当前状态等于期望状态，否则抛 `IllegalStateException("非法状态流转: " + 当前 + " -> " + 期望)`。`pay`/`ship`/`confirm`/`finishRefund` 均经此守卫。

## BR-016 订单实付金额(paidAmt)的赋值规则缺失

- **类型**: 业务规则
- **同义词**: 实付金额, paidAmt, 支付金额写入, 订单金额赋值, 实付更新
- **模块**: order
- **置信度**: 🔴 gap
- **溯源**: `src/main/java/com/acme/mall/order/Order.java:28-30`, `src/main/java/com/acme/mall/order/OrderService.java:20-23`

**缺失点**：`Order.paidAmt`（实付金额）字段仅声明与读取（`getPaidAmt`），`pay(Order)` 只调用 `setState(PAID)`，未设置 `paidAmt`。实付金额由谁、依据什么规则写入无法确定，需人工确认。

## BR-017 会员分层折扣率

- **类型**: 业务规则
- **同义词**: 会员折扣, 等级折扣, 分层折扣, 打折, member discount, VIP优惠, 折扣率, 85折, 9折
- **模块**: pricing
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/pricing/DiscountService.java:12-15`, `src/main/java/com/acme/mall/pricing/DiscountService.java:20-31`

**规则**：按会员分层返回结算系数：`PLATINUM`=0.85、`GOLD`=0.90、`SILVER`=0.95，其余（`NORMAL`）=1.00。

## BR-018 活动商品不适用分层折扣

- **类型**: 业务规则
- **同义词**: 活动商品不打折, 促销不叠加折扣, 原价结算, promo no discount, 活动价不与会员折扣叠加
- **模块**: pricing
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/pricing/DiscountService.java:33-40`

**规则**：`promoItem=true` 时 `apply` 直接返回 `normalize(gross)`，不乘分层系数。
**说明**：注释「活动商品按原价结算，不适用分层系数」。

## BR-019 试算顺序：净额 → 券 → 运费 → 应付

- **类型**: 业务规则
- **同义词**: 试算顺序, 计价顺序, 价格计算顺序, 应付计算, quote order, 结算顺序
- **模块**: pricing
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/pricing/PriceCalculator.java:28-39`

**规则**：
1. `rate = promoItem ? 1 : rateOf(lvl)`；
2. `goodsNet = discountService.apply(gross, lvl, promoItem)`（会员折后净额）；
3. `couponCut = couponService.bestReduction(goodsNet, coupons, rate)`；
4. `afterCoupon = normalize(goodsNet − couponCut)`；
5. `shipFee = shippingFeeCalculator.fee(afterCoupon, lvl, regionCode)`（以券后金额为运费判定基数）；
6. `payableAmt = chargeable(afterCoupon + shipFee)`（不低于 0.01）。

**例外**：活动商品时 `rate` 取 1.00，会员权益值为 0，券只要抵扣 > 0 即被采用。券与会员折扣的取向见 BR-008。

## BR-020 售后 7 天窗口

- **类型**: 业务规则
- **同义词**: 售后期限规则, 7天窗口, 超出售后期限, within window, 退货时间限制, 售后时效校验
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundService.java:16-17`, `src/main/java/com/acme/mall/refund/RefundService.java:28-33`, `src/main/java/com/acme/mall/refund/RefundService.java:45-48`

**规则**：`withinWindow`：若订单状态不是 `COMPLETED` 则直接返回 true；若为 `COMPLETED`，则要求 `completedAt + 7 天` 晚于 `now`。`create` 中若不在窗口内，抛 `IllegalStateException("已超出售后申请期限")`。
**例外**：时间窗只约束已完成订单；其它状态（如 SHIPPED）不进行时间窗校验。

## BR-021 退款金额：整单退净额+运费，部分退净额

- **类型**: 业务规则
- **同义词**: 退款金额, 退货金额, 退款计算, refund amount, calcRefund, 应退金额
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundService.java:35-43`

**规则**：`wholeOrder=true` 时退 `normalize(goodsAmt + shipFee)`（商品净额 + 运费）；否则退 `normalize(goodsPortion)`（仅对应商品净额）。

## BR-022 发起退款触发订单进入退款中

- **类型**: 业务规则
- **同义词**: 发起退款, 申请退款, 进入退款中, begin refund, REFUNDING, 退款状态流转
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundService.java:45-50`

**规则**：`create` 先校验售后时间窗，再调用 `orderService.beginRefund(o)` 将订单置为 `REFUNDING`。若订单状态不在 `{SHIPPED, COMPLETED}` 会被 `beginRefund` 拒绝（见 BR-014）。

## BR-023 整单/部分由 itemIds 是否为空决定

- **类型**: 业务规则
- **同义词**: 整单判定, itemIds 为空, 是否整单退款, whole order flag, 退款方式判定
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:23-26`

**规则**：`RefundController.create` 将 `req.getItemIds() == null` 作为 `wholeOrder` 传入 `refundService.create`。即：未指定商品行（itemIds 为 null）时按整单退款处理。

## BR-024 退款须经客服主管审批

- **类型**: 业务规则
- **同义词**: 退款审批, 主管审批, 退款须审批, approval required, 审批后出款, 退款审核
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:28-33`

**规则**：退款审批为独立步骤，限定 `CS_LEAD` 角色调用；方法注释「退款须经客服主管审批后方可执行」，正文注释「审批后由结算系统出款」。
**例外**：`approve` 方法体为空，批准与后续出款/完成退款之间的实际衔接在代码中未体现（见 WF-004）。

## BR-025 发起退款接口未解析订单实体

- **类型**: 业务规则
- **同义词**: 退款订单为空, create null, 订单未解析, RefundController 缺陷, 退款接口问题
- **模块**: refund
- **置信度**: 🔴 gap
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:23-25`, `src/main/java/com/acme/mall/refund/RefundService.java:45-48`

**缺失点**：`RefundController.create` 调用 `refundService.create(null, ...)`，把订单实参写死为 `null`。而 `RefundService.create` → `withinWindow(o,...)` 会立即对 `o.stateOf()` 解引用。订单实体应如何由 `orderId` 解析、以及该接口能否正常工作，无法从代码确定，需人工确认（疑为缺陷或未完成接线）。

## BR-026 运费基础与免运费规则

- **类型**: 业务规则
- **同义词**: 运费规则, 包邮, 免运费, 满99包邮, 白金包邮, free shipping, BASE_FEE, FREE_LINE, 基础运费
- **模块**: shipping
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:14-15`, `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:28-32`

**规则**：基础运费 `BASE_FEE`=12.00 元；若会员为 `PLATINUM` 或商品净额 `netAmount >= FREE_LINE`(99.00)，则运费置为 0。
**例外**：免运费只免基础运费，偏远加收仍会另加（见 BR-027）。

## BR-027 偏远地区加收 15 元

- **类型**: 业务规则
- **同义词**: 偏远加收, 偏远附加费, 偏远运费, remote surcharge, 15元, 加收运费
- **模块**: shipping
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:16-19`, `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:33-35`

**规则**：若 `regionCode` 属于 `{XZ, XJ, NM, QH}`，在（可能已置 0 的）运费基础上再加 `REMOTE_SURCHARGE`=15.00 元。
