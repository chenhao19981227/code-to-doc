# 业务实体 (entities)

本文件收录业务实体卡（核心对象及其关键关系/约束）。

## ENT-001 优惠券 Coupon

- **类型**: 业务实体
- **同义词**: 优惠券, 券, coupon, t_coupon, 券实体, 优惠券表
- **模块**: coupon
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/coupon/Coupon.java:10-38`

**说明**：数据库实体，表名 `t_coupon`。关键字段：`coupType`（券类型序号，对应 CouponType）、`faceValue`（满减/现金券面额）、`rateValue`（折扣券比例值）、`threshold`（满减券门槛）、`usableFlag`（true=可用，false=已冻结）、`expireAt`（过期时间）。
**约束/关系**：无 ORM 关联；券不持有归属人，可用券列表由调用方传入。

## ENT-002 会员 Member

- **类型**: 业务实体
- **同义词**: 会员, 用户, 客户, 会员信息, member, user, t_member
- **模块**: loyalty
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/loyalty/Member.java:10-29`

**说明**：数据库实体，表名 `t_member`。字段：`vipLvl`（分层序号）、`status`（1=启用，0=注销，语义来自字段注释）、`lastOrderAt`（最近下单时间）、`totalSpent`（累计消费）。
**约束/关系**：无 ORM 关联；`memberId` 在 Order 中逻辑引用会员。
**注意**：源码中未发现写入 `status` / `lastOrderAt` / `totalSpent` 的逻辑（见 BR-011）。

## ENT-003 订单 Order

- **类型**: 业务实体
- **同义词**: 订单, 交易单, order, t_order, 订单表
- **模块**: order
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/order/Order.java:10-39`

**说明**：数据库实体，表名 `t_order`。字段：`memberId`（会员）、`goodsAmt`（商品折后净额）、`shipFee`（运费）、`paidAmt`（实付金额）、`state`（状态序号）、`createdAt`（创建时间）、`completedAt`（完成时间）。
**约束/关系**：无 ORM 关联；`memberId` 逻辑指向 Member。
**注意**：源码中未发现写入 `paidAmt` 的逻辑（见 BR-016）。

## ENT-004 结算试算结果 Quote

- **类型**: 业务实体
- **同义词**: 试算结果, 报价, 试算单, 结算结果, quote, 计价结果
- **模块**: pricing
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/pricing/Quote.java:5-20`

**说明**：不可变值对象（非数据库实体），含 `goodsNet`（商品净额）、`couponCut`（券抵扣额）、`shipFee`（运费）、`payableAmt`（应付金额）。

## ENT-005 试算入参 QuoteRequest

- **类型**: 业务实体
- **同义词**: 试算入参, 询价入参, 试算请求, quote request, QuoteRequest, 计价入参
- **模块**: pricing
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/pricing/PricingController.java:29-36`

**说明**：试算接口入参，含 `gross`（商品原价）、`level`（会员分层）、`promoItem`（是否活动商品）、`coupons`（可用券列表）、`regionCode`（收货地区编码）。为 `PricingController` 的静态内部类。

## ENT-006 退款申请 RefundRequest

- **类型**: 业务实体
- **同义词**: 退款申请, 退货申请, 退款单, refund request, RefundRequest, 售后申请
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundRequest.java:6-19`

**说明**：退款申请入参，字段：`orderId`（订单）、`itemIds`（申请退款的商品行，为空表示整单退款）、`goodsPortion`（部分退款时对应商品的净额）、`reason`（原因）。无 setter，为反序列化 DTO。
