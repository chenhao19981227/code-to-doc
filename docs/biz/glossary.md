# 术语表 (glossary)

本文件收录领域术语卡。检索单元为每个 `## TERM-xxx` 二级标题块。

## TERM-001 金额归一化

- **类型**: 术语
- **同义词**: 金额归一化, 金额处理, 金额规整, 保留两位小数, 金额精度, amount normalization, normalize, AmountUtils, 金额工具
- **模块**: common
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/common/AmountUtils.java:6-8`, `src/main/java/com/acme/mall/common/AmountUtils.java:20-25`

**说明**：AmountUtils 为金额处理工具，注释明确「所有对外可见的金额都必须经过此处归一化」。内部计算值经归一化后作为对外金额。

## TERM-002 优惠券类型

- **类型**: 术语
- **同义词**: 券类型, 优惠券类型, 券种, 优惠券种类, coupon type, CouponType, coup_type, 券类别
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponType.java:3-9`, `src/main/java/com/acme/mall/coupon/Coupon.java:17-19`

**说明**：券类型枚举 `CouponType` 含三种：`FULL_REDUCTION`（满减）、`DISCOUNT`（折扣）、`CASH`（现金）。数据库列 `t_coupon.coup_type` 存其序号，`Coupon.type()` 用 `CouponType.values()[coupType]` 还原。

## TERM-003 满减券

- **类型**: 术语
- **同义词**: 满减券, 满减, 满X减Y, 满减优惠, full reduction, threshold coupon, 门槛券
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponType.java:7`, `src/main/java/com/acme/mall/coupon/Coupon.java:29-31`, `src/main/java/com/acme/mall/coupon/CouponService.java:43-44`

**说明**：`FULL_REDUCTION` 券，需达到使用门槛 `threshold` 才抵扣面额 `faceValue`。

## TERM-004 折扣券

- **类型**: 术语
- **同义词**: 折扣券, 打折券, 折扣优惠, discount coupon, rate coupon, 折扣率, rate_value
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponType.java:8`, `src/main/java/com/acme/mall/coupon/Coupon.java:25-27`, `src/main/java/com/acme/mall/coupon/CouponService.java:41-42`

**说明**：`DISCOUNT` 券，按比例值 `rateValue`（如 0.88）抵扣；`rateValue` 表示折后系数。

## TERM-005 现金券

- **类型**: 术语
- **同义词**: 现金券, 代金券, 无门槛券, 抵金券, cash coupon, voucher, 面额
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/CouponType.java:9`, `src/main/java/com/acme/mall/coupon/Coupon.java:21-23`, `src/main/java/com/acme/mall/coupon/CouponService.java:45-46`

**说明**：`CASH` 券，直接抵扣面额 `faceValue`，无门槛判断。

## TERM-006 会员等级 / 用户分层

- **类型**: 术语
- **同义词**: 会员等级, 用户分层, 会员分层, 会员级别, 等级, 会员, VIP等级, member level, vip level, MemberLevel, vipLvl
- **模块**: loyalty
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/loyalty/MemberLevel.java:3-10`, `src/main/java/com/acme/mall/loyalty/Member.java:17-19`

**说明**：用户分层枚举 `MemberLevel`，常量顺序 `NORMAL`、`SILVER`、`GOLD`、`PLATINUM`。代码注释「顺序与 t_member.vip_lvl 的取值一一对应」；`Member.vipLvl` 字段注释为「用户分层值，对应 MemberLevel 的序号」，`Member.level()` 用 `MemberLevel.values()[vipLvl]` 还原。

## TERM-007 会员等级中文称谓

- **类型**: 术语
- **同义词**: 普通会员, 银卡会员, 金卡会员, 白金会员, 普通, 银卡, 金卡, 白金, normal, silver, gold, platinum
- **模块**: loyalty
- **置信度**: 🟡 inferred
- **溯源**: `src/main/java/com/acme/mall/loyalty/MemberLevel.java:6-10`

**说明（推断）**：代码仅给出英文常量 `NORMAL/SILVER/GOLD/PLATINUM`，未出现中文等级名。按命名惯例推断对应「普通 / 银卡 / 金卡 / 白金」。
**缺失证据**：源代码与注释中无官方的中文称谓映射。

## TERM-008 订单状态

- **类型**: 术语
- **同义词**: 订单状态, 订单状态值, order status, order state, OrderState, 订单阶段
- **模块**: order
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/order/OrderState.java:3-13`

**说明**：`OrderState` 七个状态：`PENDING`（待支付）、`PAID`（已支付）、`SHIPPED`（已发货）、`COMPLETED`（已完成）、`REFUNDING`（退款中）、`REFUNDED`（已退款）、`CANCELLED`（已取消）。注释「序号持久化于 t_order.state」，`Order.stateOf()`/`setState()` 以 ordinal 与枚举互转。

## TERM-009 结算系数 / 会员折扣率

- **类型**: 术语
- **同义词**: 结算系数, 会员折扣率, 折扣系数, 打折系数, discount rate, member rate, rateOf, 分层系数
- **模块**: pricing
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/pricing/DiscountService.java:12-15`, `src/main/java/com/acme/mall/pricing/DiscountService.java:20-31`

**说明**：每个会员分层对应一个结算系数：`NORMAL`=1.00、`SILVER`=0.95、`GOLD`=0.90、`PLATINUM`=0.85。折后金额 = 原价 × 结算系数。

## TERM-010 活动商品

- **类型**: 术语
- **同义词**: 活动商品, 促销商品, 特价商品, 活动价商品, promo item, promotion, promoItem, 促销品
- **模块**: pricing
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/pricing/DiscountService.java:33-40`, `src/main/java/com/acme/mall/pricing/PriceCalculator.java:33`

**说明**：`promoItem=true` 的商品按原价结算，不适用会员分层系数（见 BR-018）。

## TERM-011 商品净额与应付金额

- **类型**: 术语
- **同义词**: 商品净额, 折后净额, 净额, 应付金额, 实付金额, goodsNet, payableAmt, net amount, 商品金额
- **模块**: pricing
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/pricing/PriceCalculator.java:28-39`, `src/main/java/com/acme/mall/pricing/Quote.java:8-20`

**说明**：商品净额（goodsNet）= 会员折后商品金额；应付金额（payableAmt）= 净额 − 券抵扣 + 运费，且不低于 0.01 元。

## TERM-012 售后申请期限

- **类型**: 术语
- **同义词**: 售后期限, 售后申请期限, 退货期限, 售后窗口, 7天, after-sale days, AFTER_SALE_DAYS, 售后时效
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundService.java:16-17`, `src/main/java/com/acme/mall/refund/RefundService.java:28-33`

**说明**：自订单完成之日起 7 天内可申请售后（`AFTER_SALE_DAYS = 7`）。

## TERM-013 整单退款 / 部分退款

- **类型**: 术语
- **同义词**: 整单退款, 部分退款, 全额退款, 按行退款, whole order refund, partial refund, 退货方式
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundService.java:35-43`, `src/main/java/com/acme/mall/refund/RefundRequest.java:13-17`

**说明**：整单退款退回商品净额与运费；部分退款只退对应商品净额（goodsPortion）。入参 `itemIds` 为空表示整单退款。

## TERM-014 运费

- **类型**: 术语
- **同义词**: 运费, 邮费, 物流费, 快递费, shipping fee, shipFee, freight, 配送费
- **模块**: shipping
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:11-19`, `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:28-37`

**说明**：由 `ShippingFeeCalculator.fee` 计算，基础运费 `BASE_FEE`=12.00 元，包邮线 `FREE_LINE`=99.00 元，偏远加收 `REMOTE_SURCHARGE`=15.00 元。

## TERM-015 偏远地区

- **类型**: 术语
- **同义词**: 偏远地区, 偏远附加费, 偏远加收, 偏远运费, remote region, surcharge, 地区编码, XZ, XJ, NM, QH
- **模块**: shipping
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:16-19`, `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:33-35`

**说明**：`REMOTE_REGIONS = ["XZ", "XJ", "NM", "QH"]`（西藏/新疆/内蒙古/青海的地区编码），命中即加收 15.00 元。
