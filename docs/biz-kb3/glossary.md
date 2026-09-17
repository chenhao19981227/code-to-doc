# 术语表（Glossary）

> Kill Bill 业务知识库 v3（合并 kb2 既有卡 + kb3 补充卡）；共 98 张卡。

---

## TERM-001 发票项类型（InvoiceItemType）

- **类型**: 术语
- **同义词**: 发票项类型, 条目类型, invoice item type, InvoiceItemType, 费用类型, 账单项类型, line item type
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:39-94`

**说明**：发票项（InvoiceItem）按类型分四类语义：
- **收费项（charge）**：`RECURRING`（周期订阅费）、`FIXED`（固定费/一次性）、`USAGE`（用量费）、`EXTERNAL_CHARGE`（外部收费）、`TAX`（税）。
- **项调整**：`ITEM_ADJ`（针对具体发票项调整）、`REPAIR_ADJ`（修复/改套餐产生的冲销）。
- **账户信用**：`CBA_ADJ`（账户信用余额增减，credit balance adjustment）。
- **发票级信用调整**：`CREDIT_ADJ`（发票级信用）。
- **父账户汇总**：`PARENT_SUMMARY`（父发票上汇总子账户金额的条目）。

## TERM-002 发票项（InvoiceItem）

- **类型**: 术语
- **同义词**: 发票项, 账单项, 条目, invoice item, InvoiceItem, 明细行, line item
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/InvoiceItemBase.java:34-100`

**说明**：发票项是发票的最小计费单元。公共字段：`invoiceId`、`accountId`、`childAccountId`、`startDate`/`endDate`（计费区间）、`amount`（金额）、`currency`、`description`、`invoiceItemType`（类型）。订阅相关项另有 `subscriptionId`、`bundleId`；周期项有 `rate`；修复项有 `linkedItemId`（被冲销的原项目）；用量项有 `quantity`、`itemDetails`。

## TERM-003 发票支付类型（InvoicePaymentType）

- **类型**: 术语
- **同义词**: 支付类型, 发票支付, invoice payment type, ATTEMPT, REFUND, CHARGED_BACK, 退款, 拒付, 支付尝试
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:207-242`

**说明**：发票支付（InvoicePayment）对应支付类型：`ATTEMPT`（支付尝试，成功则计入已付）、`REFUND`（退款）、`CHARGED_BACK`（拒付/退单）。只有支付状态为 `SUCCESS`（InvoicePaymentStatus.SUCCESS）的记录才计入金额统计。

## TERM-004 干跑类型（DryRunType）

- **类型**: 术语
- **同义词**: 干跑, 预演, dry run, DryRunType, 试算发票, 模拟开票, UPCOMING_INVOICE, TARGET_DATE, SUBSCRIPTION_ACTION
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:362-374`, `api/src/main/java/org/killbill/billing/invoice/api/DryRunInfo.java:22-39`

**说明**：干跑（dry-run）表示“只试算、不落库”地生成一张预览发票。`DryRunType` 有三种取值：
- `TARGET_DATE`：按给定目标日期试算；
- `UPCOMING_INVOICE`：由系统自动计算下一张发票的目标日期（此时 inputTargetDate 允许为 null）；
- `SUBSCRIPTION_ACTION`：模拟某个订阅动作（如改套餐/取消）后的开票结果，使用该动作的 effectiveDate。

## TERM-005 用量类型（UsageType: CAPACITY / CONSUMABLE）

- **类型**: 术语
- **同义词**: 用量类型, usage type, UsageType, CAPACITY, CONSUMABLE, 容量计费, 消耗量计费, 按量计费
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:142`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:539-548`

**说明**：用量（usage）分两类：
- `CAPACITY`（容量型）：同一计费周期内取**峰值**（最大值）计费；
- `CONSUMABLE`（消耗型）：同一计费周期内**累加**所有用量计费。

## TERM-006 用量分层（Tier / TieredBlock）

- **类型**: 术语
- **同义词**: 分层定价, 阶梯计费, tier, tiered block, usage tier, 用量档位, 阶梯用量
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:34-87`

**说明**：用量价格按目录中的 **Tier（层/档）** 定义：
- `CONSUMABLE` 用量使用 `TieredBlock`（每层一个 block，按用途单位名匹配），量在本层内按块计价；
- `CAPACITY` 用量使用每层的 `Limit` 定义容量区间。
每个用量至少需要一层（`tiers.length > 0`），否则目录视为非法。

## TERM-007 分比（Proration）

- **类型**: 术语
- **同义词**: 分比, 按比例分摊, proration, pro-ration, 按天折算
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:75-77`, `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:162`

**说明**：分比（pro-ration）指对**不足一个完整计费周期**的使用期间，按天/比例折算应收费用。常见于套餐中途变更、取消、订阅创建未对齐 BCD 等场景。相关计算：`calculateProRationBeforeFirstBillingPeriod`、`calculateProRationAfterLastBillingCycleDate`、`calculateProrationBetweenDates`。

## TERM-008 展示名（pretty name）

- **类型**: 术语
- **同义词**: 展示名, 友好名称, pretty name, prettyPlanName, prettyProductName, 显示名称
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/InvoiceItemFactory.java:131-205`

**说明**：`pretty*` 名称是根据目录（catalog）为发票项计算出的**人类可读展示名**（prettyProductName / prettyPlanName / prettyPhaseName / prettyUsageName），仅对 `FIXED`/`RECURRING`/`TAX`/`USAGE` 类型计算；计算失败或目录缺失时为 null，此时回退到原始名称。

## TERM-009 自动开票关闭（auto_invoice_off）

- **类型**: 术语
- **同义词**: 自动开票关闭, auto invoice off, auto_invoice_off, 停止自动开票, 暂停出账
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:108-110`, `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:387-389`

**说明**：对标记为 `auto_invoice_off` 的订阅，系统在生成固定/周期发票项时会**跳过**其 billing events（不生成该项）；对 `isAccountAutoInvoiceOff()` 为 true 的账户，非 API 触发的开票直接返回空（不自动开票）。

## TERM-010 计费模式（BillingMode: IN_ADVANCE / IN_ARREAR）

- **类型**: 术语
- **同义词**: 计费模式, 预付, 后付, billing mode, IN_ADVANCE, IN_ARREAR, 先付费, 后付费
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:302-321`, `invoice/src/main/java/org/killbill/billing/invoice/optimizer/InvoiceOptimizerExp.java:147-148`

**说明**：`BillingMode` 分两种：
- `IN_ADVANCE`（预付/先付费）：在计费周期**开始时**收费；
- `IN_ARREAR`（后付/后付费）：在计费周期**结束后**收费。

## TERM-011 发票支付状态（InvoicePaymentStatus）完整取值

- **类型**: 术语
- **同义词**: 支付状态, 支付状态枚举, InvoicePaymentStatus, INIT, PENDING, SUCCESS, 支付初始化, 支付挂起, 支付成功
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoicePayment.java:55`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:825`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:990`, `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:69-72`

**说明**：`InvoicePaymentStatus` 在本模块代码中出现 **3 个**取值：
- `INIT`：支付初始化（`notifyOfPaymentInit` 记录；拒付撤销 `postChargebackReversal` 把状态改回 INIT）。
- `PENDING`：支付挂起中（会**阻止**该发票消费账户信用 CBA，见 CBADao 判定）。
- `SUCCESS`：支付成功（唯一会被计入「已付 / 已退款」金额与违约判定的状态）。

**含义**：只有 `SUCCESS` 的支付/退款/拒付计入金额统计；`PENDING` 只用于 CBA 消费门控；`INIT` 表示未完成或已回退。

## TERM-012 发票项默认描述（description）汇总

- **类型**: 术语
- **同义词**: 项描述默认值, item description defaults, 发票项描述, description fallback
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/TaxInvoiceItem.java:84-90`, `invoice/src/main/java/org/killbill/billing/invoice/model/CreditAdjInvoiceItem.java:51-53`, `invoice/src/main/java/org/killbill/billing/invoice/model/ItemAdjInvoiceItem.java:53-55`, `invoice/src/main/java/org/killbill/billing/invoice/model/RepairAdjInvoiceItem.java:51-53`

**说明**：当发票项未显式提供 `description` 时的默认文案：
- `TAX`（TaxInvoiceItem）→ `"Tax"`；
- `CREDIT_ADJ`（CreditAdjInvoiceItem）→ `"Invoice adjustment"`；
- `ITEM_ADJ`（ItemAdjInvoiceItem）→ `"Invoice item adjustment"`；
- `REPAIR_ADJ`（RepairAdjInvoiceItem）→ `"Adjustment (subscription change)"`；
- `FIXED` → `"Fixed price charge"`（有 phase 名时 `"<phase> (fixed price)"`；见 ENT-006）；
- `EXTERNAL_CHARGE` → `"External charge"`（或 `"<plan> (external charge)"`；见 ENT-007）。
- 调整项（AdjInvoiceItem 子类）的 `getCatalogEffectiveDate()` 恒为 null。

## TERM-013 逾期催收（Overdue / Dunning）

- **类型**: 术语
- **同义词**: 逾期, 逾期催收, 催收, 违约, 欠费, 坏账处理, overdue, dunning, delinquency, overdue service, 逾期服务
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `api/src/main/java/org/killbill/billing/overdue/OverdueService.java:26-30`, `overdue/src/main/java/org/killbill/billing/overdue/service/DefaultOverdueService.java:81-89`

**含义**：overdue 是 Kill Bill 的逾期（催收）子系统，作为独立 KillbillService 注册，服务名为 `overdue-service`。它根据「账户当前未付发票情况」自动计算并施加一个命名逾期状态（如 OD1/OD2/OD3），并对账户执行动作（阻止变更、暂停权益、取消订阅、关闭自动开票等）。注意：状态是**账户级**的，不是单订阅级（见 BR-107）。

## TERM-014 逾期状态（OverdueState）

- **类型**: 术语
- **同义词**: 逾期状态, 催收阶段, 逾期等级, 催收级别, overdue state, overdue stage, dunning state, OD1, OD2, OD3
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:44-72`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:85-125`

**含义**：配置中一个带名字的逾期状态，由「一个条件（condition）」+「一组动作」组成。字段包括：`name`（状态名，XML ID，最大 50 字符）、`condition`、`externalMessage`、`blockChanges`、`disableEntitlementAndChangesBlocked`、`subscriptionCancellationPolicy`、`isClearState`、`autoReevaluationInterval`。状态名不是固定枚举值，完全由配置定义（示例配置使用 OD1/OD2/OD3、Good、Overdue、OD4）。

## TERM-015 逾期条件（OverdueCondition）

- **类型**: 术语
- **同义词**: 逾期条件, 催收触发条件, 进入逾期状态条件, overdue condition, dunning condition, condition
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:48-67`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:69-84`

**含义**：判定「账户是否应进入某逾期状态」的谓词，最多包含 6 个子条件：`numberOfUnpaidInvoicesEqualsOrExceeds`、`totalUnpaidInvoiceBalanceEqualsOrExceeds`、`timeSinceEarliestUnpaidInvoiceEqualsOrExceeds`、`responseForLastFailedPaymentIn`、`controlTagInclusion`、`controlTagExclusion`。子条件之间是逻辑 AND；未配置的子条件被忽略（视为真）。

## TERM-016 清算状态（Clear State / 未逾期）

- **类型**: 术语
- **同义词**: 清算状态, 未逾期, 正常状态, 清除状态, clear state, clear, not overdue, __KILLBILL__CLEAR__OVERDUE_STATE__
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:51`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:37`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:42-52`

**含义**：内建的特殊状态，常量名为 `__KILLBILL__CLEAR__OVERDUE_STATE__`（`OverdueWrapper.CLEAR_STATE_NAME`），由状态集的 `clearState` 提供（`isClearState=true`）。当没有任何配置状态的条件命中时返回它；账户的 blocking state 不存在时也默认按 clear 处理。`findState` 对该名字特判返回内建 clearState。

## TERM-017 计费状态（BillingState）

- **类型**: 术语
- **同义词**: 计费状态, 账单状态, 欠费快照, billing state, billing snapshot, unpaid invoice summary
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `api/src/main/java/org/killbill/billing/overdue/config/api/BillingState.java:29-53`, `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:67-84`

**含义**：评估逾期条件所依据的账户级事实快照，字段：`objectId`、`numberOfUnpaidInvoices`、`balanceOfUnpaidInvoices`（未付发票余额合计）、`dateOfEarliestUnpaidInvoice`、`idOfEarliestUnpaidInvoice`、`responseForLastFailedPayment`、`tags`。由 `BillingStateCalculator.calculateBillingState` 计算。

## TERM-018 重新评估间隔（Reevaluation Interval）

- **类型**: 术语
- **同义词**: 重新评估间隔, 重估间隔, 复评间隔, 催收定时, 下次检查时间, reevaluation interval, autoReevaluationInterval, initialReevaluationInterval, dunning poll interval
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:71-72`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:119-125`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:35-36`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:51-57`

**含义**：控制「多久后再自动评估一次该账户逾期状态」的两个配置：
1. `autoReevaluationInterval`：每个状态上的属性（`DefaultDuration`），用于非 clear 状态——进入该状态后按此间隔安排下一次检查。
2. `initialReevaluationInterval`：账户状态集级别（`accountOverdueStates` 下），用于 clear 状态/尚未进入首状态时的轮询间隔。
非法值（null、`UNLIMITED`、number=0）分别导致抛 `OVERDUE_NO_REEVALUATION_INTERVAL`（非 clear）或返回 null（不安排通知）。

## TERM-019 阻止变更（blockChanges）

- **类型**: 术语
- **同义词**: 阻止变更, 禁止修改, 冻结账户修改, block changes, isBlockChanges, blockChange
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:59-60`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:104-107`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:263-265`

**含义**：状态动作之一。若为 true，施加的 BlockingState 的 `blockChange=true`，阻止该账户上的变更类操作。当 `disableEntitlementAndChangesBlocked=true` 时，即使 `blockChanges=false` 也会强制 block changes（见 BR-119）。

## TERM-020 禁用权益并阻止变更（disableEntitlementAndChangesBlocked）

- **类型**: 术语
- **同义词**: 暂停订阅, 停用权益, 禁用服务, 阻断计费, 暂停服务, disableEntitlement, disableEntitlementAndChangesBlocked, suspend entitlement, block billing
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:62-63`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:263-273`

**含义**：状态动作之一。若为 true，施加的 BlockingState 同时设置 `blockEntitlement=true`、`blockBilling=true`（并隐含 `blockChange=true`），效果是**暂停/停用该账户权益并停止计费**（pause 语义）。恢复（resume）发生在状态回落为不 block billing 时（见 BR-121）。

## TERM-021 外部消息（externalMessage）

- **类型**: 术语
- **同义词**: 外部消息, 提示文案, 催收提示, 用户提示语, external message, externalMessage, dunning message
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:56-57`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:99-102`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:141-144`

**含义**：状态上的可读文案（默认空字符串），随状态一起暴露给上层/API（例如 OverdueStateConfigJson 输出），用于向用户展示「已进入某催收阶段」的提示。它不直接触发任何动作。

## TERM-022 逾期强制关闭标签（OVERDUE_ENFORCEMENT_OFF）

- **类型**: 术语
- **同义词**: 关闭催收, 停止催收, 豁免催收, 逾期豁免, 免催收标签, OVERDUE_ENFORCEMENT_OFF, overdue enforcement off, disable dunning
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:334-349`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-108`

**含义**：账户级控制标签。存在该标签时：`refresh` 直接跳过（不评估、不改状态，见 `refreshWithLock` 调用点）；且给账户打上该标签的事件会以 `CLEAR` 动作入队，从而清除该账户的逾期状态。它也是条件 `controlTagInclusion/Exclusion` 可用的控制标签之一。

## TERM-023 自动开票关闭标签（AUTO_INVOICING_OFF）

- **类型**: 术语
- **同义词**: 关闭自动开票, 停止开票, 暂停出账, 停止生成发票, AUTO_INVOICING_OFF, auto invoicing off, AUTO_INVOICE_OFF
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:176-183`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:237-253`

**含义**：账户级控制标签。overdue 不会由用户直接配置它，而是**自动维护**：当状态从「不 block billing」变为「block billing」时自动打上，避免继续产生额外发票/信用；当从 block billing 回落时自动移除。见 BR-121。

## TERM-024 发票核销标签（WRITTEN_OFF）

- **类型**: 术语
- **同义词**: 发票核销, 坏账核销, 注销发票, WRITTEN_OFF, written off, write-off
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:103-106`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:114-119`

**含义**：发票级控制标签。给发票打/摘该标签会触发对应账户的逾期重新评估（REFRESH）：监听器先由事件反查所属账户，再入队。它解释了「核销一张未付发票会改变逾期状态」的业务语义。

## TERM-025 订阅取消策略（subscriptionCancellationPolicy）

- **类型**: 术语
- **同义词**: 订阅取消策略, 逾期取消订阅, 自动退订, 终止订阅策略, subscription cancellation policy, OverdueCancellationPolicy, IMMEDIATE, END_OF_TERM, NONE
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:65-66`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:285-302`

**含义**：状态动作之一，枚举 `OverdueCancellationPolicy`，取值 `NONE`（默认，不取消）、`IMMEDIATE`（立即取消）、`END_OF_TERM`（到期取消）。进入状态时若不为 NONE，会把账户下所有非 ADD_ON 的订阅按对应 BillingActionPolicy 取消（见 BR-120）。

## TERM-026 租户级逾期配置（tenant-level overdue config）

- **类型**: 术语
- **同义词**: 租户逾期配置, 多租户催收配置, 上传逾期配置, tenant overdue config, OVERDUE_CONFIG, overdue config upload
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:66-89`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:93-106`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:108-113`

**含义**：逾期规则可**按租户**分别配置。上传的 XML 存到租户 KV 键 `OVERDUE_CONFIG`（`TenantKey.OVERDUE_CONFIG`），并缓存于 `CacheType.TENANT_OVERDUE_CONFIG`（键为 tenantRecordId）。租户无自定义配置时回退到默认配置；内部租户记录（`INTERNAL_TENANT_RECORD_ID`）始终使用默认配置。

## TERM-027 逾期状态配置元素全集（XML 名称 / 默认值 / 可空性）

- **类型**: 术语
- **同义词**: 状态配置元素, 状态字段, 状态XML映射, state configuration elements, DefaultOverdueState fields, state defaults, overdue state schema
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:49-76`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:99-125`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:247-272`

**含义**：一个 `<state>` 配置元素可携带的全部字段（Java 字段名 / XML 名 / 必需性 / 默认值）：

| Java 字段 | XML 元素/属性 | 必需 | 默认值 |
|---|---|---|---|
| `name` | `name`（**属性**） | 是 | 无（必填） |
| `condition` | `condition` | 否 | `null`（无子条件） |
| `externalMessage` | `externalMessage` | 否 | `""`（空字符串） |
| `blockChanges` | `blockChanges` | 否 | `false` |
| `disableEntitlement` | `disableEntitlementAndChangesBlocked` | 否 | `false` |
| `subscriptionCancellationPolicy` | `subscriptionCancellationPolicy` | 否 | `NONE` |
| `isClearState` | `isClearState` | 否 | `false` |
| `autoReevaluationInterval` | `autoReevaluationInterval` | 否 | `null` |
| `enterStateEmailNotification` | `enterStateEmailNotification` | 否 | `null`（**已废弃**） |

**注意（反直觉命名）**：Java 私有字段叫 `disableEntitlement`，但 XML 元素名是 `disableEntitlementAndChangesBlocked`，对外 getter 是 `isDisableEntitlementAndChangesBlocked()`。
**注意（序列化缺口）**：`writeExternal`（247-260）**不写出** `enterStateEmailNotification`，该方法只序列化 condition/name/externalMessage/blockChanges/disableEntitlement/cancellationPolicy/isClearState/autoReevaluationInterval；`readExternal` 也不读它。即废弃的邮件通知字段在 Externalizable 往返中会丢失。

## TERM-028 时长配置 DefaultDuration：unit/number 语义与 -1 默认陷阱

- **类型**: 术语
- **同义词**: 时长单位, 时长度量, 时间间隔配置, DefaultDuration, duration unit, number default -1, TimeUnit DAYS WEEKS MONTHS YEARS, UNLIMITED
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:41-55`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:79-118`

**含义**：`DefaultDuration` 由两个子元素组成：
- `unit`（`@XmlElement(required = true)`）：`TimeUnit` 枚举，缺省无值（null）。
- `number`（`@XmlElement(required = false)`）：**Java 默认值是 `-1`，不是 null**（第 45 行）。仅当外部显式反序列化写入 null 时才可能是 null。

**`number = -1` 的影响**：`toJodaPeriod()` / `addToLocalDate()` / `addToDateTime()` 对 `DAYS/WEEKS/MONTHS/YEARS` 直接执行 `withDays(-1)` 等，产生**负一天**的周期；只有当 `number == null && unit != UNLIMITED` 时才返回恒等周期 `new Period()`（102 行）。
**UNLIMITED 的语义**：`toJodaPeriod()`/`addToLocalDate()`/`addToDateTime()` 遇到 `UNLIMITED` **抛 `IllegalStateException("Unexpected duration unit")`**（74/95/116 行）。`validate()` 只有一个 TODO、不做任何校验（121-124 行）。

## TERM-029 内建清算状态对象（Built-in Clear State）与保留名

- **类型**: 术语
- **同义词**: 内建清算状态, 清算状态对象, 保留状态名, built-in clear state, __KILLBILL__CLEAR__OVERDUE_STATE__, reserved state name, clearState field
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:35-57`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:51`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:49-76`

**含义**：状态集内部**始终持有一个独立的内建 clearState 对象**（`DefaultOverdueStateSet.java:37`），它是 `new DefaultOverdueState().setName(CLEAR_STATE_NAME).setClearState(true)`：
- 名字固定为 `__KILLBILL__CLEAR__OVERDUE_STATE__`（`OverdueWrapper.CLEAR_STATE_NAME`）。
- `isClearState=true`；其余字段取其默认值（condition=null，externalMessage=""，blockChanges=false，disableEntitlement=false，cancellationPolicy=NONE，autoReevaluationInterval=null）。
- `getClearState()` **无条件返回这个内建对象**（55-57 行），从不抛异常。
- `findState(CLEAR_STATE_NAME)` 在遍历配置状态**之前**特判返回该内建对象（41-45 行）。
**推论**：任何用户配置的 `<state name="__KILLBILL__CLEAR__OVERDUE_STATE__">` 永远不会被 `findState` 命中（被特判短路）；这是**保留状态名**。

## TERM-030 订阅取消策略枚举 OverdueCancellationPolicy

- **类型**: 术语
- **同义词**: 取消策略枚举, 订阅取消策略取值, OverdueCancellationPolicy, NONE, IMMEDIATE, END_OF_TERM, subscription cancellation policy
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:65-66`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:285-314`

**含义**：状态动作 `subscriptionCancellationPolicy` 的取值枚举：
- `NONE` — 默认值，不取消任何订阅（applicator 286-288 直接 return）。
- `IMMEDIATE` — 立即取消，映射为 `BillingActionPolicy.IMMEDIATE`。
- `END_OF_TERM` — 到期取消，映射为 `BillingActionPolicy.END_OF_TERM`。
- 其他值 — applicator 的 `default` 分支抛 `IllegalStateException("Unexpected OverdueCancellationPolicy ...")`（300-301 行）。
**作用条件**：该动作**只在状态名发生变化时**才会执行（见 BR-153 的 no-op 短路），并且取消列表先经 BR-160 的范围过滤。

## TERM-031 两个同名的 OverdueConfig（XML 配置对象 vs 属性/多租户接口）

- **类型**: 术语
- **同义词**: OverdueConfig 命名冲突, 配置对象与属性接口, two OverdueConfig types, org.killbill.billing.overdue.api.OverdueConfig, util.config.definition.OverdueConfig, MultiTenantOverdueConfig
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueConfig.java:35-52`, `overdue/src/main/java/org/killbill/billing/overdue/config/MultiTenantOverdueConfig.java:34-47`, `overdue/src/main/java/org/killbill/billing/overdue/glue/DefaultOverdueModule.java:82-88`

**含义**：代码里有两个不同包下的 `OverdueConfig`，容易混淆：
1. **XML 配置对象** `org.killbill.billing.overdue.api.OverdueConfig`：由 `DefaultOverdueConfig` 实现，`@XmlRootElement(name="overdueConfig")`，承载 `<accountOverdueStates>`；也就是租户上传/缓存的业务规则。
2. **属性接口** `org.killbill.billing.util.config.definition.OverdueConfig`：由 `MultiTenantOverdueConfig` 实现（继承 `MultiTenantLockAwareConfigBase`），用于从 killbill 配置提供 `getRescheduleIntervalOnLock(context)` 等运行时属性，并作为 `@Named(STATIC_CONFIG)` 的静态来源。
**绑定关系**：`DefaultOverdueModule.installConfig()` 把静态 `OverdueConfig` 绑定为 `STATIC_CONFIG`，再把无注解的 `OverdueConfig` 绑定到 `MultiTenantOverdueConfig`（82-88 行）。两个同名字符串常量跨包引用，是本模块最易踩坑处之一。

## TERM-032 逾期变更事件 OverdueChangeInternalEvent 字段与转移布尔

- **类型**: 术语
- **同义词**: 逾期变更事件字段, 事件布尔, blocked billing, unblocked billing, OverdueChangeInternalEvent, isBlockedBilling, isUnblockedBilling, OVERDUE_CHANGE
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/DefaultOverdueChangeEvent.java:28-58`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/DefaultOverdueChangeEvent.java:75-85`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:255-261`

**含义**：事件字段与 JSON 名：
- `overdueObjectId`（账户 id）、`previousOverdueStateName`、`nextOverdueStateName`、`isBlockedBilling`、`isUnblockedBilling`；`getBusEventType()==OVERDUE_CHANGE`。
- Jackson 序列化时 `isBlockedBilling`/`isUnblockedBilling` 通过 `@JsonProperty` 显式命名（75-85 行）。
**两个布尔的精确语义**（applicator 255-261）：
- `isBlockedBilling = !blockBilling(prev) && blockBilling(next)`（从「不 block 计费」→「block 计费」转移）。
- `isUnblockedBilling = blockBilling(prev) && !blockBilling(next)`（反向转移）。
- 其中 `blockBilling(s) = s.isDisableEntitlementAndChangesBlocked()`。
**互斥性**：二者**不可能同时为真**（布尔互斥），但**可以同时为假**（例如仅 blockChanges 变化、或两个状态都 block billing）。

## TERM-033 计划 (Plan)

- **类型**: 术语
- **同义词**: 计划, 套餐, 资费计划, 产品计划, 订阅计划, plan, Plan, product plan, subscription plan
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:61-97`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:199-237`

**含义**：Plan 是订阅实际购买/切换的单位。每个 Plan 绑定一个 Product（产品），包含若干 `initialPhases`（起始阶段，可为空）与**恰好一个** `finalPhase`（最终阶段），并归属到某个价格表（`priceListName`）。

**关键字段**：`name`（唯一 ID）、`prettyName`（展示名，缺省=name）、`product`、`recurringBillingMode`、`plansAllowedInBundle`、`effectiveDateForExistingSubscriptions`。

**说明**：`getAllPhases()` 返回 = initialPhases + finalPhase；`getRecurringBillingPeriod()` 取 finalPhase 的 recurring 周期，若 finalPhase 无 recurring 则返回 `NO_BILLING_PERIOD`。

## TERM-034 计划阶段 (Plan Phase)

- **类型**: 术语
- **同义词**: 阶段, 计费阶段, 试用期, 优惠期, phase, plan phase, PlanPhase, billing phase
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:52-102`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:104-115`

**含义**：PlanPhase 是 Plan 内部按时间顺序排列的计费阶段，每个阶段有 `type`（PhaseType）、`duration`（时长）、可选的 `fixed`（一次性固定费）、`recurring`（周期性费用）和 `usages`（用量计费）。

**命名规则**：阶段名由计划名 + 阶段类型小写拼成：`phaseName = planName + "-" + phaseType.toLowerCase()`（例如 `foo-trial`、`foo-evergreen`）。

## TERM-035 产品 (Product)

- **类型**: 术语
- **同义词**: 产品, 商品, 产品定义, product, Product, catalog product
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:47-73`

**含义**：Product 是目录中的顶层可售对象，拥有 `name`、`category`（产品类别）、`included`（随主产品一起购买的附加产品集合）、`available`（可单独购买的附加产品集合）和 `limits`（用量限制）。

## TERM-036 产品类别 (Product Category)

- **类型**: 术语
- **同义词**: 产品类别, 产品类型, BASE, ADD_ON, STANDALONE, 主产品, 附加产品, 独立产品, base product, add-on, standalone product, product category
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:58-59`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:128-138`

**含义**：`ProductCategory` 取值 `BASE`（基础/主产品）、`ADD_ON`（附加产品）、`STANDALONE`（独立产品）。它决定产品在 bundle 中的组合方式：ADD_ON 需挂在 BASE 上，STANDALONE 不与其他产品组合。

**约束线索**：`plansAllowedInBundle` 注释明确 BASE 计划只允许值 1、Tiered ADDON 也只允许值 1（见 ENT-033 与此处引用）。

## TERM-037 价格表 (Price List)

- **类型**: 术语
- **同义词**: 价格表, 价目表, 定价方案, 价格清单, price list, pricelist, PriceList, price plan
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceList.java:47-68`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:47-53`

**含义**：PriceList 是一组 Plan 的集合，允许同一产品/计费周期在不同价格表下有不同的价格（如默认价、促销价）。目录中有一个 `defaultPriceList`（默认价格表）和若干 `childPriceList`（子价格表）。

**保留名**：默认价格表的名称固定为 `DEFAULT`（`PriceListSet.DEFAULT_PRICELIST_NAME`），子价格表不得使用该名。

## TERM-038 计费周期 (Billing Period)

- **类型**: 术语
- **同义词**: 计费周期, 账单周期, 月付, 年付, billing period, BillingPeriod, recurring period, NO_BILLING_PERIOD
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:234-237`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:295-298`

**含义**：`BillingPeriod` 表示 recurring 费用的收费频率。计划层面的周期取自 finalPhase 的 recurring；若 finalPhase 没有 recurring，计划周期为 `NO_BILLING_PERIOD`（纯用量/一次性计划）。

## TERM-039 阶段类型 (Phase Type)

- **类型**: 术语
- **同义词**: 阶段类型, 试用, 试用期, 折扣期, 固定期限, 长期, phase type, PhaseType, TRIAL, DISCOUNT, FIXEDTERM, EVERGREEN
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:304-319`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:108-115`

**含义**：`PhaseType` 取值 `TRIAL`（试用）、`DISCOUNT`（折扣）、`FIXEDTERM`（固定期限）、`EVERGREEN`（长期/常青）。阶段名后缀即其小写形式（如 `-trial`、`-evergreen`），因此可通过阶段名反推计划名与类型。

## TERM-040 计费模式 (Billing Mode)

- **类型**: 术语
- **同义词**: 计费模式, 预付, 后付, 先付, 后付费, billing mode, BillingMode, IN_ADVANCE, IN_ARREAR
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:65-66`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:79-81`

**含义**：`BillingMode` 取值 `IN_ADVANCE`（先付/预付）与 `IN_ARREAR`（后付/后付费）。可用量计费（usage）维度与计划级别 recurring 维度分别声明；计划若缺省则继承目录级 `recurringBillingMode`。

## TERM-041 用量计费 (Usage)

- **类型**: 术语
- **同义词**: 用量计费, 按量计费, 使用量, 计量计费, usage, usage-based billing, metered usage, Usage
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:56-95`

**含义**：Usage 是阶段内的用量计费段，包含 `billingMode`（IN_ADVANCE/IN_ARREAR）、`usageType`（CONSUMABLE/CAPACITY）、`tierBlockPolicy`、`billingPeriod`，以及 `limits`、`blocks`、`tiers`、可选的整段 `fixedPrice`/`recurringPrice`。

## TERM-042 用量类型 (Usage Type)

- **类型**: 术语
- **同义词**: 用量类型, 消耗型, 容量型, consumable, capacity, usage type, UsageType
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:212-229`

**含义**：`UsageType.CONSUMABLE` 表示按使用量累加计费（用多少算多少）；`UsageType.CAPACITY` 表示按容量/上限计费。校验规则要求 IN_ADVANCE+CAPACITY 必须定义 limits、IN_ADVANCE+CONSUMABLE 必须定义 blocks。

## TERM-043 分层 (Tier)

- **类型**: 术语
- **同义词**: 分层, 阶梯, 阶梯价, 分层计价, tier, tiered pricing, Tier, pricing tier
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:45-62`

**含义**：Tier 是 usage 定价的阶梯，每个 Tier 有 `limits`、`blocks`（tieredBlock 列表）以及可选的整段 `fixedPrice`/`recurringPrice`。IN_ARREAR 的 usage 必须定义 tiers。

## TERM-044 限制 (Limit)

- **类型**: 术语
- **同义词**: 限制, 上限, 下限, 用量上限, limit, cap, min, max, usage limit
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultLimit.java:42-105`

**含义**：Limit 由 `unit`（单位）+ `min`/`max` 组成，用来约束用量或容量。`compliesWith(value)` 判定：若 max 有效且 value>max 则不通过；若 min 有效且 value>min 也不通过（注意源码此处为 `> min` 判断，见 BR 卡）。

## TERM-045 计费对齐 (Billing Alignment)

- **类型**: 术语
- **同义词**: 计费对齐, 账单日对齐, 对齐方式, 账户对齐, 订阅对齐, 账单对齐, billing alignment, BillingAlignment, ACCOUNT, SUBSCRIPTION, BUNDLE
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:137-141`, `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:50-72`

**含义**：`BillingAlignment` 决定订阅的账单日（BCD）如何对齐，取值 `ACCOUNT`（对齐账户 BCD）、`SUBSCRIPTION`（对齐订阅自身起始日）、`BUNDLE`（对齐 bundle 内基础订阅的 BCD）。目录中通过 `billingAlignment` 规则按产品/类别/周期/价格表/阶段类型匹配；未匹配到时默认 `ACCOUNT`。

**注意**：当对齐为 ACCOUNT 但账户 BCD 尚未设置（=0）时，系统会临时回退到 SUBSCRIPTION 推算 BCD（`resolveEffectiveBillingAlignment`）。

## TERM-046 阶梯块策略 (Tier Block Policy)

- **类型**: 术语
- **同义词**: 阶梯策略, 分层策略, 计费阶梯策略, ALL_TIERS, TOP_TIER, tier block policy, TierBlockPolicy
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:71-72`, `invoice/src/test/java/org/killbill/billing/invoice/usage/TestContiguousIntervalConsumableInArrear.java:152-244`

**含义**：`TierBlockPolicy` 决定用量达到多阶梯时如何计价，取值 `ALL_TIERS`（对所有经过的阶梯分别计价）与 `TOP_TIER`（只按最高到达阶梯计价）；测试用例名 `testComputeBilledUsageWith_ALL_TIERS` / `testComputeBilledUsageWith_TOP_TIER` 直接印证这两种策略。

## TERM-047 块类型 (Block Type)

- **类型**: 术语
- **同义词**: 块类型, 用量块类型, 充值块, 阶梯块, VANILLA, TOP_UP, TIERED, block type, BlockType
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:49-50`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:92-110`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTieredBlock.java:62-71`

**含义**：`BlockType` 取值 `VANILLA`（缺省普通块）、`TOP_UP`（充值块，需定义 `minTopUpCredit`）、`TIERED`（阶梯块，来自 DefaultTieredBlock）。对非 TOP_UP 块调用 `getMinTopUpCredit()` 会抛 `CAT_NOT_TOP_UP_BLOCK`。

## TERM-048 价格覆盖 (Price Override)

- **类型**: 术语
- **同义词**: 价格覆盖, 自定义价格, 覆盖定价, 计划价格覆盖, price override, plan price override, fixedPrice override, recurringPrice override
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:83-102`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:57-86`

**含义**：创建订阅时可对计划的阶段价格做覆盖：`PlanPhasePriceOverride` 可覆盖固定费、周期费与各 usage 的阶梯价格。覆盖按币种替换对应 `DefaultPrice`，未覆盖的币种价格保留。

## TERM-049 目录版本 (Catalog Version)

- **类型**: 术语
- **同义词**: 目录版本, 版本, 目录生效日, catalog version, versioned catalog, effective date, 生效日期
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:50-107`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:62-77`

**含义**：一个目录名称下可有多个版本（`StandaloneCatalog`），每个版本有唯一 `effectiveDate`。查询某日期时，取生效日 ≤ 该日期的**最新**版本；若所有版本都晚于查询日期，则返回第一个版本。

## TERM-050 固定费类型 (Fixed Type)

- **类型**: 术语
- **同义词**: 固定费类型, 一次性费用, ONE_TIME, fixed type, FixedType
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultFixed.java:41-55`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultFixed.java:76-82`

**含义**：阶段内的固定费（`Fixed`）带一个 `FixedType type`，缺省为 `ONE_TIME`（一次性收费）；其价格来自 `fixedPrice`（InternationalPrice，多币种）。

## TERM-051 账单日 (BCD / Bill Cycle Day)

- **类型**: 术语
- **同义词**: 账单日, 计费日, 出账日, 出账日期, BCD, bill cycle day, billing cycle day, 每月几号出账
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:35-88`, `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:133-139`

**含义**：BCD 是订阅每月出账的「日」，由订阅 `getDateOfFirstRecurringNonZeroCharge()`（首个非零周期费日期）的当月日号决定，或按计费对齐规则取账户/bundle/订阅的 BCD。

**对齐规则**：仅对「以月/年为单位」的计费周期（MONTHLY/QUARTERLY/BIANNUAL/ANNUAL）做 BCD 对齐；若 BCD 大于当月天数，取**当月最后一天**。

## TERM-052 计费动作策略 (BillingActionPolicy)

- **类型**: 术语
- **同义词**: 计费动作策略, 变更策略, 取消策略, 立即生效, 期末生效, IMMEDIATE, END_OF_TERM, billing action policy
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:131-135`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:172-176`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:332-344`

**含义**：计划变更/取消时的计费动作策略，取值 `IMMEDIATE`（立即生效）与 `END_OF_TERM`（期末生效）。目录规则未匹配时默认 `END_OF_TERM`；简化计划 API 生成的默认规则使用 `IMMEDIATE`。

## TERM-053 简化计划描述符 (SimplePlanDescriptor)

- **类型**: 术语
- **同义词**: 简化计划, 计划描述符, simple plan, SimplePlanDescriptor, 快速建计划
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:119-161`, `catalog/src/main/java/org/killbill/billing/catalog/api/user/DefaultSimplePlanDescriptor.java:29-39`

**含义**：`SimplePlanDescriptor` 是创建/更新「简化计划」的输入模型，包含 planId、productName、productCategory、billingPeriod、currency、amount、可选 trial 信息（trialLength/trialTimeUnit）以及 ADD_ON 的 availableBaseProducts。

## TERM-054 时长单位 TimeUnit 全枚举与 addToDateTime 映射

- **类型**: 术语
- **同义词**: 时长单位, 时间单位, 天, 周, 月, 年, 无限期, duration unit, TimeUnit, DAYS, WEEKS, MONTHS, YEARS, UNLIMITED
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultDuration.java:64-104`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultDuration.java:106-123`

**枚举取值（5 个）**：`DAYS`（天）、`WEEKS`（周）、`MONTHS`（月）、`YEARS`（年）、`UNLIMITED`（无限期）。

**加日期映射**（`addToDateTime` / `addToLocalDate` 完全一致）：
- `DAYS` → `plusDays(number)`；`WEEKS` → `plusWeeks(number)`；`MONTHS` → `plusMonths(number)`；`YEARS` → `plusYears(number)`。
- `UNLIMITED`（或任何未列出的值，走 `default`）→ 抛 `CatalogApiException(CAT_UNDEFINED_DURATION)`。

**特例**：当 `number == null` 且 `unit != UNLIMITED` 时，`addToDateTime`/`addToLocalDate`/`toJodaPeriod` 直接返回原日期/空 Period（不报错）；`toJodaPeriod()` 对 `UNLIMITED` 抛 `IllegalStateException("Unexpected duration unit UNLIMITED")`。

**校验**：`UNLIMITED` 必须省略 `number`（-1），否则报 `Duration can only have 'UNLIMITED' unit if the number is omitted`；非 `UNLIMITED` 必须给出 `number`，否则报 `Finite Duration must have a well defined length`。

## TERM-055 PhaseType 全枚举与「阶段名后缀」强耦合

- **类型**: 术语
- **同义词**: 阶段类型, 试用, 折扣, 固定期限, 常青, phase type, PhaseType, TRIAL, DISCOUNT, FIXEDTERM, EVERGREEN, 阶段名后缀
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:104-115`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:304-319`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:290-310`

**枚举取值（4 个）**：`TRIAL`（试用）、`DISCOUNT`（折扣）、`FIXEDTERM`（固定期限）、`EVERGREEN`（常青/长期）。

**值 → 位置/时长合法矩阵**（由 `DefaultPlan.validate` + `StandaloneCatalog.validatePlanDuration` 共同决定）：
- `TRIAL`：可作初始阶段；**不得**作最终阶段；时长必须有限（非 UNLIMITED）。
- `DISCOUNT`：可作初始阶段；**不得**作最终阶段；时长必须有限。
- `FIXEDTERM`：可作初始或最终阶段；时长必须有限。
- `EVERGREEN`：**不得**作初始阶段；通常作最终阶段；时长**必须** `UNLIMITED`。

**命名耦合**：阶段名 = `planName + "-" + phaseType.toLowerCase()`；反解时按 `PhaseType.values()` 的**声明顺序**遍历，阶段名以某类型小写结尾即命中，截取 `length - type长度 - 1`。因此若计划名本身以 `trial/discount/fixedterm/evergreen` 结尾，反解会产生歧义（取 values() 顺序中第一个匹配者）。

## TERM-056 计费周期 BillingPeriod 枚举（catalog 内可证取值）

- **类型**: 术语
- **同义词**: 计费周期, 收费频率, 月付, 季付, 年付, 无周期, billing period, BillingPeriod, NO_BILLING_PERIOD, MONTHLY
- **模块**: catalog
- **置信度**: 🟡 inferred
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:234-237`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultRecurring.java:90-111`, `catalog/src/main/resources/EmptyCatalog.xml:53-64`

**catalog 源码中实际引用到的取值**：
- `NO_BILLING_PERIOD`：无周期（纯用量/一次性计划）。`DefaultPlan.getRecurringBillingPeriod()` 在 finalPhase 无 recurring 时返回它。
- `MONTHLY`：在 `EmptyCatalog.xml` 的 `<billingPeriod>MONTHLY</billingPeriod>` 中作为合法值出现。

**推断取值（🟡，未在 catalog 源码出现，源自 killbill-api 外部构件）**：`DAILY`、`WEEKLY`、`MONTHLY`、`QUARTERLY`、`BIANNUAL`、`ANNUAL`、`NO_BILLING_PERIOD`。

**关键校验**：`DefaultRecurring` 要求「有 recurringPrice ⇒ billingPeriod 存在且 ≠ NO_BILLING_PERIOD」「无 recurringPrice ⇒ billingPeriod 必须是 NO_BILLING_PERIOD」，否则目录校验失败。

## TERM-057 计费模式 BillingMode 枚举与「各模式必填结构」摘要

- **类型**: 术语
- **同义词**: 计费模式, 预付, 后付, 先付, billing mode, BillingMode, IN_ADVANCE, IN_ARREAR
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:212-229`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:147-159`

**枚举取值（2 个）**：`IN_ADVANCE`（先付/预付）、`IN_ARREAR`（后付/后付费）。

**在 usage 段的条件校验**（`DefaultUsage.validate`）：
- `IN_ADVANCE + CAPACITY` 且 `limits.length == 0` → 报 `Usage [IN_ADVANCE CAPACITY] section of phase ... needs to define some limits`。
- `IN_ADVANCE + CONSUMABLE` 且 `blocks.length == 0` → 报 `Usage [IN_ADVANCE CONSUMABLE] section of phase ... needs to define some blocks`。
- `IN_ARREAR` 且 `tiers.length == 0` → 报 `Usage [IN_ARREAR] section of phase ... needs to define some tiers`。

**在 tier 段的条件校验**（`DefaultTier.validate`，错误信息类名仍挂 `DefaultUsage`）：`IN_ARREAR + CAPACITY` 需 limits；`IN_ARREAR + CONSUMABLE` 需 blocks。

**继承**：计划的 `recurringBillingMode` 可缺省，initialize 时回退到目录级 `StandaloneCatalog.recurringBillingMode`。

## TERM-058 用量类型 UsageType 枚举与语义

- **类型**: 术语
- **同义词**: 用量类型, 消耗型, 容量型, usage type, UsageType, CONSUMABLE, CAPACITY
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:212-229`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:147-159`

**枚举取值（2 个）**：
- `CAPACITY`（容量型）：按容量/上限计费。与 `IN_ADVANCE` 组合时必须提供 `limits`；与 `IN_ARREAR` 组合时 tier 必须提供 `limits`。
- `CONSUMABLE`（消耗型）：按累计使用量计费。与 `IN_ADVANCE` 组合时必须提供 `blocks`；与 `IN_ARREAR` 组合时 tier 必须提供 `blocks`。

**判定顺序**：`DefaultUsage.validate` 先做 billingMode/usageType 组合校验，再对 `limits` 与 `tiers` 递归 `validateCollection`；`DefaultTier.validate` 再做 tier 级别同组合校验。

## TERM-059 块类型 BlockType 枚举与 minTopUpCredit 语义

- **类型**: 术语
- **同义词**: 块类型, 用量块类型, 充值块, 阶梯块, block type, BlockType, VANILLA, TOP_UP, TIERED, minTopUpCredit
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:49-50`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:91-111`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTieredBlock.java:51-65`

**枚举取值（3 个）**：
- `VANILLA`：普通块，**缺省值**（`DefaultBlock.type` 初始即 `BlockType.VANILLA`，`CatalogSafetyInitializer` 对 null 也回填 VANILLA）。
- `TOP_UP`：充值块，必须定义 `minTopUpCredit`。
- `TIERED`：阶梯块，由 `DefaultTieredBlock` 固定返回（`getType()` 恒 `TIERED`，`setType` 被强制覆盖为 `TIERED`）。

**关键行为**：
- `DefaultBlock.validate`：`type == TOP_UP && !minTopUpCreditHasValue` → 报 `TOP_UP block needs to define minTopUpCredit for phase ...`；`type == null` → 抛 `IllegalStateException`（安全网）。
- `minTopUpCreditHasValue` 在 `initialize` 中确定：`minTopUpCredit != null && minTopUpCredit != -1`（-1 为「未设置」哨兵值）。
- 对**非** TOP_UP 块调用 `getMinTopUpCredit()` 会抛 `CatalogApiException(CAT_NOT_TOP_UP_BLOCK)`。

## TERM-060 固定费类型 FixedType 枚举

- **类型**: 术语
- **同义词**: 固定费类型, 一次性费用, fixed type, FixedType, ONE_TIME
- **模块**: catalog
- **置信度**: 🟡 inferred
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultFixed.java:41-45`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultFixed.java:75-82`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogSafetyInitializer.java:58-65`

**catalog 源码中实际引用到的取值**：
- `ONE_TIME`（一次性收费）：`Fixed.type` 的缺省值；`CatalogSafetyInitializer` 对 null 的 FixedType 字段回填 `FixedType.ONE_TIME`；`DefaultFixed.validate` 若 type 仍为 null 抛 `IllegalStateException("fixedPrice should have been automatically been initialized with ONE_TIME")`。

**推断**：FixedType 是 killbill-api 中的独立枚举（🟡）；catalog 源码未引用 `ONE_TIME` 之外的取值，故无法从本模块确认是否存在其它取值。

**价格载体**：固定费金额来自 `fixedPrice`（`InternationalPrice`，多币种）；固定费可为 null（阶段可不含 fixed）。

## TERM-061 BillingActionPolicy 全枚举（变更/取消策略）

- **类型**: 术语
- **同义词**: 计费动作策略, 变更策略, 取消策略, 立即, 期末, 期初, 禁止, billing action policy, BillingActionPolicy, IMMEDIATE, END_OF_TERM, START_OF_TERM, ILLEGAL
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:131-176`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCaseCancelPolicy.java:51-57`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:334-344`

**catalog 源码中实际引用到的取值（4 个）**：
- `IMMEDIATE`：立即生效。简化计划默认规则使用（`CatalogUpdater` 第 336/344 行），`EmptyCatalog.xml` 的 change/cancel 策略也是 IMMEDIATE。
- `END_OF_TERM`：期末生效。变更/取消规则未命中时的默认值（`DefaultPlanRules` 第 134/175 行）。
- `ILLEGAL`：禁止。变更策略解析为 ILLEGAL 时抛 `IllegalPlanChange`（第 157-159 行）。
- `START_OF_TERM`：期初生效。**默认目录中未实现**：`DefaultCaseCancelPolicy.validate` 明确报错 `Default catalog START_OF_TERM has not been implemented, such policy can be used during cancellation by overriding policy`。

**用途区分**：变更策略用 `DefaultCaseChange`（匹配 from/to 两组字段）；取消策略用 `DefaultCasePhase`（匹配 phaseType + product/category/period/priceList）。

## TERM-062 计划对齐枚举 PlanAlignmentCreate / PlanAlignmentChange

- **类型**: 术语
- **同义词**: 计划创建对齐, 计划变更对齐, 计划生效对齐, plan alignment, PlanAlignmentCreate, PlanAlignmentChange, START_OF_BUNDLE
- **模块**: catalog
- **置信度**: 🟡 inferred
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:125-129`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:166-170`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:338-348`

**catalog 源码中实际引用到的取值**：`START_OF_BUNDLE`（在 bundle 起始日对齐）。
- 创建对齐：`getPlanCreateAlignment` 未命中规则 → 默认 `PlanAlignmentCreate.START_OF_BUNDLE`。
- 变更对齐：`getPlanChangeAlignment` 未命中规则 → 默认 `PlanAlignmentChange.START_OF_BUNDLE`。
- 简化计划默认规则同样使用 `START_OF_BUNDLE`。

**推断（🟡）**：这是两个**独立**枚举类型；catalog 源码只引用了 `START_OF_BUNDLE` 一个取值，是否存在其它取值（如 END_OF_BUNDLE / CHANGE_BACK）无法从本模块确定。

## TERM-063 计费对齐 BillingAlignment 全枚举与回退

- **类型**: 术语
- **同义词**: 计费对齐, 账单日对齐, 账户对齐, 订阅对齐, bundle 对齐, billing alignment, BillingAlignment, ACCOUNT, SUBSCRIPTION, BUNDLE
- **模块**: catalog
- **置信度**: 🟡 inferred
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:137-141`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCasePhase.java:43-49`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:350-352`

**catalog 源码中实际引用到的取值**：
- `ACCOUNT`（对齐账户 BCD）：`getBillingAlignment` 未命中规则时的默认值；简化计划默认规则也设为 `ACCOUNT`。

**推断取值（🟡，未在 catalog 源码出现，kb2 TERM-045 已据 util/invoice 证据列出）**：`SUBSCRIPTION`（对齐订阅自身起始日）、`BUNDLE`（对齐 bundle 内基础订阅 BCD）。

**规则匹配**：`DefaultCaseBillingAlignment` 继承 `DefaultCasePhase`，即按 `phaseType` + `product / productCategory / billingPeriod / priceList` 匹配；每个字段为 null 即通配，一组 case 按声明顺序**首个命中即返回**。

**已知回退**：当对齐为 ACCOUNT 但账户 BCD 尚未建立（=0）时，运行期回退到 SUBSCRIPTION（证据见 kb2 TERM-045/BR-202，本卡不重复）。

## TERM-064 用量单位 Unit

- **类型**: 术语
- **同义词**: 用量单位, 计量单位, 单位, unit, Unit, DefaultUnit, usage unit
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUnit.java:36-71`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:79-81`

**含义**：`Unit` 是目录 `<units>` 下按 `@XmlID` 名称定义的计量单位（如 GB、minutes）。`DefaultUnit` 只有 `name` 与可缺省的 `prettyName`（缺省=name）。

**引用关系**：`Limit.unit`、`Block.unit`、`TieredBlock.unit` 都通过 `@XmlIDREF` 指向目录内的 `DefaultUnit`；因此单位必须先声明后引用。

**校验**：`DefaultUnit.validate` 为空实现（单位本身不校验）；单位是否被正确引用由 XML `@XmlIDREF` 解析阶段保证。

## TERM-065 上架项 Listing

- **类型**: 术语
- **同义词**: 上架项, 可售清单, 列表项, listing, Listing, DefaultListing, 可购计划
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultListing.java:23-42`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:339-382`

**含义**：`Listing` = `(Plan, PriceList)` 二元组，表示「某价格表下可售的某个计划」，是目录对外暴露的「可购买项」。

**产生方式（两种）**：
- `getAvailableBasePlanListings()`：遍历所有计划，仅取产品类别为 `BASE` 者，再在所有价格表中找同名同产品的计划，逐条生成 Listing。
- `getAvailableAddOnListings(baseProductName, priceListName)`：先取该基础产品的 `available` 集合，再对每个计费周期（遍历 `BillingPeriod.values()`）与每个价格表求 `priceList.findPlans(addon, billingPeriod)`；`priceListName` 为 null 时不过滤价格表。

**容错**：`getAvailableAddOnListings` 中若基础产品不存在（`findProduct` 抛异常），捕获后返回空列表。

## TERM-066 阶梯 Tier 的组成

- **类型**: 术语
- **同义词**: 阶梯, 分层, 阶梯定价, 阶梯块列表, tier, Tier, DefaultTier, tieredBlock
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:44-171`

**含义**：`Tier` 是 usage 定价在一个区间内的完整定义，由 `limits[]`（该阶梯适用区间的上下限）、`blocks[]`（`tieredBlock` 列表）、以及可选的**整段** `fixedPrice` / `recurringPrice`（对整段打包计价）组成。

**与 usage 的关系**：`Usage.tiers[]` 承载阶梯；`IN_ARREAR` 的 usage 必须至少有一个 tier（见 TERM-057）。`billingMode` 与 `usageType` 不在 XML 中声明，而是由所属 usage 在 `initialize`/`setPhase` 时注入到 tier（`DefaultTier` 的 `billingMode`/`usageType`/`phase` 均标注为「Not defined in catalog」）。

**校验**：`DefaultTier.validate` 在 `IN_ARREAR+CAPACITY` 且 limits 为空、或 `IN_ARREAR+CONSUMABLE` 且 blocks 为空时报错（错误信息挂在 `DefaultUsage` 上）。

## TERM-067 支付交易类型 (TransactionType)

- **类型**: 术语
- **同义词**: 交易类型, 支付类型, 授权, 捕获, 扣款, 退款, 贷记, 撤销, 拒付, transaction type, AUTH, CAPTURE, PURCHASE, REFUND, CREDIT, VOID, CHARGEBACK
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:121-234`

**定义**：Kill Bill 支付交易共 7 种类型，每种对应一条子状态机与一个 OP_ 操作：

| 类型 | 中文 | 含义 |
|---|---|---|
| `AUTHORIZE` | 授权 | 冻结额度，后续可 CAPTURE 或 VOID |
| `CAPTURE` | 捕获/请款 | 对已授权金额实际扣款 |
| `PURCHASE` | 直接购买/扣款 | 授权+捕获合一 |
| `REFUND` | 退款 | 退回已捕获/购买金额 |
| `CREDIT` | 贷记 | 直接账务贷项（非关联原交易） |
| `VOID` | 撤销 | 作废未捕获的授权 |
| `CHARGEBACK` | 拒付/退单 | 银行侧发起、撤销原扣款 |

## TERM-068 Janitor (支付清理任务)

- **类型**: 术语
- **同义词**: 清洁工, 清理任务, 支付巡检, janitor, payment janitor, incomplete payment task, 未完成支付处理
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/Janitor.java:43-111`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentTransactionTask.java:57-63`

**定义**：Janitor 是 Kill Bill 支付模块后台巡检服务（队列名 `janitor`），负责"修复"处于未完成状态（PENDING / UNKNOWN）的支付交易：向支付插件回查最新交易信息，把本地状态收敛到插件返回的状态。处理范围仅包括 `TransactionStatus.PENDING` 与 `TransactionStatus.UNKNOWN`。另有一个针对控制类支付（invoice payment）的变体 `IncompletePaymentAttemptTask`。

## TERM-069 支付重试 (Payment Retry)

- **类型**: 术语
- **同义词**: 支付重试, 重试, 失败重试, 补扣, payment retry, retry payment, retry schedule
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/retry/DefaultRetryService.java:31-64`, `payment/src/main/java/org/killbill/billing/payment/retry/BaseRetryService.java:70-97`

**定义**：支付失败后由独立的通知队列 `retry` 负责在计划时间点重新发起支付。重试服务名为 `payment-service-retry`（`PAYMENT_SERVICE.getServiceName() + "-" + getQueueName()`），触发时执行 `PluginControlPaymentProcessor.retryPaymentTransaction`。

## TERM-070 AUTO_PAY_OFF（自动支付关闭标签）

- **类型**: 术语
- **同义词**: 自动支付关闭, 停止自动扣款, 关闭自动支付, 暂停代扣, AUTO_PAY_OFF, auto pay off, auto-payoff, disable auto payment
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:376-380`, `payment/src/main/java/org/killbill/billing/payment/invoice/PaymentTagHandler.java:61-77`

**定义**：`AUTO_PAY_OFF` 是账户级控制标签（ControlTagType）。账户打上该标签后，Kill Bill 会停止对发票的自动扣款；当标签被移除时，`PaymentTagHandler` 会订阅标签删除事件并触发 `process_AUTO_PAY_OFF_removal`，把之前被挂起的支付尝试重新排入重试队列。

## TERM-071 MANUAL_PAY（手动支付标签）

- **类型**: 术语
- **同义词**: 手动支付, 手动付款, 人工扣款, MANUAL_PAY, manual pay, manual payment
- **模块**: payment
- **置信度**: 🟡 inferred
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:376-380`

**定义**：与 `AUTO_PAY_OFF` 配套的账户控制标签，用于标记账户需人工发起支付。本次溯源仅在 invoice 控制插件中直接看到 `AUTO_PAY_OFF` 的判定逻辑（`ControlTagType.isAutoPayOff`），`MANUAL_PAY` 的定义在 util 模块的 `ControlTagType` 中，未在本模块代码直接引用，故置信度标为 🟡。

## TERM-072 __EXTERNAL_PAYMENT__（外部支付插件）

- **类型**: 术语
- **同义词**: 外部支付, 线下支付, 手工记录支付, 支票支付, external payment, offline payment, __EXTERNAL_PAYMENT__, 外部支付提供者
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/provider/ExternalPaymentProviderPlugin.java:47-52`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:112-116`

**定义**：`__EXTERNAL_PAYMENT__` 是 Kill Bill 内置的一个特殊支付插件（`ExternalPaymentProviderPlugin.PLUGIN_NAME`），用于记录**不是由 Kill Bill 发起**的支付（如支票等外部到账），其所有操作直接返回 PROCESSED。系统属性 `org.killbill.payment.provider.default` 默认即为 `__external_payment__`。

## TERM-073 支付控制插件 (Payment Control Plugin)

- **类型**: 术语
- **同义词**: 支付控制插件, 控制插件, 支付拦截, payment control plugin, control plugin, __INVOICE_PAYMENT_CONTROL_PLUGIN__
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:87-98`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:130-154`

**定义**：支付控制插件在支付前后提供拦截钩子（`priorCall` 决定是否/以何金额执行，`onSuccessCall` 成功后回调，`onFailureCall` 失败后回调并可返回下次重试日期）。Kill Bill 内置的发票支付控制插件名为 `__INVOICE_PAYMENT_CONTROL_PLUGIN__`（`InvoicePaymentControlPluginApi.PLUGIN_NAME`）。它在 priorCall 中校验发票状态/父账户/余额/AUTO_PAY_OFF/支付方式，并在 onSuccess 中把支付结果回收（reconcile）到发票。

## TERM-074 支付尝试状态（attempt 状态机状态）

- **类型**: 术语
- **同义词**: 支付尝试状态, attempt 状态, INIT, RETRIED, ABORTED, attempt state, 重试状态
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/resources/org/killbill/billing/payment/retry/RetryStates.xml:22-28`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:230-241`

**定义**：控制类支付（invoice payment）的支付尝试状态：
- `INIT`：初始态，表示 attempt 尚未完成；
- `SUCCESS`：重试成功/完成；
- `RETRIED`：本次失败但仍在重试；
- `ABORTED`：终止态（无对应交易等）。

## TERM-075 支付插件状态 PaymentPluginStatus

- **类型**: 术语
- **同义词**: 插件状态, 网关状态, PaymentPluginStatus, PROCESSED, PENDING, ERROR, CANCELED, UNDEFINED, 支付插件返回值
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentTransactionInfoPluginConverter.java:33-56`, `payment/src/main/java/org/killbill/billing/payment/provider/ExternalPaymentProviderPlugin.java:144-158`

**定义**：支付插件返回的状态枚举：`PROCESSED`（成功）、`PENDING`（处理中）、`ERROR`（交易已到网关但被拒，即支付失败）、`CANCELED`（插件确信交易未发生，即插件失败）、`UNDEFINED`/null（结果未知）。映射关系见 BR-239。`DefaultNoOpPaymentInfoPlugin` / `ExternalPaymentProviderPlugin` 使用 `UNDEFINED` 作为缺省。

## TERM-076 发票支付类型 InvoicePaymentType（ATTEMPT / REFUND / CHARGED_BACK）

- **类型**: 术语
- **同义词**: 发票支付类型, 发票支付记录类型, attempt, refund, chargeback, InvoicePaymentType, ATTEMPT, REFUND, CHARGED_BACK
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:168-230`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:665-673`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultInvoicePaymentApi.java:93-178`

**定义**：发票上的支付记录按类型区分：
- `ATTEMPT`：一次扣款尝试（成功或失败），对应一个 purchase 交易；发票余额计算中 ATTEMPT 视为支付入账；
- `REFUND`：退款记录（退款成功后写入，金额为负向影响发票余额）；
- `CHARGED_BACK`：拒付/退单记录（撤销原扣款）。

**退款如何呈现**：一笔退款在支付侧表现为一条 `TransactionType.REFUND` 的 PaymentTransaction，在发票侧表现为一条 `InvoicePaymentType.REFUND` 的 InvoicePayment（通过 `invoiceApi.recordRefund` 写入），支持部分退款（按发票项金额或显式金额，见 BR-236）。

## TERM-077 发票支付控制插件的内部属性契约（IPCD_*）

- **类型**: 术语
- **同义词**: IPCD 属性, 插件属性, IPCD_RETRIES, IPCD_INVOICE_ID, IPCD_REFUND_WITH_ADJUSTMENTS, IPCD_REFUND_IDS_AMOUNTS, IPCD_PAYMENT_ID, plugin properties
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:93-98`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultInvoicePaymentApi.java:200-224`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:266-270`

**定义**：`__INVOICE_PAYMENT_CONTROL_PLUGIN__` 通过 5 个命名常量插件属性（`IPCD_*` = Invoice Payment Control Data）传递调用参数：

| 属性 | 含义 | 缺省行为 |
|---|---|---|
| `IPCD_INVOICE_ID` | 目标发票 id（String→UUID） | 缺失/非 String → 抛错 "Need to specify a valid invoiceId" |
| `IPCD_RETRIES` | 是否允许 API 支付重试 | 缺失/false → API 支付不重试 |
| `IPCD_REFUND_WITH_ADJUSTMENTS` | 退款/贷记是否同时调整发票项 | 缺失/false → 不调整 |
| `IPCD_REFUND_IDS_AMOUNTS` | 发票项 id→退款金额 Map（键可为 String/UUID，值可为 BigDecimal/String/Integer/null） | 缺失 → 空 Map |
| `IPCD_PAYMENT_ID` | 贷记场景的原始支付 id（legacy） | 缺失 → 用当前 paymentId |

**组装入口**：`DefaultInvoicePaymentApi` 在退款/贷记时把 `IPCD_REFUND_WITH_ADJUSTMENTS` 与 `IPCD_REFUND_IDS_AMOUNTS` 注入插件属性；贷记额外注入 `IPCD_PAYMENT_ID`。

## TERM-078 支付控制插件回调契约（priorCall / onSuccessCall / onFailureCall）

- **类型**: 术语
- **同义词**: 控制插件回调, control plugin callbacks, priorCall, onSuccessCall, onFailureCall, PriorPaymentControlResult, OnFailurePaymentControlResult, 回调契约
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/control/ControlPluginRunner.java:64-156`, `payment/src/main/java/org/killbill/billing/payment/core/sm/control/ControlPluginRunner.java:158-222`, `payment/src/main/java/org/killbill/billing/payment/core/sm/control/ControlPluginRunner.java:224-295`, `payment/src/main/java/org/killbill/billing/payment/retry/DefaultPriorPaymentControlResult.java:47-76`, `payment/src/main/java/org/killbill/billing/payment/retry/DefaultFailureCallResult.java:30-41`

**定义**：`PaymentControlPluginApi` 有 3 个回调，由 `ControlPluginRunner` 依次驱动：

| 回调 | 时机 | 返回 | 能改变什么 |
|---|---|---|---|
| `priorCall(ctx, props)` | 调用支付插件**之前** | `PriorPaymentControlResult` | 调整 `paymentMethodId`、插件名（`AdjustedPluginName`）、金额、币种、插件属性；`isAborted()`=true 则中止 |
| `onSuccessCall(ctx, props)` | 支付交易 `SUCCESS` 或 `PENDING` 后 | `OnSuccessPaymentControlResult` | **只能**调整后续插件看到的 `pluginProperties`（`AdjustedPluginProperties`） |
| `onFailureCall(ctx, props)` | 交易失败/异常时 | `OnFailurePaymentControlResult` | 返回 `nextRetryDate`（决定重试日期）+ 调整 `pluginProperties` |

**回调上下文 `PaymentControlContext` 关键字段**：accountId、paymentMethodId、`paymentPluginName`、`attemptId`、paymentId、paymentExternalKey、transactionId、transactionExternalKey、`paymentApiType`（恒为 `PAYMENT_TRANSACTION`）、transactionType、amount/currency、processedAmount/processedCurrency、`isApiPayment`。

**异常语义**：`onSuccessCall`/`onFailureCall` 抛出的 `PaymentControlApiException` 或运行时异常会被**捕获并仅记日志**（"semantics undefined"），不阻断主流程；只有 `priorCall` 的异常/abort 会影响流转。

## TERM-079 Janitor 通知键 (JanitorNotificationKey)

- **类型**: 术语
- **同义词**: janitor 通知键, JanitorNotificationKey, 回查任务, task name, 通知负载, attempt number
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:378-399`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:425-433`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/Janitor.java:80-92`

**定义**：Janitor 回查通知的负载，字段含义：
- `uuidKey` = `paymentTransactionId`（要回查的交易）；
- `taskName` = 固定 `IncompletePaymentTransactionTask.class.toString()`（**向后兼容保留旧类名**，见 `Janitor.handleReadyNotification` 的 `if (janitorKey.getTaskName().equals(IncompletePaymentTransactionTask.class.toString()))`）；
- `apiPayment`（Boolean，老数据为 null 时按 false）；
- `attemptNumber`（Integer，从 1 开始递增）。

**入队**：`janitorQueue.recordFutureNotification(notificationTime, key, userToken, accountRecordId, tenantRecordId)`；`notificationTime` 为 null 时不入队（重试耗尽）。

## TERM-080 用量

- **类型**: 术语
- **同义词**: 用量, 使用量, 计量, 用量数据, usage, usage data, metered usage, metering, quantity
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:71-92`

**含义**：Kill Bill 中「用量」是按订阅（subscription）记录的、带日期的计量值。每条用量记录绑定到一个订阅（`subscriptionId`）、一个单位类型（`unitType`）、一个记录时刻（`recordDate`）与一个数值（`amount`）。

**边界**：用量模块只负责「记录/存储/查询」用量原始数值；它不负责定价、限额校验或计费，也不区分消费型/容量型（见 BR-294）。定价与聚合发生在开票侧（invoice 模块），目录侧定义允许的单位类型（见 TERM-082、BR-293）。

---

## TERM-081 用量记录（单日计量）

- **类型**: 术语
- **同义词**: 用量记录, 每日用量, 用量条目, usage record, usage entry, daily amount, metered record, record_date
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:85-90`, `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:6-24`

**含义**：一次「记录时刻 + 数值」的二元组即一条用量记录（`UsageRecord` = `recordDate` + `amount`）。提交时按订阅 + 单位类型分组，展开为多行落库。

**落库字段**：`subscription_id`、`unit_type`、`record_date`（datetime，精确到时刻）、`amount`（decimal(18,9)）、`tracking_id`，外加框架字段 `created_by`/`created_date`/`account_record_id`/`tenant_record_id`。

---

## TERM-082 单位类型（Unit Type）

- **类型**: 术语
- **同义词**: 单位类型, 计量单位, 用量单位, unit type, unitType, unit, meter, usage unit
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:6-24`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultRolledUpUnit.java:24-42`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:56-98`

**含义**：`unitType` 是一个自由字符串（DB 列 `unit_type varchar(255) NOT NULL`），用于在同一订阅下区分多种计量维度（如 "GB"、"minutes"、"requests"）。用量模块只把它当作分组键，不做白名单校验。

**与目录的关联**：目录（catalog）的 Usage 定义里，单位通过 `TieredBlock.getUnit().getName()` / `Limit.getUnit().getName()` 声明（见 BR-293）。也就是说：**用量侧写入的 `unitType` 字符串必须与目录中该 usage 段声明的 unit 名称一致，开票侧才能对上价**；用量模块本身不校验该一致性（不一致时的处理见 BR-295）。

---

## TERM-083 汇总用量（Rolled-Up Usage）

- **类型**: 术语
- **同义词**: 汇总用量, 聚合用量, 累计用量, rolled up usage, rolledUpUsage, aggregate usage, rolled up unit
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultRolledUpUsage.java:34-59`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:158-168`

**含义**：查询用量时的返回视图。`RolledUpUsage` = 订阅 + 区间 `[start, end)` + 若干 `RolledUpUnit`（每个 = `unitType` + 该区间内累计 `amount`）。它不是一张表，而是把区间内的多行原始用量按 `unitType` 相加后的结果。

**要点**：同一 `unitType` 的多行原始记录会被合并成一个 `RolledUpUnit`（求和），见 BR-287。

---

## TERM-084 原始用量（Raw Usage）

- **类型**: 术语
- **同义词**: 原始用量, 逐条用量, 明细用量, raw usage, rawUsage, raw usage record, 用量明细
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultRawUsage.java:26-65`, `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultInternalUserApi.java:63-84`

**含义**：未聚合的逐条用量记录，供开票侧使用。`RawUsageRecord` 暴露 `subscriptionId`、`date`（即 `recordDate`）、`unitType`、`amount`、`trackingId`。它与落库行一一对应，不做按单位类型合并。

**用途**：开票引擎只需要原始明细（它自己做区间切分和定价），因此内部 API `getRawUsageForAccount` 返回 `RawUsageRecord` 而非 `RolledUpUsage`（见 WF-036）。

---

## TERM-085 跟踪号（Tracking Id）

- **类型**: 术语
- **同义词**: 跟踪号, 追踪号, 幂等号, 去重号, tracking id, trackingId, idempotency key, dedup key
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:74-82`, `usage/src/test/java/org/killbill/billing/usage/dao/TestDefaultRolledUpUsageDao.java:171-196`

**含义**：调用方提交用量时可带的字符串（DB 列 `tracking_id varchar(128) NOT NULL`），用于**防止同一批用量被重复提交**。

**语义**：同一订阅下若已存在相同 `trackingId` 的行，再次提交会被拒绝并抛 `USAGE_RECORD_TRACKING_ID_ALREADY_EXISTS`（见 BR-282）。未提供时系统自动生成一个随机 UUID（见 BR-283）。

---

## TERM-086 消费型用量（CONSUMABLE）

- **类型**: 术语
- **同义词**: 消费型用量, 消耗型, 按量计费, 用量累加, consumable, consumable usage, usage-based, metered
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:34-67`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:539-548`

**含义**：目录 `UsageType.CONSUMABLE`，表示「按消耗计量累加」的用量。开票侧对同一区间内多条记录**求和**（`currentAmount.add(newAmount)`）。

**单位来源**：CONSUMABLE 的单位类型来自目录中各 tier 的 `TieredBlock.getUnit().getName()`（见 BR-293）。

**用量侧视角**：用量模块存储时**不区分** CONSUMABLE/CAPACITY（同一张表、同一套字段）；类型差异只在目录校验与开票聚合时体现（见 BR-294）。

---

## TERM-087 容量型用量（CAPACITY）

- **类型**: 术语
- **同义词**: 容量型用量, 容量计费, 峰值用量, 取最大值, capacity, capacity usage, peak usage, max usage
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:69-87`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:539-548`

**含义**：目录 `UsageType.CAPACITY`，表示「按容量/峰值计量」的用量。开票侧对同一区间内多条记录**取最大值**（`currentAmount.max(newAmount)`），即按区间内观测到的峰值计费。

**单位来源**：CAPACITY 的单位类型来自目录中各 tier 的 `Limit.getUnit().getName()`（见 BR-293），且 IN_ADVANCE 的 CAPACITY 段必须定义 limits（见 BR-180）。

---

## TERM-088 欠费开票模式（IN_ARREAR）

- **类型**: 术语
- **同义词**: 欠费开票, 后付费, 用后付费, 期末计费, in arrear, IN_ARREAR, postpaid, bill in arrears
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:212-229`, `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:34-74`

**含义**：`BillingMode.IN_ARREAR`。用量在期末结算，目录中该 usage 段必须有 tiers。开票侧对 IN_ARREAR 的用量按 CONSUMABLE/CAPACITY 分别处理。

**用途侧关联**：用量记录本身就是「先发生、后结算」的数据；`getRawUsageForAccount` 的注释明确这是**唯一用于开票的查询**（见 BR-286）。

---

## TERM-089 预付开票模式（IN_ADVANCE）

- **类型**: 术语
- **同义词**: 预付开票, 预付费, 期初计费, in advance, IN_ADVANCE, prepaid, bill in advance
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:212-229`

**含义**：`BillingMode.IN_ADVANCE`。目录校验要求：IN_ADVANCE + CAPACITY 必须定义 `limits`；IN_ADVANCE + CONSUMABLE 必须定义 `blocks`。用量模块不参与该模式判定，但写入的 `unitType` 必须与目录对应的 limit/block 单位名称匹配。

---

## TERM-090 用量插件（Usage Plugin）

- **类型**: 术语
- **同义词**: 用量插件, 用量提供者, 自定义用量源, usage plugin, usage provider, UsagePluginApi, OSGI usage plugin
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/BaseUserApi.java:55-94`, `usage/src/main/java/org/killbill/billing/usage/glue/DefaultUsageProviderPluginRegistry.java:30-66`

**含义**：通过 OSGI 注册的 `UsagePluginApi` 实现，可作为用量的外部数据源。用量模块在查询时**优先**向插件要数据；插件返回非 null 结果（即使为空列表）时，就不再查自身 `rolled_up_usage` 表（见 BR-290）。

**注册**：Glue 层用 `OSGIServiceRegistration<UsagePluginApi>` + `DefaultUsageProviderPluginRegistry` 以插件注册名索引（见 ENT-064）。

---

## TERM-091 用量上下文（UsageContext）

- **类型**: 术语
- **同义词**: 用量上下文, 用量查询上下文, usage context, UsageContext, tenant context
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/DefaultUsageContext.java:34-58`

**含义**：传给插件的上下文对象，暴露 `dryRunType`（试算类型）、`inputTargetDate`（目标日期）与租户上下文（`accountId`、`tenantId`）。查询用量时构造为 `new DefaultUsageContext(null, null, tenantContext)`（普通查询）或携带 dry-run 信息（开票 dry-run）。

**约束**：`BaseUserApi.getUsageFromPlugin` 首先断言 `usageContext.getAccountId()` 非空（见 `usage/src/main/java/org/killbill/billing/usage/api/BaseUserApi.java:63-65`）。

---

## TERM-092 区块（Block / TieredBlock）

- **类型**: 术语
- **同义词**: 区块, 计费块, 阶梯块, 分块, 块大小, tiered block, TieredBlock, block, block size, tieredBlock, 计价块, 用量块, 块价, Block, block price
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:47-97`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTieredBlock.java:35-71`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:49-97`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTieredBlock.java:38-60`

**含义**：CONSUMABLE IN_ARREAR 用量的最小计价单位（catalog 里的 `<tieredBlock>` / `<block>`）。字段：

- `unit`：单位名（引用 `DefaultUnit.name`，见 ENT-071）。
- `size`：每「一块」包含多少个单位（`BigDecimal`）。
- `prices`：每块价格（`InternationalPrice`，多币种；取价用 `getPrice(currency)`）。
- `max`：该档允许的最大**块数**（`BigDecimal`）；`-1`/缺省表示无上限（见 BR-301）。
- `type`：`BlockType`；`DefaultTieredBlock.getType()` 恒为 `TIERED`，普通 `<block>` 缺省 `VANILLA`。

**计价关联**：计价时把区间用量 `units` 换算为块数 `nbBlocks = ceil(units / size)`，再用 `price × nbBlocks`（见 BR-302/BR-303、ENT-068）。

**补充（minTopUpCredit）**：`minTopUpCredit` 仅 TOP_UP 类型的块使用，缺省 `-1` 表示未设置；普通用量块不使用。

---

## TERM-093 限额（Limit）

- **类型**: 术语
- **同义词**: 限额, 上限, 档位上限, 容量上限, 最大用量, limit, Limit, max, min
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultLimit.java:44-66`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultLimit.java:83-105`

**含义**：CAPACITY IN_ARREAR 的每档容量边界（catalog 里的 `<limit>`）。字段：

- `unit`：单位名（引用 `DefaultUnit.name`）。
- `min`：下限（`BigDecimal`，可空/哨兵 `-1`）。
- `max`：上限（`BigDecimal`，可空/哨兵 `-1`；`-1` 视为无上限）。

**初始化语义**：`initialize` 中 `maxHasValue = max != null && max != -1`、`minHasValue` 同理（因此 catalog 未写 max/min 会被 `CatalogSafetyInitializer` 填成 `-1`，等价于未设）。

**`compliesWith(value)`（通用限额校验，非定价路径）**：`maxHasValue && value > max → false`；否则 `!minHasValue || value <= min → true`。注意 min 的判定实现是「value ≤ min」，与直觉不同。

**CAPACITY 定价只用 `max`、忽略 `min`**（见 BR-299/BR-300）。

---

## TERM-094 档位计费策略（TierBlockPolicy）

- **类型**: 术语
- **同义词**: 档位策略, 阶梯策略, 计费策略, 全档计价, 顶档计价, tier block policy, TierBlockPolicy, ALL_TIERS, TOP_TIER, 分层策略, 计费阶梯策略
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:71-72`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogSafetyInitializer.java:63-65`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogSafetyInitializer.java:60-72`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:209-216`

**含义**：控制 CONSUMABLE IN_ARREAR 用量如何映射到档（tier），取值：

- `ALL_TIERS`：**逐档累进**——每一档只对自己区间内消耗的块数计价，各档金额求和（见 BR-302）。**这是 catalog 未显式配置时的缺省值**（CatalogSafetyInitializer 填 `ALL_TIERS`）。
- `TOP_TIER`：**单一档计价**——整段用量按用量所落的那一个档的单价计算（见 BR-303）。

**其它值**：`computeToBeBilledConsumableInArrear` 的 switch 落到 `default` 会抛 `IllegalStateException("Unknown TierBlockPolicy ...")`。

---

## TERM-095 用量输出粒度（UsageDetailMode）

- **类型**: 术语
- **同义词**: 明细模式, 汇总模式, 聚合模式, 用量输出模式, usage detail mode, UsageDetailMode, AGGREGATE, DETAIL, item result behavior mode
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:53-56`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:174-182`

**含义**：控制 usage 发票项的生成粒度，由系统属性 `org.killbill.invoice.item.result.behavior.mode` 切换，**缺省 `AGGREGATE`**：

- `AGGREGATE`：每个计费区间、每个单位类型生成 **1 个** USAGE 发票项；`itemDetails` 写整个聚合体 JSON；金额为区间合计（见 BR-305）。
- `DETAIL`：CONSUMABLE 对**每个档位明细**生成一个 USAGE 发票项（带 `quantity` 与 `rate`=档单价）；CAPACITY 仍是单项。

**关联读取点**：`UsageInvoiceItemGenerator` 在开票时读取该配置并传入每个结算区间（`invoice/src/main/java/org/killbill/billing/invoice/generator/UsageInvoiceItemGenerator.java:111`）。该配置可被租户级覆盖（`MultiTenantInvoiceConfig`）。

---

## TERM-096 计费区间（ContiguousIntervalUsageInArrear）

- **类型**: 术语
- **同义词**: 计费区间, 连续区间, 在途区间, usage interval, contiguous interval, ContiguousIntervalUsageInArrear, in-arrear 区间
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:78-92`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:131-153`

**含义**：针对「一个订阅 + 一个 usage 段 + 一个目录版本」的 in-arrear 计价单元，由一段连续的 billing events 构成（`build()` 时生成转换时间）。抽象基类在构造时按 usageType 决定参与计价的单位类型集合：CAPACITY → 各档 `Limit.getUnit().getName()`，CONSUMABLE → 各档 `TieredBlock.getUnit().getName()`（`invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:142`）。

**两个具体子类**：

- `ContiguousIntervalCapacityUsageInArrear`（CAPACITY）
- `ContiguousIntervalConsumableUsageInArrear`（CONSUMABLE）

**区间有效性**：`transitionTimes.size() < 2`（不足一个完整区间）时不产生任何发票项（`invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:277-279`）。

---

## TERM-097 转换时间（TransitionTime）

- **类型**: 术语
- **同义词**: 转换时间, 计费边界, 计费颗粒点, 计费周期边界, transition time, TransitionTime, billing transition
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:104-129`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:184-254`

**含义**：计费区间内的边界时刻，对齐到订阅的 BCD（bill cycle day）并按 `billingPeriod` 分隔；首个/末个转换点可能不对齐（受首个 billing event、`targetDate`、退订日影响）。N 个转换点划分出 **N−1** 个半开区间 `[prev, cur)`，每个区间独立聚合、定价、生成发票项。

**每个转换点绑定一个 billing event**（`targetBillingEvent`），用于取该区间的目录生效日、货币、产品/套餐名等。`build(closedInterval)`：`closedInterval=true` 表示该区间由最后一个 billing event 关闭（区间末端 = 该 event 生效日）；`false` 表示进行中，末端 = `targetDate` 当天末刻。

**退订当日特殊处理**：若最后转换点对应 CANCEL 且用量日期等于该转换点，则该用量点被纳入区间（以便对退订当日上报的用量计费，`invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:224-229`、`invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:439-471`）。

---

## TERM-098 带目录版本的用量区间（RolledUpUsageWithMetadata）

- **类型**: 术语
- **同义词**: 带元数据用量区间, 目录生效日用量, usage with metadata, RolledUpUsageWithMetadata, catalog effective date, DefaultRolledUpUsageWithMetadata
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/RolledUpUsageWithMetadata.java:24-27`, `invoice/src/main/java/org/killbill/billing/invoice/usage/DefaultRolledUpUsageWithMetadata.java:27-66`

**含义**：开票侧聚合结果，在 `RolledUpUsage`（`subscriptionId` + `[start,end)` + `rolledUpUnits`）之上额外带 `catalogEffectiveDate`。用途：保证区间以「该边界时刻对应的目录版本」定价，避免跨目录版本误用价格/档位（见 BR-311）。

**构造点**：`ContiguousIntervalUsageInArrear#getRolledUpUsage` 中，每个区间用 `prevCatalogEffectiveDate`（上一转换点的 billing event 目录生效日）构造（`invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:507`）。

---
