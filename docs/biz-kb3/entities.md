# 业务实体（Entities）

> Kill Bill 业务知识库 v3（合并 kb2 既有卡 + kb3 补充卡）；共 72 张卡。

---

## ENT-001 发票（Invoice）

- **类型**: 业务实体
- **同义词**: 发票, invoice, Invoice, 账单, 单据
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoice.java:44-127`

**说明**：发票实体关键属性：`accountId`、`invoiceNumber`（发票号）、`invoiceDate`（开票日期）、`targetDate`（目标日期）、`currency`/`processedCurrency`、`status`（DRAFT/COMMITTED/VOID）、`isMigrationInvoice`、`isWrittenOff`（核销）、`isParentInvoice`、`parentInvoice`（父发票，用于 HA/父子账户）、`grpId`（分组 id，用于一次开票产生的多张发票归组）。
**关系**：一张发票包含多个 `InvoiceItem` 与多个 `InvoicePayment`（支付）。

## ENT-002 账户信用余额调整项（CreditBalanceAdjInvoiceItem / CBA）

- **类型**: 业务实体
- **同义词**: 信用余额调整项, CBA项, credit balance adjustment item, CBA_ADJ, 账户信用项
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:243-251`, `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:78-80`

**说明**：`CreditBalanceAdjInvoiceItem` 是类型为 `CBA_ADJ` 的发票项，用于表示账户信用余额的变化（消费或累积）。构建时以传入金额的负值 `amount.negate()` 记账。

## ENT-003 用量发票项（UsageInvoiceItem）

- **类型**: 业务实体
- **同义词**: 用量发票项, 使用量条目, usage invoice item, UsageInvoiceItem, USAGE item, 用量明细
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:345-356`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:573-597`

**说明**：类型为 `USAGE` 的发票项，记录某订阅某用量在 `[startDate, endDate)` 区间的费用。关键字段：`usageName`（用量名，与目录一致）、`startDate`/`endDate`（计费区间）、`amount`、`itemDetails`（用量明细聚合的 JSON）。去重与“已计费金额”比较均基于 usageName + 区间。

## ENT-004 父汇总发票项（ParentInvoiceItem / PARENT_SUMMARY）

- **类型**: 业务实体
- **同义词**: 父汇总项, 父子账户, parent summary, PARENT_SUMMARY, ParentInvoiceItem, HA 发票项
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1380-1396`, `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:82-85`

**说明**：类型为 `PARENT_SUMMARY` 的发票项，挂在**父账户的父发票**上，用于汇总某个子账户的发票金额。关键字段：`childAccountId`（对应子账户）、`amount`、`description`（`<子账户externalKey> summary`）。

## ENT-005 周期发票项（RecurringInvoiceItem）

- **类型**: 业务实体
- **同义词**: 周期项, 订阅费, 月费, recurring item, RecurringInvoiceItem, RECURRING, 订阅周期费用
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/RecurringInvoiceItem.java:33-57`, `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:260-278`

**说明**：类型为 `RECURRING` 的发票项，表示按 billingPeriod 重复收取的订阅费。含 `bundleId`/`subscriptionId`、`productName`/`planName`/`phaseName`、`catalogEffectiveDate`、`startDate`/`endDate`、`amount`、`rate`。生成时 `amount = 周期数 × rate × quantity`（`rate` 为每周期单价，`quantity` 默认 1）。

## ENT-006 固定费用发票项（FixedPriceInvoiceItem）

- **类型**: 业务实体
- **同义词**: 固定费用, 一次性费用, 初装费, fixed price, FixedPriceInvoiceItem, FIXED, 固定价
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/FixedPriceInvoiceItem.java:32-66`, `invoice/src/main/java/org/killbill/billing/invoice/model/FixedPriceInvoiceItem.java:98-114`

**说明**：类型为 `FIXED` 的发票项，表示阶段（phase）开始时一次性收取的固定费用（无 `rate`，只有金额与日期）。描述默认 `"Fixed price charge"`；若有 phase 名则默认 `<phase> (fixed price)`。

## ENT-007 外部收费发票项（ExternalChargeInvoiceItem）

- **类型**: 业务实体
- **同义词**: 外部收费, 手动收费, 附加费用, external charge, ExternalChargeInvoiceItem, EXTERNAL_CHARGE, 额外收费
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/ExternalChargeInvoiceItem.java:32-58`, `invoice/src/main/java/org/killbill/billing/invoice/model/ExternalChargeInvoiceItem.java:91-103`

**说明**：类型为 `EXTERNAL_CHARGE` 的发票项，用于在订阅计费之外手动/外部加收费用，可关联 bundle/subscription。描述默认 `"External charge"` 或 `<plan> (external charge)`。

## ENT-008 发票支付（InvoicePayment / DefaultInvoicePayment）

- **类型**: 业务实体
- **同义词**: 发票支付, 支付记录, invoice payment, InvoicePayment, 付款, 退款记录
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoicePayment.java:34-72`

**说明**：表示发票上的一条支付/退款记录，属性：`type`（InvoicePaymentType：ATTEMPT/REFUND/CHARGED_BACK）、`paymentId`、`invoiceId`、`paymentDate`、`amount`、`currency`、`processedCurrency`、`paymentCookieId`、`linkedInvoicePaymentId`（关联的支付，如退款关联原支付）、`status`（InvoicePaymentStatus，默认 `SUCCESS`）。

## ENT-009 税项（TaxInvoiceItem / TAX）

- **类型**: 业务实体
- **同义词**: 税项, 税费, tax item, TaxInvoiceItem, TAX, 税金
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/TaxInvoiceItem.java:31-90`

**说明**：类型为 `TAX` 的发票项，继承 `InvoiceItemCatalogBase`（可带 catalog 字段）。关键构造参数：`invoiceId`、`accountId`、可选 `bundleId`、`description`、`startDate`（date，endDate 为 null）、`amount`、`currency`、可选 `linkedItemId`。**描述默认值**：`"Tax"`（未显式指定时）。可通过 `insertTaxItems` API 批量添加。

## ENT-010 发票级信用项（CreditAdjInvoiceItem / CREDIT_ADJ）

- **类型**: 业务实体
- **同义词**: 发票级信用, 信用调整项, credit adjustment, CreditAdjInvoiceItem, CREDIT_ADJ, 信用项
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/CreditAdjInvoiceItem.java:33-54`

**说明**：类型为 `CREDIT_ADJ` 的发票项，继承 `AdjInvoiceItem`（`catalogEffectiveDate` 恒为 null）。`startDate == endDate == date`，可含 `rate`/`quantity`。**描述默认值**：`"Invoice adjustment"`。
- 通过 `insertCredits` API 创建时金额会被**取负**（`amount.negate()`）；`getCreditById` 返回时再取负还原（见 BR-032）。
- 信用发票（恰好 CREDIT_ADJ + CBA_ADJ 两项）中，该 CREDIT_ADJ 参与 `computeInvoiceAmountAdjustedForAccountCredit`（见 BR-025）。

## ENT-011 项调整项（ItemAdjInvoiceItem / ITEM_ADJ）

- **类型**: 业务实体
- **同义词**: 项调整项, 条目调整, item adjustment, ItemAdjInvoiceItem, ITEM_ADJ, 单项调整
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/ItemAdjInvoiceItem.java:34-55`

**说明**：类型为 `ITEM_ADJ` 的发票项，继承 `AdjInvoiceItem`。`startDate == endDate == effectiveDate`；`linkedItemId` 指向被调整的原项（**必须非 null**）；金额为**负值**。**描述默认值**：`"Invoice item adjustment"`。可带 `rate`/`quantity`/`itemDetails`。

## ENT-012 修复冲销项（RepairAdjInvoiceItem / REPAIR_ADJ）

- **类型**: 业务实体
- **同义词**: 修复冲销项, 冲销项, repair adjustment, RepairAdjInvoiceItem, REPAIR_ADJ, 改套餐冲销
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/RepairAdjInvoiceItem.java:33-53`

**说明**：类型为 `REPAIR_ADJ` 的发票项，继承 `AdjInvoiceItem`。有独立的 `startDate`/`endDate` 区间（与 ITEM_ADJ 不同，可表示被冲销的原始服务区间）；`reversingId`（即 `linkedItemId`）指向被冲销的原项；金额为**负值**。**描述默认值**：`"Adjustment (subscription change)"`。

## ENT-013 调整项公共基类（AdjInvoiceItem）

- **类型**: 业务实体
- **同义词**: 调整基类, AdjInvoiceItem, 调整项公共字段, 调整项无目录生效日
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/AdjInvoiceItem.java:31-54`

**说明**：`CreditAdjInvoiceItem`、`ItemAdjInvoiceItem`、`RepairAdjInvoiceItem` 的公共父类（间接继承 `InvoiceItemBase`）：
- 无 bundle/subscription/product/plan/phase/usage 等目录字段（构造时传 null）；
- **`getCatalogEffectiveDate()` 恒返回 null**（调整项不参与目录 pretty name 计算）；
- 公共字段：`startDate`、`endDate`、`description`、`amount`、`currency`、`reversingId(=linkedItemId)`、可选 `rate`/`quantity`/`itemDetails`。

## ENT-014 逾期状态 OverdueState

- **类型**: 业务实体
- **同义词**: 逾期状态, 催收阶段, 逾期等级, overdue state, dunning stage, DefaultOverdueState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:44-72`

**关键字段/关系**：`name`（必填，XML `@XmlID`，最长 50）、`condition`（DefaultOverdueCondition，可空）、`externalMessage`（默认 ""）、`blockChanges`（默认 false）、`disableEntitlementAndChangesBlocked`（默认 false）、`subscriptionCancellationPolicy`（默认 NONE）、`isClearState`（默认 false）、`autoReevaluationInterval`（DefaultDuration，可空）、`enterStateEmailNotification`（**已废弃**，仅保留配置兼容）。
**关系**：隶属于账户状态集 `accountOverdueStates`；被包装为 `BlockingState` 持久化（服务名 overdue-service，类型 ACCOUNT）。

## ENT-015 逾期条件 OverdueCondition

- **类型**: 业务实体
- **同义词**: 逾期条件, 催收触发条件, overdue condition, dunning condition, DefaultOverdueCondition
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:48-67`

**关键字段**：`numberOfUnpaidInvoicesEqualsOrExceeds`(Integer)、`totalUnpaidInvoiceBalanceEqualsOrExceeds`(BigDecimal)、`timeSinceEarliestUnpaidInvoiceEqualsOrExceeds`(DefaultDuration)、`responseForLastFailedPayment`(PaymentResponse[]，XML wrapper `responseForLastFailedPaymentIn`/子元素 `response`)、`controlTagInclusion`(ControlTagType)、`controlTagExclusion`(ControlTagType)。
**关系**：实现 `ConditionEvaluation.evaluate(BillingState, LocalDate)`；被 `OverdueState` 持有，被 `OverdueStateSet.calculateOverdueState` 调用。

## ENT-016 账户逾期状态集 OverdueStatesAccount / OverdueStateSet

- **类型**: 业务实体
- **同义词**: 账户状态集, 逾期状态集合, 催收规则集, account overdue states, overdue state set, OverdueStatesAccount
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:33-40`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:35-96`, `api/src/main/java/org/killbill/billing/overdue/config/api/OverdueStateSet.java:24-45`

**关键字段/关系**：`initialReevaluationInterval`（DefaultDuration）+ `state[]`（有序状态数组）；继承内建 `clearState`。核心行为：`findState(name)`、`getClearState()`、`calculateOverdueState(billingState, now)`（返回首个命中状态，否则 clear）、`size()`、`getFirstState()`（返回数组最后一个，即入门级逾期状态）。

## ENT-017 计费状态 BillingState

- **类型**: 业务实体
- **同义词**: 计费状态, 欠费快照, billing state, BillingState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `api/src/main/java/org/killbill/billing/overdue/config/api/BillingState.java:29-53`, `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:67-84`

**关键字段/关系**：由 `BillingStateCalculator` 从 InvoiceInternalApi（未付发票）、TagInternalApi（账户标签）、Clock（当前日）构造。是条件评估的唯一输入。注意 `responseForLastFailedPayment` 目前被硬编码为 `INSUFFICIENT_FUNDS`（TODO MDW），见 BR-113。

## ENT-018 逾期配置根 OverdueConfig

- **类型**: 业务实体
- **同义词**: 逾期配置, 催收配置, overdue config, DefaultOverdueConfig, overdueConfig, overdue.xml
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueConfig.java:35-52`, `overdue/src/main/resources/NoOverdueConfig.xml:20-27`

**关键字段/关系**：XML 根元素 `<overdueConfig>`，唯一必需子节点 `<accountOverdueStates>`（DefaultOverdueStatesAccount）。当前版本**只有账户级配置**（没有 bundle/subscription 级状态集）。`validate` 委托给 accountOverdueStates 校验。

## ENT-019 逾期包装器 OverdueWrapper

- **类型**: 业务实体
- **同义词**: 逾期包装器, 账户逾期执行器, overdue wrapper, OverdueWrapper
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:48-87`

**关键字段/关系**：绑定单个 Account（`overdueable`）+ OverdueStateSet + BillingStateCalculator + OverdueStateApplicator + GlobalLocker。对外能力：`refresh(effectiveDate, ctx)`、`getNextOverdueState`、`clear`、`billingState`。常量 `CLEAR_STATE_NAME`、`MAX_LOCK_RETRIES=50`。是「评估+施加」的编排门面（见 WF-010）。

## ENT-020 计费状态计算器 BillingStateCalculator

- **类型**: 业务实体
- **同义词**: 计费状态计算器, 欠费统计, billing state calculator, BillingStateCalculator
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:45-108`

**关键字段/关系**：依赖 InvoiceInternalApi、TagInternalApi、Clock。`unpaidInvoicesForAccount` 取未付发票并按 `getInvoiceDate()` 升序（同日期用 hashCode 稳定打破平局）；`sumBalance` 求和；`earliest` 取最早一张；`calculateBillingState` 组装 BillingState。

## ENT-021 逾期状态施加器 OverdueStateApplicator

- **类型**: 业务实体
- **同义词**: 逾期状态施加器, 状态执行器, overdue state applicator, OverdueStateApplicator
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:71-102`

**关键字段/关系**：依赖 BlockingInternalApi、AccountInternalApi、EntitlementApi/EntitlementInternalApi、TagInternalApi、OverduePoster(check)、BusOptimizer、InternalCallContextFactory。核心方法：`apply(...)`（状态切换+动作+事件+定时）、`clear(...)`、`storeNewState(...)`、`cancelSubscriptionsIfRequired(...)`、`isAccountTaggedWith_OVERDUE_ENFORCEMENT_OFF(...)`。

## ENT-022 逾期变更事件 OverdueChangeInternalEvent

- **类型**: 业务实体
- **同义词**: 逾期变更事件, 状态变更事件, overdue change event, OverdueChangeInternalEvent, OVERDUE_CHANGE
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/DefaultOverdueChangeEvent.java:28-58`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:215-219`

**关键字段/关系**：`overdueObjectId`、`previousOverdueStateName`、`nextOverdueStateName`、`isBlockedBilling`、`isUnblockedBilling`，`getBusEventType()=OVERDUE_CHANGE`。在 `apply`/`clear` 末尾经 BusOptimizer 投递；是 invoice 等下游模块感知逾期状态变化的通道。

## ENT-023 逾期通知键 OverdueCheckNotificationKey / OverdueAsyncBusNotificationKey

- **类型**: 业务实体
- **同义词**: 逾期通知键, 催收通知, overdue notification key, NotificationKey, REFRESH, CLEAR
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueCheckNotificationKey.java:26-31`, `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusNotificationKey.java:26-45`

**关键字段/关系**：`OverdueCheckNotificationKey` 持 `uuidKey`（账户 id，继承 DefaultUUIDNotificationKey）。`OverdueAsyncBusNotificationKey` 额外持 `action`，枚举 `OverdueAsyncBusNotificationAction{REFRESH, CLEAR}`——这是「异步总线入队」用的动作区分。

## ENT-024 逾期监听器 OverdueListener

- **类型**: 业务实体
- **同义词**: 逾期监听器, 事件监听器, overdue listener, OverdueListener
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:64-94`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-157`

**关键字段/关系**：订阅总线事件：控制标签创建/删除、发票创建、发票调整、支付信息、支付错误。除少数情况外统一转成 `REFRESH` 入 async bus 通知队列；`OVERDUE_ENFORCEMENT_OFF` 创建转 `CLEAR`。还会级联刷新父/子账户（见 BR-127）。

## ENT-025 时长配置 DefaultDuration

- **类型**: 业务实体
- **同义词**: 时长, 时间长度, 周期, duration, DefaultDuration, TimeUnit, DAYS, MONTHS
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:38-55`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:99-118`

**关键字段/关系**：`unit`(TimeUnit，必需，XML `<unit>`) + `number`(Integer，默认 -1，XML `<number>`)。支持 `DAYS/WEEKS/MONTHS/YEARS`，遇到 `UNLIMITED` 抛 IllegalStateException。`toJodaPeriod()` 用于条件/间隔计算。

## ENT-026 配置状态实体 DefaultOverdueState（全字段与 getter 映射）

- **类型**: 业务实体
- **同义词**: 配置状态实体, 状态配置对象, DefaultOverdueState, configured overdue state, state entity
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:44-76`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:85-125`

**关键字段/关系**：实现 `OverdueState` + `Externalizable`，继承 `ValidatingConfig<DefaultOverdueConfig>`。
- `getConditionEvaluation()` 与 `getOverdueCondition()` **返回同一个** `condition` 对象；前者是评估接口（`ConditionEvaluation`），后者是公开配置接口（`OverdueCondition`）。
- `getAutoReevaluationInterval()` 返回 `Duration`，并在此处执行「null / UNLIMITED / number==0」的合法性校验（120-125 行，抛 `OverdueApiException(OVERDUE_NO_REEVALUATION_INTERVAL, name)`）。
- `isBlockChanges()`、`isDisableEntitlementAndChangesBlocked()`、`getOverdueCancellationPolicy()`、`isClearState()`、`getName()`、`getExternalMessage()` 是状态动作/展示的全部读取点。
- `equals`/`hashCode` 涵盖 condition/name/externalMessage/blockChanges/disableEntitlement/cancellationPolicy/isClearState/autoReevaluationInterval/enterStateEmailNotification（181-230 行）。
**关系**：被 `DefaultOverdueStateSet.calculateOverdueState` 逐条评估；被 `OverdueStateApplicator` 读取动作；其名字被持久化为账户 BlockingState 的 stateName。

## ENT-027 逾期配置缓存 DefaultOverdueConfigCache（默认配置两阶段加载）

- **类型**: 业务实体
- **同义词**: 逾期配置缓存, 默认配置加载器, DefaultOverdueConfigCache, overdue config cache, default config bootstrap
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:44-66`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:68-91`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:115-132`

**关键字段/关系**：
- 持有 `CacheController<Long, OverdueConfig>`（`CacheType.TENANT_OVERDUE_CONFIG`，键为 tenantRecordId）与一个 `defaultOverdueConfig` 字段。
- **构造时**先尝试从 classpath 加载 `NoOverdueConfig.xml`；失败则 `defaultOverdueConfig = new DefaultOverdueConfig()` 并记 `error`（"should never happen!"）。
- **`loadDefaultOverdueConfig(String configURI)`**：URI 为 null/空 → 标记 missing；否则 `XMLLoader.getObjectFromUri` 覆盖默认配置；任何异常被**内部捕获**并仅记 `warn`。
- **`getOverdueConfig`**：内部租户（`INTERNAL_TENANT_RECORD_ID`）直接返回默认配置；普通租户走缓存，缓存返回 null 时回退默认配置。
- 缓存加载器 `LoaderCallback.loadOverdueConfig` 解析租户 XML，失败抛 `OVERDUE_INVALID_FOR_TENANT`。

## ENT-028 多租户配置基类 MultiTenantOverdueConfig

- **类型**: 业务实体
- **同义词**: 多租户配置基类, 租户配置, MultiTenantOverdueConfig, tenant config base, MultiTenantLockAwareConfigBase
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/MultiTenantOverdueConfig.java:34-47`, `overdue/src/main/java/org/killbill/billing/overdue/glue/DefaultOverdueModule.java:82-88`

**关键字段/关系**：继承 `MultiTenantLockAwareConfigBase`，构造注入 `@Named(STATIC_CONFIG) OverdueConfig staticConfig` 与 `CacheConfig`。
- `getConfigClass()` 返回 `org.killbill.billing.util.config.definition.OverdueConfig.class`，即**租户级属性覆盖**的目标类。
- 它是「无注解 `OverdueConfig` 绑定」的实现，因此运行时代码注入到的是它；静态默认由 `STATIC_CONFIG` 提供。
**意义**：租户可覆盖的是**属性型配置**（如锁重排间隔），而逾期规则 XML（`accountOverdueStates`）走 ENT-027/BR-164 的租户 KV 缓存，两条路径彼此独立。

## ENT-029 逾期运行时 API 实现 DefaultOverdueApi

- **类型**: 业务实体
- **同义词**: 逾期API实现, 运行时接口, DefaultOverdueApi, overdue runtime API, getOverdueStateFor, uploadOverdueConfig
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:42-58`, `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:60-104`

**关键字段/关系**：实现 `OverdueApi`，依赖 `OverdueConfigCache`、`TenantUserApi`、`BlockingInternalApi`、`InternalCallContextFactory`。对外 4 个方法：
- `getOverdueConfig(TenantContext)` → 返回该租户的 `OverdueConfig`（走缓存，未命中回退默认）。
- `uploadOverdueConfig(String xml, CallContext)` → 覆盖租户 `OVERDUE_CONFIG` 并失效缓存（见 BR-164）。
- `uploadOverdueConfig(OverdueConfig, CallContext)` → 先 `XMLWriter.writeXML` 序列化再上传；序列化异常 → `OVERDUE_INVALID_FOR_TENANT`。
- `getOverdueStateFor(UUID accountId, TenantContext)` → 解析该账户当前逾期状态（见 WF-016）。
**注意**：`createInternalTenantContext` 只填 tenantRecordId（注释强调：「important to always create the (ehcache) key the same way」），而 `getOverdueStateFor` 使用带 accountId 的重载以填充 accountRecordId。

## ENT-030 通知去重策略对象 OverdueCheckPoster / OverdueAsyncBusPoster

- **类型**: 业务实体
- **同义词**: 通知投递器, 去重策略, OverdueCheckPoster, OverdueAsyncBusPoster, notification poster, dedup strategy
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueCheckPoster.java:48-85`, `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusPoster.java:47-57`, `overdue/src/main/java/org/killbill/billing/overdue/notification/DefaultOverduePosterBase.java:61-88`

**关键字段/关系**：两者都继承 `DefaultOverduePosterBase`，仅覆盖 `cleanupFutureNotificationsFormTransaction`，即「插入前如何清理既有未来通知」的策略：
- `OverdueCheckPoster`：查询结果按 effectiveDate 升序；只看**第 0 条**（最早）与待插入时间比较，决定是否插入并删除其余（保留最早策略）。
- `OverdueAsyncBusPoster`：只要已存在任意未来通知（`size != 0`）就不插入。
**共用流程**（`DefaultOverduePosterBase.insertOverdueNotification` 61-88）：在**同一事务**内查询该账户未来通知 → 调用策略 → 若允许则 `recordFutureNotificationFromTransaction`。查询按 `context.accountRecordId + tenantRecordId` 过滤（120-126 行）。

## ENT-031 唯一配置属性 OverdueProperties

- **类型**: 业务实体
- **同义词**: 逾期属性, 配置项, OverdueProperties, org.killbill.overdue.uri, config property
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/OverdueProperties.java:25-30`

**关键字段/关系**：接口 `OverdueProperties extends KillbillConfig`，仅声明一个属性：
- `@Config("org.killbill.overdue.uri")`，`@Default("NoOverdueConfig.xml")`，描述为「配置位置：classpath 或文件系统」。
**用途**：`DefaultOverdueService.loadConfig` 以 `properties.getConfigURI()` 作为默认配置来源；除该项外，overdue 模块没有其它自有配置键（租户/业务规则均通过 XML 与租户 KV 提供）。

## ENT-032 产品实体 (Product)

- **类型**: 业务实体
- **同义词**: 产品实体, 产品定义, 产品对象, product entity, Product, DefaultProduct
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:47-121`

**实体说明**：`DefaultProduct` 实现 `Product`，XML 中由 `<product>` 定义。

**关键关系/约束**：
- `category`：BASE / ADD_ON / STANDALONE。
- `included`（`included/addonProduct`）：随主产品赠送/绑定的 add-on 产品集合。
- `available`（`available/addonProduct`）：可加购的 add-on 产品集合。
- `limits`：产品级用量限制。
- 校验：产品引用的 catalogName 必须与目录一致；不允许在 included/available 中自引用（系统属性 `org.killbill.catalog.validation.ignoreSelfReferencingProducts` 可关闭此校验）。

## ENT-033 计划实体 (Plan)

- **类型**: 业务实体
- **同义词**: 计划实体, 套餐实体, plan entity, Plan, DefaultPlan
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:61-97`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:286-326`

**实体说明**：`DefaultPlan` 实现 `Plan`。

**关键关系/约束**：
- 必须关联一个 Product；必须有一个 `finalPhase`；可有 0..N 个 `initialPhases`。
- `plansAllowedInBundle`：缺省 1；BASE 计划与 Tiered ADDON 只允许 1；值 -1 表示不限量。
- `recurringBillingMode` 可缺省并回退到目录级设置。
- 校验：`effectiveDateForExistingSubscriptions` 不得早于目录 `effectiveDate`。

## ENT-034 计划阶段实体 (Plan Phase)

- **类型**: 业务实体
- **同义词**: 阶段实体, 计费阶段实体, phase entity, PlanPhase, DefaultPlanPhase
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:52-102`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:171-191`

**实体说明**：`DefaultPlanPhase` 实现 `PlanPhase`。

**关键关系/约束**：
- 必须定义 `type` 和 `duration`。
- `fixed`、`recurring`、`usages` 三者至少要有一个（否则校验失败）。
- `compliesWithLimits` 先查 usage 段限制，再查产品级限制。

## ENT-035 价格表实体与价格表集合 (PriceList / PriceListSet)

- **类型**: 业务实体
- **同义词**: 价格表实体, 价目表集合, price list entity, PriceListSet, DefaultPriceListSet, child price list
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:47-98`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceList.java:47-108`

**实体说明**：`DefaultPriceListSet` 由 1 个 `defaultPriceList` + N 个 `childPriceLists` 组成，实现 `PriceListSet`。

**关键关系/约束**：
- `findPriceListFrom(name)`：name 为 null 抛 `CAT_NULL_PRICE_LIST_NAME`；匹配默认或子表；找不到抛 `CAT_PRICE_LIST_NOT_FOUND`。
- `getPlanFrom(product, period, priceListName)`：先查指定价格表，无匹配则回退默认价格表；匹配到多个抛 `CAT_MULTIPLE_MATCHING_PLANS_FOR_PRICELIST`，0 个返回 null。
- 子价格表不得使用保留名 `DEFAULT`。

## ENT-036 目录实体 (StandaloneCatalog / StaticCatalog)

- **类型**: 业务实体
- **同义词**: 目录, 目录定义, 单一目录, catalog, StandaloneCatalog, StaticCatalog, 静态目录
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:62-95`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:280-310`

**实体说明**：`StandaloneCatalog` 实现 `StaticCatalog`，是一次目录发布的完整定义。

**关键字段/关系**：`effectiveDate`、`catalogName`、`recurringBillingMode`（目录级缺省计费模式）、`supportedCurrencies`、`units`、`products`、`plans`、`priceLists`、`rules`（`DefaultPlanRules`）。

**校验**：产品集合、计划集合、价格表、规则集依次校验；并校验阶段时长（EVERGREEN 必须 UNLIMITED，非 EVERGREEN 不得 UNLIMITED）。

## ENT-037 价格实体 (Price / InternationalPrice)

- **类型**: 业务实体
- **同义词**: 价格实体, 多币种价格, 国际价格, price, Price, InternationalPrice, price in currency
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:43-100`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPrice.java:41-73`

**实体说明**：`InternationalPrice` 是「币种 → 价格值」的多币种价格容器；`DefaultPrice` 表示单个币种的 `BigDecimal` 金额。

**关键约束**：
- 不含任何 price 时视为**所有币种零价格**（`getPrice` 返回 `BigDecimal.ZERO`）。
- 币种不在目录 `supportedCurrencies` 中 → 校验报 `Unsupported currency`。
- 价格值 < 0 → 校验报 `Negative value for price in currency`。
- 指定币种无价格 → 抛 `CAT_NO_PRICE_FOR_CURRENCY`。
- `value` 为 null 时 `getValue()` 抛 `CurrencyValueNull`。

## ENT-038 时长实体 (Duration)

- **类型**: 业务实体
- **同义词**: 时长, 阶段时长, 持续时间, duration, Duration, TimeUnit, 天数, 月数, 年数
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultDuration.java:41-83`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultDuration.java:106-123`

**实体说明**：`Duration` = `unit`（TimeUnit）+ `number`。

**关键约束**：
- TimeUnit 取值 `DAYS`/`WEEKS`/`MONTHS`/`YEARS`/`UNLIMITED`；对 `UNLIMITED` 执行 `addToDateTime`/`toJodaPeriod` 会抛 `CAT_UNDEFINED_DURATION` 或 IllegalStateException。
- `UNLIMITED` 时 number 必须省略；有限时长必须给出 number，否则校验失败。

## ENT-039 周期费实体 (Recurring)

- **类型**: 业务实体
- **同义词**: 周期费, 循环费用, 订阅费, 月费, recurring, Recurring, recurringPrice, 周期性收费
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultRecurring.java:39-113`

**实体说明**：阶段的周期性收费，由 `billingPeriod`（BillingPeriod）+ 可选 `recurringPrice`（InternationalPrice）组成。

**关键约束**：有 recurringPrice 就必须有有效的 billingPeriod（非 `NO_BILLING_PERIOD`）；没有 recurringPrice 则 billingPeriod 必须是 `NO_BILLING_PERIOD`。

## ENT-040 块与阶梯块实体 (Block / TieredBlock)

- **类型**: 业务实体
- **同义词**: 用量块, 充值块, 阶梯块, block, Block, tieredBlock, TieredBlock, usage block
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:47-64`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTieredBlock.java:36-65`

**实体说明**：`Block` 定义「一个单位块」的价格：`type`、`unit`、`size`（每块包含的单位数）、`prices`（块价）、可选 `minTopUpCredit`。`TieredBlock` 继承 Block 并额外有 `max`（该阶梯的最大用量），固定 `type=TIERED`。

## ENT-041 目录版本集合实体 (VersionedCatalog)

- **类型**: 业务实体
- **同义词**: 目录版本集合, 多版本目录, versioned catalog, VersionedCatalog, versions
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:52-120`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:133-154`

**实体说明**：`DefaultVersionedCatalog` 持有按 `effectiveDate` 升序排列的多个 `StandaloneCatalog` 版本。

**关键约束**：各版本 `catalogName` 必须一致；`effectiveDate` 不得重复；跨版本同名计划的阶段数量与阶段名必须一致。

## ENT-042 规则集实体 (PlanRules)

- **类型**: 业务实体
- **同义词**: 规则集, 计划规则, 目录规则, plan rules, PlanRules, DefaultPlanRules, 变更规则, 取消规则
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:58-83`

**实体说明**：`DefaultPlanRules` 聚合六类规则 case：`changePolicy`（变更策略）、`changeAlignment`（变更对齐）、`cancelPolicy`（取消策略）、`createAlignment`（创建对齐）、`billingAlignment`（计费对齐）、`priceList`（价格表选择）。

**关键约束**：变更策略与取消策略必须各存在一个「全空」的默认 case，且同类规则不得重复。

## ENT-043 阶段计费项实体 (Fixed / Usage / Tier / Limit)

- **类型**: 业务实体
- **同义词**: 计费项, 价格组成, 阶段内容, billing items, fixed, usage, tier, limit
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:61-72`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:74-95`

**实体说明**：一个阶段最多由四类计费项构成：`fixed`（一次性固定费）、`recurring`（周期费）、`usages[]`（用量段，内部再含 tiers/blocks/limits）、以及各计费项级别的 `limits`。

**关键约束**：阶段必须至少含 fixed / recurring / usages 之一。

## ENT-044 目录实体集合（按名索引 + 排序）

- **类型**: 业务实体
- **同义词**: 目录实体集合, 名称索引, catalog entity collection, CatalogEntityCollection, TreeMap
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogEntityCollection.java:32-63`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogEntityCollection.java:191-197`

**说明**：`CatalogEntityCollection<T extends CatalogEntity>` 是目录内产品/计划/价格表的通用容器，底层 `TreeMap<String,T>`，key 为实体 `getName()`。

**关键行为**：
- `addEntry` = `data.put(name, entry)`：同名**覆盖**（见 BR-206）。
- `findByName` 精确查找；`getEntries()`/迭代器按 name 自然序返回。
- `contains`/`containsAll` 以 name 判等价；`retainAll` 抛 `IllegalStateException("Not implemented")`。
- 可序列化（`writeExternal` 直接写整个 map）。

## ENT-045 可变目录（简化计划写模型）

- **类型**: 业务实体
- **同义词**: 可变目录, 可编辑目录, mutable catalog, DefaultMutableStaticCatalog, MutableStaticCatalog
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultMutableStaticCatalog.java:32-122`

**说明**：`DefaultMutableStaticCatalog extends StandaloneCatalog`，是 `CatalogUpdater` 写入简化计划时的可变视图（拷贝构造会克隆名称/模式/日期/币种/单位/产品/计划/规则/价格表并重新 initialize）。

**变更能力**：
- `addCurrency(currency)`：把币种追加到 `supportedCurrencies`。
- `addProduct(product)` / `addPlan(plan)`：加入产品集合 / 计划集合，并把计划登记进其价格表的计划列表。
- `addPriceList(priceList)`：重建 child price list 数组。
- `addRecurringPriceToPlan(price, newPrice)`：为计划周期价追加一个币种价格。
- `addProductAvailableAO(base, ao)`：把 add-on 加入基础产品的 `available`。

**约束**：`allocateNewEntries` 在新增项与既有项同名/同币种（按 CatalogEntity.name、Enum.name 或 Price.currency 判重）时抛 `IllegalStateException("Already existing ...")`——即**不允许重复添加**同一币种/价格表/枚举项。

## ENT-046 价格覆盖计划的命名规则与缓存键

- **类型**: 业务实体
- **同义词**: 覆盖计划命名, 自定义计划名, price override plan name, PriceOverridePattern, dryrun plan, 计划名分隔符
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/caching/PriceOverridePattern.java:26-63`, `catalog/src/main/java/org/killbill/billing/catalog/override/DefaultPriceOverrideSvc.java:121-134`, `catalog/src/main/java/org/killbill/billing/catalog/caching/DefaultOverriddenPlanCache.java:100-102`

**命名规则**：
- 覆盖计划名 = `父计划名 + 分隔符 + 记录号`。分隔符由 `useRECXMLNamesCompliant` 决定：compliant 模式用 `:`（`CUSTOM_PLAN_NAME_DELIMITER`，因其不允许出现在 XML 计划名中），否则用 `-`（`LEGACY_CUSTOM_PLAN_NAME_DELIMITER`）。
- 识别正则：`(.*)<分隔符>(\d+)(?:!\d+)?$`。`isOverriddenPlan(name)` 命中即认为是覆盖计划；`getPlanParts` 不匹配时抛 `CatalogApiException(CAT_NO_SUCH_PLAN)`。
- 持久化路径：`DefaultPriceOverrideSvc` 在 context 非空时生成 `parentPlan-<recordId>`（第 124 行）；dry-run 时生成 `parentPlan-dryrun-<自增序号>`（第 126 行）。
- 缓存键：`planName!<catalogEffectiveDateMillis>`（`DefaultOverriddenPlanCache` 第 101 行），确保覆盖计划不跨目录版本串用。

**注意**：加载路径 `getPlanName(parts)` 用配置的分隔符重新拼接，识别路径 `isOverriddenPlan` 用同一正则；若历史数据用了与当前配置不一致的分隔符，可能识别失败。

## ENT-047 InternationalPrice 的覆盖构造语义（逐币种替换）

- **类型**: 业务实体
- **同义词**: 多币种价格, 覆盖替换, 保留未覆盖币种, international price override, per-currency override
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:55-100`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:138-156`

**覆盖构造规则**：
- `DefaultInternationalPrice(in, override, fixed)`：若原价格**没有任何 price**（`prices.length == 0`），则新建**仅含覆盖币种**的一条价格（值取 fixed 或 recurring 覆盖价）。
- 若原有 price 列表非空，则**仅替换币种匹配的那一条**，其它币种原样保留。
- `DefaultInternationalPrice(in, overriddenPrice, currency)`（块价覆盖）同理：逐条替换匹配币种，其余保留。

**取值**：
- `getPrice(currency)`：`prices.length == 0` → 返回 `BigDecimal.ZERO`（视为所有币种零价）；有列表但无该币种 → 抛 `CAT_NO_PRICE_FOR_CURRENCY`。
- `isZero()`：遍历所有 price，只要存在某币种值 ≠ 0 即 false；`CurrencyValueNull`（value 为 null）按 0 处理。

## ENT-048 支付 Payment

- **类型**: 业务实体
- **同义词**: 支付, 支付单, 付款, payment, payment record, 支付记录
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dao/PaymentModelDao.java:40-52`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentModelDao.java:173-179`

**关键字段**：`accountId`（所属账户）、`paymentMethodId`（使用的支付方式）、`paymentNumber`（账户内支付序号）、`externalKey`（外部键，默认取 UUID）、`stateName`（当前支付状态）、`lastSuccessStateName`（最近一次成功状态，用于失败后重试）。

**存储**：表 `payments`（`TableName.PAYMENTS`），历史表 `payment_history`。一个 Payment 可包含多笔不同 TransactionType 的交易（如先 AUTHORIZE 后 CAPTURE）。

## ENT-049 支付交易 PaymentTransaction

- **类型**: 业务实体
- **同义词**: 支付交易, 交易, 交易记录, payment transaction, transaction, 支付明细
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dao/PaymentTransactionModelDao.java:38-49`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentTransactionModelDao.java:272-279`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentTransaction.java:31-43`

**关键字段**：`paymentId`（所属支付）、`attemptId`（所属支付尝试）、`transactionExternalKey`、`transactionType`（7 种之一）、`effectiveDate`、`transactionStatus`（`TransactionStatus`）、`amount`/`currency`、`processedAmount`/`processedCurrency`（实际处理金额与币种，可能与请求金额不同）、`gatewayErrorCode`/`gatewayErrorMsg`（网关错误码/信息）。

**存储**：表 `payment_transactions`，历史表 `payment_transaction_history`。

## ENT-050 支付方式 PaymentMethod

- **类型**: 业务实体
- **同义词**: 支付方式, 付款方式, 银行卡, 信用卡, payment method, card, 支付工具
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentMethod.java:31-45`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentMethodModelDao.java:149-156`

**关键字段**：`accountId`（所属账户）、`externalKey`、`isActive`、`pluginName`（由哪个支付插件管理，如网关插件或 `__EXTERNAL_PAYMENT__`）、`pluginDetail`（插件侧的支付方式明细）。

**存储**：表 `payment_methods`，历史表 `payment_method_history`。账户的默认支付方式由账户上的 `paymentMethodId` 指向（见 BR-238）。

## ENT-051 支付尝试 PaymentAttempt

- **类型**: 业务实体
- **同义词**: 支付尝试, 扣款尝试, 重试记录, payment attempt, attempt, 支付尝试记录
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dao/PaymentAttemptModelDao.java:40-50`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentAttemptModelDao.java:238-245`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentAttempt.java:29-40`

**关键字段**：`accountId`、`paymentMethodId`、`paymentExternalKey`、`transactionId`/`transactionExternalKey`、`transactionType`、`stateName`、`amount`/`currency`、`pluginName`（含支付控制插件名列表，逗号分隔）、`pluginProperties`（序列化后的插件属性）。

**存储**：表 `payment_attempts`，历史表 `payment_attempt_history`。支付尝试是控制类支付（invoice payment）与失败重试的关联主体，重试队列以 `attemptId` 定位任务。

## ENT-052 发票支付 InvoicePayment

- **类型**: 业务实体
- **同义词**: 发票支付, 发票付款记录, invoice payment, 发票扣款记录, 支付与发票关联
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/api/DefaultInvoicePaymentApi.java:60-63`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:168-206`

**定义**：InvoicePayment 表示一笔 payment 与一张 invoice 的关联记录，含 `type`（如 `InvoicePaymentType.ATTEMPT`）、`status`（`InvoicePaymentStatus`：INIT/SUCCESS/PENDING）、`paymentCookieId`（关联的 payment transaction externalKey）、金额与币种。支付成功后由控制插件调用 `invoiceApi.recordPaymentAttemptCompletion` 写回。

## ENT-053 支付尝试(PaymentAttempt) 与 支付交易(PaymentTransaction) 的 1:0..1 关系

- **类型**: 业务实体
- **同义词**: 尝试与交易关系, attempt transaction relationship, attempt_id, 一对多, 重试明细, payment attempt vs transaction
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dao/PaymentAttemptModelDao.java:40-50`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentTransactionModelDao.java:38-49`, `payment/src/main/resources/org/killbill/billing/payment/ddl.sql:3-31`, `payment/src/main/resources/org/killbill/billing/payment/ddl.sql:152-180`

**结构**：
- `payment_attempts.attempt_id` 不是列名；交易侧通过 `payment_transactions.attempt_id`（nullable，varchar 36）指向尝试行 `payment_attempts.id`。
- `payment_attempts.transaction_id`（nullable）反向指向最新交易 `payment_transactions.id`。
- 因此一个 **attempt 至多关联一个 transaction**（每次重试新建一个 attempt + 一个新 transaction），但一次 payment 可有多个 attempt（多行重试历史）。
- 索引：`payment_transactions.transactions_*` 与 `payment_attempts_payment_transaction_key`（按 `transaction_external_key`）、`payment_attempts_payment_key`（按 `payment_external_key`）、`payment_attempts_payment_state`（按 `state_name`）。

**尝试行的插件字段**：`plugin_name`（varchar 1024）保存**控制插件名列表**（逗号分隔，`PaymentAttemptModelDao.toPluginControlPluginNames()` 用 `,` 拆分）；`plugin_properties`（mediumblob）保存序列化后的插件属性，RETRIED 时由 `DefaultControlCompleted` 写入（控制插件可在此之前擦除敏感信息如 CVV）。

## ENT-054 未来重试的"虚拟" SCHEDULED 支付尝试

- **类型**: 业务实体
- **同义词**: 计划中尝试, future attempt, SCHEDULED, 待重试, retry projection, withAttempts
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentRefresher.java:531-590`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentRefresher.java:91`

**定义**：查询支付时若 `withAttempts=true`，Kill Bill 除了返回 `payment_attempts` 中的历史尝试，还会**把 retry 队列里的未来通知投影为一条虚拟 PaymentAttempt**：

- `stateName = "SCHEDULED"`（常量，**不是** RetryStates.xml 的合法状态）；
- `id` = 通知负载里的 `attemptId`；`effectiveDate` = 通知的 `effectiveDate`；`createdDate/updatedDate = null`；`transactionId = null`；
- 其余字段（金额、币种、支付外部键、交易外部键、交易类型、插件属性）取自最近一条同 attemptId 的历史 attempt；
- `pluginName` 取 `PaymentRetryNotificationKey.getPaymentControlPluginNames().get(0)`（**只取第一个**）。

**含义**：`SCHEDULED` 只存在于读取视图，代表"已排期但尚未执行"；不要期望在 `payment_attempts` 表里看到该状态。

## ENT-055 payments 表的唯一约束与状态索引

- **类型**: 业务实体
- **同义词**: payments 表约束, 支付唯一键, external_key 唯一, state_name 索引, payment table constraints
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/resources/org/killbill/billing/payment/ddl.sql:105-127`, `payment/src/main/resources/org/killbill/billing/payment/ddl.sql:61-81`, `payment/src/main/resources/org/killbill/billing/payment/ddl.sql:152-180`

**约束与索引**：
- `payments`：`(external_key, tenant_record_id)` **唯一**（`payments_key`）、`id` 唯一；索引 `payments_accnt(account_id)`、`payments_tenant_record_id_state_name(tenant_record_id, state_name)`（支撑按支付状态排查/审计）。
- `payment_methods`：`(external_key, tenant_record_id)` **唯一**、`id` 唯一；索引 `plugin_name`、`(tenant_record_id, account_record_id)`。
- `payment_transactions`：`id` 唯一；索引 `payment_id`、`transaction_external_key`、`transaction_status`、`(tenant_record_id, account_record_id)`——注意 `transaction_external_key` **不唯一**（同一 key 可有多条重试交易）。
- 历史表 `payment_history`/`payment_attempt_history`/`payment_transaction_history` 均含 `change_type` 与 `target_record_id`。

**含义**：一个租户内 `payment.external_key` 不可重复；但同一 `transaction_external_key` 在重试下会产生多条交易（靠 `attempt_id` 区分）。

## ENT-056 用量记录实体 / rolled_up_usage 表

- **类型**: 业务实体
- **同义词**: 用量记录实体, 用量表, 用量记录表, rolled_up_usage, RolledUpUsageModelDao, usage table, usage record entity
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/dao/RolledUpUsageModelDao.java:30-51`, `usage/src/main/resources/org/killbill/billing/usage/ddl.sql:3-22`

**字段**：
- `subscriptionId`（订阅 ID，逻辑外键 → subscriptions）
- `unitType`（单位类型，字符串）
- `recordDate`（记录时刻，`datetime NOT NULL`，精确到时刻，非仅日期）
- `amount`（数值，`decimal(18,9) NOT NULL`）
- `trackingId`（跟踪号，`varchar(128) NOT NULL`）
- 框架字段：`id`(uuid, unique)、`record_id`(serial PK)、`created_by`、`created_date`、`account_record_id`、`tenant_record_id`

**关键约束**：
- 唯一索引仅在 `id` 上（`rolled_up_usage_id`），**没有** `(subscription_id, unit_type, record_date)` 之类的业务键唯一约束（见 BR-289）。
- 索引：`subscription_id`、`(tenant_record_id, account_record_id)`、`account_record_id`、`(tracking_id, subscription_id, tenant_record_id)`。
- 无历史/审计表：`getHistoryTableName()` 返回 `null`（见 SM-014）。

---

## ENT-057 汇总用量视图（RolledUpUsage）

- **类型**: 业务实体
- **同义词**: 汇总用量, 用量汇总结果, rolled up usage, RolledUpUsage, usage view, usage response
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultRolledUpUsage.java:27-59`

**结构**：`subscriptionId` + `start` + `end` + `List<RolledUpUnit> rolledUpUnits`。

**来源**：由 `getUsageForSubscription` / `getAllUsageForSubscription` 构造；数据来自插件（`getRolledUpUnitsForRawPluginUsage`）或 DB（`getRolledUpUnits`）。

**对外序列化**：REST 返回 `RolledUpUsageJson`（`subscriptionId`/`startDate`/`endDate`/`rolledUpUnits[]`），见 `jaxrs/src/main/java/org/killbill/billing/jaxrs/json/RolledUpUsageJson.java:33-95`。

---

## ENT-058 汇总单位（RolledUpUnit）

- **类型**: 业务实体
- **同义词**: 汇总单位, 单位用量, rolled up unit, RolledUpUnit, unit amount, 单位汇总
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultRolledUpUnit.java:24-42`

**结构**：`unitType` + `amount`（该单位类型在查询区间内的累计值）。

**语义**：一个 `RolledUpUsage` 可含多个 `RolledUpUnit`（不同单位类型各一）；同一单位类型只出现一次（聚合结果）。

---

## ENT-059 订阅用量提交记录（SubscriptionUsageRecord）

- **类型**: 业务实体
- **同义词**: 订阅用量提交, 用量提交对象, subscription usage record, SubscriptionUsageRecord, usage submission, 上报用量
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/json/SubscriptionUsageRecordJson.java:36-126`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:71-92`

**结构**（提交用）：
- `subscriptionId`（必填）
- `trackingId`（可选；批量去重键）
- `List<UnitUsageRecord>`（至少一条）

**含义**：`recordRolledUpUsage` 的入参。一个提交批次由「一个订阅 + 多个单位类型 + 每个单位类型下多条带日期数值」组成。REST 层对应 `SubscriptionUsageRecordJson`（嵌套 `UnitUsageRecordJson` → `UsageRecordJson{recordDate, amount}`）。

---

## ENT-060 单位用量记录（UnitUsageRecord）

- **类型**: 业务实体
- **同义词**: 单位用量, 单位计量记录, unit usage record, UnitUsageRecord, unit type record
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/json/SubscriptionUsageRecordJson.java:66-93`

**结构**：`unitType`（单位类型）+ `List<UsageRecord> dailyAmount`（该单位类型下多条按日期的用量）。提交时其 `unitType` 会写入 `rolled_up_usage.unit_type`。

---

## ENT-061 用量记录值（UsageRecord）

- **类型**: 业务实体
- **同义词**: 用量记录值, 用量条目, usage record, UsageRecord, recordDate, amount, 计量值
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/json/SubscriptionUsageRecordJson.java:95-119`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:87-89`

**结构**：`recordDate`（`DateTime`）+ `amount`（`BigDecimal`）。前者落库为 `record_date`，后者为 `amount`。

---

## ENT-062 原始用量记录（RawUsageRecord / DefaultRawUsage）

- **类型**: 业务实体
- **同义词**: 原始用量, 原始用量记录, raw usage, RawUsageRecord, DefaultRawUsage, raw usage detail
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultRawUsage.java:26-65`, `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultInternalUserApi.java:80-83`

**结构**：`subscriptionId`、`date`、`unitType`、`amount`、`trackingId`。

**来源**：DB 行 `RolledUpUsageModelDao` → `DefaultRawUsage` 映射（`getRawUsageForAccount`），或直接来自插件 `UsagePluginApi.getUsageForAccount(...)`。

**消费方**：开票侧 `RawUsageOptimizer`（`invoice/.../usage/RawUsageOptimizer.java:85-98`）。

---

## ENT-063 用量 DAO（RolledUpUsageDao / RolledUpUsageSqlDao）

- **类型**: 业务实体
- **同义词**: 用量DAO, 用量持久化, rolled up usage dao, RolledUpUsageDao, RolledUpUsageSqlDao, usage repository
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/dao/RolledUpUsageDao.java:26-37`, `usage/src/main/java/org/killbill/billing/usage/dao/DefaultRolledUpUsageDao.java:36-69`, `usage/src/main/java/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.java:33-57`

**能力**：
- `record(usages, context)` — 批量插入
- `recordsWithTrackingIdExist(subscriptionId, trackingId, context)` — 去重探测
- `getUsageForSubscription(...)` — 单单位类型区间查询
- `getAllUsageForSubscription(...)` — 全单位类型区间查询
- `getRawUsageForAccount(...)` — 按账户查原始用量

**路由**：`DefaultRolledUpUsageDao` 使用 `DBRouter`，读操作走只读库（`onDemand(true)`），写操作 `onDemand(false)`。SQL 由 `RolledUpUsageSqlDao.sql.stg` 字符串模板生成，表名 `rolled_up_usage`。

---

## ENT-064 用量插件注册表（Usage Provider Registry）

- **类型**: 业务实体
- **同义词**: 用量插件注册表, 用量提供者注册, usage plugin registry, DefaultUsageProviderPluginRegistry, usage provider, OSGI 用量插件
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/glue/DefaultUsageProviderPluginRegistry.java:30-66`, `usage/src/main/java/org/killbill/billing/usage/glue/UsageModule.java:53-64`

**结构**：`ConcurrentHashMap<String, UsagePluginApi> pluginsByName`，按插件注册名索引。提供 `registerService` / `unregisterService` / `getServiceForName` / `getAllServices` / `getServiceType`。

**装配**：`UsageModule.installUsagePluginApi()` 把 `OSGIServiceRegistration<UsagePluginApi>` 绑定到 `DefaultUsageProviderPluginRegistryProvider`（单例）。

---

## ENT-065 内部用量 API（InternalUserApi）

- **类型**: 业务实体
- **同义词**: 内部用量接口, 开票用量接口, internal user api, InternalUserApi, getRawUsageForAccount, 内部API
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `api/src/main/java/org/killbill/billing/usage/InternalUserApi.java:28-31`, `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultInternalUserApi.java:63-84`

**方法**：`List<RawUsageRecord> getRawUsageForAccount(startDate, endDate, dryRunInfo, pluginProperties, tenantContext)`。

**用途**：专供开票模块按账户拉取区间内所有订阅的原始用量（含 dry-run）。它是用量模块向外暴露的「内部」读接口，与面向用户的 `UsageUserApi` 并列（见 WF-036）。

---

## ENT-066 目录档位（Tier）

- **类型**: 业务实体
- **同义词**: 档位, 阶梯, 计费档, usage tier, Tier, DefaultTier, tier, 档
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:47-61`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:94-113`

**字段**：

- `limits`（`DefaultLimit[]`）：CAPACITY 用。
- `blocks`（`DefaultTieredBlock[]`）：CONSUMABLE 用。
- `fixedPrice`（`InternationalPrice`，可空）。
- `recurringPrice`（`InternationalPrice`，可空）。

**关键点**：**CAPACITY IN_ARREAR 计价只读 `recurringPrice`**（`ContiguousIntervalCapacityUsageInArrear.java:125`），`fixedPrice` 不参与 in-arrear usage 定价（尽管目录允许定义）。tiers 的顺序即档位匹配优先级（见 BR-299）。

**档级校验**：`DefaultTier.validate` 要求 IN_ARREAR CAPACITY 必须定义 limits、IN_ARREAR CONSUMABLE 必须定义 blocks（见 BR-315）。

---

## ENT-067 用量计价明细（UsageInArrearTierUnitDetail）

- **类型**: 业务实体
- **同义词**: 用量计价明细, 档位单位明细, 计价明细, usage tier unit detail, UsageInArrearTierUnitDetail, tier detail, quantity
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/details/UsageInArrearTierUnitDetail.java:26-59`

**结构**：`tier`（档号，从 1 起）、`tierUnit`（单位类型）、`tierPrice`（该档单价）、`quantity`。

**用途**：作为 `itemDetails` 序列化进 USAGE 发票项（JSON 字段名 `tier`/`tierUnit`/`tierPrice`/`quantity`），用于事后对账/补开时还原分档用量（见 BR-306/BR-307）。CAPACITY 与 CONSUMABLE 的聚合明细都继承自此。

---

## ENT-068 消费型分档明细（UsageConsumableInArrearTierUnitAggregate）

- **类型**: 业务实体
- **同义词**: 消费型明细, 分档计价明细, consumable 明细, UsageConsumableInArrearTierUnitAggregate, tierBlockSize, consumable aggregate
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/details/UsageConsumableInArrearTierUnitAggregate.java:28-84`

**结构**：继承 `UsageInArrearTierUnitDetail`，额外含 `tierBlockSize`（块大小）、`amount`。

**计价公式**：`amount = tierPrice × quantity`（`computeAmount`，`UsageConsumableInArrearTierUnitAggregate.java:82-84`）。

**累加语义**：`updateQuantityAndAmount(additionalQuantity)` 把 quantity 加上并用新 quantity 重算 amount（`UsageConsumableInArrearTierUnitAggregate.java:77-80`），用于把**同一档**在多次已开票明细中的量合并（见 BR-306）。

---

## ENT-069 容量型聚合（UsageCapacityInArrearAggregate）

- **类型**: 业务实体
- **同义词**: 容量型聚合, 容量计价结果, capacity aggregate, UsageCapacityInArrearAggregate, capacity tier detail
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/details/UsageCapacityInArrearAggregate.java:26-48`

**结构**：`tierDetails`（`List<UsageInArrearTierUnitDetail>`，每个参与计价的单位类型一条）+ `amount`（该区间的应计金额，来自所命中档的 `recurringPrice`；若所有单位用量均 ≤ 0 则 `amount=0`，见 BR-300）。实现 `UsageInArrearAggregate`（只暴露 `getAmount()`）。

---

## ENT-070 消费型聚合（UsageConsumableInArrearAggregate）

- **类型**: 业务实体
- **同义词**: 消费型聚合, 消费计价结果, consumable aggregate, UsageConsumableInArrearAggregate
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/details/UsageConsumableInArrearAggregate.java:26-56`

**结构**：`tierDetails`（`List<UsageConsumableInArrearTierUnitAggregate>`，每档一条）+ `amount`。`amount = Σ tierDetails.amount`（构造时 `computeAmount` 求和，`UsageConsumableInArrearAggregate.java:50-56`）。这即是 ALL_TIERS「逐档求和」的实现（见 BR-302）。

---

## ENT-071 目录单位（DefaultUnit）

- **类型**: 业务实体
- **同义词**: 目录单位, 单位定义, 计量单位名, catalog unit, DefaultUnit, Unit, unit name, prettyName
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUnit.java:36-51`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultUnit.java:64-71`

**结构**：`name`（唯一 ID）+ `prettyName`（可空，缺省初始化为 `name`）。catalog 的 `<units><unit name="..."/></units>` 定义；tier 的 limit/block 通过引用该 name 绑定。

**与用量记录的关系**：写入 `rolled_up_usage.unit_type` 的字符串必须等于该 `name`，开票侧才能把用量对上价（大小写/拼写敏感）。

---

## ENT-072 原始用量拉取结果（RawUsageOptimizer.RawUsageResult）

- **类型**: 业务实体
- **同义词**: 原始用量结果, 拉取用量结果, raw usage result, RawUsageResult, existingTrackingIds, 已开票跟踪号
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/RawUsageOptimizer.java:212-229`, `invoice/src/main/java/org/killbill/billing/invoice/usage/RawUsageOptimizer.java:85-98`

**结构**：`rawUsage`（`List<RawUsageRecord>`，来自 `InternalUserApi.getRawUsageForAccount`）+ `existingTrackingIds`（`Set<TrackingRecordId>`，该账户在拉取区间内**已开票**的用量跟踪号，来自 `invoiceDao.getTrackingsByDateRange`）。

**用途**：开票侧据此区分「本次新用量」与「已开票用量」，实现发票级去重与补开（见 BR-319）。

---
