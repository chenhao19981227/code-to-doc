# 业务规则（BR）

> 来源模块：invoice, overdue。检索单元 = 每个 `## ` 二级标题块。

## BR-001 发票状态由自动开票草稿标记决定

- **类型**: 业务规则
- **同义词**: 草稿发票, 自动开票草稿, 发票状态, auto invoice draft, draft invoice
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:90-94`

**规则**：生成时若计费事件集 `isAccountAutoInvoiceDraft()` 为真，新发票状态为 `DRAFT`，否则 `COMMITTED`。

## BR-002 目标日期的边界与对齐

- **类型**: 业务规则
- **同义词**: 未来开票上限, 目标日期对齐, target date limit, target date adjustment
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:120-154`

**规则**：目标日期与今日相隔月数 > `getNumberOfMonthsInFuture()` 时抛 `INVOICE_TARGET_DATE_TOO_FAR_IN_THE_FUTURE`；随后将目标日期抬升到已有发票中含 RECURRING/USAGE 项的最大目标日期。

## BR-003 周期费用金额与跳过条件

- **类型**: 业务规则
- **同义词**: 周期费用计算, 续订金额, recurring amount, 单价乘数量, NO_BILLING_PERIOD
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:238-278`

**公式**：`rateXQuantity = recurringPrice × quantity`；`amount = numberOfCycles × rateXQuantity`（`KillBillMoney.of` 按币种取整）。

**例外**：`BillingPeriod == NO_BILLING_PERIOD` 或 `recurringPrice == null` 时不生成周期项。

## BR-004 首期与末段按比例计费

- **类型**: 业务规则
- **同义词**: 首期按比例, 尾段按比例, leading proration, trailing proration, 按天折算
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:367-423`, `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceDateUtils.java:53-99`

**规则**：首个计费周期日晚于开始日时，对 `[startDate, firstBillingCycleDate)` 按比例收费；有效结束日晚于最后计费周期日时，对 `[lastBillingCycleDate, effectiveEndDate)` 按比例收费；比例 > 0 才生成项。

**分母**：`fixedDaysInMonth != 0` 时以固定天数作分母并跨月扣除 `(当月最大日 − 固定天数)`；`daysBetween <= 0` 时比例为 0。

## BR-005 固定费用项生成与去重

- **类型**: 业务规则
- **同义词**: 固定费用, 一次性费用, 试用期费用, fixed price item, fixed item dedupe
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:194-221`, `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:427-472`

**规则**：金额 = `fixedPrice × quantity`；无周期费用且阶段类型非 `EVERGREEN` 时结束日取下一 PHASE 事件日，否则按阶段时长推算。若上一条固定项与当前事件“同订阅且同一生效日”，不重复加入。

## BR-006 发票生成安全边界

- **类型**: 业务规则
- **同义词**: 安全边界, 重复项防护, safety bound, max daily items
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:476-548`

**规则**：
- 同一 subscriptionId + startDate 出现 > 1 个 FIXED 项 → 抛异常；
- 同一 subscriptionId + 相同 [startDate,endDate] 出现 > 1 个 RECURRING 项 → 抛异常；
- 每日每订阅项数超过 `getMaxDailyNumberOfItemsSafetyBound()`（`-1` 表示关闭）→ 抛异常。

## BR-007 全额修复项在后续计算中剔除

- **类型**: 业务规则
- **同义词**: 修复闭包, 全额冲销, fully repaired, repair closure
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoicePruner.java:88-116`, `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoicePruner.java:156-232`

**规则**：当某 RECURRING 项的修复额等于原额时，该原项及共同关联修复项整体视为“已修复”，后续不参与树合并（避免区间重叠）。

**例外**：目标原项金额为 $0 时直接忽略。

## BR-008 发票余额公式与计费金额构成

- **类型**: 业务规则
- **同义词**: 发票余额, 未付金额, raw balance, charged amount
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:96-110`, `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:157-190`

**公式**：`balance = (charged + credited + adjustedForAccountCredit) − (amountPaid + amountRefunded)`。

**charged** = Σ(charge 类项) + Σ(发票级 CREDIT_ADJ，且非独立信用发票) + Σ(ITEM_ADJ/REPAIR_ADJ) + Σ(PARENT_SUMMARY)。`originalChargedAmount` 仅累计创建日等于发票创建日的 charge 项。

## BR-009 已付与已退款金额口径

- **类型**: 业务规则
- **同义词**: 已付金额, 已退款金额, 拒付, amount paid, refunded amount, chargeback
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:207-242`

**规则**：仅 `status == SUCCESS` 的支付计入；`type == ATTEMPT` 计入已付，`type ∈ {REFUND, CHARGED_BACK}` 计入已退款。

## BR-010 发票余额为 0 与信用发票判定

- **类型**: 业务规则
- **同义词**: 零余额, 信用发票, 独立信用单, zero balance, credit invoice
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoice.java:274-288`, `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:39-70`

**规则**：发票被核销、是迁移发票、状态为 DRAFT/VOID、或父发票余额为 0 时 `getBalance()` 返回 0。

**信用发票**：仅当发票恰含 2 项、一项为 CREDIT_ADJ 且另一项为 CBA_ADJ（同发票、金额互为相反数）时成立；否则 CREDIT_ADJ 作为发票级信用调整参与 charged。

## BR-011 负余额发票生成账户信用

- **类型**: 业务规则
- **同义词**: 生成信用, 负余额转信用, credit generation, CBA generation
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:67-76`, `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:243-251`

**规则**：发票余额 < 0 时生成 CBA_ADJ 项，金额为余额的相反数（正信用）。

## BR-012 正余额已提交发票消耗账户信用

- **类型**: 业务规则
- **同义词**: 使用信用, 抵扣欠款, use credit, consume CBA
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:77-92`

**规则**：仅当余额 > 0 且状态 `COMMITTED`、无 `PENDING` 的 ATTEMPT 支付、且未核销时才可抵扣；抵扣额 = min(accountCBA, balance)；accountCBA ≤ 0 不处理。

## BR-013 账户信用按发票日期顺序分配 & 未付发票定义

- **类型**: 业务规则
- **同义词**: 信用分配, 抵扣顺序, 未付发票, CBA distribution, unpaid invoice
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:186-218`, `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:189-203`

**规则**：将账户 CBA 依次分配到按 `invoiceDate` 升序的未付发票，直到用尽；每分配一次更新剩余 CBA。

**未付发票**：状态 `COMMITTED`、原始余额 ≥ 1、未核销；父发票存在时以父发票余额判断。

## BR-014 行项目调账与退款校验

- **类型**: 业务规则
- **同义词**: 调账上限, 退款上限, refund validation, item adjustment limit
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:112-174`

**规则**：
- 可调账上限 = 原项金额 − 已调整/已修复金额；超出抛 `INVOICE_ITEM_ADJUSTMENT_AMOUNT_INVALID`；请求为 null 时按上限全额调账；
- 退款额 > 支付额抛 `REFUND_AMOUNT_TOO_HIGH`；未指定则默认支付全额；
- 若指定调账行项目，其金额之和必须 ≥ 退款额，否则抛 `REFUND_AMOUNT_DONT_MATCH_ITEMS_TO_ADJUST`。

## BR-015 作废发票与状态变更限制

- **类型**: 业务规则
- **同义词**: 作废发票, 撤销发票, void invoice, invalid status
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:753-788`, `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:815-825`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:1387-1391`

**规则**：已提交发票作废前，已修复 → `CAN_NOT_VOID_INVOICE_THAT_IS_REPAIRED`；其生成的正 CBA 已被使用 → `CAN_NOT_VOID_INVOICE_THAT_GENERATED_USED_CREDIT`；已支付(净额≠0) → `CAN_NOT_VOID_INVOICE_THAT_IS_PAID`。状态变更为相同状态或源状态已 VOID → `INVOICE_INVALID_STATUS`。

## BR-016 贷项/外部费用金额与币种校验

- **类型**: 业务规则
- **同义词**: 贷项校验, 外部费用校验, credit validation, external charge validation
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:560-572`, `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:633-647`

**规则**：外部费用/贷项金额为 null 或 < 0 时分别抛 `EXTERNAL_CHARGE_AMOUNT_INVALID`/`CREDIT_AMOUNT_INVALID`；币种与账户币种不一致抛 `CURRENCY_INVALID`；贷项金额入库取负。

## BR-017 账户余额计算排除与扣减规则

- **类型**: 业务规则
- **同义词**: 账户余额计算, account balance rule
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:734-758`

**规则**：跳过 DRAFT/VOID 发票；核销发票或“父发票余额为 0”的子发票余额按 0 计；最终 `accountBalance − Σ CBA`。

## BR-018 DRAFT→COMMITTED 迁移与发票编号

- **类型**: 业务规则
- **同义词**: 草稿转正式, 提交草稿, 发票编号, draft to committed, invoice number
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:513-535`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:507-512`, `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:786-802`

**规则**：落盘发票已存在时仅允许 `COMMITTED` 覆盖 `DRAFT`，目标日期只允许向后更新。发票编号从插件属性 `INVOICE_SEQUENCE_NUMBER` 读入并作为同名字段持久化，读取时回填。

## BR-019 AUTO_INVOICING_OFF 对开票的影响

- **类型**: 业务规则
- **同义词**: 关闭自动开票, 暂停开票, AUTO_INVOICING_OFF, 标签移除重跑
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:108-110`, `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:387-389`, `invoice/src/main/java/org/killbill/billing/invoice/InvoiceTagHandler.java:72-81`

**规则**：订阅级 `AUTO_INVOICING_OFF` 使该订阅的项被排除；账户级 `isAccountAutoInvoiceOff()` 在非 API 路径直接返回空；账户上的 `AUTO_INVOICING_OFF` 标签被删除时触发重新生成未付发票。

## BR-020 用量后付金额 = 应计 − 已计（及负额处理）

- **类型**: 业务规则
- **同义词**: 用量差额, 增量计费, 用量负额, usage delta, negative usage
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:88-120`

**规则**：`TierBlockPolicy == ALL_TIERS` 且历史项均含明细时 `amountToBill = toBeBilledUsage`，否则 `= toBeBilledUsage − billedUsage`；仅当区间未计过费或差额 > 0 时生成项。差额 < 0 时，试算或 `isUsageMissingLenient` 为真则跳过，否则抛 `UNEXPECTED_ERROR`。

## BR-021 用量分档与向上取整

- **类型**: 业务规则
- **同义词**: 分档计费, 阶梯计费, all tiers, top tier, 向上取整, tier block
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:219-299`

**规则**：块数 = `ceil(remainingUnits / blockSize)`。
- `ALL_TIERS`：逐档消耗，超过档位 max 则消耗 max 块并进入下一档；第一档即使为 0 也生成条目（支持 $0 用量项）；已有历史用量按档位扣除。
- `TOP_TIER`：定位用量所在最高档，全部用量按该档单价与块大小计费。

## BR-022 用量明细模式逐档出账 & 仅后付用量

- **类型**: 业务规则
- **同义词**: 用量明细, 逐档出账, 仅后付用量, usage detail mode, in arrear only
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:103-118`, `invoice/src/main/java/org/killbill/billing/invoice/generator/UsageInvoiceItemGenerator.java:146-155`, `invoice/src/main/java/org/killbill/billing/invoice/generator/UsageInvoiceItemGenerator.java:262-274`

**规则**：`UsageDetailMode.DETAIL` 时每个 tier 明细生成一条 `UsageInvoiceItem`（含 quantity、tier rate、itemDetails JSON），否则整个聚合一条。仅当订阅存在 `BillingMode.IN_ARREAR` 用量时才计算；已有用量项只保留 catalog 中定义为 IN_ARREAR 的项。

## BR-023 子发票忽略规则与子发票金额

- **类型**: 业务规则
- **同义词**: 子发票忽略, 子发票金额, ignore child invoice, child invoice amount
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1407-1425`, `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:112-131`

**规则**：子发票金额为负时忽略（作为信用留待下张）；> 0 纳入；= 0 时仅当含 FIXED 或 RECURRING 项才纳入。

**子发票金额**：无 charge 类项时返回贷项金额的相反数（用于从父项中扣减），否则返回 charged + credited + adjustedForAccountCredit。

## BR-024 父发票汇总项更新与调账传播

- **类型**: 业务规则
- **同义词**: 父发票汇总, 汇总项更新, parent summary, adjustment propagation
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1365-1404`, `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1443-1500`

**规则**：父草稿发票已有该子账户 PARENT_SUMMARY 项时，累加子发票金额并更新该项，否则新增项。子发票产生 ITEM_ADJ 时，父发票已 COMMITTED 则新增 ITEM_ADJ 关联父汇总项，否则更新父汇总项金额；父发票余额为 0 时忽略调账。

## BR-025 用量零额项可被禁用

- **类型**: 业务规则
- **同义词**: 零额用量项, 去除零额, disable zero usage
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:110-114`

**规则**：当 `isUsageZeroAmountDisabled` 为真时移除 $0 用量项（即使发票因此为空，仍可能需要设置 CTD）。

## BR-026 逾期条件之间为逻辑与

- **类型**: 业务规则
- **同义词**: 条件与, 多条件组合, condition AND, all conditions
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:69-84`

**规则**：`evaluate` 对每个非空条件做与运算：仅当所有已配置条件同时满足才返回 true；未配置的条件不参与判定。

## BR-027 欠费张数/总额阈值

- **类型**: 业务规则
- **同义词**: 欠费张数阈值, 欠费金额阈值, unpaid invoices threshold, balance threshold
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:76-80`

**规则**：`numberOfUnpaidInvoicesEqualsOrExceeds` ≤ 实际欠费张数；`totalUnpaidInvoiceBalanceEqualsOrExceeds` ≤ 实际欠费总额，两者均满足才通过（各条件在 BR-001 的与逻辑中）。

## BR-028 最早欠费时长与失败支付响应条件

- **类型**: 业务规则
- **同义词**: 欠费时长, 逾期天数, 支付失败响应, days overdue, last failed payment
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:70-94`

**规则**：`unpaidInvoiceTriggerDate = 最早欠费发票日期 + timeSinceEarliestUnpaidInvoiceEqualsOrExceeds`（无日期则视为无欠费，条件不成立）；当该日期不晚于当前日期时满足。`responseForLastFailedPaymentIn` 要求实际 `PaymentResponse` 命中集合之一。

**例外 / 🟡**：`BillingStateCalculator` 目前将 `responseForLastFailedPayment` **硬编码**为 `INSUFFICIENT_FUNDS`（源码注释 `//TODO MDW`），见 BR-014 溯源；因此该条件的真实取值需人工确认。

## BR-029 控制标签包含/排除条件

- **类型**: 业务规则
- **同义词**: 标签包含, 标签排除, control tag inclusion, control tag exclusion
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:81-112`

**规则**：配置 `controlTagInclusion` 时要求账户标签含该控制标签；配置 `controlTagExclusion` 时要求账户标签不含该控制标签。

## BR-030 逾期状态选择与清账回退

- **类型**: 业务规则
- **同义词**: 状态选择, 首个匹配, 清账回退, state selection, clear fallback
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:41-67`

**规则**：按配置顺序遍历状态，返回**第一个**条件成立的状态；若无任何条件成立则返回清账状态。`findState` 支持按名字查清账状态，找不到抛 `CAT_NO_SUCH_OVERDUE_STATE`。

## BR-031 重新评估间隔规则

- **类型**: 业务规则
- **同义词**: 重评间隔规则, 无间隔, reevaluation interval rule
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:51-57`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:119-125`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`

**规则**：`initialReevaluationInterval` 为 null、UNLIMITED 或 0 时返回 null；状态的 `autoReevaluationInterval` 若为 UNLIMITED/0 抛 `OVERDUE_NO_REEVALUATION_INTERVAL`，由 applicator 捕获并视为“无间隔则不再排下一次检查”。

## BR-032 OVERDUE_ENFORCEMENT_OFF 关闭逾期执行

- **类型**: 业务规则
- **同义词**: 关闭逾期执行, 逾期豁免, enforcement off
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:109-113`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:334-349`

**规则**：账户带 `OVERDUE_ENFORCEMENT_OFF` 标签时，`refreshWithLock` 直接返回，不做任何状态计算与应用。

## BR-033 逾期状态到封禁状态的映射

- **类型**: 业务规则
- **同义词**: 封禁映射, 封禁变更, 禁用权益, blocking mapping
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:221-273`

**规则**：写入封禁状态时：`blockChanges = isBlockChanges() || isDisableEntitlementAndChangesBlocked()`；`blockEntitlement = isDisableEntitlementAndChangesBlocked()`；`blockBilling = isDisableEntitlementAndChangesBlocked()`。

**幂等**：若上一状态名与下一状态名相同，applicator 记为 no-op 直接返回。

## BR-034 封禁计费时自动关闭开票

- **类型**: 业务规则
- **同义词**: 封禁计费关开票, 避免多出信用, AUTO_INVOICING_OFF toggle
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:176-183`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:237-261`

**规则**：当发生“从可计费 → 封禁计费”的转换时，给账户打 `AUTO_INVOICING_OFF`；发生“从封禁计费 → 可计费”的转换时移除该标签（避免产生多余信用）。

## BR-035 逾期触发订阅取消

- **类型**: 业务规则
- **同义词**: 逾期取消订阅, 强制退订, cancellation policy
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:285-329`

**规则**：`subscriptionCancellationPolicy == NONE` 时不取消；`END_OF_TERM`/`IMMEDIATE` 分别映射为 `BillingActionPolicy.END_OF_TERM`/`IMMEDIATE`，取消该账户所有非 ADD_ON 权益（ADD_ON 由 entitlement 层随基础订阅一起取消）。

## BR-036 支付委派给父账户时以父账户计费状态判定

- **类型**: 业务规则
- **同义词**: 父子逾期, 委派支付, parent payment delegation
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:151-159`

**规则**：若账户 `getParentAccountId() != null` 且 `isPaymentDelegatedToParent()`，则使用**父账户**上下文计算计费状态。

## BR-037 欠费发票排序与最早发票

- **类型**: 业务规则
- **同义词**: 欠费排序, 最早欠费发票, unpaid invoices ordering, earliest unpaid
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:47-54`, `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:87-108`

**规则**：按 `invoiceDate` 升序排序（同日期用 hashCode 稳定打破平局）；最早发票 = 排序集合的第一项；欠费总额 = 各欠费发票 `getBalance()` 之和；欠费发票从 `invoiceApi.getUnpaidInvoicesByAccountId` 获取。

## BR-038 触发逾期重算的事件与通知优化

- **类型**: 业务规则
- **同义词**: 触发重算, 事件驱动, notification optimization
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-157`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:207-225`

**规则**：监听器订阅并触发 REFRESH 的事件：`InvoicePaymentInfo`、`InvoicePaymentError`、`InvoiceAdjustment`、`InvoiceCreation`、以及账户级 `OVERDUE_ENFORCEMENT_OFF`/发票级 `WRITTEN_OFF` 标签变更；`OVERDUE_ENFORCEMENT_OFF` 创建触发 CLEAR。若逾期配置缺失或状态集为空或无任何条件，则不插入通知（优化）。

## BR-039 计费状态快照的构造与限制

- **类型**: 业务规则
- **同义词**: 计费状态构造, 失败响应硬编码, billing state snapshot
- **模块**: overdue
- **置信度**: 🟡 inferred
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:67-84`

**规则（推断）**：`BillingState` 由欠费发票集合 + 账户标签构造。源码将 `responseForLastFailedPayment` 硬编码为 `PaymentResponse.INSUFFICIENT_FUNDS`（标注 `//TODO MDW`），说明“以真实支付失败响应作为条件”的行为在本版本**未真正实现**。此卡据此标记为 🟡，需人工确认。
