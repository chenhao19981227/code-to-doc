# 模块：coupon

## 模块概述

`coupon` 模块负责优惠券的定义与抵扣计算，含枚举 `CouponType`、实体 `Coupon` 与服务 `CouponService`。它决定单张券的抵扣额、可用性过滤，以及"一单一券"和"券与会员折扣如何取舍"的规则，是 pricing 试算中优惠环节的核心。

**本模块能力**：券类型建模（满减/折扣/现金）、单券抵扣计算、可用券筛选、一单一券、券与会员折扣互斥取向。

---

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

## ENT-001 优惠券 Coupon

- **类型**: 业务实体
- **同义词**: 优惠券, 券, coupon, t_coupon, 券实体, 优惠券表
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/Coupon.java:10-38`

**说明**：数据库实体，表名 `t_coupon`。关键字段：`coupType`（券类型序号，对应 CouponType）、`faceValue`（满减/现金券面额）、`rateValue`（折扣券比例值）、`threshold`（满减券门槛）、`usableFlag`（true=可用，false=已冻结）、`expireAt`（过期时间）。
**约束/关系**：无 ORM 关联；券不持有归属人，可用券列表由调用方传入。

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
