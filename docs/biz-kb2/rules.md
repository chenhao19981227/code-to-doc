# 业务规则 (Rules)


> 由 .bizdoc-kb2/cards 合成；本文件共 177 张卡。

## BR-001 初始阶段不能是 EVERGREEN

- **类型**: 业务规则
- **同义词**: 初始阶段约束, 起始阶段不能常青, initial phase evergreen, 阶段顺序规则, phase ordering
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:304-310`

**规则**：计划的每个 `initialPhase`（初始阶段）不得为 `PhaseType.EVERGREEN`；否则目录校验报错 `Initial Phase %s of plan %s cannot be of type EVERGREEN`。

**含义**：EVERGREEN 只能作为计划最后一个阶段（finalPhase），保证计划有明确的阶段性结构。

## BR-002 最终阶段不能是 TRIAL 或 DISCOUNT

- **类型**: 业务规则
- **同义词**: 最终阶段约束, 结束阶段不能试用, final phase trial, final phase discount, 阶段顺序规则
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:313-319`

**规则**：计划的 `finalPhase`（最终阶段）不得为 `PhaseType.TRIAL` 或 `PhaseType.DISCOUNT`；否则校验报错 `Final Phase %s of plan %s cannot be of type %s`。

**含义**：试用/折扣阶段只能出现在中间，最终阶段必须是 FIXEDTERM 或 EVERGREEN。

## BR-003 阶段必须至少定义一种计费项

- **类型**: 业务规则
- **同义词**: 阶段必填项, 阶段计价完整性, phase needs pricing, 空阶段校验
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:176-180`

**规则**：若一个阶段同时没有 `fixed`、没有 `recurring` 且 `usages` 为空，则校验失败，报错 `Phase %s of plan %s need to define at least either a fixed or recurrring or usage section.`。

## BR-004 阶段名与计划名互推规则

- **类型**: 业务规则
- **同义词**: 阶段命名, 计划名解析, phase name, plan name from phase, 阶段名后缀
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:104-115`

**规则**：
- 阶段名 = `planName + "-" + phaseType.toLowerCase()`。
- 反向解析：遍历 `PhaseType.values()`，看阶段名是否以某类型小写结尾，是则去掉「类型长度+1」个字符得到计划名；否则抛 `CAT_BAD_PHASE_NAME`。

**例外**：若计划名本身以某个 phase type 单词结尾，反向解析可能产生歧义（源码按 values() 顺序取首个匹配）。

## BR-005 EVERGREEN 必须 UNLIMITED，非 EVERGREEN 不得 UNLIMITED

- **类型**: 业务规则
- **同义词**: 常青阶段无限时长, evergreen unlimited, 阶段时长约束, 无限期阶段
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:290-310`

**规则**：遍历计划全部阶段：若阶段类型为 `EVERGREEN` 但其 `duration.unit != UNLIMITED`，报错「must have duration as UNLIMITED」；若阶段类型非 `EVERGREEN` 但其 `duration.unit == UNLIMITED`，报错「must not have duration as UNLIMITED」。

## BR-006 UNLIMITED 时长与 number 互斥

- **类型**: 业务规则
- **同义词**: 时长数量校验, unlimited 无数量, duration number, 时长必填
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultDuration.java:106-123`

**规则**：`unit == UNLIMITED` 时 `number` 必须为缺省（-1），否则报「Duration can only have 'UNLIMITED' unit if the number is omitted」；`unit != UNLIMITED` 时 `number` 必须给出，否则报「Finite Duration must have a well defined length」。

## BR-007 周期费与计费周期一致性

- **类型**: 业务规则
- **同义词**: 循环费周期校验, recurring billing period, 周期费必填周期, no billing period
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultRecurring.java:90-111`

**规则**：
- 有 `recurringPrice` 时必须有 `billingPeriod` 且不得为 `NO_BILLING_PERIOD`。
- 没有 `recurringPrice` 时 `billingPeriod` 必须是 `NO_BILLING_PERIOD`。
- 违反时报「has a recurring price but no billing period」或「has no recurring price but does have a billing period」。

## BR-008 价格不得为负且币种必须受支持

- **类型**: 业务规则
- **同义词**: 价格校验, 负价格, 非法币种, negative price, unsupported currency, 价格合法性
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:107-127`

**规则**：对每个 `Price`：
- 其 `currency` 不在目录 `supportedCurrencies` 中 → 校验错误 `Unsupported currency: <CUR>`。
- 其 `value < 0.0` → 校验错误 `Negative value for price in currency: <CUR>`。
- 若 `value` 为 null（抛 `CurrencyValueNull`），跳过负值检查。

## BR-009 指定币种无价格时抛 CAT_NO_PRICE_FOR_CURRENCY

- **类型**: 业务规则
- **同义词**: 币种缺价, 无报价币种, no price for currency, 价格缺失
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:88-100`

**规则**：`InternationalPrice` 无任何 price 时，视为所有币种价格 = 0（返回 `BigDecimal.ZERO`）；若有 price 列表但找不到请求的币种，则抛 `CatalogApiException(CAT_NO_PRICE_FOR_CURRENCY, currency)`。

## BR-010 用量各模式的必填结构校验

- **类型**: 业务规则
- **同义词**: 用量校验, 预付容量, 预付消耗, 后付阶梯, usage validation, IN_ADVANCE, IN_ARREAR, limits, blocks, tiers, 用量段校验, 目录校验, usage section validation, in advance limits, in arrears tiers
- **模块**: catalog, usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:212-229`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:147-159`

**规则**：
- `IN_ADVANCE + CAPACITY`：必须定义 `limits`，否则报错。
- `IN_ADVANCE + CONSUMABLE`：必须定义 `blocks`，否则报错。
- `IN_ARREAR`：必须定义 `tiers`，否则报错。
- 在 Tier 级别：`IN_ARREAR + CAPACITY` 需 limits，`IN_ARREAR + CONSUMABLE` 需 blocks（校验信息挂在 DefaultUsage 上）。

**规则**（目录加载时校验，决定用量可被如何计费）：
- `IN_ADVANCE` + `CAPACITY` 且 `limits.length == 0` → 报错「needs to define some limits」。
- `IN_ADVANCE` + `CONSUMABLE` 且 `blocks.length == 0` → 报错「needs to define some blocks」。
- `IN_ARREAR` 且 `tiers.length == 0` → 报错「needs to define some tiers」。

**关联**：这些是目录对「用量类型 + 计费模式」组合的合法性约束，间接规定了对应用量记录应携带哪些单位类型。

## BR-011 Limit 的上下限判定

- **类型**: 业务规则
- **同义词**: 用量限制, 上限下限, limit min max, complies with limits, 超限
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultLimit.java:84-105`

**规则**：
- 校验：`max` 与 `min` 都有值时，`max < min` 报错「max must be greater than min」。
- 判定：`maxHasValue && value > max` → 不通过（false）；否则当 `minHasValue && value > min` 也不通过，其余通过。缺省值 -1 视为「未设置」。

**注意（源码疑点）**：`min` 判定使用 `value.compareTo(min) <= 0`（即 value > min 不通过），语义上更像是「未超过 min」；业务使用时需与官方文档核对。

## BR-012 effectiveDateForExistingSubscriptions 不得早于目录生效日

- **类型**: 业务规则
- **同义词**: 存量订阅生效日, existing subscriptions date, 目录生效日约束, price effective date
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:286-293`

**规则**：若计划设置了 `effectiveDateForExistingSubscriptions` 且它早于目录的 `effectiveDate`，则校验报错「Price effective date %s is before catalog effective date '%s'」。该字段用于控制计划变更对存量订阅生效的时点。

## BR-013 纯用量计划可不设 recurringBillingMode

- **类型**: 业务规则
- **同义词**: 纯用量计划, recurring billing mode 缺省, usage only plan, 计费模式继承
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:79-81`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:276-278`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:295-298`

**规则**：若计划的 recurring billing period 为 `NO_BILLING_PERIOD`（纯用量计划），可缺省 `recurringBillingMode`；否则必须有值，否则校验报「Invalid recurring billingMode for plan '%s'」。计划级缺省时继承目录级 `recurringBillingMode`。

## BR-014 plansAllowedInBundle 的取值语义

- **类型**: 业务规则
- **同义词**: bundle 内计划数量, plans allowed in bundle, 允许多少计划, 不限量 -1
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:90-95`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:239-251`

**规则**：`plansAllowedInBundle` 表示一个 bundle 内该计划允许存在的数量：
- 缺省值 1；BASE 计划与 Tiered ADDON 只允许 1（源码注释明确）。
- 值 `-1` 表示不限量。
- 未设置时由初始化安全网填为 -1，运行期若仍为 null 会抛 IllegalStateException（安全校验）。

## BR-015 默认价格表名 DEFAULT 为保留名

- **类型**: 业务规则
- **同义词**: 默认价格表命名, DEFAULT 保留, reserved price list name, 价格表命名约束
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:106-118`, `catalog/src/main/java/org/killbill/billing/catalog/PriceListDefault.java:36-45`

**规则**：
- 默认价格表（PriceListDefault）的名称 `getName()` 恒返回 `PriceListSet.DEFAULT_PRICELIST_NAME`（值 `DEFAULT`）。
- 子价格表名称不得等于 `DEFAULT`，否则校验报「Pricelists cannot use the reserved name 'DEFAULT'」。
- 若默认价格表名称不等于 `DEFAULT`，报「The name of the default pricelist must be 'DEFAULT'」。

## BR-016 价格表解析与默认回退

- **类型**: 业务规则
- **同义词**: 找价格表, price list fallback, 默认价格表回退, 多匹配计划, price list resolution
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:64-98`

**规则**：
- `getPlanFrom(product, period, priceListName)`：先在指定价格表查匹配计划；若 0 个，则回退到默认价格表再查。
- 最终 0 个 → 返回 null；1 个 → 返回该计划；>1 个 → 抛 `CAT_MULTIPLE_MATCHING_PLANS_FOR_PRICELIST`。
- `findPriceListFrom(name)`：name 为 null 抛 `CAT_NULL_PRICE_LIST_NAME`；依次匹配默认表与子表；找不到抛 `CAT_PRICE_LIST_NOT_FOUND`。

## BR-017 计划缺省价格表的自动解析

- **类型**: 业务规则
- **同义词**: 计划归属价格表, plan price list, price list for plan, 自动找价格表
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:280-281`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:404-412`

**规则**：若计划未显式声明 `priceListName`，初始化时遍历目录所有价格表，找到第一个包含该计划的表名；若都找不到则抛 `IllegalStateException("Cannot extract pricelist for plan ...")`。

## BR-018 目录版本按生效日期选取

- **类型**: 业务规则
- **同义词**: 目录版本选择, catalog for date, effective date 选择, 历史目录
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:82-107`

**规则**：给定日期查版本时，从最新版本往前找第一个 `effectiveDate <= 查询日期` 的版本；若所有版本都晚于查询日期，返回第一个（最早）版本（源码注释说明这是容错处理，见 issue #760）。版本集合按 effectiveDate 升序排序。

## BR-019 版本生效日唯一且 catalogName 一致

- **类型**: 业务规则
- **同义词**: 版本重复生效日, catalog name 一致, version effective date unique, 目录版本校验
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:133-154`

**规则**：校验所有版本：
- 每个版本的 `effectiveDate` 必须唯一，重复报「Catalog effective date '%s' already exists for a previous version」。
- 每个版本的 `catalogName` 必须与目录名一致，否则报「Catalog name '%s' is not consistent across versions」。
- 每个 `StandaloneCatalog` 版本自身再跑一遍校验。

## BR-020 跨版本同名计划形状必须一致

- **类型**: 业务规则
- **同义词**: 跨版本计划一致性, plan shape, 阶段数量一致, 阶段名一致, uniform plan shape
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:156-192`

**规则**：对任意两个版本中同名的计划：阶段数量必须相同，且逐位阶段名必须一致。违反时报「Number of phases for plan ... differs between version ...」或「Phase ... does not exist in version ...」。若某版本无该计划则跳过（允许后续版本重新定义）。

## BR-021 规则未命中时的默认策略/对齐值

- **类型**: 业务规则
- **同义词**: 默认策略, 默认对齐, default policy, default billing alignment, 规则缺省值
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:125-176`

**规则**：当相应规则 case 无匹配时：
- 创建对齐 → `PlanAlignmentCreate.START_OF_BUNDLE`
- 变更策略 → `BillingActionPolicy.END_OF_TERM`
- 取消策略 → `BillingActionPolicy.END_OF_TERM`
- 变更对齐 → `PlanAlignmentChange.START_OF_BUNDLE`
- 计费对齐 → `BillingAlignment.ACCOUNT`

## BR-022 ILLEGAL 变更策略直接拒绝计划变更

- **类型**: 业务规则
- **同义词**: 禁止变更, 非法换套餐, illegal plan change, ILLEGAL policy
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:143-164`

**规则**：`getPlanChangeResult(from, to)` 先解析目标价格表与策略；若策略为 `BillingActionPolicy.ILLEGAL`，抛 `IllegalPlanChange`；否则返回 `PlanChangeResult(toPriceList, policy, alignment)`。

## BR-023 规则集必须存在默认 case 且不得重复

- **类型**: 业务规则
- **同义词**: 规则校验, 默认规则缺失, 规则去重, plan rules validation, duplicate rule
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:187-278`

**规则**：
- 变更策略（changePolicyCase）和取消策略（cancelPolicyCase）必须各存在一个所有匹配字段均为 null 的「默认 case」，否则报「Missing default rule case for plan change/cancellation」。
- 每类规则（变更策略/取消策略/变更对齐/创建对齐/计费对齐/价格表）内部不得有重复项，重复报「Duplicate rule for ...」。

## BR-024 产品自引用与 catalogName 校验

- **类型**: 业务规则
- **同义词**: 产品自引用, 产品校验, self referencing product, catalog name 校验
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:187-208`

**规则**：
- 产品的 `catalogName` 必须与所属目录一致，否则报「Invalid catalogName for product」。
- 产品不得在 `included` 或 `available` 中引用自身，否则报「Product refers to itself ...」。
- 例外：系统属性 `org.killbill.catalog.validation.ignoreSelfReferencingProducts=true` 可跳过自引用校验。
- 运行期 `getIncluded()/getAvailable()` 会过滤掉自引用项（历史目录兼容）。

## BR-025 TOP_UP 块必须定义 minTopUpCredit

- **类型**: 业务规则
- **同义词**: 充值块校验, top-up 最低充值, minTopUpCredit, top_up block
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:92-110`

**规则**：`BlockType.TOP_UP` 的块必须定义 `minTopUpCredit`（大于缺省 -1），否则校验报「TOP_UP block needs to define minTopUpCredit」；对非 TOP_UP 块调用 `getMinTopUpCredit()` 抛 `CAT_NOT_TOP_UP_BLOCK`。

## BR-026 规则 case 的匹配语义

- **类型**: 业务规则
- **同义词**: 规则匹配, case 匹配, 规则优先级, rule matching, case satisfies
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCase.java:47-88`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCasePhase.java:43-62`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCaseChange.java:86-151`

**规则**：
- 单条 case 的每个字段为 null 表示「通配」；非 null 字段必须与输入的产品/类别/周期/价格表（阶段规则还含 phaseType）匹配。
- 一组 case 按声明顺序**首个匹配即返回**（first-match wins）。
- 变更类规则同时匹配 from 与 to 两组字段。

## BR-027 createOrFindPlan 的计划解析与异常

- **类型**: 业务规则
- **同义词**: 计划解析, 按产品找计划, createOrFindPlan, plan not found, 价格表缺省
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:205-229`

**规则**：
- 给了 `planName` → 直接 `findPlan(planName)`。
- 否则必须有 `productName` 与 `billingPeriod`（缺失分别抛 `CAT_NULL_PRODUCT_NAME` / `CAT_NULL_BILLING_PERIOD`）；价格表缺省用 `DEFAULT`，再经 `PriceListSet.getPlanFrom` 解析。
- 最终计划为 null → 抛 `CAT_PLAN_NOT_FOUND`。

## BR-028 价格表查找的异常语义

- **类型**: 业务规则
- **同义词**: 价格表异常, price list not found, 空价格表名, null price list
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:85-98`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:271-278`

**规则**：`findPriceList(name)`：name 为 null 或 priceLists 为 null → `CAT_PRICE_LIST_NOT_FOUND`；通过集合查找时 name 为 null 抛 `CAT_NULL_PRICE_LIST_NAME`，找不到抛 `CAT_PRICE_LIST_NOT_FOUND`。

## BR-029 BCD 由首个非零周期费日期推算

- **类型**: 业务规则
- **同义词**: 首个收费日, 非零周期费, first recurring charge, BCD 计算, dateOfFirstRecurringNonZeroCharge
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:329-352`, `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:133-139`

**规则**：`dateOfFirstRecurringNonZeroCharge(subscriptionStartDate, initialPhaseType)` 从订阅起始日出发，跳过价格为 0（或非 UNLIMITED 且 recurring 价格为空/零）的阶段，累加其时长，得到第一个「非零周期费」的日期。订阅对齐（SUBSCRIPTION）的 BCD = 该日期的当月日号。

**可选参数**：传入 `initialPhaseType` 时会先跳过到指定阶段类型再开始计算。

## BR-030 BCD 对齐的月末处理

- **类型**: 业务规则
- **同义词**: 月末账单日, 2月对齐, month end billing, BCD 29/30/31, lastDayOfMonth
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:74-116`

**规则**：
- 仅当计费周期以「月/年」为单位时才做 BCD 对齐；以天/周为单位的周期直接返回原日期。
- 若 `billingCycleDay > 当月最大天数`，则取当月最后一天（例如 BCD=31 在 2 月对齐为 28/29 日）。
- 若当前日期已过本月 BCD，则对齐到下月同一 BCD。

## BR-031 账户 BCD 取最早的有计费 ACCOUNT 对齐事件

- **类型**: 业务规则
- **同义词**: 账户账单日计算, account BCD, 账户首个账单日, computeAccountBCD
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `junction/src/main/java/org/killbill/billing/junction/plumbing/billing/DefaultInternalBillingApi.java:220-274`

**规则**：当账户尚未设置 BCD（=0）时，从所有 billing event 中筛选 `BillingAlignment.ACCOUNT` 且「有周期价（可为 0）或有 usage」的事件，取 effectiveDate（并列时取 totalOrdering）最小的一个，其 `getBillCycleDayLocal()` 即候选账户 BCD（必须 > 0）。dry-run 模式下不落库。

## BR-032 ACCOUNT 对齐但账户 BCD 未设时回退 SUBSCRIPTION

- **类型**: 业务规则
- **同义词**: 账单日回退, ACCOUNT 未设置, alignment fallback, 订阅对齐
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:39-72`, `entitlement/src/main/java/org/killbill/billing/entitlement/engine/core/EventsStreamBuilder.java:451-457`

**规则**：`resolveEffectiveBillingAlignment(ACCOUNT, accountBCD==0)` 返回 `SUBSCRIPTION`，以便在账户 BCD 尚未建立期间仍能按订阅起始日推算 BCD。构建事件流时若对齐为 ACCOUNT 且账户 BCD=0，则不预先计算 defaultAlignmentDay（留给后续账户 BCD 计算）。

## BR-033 简化计划只支持 EVERGREEN 与单 TRIAL

- **类型**: 业务规则
- **同义词**: 简化计划约束, simple plan validation, 仅 EVERGREEN, trial 校验
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:227-283`

**规则**：更新已有计划时校验：
- 起始阶段最多一个，且若存在必须是 `TRIAL` 且其固定价为 0（$0 试用）；否则失败。
- 若描述符带 trial 信息，则计划是否含 trial 必须一致，且时长（unit+number）必须完全匹配。
- 最终阶段必须是 `EVERGREEN`；billingPeriod 与（若已有该币种）金额必须与描述符一致。
- 任一不符 → 抛 `CAT_FAILED_SIMPLE_PLAN_VALIDATION`。

## BR-034 ADD_ON 必须提供有效的可用基础产品

- **类型**: 业务规则
- **同义词**: 附加产品校验, add-on base product, availableBaseProducts, BASE_PLAN_PRODUCTS_NOT_EMPTY
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:296-313`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:195-209`

**规则**：产品类别为 `ADD_ON` 时，`availableBaseProducts` 不得为空（否则报「List of available base products should not be empty for add-ons.」），且其中每个产品必须已存在于目录（否则报「Available base products contain invalid product.」）。创建 add-on 时会在这些基础产品的 `available` 列表中加入该 add-on。

## BR-035 发票未来生成最大月数

- **类型**: 业务规则
- **同义词**: 发票生成未来月数, 最多提前几个月开票, 目标日期上限, max months in future, maxNumberOfMonthsInFuture
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:63-71`

**规则**：生成（或干跑 dry-run）发票时，最多只考虑未来 36 个月内的目标日期（targetDate）。配置项 `org.killbill.invoice.maxNumberOfMonthsInFuture`，默认值 `36`。

**用途**：限制一次性提前生成过多期发票，避免未来账期被过度预开。

## BR-036 用量重复计费防护（tracking id 去重 + 已开票区间跳过）

- **类型**: 业务规则
- **同义词**: 用量去重, 防止重复计费, usage dedup, tracking id, 已开票跳过, double billing usage, 跟踪号去重, 幂等, 重复提交拦截, tracking id duplicate, idempotency, 重复用量
- **模块**: invoice, usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:290-307`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:333-356`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:74-82`, `usage/src/main/java/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.java:36-39`

**规则**：
1. 每条原始用量带 tracking id；只有**不在既有 tracking id 集合**中的用量才会被计费（新增用量）。
2. 若某个用量区间已被既有 `USAGE` 发票项覆盖（同 usage name 且 start/end 落入既有项内），则**跳过**该区间，避免重复计费（尤其阻断/重跑场景）。

**规则**：调用方传入非空 `trackingId` 时，先查该订阅下是否已存在相同 `trackingId` 的行（`recordsWithTrackingIdExist`，SQL `select 1 ... where subscription_id=? and tracking_id=? ... limit 1`）。若已存在 → 抛 `UsageApiException(ErrorCode.USAGE_RECORD_TRACKING_ID_ALREADY_EXISTS, trackingId)`，整批用量不落库。

**范围**：去重键是 `(subscription_id, tracking_id, tenant_record_id)`（索引 `rolled_up_usage_tracking_id_subscription_id_tenant_record_id`）。因此同一 trackingId 在**不同订阅**下互不影响。

## BR-037 发票防重复计费安全检查

- **类型**: 业务规则
- **同义词**: 防重复计费, 计费安全检查, 幂等保护, sanity check, sanitySafetyBoundEnabled, double billing
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:73-81`

**规则**：系统默认开启内部安全检查（`org.killbill.invoice.sanitySafetyBoundEnabled` = `true`），用于防止错误计费与重复计费（mis- and double-billing）。关闭后不推荐用于生产。

## BR-038 零金额用量项是否写出

- **类型**: 业务规则
- **同义词**: 零金额用量项, 0元用量, $0 usage, zero amount, disable.usage.zero.amount, isUsageZeroAmountDisabled
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:84-92`

**规则**：配置项 `org.killbill.invoice.disable.usage.zero.amount` 默认 `false`，即**默认会写出金额为 $0 的用量项**。设为 `true` 时禁用写入 $0 用量项（不生成零金额用量行）。

## BR-039 缺失历史用量记录时的处理

- **类型**: 业务规则
- **同义词**: 缺失用量记录, 用量数据缺失, missing usage, usage.missing.lenient, 用量宽容模式
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:94-102`

**规则**：配置项 `org.killbill.invoice.usage.missing.lenient` 默认 `false`（不宽容）。默认情况下，若发现过去存在缺失的用量记录，发票生成会**失败**；设为 `true` 时改为宽容处理，不因缺失用量记录而使发票失败。

## BR-040 每日每订阅最大发票项数

- **类型**: 业务规则
- **同义词**: 每日发票项上限, 每天最多开多少项, maxDailyNumberOfItemsSafetyBound, daily items safety bound
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:104-112`

**规则**：对单个订阅（subscription id）每日生成的发票项数量上限为 `15`。配置项 `org.killbill.invoice.maxDailyNumberOfItemsSafetyBound`，默认值 `15`，作为安全边界防止异常爆炸式开票。

## BR-041 干跑发票通知提前时间

- **类型**: 业务规则
- **同义词**: 干跑通知, 预开票通知, dry run notification, dryRunNotificationSchedule, 提前通知时间
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:114-122`

**规则**：DryRun（干跑）发票通知在目标日期（targetDate）**之前**发送。配置项 `org.killbill.invoice.dryRunNotificationSchedule` 默认 `0s`；当设为 `0s` 时该通知被忽略（不发送）。

## BR-042 原始用量回看账期数（usage lookback）

- **类型**: 业务规则
- **同义词**: 用量回看, 回看账期, usage lookback, readMaxRawUsagePreviousPeriod, 历史用量读取期数, 用量优化
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:124-132`

**规则**：用量优化（usage optimization）时，系统最多读取**过去 2 个账期**的原始用量（raw usage）数据。配置项 `org.killbill.invoice.readMaxRawUsagePreviousPeriod`，默认值 `2`。

**用途**：限制每期开票时回查历史原始用量的范围，用于处理迟到/跨期的用量点。

## BR-043 全局锁获取最大重试次数

- **类型**: 业务规则
- **同义词**: 全局锁重试, global lock retries, globalLock.retries, 锁重试次数
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:134-137`

**规则**：系统获取全局锁最多重试 `50` 次，每次等待 100ms。配置项 `org.killbill.invoice.globalLock.retries`，默认值 `50`。

## BR-044 默认发票插件

- **类型**: 业务规则
- **同义词**: 发票插件, invoice plugin, 默认插件, org.killbill.invoice.plugin
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:139-147`

**规则**：配置项 `org.killbill.invoice.plugin` 默认为空字符串 `""`，即默认不加载任何发票插件。可配置一个（逗号分隔的）发票插件名列表，插件可在发票生成过程中注入/调整发票项。

## BR-045 发票创建邮件通知开关

- **类型**: 业务规则
- **同义词**: 发票邮件通知, invoice email notification, emailNotificationsEnabled, 开票发邮件
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:149-152`

**规则**：配置项 `org.killbill.invoice.emailNotificationsEnabled` 默认 `false`。开启后，对已配置的账户在发票创建时发送邮件通知。

## BR-046 发票系统总开关

- **类型**: 业务规则
- **同义词**: 发票系统开关, invoicing enabled, invoice.enabled, 关闭开票
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:154-157`

**规则**：配置项 `org.killbill.invoice.enabled` 默认 `true`，即发票系统默认启用。设为 `false` 可整体关闭开票系统。

## BR-047 用量聚合规则（CAPACITY 取峰值 / CONSUMABLE 累加）

- **类型**: 业务规则
- **同义词**: 用量聚合, 峰值计费, 累加计费, usage aggregation, capacity max, consumable sum, 用量合并, 容量取最大, 消费求和
- **模块**: invoice, usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:539-548`

**规则**：把同一区间内的多条原始用量合并为一个金额时：
- 若 usage 类型为 `CAPACITY` → 取 `max(当前值, 新值)`（保留峰值）；
- 若为 `CONSUMABLE` → 取 `当前值 + 新值`（累加）。

**规则**（开票侧聚合，用量数据的使用方语义）：对同一单位类型在一段计费区间内的多次观测值 `computeUpdatedAmount(current, new)`：
- `UsageType.CAPACITY` → 返回 `max(current, new)`（区间峰值）。
- 否则（`UsageType.CONSUMABLE`）→ 返回 `current.add(new)`（多点累加）。
- 任一侧为 `null` 视为 `ZERO` 再参与运算。

**用量侧关联**：用量模块本身按 BR-006 对查询区间求和；CAPACITY 的「取最大」发生在开票消费这些原始/汇总数据时（`SubscriptionUsageInArrear` 按 usageType 选择不同 interval 实现，见 `invoice/.../SubscriptionUsageInArrear.java:188-193`）。

## BR-048 父发票自动提交时间

- **类型**: 业务规则
- **同义词**: 父发票提交, 父账户发票, parent invoice commit, parentAutoCommitUtcTime, HA发票提交时间
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:159-167`

**规则**：父账户（parent account）发票每天在指定 UTC 时间自动提交（commit）。配置项 `org.killbill.invoice.parent.commit.local.utc.time` 默认 `23:59:59.999`。

## BR-049 发票项结果报告模式

- **类型**: 业务规则
- **同义词**: 发票项结果模式, 聚合模式, 明细模式, aggregate vs detail, item.result.behavior.mode, UsageDetailMode
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:53-56`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:174-182`

**规则**：发票项结果报告方式由 `org.killbill.invoice.item.result.behavior.mode` 控制，默认 `AGGREGATE`（聚合）；可选 `DETAIL`（明细）。对应枚举 `UsageDetailMode { AGGREGATE, DETAIL }`。

## BR-050 用量时区偏移模式

- **类型**: 业务规则
- **同义词**: 用量时区, 夏令时处理, usage timezone, usage.tz.mode, AccountTzOffset, 日光节约
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:39-51`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:185-193`

**规则**：控制用量点（usage points）在夏令时（DST）下的归属，配置项 `org.killbill.invoice.usage.tz.mode`，默认 `FIXED`。
- `FIXED`：使用账户创建时一次性计算的固定时区偏移（与 RECURRING 发票项行为一致）。
- `VARIABLE`：按当前年内所处时间重新计算偏移，使相同 TZ/订阅/用量点的相似账户结果一致（夏/冬季开始时间不同也不受影响）。

## BR-051 in-arrear 计划计费模式

- **类型**: 业务规则
- **同义词**: 后付费模式, in arrear mode, inArrear.mode, GREEDY, 后计费策略
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:58-61`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:195-203`

**规则**：配置项 `org.killbill.invoice.inArrear.mode` 默认 `DEFAULT`，决定系统对 in-arrear（后付费）计划的处理行为；可选 `GREEDY`。对应枚举 `InArrearMode { DEFAULT, GREEDY }`。

## BR-052 目录中未定义的用量处理（可挂起账户）

- **类型**: 业务规则
- **同义词**: 未知用量挂起, park account, 挂起账户, parkAccountsWithUnknownUsage, 账户暂停, 未知用量单位, unknown usage unit, unit type not defined, park account usage, 未知用量, 未定义用量, park账户, unknown usage, park accounts, usage not in catalog
- **模块**: invoice, usage
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:205-213`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:485-505`

**规则**：配置项 `org.killbill.invoice.parkAccountsWithUnknownUsage` 默认 `false`。设为 `true` 时，若记录了用量数据但该用量在目录（catalog）中未定义，则将该账户挂起（park）。

**规则**：当上报的用量单位类型（unitType）**未在任何 billing event 的目录中定义**时：
- 若 `org.killbill.invoice.parkAccountsWithUnknownUsage` = `true` → 抛 `InvoiceApiException`（ILLEGAL INVOICING STATE），导致账户被挂起；
- 否则 → 记录告警并**忽略**该单位类型，同时移除其关联的 tracking id。

**规则**：系统属性 `org.killbill.invoice.parkAccountsWithUnknownUsage`（默认 `false`）控制：当账户记录了目录中未定义的用量数据时，是否将该账户 park（暂停自动开票，直到人工介入）。

**含义**：这是用量数据与目录一致性问题（BR-012）的兜底策略，由开票侧读取，用量模块不读取该配置。

## BR-053 不可恢复异常时挂起账户

- **类型**: 业务规则
- **同义词**: 异常挂起账户, park on exceptions, parkAccountsOnAllExceptions, 发票处理失败挂起
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:215-223`

**规则**：配置项 `org.killbill.invoice.parkAccountsOnAllExceptions` 默认 `true`。当发票处理发生不可恢复失败（锁失败、订阅者异常、billing event 获取失败）时，默认将账户挂起。

## BR-054 发票生成最大回看时间

- **类型**: 业务规则
- **同义词**: 发票回看限制, 最大回看时间, maxInvoiceLimit, 开票时间下限, 追溯多久
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:37`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:225-233`

**规则**：发票生成向前回看（look back）的时间上限由 `org.killbill.invoice.maxInvoiceLimit` 控制，默认 `DEFAULT_NULL_PERIOD` = `P200Y`（200 年，实际等于不限）。用于限定发票生成时追溯历史 billing events 的最远时间。

## BR-055 固定天数免分比

- **类型**: 业务规则
- **同义词**: 免分比, 分比天数, proration fixed days, proration.fixed.days, 避免按比例分摊
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:235-243`

**规则**：配置项 `org.killbill.invoice.proration.fixed.days` 默认 `0`。设置一个月内的固定天数以避免分比（proration）；`0` 表示不启用该固定天数行为。

## BR-056 发票余额计算（balance）

- **类型**: 业务规则
- **同义词**: 发票余额, 欠款, 应收, invoice balance, getBalance, outstanding amount, 未付金额, 余额怎么算
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:96-110`

**规则**：发票原始余额 `computeRawInvoiceBalance` = **计费金额合计 − 已付金额合计（含退款）**：
- `amountPaid = computeInvoiceAmountPaid + computeInvoiceAmountRefunded`
- `chargedAmount = computeInvoiceAmountCharged + computeInvoiceAmountCredited + computeInvoiceAmountAdjustedForAccountCredit`
- `invoiceBalance = chargedAmount + (−amountPaid)`

## BR-057 发票余额为零的情形

- **类型**: 业务规则
- **同义词**: 余额为零, 无需付款, zero balance, 已核销, 草稿发票余额, 作废发票余额, written off
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoice.java:273-288`

**规则**：满足以下任一条件时，`getBalance()` 直接返回 `BigDecimal.ZERO`：
1. 发票已核销（`isWrittenOff()`）；
2. 迁移发票（`isMigrationInvoice()`）；
3. 状态为 `DRAFT`；
4. 状态为 `VOID`；
5. 父发票余额为 0（`hasZeroParentBalance()`）。
否则按 BR-020 的公式计算。

## BR-058 发票已付金额（paid amount）

- **类型**: 业务规则
- **同义词**: 已付金额, 已支付, paid amount, amountPaid, 付款统计
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:207-223`

**规则**：`computeInvoiceAmountPaid` 只累计**支付状态为 SUCCESS 且类型为 ATTEMPT** 的发票支付金额。其他支付状态或类型的记录不计入已付金额。

## BR-059 发票已退款金额（refunded amount）

- **类型**: 业务规则
- **同义词**: 已退款金额, 退款统计, refunded amount, 拒付金额, charged back
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:225-242`

**规则**：`computeInvoiceAmountRefunded` 只累计**支付状态为 SUCCESS 且类型为 REFUND 或 CHARGED_BACK** 的金额。非 SUCCESS 的记录跳过。

## BR-060 发票计费金额组成（charged amount）

- **类型**: 业务规则
- **同义词**: 计费金额, 应收金额, charged amount, amountCharged, 发票总额, 账单金额
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:157-174`

**规则**：`computeInvoiceAmountCharged` 累加满足以下任一条件的发票项金额：
- 收费项（TAX / EXTERNAL_CHARGE / FIXED / USAGE / RECURRING）；或
- 发票级调整项（CREDIT_ADJ，且该发票不是“信用发票”本身）；或
- 项调整（ITEM_ADJ / REPAIR_ADJ）；或
- 父账户汇总项（PARENT_SUMMARY）。

## BR-061 子发票金额（父账户汇总）

- **类型**: 业务规则
- **同义词**: 子发票金额, 父账户汇总, child invoice amount, parent summary, HA子账户金额
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:112-131`

**规则**：`computeChildInvoiceAmount` 计算应在父发票上汇总的子账户金额：
- 若子发票**无收费项**，返回其信用金额（credited）的负值（仅把信用额从父项金额中扣减）；
- 否则返回 `charged + credited + adjustedForAccountCredit` 的合计。

## BR-062 信用发票识别（CREDIT_ADJ + CBA_ADJ）

- **类型**: 业务规则
- **同义词**: 信用发票, 账户信用, credit invoice, CREDIT_ADJ, CBA_ADJ, 信用余额, account credit
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:46-70`

**规则**：当一张发票**恰好只有 2 个发票项**，且其中一项为 `CREDIT_ADJ`、另一项为 `CBA_ADJ` 且两者 `invoiceId` 相同、金额互为相反数时，判定为“信用发票”。信用发票允许其 `CREDIT_ADJ` 金额被计入余额调整。

## BR-063 账户信用（CBA）生成与使用规则

- **类型**: 业务规则
- **同义词**: 账户信用, 信用余额, credit balance adjustment, CBA, CBA_ADJ, 抵扣余额, 信用生成, 信用使用
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:63-97`

**规则**：计算发票的信用余额调整（CBA）时：
1. 若发票**余额 < 0**（负余额）→ 生成一条**正向信用**（CBA 项金额取负值，即给账户增加可用信用）。
2. 若发票**余额 > 0** 且发票状态为 `COMMITTED`、**无 PENDING 支付**、且**未核销** → 使用账户已有信用抵扣该发票（消费额 = min(账户 CBA, 发票余额)），生成负向 CBA 项。
3. 若余额为 0 → 不做任何处理。

## BR-064 账户信用按发票日期分配给未付发票

- **类型**: 业务规则
- **同义词**: 信用分配, 抵扣未付发票, distribute CBA, 信用抵扣顺序, account credit allocation
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:172-218`

**规则**：账户可用信用（CBA）会被分配到所有 **COMMITTED 且未付** 的发票上，分配顺序按 `invoiceDate` **升序**（先旧后新），逐张抵扣直到信用耗尽或发票付清。每张发票的抵扣额 = min(剩余信用, 该发票余额)。

## BR-065 发票目标日期上限校验（未来 36 个月）

- **类型**: 业务规则
- **同义词**: 目标日期过远, target date too far, 未来开票上限, INVOICE_TARGET_DATE_TOO_FAR_IN_THE_FUTURE
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:120-126`

**规则**：生成发票时校验目标日期：若 `targetDate` 与当前 UTC 今天的月差**大于** `org.killbill.invoice.maxNumberOfMonthsInFuture`（默认 36），则抛出 `InvoiceApiException`，错误码 `INVOICE_TARGET_DATE_TOO_FAR_IN_THE_FUTURE`。

## BR-066 发票目标日期自动前推（避免回溯重复开票）

- **类型**: 业务规则
- **同义词**: 目标日期调整, adjust target date, 已有未来发票, 防止重复开票
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:128-154`

**规则**：生成发票前，若账户已存在**含 RECURRING 或 USAGE 项**、且其 `targetDate` 晚于本次请求的 `targetDate` 的发票，则把本次 `targetDate` 上调为这些发票中最晚的 `targetDate`（防止对已开票区间重复开票）。

## BR-067 作废发票（VOID）的前置校验

- **类型**: 业务规则
- **同义词**: 作废发票, 发票作废, void invoice, 不能作废, CAN_NOT_VOID, 已支付不能作废, 已修复不能作废
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:753-825`

**规则**：调用 `voidInvoice` 时依次校验（任一失败即抛 InvoiceApiException）：
1. 若发票状态为 `COMMITTED`：
   - 若发票已被修复（`isRepaired`）→ 抛 `CAN_NOT_VOID_INVOICE_THAT_IS_REPAIRED`；
   - 若发票含“已使用过的正向 CBA 信用” → 抛 `CAN_NOT_VOID_INVOICE_THAT_GENERATED_USED_CREDIT`。
2. 若发票已有支付且已付金额（含退款）≠ 0 → 抛 `CAN_NOT_VOID_INVOICE_THAT_IS_PAID`。
3. 通过后将状态改为 `VOID`。

## BR-068 提交草稿发票（commit）

- **类型**: 业务规则
- **同义词**: 提交发票, 确认发票, commit invoice, 草稿转正式, DRAFT 转 COMMITTED
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:688-708`

**规则**：`commitInvoice` 将发票状态改为 `COMMITTED`，随后更新其计费截止日期（charged-through dates），并通过发票插件链以 `INVOICE_OPERATION=commit` 派发。

## BR-069 外部收费与信用金额校验

- **类型**: 业务规则
- **同义词**: 外部收费, 手动收费, external charge, 信用金额校验, 金额必须为正, CREDIT_AMOUNT_INVALID, EXTERNAL_CHARGE_AMOUNT_INVALID
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:556-600`, `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:638-646`

**规则**：
- 外部收费（EXTERNAL_CHARGE）或信用（CREDIT_ADJ）金额若为 null 或 < 0 → 抛 `EXTERNAL_CHARGE_AMOUNT_INVALID` / `CREDIT_AMOUNT_INVALID`（金额必须为正）。
- 金额币种必须与账户币种一致，否则 `CURRENCY_INVALID`。
- 若把费用加到**已存在的发票**上：该发票为 `COMMITTED` → 抛 `INVOICE_ALREADY_COMMITTED`；为 `VOID` → 抛 IllegalStateException；仅 `DRAFT` 允许。
- 信用项在写入时金额会被**取负**（`amount.negate()`）。

## BR-070 账户余额与账户信用余额查询

- **类型**: 业务规则
- **同义词**: 账户余额, 账户信用, account balance, account CBA, getAccountBalance, getAccountCBA, 余额查询
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:229-239`

**规则**：`getAccountBalance(accountId)` 与 `getAccountCBA(accountId)` 从数据库聚合；当结果为空（null）时统一返回 `BigDecimal.ZERO`。

## BR-071 子账户信用转给父账户

- **类型**: 业务规则
- **同义词**: 子账户信用转移, 信用转父账户, transferChildCreditToParent, CHILD_ACCOUNT_MISSING_CREDIT, 父子账户信用
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:709-731`

**规则**：`transferChildCreditToParent` 前置条件：
1. 子账户必须**存在父账户**，否则抛 `ACCOUNT_DOES_NOT_HAVE_PARENT_ACCOUNT`；
2. 子账户账户信用（CBA）必须 **> 0**，否则抛 `CHILD_ACCOUNT_MISSING_CREDIT`；
3. 通过后将子账户信用转移给父账户。

## BR-072 发票项调整（ITEM_ADJ）校验

- **类型**: 业务规则
- **同义词**: 发票项调整, 条目调整, item adjustment, ITEM_ADJ, INVOICE_ITEM_ADJUSTMENT_AMOUNT_SHOULD_BE_POSITIVE, 调整金额
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:409-451`

**规则**：`insertInvoiceItemAdjustment`：
1. 若指定了调整金额且 ≤ 0 → 抛 `INVOICE_ITEM_ADJUSTMENT_AMOUNT_SHOULD_BE_POSITIVE`；
2. 目标发票状态为 `VOID` → 抛 `INVOICE_VOID_UPDATED`（作废发票不可调整）；
3. 指定币种必须与发票币种一致，否则 `CURRENCY_INVALID`；
4. 会为被调整项生成一条 `ITEM_ADJ` 项。

## BR-073 发票核销（written off）标记

- **类型**: 业务规则
- **同义词**: 发票核销, 坏账核销, write off, WRITTEN_OFF, tagInvoiceAsWrittenOff, 不再收款
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:313-335`

**规则**：对发票打上 `WRITTEN_OFF` 控制标签即表示核销（`tagInvoiceAsWrittenOff`），移除该标签为取消核销（`tagInvoiceAsNotWrittenOff`）。核销后发票余额恒为 0（见 BR-021），并会向总线发送发票调整事件（用于 overdue 等）。

## BR-074 用量计费区间按 BCD 对齐

- **类型**: 业务规则
- **同义词**: 用量账期, BCD 对齐, billing cycle day, usage interval, 计费周期划分, transition time
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:155-254`

**规则**：用量计费区间（transitionTimes）按订阅的 **BCD（bill cycle day）** 与用量 billingPeriod 对齐划分；首个与最后区间可能是不完整的（受订阅创建/取消/targetDate 影响）。取消发生的当日用量（cancellation day）会被特殊纳入最后一个区间一并计费。

```mermaid
flowchart LR
  T1[创建/起始] -->|按 BCD 对齐| T2[完整账期]
  T2 -->|按 BCD 对齐| T3[完整账期]
  T3 -->|取消/目标日期| T4[末段不完整区间]
```

## BR-075 手动支付账户的发票渲染

- **类型**: 业务规则
- **同义词**: 手动支付, manual pay, MANUAL_PAY, 线下支付, 发票渲染
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:483-493`

**规则**：生成发票 HTML（`getInvoiceAsHTML`）时，若账户带有 `MANUAL_PAY` 控制标签，则以 `manualPay=true` 渲染发票，表示该账户走**手动/线下支付**而非自动扣款。

## BR-076 发票优化时间边界（cutoff / maxInvoiceLimit）

- **类型**: 业务规则
- **同义词**: 发票优化, invoice optimization, cutoff date, maxInvoiceLimit, 历史发票截断, 性能优化
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/optimizer/InvoiceOptimizerExp.java:67-88`

**规则**：当 `org.killbill.invoice.maxInvoiceLimit` 已设置且不等于默认 `P200Y` 时：
- 发票 cutoffDt = 当前 UTC 时间 `−` maxInvoiceLimit；
- billing event 的 cutoff beCutoffDt = cutoffDt `−` maxInvoiceLimit（比发票再多回溯一个周期，用于支持 in-arrear 尾部分摊）；
- 只加载 cutoffDt 之后的既有发票参与本次开票。

## BR-077 建议开票项过滤（optimizer filterProposedItems）

- **类型**: 业务规则
- **同义词**: 开票项过滤, proposed items, 避免重复开票, filterProposedItems, 抵消项
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/optimizer/InvoiceOptimizerExp.java:100-170`

**规则**：若设置了 cutoffDate，对**提议的** RECURRING/FIXED 发票项过滤：
- `FIXED`：保留 `startDate >= cutoffDate`；
- `RECURRING` 且 billing mode 为 `IN_ADVANCE`：保留 `startDate >= cutoffDate`；
- `RECURRING` 且 billing mode 为 `IN_ARREAR`：保留 `endDate >= cutoffDate`；
- 否则：若既有发票中存在相同 subscriptionId 且相同 startDate 的 RECURRING 项则保留（便于后续抵消），其余丢弃。

## BR-078 用量仅支持后付费（IN_ARREAR）

- **类型**: 业务规则
- **同义词**: 后付费, in arrear, 用量后计费, BillingMode, IN_ARREAR, 用量计费模式
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:36`, `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:57`, `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:70`, `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:77`

**规则**：用量计费的各种取层/取单位方法均以 `Preconditions` 强制要求 `usage.getBillingMode() == BillingMode.IN_ARREAR`（后付费）——用量只在账单周期结束后计费，且 tiers 不能为空。

## BR-079 父发票提交通知去重

- **类型**: 业务规则
- **同义词**: 通知去重, parent invoice notification dedup, 重复通知
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/notification/ParentInvoiceCommitmentPoster.java:58-88`

**规则**：插入父发票提交通知前，检查队列中是否已存在**相同生效日期且相同 invoiceId** 的未来通知；若存在则跳过（不重复记录）。

## BR-080 发票系统关闭时挂起账户

- **类型**: 业务规则
- **同义词**: 发票系统关闭, invoicing off, invoice.enabled=false, 挂起账户, park account
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:289-300`

**规则**：当 `org.killbill.invoice.enabled` = `false`（发票系统关闭）时，来自通知/总线事件的账户处理会**直接挂起该账户**并返回空结果（不生成发票）。

## BR-081 已挂起账户跳过开票

- **类型**: 业务规则
- **同义词**: 挂起账户, parked account, 跳过开票, 账户暂停, isParked
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:311-320`

**规则**：若账户处于挂起（parked）状态且本次调用**不是 API 调用**，则本次发票生成被忽略（返回空）。API 调用（isApiCall=true）仍会尝试开票。

## BR-082 发票生成的账户级全局锁

- **类型**: 业务规则
- **同义词**: 全局锁, account lock, ACCNT_INV_PAY, 发票并发锁, 加锁失败重试
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:322-338`

**规则**：非 dry-run 的发票生成会对账户加全局锁（锁类型 `ACCNT_INV_PAY`），最多重试 `org.killbill.invoice.globalLock.retries`（默认 50）次。
- 加锁失败且为 API 调用 → 抛 `InvoiceApiException`（UNEXPECTED_ERROR，“failed to acquire lock”）；
- 加锁失败且非 API 调用 → 抛 `QueueRetryException`，按 `rescheduleIntervalOnLock` 之后重试。

## BR-083 干跑通知仅余额大于 0 时发送

- **类型**: 业务规则
- **同义词**: 干跑通知, 余额大于0, 发票通知事件, invoice notification, dryRun balance
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:264-280`

**规则**：`processSubscriptionForInvoiceNotification` 干跑生成发票后，**仅当该预览发票余额 > 0** 时才向总线发送 `InvoiceNotificationInternalEvent`（用于“即将开票”提醒）。

## BR-084 订阅 EXPIRED 事件不触发开票

- **类型**: 业务规则
- **同义词**: 过期事件, EXPIRED, 订阅到期, 不触发开票, subscription expired
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceListener.java:266-271`

**规则**：当订阅事件类型为 `SubscriptionBaseTransitionType.EXPIRED` 时，`handleSubscriptionTransition` 不把该事件交给发票处理（即订阅过期本身不触发新的开票）。

## BR-085 哪些子发票可被父发票忽略

- **类型**: 业务规则
- **同义词**: 忽略子发票, shouldIgnoreChildInvoice, 负金额子发票, 零金额子发票
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1407-1425`

**规则**：父发票汇总时对子发票的判断：
- 子发票金额 **< 0**（信用）→ **忽略**（该信用将在下次开票中使用）；
- 子发票金额 **> 0** → 不忽略；
- 子发票金额 **== 0** → 仅当子发票中**没有 FIXED 或 RECURRING 项**时忽略；若含这两类项则不忽略（保留 0 金额汇总）。

## BR-086 父发票的项调整传播

- **类型**: 业务规则
- **同义词**: 父发票调整, parent adjustment, PARENT_SUMMARY 调整, 子发票调整传播
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1427-1500`

**规则**：对子发票做项调整（ITEM_ADJ）时同步到父发票：
- 若子发票**无父发票** → 抛 `INVOICE_MISSING_PARENT_INVOICE`；
- 若父发票**原始余额为 0**（已结清）→ 忽略调整；
- 取子发票中**最新一条 ITEM_ADJ**；若父发票状态为 `COMMITTED` → 在父发票上新增一条 `ITEM_ADJ`；否则 → 更新对应 `PARENT_SUMMARY` 项的金额。

## BR-087 父发票余额为 0 时子发票的余额算法

- **类型**: 业务规则
- **同义词**: 子发票余额, parent balance zero, 父子余额, HA balance
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:100-124`

**规则**：若子发票**存在父发票且父发票原始余额为 0**，则子发票余额 = `子发票计费金额 − 父发票上归属该子账户的项金额之和`；否则使用常规发票原始余额。

## BR-088 修复项（REPAIR_ADJ）金额上限

- **类型**: 业务规则
- **同义词**: 修复冲销, REPAIR_ADJ, repair, 冲销上限, 修复金额, repair amount
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:182-200`, `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:212-218`

**规则**：当既有发票项在新一轮开票中需要被冲销（REPAIR）时，生成一条**负金额** `RepairAdjInvoiceItem`：
- 修复上限 `maxAmountForRepair = min(按新日期分比后的金额, 该项净额)`；
- 净额 `netAmount = amount − adjustedAmount − currentRepairedAmount`；
- 已完全调整的项（`amount − adjustedAmount == 0`）为 `isFullyAdjusted`。

## BR-089 分比计算（Proration）

- **类型**: 业务规则
- **同义词**: 分比, 按比例计费, proration, 按天计费, 不足整周期, prorate
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:152-168`, `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:182-189`

**规则**：分比金额 = `calculateProrationBetweenDates(newStart, newEnd, 总天数, prorationFixedDays) × amount`。
- 总天数默认 = `startDate` 到 `endDate` 的实际天数；当 `org.killbill.invoice.proration.fixed.days > 0` 时用该固定天数作分母；
- 区间被拆分（split）时按 `splitDate` 分为 `[start, split]` 与 `[split, end]` 两段，金额按比例分配。

## BR-090 原始用量优化的起始日期（用量回看）

- **类型**: 业务规则
- **同义词**: 用量回看起点, optimized start date, raw usage optimization, readMaxRawUsagePreviousPeriod, 用量拉取范围
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/RawUsageOptimizer.java:77-137`

**规则**：计算拉取原始用量的优化起始日期：
- 若 `org.killbill.invoice.readMaxRawUsagePreviousPeriod ≥ 0`：对每个已知用量的 billingPeriod，从最近一次 consumable in-arrear 用量项的 `endDate` 回退该配置指定的周期数，取所有账期中的最早值，再与 `firstEventStartDate` 取较晚者作为起点；
- 若配置 < 0：直接返回 `firstEventStartDate`。
- 特殊路径：当 `isUsageZeroAmountDisabled=true` 时改用 `min(今天, targetDate)` 回退 1 个周期来估算（避免漏开旧账期时拉取不足）。

## BR-091 发票配置支持多租户覆盖

- **类型**: 业务规则
- **同义词**: 多租户配置, tenant config override, MultiTenantInvoiceConfig, 租户级配置
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/config/MultiTenantInvoiceConfig.java:46-58`, `invoice/src/main/java/org/killbill/billing/invoice/config/MultiTenantInvoiceConfig.java:311-315`

**规则**：绝大多数 `InvoiceConfig` 配置项支持**按租户覆盖**（`getStringTenantConfig`）：租户若配置了同名项则优先使用，否则回退到静态（全局）配置。枚举型配置的非法值会回退默认值（`UsageDetailMode`→AGGREGATE、`AccountTzOffset`→FIXED、`InArrearMode`→DEFAULT）。注意 `getMaxGlobalLockRetries` 与若干无参方法仅用静态配置，不支持租户覆盖。

## BR-092 迁移发票余额恒为 0

- **类型**: 业务规则
- **同义词**: 迁移发票, migration invoice, isMigrated, 余额为0, 历史数据导入
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceModelDaoHelper.java:33-46`

**规则**：对 `isMigrated()` 为 true 的发票，`getRawBalanceForRegularInvoice` 直接返回 `BigDecimal.ZERO`，不做金额计算。

## BR-093 发票项类型与实现类映射

- **类型**: 业务规则
- **同义词**: 发票项映射, item factory, InvoiceItemFactory, type mapping, 类型对应类
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/InvoiceItemFactory.java:90-124`

**规则**：从持久层重建发票项时按类型映射到实现类：
- `EXTERNAL_CHARGE`→`ExternalChargeInvoiceItem`
- `FIXED`→`FixedPriceInvoiceItem`
- `RECURRING`→`RecurringInvoiceItem`
- `CBA_ADJ`→`CreditBalanceAdjInvoiceItem`
- `CREDIT_ADJ`→`CreditAdjInvoiceItem`
- `REPAIR_ADJ`→`RepairAdjInvoiceItem`
- `ITEM_ADJ`→`ItemAdjInvoiceItem`
- `USAGE`→`UsageInvoiceItem`
- `TAX`→`TaxInvoiceItem`
- `PARENT_SUMMARY`→`ParentInvoiceItem`
- 其他未知类型 → 抛 RuntimeException。

## BR-094 加锁失败时的重试时间表

- **类型**: 业务规则
- **同义词**: 锁重试间隔, rescheduleIntervalOnLock, 重排发票, 锁被占用重试
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/LockAwareConfig.java:30-38`

**规则**：当发票运行因账户锁被占用而无法执行时，按配置项 `org.killbill.rescheduleIntervalOnLock` 的延迟序列重排。默认值 `"30s, 1m, 1m, 3m, 3m, 10m"`（依次 30秒、1分、1分、3分、3分、10分后重试）。

## BR-095 未付发票的判定

- **类型**: 业务规则
- **同义词**: 未付发票, unpaid invoice, 欠费发票, 未结清, outstanding invoice
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:189-203`

**规则**：一张发票被视为**未付**当且仅当同时满足：
1. 状态为 `COMMITTED`；
2. 余额 ≥ 1（即 > 0）；
3. 未核销（`!isWrittenOff`）；
4.（可选）`targetDate` 落在指定的 `[startDate, upToDate]` 范围内。
若发票存在父发票，则以父发票计算余额。

## BR-096 发票状态变更的约束与副作用

- **类型**: 业务规则
- **同义词**: 状态变更, changeInvoiceStatus, 作废副作用, 提交副作用, INVOICE_INVALID_STATUS
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:1387-1414`

**规则**：变更发票状态时：
- 若新状态与当前状态相同，或当前状态已是 `VOID` → 抛 `INVOICE_INVALID_STATUS`；
- 变更后重算账户信用（CBA complexity）；
- 变更为 `COMMITTED` → 发送**发票创建事件**（InvoiceCreationEvent）；
- 变更为 `VOID` → 发送**发票调整事件**，并**停用**该发票关联的用量 tracking ids（避免已作废发票的用量被重复计费）。

## BR-097 完全修复项的剔除（InvoicePruner）

- **类型**: 业务规则
- **同义词**: 完全修复, fully repaired, InvoicePruner, 修复闭合, 避免重复修复
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoicePruner.java:88-99`, `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoicePruner.java:156-232`

**规则**：构建发票项树前，先识别**已被完全修复**的 RECURRING 项——即其 `REPAIR_ADJ` 金额合计（取负）等于原项金额；此类原项连同其修复/调整项一并从树中剔除，避免区间重叠与重复修复。金额为 `$0` 的原项被忽略。

## BR-098 发票项调整金额取负

- **类型**: 业务规则
- **同义词**: 调整取负, ITEM_ADJ amount negate, 调整金额符号
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:230-239`

**规则**：创建 `ITEM_ADJ` 发票项时，金额以**负值**入账（`amountToAdjust.negate()`）。若未指定调整金额，默认取原项**全额**；若未指定币种，默认取原项币种。

## BR-099 发票项调整的归属校验

- **类型**: 业务规则
- **同义词**: 调整校验, INVOICE_ITEM_NOT_FOUND, 项不属于发票, adjustment validation
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:219-228`

**规则**：对发票项做调整时：
- 目标项不存在 → 抛 `INVOICE_ITEM_NOT_FOUND`；
- 目标项不属于指定发票 → 抛 `INVOICE_INVALID_FOR_INVOICE_ITEM_ADJUSTMENT`。

## BR-100 固定费用发票项生成规则

- **类型**: 业务规则
- **同义词**: 固定费生成, fixed price item, 初装费生成, FIXED 生成
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:427-472`

**规则**：在阶段开始时生成固定费发票项：
- 金额 = `fixedPrice × quantity`；
- 若该阶段**无 recurring 费用**且阶段类型**不是 EVERGREEN**，则固定项的 `endDate` 取下一个 `PHASE` 事件的生效日期，或当前阶段时长结束的日期；
- 若固定项 `startDate` 晚于 `targetDate`，则不生成该项。

## BR-101 周期发票项的分比生成规则

- **类型**: 业务规则
- **同义词**: 周期项生成, recurring item, 前置分比, 后置分比, leading proration, trailing proration
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:334-425`

**规则**：周期项按 BCD（bill cycle day）对齐生成：
1. 若 `endDate` 早于首个 BCD 日期 → 只收取一段**前置分比**（leading pro-ration）后返回；
2. 否则：先收 `[startDate, firstBillingCycleDate]` 的前置分比（若有），再收取若干**完整周期**（每段 amount 系数为 1），最后若 `effectiveEndDate` 晚于最后 BCD 日期则收一段**后置分比**（trailing pro-ration）；
3. 不足一天（`hasSomethingToBill()==false`）则不计费；
4. `endDate < startDate` 或 `targetDate < startDate` → 抛 `INVOICE_INVALID_DATE_SEQUENCE`。

## BR-102 发票项安全检查边界（safety bounds）

- **类型**: 业务规则
- **同义词**: 安全检查, safety bound, 重复项检测, 防止重复计费, SAFETY BOUND TRIGGERED
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:477-548`

**规则**：
- 当 `org.killbill.invoice.sanitySafetyBoundEnabled` = `true` 时：
  - 同一订阅同一 `startDate` **不得存在多个 FIXED 项**；
  - 同一订阅同一服务期间（start-end 区间）**不得存在多个 RECURRING 项**；
  - 违反即抛 `SAFETY BOUND TRIGGERED`（ErrorCode.UNEXPECTED_ERROR）。
- 单订阅**单日**生成的发票项数超过 `org.killbill.invoice.maxDailyNumberOfItemsSafetyBound`（默认 15）也会触发异常；该配置设为 `-1` 时禁用此边界。

## BR-103 下一次开票通知日期计算

- **类型**: 业务规则
- **同义词**: 下次开票日期, next notification date, next billing cycle, 下一账期
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:298-332`

**规则**：计算某订阅的下一次开票/通知日期：
- `IN_ADVANCE` 模式：取所有周期项中**最晚的 `endDate`**；
- `IN_ARREAR` 模式：取 `nextBillingCycleDate`。

## BR-104 逾期是账户级（跨订阅）规则

- **类型**: 业务规则
- **同义词**: 逾期是账户级, 账户维度催收, 跨订阅逾期, account-level overdue, overdue is per account
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:221-235`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:109-122`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueConfig.java:41-45`

**规则**：逾期状态以**账户**为粒度计算与持久化，而非单个订阅。持久化时用 `BlockingStateType.ACCOUNT` + 服务名 `overdue-service`（`storeNewState`）；计算时对「该账户所有未付发票」聚合（`unpaidInvoicesForAccount`）。配置模型也只有 `accountOverdueStates`，无订阅级状态。
**影响**：一个账户下任一未付发票都会影响整个账户的逾期状态；取消订阅动作会作用到账户下所有非 ADD_ON 订阅（见 BR-014）。

## BR-105 条件：未付发票数量达到阈值

- **类型**: 业务规则
- **同义词**: 未付发票数量, 欠费张数, 发票数量条件, numberOfUnpaidInvoicesEqualsOrExceeds, unpaid invoice count
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:77`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestCondition.java:49-68`

**规则**：`numberOfUnpaidInvoicesEqualsOrExceeds=N` 时，当且仅当 `state.getNumberOfUnpaidInvoices() >= N` 为真。测试证实：N=1 时 0 张不命中、1 张与 2 张命中。

## BR-106 条件：未付发票余额合计达到阈值

- **类型**: 业务规则
- **同义词**: 未付余额, 欠费金额, 余额阈值, totalUnpaidInvoiceBalanceEqualsOrExceeds, total unpaid balance
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:78`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestCondition.java:70-90`

**规则**：`totalUnpaidInvoiceBalanceEqualsOrExceeds=B` 时，当且仅当 `B <= state.getBalanceOfUnpaidInvoices()` 为真（BigDecimal 比较，含等于）。测试：B=100 时余额 0 不命中、100 与 200 命中。

## BR-107 条件：最早未付发票距今时长达到阈值

- **类型**: 业务规则
- **同义词**: 逾期天数, 最早未付发票时长, 账龄条件, timeSinceEarliestUnpaidInvoiceEqualsOrExceeds, days overdue, aging
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:71-74`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:79-80`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:99-118`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestCondition.java:92-114`

**规则**：配置 `<timeSinceEarliestUnpaidInvoiceEqualsOrExceeds><unit>…</unit><number>…</number></…>`。计算：`triggerDate = dateOfEarliestUnpaidInvoice + duration`；条件为真当且仅当 `triggerDate <= now`（`!triggerDate.isAfter(date)`）。若账户无最早未付发票日期（即无未付发票），该子条件为假。
**时间单位**：来自 `DefaultDuration`/`TimeUnit`，实际支持 `DAYS / WEEKS / MONTHS / YEARS`（`UNLIMITED` 非法）。测试：unit=DAYS, number=10 时「10 天前」与「20 天前」命中、「无日期」不命中。

## BR-108 条件：控制标签必须存在（controlTagInclusion）

- **类型**: 业务规则
- **同义词**: 必须包含标签, 标签包含条件, controlTagInclusion, include control tag, 标签门控
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:82`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:96-103`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestCondition.java:140-174`

**规则**：`controlTagInclusion=T` 时，当且仅当账户标签集合中存在 `tagDefinitionId == T.getId()` 的标签才为真。测试：`OVERDUE_ENFORCEMENT_OFF` 存在时命中，不存在时（仅有 AUTO_INVOICING_OFF/DescriptiveTag）不命中。配置示例见 `overdueWithControlTag.xml`（各状态要求 `TEST` 标签）。

## BR-109 条件：控制标签必须不存在（controlTagExclusion）

- **类型**: 业务规则
- **同义词**: 必须排除标签, 标签排除条件, controlTagExclusion, exclude control tag, 标签否决
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:83`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:105-112`, `profiles/killbill/src/test/resources/org/killbill/billing/server/overdueWithExclusionControlTag.xml:18-62`

**规则**：`controlTagExclusion=T` 时，当且仅当账户标签集合中**不存在**该控制标签才为真（存在则一票否决该状态条件）。配置示例见 `overdueWithExclusionControlTag.xml`（各状态用 `<controlTagExclusion>TEST</controlTagExclusion>`）。

## BR-110 条件：上次失败支付响应（当前未真正实现）

- **类型**: 业务规则
- **同义词**: 上次支付失败原因, 支付响应条件, responseForLastFailedPaymentIn, last failed payment response, PaymentResponse
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:81`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:86-94`, `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:79`

**规则（配置层）**：`responseForLastFailedPaymentIn=[R1,R2,…]` 时，当且仅当账户「上次失败支付响应」等于列表之一才为真。可配置值示例：`INVALID_CARD`、`LOST_OR_STOLEN_CARD`、`INSUFFICIENT_FUNDS`、`DO_NOT_HONOR`。
**重要例外（未实现）**：上游 `BillingStateCalculator` 把 `responseForLastFailedPayment` **硬编码为 `PaymentResponse.INSUFFICIENT_FUNDS`（源码注释 `//TODO MDW`）**，并未从真实支付失败记录读取。因此除了「恰好配置为 INSUFFICIENT_FUNDS」外的响应类型实际上无法命中。即：该条件是「已建模、但输入未接线（not implemented）」的功能。

## BR-111 多子条件为 AND，未配置的子条件被忽略

- **类型**: 业务规则
- **同义词**: 条件组合, 多条件与, AND 组合, condition AND, all conditions must hold
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:76-84`

**规则**：`evaluate` 返回对全部 6 个子条件的合取。每个子条件写成 `(cfg == null || 实际检查)`，因此**未配置（null）的子条件恒为真**——即不构成约束。只要有一个已配置的子条件为假，整个条件即为假。

## BR-112 状态选择：按配置顺序取首个命中状态，否则 clear

- **类型**: 业务规则
- **同义词**: 状态选择, 命中优先级, 匹配第一个状态, state selection, first matching state, calculateOverdueState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:59-67`, `overdue/src/test/resources/org/killbill/billing/overdue/OverdueConfig3.xml:18-70`

**规则**：`calculateOverdueState(billingState, now)` 按 `state[]` 的**声明顺序**从头遍历，返回第一个条件为真的状态；若无任何命中则返回 clear state。因此配置中**越靠前的状态优先级越高**。示例 `OverdueConfig3.xml` 顺序为 OD4→OD3→OD2→OD1，OD4（未付≥5 且带 AUTO_PAY_OFF）优先级最高。

## BR-113 状态升级顺序与「首状态」语义

- **类型**: 业务规则
- **同义词**: 状态升级, 升级顺序, 催收梯度, escalation order, first state, getFirstState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:92-95`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestOverdueConfig.java:70-76`, `profiles/killbill/src/main/resources/overdue.xml:19-61`

**规则**：约定配置里「最严重状态写在最前、最轻状态写在最后」。`getFirstState()` 返回数组**最后一个**元素，即**入门级/最轻**的逾期状态（如 OD1/OD3 场景中的 OD1，或 overdue.xml 中的 OD1）。测试 `TestOverdueConfig` 断言 OD2、OD1 顺序下 `getFirstState().getName()=="OD1"`。
**用途**：`firstOverdueState` 用于「尚未进入首个逾期状态但有未付发票，仍要安排下次检查」的判断（见 BR-016）。

## BR-114 状态未变化时为 no-op（但仍可能安排下次通知）

- **类型**: 业务规则
- **同义词**: 状态不变, 无操作, 幂等, no-op, state unchanged
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:127-132`

**规则**：`apply` 先处理通知调度（BR-016），随后若 `previousOverdueState.getName().equals(nextOverdueState.getName())`，直接返回——不取消订阅、不切换 AUTO_INVOICING_OFF、不写 BlockingState、不发事件。即：动作只在**状态真正变化**时执行。

## BR-115 blockChanges 动作映射到 BlockingState.blockChange

- **类型**: 业务规则
- **同义词**: 阻止变更动作, blockChange, 冻结变更
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:221-231`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:263-265`, `overdue/src/test/java/org/killbill/billing/overdue/TestOverdueHelper.java:119-124`

**规则**：施加状态时创建的 `DefaultBlockingState` 中 `blockChange = state.isBlockChanges() || state.isDisableEntitlementAndChangesBlocked()`。测试 helper 断言 blocking state 的 `isBlockChange()` 等于状态的 `isBlockChanges()`（仅在未 disableEntitlement 时；两者同真时也一致）。

## BR-116 disableEntitlementAndChangesBlocked 同时暂停权益与计费

- **类型**: 业务规则
- **同义词**: 禁用权益动作, 暂停服务, 停止计费, disableEntitlement, blockEntitlement, blockBilling, pause
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:263-273`, `overdue/src/test/java/org/killbill/billing/overdue/TestOverdueHelper.java:119-124`

**规则**：若 `isDisableEntitlementAndChangesBlocked()==true`，则 BlockingState 同时 `blockEntitlement=true`、`blockBilling=true`，并因 `blockChanges()` 的或运算而 `blockChange=true`。测试 helper 断言 `isBlockEntitlement()==isBlockBilling()==state.isDisableEntitlementAndChangesBlocked()`。业务效果：**暂停该账户的服务并停止计费**（stop billing / suspend），回到非 block billing 状态即 resume（见 BR-015）。

## BR-117 订阅取消策略：NONE / IMMEDIATE / END_OF_TERM

- **类型**: 业务规则
- **同义词**: 逾期取消订阅, 立即取消, 到期取消, 自动退订, subscriptionCancellationPolicy, IMMEDIATE, END_OF_TERM, cancel subscription on overdue
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:285-314`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:316-329`

**规则**：进入新状态时若 `getOverdueCancellationPolicy()`：
- `NONE` → 直接返回，不取消任何订阅；
- `IMMEDIATE` → 以 `BillingActionPolicy.IMMEDIATE` 取消；
- `END_OF_TERM` → 以 `BillingActionPolicy.END_OF_TERM` 取消；
- 其他值 → 抛 `IllegalStateException`。

**作用范围**：取账户下所有 entitlement，但**过滤掉 `ProductCategory.ADD_ON`**，只取消基础订阅（源码注释：Entitlement 会自行取消其 add-on，引用 killbill#94）。取消生效日 `context.toLocalDate(effectiveDate)`。

## BR-118 自动维护 AUTO_INVOICING_OFF 标签（防多生成信用）

- **类型**: 业务规则
- **同义词**: 自动关闭开票, 防止额外开票, AUTO_INVOICING_OFF 自动切换, avoid extra credit, toggle auto invoice off
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:176-183`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:237-253`

**规则**：
- 「进入 block billing」的转移（`isBlockBillingTransition`：prev 不 block billing、next block billing）→ 给账户打上 `AUTO_INVOICING_OFF` 标签，避免继续开票产生多余信用。
- 「解除 block billing」的转移（`isUnblockBillingTransition`）→ 移除 `AUTO_INVOICING_OFF` 标签；若标签本就不存在（`TAG_DOES_NOT_EXIST`）则忽略该错误。

## BR-119 重新评估通知的调度规则（定时器语义）

- **类型**: 业务规则
- **同义词**: 复评定时器, 下次检查安排, 通知队列, reevaluation timer, schedule next check, notification queue
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:109-125`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`

**规则**：
1. 需要安排下次通知的条件：`!nextOverdueState.isClearState()` **或**（有首个逾期状态 **且** 存在最早未付发票日期）——即「已逾期」或「有欠费但可能还没进入首个逾期状态」。
2. 间隔取值：clear 状态用状态集的 `initialReevaluationInterval`；非 clear 状态用该状态的 `autoReevaluationInterval`。
3. 若间隔为 null（配置缺失/无时间型条件）→ **不插入通知**，日志说明「条件非时间驱动，无需重试」。
4. 否则安排 `effectiveDate + reevaluationInterval` 的未来通知。
5. 若「next 为 clear 且不满足上述第 1 条」→ **清除**该账户所有未来通知（`clearFutureNotification`）。

## BR-120 clear 状态清除未来通知

- **类型**: 业务规则
- **同义词**: 清除通知, 取消定时, clear notifications, clear future notification
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:123-125`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:275-283`

**规则**：当 `nextOverdueState.isClearState()` 且不满足「有欠费需继续检查」时，移除该账户在 `overdue-check-queue` 上的所有未来逾期检查通知（按 accountRecordId/tenantRecordId 检索后逐条删除）。`clear(...)` 路径也会调用它。

## BR-121 OVERDUE_ENFORCEMENT_OFF 短路并触发 CLEAR

- **类型**: 业务规则
- **同义词**: 豁免催收, 关闭催收生效, OVERDUE_ENFORCEMENT_OFF 短路, skip overdue enforcement, overdue enforcement off
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:109-113`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:98-107`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:334-349`

**规则**：`refreshWithLock` 首先检查账户是否被打了 `OVERDUE_ENFORCEMENT_OFF`；若是则**直接 return**（不计算、不切状态、不安排通知）。同时，给账户**新增**该控制标签的事件会以 `OverdueAsyncBusNotificationAction.CLEAR` 入队，引导 `OverdueDispatcher.clearOverdueForAccount` 把账户置回 clear 状态。业务效果：运营可用该标签「豁免/停止催收并清零状态」。

## BR-122 触发重新评估的事件集合

- **类型**: 业务规则
- **同义词**: 重新评估触发, 刷新触发, 事件驱动催收, refresh triggers, reevaluation triggers
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-157`

**规则**：以下事件会使对应账户入队 `REFRESH`（重新评估）：
- 发票创建（InvoiceCreationInternalEvent）
- 发票调整（InvoiceAdjustmentInternalEvent）
- 支付信息（InvoicePaymentInfoInternalEvent）
- 支付错误（InvoicePaymentErrorInternalEvent）
- 发票级 `WRITTEN_OFF` 标签的创建/删除
- 账户级 `OVERDUE_ENFORCEMENT_OFF` 标签的删除
（账户级 `OVERDUE_ENFORCEMENT_OFF` 标签的**新增**特殊处理为 `CLEAR`，见 BR-018。）

## BR-123 仅当存在带条件的状态时才运行逾期机制（优化）

- **类型**: 业务规则
- **同义词**: 催收启用开关, 无配置不运行, shouldInsertNotification, overdue disabled optimization
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:168-174`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:206-225`

**规则**：监听器入队前调用 `shouldInsertNotification`：若租户逾期配置为空、`accountOverdueStates` 为空、状态数组为空，或**所有状态都没有 condition**（`getConditionEvaluation()` 全为 null），则不入队、直接返回。目的：若逾期未被有效配置，就不必跑整条催收链路。

## BR-124 父/子账户的级联与委派支付

- **类型**: 业务规则
- **同义词**: 父子账户, 委派支付, 家庭账户, parent child account, payment delegated to parent, cascade overdue
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:151-159`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:179-203`

**规则**：
1. **计算委派**：若账户有 `parentAccountId` 且 `isPaymentDelegatedToParent()`，则其逾期计费状态从**父账户**的上下文计算（用父账户 recordId 构造 context）。
2. **刷新级联**：账户入队 REFRESH/CLEAR 时，若其向父账户委派支付，则父账户也入队；并遍历其子账户，凡 `isPaymentDelegatedToParent()` 的子账户也入队。加载子账户失败仅记日志、不中断。

## BR-125 账户级全局锁与重试（MAX_LOCK_RETRIES=50）

- **类型**: 业务规则
- **同义词**: 逾期并发锁, 账户锁, 锁重试, global lock, MAX_LOCK_RETRIES, ACCNT_INV_PAY lock
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:56`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:89-107`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:129-142`

**规则**：`refresh`/`clear` 都先获取类型为 `ACCNT_INV_PAY`、键为账户 id 的全局锁，最多尝试 `MAX_LOCK_RETRIES=50` 次。获取失败（`LockFailedException`）时抛 `QueueRetryException`，并携带 `overdueConfig.getRescheduleIntervalOnLock(context)` 作为重排周期（由 killbill config 项控制），保证并发下操作最终执行。锁在 finally 释放。

## BR-126 autoReevaluationInterval 合法性校验

- **类型**: 业务规则
- **同义词**: 复评间隔校验, 无复评间隔错误, autoReevaluationInterval validation, OVERDUE_NO_REEVALUATION_INTERVAL
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:119-125`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`

**规则**：`OverdueState.getAutoReevaluationInterval()` 在 `autoReevaluationInterval==null`、`unit==UNLIMITED` 或 `number==0` 时抛 `OverdueApiException(OVERDUE_NO_REEVALUATION_INTERVAL, name)`。`OverdueStateApplicator.getReevaluationInterval` 捕获该错误码并返回 null → 不安排下次通知（其他错误码则转成 OverdueException 抛出）。

## BR-127 initialReevaluationInterval 为无效值时不重试

- **类型**: 业务规则
- **同义词**: 初始复评间隔, clear 状态轮询, initialReevaluationInterval
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:51-57`

**规则**：`getInitialReevaluationInterval()` 在 `initialReevaluationInterval==null`、`unit==UNLIMITED` 或 `number==0` 时返回 `null`；`OverdueStateApplicator` 收到 null 即不插入通知。也就是说 clear 状态若要被周期性复检，必须显式配置一个正数的初始复评间隔。

## BR-128 状态名长度上限 50

- **类型**: 业务规则
- **同义词**: 状态名长度, 名称上限, state name max length
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:47`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:171-178`

**规则**：`MAX_NAME_LENGTH = 50`；校验时若状态名长度超过 50，追加 ValidationError（"Name of state '%s' exceeds the maximum length of %d"）。这是逾期配置的硬校验项。

## BR-129 默认配置只含 Clear 状态（等价于未启用催收）

- **类型**: 业务规则
- **同义词**: 默认逾期配置, 无逾期配置, NoOverdueConfig, default overdue config, overdue disabled
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/resources/NoOverdueConfig.xml:20-27`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:58-66`

**规则**：内建默认配置 `NoOverdueConfig.xml` 的 `accountOverdueStates` 只包含一个 `name="Clear"` 且 `isClearState=true` 的状态，无任何条件。因此默认情况下没有任何状态会命中，账户始终为 clear，催收动作不触发。若默认配置 URL 为空或加载失败，系统记 warn 并处于「逾期系统禁用」状态（不改变状态）。

## BR-130 配置加载失败/无效时逾期系统被禁用

- **类型**: 业务规则
- **同义词**: 逾期配置加载失败, 配置无效, overdue disabled, config load failure
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/service/DefaultOverdueService.java:91-101`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:68-86`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:99-105`

**规则**：`DefaultOverdueService.loadConfig`（生命周期 LOAD_CATALOG）从 `properties.getConfigURI()` 加载默认配置；失败则 log.warn「Overdue system disabled」并保持 `isConfigLoaded=false`。租户级配置解析失败会被包装成 `OverdueApiException(OVERDUE_INVALID_FOR_TENANT)`；单个租户配置无效不影响其他租户（`get` 失败时抛异常，未命中则回退默认配置）。

## BR-131 通知去重：check 队列保留最早、async 队列有则跳过

- **类型**: 业务规则
- **同义词**: 通知去重, 队列去重, notification dedup, cleanup future notifications
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueCheckPoster.java:48-85`, `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusPoster.java:47-57`, `overdue/src/main/java/org/killbill/billing/overdue/notification/DefaultOverduePosterBase.java:67-84`

**规则**：插入未来通知前会在事务内查询该账户已有的未来通知：
- **overdue-check（定时复评）**：若已存在一条**更早**的通知，则不再插入新通知，并删除其余未来通知；否则删除已有通知、插入新通知。即**保留最早到期的那条**。
- **overdue-async-bus（事件刷新）**：若已存在任意未来通知则直接跳过插入（源码注释承认这是近似处理，可能出现 REFRESH/CLEAR 混排的非确定行为）。

## BR-132 getOverdueStateFor 从 blocking state 名解析当前状态

- **类型**: 业务规则
- **同义词**: 查询当前逾期状态, 当前状态解析, getOverdueStateFor, current overdue state
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:91-99`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:115-119`

**规则**：查询账户当前逾期状态时，读取该账户在 `overdue-service` 上的 BlockingState；若不存在则用 `CLEAR_STATE_NAME`，再通过状态集 `findState(stateName)` 解析。`findState` 对 clear 名特判返回内建 clearState，否则按名字查配置状态，找不到抛 `CAT_NO_SUCH_OVERDUE_STATE`。这条规则同时决定了「刷新时 previousOverdueState 的取值」。

## BR-133 租户配置上传会覆盖旧值并失效缓存

- **类型**: 业务规则
- **同义词**: 上传逾期配置, 覆盖配置, 配置缓存失效, upload overdue config, cache invalidation, OVERDUE_CONFIG
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:66-89`, `overdue/src/main/java/org/killbill/billing/overdue/caching/OverdueCacheInvalidationCallback.java:39-43`, `overdue/src/main/java/org/killbill/billing/overdue/service/DefaultOverdueService.java:103-113`

**规则**：上传逾期配置时：先删除租户键 `OVERDUE_CONFIG` 的旧值（若存在），再写入新 XML，然后清除该租户的逾期配置缓存。租户配置变更也会通过 `TenantKey.OVERDUE_CONFIG` 的 `CacheInvalidationCallback` 触发缓存失效。以 `OverdueConfig` 对象上传时，先序列化为 XML（`XMLWriter`），失败抛 `OVERDUE_INVALID_FOR_TENANT`。

## BR-134 有效日与条件日期口径

- **类型**: 业务规则
- **同义词**: 生效日期, 评估日期, effectiveDate, now, account timezone
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:104-107`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:124-127`, `api/src/main/java/org/killbill/billing/overdue/config/api/OverdueStateSet.java:30-38`

**规则**：状态评估用「账户时区的 LocalDate」作为 `now`（`context.toLocalDate(context.getCreatedDate())`），条件里的时长比较基于该日；而状态施加（写 BlockingState、取消订阅）用带时间的 `effectiveDate`（`context.toLocalDate(effectiveDate)` 取日）。同一账户的评估日期口径必须在账户时区下解释。

## BR-135 取消动作只针对非 ADD_ON 基础订阅

- **类型**: 业务规则
- **同义词**: 取消基础订阅, 排除附加组件, 取消不含 add-on, cancel base subscriptions, exclude ADD_ON
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:316-329`

**规则**：`computeEntitlementsToCancel` 过滤掉 `ProductCategory.ADD_ON` 的 entitlement，只把非附加组件订阅放入待取消列表。源码注释说明 Entitlement 层会自动取消关联的 add-on（引用 killbill issue #94），并提示此实现会漏掉「未来创建的 add-on」。

## BR-136 逾期状态持久化为账户 BlockingState

- **类型**: 业务规则
- **同义词**: 逾期状态持久化, blocking state, 状态存储, persist overdue state, setBlockingState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:221-235`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:139-142`

**规则**：新状态通过 `blockingApi.setBlockingState(new DefaultBlockingState(accountId, BlockingStateType.ACCOUNT, stateName, "overdue-service", blockChange, blockEntitlement, blockBilling, effectiveDate))` 持久化。源码注释强调：**必须最后再存新状态**——因为 entitlement DAO 会发 BlockingTransitionInternalEvent，invoice 会据此反应，需先让含 AUTO_INVOICING_OFF 等最新信息落库。存状态失败包装为 `OVERDUE_CAT_ERROR_ENCOUNTERED`。

## BR-137 clear 路径的状态与通知处理

- **类型**: 业务规则
- **同义词**: 清除逾期, 解除逾期, 恢复账户, clear overdue, clear path
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:185-213`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:144-149`

**规则**：`clear(effectiveDate, account, previousState, clearState, ctx)` 顺序为：写入 clear 状态 → 清除未来通知 → 按需切换 AUTO_INVOICING_OFF（从 block billing 回落则移除标签）→ 构造并投递 `OverdueChangeInternalEvent`（记录 previous→clear 及 unblock 标志）。`OverdueWrapper.clearWithLock` 先查出账户当前状态名再调用它。

## BR-138 内部租户始终使用默认配置

- **类型**: 业务规则
- **同义词**: 内部租户配置, 默认配置回退, internal tenant, default config fallback
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:93-106`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:108-113`

**规则**：当 `tenantRecordId` 等于 `InternalCallContextFactory.INTERNAL_TENANT_RECORD_ID` 时，直接返回默认配置、不进租户缓存；`clearOverdueConfig` 对内部租户也是 no-op。普通租户先查 `TENANT_OVERDUE_CONFIG` 缓存，缓存未命中则返回默认配置；读取抛 IllegalStateException 时转 `OVERDUE_INVALID_FOR_TENANT`。

## BR-139 逾期配置 URI 由 `org.killbill.overdue.uri` 控制

- **类型**: 业务规则
- **同义词**: 逾期配置路径, 配置 URI, org.killbill.overdue.uri, config URI, NoOverdueConfig.xml
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/OverdueProperties.java:25-31`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:58-66`

**规则**：默认逾期配置的位置由配置项 `org.killbill.overdue.uri` 指定，默认值 `NoOverdueConfig.xml`（classpath 或文件系统 URI）。`DefaultOverdueConfigCache` 构造时会先以内建 URI `NoOverdueConfig.xml` 预载默认配置；随后 `loadConfig` 用该配置项覆盖。这解释了「系统默认不催收、要显式指向自定义 XML 才启用」的语义。

## BR-140 支付失败重试计划（默认 8,8,8 天）

- **类型**: 业务规则
- **同义词**: 重试间隔, 重试天数, 重试次数, payment retry days, retry interval, 8 8 8
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:31-39`

**规则**：系统属性 `org.killbill.payment.retry.days`（默认 `8,8,8`）定义支付失败后的重试间隔（天）。默认值表示最多重试 3 次，每次间隔 8 天。

## BR-141 插件失败重试参数（初始 300 秒 / 倍数 2 / 最多 8 次）

- **类型**: 业务规则
- **同义词**: 网关重试, 插件失败重试, 指数退避, plugin failure retry, gateway down retry, retry multiplier
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:41-90`

**规则**：当支付失败原因是插件失败（网关宕机、瞬时错误等）时：
- `org.killbill.payment.failure.retry.start.sec` 默认 `300`，即首次重试等待 300 秒；
- `org.killbill.payment.failure.retry.multiplier` 默认 `2`，后续重试间隔按倍数递增（指数退避）；
- `org.killbill.payment.failure.retry.max.attempts` 默认 `8`，最多重试 8 次。

## BR-142 Janitor 未完成交易重试计划（UNKNOWN / PENDING）

- **类型**: 业务规则
- **同义词**: janitor 重试间隔, unknown retries, pending retries, 未完成交易重试, 支付巡检间隔
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:61-79`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:102-110`

**规则**：
- `org.killbill.payment.janitor.unknown.retries` 默认 `5m,1h,1d,1d,1d,1d,1d`，即 UNKNOWN 交易的回查/重试延迟序列；
- `org.killbill.payment.janitor.pending.retries` 默认 `1h, 1d`，即 PENDING 交易的回查/重试延迟序列；
- `org.killbill.payment.janitor.rate` 默认 `1h`，Janitor 主任务的调度频率；
- `org.killbill.payment.janitor.attempts.delay` 默认 `12h`，未完成支付尝试（attempt）的重试延迟。

## BR-143 AUTO_PAY_OFF 账户自动支付中止

- **类型**: 业务规则
- **同义词**: 自动支付关闭, 停止自动扣款, auto pay off, auto-payoff abort, 标签关闭自动支付
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:730-745`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:376-380`

**规则**：当发起非 API（系统自动）发票支付时，若账户带有 `AUTO_PAY_OFF` 标签（`ControlTagType.isAutoPayOff`），则：
1. 向 `invoice_payment_control_plugin_auto_pay_off` 表插入一条挂起记录（`PluginAutoPayOffModelDao`）；
2. 中止本次支付（返回 abort）。
**例外**：API 发起的支付（`isApiPayment()` 为 true）不受 AUTO_PAY_OFF 影响。

## BR-144 未提交(非 COMMITTED)发票不允许支付

- **类型**: 业务规则
- **同义词**: 草稿发票不扣款, 发票未提交, draft invoice payment, COMMITTED invoice, 发票状态校验
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:341-351`

**规则**：购买（PURCHASE）前校验发票状态，若发票不是 `COMMITTED`（如 DRAFT），记录日志并中止支付（`DefaultPriorPaymentControlResult(true)`）。

## BR-145 委托给父账户的子账户发票不自动支付

- **类型**: 业务规则
- **同义词**: 父账户代付, 子账户委托, delegated payment, parent account payment, 子账户不扣款
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:353-360`

**规则**：若账户的支付被委托给父账户（`accountData.isPaymentDelegatedToParent()` 为 true）或发票已关联父账户（`invoice.getParentAccountId() != null`），则中止本账户的支付扣款。

## BR-146 空发票(余额为 0)支付处理

- **类型**: 业务规则
- **同义词**: 零元发票, 空发票, 余额为零, zero amount invoice, empty invoice, allowEmptyInvoice
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:362-374`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:138-141`

**规则**：当请求支付金额计算结果 ≤ 0（发票已付清）时：
- 若系统属性 `org.killbill.payment.allow.emptyInvoice` 为 `true`（默认 `false`），则**不中止**，继续以 0 元发起支付；
- 否则视为"发票已支付"并中止支付。

## BR-147 支付金额不得超过发票余额

- **类型**: 业务规则
- **同义词**: 支付金额校验, 超付校验, 余额上限, overpayment, invoice balance, invalid amount
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:710-728`

**规则**：`validateAndComputePaymentAmount` 对金额做如下判定：
- 发票余额 ≤ 0 → 返回 0；
- 若为 API 支付且显式传入金额大于发票余额 → 抛 `PaymentApiException`（`PAYMENT_PLUGIN_EXCEPTION`，"Invalid amount"）；
- 否则取 `min(输入金额, 发票余额)` 作为实际支付金额；输入为 null 时取发票余额。

## BR-148 退款金额计算（按发票项或显式金额）

- **类型**: 业务规则
- **同义词**: 退款金额, 部分退款, 退款上限, refund amount, partial refund, invoice item adjustment
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:529-556`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:438-478`

**规则**：
- 若显式指定退款金额（`specifiedRefundAmount`），必须 > 0，否则报错"需要指定正数退款金额"；该金额直接作为退款额。
- 若未指定，则按退款关联的发票项（`invoiceItemIdsWithAmounts`）累加：每项可取显式金额（必须 > 0 且不超过该项原始金额）或默认取该项原始金额。
- 若计算出的可退金额为 0 且为 API 支付 → 抛错中止退款。

## BR-149 失败支付的下次重试日期计算

- **类型**: 业务规则
- **同义词**: 重试日期, 下次重试, retry date, next retry, 重试计划计算, IPCD_RETRIES
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:567-628`

**规则**：`computeNextRetryDate` 决定失败购买交易是否/何时重试：
- **API 发起的支付默认不重试**：除非插件属性 `IPCD_RETRIES` 为 true，否则 `isApiPayment` 为真时直接返回 null（不重试）。
- 取该支付下最后一次 PURCHASE 交易的状态：
  - `PAYMENT_FAILURE` → 按 `org.killbill.payment.retry.days`（默认 8,8,8）取第 `retryCount` 天的间隔；`retryCount = 已处于 PAYMENT_FAILURE 的尝试数 - 1`；超过重试天数数组长度则不再重试。
  - `PLUGIN_FAILURE` → 按失败重试次数做指数退避：`nbSec = start.sec × multiplier^(retryAttempt-1)`，其中 retryAttempt = 已处于 PLUGIN_FAILURE 的尝试数 - 1；达到 `max.attempts`（默认 8）后不再重试。
  - `UNKNOWN` / 其他 → 不重试。

## BR-150 默认支付方式取自账户 (account.paymentMethodId)

- **类型**: 业务规则
- **同义词**: 默认支付方式, 账户默认卡, default payment method, account payment method, 自动扣款用哪张卡
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:252-257`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:382-397`

**规则**：执行支付时若调用方未显式传入 `paymentMethodId`，则使用账户上的默认支付方式（`account.getPaymentMethodId()`）。在发票自动支付场景中，若控制上下文 `getPaymentMethodId()` 为 null（账户无默认支付方式），则记录一条 `InvoicePaymentStatus.INIT` 的支付尝试完成事件并**中止**本次扣款（不会被触发）。

## BR-151 插件状态(PluginStatus)到交易状态/操作结果的映射

- **类型**: 业务规则
- **同义词**: 插件状态, 支付结果映射, plugin status, PaymentPluginStatus, PROCESSED, CANCELED, UNDEFINED, 交易状态转换
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentTransactionInfoPluginConverter.java:33-72`

**规则**：将支付插件返回的 `PaymentPluginStatus` 映射为内部 `TransactionStatus`（和操作结果 `OperationResult`）：

| 插件状态 | TransactionStatus | OperationResult | 含义 |
|---|---|---|---|
| `PROCESSED` | `SUCCESS` | `SUCCESS` | 交易成功 |
| `PENDING` | `PENDING` | `PENDING` | 处理中，待确认 |
| `ERROR` | `PAYMENT_FAILURE` | `FAILURE` | 交易到达网关但被拒（如信用卡被拒） |
| `CANCELED` | `PLUGIN_FAILURE` | `EXCEPTION` | 插件确信交易未发生（连接失败等） |
| `UNDEFINED`/null | `UNKNOWN` | `EXCEPTION` | 结果未知，交 Janitor 回查修正 |

## BR-152 单笔支付不允许并发的未决交易

- **类型**: 业务规则
- **同义词**: 防重复扣款, 未决交易, 并发支付, double payment, pending transaction, 重复提交
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:352-385`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:308-310`

**规则**：
- 对 AUTHORIZE / PURCHASE / CREDIT，若同一支付下已存在 `PENDING` 状态的交易且调用未指定该交易 id/key，则抛 `PAYMENT_INVALID_OPERATION` 阻止新交易（防止重复扣款）。
- 若待完成的交易处于 `UNKNOWN` 状态，则无法确定其在状态机中的位置，直接抛 `PAYMENT_INVALID_OPERATION` 拒绝本次操作。
- 同一 `transactionExternalKey` 不允许已有成功的非 CHARGEBACK 交易（`PAYMENT_ACTIVE_TRANSACTION_KEY_EXISTS`），且该 key 不能跨账户（`PAYMENT_TRANSACTION_DIFFERENT_ACCOUNT_ID`）。

## BR-153 执行交易前先调用 Janitor 修正状态

- **类型**: 业务规则
- **同义词**: 先巡检再支付, janitor 修正, refresh before payment, 支付前修复状态
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:282-290`

**规则**：执行任何支付操作（`performOperation`）时，若该支付已存在，系统**先**调用 `paymentRefresher.invokeJanitor` 获取插件最新状态并修正本地状态，**然后**才让状态机推进交易。这样可避免因为本地状态陈旧而做出错误的状态流转（如重复扣款或错误拒绝）。

## BR-154 Janitor 下次回查时间计算（UNKNOWN/PENDING 重试表）

- **类型**: 业务规则
- **同义词**: janitor 回查间隔, 下次巡检时间, janitor retry schedule, unknown retries, pending retries
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:401-418`

**规则**：`getNextNotificationTime` 根据交易状态选择延迟表：
- `UNKNOWN` → 使用 `org.killbill.payment.janitor.unknown.retries`（默认 `5m,1h,1d,1d,1d,1d,1d`）；
- `PENDING` → 使用 `org.killbill.payment.janitor.pending.retries`（默认 `1h, 1d`）；
- 取第 `attemptNumber` 个延迟作为下次通知时间；若 `attemptNumber > 表长度`，返回 null（不再回查）。

## BR-155 支付控制插件可调整支付参数，默认禁止覆盖已有支付方式

- **类型**: 业务规则
- **同义词**: 控制插件调整, 修改支付方式, overwrite payment method, adjusted payment method, 插件改金额
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/control/ControlPluginRunner.java:128-151`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:133-136`

**规则**：控制插件 `priorCall` 返回值可调整：支付方式 id（`AdjustedPaymentMethodId`）、插件名、金额、币种、插件属性；任一插件的 `isAborted()` 为真则抛 `PaymentControlApiAbortException` 中止。**覆盖限制**：若插件试图设置 paymentMethodId，但该支付已存在 paymentMethodId 且系统属性 `org.killbill.payment.method.overwrite` 为 `false`（默认），则抛 `PaymentControlApiException` 拒绝覆盖。

## BR-156 支付插件按支付方式的 pluginName 查找

- **类型**: 业务规则
- **同义词**: 插件查找, 找不到插件, payment plugin lookup, no such payment plugin, plugin not found
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentPluginServiceRegistration.java:80-91`

**规则**：执行支付时，系统根据支付方式记录里的 `pluginName` 从 OSGI 注册表查找对应 `PaymentPluginApi`；若插件未注册，抛 `PaymentApiException(ErrorCode.PAYMENT_NO_SUCH_PAYMENT_PLUGIN, pluginName)`。

## BR-157 支付插件调用超时与线程配置

- **类型**: 业务规则
- **同义词**: 插件超时, 支付线程数, 插件调用超时, payment plugin timeout, plugin threads, dispatch timeout
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dispatcher/PluginDispatcher.java:44-69`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:118-131`

**规则**：
- `org.killbill.payment.plugin.timeout` 默认 `30s`：每个支付插件调用通过独立线程池执行，超过该超时抛 `TimeoutException`；
- `org.killbill.payment.plugin.threads.nb` 默认 `10`：插件调度线程池大小；
- `org.killbill.payment.globalLock.retries` 默认 `50`：获取全局锁（每次等待 100ms）的最大重试次数。

## BR-158 支付错误事件与插件错误事件

- **类型**: 业务规则
- **同义词**: 支付错误事件, 插件错误事件, payment error event, plugin error event, bus event, 快照事件
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentErrorEvent.java:32-58`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentPluginErrorEvent.java:32-58`, `payment/src/main/java/org/killbill/billing/payment/core/sm/payments/PaymentEnteringStateCallback.java:49-82`

**规则**：
- `DefaultPaymentErrorEvent`（bus 类型 `PAYMENT_ERROR`）：当交易未创建且调用来自非 API（如自动扣款）时发送，消息为"Early abortion of payment transaction"（如缺少默认支付方式等异常情况）。
- `DefaultPaymentPluginErrorEvent`（bus 类型 `PAYMENT_PLUGIN_ERROR`）：插件层错误事件。
- 两者均携带 accountId / paymentId / paymentTransactionId / amount / currency / status / transactionType / effectiveDate / apiPayment / message。

## BR-159 外部支付通过插件属性模拟失败（测试/演示语义）

- **类型**: 业务规则
- **同义词**: 外部支付失败模拟, external payment fail, killbill.external.payment.fail, 演示失败
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/provider/ExternalPaymentProviderPlugin.java:144-178`

**规则**：`__EXTERNAL_PAYMENT__` 插件根据插件属性决定返回结果，便于记录/演示各种外部支付情形：
- `killbill.external.payment.fail.error=true` → 返回 `PaymentPluginStatus.ERROR`（支付失败）；
- `killbill.external.payment.fail.exception=true` → 抛 `PaymentPluginApiException`；
- `killbill.external.payment.fail.cancellation=true` → 返回 `CANCELED`（插件失败）；
- `killbill.external.payment.fail.timeout=true` → 休眠 `payment.plugin.timeout + 1000ms` 触发超时；
- 默认返回 `PROCESSED`（成功记录）。

## BR-160 外部支付（__EXTERNAL_PAYMENT__）的用途

- **类型**: 业务规则
- **同义词**: 外部支付用途, 线下支付记录, external payment usage, 记录支票支付, 手动入账
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/provider/ExternalPaymentProviderPlugin.java:47-52`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:112-116`, `payment/src/main/java/org/killbill/billing/payment/provider/DefaultPaymentProviderPluginRegistry.java:40-43`

**规则**：`__EXTERNAL_PAYMENT__` 用于**记录并非由 Kill Bill 发起/处理的外部支付**（例如支票、银行转账已到账），它不做真实网关交互，直接把交易标记为成功。系统属性 `org.killbill.payment.provider.default`（默认 `__external_payment__`）指定默认支付提供者。因此当某支付方式绑定到该插件时，Kill Bill 只记录该笔支付而不调用任何外部网关。

## BR-161 各交易类型的插件操作与无金额操作

- **类型**: 业务规则
- **同义词**: 交易类型操作, void 无金额, authorize capture purchase, 插件方法映射, 无金额撤销
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/provider/ExternalPaymentProviderPlugin.java:63-101`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:100-143`

**规则**：每类交易对应插件的不同方法，且金额语义不同：
- `AUTHORIZE`→`authorizePayment`（带金额）、`CAPTURE`→`capturePayment`（带金额）、`PURCHASE`→`purchasePayment`（带金额）；
- `REFUND`→`refundPayment`（带退款金额）、`CREDIT`→`creditPayment`（带金额）；
- `VOID`→`voidPayment`（**不带金额**，插件侧以 `BigDecimal.ZERO`/null 币种表示）；
- `CHARGEBACK`→由 `createChargeback`/`createChargebackReversal` 触发（拒绝即冲销，`ChargebackReversal` 使用 `OperationResult.FAILURE`）。
`PaymentProcessor` 对外暴露 `createAuthorization` / `createCapture` / `createPurchase` / `createVoid` / `createRefund` / `createCredit` / `createChargeback` / `createChargebackReversal` 等入口。

## BR-162 支付状态机 linkStateMachines：交易类型的先后约束

- **类型**: 业务规则
- **同义词**: 交易顺序, 授权后捕获, 捕获后退款, state machine links, 允许的交易链
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/resources/org/killbill/billing/payment/PaymentStates.xml:412-497`

**规则**：`linkStateMachines` 定义了不同交易类型之间的合法衔接（即"下一步能做什么"）：
- 从 `BIG_BANG_INIT` 可发起 AUTHORIZE / PURCHASE / CREDIT；
- `AUTH_SUCCESS` 后只能转向 CAPTURE 或 VOID；
- `CAPTURE_SUCCESS` 后可转向 REFUND、再次 CAPTURE、或 CHARGEBACK；
- `PURCHASE_SUCCESS` 后可转向 REFUND 或 CHARGEBACK；
- `REFUND_SUCCESS` 后可再次 REFUND 或 CHARGEBACK；
- `CHARGEBACK_SUCCESS` 后可再次 CHARGEBACK（多次拒付），`CHARGEBACK_FAILED` 后可 REFUND。

这解释了业务上"必须先授权再捕获、捕获后才能退款、拒付只能在扣款/退款之后"等顺序约束。

## BR-163 支付状态机成功态判定

- **类型**: 业务规则
- **同义词**: 成功态判定, isSuccessState, success state, 支付成功判断
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:236-239`

**规则**：`isSuccessState(stateName)` 判定某状态是否成功态：状态名以 `SUCCESS` 结尾**或**以 `CHARGEBACK` 开头（即所有 `CHARGEBACK_*` 状态都被视为成功，因为拒付本身是"已确认发生"的终态）。

## BR-164 未提供跟踪号时自动生成

- **类型**: 业务规则
- **同义词**: 自动跟踪号, 随机跟踪号, 默认trackingId, auto tracking id, generated tracking id, random tracking id
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:74-82`

**规则**：若 `record.getTrackingId()` 为 `null` 或空字符串，则本次提交生成一个随机 UUID 作为 `trackingId`。此时该批次不具备调用方可控的幂等键（每次提交都会是新值，无法借此拦截重复）。

## BR-165 同一批提交共用同一跟踪号

- **类型**: 业务规则
- **同义词**: 批量共用跟踪号, 同批trackingId, batch tracking id, shared tracking id, 同批次幂等
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:85-91`

**规则**：`recordRolledUpUsage` 对入参中所有 `UnitUsageRecord` × 所有 `UsageRecord` 展开出的每一行，都写入**同一个** `trackingIds` 变量值（要么是调用方给的，要么是生成的随机值）。因此去重探测的粒度是「整批」，只要有任意一行已存在该 trackingId，整批都会被拒。

## BR-166 订阅用量查询：半开区间 [start, end) + 单位类型过滤

- **类型**: 业务规则
- **同义词**: 用量查询时间范围, 半开区间, 用量区间, usage query range, start end date, record_date filter
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:37-48`, `usage/src/main/java/org/killbill/billing/usage/dao/DefaultRolledUpUsageDao.java:55-58`

**规则**：`getUsageForSubscription` 的 SQL 条件为 `record_date >= :startDate AND record_date < :endDate AND unit_type = :unitType` 且租户匹配。即左闭右开；结束时刻当刻的用量不计入。

**注意**：`unitType` 是**必须精确匹配**的过滤条件（非空时），无法用它做模糊/多值查询。查询单一单位类型用此方法。

## BR-167 账户原始用量查询：闭区间 [start, end]（开票唯一查询）

- **类型**: 业务规则
- **同义词**: 账户用量查询, 开票用量查询, 闭区间, 含退订日, raw usage for account, account usage, invoicing usage query
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:62-73`, `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultInternalUserApi.java:63-84`

**规则**：`getRawUsageForAccount` 的 SQL 条件为 `account_record_id = :accountRecordId AND record_date >= :startDate AND record_date <= :endDate`（**右闭**），且租户匹配。模板注释明确说明：「这是唯一用于开票的查询，因此使用 `<= :endDate` 以便处理退订当日的用量数据」。

**含义**：订阅维度的查询用 `< endDate`，而开票维度的账户查询用 `<= endDate`，两者边界语义不同，不能混用。

**范围**：该方法按 `account_record_id` 跨该账户下所有订阅查询，返回全部单位类型的明细（无 `unit_type` 过滤）。

## BR-168 用量按单位类型汇总求和

- **类型**: 业务规则
- **同义词**: 用量汇总, 求和, 聚合, rollup sum, aggregate usage, sum by unit type
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:158-168`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:136-156`

**规则**：无论数据来自 DB（`getRolledUpUnits`）还是插件（`getRolledUpUnitsForRawPluginUsage`），都用一个 `Map<String, BigDecimal>` 以 `unitType` 为键累加 `amount`（`currentAmount.add(cur.getAmount())`），最后映射为 `RolledUpUnit` 列表。

**含义**：查询结果是**同一区间内同单位类型的数值之和**；重复日期、多行记录都会被累加，不会保留明细。

**插件分支的额外过滤**：插件返回的原始记录会先按 `subscriptionId` 过滤（不等则跳过），再在指定 `unitType` 时按单位类型过滤，之后才求和。

## BR-169 查询结果排序：按 record_id 升序（提交顺序）

- **类型**: 业务规则
- **同义词**: 用量排序, 查询顺序, 提交顺序, order by record_id, usage ordering, insertion order
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:46-47`, `util/src/main/resources/org/killbill/billing/util/entity/dao/EntitySqlDao.sql.stg:31-33`

**规则**：所有用量查询都带 `<defaultOrderBy("")>`，展开为 `order by record_id ASC`。`record_id` 是自增 serial 主键，故返回顺序即**落库（提交）先后顺序**，而非按 `record_date` 排序。

**注意**：不要假设结果按日期升序；如需按日期处理，调用方须自行排序（开票侧 `RawUsageOptimizer` 即自行按 endDate 排序）。

## BR-170 同一 (订阅, 单位类型, 日期) 重复提交会累加，不覆盖

- **类型**: 业务规则
- **同义词**: 重复用量, 用量覆盖, 用量累加, duplicate usage, overwrite, additive, 重复记录
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/ddl.sql:18`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:158-168`, `usage/src/test/java/org/killbill/billing/usage/dao/TestDefaultRolledUpUsageDao.java:139-169`

**规则**：`rolled_up_usage` 唯一的唯一索引建在 `id`（随机 UUID）上，**没有** `(subscription_id, unit_type, record_date)` 的业务键唯一约束。因此：
- 用不同 `trackingId` 对同一订阅、同一单位类型、同一日期再次提交，会新增行，查询时被求和 → **数值翻倍（累加而非覆盖）**。
- 没有任何「更新/覆盖」用量的 API；用量是**只追加（append-only）**的（DAO 无 update 方法，实体 `getHistoryTableName()` 为 `null`）。
- 测试 `testDuplicateRecords` 展示的是「把同一批 `RolledUpUsageModelDao`（含固定 `id`）插入两次」会因唯一索引 `rolled_up_usage_id` 冲突抛 `UnableToExecuteStatementException`——即只有**相同记录 ID**才会被拒。

**业务结论**：去重的唯一可靠手段是 `trackingId`（见 BR-001）；不要依赖系统对「同日期重复上报」自动去重。

## BR-171 插件优先：插件返回非 null（含空列表）即不查库

- **类型**: 业务规则
- **同义词**: 插件优先, 数据源优先级, 用量来源, plugin precedence, usage source priority, fallback to db
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/BaseUserApi.java:55-94`

**规则**：查询用量时按注册顺序遍历所有 `UsagePluginApi`：
- 若没有任何插件注册（`getAllServices().isEmpty()`）→ 返回 `null` → 用量模块回退查自身 `rolled_up_usage` 表。
- 对每个插件调用 `getUsageForSubscription` / `getUsageForAccount`；**第一个返回非 null 的插件结果胜出**，直接返回（可能是空列表），**不再查库**。
- 所有注册插件都返回 `null` → 回退查库。

**含义**：插件一旦接管某租户/账户的用量数据，本地的 `rolled_up_usage` 表对该查询就完全不可见；插件返回空列表也代表「确实没有用量」，而非触发回退。

## BR-172 插件越界数据仅告警，不拒绝

- **类型**: 业务规则
- **同义词**: 插件数据校验, 越界告警, plugin out of range, usage warning, date range warning
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/BaseUserApi.java:77-90`

**规则**：对插件返回的每条 `RawUsageRecord`，若其 `date` 落在请求区间之外（`date < startDate || date >= endDate`），仅记录 `warn` 日志（"Usage plugin returned usage data with date {}, not in the specified range"），**仍然原样返回给调用方**，不做过滤或拒绝。

**含义**：插件数据可能包含区间外的点，过滤责任在下游（开票侧按自己的区间切分）。这是 `>= endDate` 的右开判断，与 BR-004 的半开区间一致。

## BR-173 单位类型来源：CAPACITY→limit，CONSUMABLE→tier block

- **类型**: 业务规则
- **同义词**: 单位类型映射, 目录单位, capacity limit unit, consumable tier unit, unit type catalog link
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:34-87`

**规则**（目录→开票的映射，用量 `unitType` 必须与之对齐）：
- CONSUMABLE IN_ARREAR：单位类型集合 = 各 tier 的 `TieredBlock.getUnit().getName()`；取价时对每个 tier 找匹配 `unitType` 的 block，且要求每个 tier 都有该 unit 的定义（否则 `Preconditions.checkState` 失败）。
- CAPACITY IN_ARREAR：单位类型集合 = 各 tier 的 `Limit.getUnit().getName()`。

**对用量模块的含义**：写入的 `unitType` 是字符串，若与目录声明的 unit 名不匹配，则开票无法定价；此一致性不由用量模块强制（见 BR-015）。

## BR-174 用量存储层不区分 CONSUMABLE / CAPACITY

- **类型**: 业务规则
- **同义词**: 存储不区分类型, 用量类型无关存储, usage type agnostic storage, storage semantics
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/dao/RolledUpUsageModelDao.java:30-36`, `usage/src/main/resources/org/killbill/billing/usage/ddl.sql:4-16`

**规则**：`rolled_up_usage` 表与 `RolledUpUsageModelDao` **没有**任何字段表示 usageType/billingMode。无论消费型还是容量型，用量记录都写同样的列（`subscription_id`/`unit_type`/`record_date`/`amount`/`tracking_id`）。

**含义**：CAPACITY vs CONSUMABLE 的差异完全由（a）目录定义与（b）开票聚合决定，用量模块只提供中立的事实数据。回答「某一用量是消费型还是容量型」时，不能从用量表判断，必须查目录中的 usage 定义。

## BR-175 用量提交的必填校验

- **类型**: 业务规则
- **同义词**: 用量校验, 必填字段, usage validation, required fields, mandatory usage fields
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/UsageResource.java:119-132`, `jaxrs/src/main/java/org/killbill/billing/jaxrs/json/SubscriptionUsageRecordJson.java:36-119`

**规则**（提交用量时，API 层校验）：
- `subscriptionId` 必填。
- `unitUsageRecords` 必填且非空（`!isEmpty()`）。
- 每个 `UnitUsageRecordJson.unitType` 必填非空。
- 每个单位类型的 `usageRecords` 至少 1 条。
- 每条 `UsageRecordJson` 的 `amount` 与 `recordDate` 必填非 null。

**失败行为**：校验失败返回 400 / 抛出参数异常。用量模块 `recordRolledUpUsage` 自身不做这些断言，依赖 API 层先行校验。

## BR-176 退订后不得记录晚于生效结束日的用量

- **类型**: 业务规则
- **同义词**: 退订用量校验, 生效结束日, cancel usage, effective end date, usage after cancellation
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/UsageResource.java:134-141`, `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/UsageResource.java:150-158`

**规则**：记录用量前，先按 `subscriptionId` 取订阅（entitlement）；若其 `getEffectiveEndDate()` 非 null（即已退订/已结束），则取本次提交中所有用量记录的**最大 `recordDate`**；若 `effectiveEndDate < highestRecordDate` → 返回 400 Bad Request。

**含义**：不允许为已结束订阅记录结束日之后的用量。注意这是 API 层校验，不写在 `DefaultUsageUserApi` 内。

## BR-177 用量相关系统属性（配置项清单）

- **类型**: 业务规则
- **同义词**: 用量配置, 系统属性, usage config, system properties, 用量参数
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:84-101`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:124-131`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:205-213`

**影响用量存储/检索的系统属性**（定义在开票配置 `InvoiceConfig`，用量模块/开票侧读取）：

| 属性 | 默认 | 作用 |
|---|---|---|
| `org.killbill.invoice.readMaxRawUsagePreviousPeriod` | — | 拉取原始用量时向前回溯的最大计费周期数（用量优化），决定 `getRawUsageForAccount` 的 startDate |
| `org.killbill.invoice.disable.usage.zero.amount` | — | 是否不写入 $0 的用量金额 |
| `org.killbill.invoice.usage.missing.lenient` | — | 发现缺失的历史用量记录时是否放宽（不失败开票） |
| `org.killbill.invoice.usage.tz.mode` | — | 夏令时下包含用量点的行为 |
| `org.killbill.invoice.parkAccountsWithUnknownUsage` | `false` | 记录了目录未定义用量时是否 park 账户 |

**说明**：`usage` 模块自身**没有**配置文件或 `@Config` 属性（其 `resources` 下仅有 `ddl.sql`、SQL 模板与 migration）。用量存储/检索可调行为均由开票侧的上述配置驱动。属性读取点在 `invoice/.../usage/RawUsageOptimizer.java:78-79`、`85-98`、`116-119`、`122-127`。
