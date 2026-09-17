# 未确定项 (gaps)

本文件列出所有 🔴 gap 卡（无法从代码确定、需人工确认的知识点）。下列条目为**清单索引**，完整卡片见对应类型文件（rules.md / workflows.md）。

### BR-011 会员累计消费与最近下单时间的更新规则缺失

- **模块**: loyalty
- **完整卡片**: [rules.md](rules.md) 之 `BR-011`
- **缺失点**：`Member.totalSpent` 与 `Member.lastOrderAt` 仅声明与读取，代码中未发现写入点（OrderService 的 pay/ship/confirm 均不更新会员）。由谁、在何时更新无法确定（可能由本代码库之外的结算/会员系统负责）。
- **溯源**: `src/main/java/com/acme/mall/loyalty/Member.java:25-29`, `src/main/java/com/acme/mall/order/OrderService.java:20-34`

### BR-016 订单实付金额(paidAmt)的赋值规则缺失

- **模块**: order
- **完整卡片**: [rules.md](rules.md) 之 `BR-016`
- **缺失点**：`Order.paidAmt` 仅声明与读取，`pay(Order)` 只置状态 `PAID`，未设置 `paidAmt`。实付金额由谁、依据什么规则写入无法确定。
- **溯源**: `src/main/java/com/acme/mall/order/Order.java:28-30`, `src/main/java/com/acme/mall/order/OrderService.java:20-23`

### BR-025 发起退款接口未解析订单实体

- **模块**: refund
- **完整卡片**: [rules.md](rules.md) 之 `BR-025`
- **缺失点**：`RefundController.create` 调用 `refundService.create(null, ...)`，订单实参写死为 `null`；而下游 `withinWindow` 会立即对 `o.stateOf()` 解引用。订单应如何由 `orderId` 解析、接口能否正常工作无法从代码确定（疑为缺陷或未完成接线）。
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:23-25`, `src/main/java/com/acme/mall/refund/RefundService.java:45-48`

### WF-004 退款审批后的出款与完成衔接缺失

- **模块**: refund
- **完整卡片**: [workflows.md](workflows.md) 之 `WF-004`
- **缺失点**：`RefundController.approve` 方法体为空（仅注释"审批后由结算系统出款"）。从审批到结算出款、再到 `OrderService.finishRefund`（REFUNDING → REFUNDED）的触发者在代码中不存在。
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:28-33`, `src/main/java/com/acme/mall/order/OrderService.java:53-56`

---

**汇总**：🔴 gap 卡共 4 张（BR-011、BR-016、BR-025、WF-004）。
