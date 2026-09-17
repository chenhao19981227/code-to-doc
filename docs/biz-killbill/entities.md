# 业务实体（ENT）

> 来源模块：invoice, overdue。检索单元 = 每个 `## ` 二级标题块。

## ENT-001 发票

- **类型**: 业务实体
- **同义词**: 发票实体, 账单实体, invoice entity
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoice.java:44-62`

**关系**：1 张发票 → N 个 `InvoiceItem`、N 个 `InvoicePayment`、N 个 trackingId；子发票 → 1 张父发票。

## ENT-002 发票行项目

- **类型**: 业务实体
- **同义词**: 行项目实体, invoice item entity
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/InvoiceItemFactory.java:54-126`

**关键字段**：`id`、`invoiceId`、`accountId`、`bundleId`、`subscriptionId`、`productName/planName/phaseName/usageName`、`startDate/endDate`、`amount`、`rate`、`currency`、`linkedItemId`、`quantity`、`itemDetails`。

## ENT-003 发票支付

- **类型**: 业务实体
- **同义词**: 发票支付, 支付记录, 收款记录, invoice payment, payment on invoice
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:207-242`

**关键字段**：`type`(ATTEMPT/REFUND/CHARGED_BACK)、`status`(SUCCESS/PENDING/…)、`amount`、`currency`/`processedCurrency`。仅 `SUCCESS` 参与金额统计。

## ENT-004 账户余额与账户 CBA

- **类型**: 业务实体
- **同义词**: 账户余额, 账户欠款, 账户信用, account balance, account CBA
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:730-765`

**计算**：账户余额 = Σ(非 DRAFT/VOID、非核销、父余额非 0 的发票原始余额) − Σ(账户 CBA)。

## ENT-005 父发票—子发票关系

- **类型**: 业务实体
- **同义词**: 父子发票映射, 父发票关联, parent-child invoice, InvoiceParentChild
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1402-1404`, `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:497-519`

**约束**：一个子发票至多映射到一个父发票（`checkState(mappings.size() == 1)`）。

## ENT-006 用量追踪号

- **类型**: 业务实体
- **同义词**: 用量追踪ID, 计量追踪, tracking id, InvoiceTracking
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:805-808`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:1404-1413`

**含义**：记录某段用量已被哪张发票结算，防止重复计费；发票作废时对应 trackingId 被停用。

## ENT-007 逾期状态实体

- **类型**: 业务实体
- **同义词**: 逾期状态实体, overdue state entity
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:47-76`

**关键字段**：`name`（XML `@XmlID`，唯一）、`condition`、`externalMessage`、`blockChanges`、`disableEntitlement`、`subscriptionCancellationPolicy`、`isClearState`、`autoReevaluationInterval`。

## ENT-008 逾期条件实体

- **类型**: 业务实体
- **同义词**: 逾期条件实体, overdue condition entity
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:50-67`

**关键字段**：`numberOfUnpaidInvoicesEqualsOrExceeds`、`totalUnpaidInvoiceBalanceEqualsOrExceeds`、`timeSinceEarliestUnpaidInvoiceEqualsOrExceeds`、`responseForLastFailedPayment[]`、`controlTagInclusion`、`controlTagExclusion`。

## ENT-009 逾期配置与账户状态集

- **类型**: 业务实体
- **同义词**: 逾期配置实体, 账户状态集, overdue config entity, account overdue states
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueConfig.java:41-46`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:33-56`

**关系**：`DefaultOverdueConfig` 1 → 1 `DefaultOverdueStatesAccount`；状态集含 `state[]` 与 `initialReevaluationInterval`，并恒有一个内置清账状态。

## ENT-010 计费状态

- **类型**: 业务实体
- **同义词**: 计费状态实体, billing state entity
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:67-83`

**关键字段**：`accountId`、`numberOfUnpaidInvoices`、`balanceOfUnpaidInvoices`、`dateOfEarliestUnpaidInvoice`、`idOfEarliestUnpaidInvoice`、`responseForLastFailedPayment`、`tags[]`。

## ENT-011 封禁状态

- **类型**: 业务实体
- **同义词**: 封禁状态, 阻塞状态, blocking state
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:221-235`

**含义**：逾期服务写入账户级封禁状态，服务名 `OverdueService.OVERDUE_SERVICE_NAME`，状态名即逾期状态名，并携带 blockChanges/blockEntitlement/blockBilling 三个布尔与生效时间。
