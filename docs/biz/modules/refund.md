# 模块：refund

## 模块概述

`refund` 模块负责售后退款，含 `RefundController`、`RefundRequest`、`RefundService`。它定义退款申请入参、售后 7 天窗口、退款金额计算，并通过订单服务把订单从 `SHIPPED`/`COMPLETED` 推进到 `REFUNDING`；同时通过 `@PreAuthorize` 约束客服与客服主管的权限。

**本模块能力**：退款申请、整单/部分退款判定与金额计算、售后时间窗校验、退款权限（CS 发起 / CS_LEAD 审批）。

---

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

## ENT-006 退款申请 RefundRequest

- **类型**: 业务实体
- **同义词**: 退款申请, 退货申请, 退款单, refund request, RefundRequest, 售后申请
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundRequest.java:6-19`

**说明**：退款申请入参，字段：`orderId`（订单）、`itemIds`（申请退款的商品行，为空表示整单退款）、`goodsPortion`（部分退款时对应商品的净额）、`reason`（原因）。无 setter，为反序列化 DTO。

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

## WF-003 退款流程

- **类型**: 业务流程
- **同义词**: 退款流程, 退货流程, 售后流程, 退款审批流程, refund process, 退款处理
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:20-33`, `src/main/java/com/acme/mall/refund/RefundService.java:45-50`, `src/main/java/com/acme/mall/order/OrderService.java:46-56`

**步骤**：
1. 客服（CS 或 CS_LEAD）调用 `POST /api/refunds` 发起退款申请。
2. 依据 `itemIds` 是否为空判定整单/部分退款，并计算应退金额。
3. 校验售后 7 天窗口（仅约束已完成订单）。
4. 调用 `orderService.beginRefund` 将订单从 `SHIPPED`/`COMPLETED` 置为 `REFUNDING`。
5. 客服主管（CS_LEAD）调用 `POST /api/refunds/{id}/approve` 审批。
6. 审批后由结算系统出款；订单最终经 `finishRefund` 置为 `REFUNDED`。

```mermaid
flowchart TD
  A[客服 CS/CS_LEAD 发起退款 POST /api/refunds] --> B{售后 7 天窗口内?}
  B -- 否 --> X[拒绝: 已超出售后申请期限]
  B -- 是 --> C[订单置为 REFUNDING beginRefund]
  C --> D[客服主管 CS_LEAD 审批 POST /api/refunds/{id}/approve]
  D --> E[结算系统出款]
  E --> F[finishRefund 订单置为 REFUNDED]
```

## WF-004 退款审批后的出款与完成衔接缺失

- **类型**: 业务流程
- **同义词**: 审批后出款, approve 空实现, 退款完成衔接, payout after approval, 退款出款
- **模块**: refund
- **置信度**: 🔴 gap
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:28-33`, `src/main/java/com/acme/mall/order/OrderService.java:53-56`

**缺失点**：`RefundController.approve` 方法体为空，仅注释「审批后由结算系统出款」。从「审批」到「结算出款」，再到 `OrderService.finishRefund`（REFUNDING → REFUNDED）的触发者在代码中不存在。该流程段的实现或外部系统责任需人工确认。

## ROLE-002 客服（CS）可代客发起退款

- **类型**: 角色/权限
- **同义词**: 客服, CS, 客服权限, 代客退款, customer service, 发起退款权限, 售后客服
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:20-23`

**说明**：角色 `CS` 或 `CS_LEAD` 可调用 `POST /api/refunds` 发起退款申请，方法注释「客服可代客发起退款」，权限表达式 `@PreAuthorize("hasAnyRole('CS', 'CS_LEAD')")`。

## ROLE-003 客服主管（CS_LEAD）审批退款

- **类型**: 角色/权限
- **同义词**: 客服主管, CS_LEAD, 主管, 主管审批, 退款审批权限, refund approval
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:28-30`

**说明**：仅角色 `CS_LEAD` 可调用 `POST /api/refunds/{id}/approve` 审批退款，权限表达式 `@PreAuthorize("hasRole('CS_LEAD')")`。
