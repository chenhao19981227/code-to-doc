# 业务实体 (Entities)


> 由 .bizdoc-kb2/cards 合成；本文件共 46 张卡。

## ENT-001 产品实体 (Product)

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

## ENT-002 计划实体 (Plan)

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

## ENT-003 计划阶段实体 (Plan Phase)

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

## ENT-004 价格表实体与价格表集合 (PriceList / PriceListSet)

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

## ENT-005 目录实体 (StandaloneCatalog / StaticCatalog)

- **类型**: 业务实体
- **同义词**: 目录, 目录定义, 单一目录, catalog, StandaloneCatalog, StaticCatalog, 静态目录
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:62-95`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:280-310`

**实体说明**：`StandaloneCatalog` 实现 `StaticCatalog`，是一次目录发布的完整定义。

**关键字段/关系**：`effectiveDate`、`catalogName`、`recurringBillingMode`（目录级缺省计费模式）、`supportedCurrencies`、`units`、`products`、`plans`、`priceLists`、`rules`（`DefaultPlanRules`）。

**校验**：产品集合、计划集合、价格表、规则集依次校验；并校验阶段时长（EVERGREEN 必须 UNLIMITED，非 EVERGREEN 不得 UNLIMITED）。

## ENT-006 价格实体 (Price / InternationalPrice)

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

## ENT-007 时长实体 (Duration)

- **类型**: 业务实体
- **同义词**: 时长, 阶段时长, 持续时间, duration, Duration, TimeUnit, 天数, 月数, 年数
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultDuration.java:41-83`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultDuration.java:106-123`

**实体说明**：`Duration` = `unit`（TimeUnit）+ `number`。

**关键约束**：
- TimeUnit 取值 `DAYS`/`WEEKS`/`MONTHS`/`YEARS`/`UNLIMITED`；对 `UNLIMITED` 执行 `addToDateTime`/`toJodaPeriod` 会抛 `CAT_UNDEFINED_DURATION` 或 IllegalStateException。
- `UNLIMITED` 时 number 必须省略；有限时长必须给出 number，否则校验失败。

## ENT-008 周期费实体 (Recurring)

- **类型**: 业务实体
- **同义词**: 周期费, 循环费用, 订阅费, 月费, recurring, Recurring, recurringPrice, 周期性收费
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultRecurring.java:39-113`

**实体说明**：阶段的周期性收费，由 `billingPeriod`（BillingPeriod）+ 可选 `recurringPrice`（InternationalPrice）组成。

**关键约束**：有 recurringPrice 就必须有有效的 billingPeriod（非 `NO_BILLING_PERIOD`）；没有 recurringPrice 则 billingPeriod 必须是 `NO_BILLING_PERIOD`。

## ENT-009 块与阶梯块实体 (Block / TieredBlock)

- **类型**: 业务实体
- **同义词**: 用量块, 充值块, 阶梯块, block, Block, tieredBlock, TieredBlock, usage block
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:47-64`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTieredBlock.java:36-65`

**实体说明**：`Block` 定义「一个单位块」的价格：`type`、`unit`、`size`（每块包含的单位数）、`prices`（块价）、可选 `minTopUpCredit`。`TieredBlock` 继承 Block 并额外有 `max`（该阶梯的最大用量），固定 `type=TIERED`。

## ENT-010 目录版本集合实体 (VersionedCatalog)

- **类型**: 业务实体
- **同义词**: 目录版本集合, 多版本目录, versioned catalog, VersionedCatalog, versions
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:52-120`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:133-154`

**实体说明**：`DefaultVersionedCatalog` 持有按 `effectiveDate` 升序排列的多个 `StandaloneCatalog` 版本。

**关键约束**：各版本 `catalogName` 必须一致；`effectiveDate` 不得重复；跨版本同名计划的阶段数量与阶段名必须一致。

## ENT-011 规则集实体 (PlanRules)

- **类型**: 业务实体
- **同义词**: 规则集, 计划规则, 目录规则, plan rules, PlanRules, DefaultPlanRules, 变更规则, 取消规则
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:58-83`

**实体说明**：`DefaultPlanRules` 聚合六类规则 case：`changePolicy`（变更策略）、`changeAlignment`（变更对齐）、`cancelPolicy`（取消策略）、`createAlignment`（创建对齐）、`billingAlignment`（计费对齐）、`priceList`（价格表选择）。

**关键约束**：变更策略与取消策略必须各存在一个「全空」的默认 case，且同类规则不得重复。

## ENT-012 阶段计费项实体 (Fixed / Usage / Tier / Limit)

- **类型**: 业务实体
- **同义词**: 计费项, 价格组成, 阶段内容, billing items, fixed, usage, tier, limit
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:61-72`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:74-95`

**实体说明**：一个阶段最多由四类计费项构成：`fixed`（一次性固定费）、`recurring`（周期费）、`usages[]`（用量段，内部再含 tiers/blocks/limits）、以及各计费项级别的 `limits`。

**关键约束**：阶段必须至少含 fixed / recurring / usages 之一。

## ENT-013 发票（Invoice）

- **类型**: 业务实体
- **同义词**: 发票, invoice, Invoice, 账单, 单据
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoice.java:44-127`

**说明**：发票实体关键属性：`accountId`、`invoiceNumber`（发票号）、`invoiceDate`（开票日期）、`targetDate`（目标日期）、`currency`/`processedCurrency`、`status`（DRAFT/COMMITTED/VOID）、`isMigrationInvoice`、`isWrittenOff`（核销）、`isParentInvoice`、`parentInvoice`（父发票，用于 HA/父子账户）、`grpId`（分组 id，用于一次开票产生的多张发票归组）。
**关系**：一张发票包含多个 `InvoiceItem` 与多个 `InvoicePayment`（支付）。

## ENT-014 账户信用余额调整项（CreditBalanceAdjInvoiceItem / CBA）

- **类型**: 业务实体
- **同义词**: 信用余额调整项, CBA项, credit balance adjustment item, CBA_ADJ, 账户信用项
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:243-251`, `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:78-80`

**说明**：`CreditBalanceAdjInvoiceItem` 是类型为 `CBA_ADJ` 的发票项，用于表示账户信用余额的变化（消费或累积）。构建时以传入金额的负值 `amount.negate()` 记账。

## ENT-015 用量发票项（UsageInvoiceItem）

- **类型**: 业务实体
- **同义词**: 用量发票项, 使用量条目, usage invoice item, UsageInvoiceItem, USAGE item, 用量明细
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:345-356`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:573-597`

**说明**：类型为 `USAGE` 的发票项，记录某订阅某用量在 `[startDate, endDate)` 区间的费用。关键字段：`usageName`（用量名，与目录一致）、`startDate`/`endDate`（计费区间）、`amount`、`itemDetails`（用量明细聚合的 JSON）。去重与“已计费金额”比较均基于 usageName + 区间。

## ENT-016 父汇总发票项（ParentInvoiceItem / PARENT_SUMMARY）

- **类型**: 业务实体
- **同义词**: 父汇总项, 父子账户, parent summary, PARENT_SUMMARY, ParentInvoiceItem, HA 发票项
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1380-1396`, `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:82-85`

**说明**：类型为 `PARENT_SUMMARY` 的发票项，挂在**父账户的父发票**上，用于汇总某个子账户的发票金额。关键字段：`childAccountId`（对应子账户）、`amount`、`description`（`<子账户externalKey> summary`）。

## ENT-017 发票支付 (InvoicePayment)

- **类型**: 业务实体
- **同义词**: 发票支付, 支付记录, invoice payment, InvoicePayment, 付款, 退款记录, 发票付款记录, 发票扣款记录, 支付与发票关联
- **模块**: invoice, payment
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoicePayment.java:34-72`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultInvoicePaymentApi.java:60-63`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:168-206`

**说明**：表示发票上的一条支付/退款记录，属性：`type`（InvoicePaymentType：ATTEMPT/REFUND/CHARGED_BACK）、`paymentId`、`invoiceId`、`paymentDate`、`amount`、`currency`、`processedCurrency`、`paymentCookieId`、`linkedInvoicePaymentId`（关联的支付，如退款关联原支付）、`status`（InvoicePaymentStatus，默认 `SUCCESS`）。

**定义**：InvoicePayment 表示一笔 payment 与一张 invoice 的关联记录，含 `type`（如 `InvoicePaymentType.ATTEMPT`）、`status`（`InvoicePaymentStatus`：INIT/SUCCESS/PENDING）、`paymentCookieId`（关联的 payment transaction externalKey）、金额与币种。支付成功后由控制插件调用 `invoiceApi.recordPaymentAttemptCompletion` 写回。

## ENT-018 周期发票项（RecurringInvoiceItem）

- **类型**: 业务实体
- **同义词**: 周期项, 订阅费, 月费, recurring item, RecurringInvoiceItem, RECURRING, 订阅周期费用
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/RecurringInvoiceItem.java:33-57`, `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:260-278`

**说明**：类型为 `RECURRING` 的发票项，表示按 billingPeriod 重复收取的订阅费。含 `bundleId`/`subscriptionId`、`productName`/`planName`/`phaseName`、`catalogEffectiveDate`、`startDate`/`endDate`、`amount`、`rate`。生成时 `amount = 周期数 × rate × quantity`（`rate` 为每周期单价，`quantity` 默认 1）。

## ENT-019 固定费用发票项（FixedPriceInvoiceItem）

- **类型**: 业务实体
- **同义词**: 固定费用, 一次性费用, 初装费, fixed price, FixedPriceInvoiceItem, FIXED, 固定价
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/FixedPriceInvoiceItem.java:32-66`, `invoice/src/main/java/org/killbill/billing/invoice/model/FixedPriceInvoiceItem.java:98-114`

**说明**：类型为 `FIXED` 的发票项，表示阶段（phase）开始时一次性收取的固定费用（无 `rate`，只有金额与日期）。描述默认 `"Fixed price charge"`；若有 phase 名则默认 `<phase> (fixed price)`。

## ENT-020 外部收费发票项（ExternalChargeInvoiceItem）

- **类型**: 业务实体
- **同义词**: 外部收费, 手动收费, 附加费用, external charge, ExternalChargeInvoiceItem, EXTERNAL_CHARGE, 额外收费
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/ExternalChargeInvoiceItem.java:32-58`, `invoice/src/main/java/org/killbill/billing/invoice/model/ExternalChargeInvoiceItem.java:91-103`

**说明**：类型为 `EXTERNAL_CHARGE` 的发票项，用于在订阅计费之外手动/外部加收费用，可关联 bundle/subscription。描述默认 `"External charge"` 或 `<plan> (external charge)`。

## ENT-021 逾期状态 OverdueState

- **类型**: 业务实体
- **同义词**: 逾期状态, 催收阶段, 逾期等级, overdue state, dunning stage, DefaultOverdueState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:44-72`

**关键字段/关系**：`name`（必填，XML `@XmlID`，最长 50）、`condition`（DefaultOverdueCondition，可空）、`externalMessage`（默认 ""）、`blockChanges`（默认 false）、`disableEntitlementAndChangesBlocked`（默认 false）、`subscriptionCancellationPolicy`（默认 NONE）、`isClearState`（默认 false）、`autoReevaluationInterval`（DefaultDuration，可空）、`enterStateEmailNotification`（**已废弃**，仅保留配置兼容）。
**关系**：隶属于账户状态集 `accountOverdueStates`；被包装为 `BlockingState` 持久化（服务名 overdue-service，类型 ACCOUNT）。

## ENT-022 逾期条件 OverdueCondition

- **类型**: 业务实体
- **同义词**: 逾期条件, 催收触发条件, overdue condition, dunning condition, DefaultOverdueCondition
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:48-67`

**关键字段**：`numberOfUnpaidInvoicesEqualsOrExceeds`(Integer)、`totalUnpaidInvoiceBalanceEqualsOrExceeds`(BigDecimal)、`timeSinceEarliestUnpaidInvoiceEqualsOrExceeds`(DefaultDuration)、`responseForLastFailedPayment`(PaymentResponse[]，XML wrapper `responseForLastFailedPaymentIn`/子元素 `response`)、`controlTagInclusion`(ControlTagType)、`controlTagExclusion`(ControlTagType)。
**关系**：实现 `ConditionEvaluation.evaluate(BillingState, LocalDate)`；被 `OverdueState` 持有，被 `OverdueStateSet.calculateOverdueState` 调用。

## ENT-023 账户逾期状态集 OverdueStatesAccount / OverdueStateSet

- **类型**: 业务实体
- **同义词**: 账户状态集, 逾期状态集合, 催收规则集, account overdue states, overdue state set, OverdueStatesAccount
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:33-40`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:35-96`, `api/src/main/java/org/killbill/billing/overdue/config/api/OverdueStateSet.java:24-45`

**关键字段/关系**：`initialReevaluationInterval`（DefaultDuration）+ `state[]`（有序状态数组）；继承内建 `clearState`。核心行为：`findState(name)`、`getClearState()`、`calculateOverdueState(billingState, now)`（返回首个命中状态，否则 clear）、`size()`、`getFirstState()`（返回数组最后一个，即入门级逾期状态）。

## ENT-024 计费状态 BillingState

- **类型**: 业务实体
- **同义词**: 计费状态, 欠费快照, billing state, BillingState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `api/src/main/java/org/killbill/billing/overdue/config/api/BillingState.java:29-53`, `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:67-84`

**关键字段/关系**：由 `BillingStateCalculator` 从 InvoiceInternalApi（未付发票）、TagInternalApi（账户标签）、Clock（当前日）构造。是条件评估的唯一输入。注意 `responseForLastFailedPayment` 目前被硬编码为 `INSUFFICIENT_FUNDS`（TODO MDW），见 BR-007。

## ENT-025 逾期配置根 OverdueConfig

- **类型**: 业务实体
- **同义词**: 逾期配置, 催收配置, overdue config, DefaultOverdueConfig, overdueConfig, overdue.xml
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueConfig.java:35-52`, `overdue/src/main/resources/NoOverdueConfig.xml:20-27`

**关键字段/关系**：XML 根元素 `<overdueConfig>`，唯一必需子节点 `<accountOverdueStates>`（DefaultOverdueStatesAccount）。当前版本**只有账户级配置**（没有 bundle/subscription 级状态集）。`validate` 委托给 accountOverdueStates 校验。

## ENT-026 逾期包装器 OverdueWrapper

- **类型**: 业务实体
- **同义词**: 逾期包装器, 账户逾期执行器, overdue wrapper, OverdueWrapper
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:48-87`

**关键字段/关系**：绑定单个 Account（`overdueable`）+ OverdueStateSet + BillingStateCalculator + OverdueStateApplicator + GlobalLocker。对外能力：`refresh(effectiveDate, ctx)`、`getNextOverdueState`、`clear`、`billingState`。常量 `CLEAR_STATE_NAME`、`MAX_LOCK_RETRIES=50`。是「评估+施加」的编排门面（见 WF-001）。

## ENT-027 计费状态计算器 BillingStateCalculator

- **类型**: 业务实体
- **同义词**: 计费状态计算器, 欠费统计, billing state calculator, BillingStateCalculator
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:45-108`

**关键字段/关系**：依赖 InvoiceInternalApi、TagInternalApi、Clock。`unpaidInvoicesForAccount` 取未付发票并按 `getInvoiceDate()` 升序（同日期用 hashCode 稳定打破平局）；`sumBalance` 求和；`earliest` 取最早一张；`calculateBillingState` 组装 BillingState。

## ENT-028 逾期状态施加器 OverdueStateApplicator

- **类型**: 业务实体
- **同义词**: 逾期状态施加器, 状态执行器, overdue state applicator, OverdueStateApplicator
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:71-102`

**关键字段/关系**：依赖 BlockingInternalApi、AccountInternalApi、EntitlementApi/EntitlementInternalApi、TagInternalApi、OverduePoster(check)、BusOptimizer、InternalCallContextFactory。核心方法：`apply(...)`（状态切换+动作+事件+定时）、`clear(...)`、`storeNewState(...)`、`cancelSubscriptionsIfRequired(...)`、`isAccountTaggedWith_OVERDUE_ENFORCEMENT_OFF(...)`。

## ENT-029 逾期变更事件 OverdueChangeInternalEvent

- **类型**: 业务实体
- **同义词**: 逾期变更事件, 状态变更事件, overdue change event, OverdueChangeInternalEvent, OVERDUE_CHANGE
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/DefaultOverdueChangeEvent.java:28-58`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:215-219`

**关键字段/关系**：`overdueObjectId`、`previousOverdueStateName`、`nextOverdueStateName`、`isBlockedBilling`、`isUnblockedBilling`，`getBusEventType()=OVERDUE_CHANGE`。在 `apply`/`clear` 末尾经 BusOptimizer 投递；是 invoice 等下游模块感知逾期状态变化的通道。

## ENT-030 逾期通知键 OverdueCheckNotificationKey / OverdueAsyncBusNotificationKey

- **类型**: 业务实体
- **同义词**: 逾期通知键, 催收通知, overdue notification key, NotificationKey, REFRESH, CLEAR
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueCheckNotificationKey.java:26-31`, `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusNotificationKey.java:26-45`

**关键字段/关系**：`OverdueCheckNotificationKey` 持 `uuidKey`（账户 id，继承 DefaultUUIDNotificationKey）。`OverdueAsyncBusNotificationKey` 额外持 `action`，枚举 `OverdueAsyncBusNotificationAction{REFRESH, CLEAR}`——这是「异步总线入队」用的动作区分。

## ENT-031 逾期监听器 OverdueListener

- **类型**: 业务实体
- **同义词**: 逾期监听器, 事件监听器, overdue listener, OverdueListener
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:64-94`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-157`

**关键字段/关系**：订阅总线事件：控制标签创建/删除、发票创建、发票调整、支付信息、支付错误。除少数情况外统一转成 `REFRESH` 入 async bus 通知队列；`OVERDUE_ENFORCEMENT_OFF` 创建转 `CLEAR`。还会级联刷新父/子账户（见 BR-021）。

## ENT-032 时长配置 DefaultDuration

- **类型**: 业务实体
- **同义词**: 时长, 时间长度, 周期, duration, DefaultDuration, TimeUnit, DAYS, MONTHS
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:38-55`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:99-118`

**关键字段/关系**：`unit`(TimeUnit，必需，XML `<unit>`) + `number`(Integer，默认 -1，XML `<number>`)。支持 `DAYS/WEEKS/MONTHS/YEARS`，遇到 `UNLIMITED` 抛 IllegalStateException。`toJodaPeriod()` 用于条件/间隔计算。

## ENT-033 支付 Payment

- **类型**: 业务实体
- **同义词**: 支付, 支付单, 付款, payment, payment record, 支付记录
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dao/PaymentModelDao.java:40-52`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentModelDao.java:173-179`

**关键字段**：`accountId`（所属账户）、`paymentMethodId`（使用的支付方式）、`paymentNumber`（账户内支付序号）、`externalKey`（外部键，默认取 UUID）、`stateName`（当前支付状态）、`lastSuccessStateName`（最近一次成功状态，用于失败后重试）。

**存储**：表 `payments`（`TableName.PAYMENTS`），历史表 `payment_history`。一个 Payment 可包含多笔不同 TransactionType 的交易（如先 AUTHORIZE 后 CAPTURE）。

## ENT-034 支付交易 PaymentTransaction

- **类型**: 业务实体
- **同义词**: 支付交易, 交易, 交易记录, payment transaction, transaction, 支付明细
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dao/PaymentTransactionModelDao.java:38-49`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentTransactionModelDao.java:272-279`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentTransaction.java:31-43`

**关键字段**：`paymentId`（所属支付）、`attemptId`（所属支付尝试）、`transactionExternalKey`、`transactionType`（7 种之一）、`effectiveDate`、`transactionStatus`（`TransactionStatus`）、`amount`/`currency`、`processedAmount`/`processedCurrency`（实际处理金额与币种，可能与请求金额不同）、`gatewayErrorCode`/`gatewayErrorMsg`（网关错误码/信息）。

**存储**：表 `payment_transactions`，历史表 `payment_transaction_history`。

## ENT-035 支付方式 PaymentMethod

- **类型**: 业务实体
- **同义词**: 支付方式, 付款方式, 银行卡, 信用卡, payment method, card, 支付工具
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentMethod.java:31-45`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentMethodModelDao.java:149-156`

**关键字段**：`accountId`（所属账户）、`externalKey`、`isActive`、`pluginName`（由哪个支付插件管理，如网关插件或 `__EXTERNAL_PAYMENT__`）、`pluginDetail`（插件侧的支付方式明细）。

**存储**：表 `payment_methods`，历史表 `payment_method_history`。账户的默认支付方式由账户上的 `paymentMethodId` 指向（见 BR-011）。

## ENT-036 支付尝试 PaymentAttempt

- **类型**: 业务实体
- **同义词**: 支付尝试, 扣款尝试, 重试记录, payment attempt, attempt, 支付尝试记录
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dao/PaymentAttemptModelDao.java:40-50`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentAttemptModelDao.java:238-245`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentAttempt.java:29-40`

**关键字段**：`accountId`、`paymentMethodId`、`paymentExternalKey`、`transactionId`/`transactionExternalKey`、`transactionType`、`stateName`、`amount`/`currency`、`pluginName`（含支付控制插件名列表，逗号分隔）、`pluginProperties`（序列化后的插件属性）。

**存储**：表 `payment_attempts`，历史表 `payment_attempt_history`。支付尝试是控制类支付（invoice payment）与失败重试的关联主体，重试队列以 `attemptId` 定位任务。

## ENT-037 用量记录实体 / rolled_up_usage 表

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
- 唯一索引仅在 `id` 上（`rolled_up_usage_id`），**没有** `(subscription_id, unit_type, record_date)` 之类的业务键唯一约束（见 BR-008）。
- 索引：`subscription_id`、`(tenant_record_id, account_record_id)`、`account_record_id`、`(tracking_id, subscription_id, tenant_record_id)`。
- 无历史/审计表：`getHistoryTableName()` 返回 `null`（见 SM-001）。

## ENT-038 汇总用量视图（RolledUpUsage）

- **类型**: 业务实体
- **同义词**: 汇总用量, 用量汇总结果, rolled up usage, RolledUpUsage, usage view, usage response
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultRolledUpUsage.java:27-59`

**结构**：`subscriptionId` + `start` + `end` + `List<RolledUpUnit> rolledUpUnits`。

**来源**：由 `getUsageForSubscription` / `getAllUsageForSubscription` 构造；数据来自插件（`getRolledUpUnitsForRawPluginUsage`）或 DB（`getRolledUpUnits`）。

**对外序列化**：REST 返回 `RolledUpUsageJson`（`subscriptionId`/`startDate`/`endDate`/`rolledUpUnits[]`），见 `jaxrs/src/main/java/org/killbill/billing/jaxrs/json/RolledUpUsageJson.java:33-95`。

## ENT-039 汇总单位（RolledUpUnit）

- **类型**: 业务实体
- **同义词**: 汇总单位, 单位用量, rolled up unit, RolledUpUnit, unit amount, 单位汇总
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultRolledUpUnit.java:24-42`

**结构**：`unitType` + `amount`（该单位类型在查询区间内的累计值）。

**语义**：一个 `RolledUpUsage` 可含多个 `RolledUpUnit`（不同单位类型各一）；同一单位类型只出现一次（聚合结果）。

## ENT-040 订阅用量提交记录（SubscriptionUsageRecord）

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

## ENT-041 单位用量记录（UnitUsageRecord）

- **类型**: 业务实体
- **同义词**: 单位用量, 单位计量记录, unit usage record, UnitUsageRecord, unit type record
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/json/SubscriptionUsageRecordJson.java:66-93`

**结构**：`unitType`（单位类型）+ `List<UsageRecord> dailyAmount`（该单位类型下多条按日期的用量）。提交时其 `unitType` 会写入 `rolled_up_usage.unit_type`。

## ENT-042 用量记录值（UsageRecord）

- **类型**: 业务实体
- **同义词**: 用量记录值, 用量条目, usage record, UsageRecord, recordDate, amount, 计量值
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/json/SubscriptionUsageRecordJson.java:95-119`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:87-89`

**结构**：`recordDate`（`DateTime`）+ `amount`（`BigDecimal`）。前者落库为 `record_date`，后者为 `amount`。

## ENT-043 原始用量记录（RawUsageRecord / DefaultRawUsage）

- **类型**: 业务实体
- **同义词**: 原始用量, 原始用量记录, raw usage, RawUsageRecord, DefaultRawUsage, raw usage detail
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultRawUsage.java:26-65`, `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultInternalUserApi.java:80-83`

**结构**：`subscriptionId`、`date`、`unitType`、`amount`、`trackingId`。

**来源**：DB 行 `RolledUpUsageModelDao` → `DefaultRawUsage` 映射（`getRawUsageForAccount`），或直接来自插件 `UsagePluginApi.getUsageForAccount(...)`。

**消费方**：开票侧 `RawUsageOptimizer`（`invoice/.../usage/RawUsageOptimizer.java:85-98`）。

## ENT-044 用量 DAO（RolledUpUsageDao / RolledUpUsageSqlDao）

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

## ENT-045 用量插件注册表（Usage Provider Registry）

- **类型**: 业务实体
- **同义词**: 用量插件注册表, 用量提供者注册, usage plugin registry, DefaultUsageProviderPluginRegistry, usage provider, OSGI 用量插件
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/glue/DefaultUsageProviderPluginRegistry.java:30-66`, `usage/src/main/java/org/killbill/billing/usage/glue/UsageModule.java:53-64`

**结构**：`ConcurrentHashMap<String, UsagePluginApi> pluginsByName`，按插件注册名索引。提供 `registerService` / `unregisterService` / `getServiceForName` / `getAllServices` / `getServiceType`。

**装配**：`UsageModule.installUsagePluginApi()` 把 `OSGIServiceRegistration<UsagePluginApi>` 绑定到 `DefaultUsageProviderPluginRegistryProvider`（单例）。

## ENT-046 内部用量 API（InternalUserApi）

- **类型**: 业务实体
- **同义词**: 内部用量接口, 开票用量接口, internal user api, InternalUserApi, getRawUsageForAccount, 内部API
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `api/src/main/java/org/killbill/billing/usage/InternalUserApi.java:28-31`, `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultInternalUserApi.java:63-84`

**方法**：`List<RawUsageRecord> getRawUsageForAccount(startDate, endDate, dryRunInfo, pluginProperties, tenantContext)`。

**用途**：专供开票模块按账户拉取区间内所有订阅的原始用量（含 dry-run）。它是用量模块向外暴露的「内部」读接口，与面向用户的 `UsageUserApi` 并列（见 WF-004）。
