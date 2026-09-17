# 术语（TERM）

> 来源模块：invoice, overdue。检索单元 = 每个 `## ` 二级标题块。

## TERM-001 发票

- **类型**: 术语
- **同义词**: 发票, 账单, 单据, 费用单, invoice, bill
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoice.java:44-62`, `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:90-94`

**含义**：账户在目标日期前应收费用的汇总单，携带账户、发票日期、目标日期、币种、状态(DRAFT/COMMITTED/VOID)、行项目、支付、追踪号。

## TERM-002 发票行项目

- **类型**: 术语
- **同义词**: 发票行项目, 明细行, 收费项, 账单条目, invoice item, line item
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/InvoiceItemFactory.java:54-126`

**含义**：发票下的一条费用/抵扣明细，带类型、金额、起止服务期、关联订阅/套餐/阶段、`linkedItemId`（调账/修复指向原项）等。

## TERM-003 行项目类型

- **类型**: 术语
- **同义词**: 行项目类型, 费用类型, item type, invoice item type
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:73-94`, `invoice/src/main/java/org/killbill/billing/invoice/model/InvoiceItemFactory.java:91-124`

**含义**：`EXTERNAL_CHARGE`、`FIXED`、`RECURRING`、`USAGE`、`TAX`、`CBA_ADJ`、`CREDIT_ADJ`、`ITEM_ADJ`、`REPAIR_ADJ`、`PARENT_SUMMARY`。分类：收费类 = TAX/EXTERNAL_CHARGE/FIXED/USAGE/RECURRING；账户信用 = CBA_ADJ；行项目调整 = ITEM_ADJ/REPAIR_ADJ。

## TERM-004 账户信用余额（CBA）

- **类型**: 术语
- **同义词**: 账户余额抵扣, 信用余额, 抵扣余额, 账户贷方, 预存余额, CBA, credit balance, account credit
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:77-80`, `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:56-97`

**含义**：账户级可抵扣余额，由 `CBA_ADJ` 累计。负余额发票**生成信用**（正 CBA），正余额已提交发票**消耗信用**（负 CBA）。

## TERM-005 账单日与计费周期

- **类型**: 术语
- **同义词**: 账单日, 计费日, BCD, bill cycle day, 计费周期, billing period
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:247-254`

**含义**：`billCycleDayLocal`(BCD) 决定订阅每月出账日；`BillingPeriod`(MONTHLY/ANNUAL 等) 决定周期长度；周期对齐由 `BillingIntervalDetail` 完成。

## TERM-006 按比例计费

- **类型**: 术语
- **同义词**: 按比例计费, 尾差, 按天折算, 分摊, proration, pro-ration
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceDateUtils.java:53-89`

**含义**：服务起止与完整计费周期不对齐时按天数比例计费；含首期按比例(leading)与末段按比例(trailing)。

## TERM-007 试算（Dry Run）

- **类型**: 术语
- **同义词**: 试算, 预演, 预览账单, 模拟开票, dry run, preview invoice, upcoming invoice
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:362-374`

**含义**：`DryRunArguments`/`DryRunInfo` 驱动、不落盘的发票生成；类型含 `TARGET_DATE`/`UPCOMING_INVOICE`/`SUBSCRIPTION_ACTION`。

## TERM-008 用量计费（后付，in arrear）

- **类型**: 术语
- **同义词**: 用量计费, 按用量收费, 后付, 使用量账单, usage billing, usage in arrear, metered billing
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/UsageInvoiceItemGenerator.java:146-155`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:199-217`

**含义**：按订阅计量单位累计量计费；`BillingMode.IN_ARREAR` 表示周期结束后结算，`TierBlockPolicy` 决定分档(ALL_TIERS/TOP_TIER)。

## TERM-009 发票核销（Write-off）

- **类型**: 术语
- **同义词**: 核销, 坏账核销, 标记为坏账, write-off, writeoff, bad debt
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:417-422`, `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:485-489`

**含义**：给发票打 `WRITTEN_OFF` 控制标签，声明不再计入余额；核销发票按 0 参与账户余额计算。

## TERM-010 迁移发票

- **类型**: 术语
- **同义词**: 迁移发票, 数据迁移账单, 历史账单导入, migration invoice
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceModelDaoHelper.java:33-46`

**含义**：`isMigrationInvoice()==true` 的发票，原始余额固定为 0。

## TERM-011 父子账户合并开票

- **类型**: 术语
- **同义词**: 父账户, 子账户, 合并开票, 汇总账单, 集团账单, parent invoice, consolidated invoicing, hierarchical billing
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1340-1405`

**含义**：子账户发票金额汇总到父账户的一张 `PARENT_SUMMARY` 草稿发票，由父账户统一支付。

## TERM-012 目标日期

- **类型**: 术语
- **同义词**: 目标日期, 计费截止日, 开票截止日, target date, targetDate
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:120-154`

**含义**：本次开票计算的时间边界，仅对 `effectiveDate <= targetDate` 的事件出账；受“最远未来 N 个月”与已有发票目标日期约束。

## TERM-013 修复

- **类型**: 术语
- **同义词**: 修复, 冲销重开, 退订重算, repair, REPAIR_ADJ
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoicePruner.java:88-116`

**含义**：订阅变更/取消导致已开票周期项需冲减时，生成 `REPAIR_ADJ` 负项关联原 `RECURRING` 项；被全额修复的项在后续计算中剔除。

## TERM-014 逾期状态

- **类型**: 术语
- **同义词**: 逾期状态, 欠费状态, 催收阶段, overdue state, delinquency state
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:45-76`

**含义**：配置驱动、有名字的账户逾期等级；每个状态携带条件、对外消息、是否封禁变更、是否禁用权益、取消策略、是否清账状态、自动重评间隔。

## TERM-015 清账状态

- **类型**: 术语
- **同义词**: 清账状态, 恢复状态, 正常状态, clear state, recovered state
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:51`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:37-39`

**含义**：表示账户不再逾期；名字固定为 `__KILLBILL__CLEAR__OVERDUE_STATE__`，由 `isClearState=true` 标识，不来自配置。

## TERM-016 逾期条件

- **类型**: 术语
- **同义词**: 逾期条件, 触发条件, 判定条件, overdue condition, trigger condition
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:48-67`

**含义**：对 `BillingState` 的阈值判定组合，字段含欠费发票张数、欠费总额、最早欠费距今时长、上次支付失败响应集合、控制标签包含/排除。

## TERM-017 逾期配置

- **类型**: 术语
- **同义词**: 逾期配置, 催收配置, overdue config, overdue XML
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueConfig.java:35-52`, `overdue/src/main/java/org/killbill/billing/overdue/OverdueProperties.java:27-30`

**含义**：根元素 `overdueConfig` 下含 `accountOverdueStates`（状态集与初始重评间隔）；默认来源 `NoOverdueConfig.xml`，可经 `org.killbill.overdue.uri` 或按租户上传覆盖。

## TERM-018 计费状态

- **类型**: 术语
- **同义词**: 计费状态, 账单快照, billing state, BillingState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:67-84`

**含义**：逾期判定的输入快照，含账户 ID、欠费发票张数、欠费总额、最早欠费发票日期/ID、上次失败支付响应、账户标签。

## TERM-019 重新评估间隔

- **类型**: 术语
- **同义词**: 重评间隔, 复查周期, 催收轮询, reevaluation interval
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:51-57`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:119-125`

**含义**：决定下次重算逾期状态的时间间隔。清账状态使用账户级 `initialReevaluationInterval`；非清账状态使用状态级 `autoReevaluationInterval`。UNLIMITED 或 0 表示“无间隔”。

## TERM-020 逾期取消策略与封禁标志

- **类型**: 术语
- **同义词**: 逾期取消策略, 封禁变更, 禁用权益, cancellation policy, block changes, disable entitlement
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:59-69`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:285-301`

**含义**：`disableEntitlement`(禁用权益并封禁变更) 与 `blockChanges`(仅封禁变更) 控制是否写封禁状态；`subscriptionCancellationPolicy` ∈ {NONE, END_OF_TERM, IMMEDIATE} 控制是否取消订阅。

## TERM-021 逾期相关控制标签

- **类型**: 术语
- **同义词**: 逾期开关, 关闭逾期执行, 坏账标签, overdue enforcement off, AUTO_INVOICING_OFF, WRITTEN_OFF
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:237-253`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:334-349`

**含义**：`OVERDUE_ENFORCEMENT_OFF`（账户级，关闭逾期执行）、`AUTO_INVOICING_OFF`（账户级，封禁计费时自动打上）、`WRITTEN_OFF`（发票级，核销触发逾期重算）。

## TERM-022 逾期通知队列

- **类型**: 术语
- **同义词**: 逾期通知队列, 定时检查队列, overdue queue, check queue, async bus queue
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueCheckNotifier.java:39`, `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusNotifier.java:39`

**含义**：`overdue-check-queue` 承载定时重算；`overdue-async-bus-queue` 承载由发票/支付/标签事件触发的 REFRESH 或 CLEAR 动作。
