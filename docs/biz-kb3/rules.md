# 业务规则（Rules）

> Kill Bill 业务知识库 v3（合并 kb2 既有卡 + kb3 补充卡）；共 319 张卡。

---

## BR-001 发票未来生成最大月数

- **类型**: 业务规则
- **同义词**: 发票生成未来月数, 最多提前几个月开票, 目标日期上限, max months in future, maxNumberOfMonthsInFuture, maxNumberOfMonthsInFuture
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:63-71`

**规则**：生成（或干跑 dry-run）发票时，最多只考虑未来 36 个月内的目标日期（targetDate）。配置项 `org.killbill.invoice.maxNumberOfMonthsInFuture`，默认值 `36`。

**用途**：限制一次性提前生成过多期发票，避免未来账期被过度预开。

## BR-002 发票防重复计费安全检查

- **类型**: 业务规则
- **同义词**: 防重复计费, 计费安全检查, 幂等保护, sanity check, sanitySafetyBoundEnabled, double billing
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:73-81`

**规则**：系统默认开启内部安全检查（`org.killbill.invoice.sanitySafetyBoundEnabled` = `true`），用于防止错误计费与重复计费（mis- and double-billing）。关闭后不推荐用于生产。

## BR-003 零金额用量项是否写出

- **类型**: 业务规则
- **同义词**: 零金额用量项, 0元用量, $0 usage, zero amount, disable.usage.zero.amount, isUsageZeroAmountDisabled
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:84-92`

**规则**：配置项 `org.killbill.invoice.disable.usage.zero.amount` 默认 `false`，即**默认会写出金额为 $0 的用量项**。设为 `true` 时禁用写入 $0 用量项（不生成零金额用量行）。

## BR-004 缺失历史用量记录时的处理

- **类型**: 业务规则
- **同义词**: 缺失用量记录, 用量数据缺失, missing usage, usage.missing.lenient, 用量宽容模式
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:94-102`

**规则**：配置项 `org.killbill.invoice.usage.missing.lenient` 默认 `false`（不宽容）。默认情况下，若发现过去存在缺失的用量记录，发票生成会**失败**；设为 `true` 时改为宽容处理，不因缺失用量记录而使发票失败。

## BR-005 每日每订阅最大发票项数

- **类型**: 业务规则
- **同义词**: 每日发票项上限, 每天最多开多少项, maxDailyNumberOfItemsSafetyBound, daily items safety bound
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:104-112`

**规则**：对单个订阅（subscription id）每日生成的发票项数量上限为 `15`。配置项 `org.killbill.invoice.maxDailyNumberOfItemsSafetyBound`，默认值 `15`，作为安全边界防止异常爆炸式开票。

## BR-006 干跑发票通知提前时间

- **类型**: 业务规则
- **同义词**: 干跑通知, 预开票通知, dry run notification, dryRunNotificationSchedule, 提前通知时间
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:114-122`

**规则**：DryRun（干跑）发票通知在目标日期（targetDate）**之前**发送。配置项 `org.killbill.invoice.dryRunNotificationSchedule` 默认 `0s`；当设为 `0s` 时该通知被忽略（不发送）。

## BR-007 原始用量回看账期数（usage lookback）

- **类型**: 业务规则
- **同义词**: 用量回看, 回看账期, usage lookback, readMaxRawUsagePreviousPeriod, 历史用量读取期数, 用量优化
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:124-132`

**规则**：用量优化（usage optimization）时，系统最多读取**过去 2 个账期**的原始用量（raw usage）数据。配置项 `org.killbill.invoice.readMaxRawUsagePreviousPeriod`，默认值 `2`。

**用途**：限制每期开票时回查历史原始用量的范围，用于处理迟到/跨期的用量点。

## BR-008 全局锁获取最大重试次数

- **类型**: 业务规则
- **同义词**: 全局锁重试, global lock retries, globalLock.retries, 锁重试次数
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:134-137`

**规则**：系统获取全局锁最多重试 `50` 次，每次等待 100ms。配置项 `org.killbill.invoice.globalLock.retries`，默认值 `50`。

## BR-009 默认发票插件

- **类型**: 业务规则
- **同义词**: 发票插件, invoice plugin, 默认插件, org.killbill.invoice.plugin
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:139-147`

**规则**：配置项 `org.killbill.invoice.plugin` 默认为空字符串 `""`，即默认不加载任何发票插件。可配置一个（逗号分隔的）发票插件名列表，插件可在发票生成过程中注入/调整发票项。

## BR-010 发票创建邮件通知开关

- **类型**: 业务规则
- **同义词**: 发票邮件通知, invoice email notification, emailNotificationsEnabled, 开票发邮件
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:149-152`

**规则**：配置项 `org.killbill.invoice.emailNotificationsEnabled` 默认 `false`。开启后，对已配置的账户在发票创建时发送邮件通知。

## BR-011 发票系统总开关

- **类型**: 业务规则
- **同义词**: 发票系统开关, invoicing enabled, invoice.enabled, 关闭开票
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:154-157`

**规则**：配置项 `org.killbill.invoice.enabled` 默认 `true`，即发票系统默认启用。设为 `false` 可整体关闭开票系统。

## BR-012 父发票自动提交时间

- **类型**: 业务规则
- **同义词**: 父发票提交, 父账户发票, parent invoice commit, parentAutoCommitUtcTime, HA发票提交时间
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:159-167`

**规则**：父账户（parent account）发票每天在指定 UTC 时间自动提交（commit）。配置项 `org.killbill.invoice.parent.commit.local.utc.time` 默认 `23:59:59.999`。

## BR-013 发票项结果报告模式

- **类型**: 业务规则
- **同义词**: 发票项结果模式, 聚合模式, 明细模式, aggregate vs detail, item.result.behavior.mode, UsageDetailMode
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:53-56`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:174-182`

**规则**：发票项结果报告方式由 `org.killbill.invoice.item.result.behavior.mode` 控制，默认 `AGGREGATE`（聚合）；可选 `DETAIL`（明细）。对应枚举 `UsageDetailMode { AGGREGATE, DETAIL }`。

## BR-014 用量时区偏移模式

- **类型**: 业务规则
- **同义词**: 用量时区, 夏令时处理, usage timezone, usage.tz.mode, AccountTzOffset, 日光节约
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:39-51`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:185-193`

**规则**：控制用量点（usage points）在夏令时（DST）下的归属，配置项 `org.killbill.invoice.usage.tz.mode`，默认 `FIXED`。
- `FIXED`：使用账户创建时一次性计算的固定时区偏移（与 RECURRING 发票项行为一致）。
- `VARIABLE`：按当前年内所处时间重新计算偏移，使相同 TZ/订阅/用量点的相似账户结果一致（夏/冬季开始时间不同也不受影响）。

## BR-015 in-arrear 计划计费模式

- **类型**: 业务规则
- **同义词**: 后付费模式, in arrear mode, inArrear.mode, GREEDY, 后计费策略
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:58-61`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:195-203`

**规则**：配置项 `org.killbill.invoice.inArrear.mode` 默认 `DEFAULT`，决定系统对 in-arrear（后付费）计划的处理行为；可选 `GREEDY`。对应枚举 `InArrearMode { DEFAULT, GREEDY }`。

## BR-016 不可恢复异常时挂起账户

- **类型**: 业务规则
- **同义词**: 异常挂起账户, park on exceptions, parkAccountsOnAllExceptions, 发票处理失败挂起
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:215-223`

**规则**：配置项 `org.killbill.invoice.parkAccountsOnAllExceptions` 默认 `true`。当发票处理发生不可恢复失败（锁失败、订阅者异常、billing event 获取失败）时，默认将账户挂起。

## BR-017 发票生成最大回看时间

- **类型**: 业务规则
- **同义词**: 发票回看限制, 最大回看时间, maxInvoiceLimit, 开票时间下限, 追溯多久
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:37`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:225-233`

**规则**：发票生成向前回看（look back）的时间上限由 `org.killbill.invoice.maxInvoiceLimit` 控制，默认 `DEFAULT_NULL_PERIOD` = `P200Y`（200 年，实际等于不限）。用于限定发票生成时追溯历史 billing events 的最远时间。

## BR-018 固定天数免分比

- **类型**: 业务规则
- **同义词**: 免分比, 分比天数, proration fixed days, proration.fixed.days, 避免按比例分摊
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:235-243`

**规则**：配置项 `org.killbill.invoice.proration.fixed.days` 默认 `0`。设置一个月内的固定天数以避免分比（proration）；`0` 表示不启用该固定天数行为。

## BR-019 发票余额计算（balance）

- **类型**: 业务规则
- **同义词**: 发票余额, 欠款, 应收, invoice balance, getBalance, outstanding amount, 未付金额, 余额怎么算
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:96-110`

**规则**：发票原始余额 `computeRawInvoiceBalance` = **计费金额合计 − 已付金额合计（含退款）**：
- `amountPaid = computeInvoiceAmountPaid + computeInvoiceAmountRefunded`
- `chargedAmount = computeInvoiceAmountCharged + computeInvoiceAmountCredited + computeInvoiceAmountAdjustedForAccountCredit`
- `invoiceBalance = chargedAmount + (−amountPaid)`

## BR-020 发票余额为零的情形

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
否则按 BR-019 的公式计算。

## BR-021 发票已付金额（paid amount）

- **类型**: 业务规则
- **同义词**: 已付金额, 已支付, paid amount, amountPaid, 付款统计
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:207-223`

**规则**：`computeInvoiceAmountPaid` 只累计**支付状态为 SUCCESS 且类型为 ATTEMPT** 的发票支付金额。其他支付状态或类型的记录不计入已付金额。

## BR-022 发票已退款金额（refunded amount）

- **类型**: 业务规则
- **同义词**: 已退款金额, 退款统计, refunded amount, 拒付金额, charged back
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:225-242`

**规则**：`computeInvoiceAmountRefunded` 只累计**支付状态为 SUCCESS 且类型为 REFUND 或 CHARGED_BACK** 的金额。非 SUCCESS 的记录跳过。

## BR-023 发票计费金额组成（charged amount）

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

## BR-024 子发票金额（父账户汇总）

- **类型**: 业务规则
- **同义词**: 子发票金额, 父账户汇总, child invoice amount, parent summary, HA子账户金额
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:112-131`

**规则**：`computeChildInvoiceAmount` 计算应在父发票上汇总的子账户金额：
- 若子发票**无收费项**，返回其信用金额（credited）的负值（仅把信用额从父项金额中扣减）；
- 否则返回 `charged + credited + adjustedForAccountCredit` 的合计。

## BR-025 信用发票识别（CREDIT_ADJ + CBA_ADJ）

- **类型**: 业务规则
- **同义词**: 信用发票, 账户信用, credit invoice, CREDIT_ADJ, CBA_ADJ, 信用余额, account credit
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:46-70`

**规则**：当一张发票**恰好只有 2 个发票项**，且其中一项为 `CREDIT_ADJ`、另一项为 `CBA_ADJ` 且两者 `invoiceId` 相同、金额互为相反数时，判定为“信用发票”。信用发票允许其 `CREDIT_ADJ` 金额被计入余额调整。

## BR-026 账户信用（CBA）生成与使用规则

- **类型**: 业务规则
- **同义词**: 账户信用, 信用余额, credit balance adjustment, CBA, CBA_ADJ, 抵扣余额, 信用生成, 信用使用
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:63-97`

**规则**：计算发票的信用余额调整（CBA）时：
1. 若发票**余额 < 0**（负余额）→ 生成一条**正向信用**（CBA 项金额取负值，即给账户增加可用信用）。
2. 若发票**余额 > 0** 且发票状态为 `COMMITTED`、**无 PENDING 支付**、且**未核销** → 使用账户已有信用抵扣该发票（消费额 = min(账户 CBA, 发票余额)），生成负向 CBA 项。
3. 若余额为 0 → 不做任何处理。

## BR-027 账户信用按发票日期分配给未付发票

- **类型**: 业务规则
- **同义词**: 信用分配, 抵扣未付发票, distribute CBA, 信用抵扣顺序, account credit allocation
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:172-218`

**规则**：账户可用信用（CBA）会被分配到所有 **COMMITTED 且未付** 的发票上，分配顺序按 `invoiceDate` **升序**（先旧后新），逐张抵扣直到信用耗尽或发票付清。每张发票的抵扣额 = min(剩余信用, 该发票余额)。

## BR-028 发票目标日期上限校验（未来 36 个月）

- **类型**: 业务规则
- **同义词**: 目标日期过远, target date too far, 未来开票上限, INVOICE_TARGET_DATE_TOO_FAR_IN_THE_FUTURE
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:120-126`

**规则**：生成发票时校验目标日期：若 `targetDate` 与当前 UTC 今天的月差**大于** `org.killbill.invoice.maxNumberOfMonthsInFuture`（默认 36），则抛出 `InvoiceApiException`，错误码 `INVOICE_TARGET_DATE_TOO_FAR_IN_THE_FUTURE`。

## BR-029 发票目标日期自动前推（避免回溯重复开票）

- **类型**: 业务规则
- **同义词**: 目标日期调整, adjust target date, 已有未来发票, 防止重复开票
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/DefaultInvoiceGenerator.java:128-154`

**规则**：生成发票前，若账户已存在**含 RECURRING 或 USAGE 项**、且其 `targetDate` 晚于本次请求的 `targetDate` 的发票，则把本次 `targetDate` 上调为这些发票中最晚的 `targetDate`（防止对已开票区间重复开票）。

## BR-030 作废发票（VOID）的前置校验

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

## BR-031 提交草稿发票（commit）

- **类型**: 业务规则
- **同义词**: 提交发票, 确认发票, commit invoice, 草稿转正式, DRAFT 转 COMMITTED
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:688-708`

**规则**：`commitInvoice` 将发票状态改为 `COMMITTED`，随后更新其计费截止日期（charged-through dates），并通过发票插件链以 `INVOICE_OPERATION=commit` 派发。

## BR-032 外部收费与信用金额校验

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

## BR-033 账户余额与账户信用余额查询

- **类型**: 业务规则
- **同义词**: 账户余额, 账户信用, account balance, account CBA, getAccountBalance, getAccountCBA, 余额查询
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:229-239`

**规则**：`getAccountBalance(accountId)` 与 `getAccountCBA(accountId)` 从数据库聚合；当结果为空（null）时统一返回 `BigDecimal.ZERO`。

## BR-034 子账户信用转给父账户

- **类型**: 业务规则
- **同义词**: 子账户信用转移, 信用转父账户, transferChildCreditToParent, CHILD_ACCOUNT_MISSING_CREDIT, 父子账户信用
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:709-731`

**规则**：`transferChildCreditToParent` 前置条件：
1. 子账户必须**存在父账户**，否则抛 `ACCOUNT_DOES_NOT_HAVE_PARENT_ACCOUNT`；
2. 子账户账户信用（CBA）必须 **> 0**，否则抛 `CHILD_ACCOUNT_MISSING_CREDIT`；
3. 通过后将子账户信用转移给父账户。

## BR-035 发票项调整（ITEM_ADJ）校验

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

## BR-036 发票核销（written off）标记

- **类型**: 业务规则
- **同义词**: 发票核销, 坏账核销, write off, WRITTEN_OFF, tagInvoiceAsWrittenOff, 不再收款
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:313-335`

**规则**：对发票打上 `WRITTEN_OFF` 控制标签即表示核销（`tagInvoiceAsWrittenOff`），移除该标签为取消核销（`tagInvoiceAsNotWrittenOff`）。核销后发票余额恒为 0（见 BR-020），并会向总线发送发票调整事件（用于 overdue 等）。

## BR-037 用量重复计费防护（tracking id + 已开票区间跳过）

- **类型**: 业务规则
- **同义词**: 用量去重, 防止重复计费, usage dedup, tracking id, 已开票跳过, double billing usage
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:290-307`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:333-356`

**规则**：
1. 每条原始用量带 tracking id；只有**不在既有 tracking id 集合**中的用量才会被计费（新增用量）。
2. 若某个用量区间已被既有 `USAGE` 发票项覆盖（同 usage name 且 start/end 落入既有项内），则**跳过**该区间，避免重复计费（尤其阻断/重跑场景）。

## BR-038 目录中未定义的用量单位处理

- **类型**: 业务规则
- **同义词**: 未知用量单位, unknown usage unit, unit type not defined, 挂起账户, park account usage
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:485-505`

**规则**：当上报的用量单位类型（unitType）**未在任何 billing event 的目录中定义**时：
- 若 `org.killbill.invoice.parkAccountsWithUnknownUsage` = `true` → 抛 `InvoiceApiException`（ILLEGAL INVOICING STATE），导致账户被挂起；
- 否则 → 记录告警并**忽略**该单位类型，同时移除其关联的 tracking id。

## BR-039 用量计费区间按 BCD 对齐

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

## BR-040 手动支付账户的发票渲染

- **类型**: 业务规则
- **同义词**: 手动支付, manual pay, MANUAL_PAY, 线下支付, 发票渲染
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:483-493`

**规则**：生成发票 HTML（`getInvoiceAsHTML`）时，若账户带有 `MANUAL_PAY` 控制标签，则以 `manualPay=true` 渲染发票，表示该账户走**手动/线下支付**而非自动扣款。

## BR-041 发票优化时间边界（cutoff / maxInvoiceLimit）

- **类型**: 业务规则
- **同义词**: 发票优化, invoice optimization, cutoff date, maxInvoiceLimit, 历史发票截断, 性能优化
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/optimizer/InvoiceOptimizerExp.java:67-88`

**规则**：当 `org.killbill.invoice.maxInvoiceLimit` 已设置且不等于默认 `P200Y` 时：
- 发票 cutoffDt = 当前 UTC 时间 `−` maxInvoiceLimit；
- billing event 的 cutoff beCutoffDt = cutoffDt `−` maxInvoiceLimit（比发票再多回溯一个周期，用于支持 in-arrear 尾部分摊）；
- 只加载 cutoffDt 之后的既有发票参与本次开票。

## BR-042 建议开票项过滤（optimizer filterProposedItems）

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

## BR-043 用量仅支持后付费（IN_ARREAR）

- **类型**: 业务规则
- **同义词**: 后付费, in arrear, 用量后计费, BillingMode, IN_ARREAR, 用量计费模式
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:36`, `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:57`, `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:70`, `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:77`

**规则**：用量计费的各种取层/取单位方法均以 `Preconditions` 强制要求 `usage.getBillingMode() == BillingMode.IN_ARREAR`（后付费）——用量只在账单周期结束后计费，且 tiers 不能为空。

## BR-044 父发票提交通知去重

- **类型**: 业务规则
- **同义词**: 通知去重, parent invoice notification dedup, 重复通知
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/notification/ParentInvoiceCommitmentPoster.java:58-88`

**规则**：插入父发票提交通知前，检查队列中是否已存在**相同生效日期且相同 invoiceId** 的未来通知；若存在则跳过（不重复记录）。

## BR-045 订阅 EXPIRED 事件不触发开票

- **类型**: 业务规则
- **同义词**: 过期事件, EXPIRED, 订阅到期, 不触发开票, subscription expired
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceListener.java:266-271`

**规则**：当订阅事件类型为 `SubscriptionBaseTransitionType.EXPIRED` 时，`handleSubscriptionTransition` 不把该事件交给发票处理（即订阅过期本身不触发新的开票）。

## BR-046 发票系统关闭时挂起账户

- **类型**: 业务规则
- **同义词**: 发票系统关闭, invoicing off, invoice.enabled=false, 挂起账户, park account
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:289-300`

**规则**：当 `org.killbill.invoice.enabled` = `false`（发票系统关闭）时，来自通知/总线事件的账户处理会**直接挂起该账户**并返回空结果（不生成发票）。

## BR-047 已挂起账户跳过开票

- **类型**: 业务规则
- **同义词**: 挂起账户, parked account, 跳过开票, 账户暂停, isParked
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:311-320`

**规则**：若账户处于挂起（parked）状态且本次调用**不是 API 调用**，则本次发票生成被忽略（返回空）。API 调用（isApiCall=true）仍会尝试开票。

## BR-048 发票生成的账户级全局锁

- **类型**: 业务规则
- **同义词**: 全局锁, account lock, ACCNT_INV_PAY, 发票并发锁, 加锁失败重试
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:322-338`

**规则**：非 dry-run 的发票生成会对账户加全局锁（锁类型 `ACCNT_INV_PAY`），最多重试 `org.killbill.invoice.globalLock.retries`（默认 50）次。
- 加锁失败且为 API 调用 → 抛 `InvoiceApiException`（UNEXPECTED_ERROR，“failed to acquire lock”）；
- 加锁失败且非 API 调用 → 抛 `QueueRetryException`，按 `rescheduleIntervalOnLock` 之后重试。

## BR-049 干跑通知仅余额大于 0 时发送

- **类型**: 业务规则
- **同义词**: 干跑通知, 余额大于0, 发票通知事件, invoice notification, dryRun balance
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:264-280`

**规则**：`processSubscriptionForInvoiceNotification` 干跑生成发票后，**仅当该预览发票余额 > 0** 时才向总线发送 `InvoiceNotificationInternalEvent`（用于“即将开票”提醒）。

## BR-050 哪些子发票可被父发票忽略

- **类型**: 业务规则
- **同义词**: 忽略子发票, shouldIgnoreChildInvoice, 负金额子发票, 零金额子发票
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1407-1425`

**规则**：父发票汇总时对子发票的判断：
- 子发票金额 **< 0**（信用）→ **忽略**（该信用将在下次开票中使用）；
- 子发票金额 **> 0** → 不忽略；
- 子发票金额 **== 0** → 仅当子发票中**没有 FIXED 或 RECURRING 项**时忽略；若含这两类项则不忽略（保留 0 金额汇总）。

## BR-051 父发票的项调整传播

- **类型**: 业务规则
- **同义词**: 父发票调整, parent adjustment, PARENT_SUMMARY 调整, 子发票调整传播
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:1427-1500`

**规则**：对子发票做项调整（ITEM_ADJ）时同步到父发票：
- 若子发票**无父发票** → 抛 `INVOICE_MISSING_PARENT_INVOICE`；
- 若父发票**原始余额为 0**（已结清）→ 忽略调整；
- 取子发票中**最新一条 ITEM_ADJ**；若父发票状态为 `COMMITTED` → 在父发票上新增一条 `ITEM_ADJ`；否则 → 更新对应 `PARENT_SUMMARY` 项的金额。

## BR-052 父发票余额为 0 时子发票的余额算法

- **类型**: 业务规则
- **同义词**: 子发票余额, parent balance zero, 父子余额, HA balance
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:100-124`

**规则**：若子发票**存在父发票且父发票原始余额为 0**，则子发票余额 = `子发票计费金额 − 父发票上归属该子账户的项金额之和`；否则使用常规发票原始余额。

## BR-053 修复项（REPAIR_ADJ）金额上限

- **类型**: 业务规则
- **同义词**: 修复冲销, REPAIR_ADJ, repair, 冲销上限, 修复金额, repair amount
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:182-200`, `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:212-218`

**规则**：当既有发票项在新一轮开票中需要被冲销（REPAIR）时，生成一条**负金额** `RepairAdjInvoiceItem`：
- 修复上限 `maxAmountForRepair = min(按新日期分比后的金额, 该项净额)`；
- 净额 `netAmount = amount − adjustedAmount − currentRepairedAmount`；
- 已完全调整的项（`amount − adjustedAmount == 0`）为 `isFullyAdjusted`。

## BR-054 分比计算（Proration）

- **类型**: 业务规则
- **同义词**: 分比, 按比例计费, proration, 按天计费, 不足整周期, prorate
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:152-168`, `invoice/src/main/java/org/killbill/billing/invoice/tree/Item.java:182-189`

**规则**：分比金额 = `calculateProrationBetweenDates(newStart, newEnd, 总天数, prorationFixedDays) × amount`。
- 总天数默认 = `startDate` 到 `endDate` 的实际天数；当 `org.killbill.invoice.proration.fixed.days > 0` 时用该固定天数作分母；
- 区间被拆分（split）时按 `splitDate` 分为 `[start, split]` 与 `[split, end]` 两段，金额按比例分配。

## BR-055 原始用量优化的起始日期（用量回看）

- **类型**: 业务规则
- **同义词**: 用量回看起点, optimized start date, raw usage optimization, readMaxRawUsagePreviousPeriod, 用量拉取范围
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/RawUsageOptimizer.java:77-137`

**规则**：计算拉取原始用量的优化起始日期：
- 若 `org.killbill.invoice.readMaxRawUsagePreviousPeriod ≥ 0`：对每个已知用量的 billingPeriod，从最近一次 consumable in-arrear 用量项的 `endDate` 回退该配置指定的周期数，取所有账期中的最早值，再与 `firstEventStartDate` 取较晚者作为起点；
- 若配置 < 0：直接返回 `firstEventStartDate`。
- 特殊路径：当 `isUsageZeroAmountDisabled=true` 时改用 `min(今天, targetDate)` 回退 1 个周期来估算（避免漏开旧账期时拉取不足）。

## BR-056 发票配置支持多租户覆盖

- **类型**: 业务规则
- **同义词**: 多租户配置, tenant config override, MultiTenantInvoiceConfig, 租户级配置
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/config/MultiTenantInvoiceConfig.java:46-58`, `invoice/src/main/java/org/killbill/billing/invoice/config/MultiTenantInvoiceConfig.java:311-315`

**规则**：绝大多数 `InvoiceConfig` 配置项支持**按租户覆盖**（`getStringTenantConfig`）：租户若配置了同名项则优先使用，否则回退到静态（全局）配置。枚举型配置的非法值会回退默认值（`UsageDetailMode`→AGGREGATE、`AccountTzOffset`→FIXED、`InArrearMode`→DEFAULT）。注意 `getMaxGlobalLockRetries` 与若干无参方法仅用静态配置，不支持租户覆盖。

## BR-057 迁移发票余额恒为 0

- **类型**: 业务规则
- **同义词**: 迁移发票, migration invoice, isMigrated, 余额为0, 历史数据导入
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceModelDaoHelper.java:33-46`

**规则**：对 `isMigrated()` 为 true 的发票，`getRawBalanceForRegularInvoice` 直接返回 `BigDecimal.ZERO`，不做金额计算。

## BR-058 发票项类型与实现类映射

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

## BR-059 加锁失败时的重试时间表

- **类型**: 业务规则
- **同义词**: 锁重试间隔, rescheduleIntervalOnLock, 重排发票, 锁被占用重试
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/LockAwareConfig.java:30-38`

**规则**：当发票运行因账户锁被占用而无法执行时，按配置项 `org.killbill.rescheduleIntervalOnLock` 的延迟序列重排。默认值 `"30s, 1m, 1m, 3m, 3m, 10m"`（依次 30秒、1分、1分、3分、3分、10分后重试）。

## BR-060 未付发票的判定

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

## BR-061 发票状态变更的约束与副作用

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

## BR-062 完全修复项的剔除（InvoicePruner）

- **类型**: 业务规则
- **同义词**: 完全修复, fully repaired, InvoicePruner, 修复闭合, 避免重复修复
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoicePruner.java:88-99`, `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoicePruner.java:156-232`

**规则**：构建发票项树前，先识别**已被完全修复**的 RECURRING 项——即其 `REPAIR_ADJ` 金额合计（取负）等于原项金额；此类原项连同其修复/调整项一并从树中剔除，避免区间重叠与重复修复。金额为 `$0` 的原项被忽略。

## BR-063 发票项调整金额取负

- **类型**: 业务规则
- **同义词**: 调整取负, ITEM_ADJ amount negate, 调整金额符号
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:230-239`

**规则**：创建 `ITEM_ADJ` 发票项时，金额以**负值**入账（`amountToAdjust.negate()`）。若未指定调整金额，默认取原项**全额**；若未指定币种，默认取原项币种。

## BR-064 发票项调整的归属校验

- **类型**: 业务规则
- **同义词**: 调整校验, INVOICE_ITEM_NOT_FOUND, 项不属于发票, adjustment validation
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:219-228`

**规则**：对发票项做调整时：
- 目标项不存在 → 抛 `INVOICE_ITEM_NOT_FOUND`；
- 目标项不属于指定发票 → 抛 `INVOICE_INVALID_FOR_INVOICE_ITEM_ADJUSTMENT`。

## BR-065 固定费用发票项生成规则

- **类型**: 业务规则
- **同义词**: 固定费生成, fixed price item, 初装费生成, FIXED 生成
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:427-472`

**规则**：在阶段开始时生成固定费发票项：
- 金额 = `fixedPrice × quantity`；
- 若该阶段**无 recurring 费用**且阶段类型**不是 EVERGREEN**，则固定项的 `endDate` 取下一个 `PHASE` 事件的生效日期，或当前阶段时长结束的日期；
- 若固定项 `startDate` 晚于 `targetDate`，则不生成该项。

## BR-066 周期发票项的分比生成规则

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

## BR-067 发票项安全检查边界（safety bounds）

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

## BR-068 下一次开票通知日期计算

- **类型**: 业务规则
- **同义词**: 下次开票日期, next notification date, next billing cycle, 下一账期
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/FixedAndRecurringInvoiceItemGenerator.java:298-332`

**规则**：计算某订阅的下一次开票/通知日期：
- `IN_ADVANCE` 模式：取所有周期项中**最晚的 `endDate`**；
- `IN_ARREAR` 模式：取 `nextBillingCycleDate`。

<!-- module: invoice | cards: 97 | BR:70 TERM:10 ENT:8 WF:7 SM:1 ROLE:1 | confidence: 96 confirmed / 0 inferred / 1 gap | extracted_at: 2026-09-16 -->

## BR-069 可被 ITEM_ADJ 调整的发票项类型白名单

- **类型**: 业务规则
- **同义词**: 可调整项类型, 哪些项能调整, adjustable item types, INVOICE_ITEM_TYPES_ADJUSTABLE, 不可调整项
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:127-132`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:1362-1370`

**规则**：只有以下 **6 种**发票项类型可被 `ITEM_ADJ`（发票项调整）作为目标项：
`EXTERNAL_CHARGE`、`FIXED`、`RECURRING`、`TAX`、`USAGE`、`PARENT_SUMMARY`。

**校验**：写入 `ITEM_ADJ` 时，DAO 会读取 `linkedItemId` 指向的原项；若原项类型不在上述白名单内 → 抛 `INVOICE_ITEM_ADJUSTMENT_ITEM_INVALID`。`ITEM_ADJ` 的 `linkedItemId` 不得为 null。

**含义**：`CBA_ADJ`、`CREDIT_ADJ`、`ITEM_ADJ`、`REPAIR_ADJ` 本身**不能**作为被调整目标（即不能对调整项再调整，也不能对信用项直接做 ITEM_ADJ）。

## BR-070 发票插件可新增/修改的发票项类型白名单

- **类型**: 业务规则
- **同义词**: 插件可注入项, plugin item types, ALLOWED_INVOICE_ITEM_TYPES, 插件限制, 插件新增发票项
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoicePluginDispatcher.java:79-82`, `invoice/src/main/java/org/killbill/billing/invoice/InvoicePluginDispatcher.java:388-394`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:544-554`

**规则**：发票插件通过 `getAdditionalInvoiceItems` 只能**新增**以下 **4 种**类型的发票项：
`EXTERNAL_CHARGE`、`ITEM_ADJ`、`CREDIT_ADJ`、`TAX`。

- 若插件返回的新项类型不在白名单内、且该 id 不是已存在项 → 抛 `INVOICE_ITEM_TYPE_INVALID`（该插件项被丢弃）。
- 若插件项 id 命中**已存在项**，则允许以白名单类型去**修改**该项。
- DAO 层对白名单类型的既有项，仅当金额发生变化时才会更新其可变字段（`updateItemFields`），用于防止重复写入（见 Kill Bill issue #993）。

**含义**：插件不能凭空插入 `RECURRING`/`FIXED`/`USAGE`/`PARENT_SUMMARY`/`CBA_ADJ`/`REPAIR_ADJ` 等类型的新项。

## BR-071 发票插件项的「可变 / 不可变」字段规则

- **类型**: 业务规则
- **同义词**: 插件字段覆盖, mutable field, immutable field, 插件修改发票项, 字段不可变
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoicePluginDispatcher.java:388-463`

**规则**：插件修改既有发票项时，字段分两类：
- **可变（插件新值优先）**：`description`、`amount`、`rate`、`quantity`、`itemDetails`、`prettyProductName`、`prettyPlanName`、`prettyPhaseName`、`prettyUsageName`、`createdDate`。
- **不可变（保留既有值，插件新值被忽略并告警）**：`accountId`、`bundleId`、`subscriptionId`、`productName`、`planName`、`phaseName`、`usageName`、`catalogEffectiveDate`、`startDate`、`endDate`、`currency`、`linkedItemId`、`invoiceItemType`。
- `invoiceId`：优先取既有项，其次插件值，最后回退到原发票 id；`id` 缺省时随机生成。

**含义**：插件无法改变账期、币种、订阅归属与类型，只能改金额/描述/数量等。

## BR-072 发票项调整金额上限计算（不可超调）

- **类型**: 业务规则
- **同义词**: 项调整上限, 不可超调, maxAdjLeftAmount, INVOICE_ITEM_ADJUSTMENT_AMOUNT_INVALID, 部分调整
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:105-144`

**规则**：对某原项做调整时，先算出「本次最多还能调整多少」：
- `positiveAdjustedOrRepairedAmount` = 该原项所有 `ITEM_ADJ`/`REPAIR_ADJ`（金额为负）取负后之和；
- `maxAdjLeftAmount = 原项金额 − positiveAdjustedOrRepairedAmount`。
- 若用户显式指定调整金额且 **> maxAdjLeftAmount** → 抛 `INVOICE_ITEM_ADJUSTMENT_AMOUNT_INVALID`；
- 若未指定金额 → 默认调整为 `maxAdjLeftAmount`（即调整剩余全部，支持多次部分调整后再全额调整）；
- 结果为 0 时不生成调整项。

**含义**：支持对同一发票项**多次部分调整**，累计调整额不会超过原项金额。

## BR-073 退款与发票项调整必须成对出现

- **类型**: 业务规则
- **同义词**: 退款带调整, refund with item adjustment, isInvoiceAdjusted, INVOICE_ITEMS_ADJUSTMENT_MISSING, 退款不给调整
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:806-813`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:882-912`

**规则**：创建退款（`createRefund`）时：
- 若 `isInvoiceAdjusted=true` 但 `invoiceItemIdsWithNullAmounts` **为空** → 抛 `INVOICE_ITEMS_ADJUSTMENT_MISSING`（声明要调整项却没说调整哪些）。
- 仅当退款状态为 `SUCCESS` 时，才会真正生成 `ITEM_ADJ` 项并触发 CBA 重算；非 SUCCESS 的退款只记录支付行，不调整项、不算 CBA。
- 退款记录金额以**负值**存储（`requestedPositiveAmount.negate()`）。

**含义**：模拟「退款不调项」（只退钱、账单金额不变）与「退款并调项」（退钱且冲减应收）两种组合。

## BR-074 退款金额上限与「退款额=调整项之和」校验

- **类型**: 业务规则
- **同义词**: 退款上限, REFUND_AMOUNT_TOO_HIGH, REFUND_AMOUNT_DONT_MATCH_ITEMS_TO_ADJUST, 退款金额校验
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:155-175`

**规则**：`computePositiveRefundAmount`：
- 最大可退金额 `maxRefundAmount` = 原支付（ATTEMPT）金额；未指定退款额时默认取该最大值；
- 若请求退款额 **> 最大可退金额** → 抛 `REFUND_AMOUNT_TOO_HIGH`；
- 若指定了要调整的发票项，则 `amountFromItems` = 各调整额之和；若该和 ≠ 0 且 **请求退款额 < amountFromItems** → 抛 `REFUND_AMOUNT_DONT_MATCH_ITEMS_TO_ADJUST`（退款额必须 ≥ 项调整之和）。

## BR-075 退款的幂等去重（按 transactionExternalKey）

- **类型**: 业务规则
- **同义词**: 退款幂等, refund idempotency, paymentCookieId, transactionExternalKey, 重复退款
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:844-873`

**规则**：退款前用 `transactionExternalKey`（即 `paymentCookieId`）查询既有退款记录：
- 若已存在：校验金额与 `paymentId` 一致，否则抛 `Preconditions` 异常；
- 若已存在且状态相同 → 直接返回既有记录（**不重复生成项、不算 CBA、不发事件**）；
- 若已存在但状态不同 → 仅更新其**状态与支付日期**（状态机重放）。

**含义**：支付系统可能对同一 refundId 多次回调，此机制保证退款只落一次账。

## BR-076 拒付（chargeback）金额与币种约束

- **类型**: 业务规则
- **同义词**: 拒付, 退单, chargeback, CHARGE_BACK_AMOUNT_IS_NEGATIVE, CHARGE_BACK_AMOUNT_TOO_HIGH, 拒付金额
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:920-966`

**规则**：`postChargeback`：
- 依据原 `ATTEMPT` 支付计算 `maxChargedBackAmount` = 该支付**剩余可拒付金额**（`getRemainingAmountPaid`）；
- 未指定金额时默认拒付全部剩余；
- 拒付额 ≤ 0 → 抛 `CHARGE_BACK_AMOUNT_IS_NEGATIVE`；
- 拒付额 > `maxChargedBackAmount` → 抛 `CHARGE_BACK_AMOUNT_TOO_HIGH`；
- 拒付币种必须与原支付币种一致（`Preconditions.checkArgument`）；
- 生成的 `CHARGED_BACK` 支付记录金额取**负值**，状态固定 `SUCCESS`，随后触发 CBA 重算并发送支付事件。

## BR-077 拒付撤销（chargeback reversal）语义

- **类型**: 业务规则
- **同义词**: 拒付撤销, chargeback reversal, 撤销拒付, INIT 状态, 恢复支付
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:970-1004`

**规则**：`postChargebackReversal` 按 `chargebackTransactionExternalKey` 找到原 `CHARGED_BACK` 支付行，将其状态改回 `INIT`（金额不变，仍为负），随后重算 CBA 并发送支付事件。找不到对应支付行 → 抛 `PAYMENT_NO_SUCH_PAYMENT`。

**含义**：撤销拒付不是删除记录，而是把状态从 SUCCESS 退回 INIT，从而不再计入 CBA/余额相关判定（因为只有 SUCCESS 才计入）。

## BR-078 删除账户信用（deleteCBA）规则

- **类型**: 业务规则
- **同义词**: 删除信用, deleteCBA, 取消信用, INVOICE_CBA_DELETED, 删除已用信用
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:1173-1234`

**规则**：`deleteCBA(accountId, invoiceId, invoiceItemId)`：
- 发票必须属于该账户、非迁移、且状态为 `COMMITTED`，否则抛 `INVOICE_NOT_FOUND`；CBA 项必须属于该发票，否则 `INVOICE_ITEM_NOT_FOUND`。
- **消费型 CBA（金额 < 0）**：直接把该项金额更新为 0（描述 `"Delete used credit"`）。
- **生成型 CBA（金额 > 0，即信用发票）**：需在该发票上找一条 `CREDIT_ADJ`（其金额取负 ≥ CBA 金额）。找到则：
  - 若账户剩余 CBA < 该 CBA 金额 → 通过 `reclaimCreditFromTransaction` 回收不足部分（可能跨多张发票，更新已用 CBA 项金额，描述 `"Reclaim used credit"`），并断言回收额精确匹配；
  - 把该 CBA 项金额更新为 0；`CREDIT_ADJ` 金额更新为 `原值 + CBA 值`（描述 `"Delete gen credit"`）。
- **系统生成的信用**（如 repair 产生、无对应 CREDIT_ADJ）→ 抛 `INVOICE_CBA_DELETED`。
- 最后对涉及的每张发票发送发票调整事件。

## BR-079 回收已用信用（reclaim）跨发票机制

- **类型**: 业务规则
- **同义词**: 回收信用, reclaim credit, 已用信用回收, Reclaim used credit, 信用回滚
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:1147-1170`

**规则**：`reclaimCreditFromTransaction(amountToReclaim, ...)` 拉取所有**已消费的 CBA 项**（`getConsumedCBAItems`），按顺序逐条回收：
- 对每条消费 CBA（金额为负），可回收上限 = `−金额`；
- 本次回收 `adjustedAmount = min(剩余待回收, 该条上限)`；
- 将该 CBA 项金额改为 `−(上限 − 已回收)`（描述 `"Reclaim used credit"`）；
- 累加剩余待回收，直至归零或遍历完；返回实际回收总额。

**含义**：删除「生成型信用」而账户剩余信用不足时，会逆向回收此前已被消费掉的信用，保证账户 CBA 不为负。

## BR-080 账户余额（account balance）的完整计算口径

- **类型**: 业务规则
- **同义词**: 账户余额算法, account balance formula, 跳过草稿作废, 扣减CBA, 核销不计
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:730-759`

**规则**：`getAccountBalance` 遍历账户全部（非作废）发票：
- **跳过** `DRAFT` 与 `VOID` 状态的发票；
- 对每张发票：若**已核销**或「父发票余额为 0/父发票为 DRAFT/VOID/已核销」（`hasZeroParentBalance`）→ 该发票计 0；
  否则计入其 `getRawBalanceForRegularInvoice`；
- 同时累加该发票的 `getCBAAmount`；
- 最终 `accountBalance = Σ发票余额 − ΣCBA`。
- 此外：`getAccountBalance`/`getAccountCBA` 查询返回 null 时统一当 `BigDecimal.ZERO`。

**含义**：账户余额口径与单张发票余额（BR-019/BR-020）不同——账户余额会扣减账户信用（CBA），且完全排除草稿/作废。

## BR-081 支付事件：成功发 Info，其他发 Error

- **类型**: 业务规则
- **同义词**: 支付事件, payment event, DefaultInvoicePaymentInfoEvent, DefaultInvoicePaymentErrorEvent, 支付成功事件
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:1292-1333`

**规则**：发送支付事件时按状态分流：
- `InvoicePaymentStatus.SUCCESS` → 发 `DefaultInvoicePaymentInfoEvent`；
- 其他状态（INIT/PENDING）→ 发 `DefaultInvoicePaymentErrorEvent`。
两者都携带 `accountId`、`paymentId`、`paymentAttemptId`、`type`、`invoiceId`、`paymentDate`、`amount`、`currency`、`linkedInvoicePaymentId`、`paymentCookieId`、`processedCurrency`、账户/租户 recordId、userToken。

## BR-082 支付尝试记录的创建与更新（INIT / completion）

- **类型**: 业务规则
- **同义词**: 支付尝试记录, payment attempt, notifyOfPaymentInit, notifyOfPaymentCompletion, paymentId 不可变
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:1078-1140`

**规则**：
- `notifyOfPaymentInit` 一律记录一条 `INIT` 支付行；`notifyOfPaymentCompletion` 若 `paymentId == null`（从未真正发起支付，如无支付方式）则**不落行**，但仍发送事件（供 Overdue 使用）。
- 按 `invoiceId` + `type=ATTEMPT` + `paymentCookieId=transactionExternalKey` 查找既有尝试行：
  - 不存在 → 新建；
  - 存在 → 更新日期/金额/币种/状态；`paymentId` 只允许从 null 补全或在双方相同时保留，否则 Preconditions 失败（issue #1230）。
- 更新时 `linkedInvoicePaymentId` 传 null（重置）。

## BR-083 发票号的来源（插件属性 INVOICE_SEQUENCE_NUMBER）

- **类型**: 业务规则
- **同义词**: 发票号来源, invoice number, INVOICE_SEQUENCE_NUMBER, 序列号, invoiceSequenceNumber, 自定义发票号
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/InvoiceApiHelper.java:123-129`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:507-512`, `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:491-495`

**规则**：
- 发票号并非数据库列，而是以 **CustomField**（字段名常量 `INVOICE_SEQUENCE_NUMBER`）形式挂在发票对象上（`ObjectType.INVOICE`）。
- API 写入时，插件属性中若含 key = `INVOICE_SEQUENCE_NUMBER` 且值非空，则解析为 Integer 设为该发票的 `invoiceNumber`。
- 读取发票时，`InvoiceDaoHelper.setInvoiceNumber` 从该 CustomField 反填 `InvoiceModelDao.invoiceNumber`。
- `getInvoiceByNumber` 与 `searchInvoices`（搜索串可解析为整数时）都走发票号路径。

## BR-084 通过 API 写发票项的统一加锁与插件链

- **类型**: 业务规则
- **同义词**: API 写项加锁, dispatchToInvoicePluginsAndInsertItems, ACCNT_INV_PAY, 插件链, 发票 API 锁
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/InvoiceApiHelper.java:79-176`

**规则**：外部收费 / 税 / 信用 / 项调整 / 提交 / 作废等 API 都通过 `dispatchToInvoicePluginsAndInsertItems`：
1. 先调插件 `priorCall`；若插件返回 rescheduleDate → 抛 `INVOICE_PLUGIN_API_ABORTED`（“delayed scheduling is unsupported for API calls”）。
2. 以 `LockerType.ACCNT_INV_PAY` 对账户加全局锁（重试次数 `getMaxGlobalLockRetries`）；加锁失败抛 `UNEXPECTED_ERROR`（“failed to acquire lock”）。
3. `withAccountLock.prepareInvoices()` 在锁内准备/校验发票。
4. 逐张发票调插件 `getAdditionalInvoiceItems`（可修改金额），再把结果落库。
5. **成功** → 对每张发票调插件 `onSuccessCall`；**失败** → 调 `onFailureCall`。
6. `insertItems=false` 时（如 commit/void）只执行锁内逻辑与插件回调，不写新项。

## BR-085 发票 HTML 渲染时合并 CBA 与信用调整项

- **类型**: 业务规则
- **同义词**: 发票渲染合并, merge CBA, 合并信用项, HTML 发票, 隐藏内部调整, mergeCBAAndCreditAdjustmentItems
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/template/formatters/DefaultInvoiceFormatter.java:109-190`

**规则**：生成发票 HTML/模板时：
- 所有 `CBA_ADJ` 项**合并为一条**（金额相加），描述为对客户的内部调整（避免暴露多条自动调整）；
- 所有 `CREDIT_ADJ` 项**合并为一条**；
- 合并后若某条合并项金额为 **0** → **不展示**；
- 币种不同的 CBA/信用项不合并（各自保留）。
- 发票号未设置时展示为 `0`；`paidAmount`/`balance`/`chargedAmount` 等 null 时按 0 展示。

**含义**：面向客户的发票只显示汇总后的信用/账户信用，明细行的合并策略与其他类型项无关。

## BR-086 已计费截止日期（charged-through dates）计算规则

- **类型**: 业务规则
- **同义词**: 计费截止日, charged through date, CTD, chargedThroughDates, 已开票到哪天
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceWithMetadata.java:116-154`

**规则**：`computeChargedThroughDates`：
- 仅当发票状态为 `COMMITTED` 时才计算（issue #1296）；否则返回空 Map。
- 只考虑 `FIXED`/`RECURRING`/`USAGE` 三类项（插件项也不排除，按类型过滤）。
- 每项取 `endDate`（为 null 时取 `startDate`）作为候选 CTD；
- 同一订阅取**最晚**的候选 CTD；
- 最终按 CTD 日期分组，输出 `Map<DateTime, List<subscriptionId>>`。

## BR-087 IN_ADVANCE 待开票日期清零（防止无限通知循环）

- **类型**: 业务规则
- **同义词**: 清零下次开票日, reset next recurring date, 无限循环, IN_ADVANCE 通知
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceWithMetadata.java:77-89`

**规则**：`InvoiceWithMetadata.build()` 在收敛未来通知日期时：
- 若某订阅计算的 `nextRecurringDate` 非空、且其 `recurringBillingMode == IN_ADVANCE`、且**该订阅最终没有任何 RECURRING 项**、且没有任何项落在该日期上（如 REPAIR_ADJ）→ 将该 `nextRecurringDate` **清零**。
- 目的：`nextRecurringDate` 基于「提议项」而非「缺失项」计算，若不清零会生成过多通知日期，可能造成无限循环。

## BR-088 下一次开票通知的去重与订阅合并

- **类型**: 业务规则
- **同义词**: 下次开票通知去重, next billing notification dedup, 合并订阅, 通知合并
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/notification/DefaultNextBillingDatePoster.java:76-157`

**规则**：插入「下一次开票」未来通知时：
- 按「生效**本地日期**相同 **且** dry-run 标志相同」查找既有通知；普通通知与 dry-run 通知互不视为重复。
- 若不存在 → 新建通知（携带 subscriptionIds、targetDate、isDryRun、isRescheduled）。
- 若存在且新订阅集合是既有集合的**子集** → 忽略（debug 日志）。
- 若存在且包含**新订阅** → **更新**既有通知，合并订阅 id。
- 通知主键 `NextBillingDateNotificationKey` 由 `(uuidKeys, targetDate, isDryRunForInvoiceNotification, isRescheduled)` 构成。

## BR-089 账户信用余额查询口径（getCBAAmount = credited）

- **类型**: 业务规则
- **同义词**: 信用余额口径, getCBAAmount, 账户CBA, credited amount, 信用汇总
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceModelDaoHelper.java:48-56`

**规则**：`InvoiceModelDaoHelper` 的两个聚合：
- `getCBAAmount(发票)` = `InvoiceCalculatorUtils.computeInvoiceAmountCredited`，即该发票所有 `CBA_ADJ` 项金额之和。
- `getAmountCharged(发票)` = `computeInvoiceAmountCharged`（见 BR-023）。
账户层 CBA 由数据库直接聚合（`InvoiceItemSqlDao.getAccountCBA`）；账户余额则用 `Σ发票余额 − ΣgetCBAAmount`（见 BR-080）。

## BR-090 原始计费金额（original charged amount）

- **类型**: 业务规则
- **同义词**: 原始计费金额, original charged amount, getOriginalChargedAmount, 发票创建时金额, original amount charged
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/calculator/InvoiceCalculatorUtils.java:176-190`, `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoice.java:254-256`

**规则**：`getOriginalChargedAmount` = 仅累加**收费项**（`isCharge`）中 **`createdDate` 恰好等于发票 `createdDate`** 的金额。即「发票创建当时就存在的收费金额」，用于与后续追加/调整后的 `getChargedAmount` 对比。

**对照**：`getChargedAmount` = 全部收费项 + 发票级调整 + 项调整 + 父汇总（BR-023）；`getCreditedAmount` = 全部 `CBA_ADJ` 之和；`getRefundedAmount` = SUCCESS 的 REFUND + CHARGED_BACK 之和（BR-022）。

## BR-091 发票分组 id（grpId）默认值

- **类型**: 业务规则
- **同义词**: 分组 id, grpId, invoice group, 一次开票分组, group id
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceModelDao.java:81`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:497-500`

**规则**：
- `InvoiceModelDao.grpId` **默认等于发票自身 id**（构造时 `this.grpId = id`），除非显式设置。
- 在一次 `createInvoices` 批量创建中，第一张新建发票的 id 会成为**整个批次共享的 grpId**（用于把同一次开票产生的多张发票归为一组）。
- 可通过 `getInvoicesByGroup(accountId, groupId)` 按分组查询。

## BR-092 金额舍入规则（KillBillMoney）

- **类型**: 业务规则
- **同义词**: 金额舍入, rounding, 四舍五入, KillBillMoney, MAX_SCALE, ROUND_HALF_UP, 小数位
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/currency/KillBillMoney.java:27-34`, `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceDateUtils.java:80-89`

**规则**：
- 金额四舍五入方式 `ROUNDING_METHOD = BigDecimal.ROUND_HALF_UP`（标准四舍五入）。
- 分比（proration）等中间计算使用最大精度常量 `MAX_SCALE = 9`（即保留 9 位小数）。
- `KillBillMoney.of(amount, currency)` 最终按**币种的小数位**（`currencyUnit.getDecimalPlaces()`）以 HALF_UP 收敛。invoice 模块的余额/金额聚合结果都经过该规范化。

## BR-093 整周期数与分比天数的计算（InvoiceDateUtils）

- **类型**: 业务规则
- **同义词**: 整周期数, whole billing periods, 分比天数, proration days, fixedDaysInMonth, advanceByNPeriods
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceDateUtils.java:34-115`

**规则**：
- `calculateNumberOfWholeBillingPeriods(start, end, period)`：按 billingPeriod 的单位（天/周/月/年，取决于 period 的哪个字段非 0）计算两日期间隔并**整除**周期长度，得到完整周期数。
- 分比比例 = `days / daysInPeriod`，使用 MAX_SCALE(9) 精度 + HALF_UP。
- `daysInPeriod`：`prorationFixedDays == 0` 时取 `previousBillingCycleDate → nextBillingCycleDate` 的实际天数；否则取 `prorationFixedDays`。
- `days`：`prorationFixedDays == 0` 时取实际天数；否则用 `daysBetweenWithFixedDaysInMonth`：同月直接返回实际天数，跨月则减去 `(该月最后一天 − fixedDaysInMonth)`。
- `daysBetween <= 0` → 分比返回 `BigDecimal.ZERO`。
- `advanceByNPeriods`/`recedeByNPeriods`：按周期循环加减 N 次（支持负数周期语义）。

## BR-094 账户挂起 / 解挂机制（PARK 系统标签）

- **类型**: 业务规则
- **同义词**: 挂起账户, park account, PARK 标签, unpark, isParked, 系统标签
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/ParkedAccountsManager.java:47-67`

**规则**：账户的「挂起」是通过给账户打上系统标签 `PARK_TAG_DEFINITION_ID` 实现的：
- `parkAccount`：添加该标签；**幂等**——若已存在（`TAG_ALREADY_EXISTS`）则忽略。
- `unparkAccount`：移除该标签。
- `isParked`：查询账户级标签中是否存在该 tag definition id。
（挂起后对开票的影响见 BR-046/BR-047。）

## BR-095 移除 AUTO_INVOICING_OFF 标签后重新开票

- **类型**: 业务规则
- **同义词**: 恢复自动开票, AUTO_INVOICING_OFF 移除, tag deletion, 重新开票, InvoiceTagHandler
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceTagHandler.java:72-125`

**规则**：`InvoiceTagHandler` 订阅账户级 `ControlTagDeletionInternalEvent`：
- 当被删除的标签是 `AUTO_INVOICING_OFF` 且对象类型为 `ACCOUNT` 时，调用 `dispatcher.processAccountFromNotificationOrBusEvent` 为账户重新尝试开票（可能补开被暂停期间的发票）。
- 处理经可靠订阅队列重试（失败仅告警，不阻塞）。

## BR-096 退款金额必须为正

- **类型**: 业务规则
- **同义词**: 退款金额校验, PAYMENT_REFUND_AMOUNT_NEGATIVE_OR_NULL, 退款不能为负, refund amount
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/svcs/DefaultInvoiceInternalApi.java:130-135`

**规则**：`recordRefund` 入口即校验 `amount ≤ 0` → 抛 `PAYMENT_REFUND_AMOUNT_NEGATIVE_OR_NULL`。随后调用 DAO `createRefund` 并（为事件传播）重新走一遍开票插件链（`dispatchToInvoicePluginsAndInsertItems`）。

## BR-097 退款项调整的预校验入口

- **类型**: 业务规则
- **同义词**: 退款项预校验, validateInvoiceItemAdjustments, 退款调整映射, INVOICE_ITEMS_ADJUSTMENT_MISSING
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/svcs/DefaultInvoiceInternalApi.java:164-171`

**规则**：`validateInvoiceItemAdjustments(paymentId, idWithAmount)`：
- `idWithAmount` 为空 → 抛 `INVOICE_ITEMS_ADJUSTMENT_MISSING`（退款必须带项调整映射）；
- 通过原 `ATTEMPT` 支付找到发票，再调用 `computeItemAdjustments`（BR-072 的上限/校验逻辑）返回校验后的 `id→金额` 映射。

**含义**：支付模块在发起退款前会先调用此接口校验项调整是否合法。

## BR-098 按 paymentId 取支付时只认 SUCCESS 的 ATTEMPT

- **类型**: 业务规则
- **同义词**: paymentId 查支付, SUCCESS ATTEMPT, getInvoicePayment, 支付过滤
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/svcs/DefaultInvoiceInternalApi.java:174-181`

**规则**：`getInvoicePayment(paymentId, type)` 在按 paymentId 取某类型支付时，只保留 **`status == SUCCESS`** 的记录，返回第一条匹配；无则返回 null。退款、拒付关联的查找也遵循同样过滤。

## BR-099 发票状态默认值与迁移发票构造

- **类型**: 业务规则
- **同义词**: 发票默认状态, COMMITTED 默认, 迁移发票构造, migration invoice constructor, DRAFT 构造
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceModelDao.java:84-94`, `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoice.java:76`

**规则**：
- `InvoiceModelDao(accountId, invoiceDate, targetDate, currency, migrated)`：状态**默认 `COMMITTED`**、`isParentInvoice=false`。
- 带 `status` 参数的构造可显式指定 DRAFT/COMMITTED。
- 父发票专用构造 `InvoiceModelDao(accountId, invoiceDate, currency, status, isParentInvoice=true)`：`targetDate` 为 **null**。
- `DefaultInvoice(accountId, invoiceDate, targetDate, currency)`：状态默认 `COMMITTED`。
- 迁移发票（`migrated=true`）创建时状态也为 `COMMITTED`（见 BR-057：其余额恒为 0）。

## BR-100 批量写入中的 shell 发票与缺失发票校验

- **类型**: 业务规则
- **同义词**: shell invoice, 空壳发票, invoiceIdsReferencedFromItems, INVOICE_NOT_FOUND, 引用发票校验
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:487-536`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:576-581`

**规则**：`createInvoices` 处理一批发票时：
- 若某发票 id 只作为**已存在发票项**的引用出现（被 `invoiceIdsReferencedFromItems` 集合包含，即该发票本身不在本批创建列表中）→ 视为「shell 发票」，**不创建**该发票行。
- 若该引用发票在磁盘上也不存在 → 抛 `INVOICE_NOT_FOUND`。
- 真正新建的发票会分配共享 `grpId`（BR-091），并可写入发票号 CustomField（BR-083）。

## BR-101 复用草稿发票：DRAFT→COMMITTED 与 targetDate 只前移

- **类型**: 业务规则
- **同义词**: 复用草稿, reuse draft, DRAFT 转 COMMITTED, targetDate 前移, 幂等开票
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:516-536`

**规则**：当输入的发票在磁盘上已存在（常见于 `AUTO_INVOICING_REUSE_DRAFT`）：
- 状态：仅当**输入为 COMMITTED 且磁盘为 DRAFT** 时，才把磁盘发票更新为 COMMITTED；其他状态组合保持不变（不回退）。
- `targetDate`：仅当输入 `targetDate` 非空、且磁盘 `targetDate` 为空或**早于**输入值时才更新——即 targetDate **只能前移，不能后退**。
- 状态或 targetDate 有变化时记入 `committedReusedInvoiceId`，用于后续事件判定。

## BR-102 发票调整事件的发送条件

- **类型**: 业务规则
- **同义词**: 调整事件, invoice adjustment event, adjustedCommittedInvoiceIds, 余额变化事件
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:556-569`

**规则**：批量写入时对状态为 `COMMITTED` 的发票：
- 若本次**新建或刚提交**（`wasInvoiceCreatedOrCommitted`）→ 发送**发票创建事件**（InvoiceCreationEvent，携带 rawBalance/currency）。
- 否则若本次**新增了发票项**（`hasInvoiceBeenAdjusted`，如调整/退款/外部收费）→ 记入 `adjustedCommittedInvoiceIds`，随后发送**发票调整事件**（InvoiceAdjustmentEvent，供 Overdue 等使用）。
- 父发票被新建时改发 `notifyOfParentInvoiceCreation`（安排父发票提交通知，见 WF-004）。

## BR-103 发票支付金额的符号约定与关联

- **类型**: 业务规则
- **同义词**: 支付金额符号, amount sign, 退款负数, 拒付负数, linkedInvoicePaymentId, 支付关联
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:875-878`, `invoice/src/main/java/org/killbill/billing/invoice/dao/DefaultInvoiceDao.java:951-954`, `invoice/src/main/java/org/killbill/billing/invoice/model/DefaultInvoicePayment.java:55`

**规则**：`InvoicePayment` 金额符号有固定约定：
- `ATTEMPT`（支付尝试）：**正数**（按实际支付金额）。
- `REFUND`（退款）：**负数**（`requestedPositiveAmount.negate()`）。
- `CHARGED_BACK`（拒付）：**负数**（`requestedChargedBackAmount.negate()`）。
- `linkedInvoicePaymentId`：退款/拒付记录指向**原 ATTEMPT 支付**的 id（`payment.getId()`）。
- `DefaultInvoicePayment` 未指定状态时默认 `SUCCESS`。

**含义**：余额计算中 `amountPaid = ΣATTEMPT + Σ(REFUND+CHARGED_BACK)`（后者为负），所以退款/拒付自然抵减已付金额（见 BR-019/BR-021/BR-022）。

## BR-104 发票 processing currency（processedCurrency）的推断

- **类型**: 业务规则
- **同义词**: 处理币种, processed currency, processedCurrency, 支付币种, 币种转换
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceDaoHelper.java:365-407`, `invoice/src/main/java/org/killbill/billing/invoice/dao/InvoiceModelDao.java:129-135`, `invoice/src/main/java/org/killbill/billing/invoice/template/formatters/DefaultInvoiceFormatter.java:291-323`

**规则**：
- 加载发票的支付后，若发现**任一条**支付的 `currency != processedCurrency`，则把该 `processedCurrency` 设为发票的 `processedCurrency`（取第一条不同的）。
- `InvoiceModelDao.getProcessedCurrency()` 在未设置时回退到发票本身币种。
- 模板渲染时：仅当 `processedCurrency != 发票币种` 才展示处理币种与换算率；否则 `getProcessedCurrency()` 返回 null（模板不打印）。换算率取**最后一笔支付**的日期，通过 CurrencyConversionApi 查询到发票币种的汇率。

**含义**：一张发票可用非账户币种支付（如跨境），此时发票上记录处理币种，模板额外展示原币金额与汇率。

## BR-105 按支付 / 发票项 / 分组反查发票

- **类型**: 业务规则
- **同义词**: 反查发票, getInvoiceByPayment, getInvoiceByInvoiceItem, getInvoicesByGroup, 按支付查发票
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:184-199`, `invoice/src/main/java/org/killbill/billing/invoice/api/user/DefaultInvoiceUserApi.java:262-268`

**规则**：
- `getInvoiceByPayment(paymentId)`：由支付 id → 发票 id；找不到发票 id → 抛 `INVOICE_NOT_FOUND`。
- `getInvoiceByInvoiceItem(invoiceItemId)`：由发票项 id 反查其所属发票。
- `getInvoicesByGroup(accountId, groupId)`：取同一次开票分组（grpId，见 BR-091）产生的全部发票。
- 上述返回的发票都会附带目录（若可用）以填充 pretty names。

## BR-106 账户信用消费的票据处理优先级（candidate → unpaid）

- **类型**: 业务规则
- **同义词**: 信用消费顺序, CBA priority, candidate invoices, remainingAccountCBA, 信用先用后分配
- **模块**: invoice
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/dao/CBADao.java:152-218`

**规则**：一次事务内的 CBA 处理顺序：
1. 先从数据库一次性算出账户当前可用信用 `remainingAccountCBA = getAccountCBAFromTransaction`。
2. 若本次有**候选/新建发票**：逐张计算 CBA（生成或消费），并用 `remainingAccountCBA = remainingAccountCBA + cbaItem.getAmount()`（CBA 项金额本身带符号）**滚动更新**剩余额度。
3. 再用剩余信用跑一遍**全部未付发票**（按 invoiceDate 升序，见 BR-027），逐张抵扣直至信用耗尽（`remainingAccountCBA ≤ 0` 即 break）。
4. 返回涉及的所有发票 id（去重），用于发送发票调整事件。

**含义**：新建发票的信用结果会影响后续对历史未付发票的信用分配额度，二者在一次事务中按上述顺序完成。

<!-- supplement: 50 cards | BR-I: 40, TERM-I: 2, ENT-I: 5, WF-I: 2, SM-I: 1 | module: invoice | extracted_at: 2026-09-17 -->

## BR-107 逾期是账户级（跨订阅）规则

- **类型**: 业务规则
- **同义词**: 逾期是账户级, 账户维度催收, 跨订阅逾期, account-level overdue, overdue is per account
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:221-235`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:109-122`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueConfig.java:41-45`

**规则**：逾期状态以**账户**为粒度计算与持久化，而非单个订阅。持久化时用 `BlockingStateType.ACCOUNT` + 服务名 `overdue-service`（`storeNewState`）；计算时对「该账户所有未付发票」聚合（`unpaidInvoicesForAccount`）。配置模型也只有 `accountOverdueStates`，无订阅级状态。
**影响**：一个账户下任一未付发票都会影响整个账户的逾期状态；取消订阅动作会作用到账户下所有非 ADD_ON 订阅（见 BR-120）。

## BR-108 条件：未付发票数量达到阈值

- **类型**: 业务规则
- **同义词**: 未付发票数量, 欠费张数, 发票数量条件, numberOfUnpaidInvoicesEqualsOrExceeds, unpaid invoice count
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:77`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestCondition.java:49-68`

**规则**：`numberOfUnpaidInvoicesEqualsOrExceeds=N` 时，当且仅当 `state.getNumberOfUnpaidInvoices() >= N` 为真。测试证实：N=1 时 0 张不命中、1 张与 2 张命中。

## BR-109 条件：未付发票余额合计达到阈值

- **类型**: 业务规则
- **同义词**: 未付余额, 欠费金额, 余额阈值, totalUnpaidInvoiceBalanceEqualsOrExceeds, total unpaid balance
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:78`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestCondition.java:70-90`

**规则**：`totalUnpaidInvoiceBalanceEqualsOrExceeds=B` 时，当且仅当 `B <= state.getBalanceOfUnpaidInvoices()` 为真（BigDecimal 比较，含等于）。测试：B=100 时余额 0 不命中、100 与 200 命中。

## BR-110 条件：最早未付发票距今时长达到阈值

- **类型**: 业务规则
- **同义词**: 逾期天数, 最早未付发票时长, 账龄条件, timeSinceEarliestUnpaidInvoiceEqualsOrExceeds, days overdue, aging
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:71-74`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:79-80`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:99-118`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestCondition.java:92-114`

**规则**：配置 `<timeSinceEarliestUnpaidInvoiceEqualsOrExceeds><unit>…</unit><number>…</number></…>`。计算：`triggerDate = dateOfEarliestUnpaidInvoice + duration`；条件为真当且仅当 `triggerDate <= now`（`!triggerDate.isAfter(date)`）。若账户无最早未付发票日期（即无未付发票），该子条件为假。
**时间单位**：来自 `DefaultDuration`/`TimeUnit`，实际支持 `DAYS / WEEKS / MONTHS / YEARS`（`UNLIMITED` 非法）。测试：unit=DAYS, number=10 时「10 天前」与「20 天前」命中、「无日期」不命中。

## BR-111 条件：控制标签必须存在（controlTagInclusion）

- **类型**: 业务规则
- **同义词**: 必须包含标签, 标签包含条件, controlTagInclusion, include control tag, 标签门控
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:82`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:96-103`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestCondition.java:140-174`

**规则**：`controlTagInclusion=T` 时，当且仅当账户标签集合中存在 `tagDefinitionId == T.getId()` 的标签才为真。测试：`OVERDUE_ENFORCEMENT_OFF` 存在时命中，不存在时（仅有 AUTO_INVOICING_OFF/DescriptiveTag）不命中。配置示例见 `overdueWithControlTag.xml`（各状态要求 `TEST` 标签）。

## BR-112 条件：控制标签必须不存在（controlTagExclusion）

- **类型**: 业务规则
- **同义词**: 必须排除标签, 标签排除条件, controlTagExclusion, exclude control tag, 标签否决
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:83`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:105-112`, `profiles/killbill/src/test/resources/org/killbill/billing/server/overdueWithExclusionControlTag.xml:18-62`

**规则**：`controlTagExclusion=T` 时，当且仅当账户标签集合中**不存在**该控制标签才为真（存在则一票否决该状态条件）。配置示例见 `overdueWithExclusionControlTag.xml`（各状态用 `<controlTagExclusion>TEST</controlTagExclusion>`）。

## BR-113 条件：上次失败支付响应（当前未真正实现）

- **类型**: 业务规则
- **同义词**: 上次支付失败原因, 支付响应条件, responseForLastFailedPaymentIn, last failed payment response, PaymentResponse
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:81`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:86-94`, `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:79`

**规则（配置层）**：`responseForLastFailedPaymentIn=[R1,R2,…]` 时，当且仅当账户「上次失败支付响应」等于列表之一才为真。可配置值示例：`INVALID_CARD`、`LOST_OR_STOLEN_CARD`、`INSUFFICIENT_FUNDS`、`DO_NOT_HONOR`。
**重要例外（未实现）**：上游 `BillingStateCalculator` 把 `responseForLastFailedPayment` **硬编码为 `PaymentResponse.INSUFFICIENT_FUNDS`（源码注释 `//TODO MDW`）**，并未从真实支付失败记录读取。因此除了「恰好配置为 INSUFFICIENT_FUNDS」外的响应类型实际上无法命中。即：该条件是「已建模、但输入未接线（not implemented）」的功能。

## BR-114 多子条件为 AND，未配置的子条件被忽略

- **类型**: 业务规则
- **同义词**: 条件组合, 多条件与, AND 组合, condition AND, all conditions must hold
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:76-84`

**规则**：`evaluate` 返回对全部 6 个子条件的合取。每个子条件写成 `(cfg == null || 实际检查)`，因此**未配置（null）的子条件恒为真**——即不构成约束。只要有一个已配置的子条件为假，整个条件即为假。

## BR-115 状态选择：按配置顺序取首个命中状态，否则 clear

- **类型**: 业务规则
- **同义词**: 状态选择, 命中优先级, 匹配第一个状态, state selection, first matching state, calculateOverdueState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:59-67`, `overdue/src/test/resources/org/killbill/billing/overdue/OverdueConfig3.xml:18-70`

**规则**：`calculateOverdueState(billingState, now)` 按 `state[]` 的**声明顺序**从头遍历，返回第一个条件为真的状态；若无任何命中则返回 clear state。因此配置中**越靠前的状态优先级越高**。示例 `OverdueConfig3.xml` 顺序为 OD4→OD3→OD2→OD1，OD4（未付≥5 且带 AUTO_PAY_OFF）优先级最高。

## BR-116 状态升级顺序与「首状态」语义

- **类型**: 业务规则
- **同义词**: 状态升级, 升级顺序, 催收梯度, escalation order, first state, getFirstState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:92-95`, `overdue/src/test/java/org/killbill/billing/overdue/config/TestOverdueConfig.java:70-76`, `profiles/killbill/src/main/resources/overdue.xml:19-61`

**规则**：约定配置里「最严重状态写在最前、最轻状态写在最后」。`getFirstState()` 返回数组**最后一个**元素，即**入门级/最轻**的逾期状态（如 OD1/OD3 场景中的 OD1，或 overdue.xml 中的 OD1）。测试 `TestOverdueConfig` 断言 OD2、OD1 顺序下 `getFirstState().getName()=="OD1"`。
**用途**：`firstOverdueState` 用于「尚未进入首个逾期状态但有未付发票，仍要安排下次检查」的判断（见 BR-122）。

## BR-117 状态未变化时为 no-op（但仍可能安排下次通知）

- **类型**: 业务规则
- **同义词**: 状态不变, 无操作, 幂等, no-op, state unchanged
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:127-132`

**规则**：`apply` 先处理通知调度（BR-122），随后若 `previousOverdueState.getName().equals(nextOverdueState.getName())`，直接返回——不取消订阅、不切换 AUTO_INVOICING_OFF、不写 BlockingState、不发事件。即：动作只在**状态真正变化**时执行。

## BR-118 blockChanges 动作映射到 BlockingState.blockChange

- **类型**: 业务规则
- **同义词**: 阻止变更动作, blockChange, 冻结变更
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:221-231`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:263-265`, `overdue/src/test/java/org/killbill/billing/overdue/TestOverdueHelper.java:119-124`

**规则**：施加状态时创建的 `DefaultBlockingState` 中 `blockChange = state.isBlockChanges() || state.isDisableEntitlementAndChangesBlocked()`。测试 helper 断言 blocking state 的 `isBlockChange()` 等于状态的 `isBlockChanges()`（仅在未 disableEntitlement 时；两者同真时也一致）。

## BR-119 disableEntitlementAndChangesBlocked 同时暂停权益与计费

- **类型**: 业务规则
- **同义词**: 禁用权益动作, 暂停服务, 停止计费, disableEntitlement, blockEntitlement, blockBilling, pause
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:263-273`, `overdue/src/test/java/org/killbill/billing/overdue/TestOverdueHelper.java:119-124`

**规则**：若 `isDisableEntitlementAndChangesBlocked()==true`，则 BlockingState 同时 `blockEntitlement=true`、`blockBilling=true`，并因 `blockChanges()` 的或运算而 `blockChange=true`。测试 helper 断言 `isBlockEntitlement()==isBlockBilling()==state.isDisableEntitlementAndChangesBlocked()`。业务效果：**暂停该账户的服务并停止计费**（stop billing / suspend），回到非 block billing 状态即 resume（见 BR-121）。

## BR-120 订阅取消策略：NONE / IMMEDIATE / END_OF_TERM

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

## BR-121 自动维护 AUTO_INVOICING_OFF 标签（防多生成信用）

- **类型**: 业务规则
- **同义词**: 自动关闭开票, 防止额外开票, AUTO_INVOICING_OFF 自动切换, avoid extra credit, toggle auto invoice off
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:176-183`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:237-253`

**规则**：
- 「进入 block billing」的转移（`isBlockBillingTransition`：prev 不 block billing、next block billing）→ 给账户打上 `AUTO_INVOICING_OFF` 标签，避免继续开票产生多余信用。
- 「解除 block billing」的转移（`isUnblockBillingTransition`）→ 移除 `AUTO_INVOICING_OFF` 标签；若标签本就不存在（`TAG_DOES_NOT_EXIST`）则忽略该错误。

## BR-122 重新评估通知的调度规则（定时器语义）

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

## BR-123 clear 状态清除未来通知

- **类型**: 业务规则
- **同义词**: 清除通知, 取消定时, clear notifications, clear future notification
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:123-125`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:275-283`

**规则**：当 `nextOverdueState.isClearState()` 且不满足「有欠费需继续检查」时，移除该账户在 `overdue-check-queue` 上的所有未来逾期检查通知（按 accountRecordId/tenantRecordId 检索后逐条删除）。`clear(...)` 路径也会调用它。

## BR-124 OVERDUE_ENFORCEMENT_OFF 短路并触发 CLEAR

- **类型**: 业务规则
- **同义词**: 豁免催收, 关闭催收生效, OVERDUE_ENFORCEMENT_OFF 短路, skip overdue enforcement, overdue enforcement off
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:109-113`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:98-107`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:334-349`

**规则**：`refreshWithLock` 首先检查账户是否被打了 `OVERDUE_ENFORCEMENT_OFF`；若是则**直接 return**（不计算、不切状态、不安排通知）。同时，给账户**新增**该控制标签的事件会以 `OverdueAsyncBusNotificationAction.CLEAR` 入队，引导 `OverdueDispatcher.clearOverdueForAccount` 把账户置回 clear 状态。业务效果：运营可用该标签「豁免/停止催收并清零状态」。

## BR-125 触发重新评估的事件集合

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
（账户级 `OVERDUE_ENFORCEMENT_OFF` 标签的**新增**特殊处理为 `CLEAR`，见 BR-124。）

## BR-126 仅当存在带条件的状态时才运行逾期机制（优化）

- **类型**: 业务规则
- **同义词**: 催收启用开关, 无配置不运行, shouldInsertNotification, overdue disabled optimization
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:168-174`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:206-225`

**规则**：监听器入队前调用 `shouldInsertNotification`：若租户逾期配置为空、`accountOverdueStates` 为空、状态数组为空，或**所有状态都没有 condition**（`getConditionEvaluation()` 全为 null），则不入队、直接返回。目的：若逾期未被有效配置，就不必跑整条催收链路。

## BR-127 父/子账户的级联与委派支付

- **类型**: 业务规则
- **同义词**: 父子账户, 委派支付, 家庭账户, parent child account, payment delegated to parent, cascade overdue
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:151-159`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:179-203`

**规则**：
1. **计算委派**：若账户有 `parentAccountId` 且 `isPaymentDelegatedToParent()`，则其逾期计费状态从**父账户**的上下文计算（用父账户 recordId 构造 context）。
2. **刷新级联**：账户入队 REFRESH/CLEAR 时，若其向父账户委派支付，则父账户也入队；并遍历其子账户，凡 `isPaymentDelegatedToParent()` 的子账户也入队。加载子账户失败仅记日志、不中断。

## BR-128 账户级全局锁与重试（MAX_LOCK_RETRIES=50）

- **类型**: 业务规则
- **同义词**: 逾期并发锁, 账户锁, 锁重试, global lock, MAX_LOCK_RETRIES, ACCNT_INV_PAY lock
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:56`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:89-107`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:129-142`

**规则**：`refresh`/`clear` 都先获取类型为 `ACCNT_INV_PAY`、键为账户 id 的全局锁，最多尝试 `MAX_LOCK_RETRIES=50` 次。获取失败（`LockFailedException`）时抛 `QueueRetryException`，并携带 `overdueConfig.getRescheduleIntervalOnLock(context)` 作为重排周期（由 killbill config 项控制），保证并发下操作最终执行。锁在 finally 释放。

## BR-129 autoReevaluationInterval 合法性校验

- **类型**: 业务规则
- **同义词**: 复评间隔校验, 无复评间隔错误, autoReevaluationInterval validation, OVERDUE_NO_REEVALUATION_INTERVAL
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:119-125`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`

**规则**：`OverdueState.getAutoReevaluationInterval()` 在 `autoReevaluationInterval==null`、`unit==UNLIMITED` 或 `number==0` 时抛 `OverdueApiException(OVERDUE_NO_REEVALUATION_INTERVAL, name)`。`OverdueStateApplicator.getReevaluationInterval` 捕获该错误码并返回 null → 不安排下次通知（其他错误码则转成 OverdueException 抛出）。

## BR-130 initialReevaluationInterval 为无效值时不重试

- **类型**: 业务规则
- **同义词**: 初始复评间隔, clear 状态轮询, initialReevaluationInterval
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:51-57`

**规则**：`getInitialReevaluationInterval()` 在 `initialReevaluationInterval==null`、`unit==UNLIMITED` 或 `number==0` 时返回 `null`；`OverdueStateApplicator` 收到 null 即不插入通知。也就是说 clear 状态若要被周期性复检，必须显式配置一个正数的初始复评间隔。

## BR-131 状态名长度上限 50

- **类型**: 业务规则
- **同义词**: 状态名长度, 名称上限, state name max length
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:47`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:171-178`

**规则**：`MAX_NAME_LENGTH = 50`；校验时若状态名长度超过 50，追加 ValidationError（"Name of state '%s' exceeds the maximum length of %d"）。这是逾期配置的硬校验项。

## BR-132 默认配置只含 Clear 状态（等价于未启用催收）

- **类型**: 业务规则
- **同义词**: 默认逾期配置, 无逾期配置, NoOverdueConfig, default overdue config, overdue disabled
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/resources/NoOverdueConfig.xml:20-27`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:58-66`

**规则**：内建默认配置 `NoOverdueConfig.xml` 的 `accountOverdueStates` 只包含一个 `name="Clear"` 且 `isClearState=true` 的状态，无任何条件。因此默认情况下没有任何状态会命中，账户始终为 clear，催收动作不触发。若默认配置 URL 为空或加载失败，系统记 warn 并处于「逾期系统禁用」状态（不改变状态）。

## BR-133 配置加载失败/无效时逾期系统被禁用

- **类型**: 业务规则
- **同义词**: 逾期配置加载失败, 配置无效, overdue disabled, config load failure
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/service/DefaultOverdueService.java:91-101`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:68-86`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:99-105`

**规则**：`DefaultOverdueService.loadConfig`（生命周期 LOAD_CATALOG）从 `properties.getConfigURI()` 加载默认配置；失败则 log.warn「Overdue system disabled」并保持 `isConfigLoaded=false`。租户级配置解析失败会被包装成 `OverdueApiException(OVERDUE_INVALID_FOR_TENANT)`；单个租户配置无效不影响其他租户（`get` 失败时抛异常，未命中则回退默认配置）。

## BR-134 通知去重：check 队列保留最早、async 队列有则跳过

- **类型**: 业务规则
- **同义词**: 通知去重, 队列去重, notification dedup, cleanup future notifications
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueCheckPoster.java:48-85`, `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusPoster.java:47-57`, `overdue/src/main/java/org/killbill/billing/overdue/notification/DefaultOverduePosterBase.java:67-84`

**规则**：插入未来通知前会在事务内查询该账户已有的未来通知：
- **overdue-check（定时复评）**：若已存在一条**更早**的通知，则不再插入新通知，并删除其余未来通知；否则删除已有通知、插入新通知。即**保留最早到期的那条**。
- **overdue-async-bus（事件刷新）**：若已存在任意未来通知则直接跳过插入（源码注释承认这是近似处理，可能出现 REFRESH/CLEAR 混排的非确定行为）。

## BR-135 getOverdueStateFor 从 blocking state 名解析当前状态

- **类型**: 业务规则
- **同义词**: 查询当前逾期状态, 当前状态解析, getOverdueStateFor, current overdue state
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:91-99`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:115-119`

**规则**：查询账户当前逾期状态时，读取该账户在 `overdue-service` 上的 BlockingState；若不存在则用 `CLEAR_STATE_NAME`，再通过状态集 `findState(stateName)` 解析。`findState` 对 clear 名特判返回内建 clearState，否则按名字查配置状态，找不到抛 `CAT_NO_SUCH_OVERDUE_STATE`。这条规则同时决定了「刷新时 previousOverdueState 的取值」。

## BR-136 租户配置上传会覆盖旧值并失效缓存

- **类型**: 业务规则
- **同义词**: 上传逾期配置, 覆盖配置, 配置缓存失效, upload overdue config, cache invalidation, OVERDUE_CONFIG
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:66-89`, `overdue/src/main/java/org/killbill/billing/overdue/caching/OverdueCacheInvalidationCallback.java:39-43`, `overdue/src/main/java/org/killbill/billing/overdue/service/DefaultOverdueService.java:103-113`

**规则**：上传逾期配置时：先删除租户键 `OVERDUE_CONFIG` 的旧值（若存在），再写入新 XML，然后清除该租户的逾期配置缓存。租户配置变更也会通过 `TenantKey.OVERDUE_CONFIG` 的 `CacheInvalidationCallback` 触发缓存失效。以 `OverdueConfig` 对象上传时，先序列化为 XML（`XMLWriter`），失败抛 `OVERDUE_INVALID_FOR_TENANT`。

## BR-137 有效日与条件日期口径

- **类型**: 业务规则
- **同义词**: 生效日期, 评估日期, effectiveDate, now, account timezone
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:104-107`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:124-127`, `api/src/main/java/org/killbill/billing/overdue/config/api/OverdueStateSet.java:30-38`

**规则**：状态评估用「账户时区的 LocalDate」作为 `now`（`context.toLocalDate(context.getCreatedDate())`），条件里的时长比较基于该日；而状态施加（写 BlockingState、取消订阅）用带时间的 `effectiveDate`（`context.toLocalDate(effectiveDate)` 取日）。同一账户的评估日期口径必须在账户时区下解释。

## BR-138 取消动作只针对非 ADD_ON 基础订阅

- **类型**: 业务规则
- **同义词**: 取消基础订阅, 排除附加组件, 取消不含 add-on, cancel base subscriptions, exclude ADD_ON
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:316-329`

**规则**：`computeEntitlementsToCancel` 过滤掉 `ProductCategory.ADD_ON` 的 entitlement，只把非附加组件订阅放入待取消列表。源码注释说明 Entitlement 层会自动取消关联的 add-on（引用 killbill issue #94），并提示此实现会漏掉「未来创建的 add-on」。

## BR-139 逾期状态持久化为账户 BlockingState

- **类型**: 业务规则
- **同义词**: 逾期状态持久化, blocking state, 状态存储, persist overdue state, setBlockingState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:221-235`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:139-142`

**规则**：新状态通过 `blockingApi.setBlockingState(new DefaultBlockingState(accountId, BlockingStateType.ACCOUNT, stateName, "overdue-service", blockChange, blockEntitlement, blockBilling, effectiveDate))` 持久化。源码注释强调：**必须最后再存新状态**——因为 entitlement DAO 会发 BlockingTransitionInternalEvent，invoice 会据此反应，需先让含 AUTO_INVOICING_OFF 等最新信息落库。存状态失败包装为 `OVERDUE_CAT_ERROR_ENCOUNTERED`。

## BR-140 clear 路径的状态与通知处理

- **类型**: 业务规则
- **同义词**: 清除逾期, 解除逾期, 恢复账户, clear overdue, clear path
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:185-213`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:144-149`

**规则**：`clear(effectiveDate, account, previousState, clearState, ctx)` 顺序为：写入 clear 状态 → 清除未来通知 → 按需切换 AUTO_INVOICING_OFF（从 block billing 回落则移除标签）→ 构造并投递 `OverdueChangeInternalEvent`（记录 previous→clear 及 unblock 标志）。`OverdueWrapper.clearWithLock` 先查出账户当前状态名再调用它。

## BR-141 内部租户始终使用默认配置

- **类型**: 业务规则
- **同义词**: 内部租户配置, 默认配置回退, internal tenant, default config fallback
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:93-106`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:108-113`

**规则**：当 `tenantRecordId` 等于 `InternalCallContextFactory.INTERNAL_TENANT_RECORD_ID` 时，直接返回默认配置、不进租户缓存；`clearOverdueConfig` 对内部租户也是 no-op。普通租户先查 `TENANT_OVERDUE_CONFIG` 缓存，缓存未命中则返回默认配置；读取抛 IllegalStateException 时转 `OVERDUE_INVALID_FOR_TENANT`。

## BR-142 逾期配置 URI 由 `org.killbill.overdue.uri` 控制

- **类型**: 业务规则
- **同义词**: 逾期配置路径, 配置 URI, org.killbill.overdue.uri, config URI, NoOverdueConfig.xml
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/OverdueProperties.java:25-31`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:58-66`

**规则**：默认逾期配置的位置由配置项 `org.killbill.overdue.uri` 指定，默认值 `NoOverdueConfig.xml`（classpath 或文件系统 URI）。`DefaultOverdueConfigCache` 构造时会先以内建 URI `NoOverdueConfig.xml` 预载默认配置；随后 `loadConfig` 用该配置项覆盖。这解释了「系统默认不催收、要显式指向自定义 XML 才启用」的语义。

## BR-143 状态声明顺序即匹配优先级；无 condition 的状态永不胜出

- **类型**: 业务规则
- **同义词**: 状态声明顺序, 匹配优先级, 无条件下不生效, state declaration order, matching priority, state without condition never matches
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:59-67`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:38-40`

**规则**：`calculateOverdueState(billingState, now)` 严格按 `accountOverdueStates` 数组（即 XML 中 `<state>` 的**文档声明顺序**）从头遍历：
- 只考虑 `overdueState.getConditionEvaluation() != null` 的状态；
- 返回**第一个** `condition.evaluate(...) == true` 的状态；
- 一个都没命中 → 返回内建 clearState。
**关键推论 1**：**未写 `<condition>` 的状态永远不会被选中**（既不会被遍历命中，也不会成为「兜底」；兜底恒为内建 clear）。因此「无条件状态」在配置中只具占位/文档意义。
**关键推论 2**：因为先匹配先赢，配置**必须按「最严重 → 最轻」顺序声明**（严重状态条件更严，放前面；轻状态放后面），否则轻状态会抢赢。代码不作顺序校验，这是纯语义契约。

## BR-144 状态名命名约束（@XmlID 唯一性 + XML ID 合法性 + 50 上限 + 保留名）

- **类型**: 业务规则
- **同义词**: 状态名约束, 命名限制, 状态名唯一, 状态名长度, state name restriction, XmlID, unique state name, max 50
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:47`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:52-54`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:171-178`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:41-52`

**规则**（状态名必须满足全部约束）：
1. **XML ID**：`name` 标注 `@XmlAttribute(name="name", required=true)` 且 `@XmlID`（52-54 行）。作为 XML ID，它必须是合法 NCName（不能含空格/冒号，不能以数字开头），且在配置文档内**唯一**——两个 `<state>` 同名会被 schema/JAXB 判为非法。
2. **长度上限 50**：`MAX_NAME_LENGTH = 50`；`validate` 中超过即追加 `ValidationError("Name of state '%s' exceeds the maximum length of %d")`（171-178 行）。
3. **唯一性由代码兜底**：`findState(name)` 用**精确字符串相等**逐个匹配，同名状态只会命中第一个。
4. **保留名**：`__KILLBILL__CLEAR__OVERDUE_STATE__` 被 `findState` 特判（41-45 行），同名用户状态不可达。
5. 名字影响业务：状态名即持久化到 BlockingState 的状态名，改名会破坏既有数据的可解析性（见 BR-146）。

## BR-145 getFirstState() = 最后一个声明状态；空数组会越界

- **类型**: 业务规则
- **同义词**: 首状态, 入门级状态, 最后声明, getFirstState, first state, entry level overdue state, empty states array
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:87-95`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:109-113`

**规则**：`getFirstState()` 返回 `getStates()[size()-1]`，即数组**最后一个**元素。
- 由 BR-143 的「最严重在前」契约可知，最后一个元素是**最轻/入门级**状态（如 OD1）。
- 该值在 applicator 里用于判断「尚未进入首状态但有欠费仍需复检」：`conditionForNextNotfication = !next.isClearState() || (firstOverdueState != null && billingState.getDateOfEarliestUnpaidInvoice() != null)`（109-113 行）。
**边界行为**：若状态数组为空，`size()-1 = -1`，`getStates()[-1]` 抛 `ArrayIndexOutOfBoundsException`。实际运行中由 `OverdueWrapper.refresh` 的 `size() < 1` 早退（BR-170）以及 `OverdueWrapperFactory` 返回空状态集共同规避，application 层不会以空集调用 `getFirstState()`。

## BR-146 配置 isClearState 标志不决定清算；内建 clearState 是唯一出口

- **类型**: 业务规则
- **同义词**: isClearState 标志, 清算标志, 内建清算状态, configured isClearState flag, built-in clear state, clear state resolution
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:37-57`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:69-85`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`

**规则**：`DefaultOverdueStatesAccount` **不**从其配置状态里挑选 `isClearState=true` 的状态作为清算状态。清算状态恒为状态集内建的 `clearState`（BR-143/TERM-029）：
- `calculateOverdueState` 未命中时返回内建 clearState；
- `findState` 对保留名特判返回内建 clearState；
- `getClearState()` 直接返回内建 clearState。
**用户配置 `<isClearState>true</isClearState>` 的真实影响**：仅当该状态**自身被 condition 命中**而成为 next 时，`nextOverdueState.isClearState()` 为真，从而影响 `OverdueStateApplicator.getReevaluationInterval`（用状态集级 `initialReevaluationInterval` 而非状态级 `autoReevaluationInterval`）以及「是否清空未来通知」的判断（applicator 123-125 行）。它**不会**让该状态成为兜底状态。
**校验死分支**：`DefaultOverdueStateSet.validate` 里对 `CAT_MISSING_CLEAR_STATE` 的检查（78-80 行）在现状下不可达——因为 `getClearState()` 从不抛异常。

## BR-147 时间条件为「含等于」（inclusive）：triggerDate <= now

- **类型**: 业务规则
- **同义词**: 时间条件含等于, 边界包含, 账龄包含当天, inclusive time condition, triggerDate <= now, timeSinceEarliestUnpaidInvoiceEqualsOrExceeds
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:69-84`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:56-57`

**规则**：`timeSinceEarliestUnpaidInvoiceEqualsOrExceeds` 的判定为：
1. 仅当配置了该子条件**且**账户有最早未付发票日期时，计算 `triggerDate = dateOfEarliestUnpaidInvoice.plus(duration.toJodaPeriod())`。
2. 条件为真当且仅当 `!triggerDate.isAfter(now)`，即 **`triggerDate <= now`（含等于，inclusive）**。
3. 若账户无最早未付发票日期（无未付发票），该子条件**为假**（源码注释 `// no date => no unpaid invoices`，72 行）。
**口径**：`now` 来自账户时区的 `LocalDate`（applicator 传入 `context.toLocalDate(context.getCreatedDate())`）；`dateOfEarliestUnpaidInvoice` 是发票日期（非到期日 dueDate）。到触发当天即命中。

## BR-148 时间/间隔单位仅 DAYS/WEEKS/MONTHS/YEARS；UNLIMITED 非法

- **类型**: 业务规则
- **同义词**: 时间单位, 支持的单位, 无限期非法, supported time units, UNLIMITED illegal, DAYS WEEKS MONTHS YEARS
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:57-118`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:119-125`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStatesAccount.java:51-57`

**规则**：`DefaultDuration` 在条件与间隔中均只支持四种 `TimeUnit`：`DAYS`、`WEEKS`、`MONTHS`、`YEARS`（分别映射 Joda `withDays/withWeeks/withMonths/withYears`）。
- `UNLIMITED` → `toJodaPeriod()/addToLocalDate()/addToDateTime()` 抛 `IllegalStateException`（74/95/116 行）。
- 作为 **autoReevaluationInterval**：`UNLIMITED` 与 `number==0`、`autoReevaluationInterval==null` 一起被判为非法，抛 `OverdueApiException(OVERDUE_NO_REEVALUATION_INTERVAL)`（DefaultOverdueState 121-123 行）。
- 作为 **initialReevaluationInterval**：`UNLIMITED`/`number==0`/null → `getInitialReevaluationInterval()` 返回 `null`（DefaultOverdueStatesAccount 53-55 行），即不安排通知。
- `validate()` 对 unit/number 组合**无校验**（DefaultDuration 121-124 行仅 TODO）。即「UNLIMITED 配合 number」不会被配置校验拦下，而是在使用时爆炸。

## BR-149 时间条件缺省 number=-1 会立即命中（反直觉默认）

- **类型**: 业务规则
- **同义词**: 缺省数字, 默认-1, 立即命中, default number -1, missing number, immediate trigger, duration default
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:41-45`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultDuration.java:99-118`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:71-74`

**规则**：`DefaultDuration.number` 的 Java 默认值是 `-1`。若配置只写 `<unit>DAYS</unit>` 而漏写 `<number>`：
- `toJodaPeriod()` 返回 `new Period().withDays(-1)`（即**负一天**周期）；
- 时间条件 `triggerDate = dateOfEarliestUnpaidInvoice.plus(-1 day)`，通常早于 `now`，于是条件**立即为真**；
- 同样的 -1 若出现在 `autoReevaluationInterval`，会安排一个「过去时间」的通知，等价于立即触发下一次复评。
**仅当** `number == null`（外部反序列化显式写入 null）且 unit 非 UNLIMITED 时，`toJodaPeriod()` 才返回恒等 `new Period()`（102 行）——注意这与「-1」是两个不同分支，默认路径走的是 -1。**结论：配置时间条件/间隔时必须显式写 `<number>`，正数才有预期语义。**

## BR-150 数值条件：发票数量用 >=，余额用 BigDecimal.compareTo（scale 无关）

- **类型**: 业务规则
- **同义词**: 数量条件, 余额条件, 数值阈值, numberOfUnpaidInvoicesEqualsOrExceeds, totalUnpaidInvoiceBalanceEqualsOrExceeds, >=, BigDecimal compareTo
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:50-54`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:76-78`

**规则**：两个「EqualsOrExceeds」数值子条件均为**含等于（inclusive）**：
- 数量：`numberOfUnpaidInvoicesEqualsOrExceeds == null || state.getNumberOfUnpaidInvoices() >= 该值`（int 比较）。
- 余额：`totalUnpaidInvoiceBalanceEqualsOrExceeds == null || 阈值.compareTo(state.getBalanceOfUnpaidInvoices()) <= 0`，即 `state.balance >= 阈值`。
**余额比较细节**：用 `BigDecimal.compareTo`（78 行）而非 `equals`，因此**不受 scale 影响**（`100`、`100.00`、`1E2` 视为相等）；`compareTo<=0` 表示阈值不超过实际余额。
**边界**：`>=` 含等于，即数量恰好等于阈值、余额恰好等于阈值时命中。字段本身可为 null（未配置则该子条件恒真）。

## BR-151 控制标签条件仅限 ControlTagType 枚举，按 tagDefinitionId 比对

- **类型**: 业务规则
- **同义词**: 控制标签条件类型, 标签枚举限制, controlTagInclusion, controlTagExclusion, ControlTagType enum, tagDefinitionId match
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:63-67`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:96-112`

**规则**：`controlTagInclusion` / `controlTagExclusion` 的 Java 类型是 `org.killbill.billing.util.tag.ControlTagType`（**枚举**），因此：
- 配置里只能使用平台**预定义控制标签**，不能引用自定义描述性标签（DescriptiveTag）。例如 `OVERDUE_ENFORCEMENT_OFF`、`AUTO_INVOICING_OFF`。
- 匹配方式是**按定义 id**：`t.getTagDefinitionId().equals(tagType.getId())`（98、107 行）。即比较的是账户标签的 `tagDefinitionId` 是否等于该控制标签类型的固定 id。
- `controlTagInclusion`：账户标签集合中**存在**该 id → 真（`isTagIn`）；`controlTagExclusion`：存在该 id → **立即假**（`isTagNotIn` 返回 false，一票否决该状态）。
- 两个字段均只采用**单个** `ControlTagType`（无数组），与 `responseForLastFailedPayment` 的多值不同。
**对照**：`OverdueListener` 判断标签事件时用的是 `event.getTagDefinition().getName().equals(ControlTagType.X.toString())`（按名字），而条件评估用的是 `tagDefinitionId`（按 id）——两套口径不同。

## BR-152 apply 动作执行顺序（通知 → no-op → 取消 → 标签 → 存状态 → 事件）

- **类型**: 业务规则
- **同义词**: 动作执行顺序, apply 顺序, 施加顺序, apply action order, execution order, side effects order
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:104-158`

**规则**：`apply(...)` 的副作用顺序**固定**如下：
1. 计算 `firstOverdueState`/`conditionForNextNotfication`，**先**调度或清除复评通知（109-125 行）。
2. 若 `previous.name.equals(next.name)` → **直接 return**，后续动作全部跳过（127-132 行）。
3. `cancelSubscriptionsIfRequired`（按策略取消订阅，134 行）。
4. `avoid_extra_credit_by_toggling_AUTO_INVOICE_OFF`（切换 AUTO_INVOICING_OFF 标签，137 行）。
5. `storeNewState`（**最后**写 BlockingState，142 行；源码注释解释：entitlement DAO 会发 BlockingTransitionInternalEvent，invoice 需先看到含标签的最新状态）。
6. `createOverdueEvent` + `bus.post`（146-157 行）。
**反直觉点**：通知调度发生在 no-op 判定**之前**——即使状态名不变，也会按当前间隔重新调度通知；而 3~6 全被跳过。

## BR-153 状态名不变 = no-op：跳过取消/标签/持久化/事件

- **类型**: 业务规则
- **同义词**: 状态同名无操作, 幂等短路, no-op on same state name, name equality short circuit
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:127-132`

**规则**：`apply` 中唯一的变化判定是 `previousOverdueState.getName().equals(nextOverdueState.getName())`（127 行）。
- 相同 → log.debug 后 `return`；**不**取消订阅、**不**切换 AUTO_INVOICING_OFF、**不**写 BlockingState、**不**发 `OverdueChangeInternalEvent`。
- 不同 → 继续执行全部动作。
**推论（精确）**：判定只比较**名字**，不比较状态的其它属性。因此若运营只改了某状态的 `blockChanges`/`externalMessage`/`subscriptionCancellationPolicy` 而**状态名保持不变**，已有账户**不会**被重新施加动作；配置变更只对「未来发生状态名迁移」的账户生效。这解释了为何修改配置后需要账户发生真实状态迁移才能观察副作用。

## BR-154 clear 路径动作顺序（先写 clear 状态，与 apply 相反）

- **类型**: 业务规则
- **同义词**: clear 顺序, 清算动作顺序, clear action order, clear path order, store clear first
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:185-213`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:144-149`

**规则**：`clear(effectiveDate, account, previousOverdueState, clearState, ctx)` 的副作用顺序：
1. `storeNewState(..., clearState, ...)` — **先**写 clear 状态（189 行）。
2. `clearFutureNotification` — 清空该账户所有未来复评通知（191 行）。
3. `avoid_extra_credit_by_toggling_AUTO_INVOICE_OFF` — 从 block billing 回落则移除 `AUTO_INVOICING_OFF`（194 行）。
4. 构造并投递 `OverdueChangeInternalEvent`（previous→clear，201-212 行）。
**与 apply 的对比**：apply 把 `storeNewState` 放在**最后**（注释要求 BlockingTransition 前先落库标签），而 clear 把它放在**最前**——两条路径顺序不对称，是理解「清空 vs 迁移」副作用差异的关键。
**入口**：`OverdueWrapper.clearWithLock` 先由当前 BlockingState 名解析出 previousOverdueState，再调用本方法（144-149 行）。

## BR-155 blockBilling 转移判定基于 disableEntitlement 标志，而非状态名

- **类型**: 业务规则
- **同义词**: 计费阻断转移, blockBilling 判定, 转移布尔, block/unblock billing transition, disableEntitlement flag
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:255-273`

**规则**：三个布尔辅助函数定义了转移语义：
- `blockChanges(s) = s.isBlockChanges() || s.isDisableEntitlementAndChangesBlocked()`
- `blockBilling(s) = s.isDisableEntitlementAndChangesBlocked()`
- `blockEntitlement(s) = s.isDisableEntitlementAndChangesBlocked()`
- `isBlockBillingTransition(prev,next) = !blockBilling(prev) && blockBilling(next)`
- `isUnblockBillingTransition(prev,next) = blockBilling(prev) && !blockBilling(next)`
**推论**：是否触发 AUTO_INVOICING_OFF 切换、事件里的 `isBlockedBilling`/`isUnblockedBilling`，**只取决于 `disableEntitlementAndChangesBlocked`**，与状态的严重度、名字、`blockChanges` 无关。两个状态若都是 `disableEntitlement=true`，它们之间迁移不算 block/unblock billing 转移。

## BR-156 AUTO_INVOICING_OFF 仅在 block/unblock billing 转移时切换

- **类型**: 业务规则
- **同义词**: 自动开票标签切换, AUTO_INVOICING_OFF 开关时机, toggle timing, avoid extra credit, tag transition
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:176-183`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:237-253`

**规则**：
- 若 `isBlockBillingTransition` → `tagApi.addTag(accountId, ObjectType.ACCOUNT, ControlTagType.AUTO_INVOICING_OFF.getId(), ctx)`（237-243 行），避免继续开票产生多余信用。
- 若 `isUnblockBillingTransition` → `tagApi.removeTag(...)`；若标签不存在，捕获 `TagApiException` 且仅当错误码 `TAG_DOES_NOT_EXIST` 时忽略，其它错误包装成 `OverdueApiException`（245-253 行）。
- 其余情况（无 block billing 状态变化）**完全不触碰**该标签。
**与 BR-153/BR-155 的关系**：该切换只在「状态名变化」后执行，且只在 `disableEntitlement` 导致 blockBilling 翻转时发生。clear 路径同样调用它（从 block billing → clear 会移除标签）。

## BR-157 复评通知基期 = effectiveDate；间隔来源随 next 是否 clear 切换

- **类型**: 业务规则
- **同义词**: 复评基期, 下次检查时间, 事件时间, notification base date, effectiveDate plus interval, interval source
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:109-125`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:275-283`

**规则**：
- **何时安排**：`conditionForNextNotfication = !next.isClearState() || (firstOverdueState != null && billingState != null && billingState.getDateOfEarliestUnpaidInvoice() != null)`。即「next 非 clear」**或**「next 为 clear 但存在最早未付发票日期」。
- **间隔取值**（`getReevaluationInterval` 160-174）：
  - `next.isClearState()` → 状态集级 `overdueStateSet.getInitialReevaluationInterval()`（类型 `Period`）。
  - 非 clear → `nextOverdueState.getAutoReevaluationInterval().toJodaPeriod()`（**目标状态的**状态级间隔）。
  - 间隔为 `null` → 记 `debug`「missing InitialReevaluationInterval…NOT inserting notification」并**不插入**。
- **基期**：`createFutureNotification` 使用 `effectiveDate.plus(reevaluationInterval)`（121 行），即**事件生效时间**，而非 `context.getCreatedDate()`（注意：条件评估用的是 CreatedDate 的 LocalDate，见 BR-167）。
- **清空条件**：`else if (nextOverdueState.isClearState())` → `clearFutureNotification`（123-125 行），删除该账户所有未来 check 通知（按 accountRecordId/tenantRecordId 检索）。
- **间隔与「是否时间驱动」无关**：即使条件没有任何时间项，只要 next 非 clear，也会按其 `autoReevaluationInterval` 定时复评。

## BR-158 非法复评间隔：仅 OVERDUE_NO_REEVALUATION_INTERVAL 被吞成 null

- **类型**: 业务规则
- **同义词**: 复评间隔异常, 无间隔错误码, invalid interval handling, OVERDUE_NO_REEVALUATION_INTERVAL swallow, OverdueException
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:119-125`

**规则**：`getReevaluationInterval` 捕获 `OverdueApiException` 后：
- 若 `e.getCode() == ErrorCode.OVERDUE_NO_REEVALUATION_INTERVAL.getCode()` → 返回 `null`（applicator 上游据此不插入通知）。
- **其它任何错误码** → 包装成 `OverdueException(e)` 抛出，中止本次 apply。
`OVERDUE_NO_REEVALUATION_INTERVAL` 由 `DefaultOverdueState.getAutoReevaluationInterval()` 在 `null`/`UNLIMITED`/`number==0` 时抛出（121-123 行）。
**注意**：clear 分支的 `getInitialReevaluationInterval()` **不抛异常**——它在 `DefaultOverdueStatesAccount` 内直接返回 null（见 BR-148），所以该 catch 的错误码分支主要服务于非 clear 状态。

## BR-159 check 队列去重：保留最早；新到期时间 <= 已有最早时新通知胜出

- **类型**: 业务规则
- **同义词**: check 队列去重, 保留最早通知, 到期时间比较, check queue dedup, keep earliest, tie handling
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueCheckPoster.java:48-85`

**规则**：`OverdueCheckPoster.cleanupFutureNotificationsFormTransaction`（结果按 effectiveDate **升序**）：
- 只看**第 0 条**（最早）`cur`：
  - 若 `cur.getEffectiveDate().isBefore(futureNotificationTime)` → **不插入**新通知，并删除第 1 条起的其余未来通知（`minIndexToDeleteFrom=1`）。即已有更早的，保留它。
  - 否则（新时间 <= 已有最早，含**相等**）→ **插入**新通知，并删除全部已有通知（`minIndexToDeleteFrom=0`）。
- 返回值 `shouldInsertNewNotification` 决定是否 `recordFutureNotificationFromTransaction`。
**边界**：到期时间**相等**时新通知胜出（旧被删）。所有删除与插入在**同一事务**内完成（`DefaultOverduePosterBase` 61-88 行）。
**最终效果**：check 队列中每账户至多保留一条、且是调度时刻认为最早的那条。

## BR-160 async 队列去重：已有任意未来通知则跳过（REFRESH/CLEAR 混排不确定）

- **类型**: 业务规则
- **同义词**: async 队列去重, 有则跳过, 刷新清除混排, async queue dedup, skip if any, nondeterministic REFRESH CLEAR
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusPoster.java:47-57`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:168-177`

**规则**：`OverdueAsyncBusPoster.cleanupFutureNotificationsFormTransaction` 直接返回 `Iterables.size(futureNotifications) == 0`：
- 该账户**已有任意未来通知** → **跳过**插入新通知（不区分该通知是 REFRESH 还是 CLEAR，也不比较时间）。
- 无任何未来通知 → 插入。
**源码自述的近似性**（52-54 行注释）：可能出现「已有 REFRESH 又来了 CLEAR」却插入失败的情况；若真发生，说明逾期状态变化极快、行为本就非确定。
**调度时间**：`OverdueListener.insertBusEventIntoNotificationQueue` 以 `callContext.getCreatedDate()` 作为未来通知时间（177 行）。**对照**：check 队列由 applicator 以 `effectiveDate+interval` 调度（BR-157），两者基期不同。

## BR-161 订阅取消：范围（非 ADD_ON）、查询上下文与批处理

- **类型**: 业务规则
- **同义词**: 取消范围, 订阅取消实现, 非附加组件, cancellation scope, non ADD_ON, batch cancel, lastActiveProductCategory
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:285-329`

**规则**：`cancelSubscriptionsIfRequired` 的完整行为：
1. 若策略为 `NONE` → 直接 return，不做任何查询（286-288 行）。
2. 用 `internalCallContextFactory.createCallContext(context)` 生成**用户 CallContext**，查询 `entitlementApi.getAllEntitlementsForAccountId(account.getId(), callContext)`（290、317 行）。
3. 过滤：保留 `!ProductCategory.ADD_ON.equals(entitlement.getLastActiveProductCategory())` 的订阅（`computeEntitlementsToCancel`，320-328 行）。
4. 以**批量列表**调用 `entitlementInternalApi.cancel(toBeCancelled, context.toLocalDate(effectiveDate), actionPolicy, Collections.emptyList(), context)`（307 行），插件属性为空列表，使用 internal context。
**注意**：过滤依据是 `getLastActiveProductCategory()`；源码注释承认会漏掉「未来创建的 add-on」（323 行），并引用 killbill#94 说明 entitlement 层会级联取消其 add-on。

## BR-162 取消策略 → BillingActionPolicy 映射与未知值异常

- **类型**: 业务规则
- **同义词**: 策略映射, 取消动作映射, cancellation policy mapping, IMMEDIATE, END_OF_TERM, IllegalStateException
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:292-302`

**规则**：进入新状态且策略非 NONE 时：
- `END_OF_TERM` → `BillingActionPolicy.END_OF_TERM`
- `IMMEDIATE` → `BillingActionPolicy.IMMEDIATE`
- `default`（含 `NONE` 以外的未知值，理论上枚举已穷尽）→ `throw new IllegalStateException("Unexpected OverdueCancellationPolicy " + policy)`
**生效日**：取消使用 `context.toLocalDate(effectiveDate)`（按账户时区取日），而非 `context.getCreatedDate()`。
**触发时机**：仅在状态名变化后（BR-153）执行；取消前先做 BR-161 的范围过滤。

## BR-163 全局锁：ACCNT_INV_PAY + 账户 UUID，最多 50 次，失败以 reschedule 间隔重排

- **类型**: 业务规则
- **同义词**: 逾期锁键, 锁重试次数, 重排间隔, global lock key, ACCNT_INV_PAY, account UUID, MAX_LOCK_RETRIES 50, reschedule interval on lock
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:51-56`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:89-107`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:129-142`

**规则**：
- `refresh` 与 `clear` 都调用 `locker.lockWithNumberOfTries(LockerType.ACCNT_INV_PAY.toString(), overdueable.getId().toString(), MAX_LOCK_RETRIES)`。
- 锁**键是账户 UUID（`Account.getId()`）**，而非 accountRecordId；`MAX_LOCK_RETRIES` 是硬编码常量 `50`（源码注释「Should we introduce a config?」）。
- 获取失败（`LockFailedException`）→ 抛 `QueueRetryException(e, TimeSpanConverter.toListPeriod(overdueConfig.getRescheduleIntervalOnLock(context)))`，把**配置项 `rescheduleIntervalOnLock`** 转成重排周期（由 killbill 属性配置，不在 overdue 模块内）。
- 锁在 `finally` 中释放（`if (lock != null) lock.release()`）。
**与通知键的对照**：通知按 `accountRecordId + tenantRecordId` 检索/去重（ENT-030），锁按**账户 UUID**；两者键口径不同。

## BR-164 配置加载两阶段与失败降级（保留内建默认，Overdue system disabled）

- **类型**: 业务规则
- **同义词**: 配置加载两阶段, 加载失败降级, 保留内建默认, config bootstrap, load failure fallback, Overdue system disabled
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:53-66`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:68-86`, `overdue/src/main/java/org/killbill/billing/overdue/service/DefaultOverdueService.java:91-101`

**规则**：
1. **阶段一（构造期）**：无条件加载 classpath `NoOverdueConfig.xml` 得到 `defaultOverdueConfig`；若失败则 `new DefaultOverdueConfig()`（空 accountOverdueStates → 状态数组为空）并记 `error`。
2. **阶段二（service LOAD_CATALOG）**：`DefaultOverdueService.loadConfig` 调 `loadDefaultOverdueConfig(properties.getConfigURI())`；`configURI` 为 null/空或解析抛异常 → `missingOrCorruptedDefaultConfig=true`，**不覆盖**当前 `defaultOverdueConfig`（即仍保留阶段一的内建 NoOverdue 配置），仅 `log.warn("Overdue system disabled: unable to load the overdue config from uri='{}'")`，`isConfigLoaded` 保持 false。
**关键结论**：配置加载失败**不会**清空为 null，而是**回退到阶段一的内建默认（等价于不催收）**；「禁用」只是日志语义，运行期行为即 clear。`loadDefaultOverdueConfig` 内部自行捕获所有异常，因此 service 侧的 `catch(OverdueApiException)` 实为防御性死分支。

## BR-165 租户配置读取：内部租户恒默认、未命中回退默认、非法转 OVERDUE_INVALID_FOR_TENANT

- **类型**: 业务规则
- **同义词**: 租户配置读取, 内部租户特判, 回退默认, tenant config read, internal tenant, fallback default, OVERDUE_INVALID_FOR_TENANT
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:93-113`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:115-132`

**规则**：
- `tenantRecordId == InternalCallContextFactory.INTERNAL_TENANT_RECORD_ID` → 直接返回 `defaultOverdueConfig`，**不进租户缓存**；`clearOverdueConfig` 对内部租户也 no-op。
- 普通租户：`cacheController.get(tenantRecordId, cacheLoaderArgument)`；返回 `null` → 回退 `defaultOverdueConfig`。
- 缓存加载（解析租户 XML）抛 `IllegalStateException` → `OverdueApiException(OVERDUE_INVALID_FOR_TENANT, tenantRecordId)`。
- 加载器 `LoaderCallback` 把 XML 解析失败包装为 `OverdueApiException(OVERDUE_INVALID_FOR_TENANT, "Problem encountered loading overdue config ", e)`。
**业务含义**：一个租户的坏配置只影响该租户读取（抛异常），不会污染其他租户或默认配置。

## BR-166 上传逾期配置不即时校验，错误延迟到读取时暴露

- **类型**: 业务规则
- **同义词**: 上传不校验, 延迟校验, 延迟失败, upload without validation, deferred validation, lazy parse
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:66-89`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:115-132`

**规则**：
- `uploadOverdueConfig(String overdueXML, CallContext)` 的步骤仅为：查旧值非空则 `deleteTenantKey("OVERDUE_CONFIG")` → `addTenantKeyValue("OVERDUE_CONFIG", overdueXML)` → `overdueConfigCache.clearOverdueConfig(ctx)`。**全程不解析、不校验 XML**（无 XMLLoader 调用）。
- `uploadOverdueConfig(OverdueConfig, CallContext)` 只是先 `XMLWriter.writeXML` 序列化，再走上面的 String 版本。
- 因此：上传**成功返回**不代表配置合法；非法 XML 会在后续**读取/缓存加载**时抛 `OVERDUE_INVALID_FOR_TENANT`（BR-165）。
**对照**：主流程的 `DefaultOverdueState.validate`（名字长度等）只在 XMLLoader 解析时触发，同样属于「读取期校验」。

## BR-167 父账户委派：仅计算上下文用父，被评估账户对象仍是子

- **类型**: 业务规则
- **同义词**: 委派支付, 父上下文计算, 账户对象仍为子, payment delegation, parent context, child account object
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:151-159`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:179-203`

**规则**：当账户 `getParentAccountId() != null` 且 `isPaymentDelegatedToParent()`：
- `billingState(context)` 用 `internalCallContextFactory.createInternalTenantContext(parentAccountId, context)` 与 `createInternalCallContext(parentRecordId, context)` 构造**父账户上下文**；
- 但调用 `billingStateCalcuator.calculateBillingState(overdueable, parentAccountContext)` 时传入的**仍是子账户对象** `overdueable`。
**精确含义**：聚合的是「子账户的未付发票」（以子账户 id 查询），而**账龄/时间的「当前日」与租户口径来自父账户上下文**。即委派只改变上下文的 accountRecordId/时区基准，不改变查询主体。
**刷新级联**：入队 REFRESH/CLEAR 时，若向父委派则父账户也入队；并遍历子账户中 `isPaymentDelegatedToParent()` 者一并入队（179-203 行）。

## BR-168 BillingStateCalculator 的日期口径、排序 tie-break 与余额求和

- **类型**: 业务规则
- **同义词**: 计费状态计算细节, 日期口径, 排序打破平局, billingState calculation, CreatedDate, tie break hashCode, sumBalance
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:47-54`, `overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:67-108`

**规则**：
- 未付发票查询：`invoiceApi.getUnpaidInvoicesByAccountId(accountId, context.toLocalDate(context.getCreatedDate()), context)`（104 行）——传入的日期是 **`context.getCreatedDate()` 的账户时区 LocalDate**，不是 `clock.getUTCToday()`。
- 排序比较器 `UNPAID_INVOICES_FOR_ACCOUNT_COMPARATOR`：先比 `getInvoiceDate()`；**日期相同**时用 `i1.hashCode() - i2.hashCode()` 作为「consistent (arbitrary) resolution」（50-52 行）。该 tie-break 在同一 JVM 内稳定，但**跨 JVM/对象重排不保证一致**。
- 余额合计 `sumBalance`：`BigDecimal.ZERO` 起累加每张 `invoice.getBalance()`（95-101 行）；因此余额可为**负**（存在信用/退款）。
- `earliest`：`unpaidInvoices.first()` 捕获 `NoSuchElementException` 返回 null（87-93 行）→ 无未付发票时 `dateOfEarliestUnpaidInvoice=null`。

## BR-169 监听器门控：BusDispatcherOptimizer + 标签 objectType 精确匹配

- **类型**: 业务规则
- **同义词**: 监听器门控, 分发优化器, 标签对象类型, listener gating, BusDispatcherOptimizer shouldDispatch, objectType match
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-121`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-157`

**规则**：每个订阅方法（6 个事件类型）**首先**判断 `busDispatcherOptimizer.shouldDispatch(event)`，为 false 则完全忽略（不查配置、不入队）。
- 标签事件还要求**对象类型精确匹配**：
  - `OVERDUE_ENFORCEMENT_OFF` 且 `event.getObjectType() == ObjectType.ACCOUNT` → CLEAR（新增）/ REFRESH（删除）。
  - `WRITTEN_OFF` 且 `event.getObjectType() == ObjectType.INVOICE` → REFRESH（新增/删除），并用 `nonEntityDao.retrieveIdFromObject(searchKey1, ObjectType.ACCOUNT, objectIdCacheController)` 把发票反查为账户 id。
- 标签判定用的是 `event.getTagDefinition().getName().equals(ControlTagType.X.toString())`（**按枚举名字符串**）。
- 其余事件（发票创建/调整、支付信息/错误）直接 `insertBusEventIntoNotificationQueue(event.getAccountId(), event)` → REFRESH。
**结论**：不满足 objectType 的标签事件（如给订阅打 OVERDUE_ENFORCEMENT_OFF）不会触发任何逾期处理。

## BR-170 refresh 早退：配置状态数 < 1 直接返回

- **类型**: 业务规则
- **同义词**: 刷新早退, 空配置不处理, refresh early return, no configuration, size < 1
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:89-92`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapperFactory.java:95-119`

**规则**：`OverdueWrapper.refresh` 第一行判断 `if (overdueStateSet.size() < 1) return;`——**取锁之前**即返回，不计算、不加锁、不写状态。
`OverdueWrapperFactory.getOverdueStateSet` 在配置描述为 null、或其 `accountOverdueStates` 为 null 时，返回一个**匿名空状态集**（`getStates()` 返回空数组、`getInitialReevaluationInterval()` 返回 null），其 `size()==0` 正好触发早退。
**与 clear 的差异**：`clear(...)` **没有** size<1 早退（129-142 行）——即使配置为空也可执行清算（写 clear 状态、清通知）。

## BR-171 初始阶段不能是 EVERGREEN

- **类型**: 业务规则
- **同义词**: 初始阶段约束, 起始阶段不能常青, initial phase evergreen, 阶段顺序规则, phase ordering
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:304-310`

**规则**：计划的每个 `initialPhase`（初始阶段）不得为 `PhaseType.EVERGREEN`；否则目录校验报错 `Initial Phase %s of plan %s cannot be of type EVERGREEN`。

**含义**：EVERGREEN 只能作为计划最后一个阶段（finalPhase），保证计划有明确的阶段性结构。

## BR-172 最终阶段不能是 TRIAL 或 DISCOUNT

- **类型**: 业务规则
- **同义词**: 最终阶段约束, 结束阶段不能试用, final phase trial, final phase discount, 阶段顺序规则
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:313-319`

**规则**：计划的 `finalPhase`（最终阶段）不得为 `PhaseType.TRIAL` 或 `PhaseType.DISCOUNT`；否则校验报错 `Final Phase %s of plan %s cannot be of type %s`。

**含义**：试用/折扣阶段只能出现在中间，最终阶段必须是 FIXEDTERM 或 EVERGREEN。

## BR-173 阶段必须至少定义一种计费项

- **类型**: 业务规则
- **同义词**: 阶段必填项, 阶段计价完整性, phase needs pricing, 空阶段校验
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:176-180`

**规则**：若一个阶段同时没有 `fixed`、没有 `recurring` 且 `usages` 为空，则校验失败，报错 `Phase %s of plan %s need to define at least either a fixed or recurrring or usage section.`。

## BR-174 阶段名与计划名互推规则

- **类型**: 业务规则
- **同义词**: 阶段命名, 计划名解析, phase name, plan name from phase, 阶段名后缀
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:104-115`

**规则**：
- 阶段名 = `planName + "-" + phaseType.toLowerCase()`。
- 反向解析：遍历 `PhaseType.values()`，看阶段名是否以某类型小写结尾，是则去掉「类型长度+1」个字符得到计划名；否则抛 `CAT_BAD_PHASE_NAME`。

**例外**：若计划名本身以某个 phase type 单词结尾，反向解析可能产生歧义（源码按 values() 顺序取首个匹配）。

## BR-175 EVERGREEN 必须 UNLIMITED，非 EVERGREEN 不得 UNLIMITED

- **类型**: 业务规则
- **同义词**: 常青阶段无限时长, evergreen unlimited, 阶段时长约束, 无限期阶段
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:290-310`

**规则**：遍历计划全部阶段：若阶段类型为 `EVERGREEN` 但其 `duration.unit != UNLIMITED`，报错「must have duration as UNLIMITED」；若阶段类型非 `EVERGREEN` 但其 `duration.unit == UNLIMITED`，报错「must not have duration as UNLIMITED」。

## BR-176 UNLIMITED 时长与 number 互斥

- **类型**: 业务规则
- **同义词**: 时长数量校验, unlimited 无数量, duration number, 时长必填
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultDuration.java:106-123`

**规则**：`unit == UNLIMITED` 时 `number` 必须为缺省（-1），否则报「Duration can only have 'UNLIMITED' unit if the number is omitted」；`unit != UNLIMITED` 时 `number` 必须给出，否则报「Finite Duration must have a well defined length」。

## BR-177 周期费与计费周期一致性

- **类型**: 业务规则
- **同义词**: 循环费周期校验, recurring billing period, 周期费必填周期, no billing period
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultRecurring.java:90-111`

**规则**：
- 有 `recurringPrice` 时必须有 `billingPeriod` 且不得为 `NO_BILLING_PERIOD`。
- 没有 `recurringPrice` 时 `billingPeriod` 必须是 `NO_BILLING_PERIOD`。
- 违反时报「has a recurring price but no billing period」或「has no recurring price but does have a billing period」。

## BR-178 价格不得为负且币种必须受支持

- **类型**: 业务规则
- **同义词**: 价格校验, 负价格, 非法币种, negative price, unsupported currency, 价格合法性
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:107-127`

**规则**：对每个 `Price`：
- 其 `currency` 不在目录 `supportedCurrencies` 中 → 校验错误 `Unsupported currency: <CUR>`。
- 其 `value < 0.0` → 校验错误 `Negative value for price in currency: <CUR>`。
- 若 `value` 为 null（抛 `CurrencyValueNull`），跳过负值检查。

## BR-179 指定币种无价格时抛 CAT_NO_PRICE_FOR_CURRENCY

- **类型**: 业务规则
- **同义词**: 币种缺价, 无报价币种, no price for currency, 价格缺失
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:88-100`

**规则**：`InternationalPrice` 无任何 price 时，视为所有币种价格 = 0（返回 `BigDecimal.ZERO`）；若有 price 列表但找不到请求的币种，则抛 `CatalogApiException(CAT_NO_PRICE_FOR_CURRENCY, currency)`。

## BR-180 用量各模式的必填结构

- **类型**: 业务规则
- **同义词**: 用量校验, 预付容量, 预付消耗, 后付阶梯, usage validation, IN_ADVANCE, IN_ARREAR, limits, blocks, tiers, 用量段校验, 目录校验, usage section validation, in advance limits, in arrears tiers
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:212-229`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:147-159`

**规则**：
- `IN_ADVANCE + CAPACITY`：必须定义 `limits`，否则报错。
- `IN_ADVANCE + CONSUMABLE`：必须定义 `blocks`，否则报错。
- `IN_ARREAR`：必须定义 `tiers`，否则报错。
- 在 Tier 级别：`IN_ARREAR + CAPACITY` 需 limits，`IN_ARREAR + CONSUMABLE` 需 blocks（校验信息挂在 DefaultUsage 上）。

**关联**：这些是目录对「用量类型 + 计费模式」组合的合法性约束，间接规定了对应用量记录应携带哪些单位类型。

## BR-181 Limit 的上下限判定

- **类型**: 业务规则
- **同义词**: 用量限制, 上限下限, limit min max, complies with limits, 超限
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultLimit.java:84-105`

**规则**：
- 校验：`max` 与 `min` 都有值时，`max < min` 报错「max must be greater than min」。
- 判定：`maxHasValue && value > max` → 不通过（false）；否则当 `minHasValue && value > min` 也不通过，其余通过。缺省值 -1 视为「未设置」。

**注意（源码疑点）**：`min` 判定使用 `value.compareTo(min) <= 0`（即 value > min 不通过），语义上更像是「未超过 min」；业务使用时需与官方文档核对。

## BR-182 effectiveDateForExistingSubscriptions 不得早于目录生效日

- **类型**: 业务规则
- **同义词**: 存量订阅生效日, existing subscriptions date, 目录生效日约束, price effective date
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:286-293`

**规则**：若计划设置了 `effectiveDateForExistingSubscriptions` 且它早于目录的 `effectiveDate`，则校验报错「Price effective date %s is before catalog effective date '%s'」。该字段用于控制计划变更对存量订阅生效的时点。

## BR-183 纯用量计划可不设 recurringBillingMode

- **类型**: 业务规则
- **同义词**: 纯用量计划, recurring billing mode 缺省, usage only plan, 计费模式继承
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:79-81`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:276-278`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:295-298`

**规则**：若计划的 recurring billing period 为 `NO_BILLING_PERIOD`（纯用量计划），可缺省 `recurringBillingMode`；否则必须有值，否则校验报「Invalid recurring billingMode for plan '%s'」。计划级缺省时继承目录级 `recurringBillingMode`。

## BR-184 plansAllowedInBundle 的取值语义

- **类型**: 业务规则
- **同义词**: bundle 内计划数量, plans allowed in bundle, 允许多少计划, 不限量 -1
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:90-95`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:239-251`

**规则**：`plansAllowedInBundle` 表示一个 bundle 内该计划允许存在的数量：
- 缺省值 1；BASE 计划与 Tiered ADDON 只允许 1（源码注释明确）。
- 值 `-1` 表示不限量。
- 未设置时由初始化安全网填为 -1，运行期若仍为 null 会抛 IllegalStateException（安全校验）。

## BR-185 默认价格表名 DEFAULT 为保留名

- **类型**: 业务规则
- **同义词**: 默认价格表命名, DEFAULT 保留, reserved price list name, 价格表命名约束
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:106-118`, `catalog/src/main/java/org/killbill/billing/catalog/PriceListDefault.java:36-45`

**规则**：
- 默认价格表（PriceListDefault）的名称 `getName()` 恒返回 `PriceListSet.DEFAULT_PRICELIST_NAME`（值 `DEFAULT`）。
- 子价格表名称不得等于 `DEFAULT`，否则校验报「Pricelists cannot use the reserved name 'DEFAULT'」。
- 若默认价格表名称不等于 `DEFAULT`，报「The name of the default pricelist must be 'DEFAULT'」。

## BR-186 价格表解析与默认回退

- **类型**: 业务规则
- **同义词**: 找价格表, price list fallback, 默认价格表回退, 多匹配计划, price list resolution
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:64-98`

**规则**：
- `getPlanFrom(product, period, priceListName)`：先在指定价格表查匹配计划；若 0 个，则回退到默认价格表再查。
- 最终 0 个 → 返回 null；1 个 → 返回该计划；>1 个 → 抛 `CAT_MULTIPLE_MATCHING_PLANS_FOR_PRICELIST`。
- `findPriceListFrom(name)`：name 为 null 抛 `CAT_NULL_PRICE_LIST_NAME`；依次匹配默认表与子表；找不到抛 `CAT_PRICE_LIST_NOT_FOUND`。

## BR-187 计划缺省价格表的自动解析

- **类型**: 业务规则
- **同义词**: 计划归属价格表, plan price list, price list for plan, 自动找价格表
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:280-281`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:404-412`

**规则**：若计划未显式声明 `priceListName`，初始化时遍历目录所有价格表，找到第一个包含该计划的表名；若都找不到则抛 `IllegalStateException("Cannot extract pricelist for plan ...")`。

## BR-188 目录版本按生效日期选取

- **类型**: 业务规则
- **同义词**: 目录版本选择, catalog for date, effective date 选择, 历史目录
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:82-107`

**规则**：给定日期查版本时，从最新版本往前找第一个 `effectiveDate <= 查询日期` 的版本；若所有版本都晚于查询日期，返回第一个（最早）版本（源码注释说明这是容错处理，见 issue #760）。版本集合按 effectiveDate 升序排序。

## BR-189 版本生效日唯一且 catalogName 一致

- **类型**: 业务规则
- **同义词**: 版本重复生效日, catalog name 一致, version effective date unique, 目录版本校验
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:133-154`

**规则**：校验所有版本：
- 每个版本的 `effectiveDate` 必须唯一，重复报「Catalog effective date '%s' already exists for a previous version」。
- 每个版本的 `catalogName` 必须与目录名一致，否则报「Catalog name '%s' is not consistent across versions」。
- 每个 `StandaloneCatalog` 版本自身再跑一遍校验。

## BR-190 跨版本同名计划形状必须一致

- **类型**: 业务规则
- **同义词**: 跨版本计划一致性, plan shape, 阶段数量一致, 阶段名一致, uniform plan shape
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:156-192`

**规则**：对任意两个版本中同名的计划：阶段数量必须相同，且逐位阶段名必须一致。违反时报「Number of phases for plan ... differs between version ...」或「Phase ... does not exist in version ...」。若某版本无该计划则跳过（允许后续版本重新定义）。

## BR-191 规则未命中时的默认策略/对齐值

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

## BR-192 ILLEGAL 变更策略直接拒绝计划变更

- **类型**: 业务规则
- **同义词**: 禁止变更, 非法换套餐, illegal plan change, ILLEGAL policy
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:143-164`

**规则**：`getPlanChangeResult(from, to)` 先解析目标价格表与策略；若策略为 `BillingActionPolicy.ILLEGAL`，抛 `IllegalPlanChange`；否则返回 `PlanChangeResult(toPriceList, policy, alignment)`。

## BR-193 规则集必须存在默认 case 且不得重复

- **类型**: 业务规则
- **同义词**: 规则校验, 默认规则缺失, 规则去重, plan rules validation, duplicate rule
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:187-278`

**规则**：
- 变更策略（changePolicyCase）和取消策略（cancelPolicyCase）必须各存在一个所有匹配字段均为 null 的「默认 case」，否则报「Missing default rule case for plan change/cancellation」。
- 每类规则（变更策略/取消策略/变更对齐/创建对齐/计费对齐/价格表）内部不得有重复项，重复报「Duplicate rule for ...」。

## BR-194 产品自引用与 catalogName 校验

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

## BR-195 TOP_UP 块必须定义 minTopUpCredit

- **类型**: 业务规则
- **同义词**: 充值块校验, top-up 最低充值, minTopUpCredit, top_up block
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultBlock.java:92-110`

**规则**：`BlockType.TOP_UP` 的块必须定义 `minTopUpCredit`（大于缺省 -1），否则校验报「TOP_UP block needs to define minTopUpCredit」；对非 TOP_UP 块调用 `getMinTopUpCredit()` 抛 `CAT_NOT_TOP_UP_BLOCK`。

## BR-196 规则 case 的匹配语义

- **类型**: 业务规则
- **同义词**: 规则匹配, case 匹配, 规则优先级, rule matching, case satisfies
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCase.java:47-88`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCasePhase.java:43-62`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCaseChange.java:86-151`

**规则**：
- 单条 case 的每个字段为 null 表示「通配」；非 null 字段必须与输入的产品/类别/周期/价格表（阶段规则还含 phaseType）匹配。
- 一组 case 按声明顺序**首个匹配即返回**（first-match wins）。
- 变更类规则同时匹配 from 与 to 两组字段。

## BR-197 createOrFindPlan 的计划解析与异常

- **类型**: 业务规则
- **同义词**: 计划解析, 按产品找计划, createOrFindPlan, plan not found, 价格表缺省
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:205-229`

**规则**：
- 给了 `planName` → 直接 `findPlan(planName)`。
- 否则必须有 `productName` 与 `billingPeriod`（缺失分别抛 `CAT_NULL_PRODUCT_NAME` / `CAT_NULL_BILLING_PERIOD`）；价格表缺省用 `DEFAULT`，再经 `PriceListSet.getPlanFrom` 解析。
- 最终计划为 null → 抛 `CAT_PLAN_NOT_FOUND`。

## BR-198 价格表查找的异常语义

- **类型**: 业务规则
- **同义词**: 价格表异常, price list not found, 空价格表名, null price list
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:85-98`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:271-278`

**规则**：`findPriceList(name)`：name 为 null 或 priceLists 为 null → `CAT_PRICE_LIST_NOT_FOUND`；通过集合查找时 name 为 null 抛 `CAT_NULL_PRICE_LIST_NAME`，找不到抛 `CAT_PRICE_LIST_NOT_FOUND`。

## BR-199 BCD 由首个非零周期费日期推算

- **类型**: 业务规则
- **同义词**: 首个收费日, 非零周期费, first recurring charge, BCD 计算, dateOfFirstRecurringNonZeroCharge
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:329-352`, `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:133-139`

**规则**：`dateOfFirstRecurringNonZeroCharge(subscriptionStartDate, initialPhaseType)` 从订阅起始日出发，跳过价格为 0（或非 UNLIMITED 且 recurring 价格为空/零）的阶段，累加其时长，得到第一个「非零周期费」的日期。订阅对齐（SUBSCRIPTION）的 BCD = 该日期的当月日号。

**可选参数**：传入 `initialPhaseType` 时会先跳过到指定阶段类型再开始计算。

## BR-200 BCD 对齐的月末处理

- **类型**: 业务规则
- **同义词**: 月末账单日, 2月对齐, month end billing, BCD 29/30/31, lastDayOfMonth
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:74-116`

**规则**：
- 仅当计费周期以「月/年」为单位时才做 BCD 对齐；以天/周为单位的周期直接返回原日期。
- 若 `billingCycleDay > 当月最大天数`，则取当月最后一天（例如 BCD=31 在 2 月对齐为 28/29 日）。
- 若当前日期已过本月 BCD，则对齐到下月同一 BCD。

## BR-201 账户 BCD 取最早的有计费 ACCOUNT 对齐事件

- **类型**: 业务规则
- **同义词**: 账户账单日计算, account BCD, 账户首个账单日, computeAccountBCD
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `junction/src/main/java/org/killbill/billing/junction/plumbing/billing/DefaultInternalBillingApi.java:220-274`

**规则**：当账户尚未设置 BCD（=0）时，从所有 billing event 中筛选 `BillingAlignment.ACCOUNT` 且「有周期价（可为 0）或有 usage」的事件，取 effectiveDate（并列时取 totalOrdering）最小的一个，其 `getBillCycleDayLocal()` 即候选账户 BCD（必须 > 0）。dry-run 模式下不落库。

## BR-202 ACCOUNT 对齐但账户 BCD 未设时回退 SUBSCRIPTION

- **类型**: 业务规则
- **同义词**: 账单日回退, ACCOUNT 未设置, alignment fallback, 订阅对齐
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:39-72`, `entitlement/src/main/java/org/killbill/billing/entitlement/engine/core/EventsStreamBuilder.java:451-457`

**规则**：`resolveEffectiveBillingAlignment(ACCOUNT, accountBCD==0)` 返回 `SUBSCRIPTION`，以便在账户 BCD 尚未建立期间仍能按订阅起始日推算 BCD。构建事件流时若对齐为 ACCOUNT 且账户 BCD=0，则不预先计算 defaultAlignmentDay（留给后续账户 BCD 计算）。

## BR-203 简化计划只支持 EVERGREEN 与单 TRIAL

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

## BR-204 ADD_ON 必须提供有效的可用基础产品

- **类型**: 业务规则
- **同义词**: 附加产品校验, add-on base product, availableBaseProducts, BASE_PLAN_PRODUCTS_NOT_EMPTY
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:296-313`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:195-209`

**规则**：产品类别为 `ADD_ON` 时，`availableBaseProducts` 不得为空（否则报「List of available base products should not be empty for add-ons.」），且其中每个产品必须已存在于目录（否则报「Available base products contain invalid product.」）。创建 add-on 时会在这些基础产品的 `available` 列表中加入该 add-on。

## BR-205 计划/产品/价格表/单位/用量名称的字符约束（XML ID / NCName）

- **类型**: 业务规则
- **同义词**: 命名规则, 名称约束, 非法字符, 冒号禁止, naming constraint, XML ID, NCName, plan name characters
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/caching/PriceOverridePattern.java:28-39`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:65-67`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:51-53`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceList.java:49-51`

**规则**：计划名（`DefaultPlan.name`）、产品名（`DefaultProduct.name`）、价格表名（`DefaultPriceList.name`）、单位名（`DefaultUnit.name`）、用量名（`DefaultUsage.name`）均标注 `@XmlAttribute + @XmlID`，因此必须符合 XML ID / NCName 语法——**不能以数字开头、不能含空格、不能含冒号 `:`** 等。

**直接证据**：`PriceOverridePattern` 注释明确「In order to not collide with any expected character from XML planName, we chose one character that is not allowed」并选取 `CUSTOM_PLAN_NAME_DELIMITER = ":"` 作为自定义计划名的分隔符——反证 `:` 不允许出现在 XML 计划名中。若计划名不符 NCName，XML 反序列化/校验阶段即失败。

**例外/补充**：`prettyName` 是普通字符串属性（`@XmlAttribute(required=false)`），不受 NCName 约束，可含空格与中文；缺省时回填为 `name`。

## BR-206 同名条目在目录内「后写覆盖」而非报错（唯一性陷阱）

- **类型**: 业务规则
- **同义词**: 名称唯一性, 重复计划, 重复产品, 覆盖, duplicate name, name uniqueness, CatalogEntityCollection, last wins
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogEntityCollection.java:32-63`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogEntityCollection.java:191-197`, `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:83-95`

**规则**：目录内产品、计划、价格表计划列表都以 `CatalogEntityCollection`（底层 `TreeMap<String,T>`，key = `CatalogEntity.getName()`）存储。`addEntry` 使用 `data.put(name, entry)`，因此**同一目录内出现两个同名计划/产品时不会报错，后加入者静默覆盖前者**，且只保留一个条目。

**推论**：
- 计划名是事实上的主键；名称冲突的后果是「丢失一个计划」，而非校验失败。
- `findByName` 为 O(log N) 精确查找；`getEntries()` 返回按 name 自然排序的集合。
- 跨目录版本的同名计划另有「形状必须一致」校验（见 kb2 BR-190），但那发生在版本之间，不能防止单版本内重名覆盖。

**注意**：价格表集合（`PriceListSet`）本身**不做**子价格表重名校验，只有「不得用保留名 DEFAULT」这一条（见 kb2 BR-185）。

## BR-207 规则匹配时输入字段的精确解析路径

- **类型**: 业务规则
- **同义词**: 规则匹配解析, case 匹配, planName 优先, plan specifier, rule matching, satisfiesCase
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCase.java:54-75`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCaseChange.java:86-137`

**规则（单边 case，如创建对齐/计费对齐/取消策略）**：
- 若输入 `planName != null`：`findPlan(planName)`，由此取 `product`、`recurringBillingPeriod`、`product.getCategory()`、`plan.getPriceList()`。
- 否则：`findProduct(productName)` 取 category；`billingPeriod` 直接用输入值；**priceList 仅当 case 自身声明了 `priceList` 时才通过 `findPriceList(priceListName)` 解析，否则保持 null**（即 case 不指定价格表时，priceList 维度不参与匹配）。

**规则（变更 case，双边）**：对 `from` 与 `to` 各按上述逻辑分别解析出 product/category/billingPeriod/priceList，然后 `phaseType` 与 `from.phaseType`、8 个 from/to 字段逐一比对；任一非 null 字段不等即不匹配。

**返回**：`DefaultCase.getResult[...]` 按数组声明顺序遍历，**首个匹配即返回**（first-match wins）；全不匹配返回 null，由上层 `DefaultPlanRules` 套用默认值。

## BR-208 价格表解析：显式指定 vs 继承（sticky）语义

- **类型**: 业务规则
- **同义词**: 价格表解析, 价格表继承, 粘性价格表, sticky price list, price list resolution, priceListCase, toPriceList
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:143-185`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCasePriceList.java:36-108`

**规则（变更计划时目标价格表如何确定）**：
1. 若目标 `to.priceListName != null` → 直接 `root.findPriceList(to.priceListName)`（显式指定，非粘性）。
2. 否则 → `findPriceList(from)`：
   a. 先跑 `priceListCase` 规则（`DefaultCasePriceList.getResult`），命中则用其 `toPriceList`（可把价格表切到促销表等，非粘性）。
   b. 规则未命中则回退：若 from 给了 `planName`，取 `findPlan(planName).getPriceList().getName()`；否则用 from 的 `priceListName`；再 `root.findPriceList(...)`。
3. 由此得到 `PlanChangeResult(toPriceList, policy, alignment)`。

**"sticky" 含义**：目标计划未显式声明价格表、且价格表规则未命中时，**沿用来源计划的价格表**——即价格表在变更时粘住（同一价格表内换计划）。若想换表，必须显式指定 `toPriceList` 或配置 `priceListCase`。

**补充**：当 `to.planName == null`（旧式按 product/billingPeriod 指定目标）时，会先用解析出的价格表重建一个 `toWithPriceList`，保证后续策略/对齐规则看到正确的价格表维度。

## BR-209 BillingAlignment 三种对齐策略的精确计算目标

- **类型**: 业务规则
- **同义词**: 对齐语义, 对齐目标, 账户对齐, bundle 对齐, 订阅对齐, alignment semantics, ACCOUNT, BUNDLE, SUBSCRIPTION
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:50-72`, `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:122-139`

**三种对齐各自「对齐到什么」**：
- `ACCOUNT`：BCD 直接取**账户级 BCD**（`accountBillCycleDayLocal`）。计算时用 `Preconditions.checkState(accountBillCycleDayLocal != 0)` 强制要求账户 BCD 已建立，否则抛异常。
- `BUNDLE`：BCD 取**该 bundle 内 base subscription** 的 BCD（`calculateOrRetrieveBcdFromSubscription(baseSubscription, ...)`），即 add-on 跟随基础订阅。
- `SUBSCRIPTION`：BCD 取**该订阅自身**的 BCD，由 `subscription.getDateOfFirstRecurringNonZeroCharge()` 的当月日号决定。

**回退**：`resolveEffectiveBillingAlignment(ACCOUNT, accountBCD==0)` 返回 `SUBSCRIPTION`，用于账户 BCD 尚未建立的过渡期。

**对阶段/add-on 的影响**：add-on 若配置 `BUNDLE` 对齐则锚定基础订阅的 BCD（与其自身起订日无关）；`SUBSCRIPTION` 对齐则即使挂在同一账户也各自出账；`ACCOUNT` 对齐使同一账户的所有订阅统一到同一账单日。BCD 结果按订阅 id 缓存（`calculateOrRetrieveBcdFromSubscription`）。

## BR-210 BCD 对齐仅对「月/年」周期生效及跨月推进

- **类型**: 业务规则
- **同义词**: 月基周期, 账单日推进, 跨月对齐, month-based period, alignToNextBillCycleDate, NO_BILLING_PERIOD
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/bcd/BillCycleDayCalculator.java:74-116`

**规则**：
- **月基判定**：`isMonthBased = (period.getMonths() | period.getYears()) > 0`。因此只有 MONTHLY / QUARTERLY / BIANNUAL / ANNUAL 视为月基；DAILY/WEEKLY 不是。
- **NO_BILLING_PERIOD 短路**：`alignToNextBillCycleDate` 遇到 `NO_BILLING_PERIOD` 直接返回当前转换日期，不做任何对齐。
- **非月基**：从上次转换日按周期反复加，直到 `>= curTransitionDate`（不按「日号」对齐）。
- **月基**：若当前转换日的日号 > BCD，则先 `plusMonths(1)` 再对齐；否则直接对齐。对齐函数 `alignProposedBillCycleDate` 在 `billingCycleDay > 当月最大天数` 时取**当月最后一天**。

**用途**：该逻辑驱动「订阅起始日 → 实际出账日」的推进，进而决定首次账单日。

## BR-211 两个生效日期字段的分工：目录版本 vs 存量订阅

- **类型**: 业务规则
- **同义词**: 生效日期, 目录生效日, 存量订阅生效日, effective date, effectiveDateForExistingSubscriptions, deferred effective date, 新订阅, 存量订阅
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:69-73`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:285-293`, `subscription/src/main/java/org/killbill/billing/subscription/catalog/SubscriptionCatalog.java:176-213`, `subscription/src/main/java/org/killbill/billing/subscription/api/user/DefaultSubscriptionBase.java:696-724`

**两个日期字段**：
- `StandaloneCatalog.effectiveDate`（目录版本级）：决定「某日期查询时选哪个目录版本」。查询日期 ≥ 版本生效日时该版本对新订阅立即生效（对已有订阅是否切换则另看下面的字段）。
- `DefaultPlan.effectiveDateForExistingSubscriptions`（计划级，可空）：决定「新版目录中的该计划何时对**存量订阅**生效」（延迟生效/deferred）。

**精确语义（跨 catalog + subscription 两模块才能读懂）**：
- 选取版本时（`SubscriptionCatalog`）：从最新版本往回找，若命中版本比订阅变更日新，则视为「存量订阅」；此时只有当 `plan.getEffectiveDateForExistingSubscriptions() != null` **且** `requestedDate >= existingSubscriptionDate` 才用新版本计划。**该字段为 null 时，目录的任何改动都不会应用到存量订阅**（源码注释原文：`If it is null, any change to this catalog does not apply to existing subscriptions`）。
- 构建计费事件时（`DefaultSubscriptionBase`）：从当前计划出发迭代 `getNextPlanVersion`，对每个 `effectiveDateForExistingSubscriptions != null` 的后续版本生成一条 `CHANGE` 计费转换事件（可再按配置对齐到下一个 BCD）。
- 若字段 **不是 null 但早于目录 effectiveDate**，目录校验直接失败：`Price effective date %s is before catalog effective date '%s'`。

**推论**：新订阅按目录版本 effectiveDate 选取版本；存量订阅的切换由计划级 effectiveDateForExistingSubscriptions 控制，缺省（null）表示「不追溯存量」。

## BR-212 目录版本按日期选取的精确索引算法（含容错）

- **类型**: 业务规则
- **同义词**: 版本选择, 版本索引, 目录查询日期, catalog version for date, indexOfVersionForDate
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:87-107`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultVersionedCatalog.java:109-120`

**规则**：
- 版本列表在 `add()` 时按 `effectiveDate` **升序排序**。
- `indexOfVersionForDate(date)`：从 `versions.size()-1` 递减，返回第一个 `effectiveDate.getTime() <= date.getTime()` 的索引；即「生效日 ≤ 查询日期的**最新**版本」。
- **容错**：若所有版本都晚于查询日期，返回索引 0（最早版本）。源码注释说明这是为了规避时间操控导致的「早于任何目录版本」状态（见 issue #760），并非严格语义。
- 版本为空时抛 `IllegalStateException("No existing versions in the VersionedCatalog catalog for input date ...")`。

**注意**：该方法此前先把入参通过 `CatalogDateHelper.toUTCDateTime(date)` 归一化为 UTC。

## BR-213 usage/tier 级「整段打包价」fixedPrice / recurringPrice

- **类型**: 业务规则
- **同义词**: 整段价格, 打包价, usage 固定价, usage 周期价, bundled usage price, usage fixedPrice, usage recurringPrice
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultUsage.java:89-95`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:54-61`

**规则**：`Usage` 与 `Tier` 都可选地携带 `fixedPrice` / `recurringPrice`（均为 `InternationalPrice`）。源码注释：用于「把若干 limits/blocks 的单位打包成一个整段价格」——即不逐块计价，而是对整个用量段收一次性/周期性费用。

**关系**：这是与 `blocks/tiers` 逐块计价并存的第二种计费形态；两者可同时声明，具体取用由计价器按上下文决定。缺省（无该字段）表示不做整段计费。

## BR-214 DefaultLimit 的 -1 哨兵与 compliesWith 判定细节

- **类型**: 业务规则
- **同义词**: 用量限制, 上下限哨兵, limit 判定, -1 未设置, min max limit, compliesWith
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultLimit.java:54-105`

**规则**：
- **哨兵值**：`initialize` 时 `maxHasValue = max != null && max != -1`；`minHasValue = min != null && min != -1`。因此缺省/未写即被 `CatalogSafetyInitializer` 填为 -1，等价于「未设置」。
- **校验**：仅当 `maxHasValue && minHasValue && max < min` 时报 `max must be greater than min`。
- **判定 `compliesWith(value)`**：
  1. `maxHasValue && value > max` → 返回 false；
  2. 否则返回 `!minHasValue || value <= min`，即「无 min 限制则通过；有 min 时要求 value ≤ min 才通过」。
- **注意（源码语义疑点）**：`min` 分支用 `value <= min`，意味着 value 大于 min 时反而**不通过**，与直觉的「下限」相反；使用时需结合业务/官方文档确认（kb2 BR-181 已标注该疑点，本卡补充哨兵值判定细节）。

## BR-215 CatalogSafetyInitializer：缺省值注入规则

- **类型**: 业务规则
- **同义词**: 缺省值注入, 安全初始化, 反序列化默认值, safety initializer, default value, -1, zero length array
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogSafetyInitializer.java:36-78`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogSafetyInitializer.java:80-117`

**规则**：目录对象在 `initialize` 阶段对所有**非必填**（对应 XML 注解 `required=false` 或无 required）字段注入缺省值（仅当当前为 null）：
- 数组 → 零长度数组（可安全 `length`/遍历）。
- `Integer` → `-1`；`Double` → `-1.0`；`BigDecimal` → `-1`。
- 枚举：`FixedType` → `ONE_TIME`；`BlockType` → `VANILLA`；`TierBlockPolicy` → `ALL_TIERS`。

**注意**：
- 只处理 XML 注解标记为非必填的数组字段；必填数组（`required=true`）不注入，保持 null 交由校验报错。
- 枚举只对上述三种做回填；其它枚举（如 ProductCategory、PhaseType）为 null 时不会被自动补值，需依赖 XML 必填属性或各自 validate 的「Safety check」。

## BR-216 价格覆盖的前置约束（被覆盖阶段必须已存在对应计费项）

- **类型**: 业务规则
- **同义词**: 价格覆盖校验, 覆盖前置条件, invalid price override, fixed 覆盖, recurring 覆盖, usage 覆盖
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/override/DefaultPriceOverrideSvc.java:76-119`, `catalog/src/main/java/org/killbill/billing/catalog/override/DefaultPriceOverrideSvc.java:137-207`

**规则**：
- 解析阶段级覆盖：优先按 `phaseName` 精确匹配阶段；若未给 `phaseName`，则按 `phaseType` 匹配（源码注释明确：同类型多阶段时此推断会失败）。
- **硬约束**：若某阶段原本 `getFixed() == null` 但覆盖里给了 `fixedPrice` → 抛 `CatalogApiException(CAT_INVALID_INVALID_PRICE_OVERRIDE, "There is no existing fixed price for the phase ...")`；`recurring` 同理（`There is no existing recurring price for the phase ...`）。即**只能覆盖已存在的计费项价格，不能凭覆盖凭空新增计费项**。
- usage 覆盖：按 usage `name` 匹配；tier 覆盖：按 `unit 名称 + size + max` 三元组匹配；tiered block 覆盖：同样按 `unitName + size + max` 匹配（`TieredBlock` 定位到具体块）。

**结果**：`getOrCreateOverriddenPlan` 把每个阶段的覆盖归位成与 `getAllPhases()` 等长的数组（无覆盖处为 null），再构造覆盖计划。

## BR-217 简化计划描述符的精确校验条件

- **类型**: 业务规则
- **同义词**: 简化计划校验, simple plan validation, 描述符校验, planId 必填, amount 校验, currency 校验
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:119-131`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:296-314`

**规则（`validateNewPlanDescriptor`）**：
- `invalidPlan = desc.getPlanId() == null && (desc.getProductCategory() == null || desc.getBillingPeriod() == null)`。
- `invalidPrice = (desc.getAmount() == null || desc.getAmount().compareTo(BigDecimal.ZERO) < 0) || desc.getCurrency() == null`。
- 任一为真 → 抛 `CatalogApiException(CAT_INVALID_SIMPLE_PLAN_DESCRIPTOR, INVALID_PRICE)`（`INVALID_PRICE` 文案：`Please check amount and currency. Amount should be greater than 0 and currency should be valid.`）。

**入口级校验（`addSimplePlanDescriptor`）**：
- `desc == null || desc.getPlanId() == null` → 抛 `CAT_INVALID_SIMPLE_PLAN_DESCRIPTOR, INVALID_PLAN`（`Plan is invalid. Please check.`）。
- 计划不存在且 `desc.getProductName() == null` → 抛 `CAT_INVALID_SIMPLE_PLAN_DESCRIPTOR, INVALID_PRODUCT_NAME`。

**金额边界**：判断用 `< 0`，因此 `amount == 0` 是**允许**的（与文案「greater than 0」不一致，注意区分）。

## BR-218 简化计划：新增币种时重置固定价、recurringPrice 空数组语义、EVERGREEN 兜底

- **类型**: 业务规则
- **同义词**: 新增币种重置, 零价重置, 空价格数组, evergreen 兜底, simple plan currency
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:164-193`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultInternationalPrice.java:88-100`

**规则**：
- 若描述符币种**不在**目录 `supportedCurrencies`：先 `catalog.addCurrency(currency)`；并且当计划恰有 1 个初始阶段时，把该阶段固定价的 `prices` **置为 null**——目的是让后续 `isZero()` 逻辑「穿过新币种并为其设置零价」（源码注释：`Reset the fixed price to null so the isZero() logic goes through new currencies and set the zero price for all`）。
- 若计划**没有 finalPhase**：新建一个 `EVERGREEN` finalPhase，`duration.unit = UNLIMITED`。
- 若 finalPhase **没有 recurring**：新建 recurring，`billingPeriod = desc.billingPeriod`，`recurringPrice` 用**空价数组** `new DefaultPrice[0]`。
- 若 recurring 的价不含描述符币种：追加一条该币种的价格（值 = desc.amount）。
- **空数组语义**：`InternationalPrice` 在无任何 price 时对所有币种返回 `BigDecimal.ZERO`；一旦存在列表但缺某币种，则抛 `CAT_NO_PRICE_FOR_CURRENCY`。因此「先建空数组再补币种」是确保未补币种视为零价、而非报错。

## BR-219 ADD_ON 的 availableBaseProducts 校验与 available 列表注入

- **类型**: 业务规则
- **同义词**: 附加产品可用基础产品, add-on base product, availableBaseProducts, 基础产品可用列表
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:195-209`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:304-313`

**规则**：
- 类别为 `ADD_ON` 时，`availableBaseProducts` 不得为 null 或空，否则抛 `CAT_INVALID_SIMPLE_PLAN_DESCRIPTOR, BASE_PLAN_PRODUCTS_NOT_EMPTY`（`List of available base products should not be empty for add-ons.`）。
- 其中每个产品名必须已存在于目录，否则抛 `CAT_INVALID_SIMPLE_PLAN_DESCRIPTOR, EXISTING_PRODUCTS_NOT_EMPTY`（`Available base products contain invalid product.Please check.`）。
- 通过后，对每个基础产品，若其 `available` 列表尚不含该 add-on，则调用 `catalog.addProductAvailableAO(base, product)` 追加（做存在性去重）。

**与查询的关系**：运行期 `getAvailableAddOnListings(baseProductName, priceListName)` 正是遍历该基础产品的 `available` 集合来生成可售 add-on 列表。

## BR-220 PriceList.findPlans 的匹配语义（产品相等 + 周期相等）

- **类型**: 业务规则
- **同义词**: 找计划, 价格表内查找, findPlans, 产品匹配, 周期匹配, plan lookup
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceList.java:94-108`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:257-287`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:234-237`

**规则**：`PriceList.findPlans(product, period)` 遍历该价格表内的计划，返回同时满足：
1. `cur.getProduct().equals(product)`——`Product` 相等性由 `DefaultProduct.equals` 定义，比较 `name`、`category`、`included`/`available`（经 getter，已过滤自引用）、`limits`、`catalogName`；
2. `cur.getRecurringBillingPeriod() != null && cur.getRecurringBillingPeriod().equals(period)`——计划的周期取自 **finalPhase 的 recurring**。

**推论**：纯用量/一次性计划（finalPhase 无 recurring）的 `getRecurringBillingPeriod()` 返回 `NO_BILLING_PERIOD`，只能用 `period = NO_BILLING_PERIOD` 才能查到；产品的 included/available/limits 任一不同即视为不同产品而不匹配。

## BR-221 DefaultProduct.isAvailable() 的实现缺陷（误查 included 列表）

- **类型**: 业务规则
- **同义词**: available 判定缺陷, isAvailable bug, 产品可用性, available product
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:133-149`

**规则/事实**：`isAvailable(addon)` 的实现遍历的是 `included.getEntries()`（而非 `available.getEntries()`）来判断 addon 是否「可用」——与 `isIncluded` 逻辑完全相同，属实现缺陷。因此该方法对「仅在 available、不在 included」的 add-on 会返回 false。

**影响**：这是遗留代码（`getIncluded`/`getAvailable` 另有自引用过滤的 workaround），关键路径（Listing 生成、简化计划校验）均直接访问集合本身，未依赖 `isAvailable`；但任何调用 `isAvailable` 的判断都可能得到错误结果，需注意。

## BR-222 运行期对自引用产品的过滤

- **类型**: 业务规则
- **同义词**: 自引用过滤, self reference filter, included 过滤, available 过滤
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:88-103`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultProduct.java:187-208`

**规则**：
- 运行期 `getIncluded()` 与 `getAvailable()` 都会用 `filter(c -> c != this)` 剔除指向自身的条目（源码注释：为兼容历史上含自引用的目录）。
- 但**校验期**（`validate`）仍会对 `included`/`available` 中的自引用报 `Product refers to itself in included section` / `... available section`，除非系统属性 `org.killbill.catalog.validation.ignoreSelfReferencingProducts=true`（静态常量在类加载时读取）。

**差异**：`validate` 遍历的是原始集合（含自引用），`getter` 返回过滤后的视图——因此「能加载」不代表「校验通过」。

## BR-223 计划默认价格表的自动解析顺序

- **类型**: 业务规则
- **同义词**: 计划价格表解析, findPriceListForPlan, 计划归属价格表, default price list resolution
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:276-283`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:404-412`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPriceListSet.java:140-148`

**规则**：
- `DefaultPlan.initialize`：`priceListName = (显式声明 != null) ? 显式值 : findPriceListForPlan(catalog)`。
- `findPriceListForPlan` 遍历 `catalog.getPriceLists().getAllPriceLists()`，返回**第一个** `findPlan(planName) != null` 的价格表名称；全都不含该计划则抛 `IllegalStateException("Cannot extract pricelist for plan <name>")`。
- `getAllPriceLists()` 的返回顺序是：**默认价格表在前，子价格表按声明顺序在后**。

**推论**：未显式归属的计划若同时出现在默认表与子表，会被归到**默认价格表**（先命中）。同一计划出现在多个表是允许的，但自动归属只认第一个。

## BR-224 模板目录的判定条件

- **类型**: 业务规则
- **同义词**: 模板目录, 空目录, template catalog, isTemplateCatalog, filterTemplateCatalog
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:174-178`, `catalog/src/main/java/org/killbill/billing/catalog/io/VersionedCatalogLoader.java:124-146`

**规则**：`isTemplateCatalog()` 当且仅当**三者同时为空**才返回 true：
- `products == null || products.isEmpty()`，
- `plans == null || plans.isEmpty()`，
- `supportedCurrencies == null || supportedCurrencies.length == 0`。

**用途**：目录加载时若 `filterTemplateCatalog=true`，模板目录会被**跳过**（不加入 VersionedCatalog）；默认目录加载路径不会过滤。

## BR-225 findPhase 依赖「阶段名反解出计划名」的查找链

- **类型**: 业务规则
- **同义词**: 查阶段, 阶段查找, findPhase, 反解计划名, phase lookup
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/StandaloneCatalog.java:261-269`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlanPhase.java:108-115`

**规则**：`StandaloneCatalog.findPhase(name)`：
1. 若 `name == null || plans == null` → 抛 `CAT_NO_SUCH_PHASE`。
2. 用 `DefaultPlanPhase.planName(name)` 从阶段名反解出计划名（按 PhaseType.values() 顺序匹配后缀）。
3. `findPlan(planName)` 找计划；计划不存在抛 `CAT_NO_SUCH_PLAN`。
4. `plan.findPhase(name)` 在计划内线性查找同名阶段；找不到抛 `CAT_NO_SUCH_PHASE`。

**推论**：阶段名本身不独立存储，必须先能反解出计划名；若阶段名后缀不匹配任何 PhaseType，在步骤 2 即抛 `CAT_BAD_PHASE_NAME`。

## BR-226 简化计划「更新已有计划」的精确校验（validateExistingPlan）

- **类型**: 业务规则
- **同义词**: 已有计划校验, simple plan update, validateExistingPlan, trial 一致性, evergreen 校验
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:227-283`

**规则（任一不满足即抛 `CAT_FAILED_SIMPLE_PLAN_VALIDATION`）**：
- **TRIAL 结构**：`initialPhases.length > 1`，或 `length == 1` 但 `(phaseType != TRIAL || !fixed.getPrice().isZero())` → 失败。即只允许「无起始阶段」或「单个 $0 TRIAL」。
- **TRIAL 一致性**（当描述符带 trial 信息 `trialLength != null && trialTimeUnit != null` 时）：
  - `isDescConfiguredWithTrial = trialLength > 0 && trialTimeUnit != UNLIMITED`；`isPlanConfiguredWithTrial = initialPhases.length == 1`。
  - 二者一真一假 → 失败；二者皆真则要求 `duration.unit == trialTimeUnit && duration.number == trialLength`，否则失败。
- **RECURRING**：`finalPhase.getPhaseType() != EVERGREEN` → 失败；`billingPeriod` 不一致 → 失败；若描述符给了 `currency` 与 `amount`，当前计划该币种价格必须相等（取价抛 `CatalogApiException`＝该币种尚未定义时**跳过**金额比对，不视为失败）。

**含义**：简化计划 API 只支持「EVERGREEN + 可选 $0 TRIAL」这一种形状，任何偏离都在更新时被拒绝。

## BR-227 简化计划导出前的「往返序列化」校验

- **类型**: 业务规则
- **同义词**: 目录导出校验, round trip, getCatalogXML, XMLWriter, CAT_INVALID_FOR_TENANT
- **模块**: catalog
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:104-117`

**规则**：`getCatalogXML` 先用 `XMLWriter.writeXML(catalog, StandaloneCatalog.class)` 生成 XML，再立即用 `XMLLoader.getObjectFromStream(...)` **反序列化回 StandaloneCatalog** 做往返验证。只有能成功读回才返回 XML。
- `ValidationException` 或 `JAXBException` → 抛 `CatalogApiException(CAT_INVALID_FOR_TENANT, tenantRecordId)`。
- 其它异常 → 包成 `RuntimeException`。

**含义**：即使内存中的可变目录能改，也只有在能完整序列化并重新加载通过校验时才会被接受/落盘。

## BR-228 支付失败重试计划（默认 8,8,8 天）

- **类型**: 业务规则
- **同义词**: 重试间隔, 重试天数, 重试次数, payment retry days, retry interval, 8 8 8
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:31-39`

**规则**：系统属性 `org.killbill.payment.retry.days`（默认 `8,8,8`）定义支付失败后的重试间隔（天）。默认值表示最多重试 3 次，每次间隔 8 天。

## BR-229 插件失败重试参数（初始 300 秒 / 倍数 2 / 最多 8 次）

- **类型**: 业务规则
- **同义词**: 网关重试, 插件失败重试, 指数退避, plugin failure retry, gateway down retry, retry multiplier
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:41-90`

**规则**：当支付失败原因是插件失败（网关宕机、瞬时错误等）时：
- `org.killbill.payment.failure.retry.start.sec` 默认 `300`，即首次重试等待 300 秒；
- `org.killbill.payment.failure.retry.multiplier` 默认 `2`，后续重试间隔按倍数递增（指数退避）；
- `org.killbill.payment.failure.retry.max.attempts` 默认 `8`，最多重试 8 次。

## BR-230 Janitor 未完成交易重试计划（UNKNOWN / PENDING）

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

## BR-231 AUTO_PAY_OFF 账户自动支付中止

- **类型**: 业务规则
- **同义词**: 自动支付关闭, 停止自动扣款, auto pay off, auto-payoff abort, 标签关闭自动支付
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:730-745`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:376-380`

**规则**：当发起非 API（系统自动）发票支付时，若账户带有 `AUTO_PAY_OFF` 标签（`ControlTagType.isAutoPayOff`），则：
1. 向 `invoice_payment_control_plugin_auto_pay_off` 表插入一条挂起记录（`PluginAutoPayOffModelDao`）；
2. 中止本次支付（返回 abort）。
**例外**：API 发起的支付（`isApiPayment()` 为 true）不受 AUTO_PAY_OFF 影响。

## BR-232 未提交(非 COMMITTED)发票不允许支付

- **类型**: 业务规则
- **同义词**: 草稿发票不扣款, 发票未提交, draft invoice payment, COMMITTED invoice, 发票状态校验
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:341-351`

**规则**：购买（PURCHASE）前校验发票状态，若发票不是 `COMMITTED`（如 DRAFT），记录日志并中止支付（`DefaultPriorPaymentControlResult(true)`）。

## BR-233 委托给父账户的子账户发票不自动支付

- **类型**: 业务规则
- **同义词**: 父账户代付, 子账户委托, delegated payment, parent account payment, 子账户不扣款
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:353-360`

**规则**：若账户的支付被委托给父账户（`accountData.isPaymentDelegatedToParent()` 为 true）或发票已关联父账户（`invoice.getParentAccountId() != null`），则中止本账户的支付扣款。

## BR-234 空发票(余额为 0)支付处理

- **类型**: 业务规则
- **同义词**: 零元发票, 空发票, 余额为零, zero amount invoice, empty invoice, allowEmptyInvoice
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:362-374`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:138-141`

**规则**：当请求支付金额计算结果 ≤ 0（发票已付清）时：
- 若系统属性 `org.killbill.payment.allow.emptyInvoice` 为 `true`（默认 `false`），则**不中止**，继续以 0 元发起支付；
- 否则视为"发票已支付"并中止支付。

## BR-235 支付金额不得超过发票余额

- **类型**: 业务规则
- **同义词**: 支付金额校验, 超付校验, 余额上限, overpayment, invoice balance, invalid amount
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:710-728`

**规则**：`validateAndComputePaymentAmount` 对金额做如下判定：
- 发票余额 ≤ 0 → 返回 0；
- 若为 API 支付且显式传入金额大于发票余额 → 抛 `PaymentApiException`（`PAYMENT_PLUGIN_EXCEPTION`，"Invalid amount"）；
- 否则取 `min(输入金额, 发票余额)` 作为实际支付金额；输入为 null 时取发票余额。

## BR-236 退款金额计算（按发票项或显式金额）

- **类型**: 业务规则
- **同义词**: 退款金额, 部分退款, 退款上限, refund amount, partial refund, invoice item adjustment
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:529-556`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:438-478`

**规则**：
- 若显式指定退款金额（`specifiedRefundAmount`），必须 > 0，否则报错"需要指定正数退款金额"；该金额直接作为退款额。
- 若未指定，则按退款关联的发票项（`invoiceItemIdsWithAmounts`）累加：每项可取显式金额（必须 > 0 且不超过该项原始金额）或默认取该项原始金额。
- 若计算出的可退金额为 0 且为 API 支付 → 抛错中止退款。

## BR-237 失败支付的下次重试日期计算

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

## BR-238 默认支付方式取自账户 (account.paymentMethodId)

- **类型**: 业务规则
- **同义词**: 默认支付方式, 账户默认卡, default payment method, account payment method, 自动扣款用哪张卡
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:252-257`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:382-397`

**规则**：执行支付时若调用方未显式传入 `paymentMethodId`，则使用账户上的默认支付方式（`account.getPaymentMethodId()`）。在发票自动支付场景中，若控制上下文 `getPaymentMethodId()` 为 null（账户无默认支付方式），则记录一条 `InvoicePaymentStatus.INIT` 的支付尝试完成事件并**中止**本次扣款（不会被触发）。

## BR-239 插件状态(PluginStatus)到交易状态/操作结果的映射

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

## BR-240 单笔支付不允许并发的未决交易

- **类型**: 业务规则
- **同义词**: 防重复扣款, 未决交易, 并发支付, double payment, pending transaction, 重复提交
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:352-385`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:308-310`

**规则**：
- 对 AUTHORIZE / PURCHASE / CREDIT，若同一支付下已存在 `PENDING` 状态的交易且调用未指定该交易 id/key，则抛 `PAYMENT_INVALID_OPERATION` 阻止新交易（防止重复扣款）。
- 若待完成的交易处于 `UNKNOWN` 状态，则无法确定其在状态机中的位置，直接抛 `PAYMENT_INVALID_OPERATION` 拒绝本次操作。
- 同一 `transactionExternalKey` 不允许已有成功的非 CHARGEBACK 交易（`PAYMENT_ACTIVE_TRANSACTION_KEY_EXISTS`），且该 key 不能跨账户（`PAYMENT_TRANSACTION_DIFFERENT_ACCOUNT_ID`）。

## BR-241 执行交易前先调用 Janitor 修正状态

- **类型**: 业务规则
- **同义词**: 先巡检再支付, janitor 修正, refresh before payment, 支付前修复状态
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:282-290`

**规则**：执行任何支付操作（`performOperation`）时，若该支付已存在，系统**先**调用 `paymentRefresher.invokeJanitor` 获取插件最新状态并修正本地状态，**然后**才让状态机推进交易。这样可避免因为本地状态陈旧而做出错误的状态流转（如重复扣款或错误拒绝）。

## BR-242 Janitor 下次回查时间计算（UNKNOWN/PENDING 重试表）

- **类型**: 业务规则
- **同义词**: janitor 回查间隔, 下次巡检时间, janitor retry schedule, unknown retries, pending retries
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:401-418`

**规则**：`getNextNotificationTime` 根据交易状态选择延迟表：
- `UNKNOWN` → 使用 `org.killbill.payment.janitor.unknown.retries`（默认 `5m,1h,1d,1d,1d,1d,1d`）；
- `PENDING` → 使用 `org.killbill.payment.janitor.pending.retries`（默认 `1h, 1d`）；
- 取第 `attemptNumber` 个延迟作为下次通知时间；若 `attemptNumber > 表长度`，返回 null（不再回查）。

## BR-243 支付控制插件可调整支付参数，默认禁止覆盖已有支付方式

- **类型**: 业务规则
- **同义词**: 控制插件调整, 修改支付方式, overwrite payment method, adjusted payment method, 插件改金额
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/control/ControlPluginRunner.java:128-151`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:133-136`

**规则**：控制插件 `priorCall` 返回值可调整：支付方式 id（`AdjustedPaymentMethodId`）、插件名、金额、币种、插件属性；任一插件的 `isAborted()` 为真则抛 `PaymentControlApiAbortException` 中止。**覆盖限制**：若插件试图设置 paymentMethodId，但该支付已存在 paymentMethodId 且系统属性 `org.killbill.payment.method.overwrite` 为 `false`（默认），则抛 `PaymentControlApiException` 拒绝覆盖。

## BR-244 支付插件按支付方式的 pluginName 查找

- **类型**: 业务规则
- **同义词**: 插件查找, 找不到插件, payment plugin lookup, no such payment plugin, plugin not found
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentPluginServiceRegistration.java:80-91`

**规则**：执行支付时，系统根据支付方式记录里的 `pluginName` 从 OSGI 注册表查找对应 `PaymentPluginApi`；若插件未注册，抛 `PaymentApiException(ErrorCode.PAYMENT_NO_SUCH_PAYMENT_PLUGIN, pluginName)`。

## BR-245 支付插件调用超时与线程配置

- **类型**: 业务规则
- **同义词**: 插件超时, 支付线程数, 插件调用超时, payment plugin timeout, plugin threads, dispatch timeout
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/dispatcher/PluginDispatcher.java:44-69`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:118-131`

**规则**：
- `org.killbill.payment.plugin.timeout` 默认 `30s`：每个支付插件调用通过独立线程池执行，超过该超时抛 `TimeoutException`；
- `org.killbill.payment.plugin.threads.nb` 默认 `10`：插件调度线程池大小；
- `org.killbill.payment.globalLock.retries` 默认 `50`：获取全局锁（每次等待 100ms）的最大重试次数。

## BR-246 支付错误事件与插件错误事件

- **类型**: 业务规则
- **同义词**: 支付错误事件, 插件错误事件, payment error event, plugin error event, bus event, 快照事件
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentErrorEvent.java:32-58`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultPaymentPluginErrorEvent.java:32-58`, `payment/src/main/java/org/killbill/billing/payment/core/sm/payments/PaymentEnteringStateCallback.java:49-82`

**规则**：
- `DefaultPaymentErrorEvent`（bus 类型 `PAYMENT_ERROR`）：当交易未创建且调用来自非 API（如自动扣款）时发送，消息为"Early abortion of payment transaction"（如缺少默认支付方式等异常情况）。
- `DefaultPaymentPluginErrorEvent`（bus 类型 `PAYMENT_PLUGIN_ERROR`）：插件层错误事件。
- 两者均携带 accountId / paymentId / paymentTransactionId / amount / currency / status / transactionType / effectiveDate / apiPayment / message。

## BR-247 外部支付通过插件属性模拟失败（测试/演示语义）

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

## BR-248 外部支付（__EXTERNAL_PAYMENT__）的用途

- **类型**: 业务规则
- **同义词**: 外部支付用途, 线下支付记录, external payment usage, 记录支票支付, 手动入账
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/provider/ExternalPaymentProviderPlugin.java:47-52`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:112-116`, `payment/src/main/java/org/killbill/billing/payment/provider/DefaultPaymentProviderPluginRegistry.java:40-43`

**规则**：`__EXTERNAL_PAYMENT__` 用于**记录并非由 Kill Bill 发起/处理的外部支付**（例如支票、银行转账已到账），它不做真实网关交互，直接把交易标记为成功。系统属性 `org.killbill.payment.provider.default`（默认 `__external_payment__`）指定默认支付提供者。因此当某支付方式绑定到该插件时，Kill Bill 只记录该笔支付而不调用任何外部网关。

## BR-249 各交易类型的插件操作与无金额操作

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

## BR-250 支付状态机 linkStateMachines：交易类型的先后约束

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

## BR-251 支付状态机成功态判定

- **类型**: 业务规则
- **同义词**: 成功态判定, isSuccessState, success state, 支付成功判断
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:236-239`

**规则**：`isSuccessState(stateName)` 判定某状态是否成功态：状态名以 `SUCCESS` 结尾**或**以 `CHARGEBACK` 开头（即所有 `CHARGEBACK_*` 状态都被视为成功，因为拒付本身是"已确认发生"的终态）。

<!-- module: payment | final | cards: see confidence report -->

## BR-252 支付 state 命名规则与 last_success_state_name 恢复

- **类型**: 业务规则
- **同义词**: 支付状态命名, 成功态恢复, last success state, 重试恢复点, payment state naming, lastSuccessStateName
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:83-110`, `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:121-203`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:316-320`, `payment/src/main/resources/org/killbill/billing/payment/ddl.sql:106-121`

**规则**：支付状态名统一为 `<TYPE>_<RESULT>`，共 **28** 个合法 name（`PaymentStateMachineHelper.STATE_NAMES`）：

- `<TYPE>_INIT`（初始，由 XML 定义但不在 `STATE_NAMES` 列表）、
- `<TYPE>_PENDING`（7 个：AUTH/CAPTURE/PURCHASE/REFUND/CREDIT/VOID/CHARGEBACK_PENDING）、
- `<TYPE>_SUCCESS`（7 个）、
- `<TYPE>_FAILED`（7 个）、
- `<TYPE>_ERRORED`（7 个）。

**成功态定义**：状态名以 `SUCCESS` 结尾，或以 `CHARGEBACK` 开头（即所有 `CHARGEBACK_*` 都算成功态）。

**恢复点**：`payments.last_success_state_name` 持久化最近一次成功态；执行后续交易时 `PaymentProcessor` 以 `currentStateName = payment.getLastSuccessStateName()` 作为状态机再入点，从而支持"失败后重试"从上次成功点继续（`payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:316-320`）。

**数据表**：`payments.state_name` (varchar 64) 与 `payments.last_success_state_name` (varchar 64)（`payment/src/main/resources/org/killbill/billing/payment/ddl.sql:112-113`）。

## BR-253 插件返回 null/UNDEFINED 的兜底与"状态不可推进"

- **类型**: 业务规则
- **同义词**: 空插件结果, 结果未知, null status, UNDEFINED 兜底, unknown transaction, 无插件信息
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentTransactionInfoPluginConverter.java:33-72`, `payment/src/main/java/org/killbill/billing/payment/provider/DefaultNoOpPaymentInfoPlugin.java:47-50`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentTransactionTask.java:224-229`

**规则**：
- 转换器对 `getStatus()` 为 `null` 的插件结果用 `Objects.requireNonNullElse(..., UNDEFINED)` 兜底，最终得到 `TransactionStatus.UNKNOWN` / `OperationResult.EXCEPTION`。
- Janitor 计算"新状态"时：若插件返回 `UNKNOWN`，则**保留原 `currentTransactionStatus`**（`computeNewTransactionStatusFromPaymentTransactionInfoPlugin`），从而不会把 PENDING 误降级。
- `DefaultNoOpPaymentInfoPlugin(..., PaymentPluginStatus.UNDEFINED, null, null)` 用于"取不到插件信息"的占位（例如 `getPaymentInfo` 抛异常时）。

**含义**：`UNDEFINED`/null 绝不代表成功或失败，只代表"结果未知"，必须由 Janitor 收敛（见 BR-258/BR-259）。

## BR-254 新建交易先以 UNKNOWN 落库，再由插件结果"两阶段"更新

- **类型**: 业务规则
- **同义词**: 初始未知, 两阶段写入, transaction 初始状态, create transaction unknown, 先写后更, processed amount
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentAutomatonDAOHelper.java:295-330`, `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentAutomatonDAOHelper.java:139-231`

**规则**：
- `buildNewPaymentTransactionModelDao` 创建交易时**固定写 `TransactionStatus.UNKNOWN`**，此时 `processed_amount`/`processed_currency` 为 null（`payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentAutomatonDAOHelper.java:311,324`）。
- 插件调用完成后由 `processPaymentInfoPlugin` 更新交易与支付：
  - `SUCCESS`/`PENDING` → `processedAmount = 插件返回的 amount`（插件 amount 为空则用默认值），`processedCurrency = 插件 currency`（为空则默认币种）；
  - 其余状态（失败类）→ `processedAmount = BigDecimal.ZERO`；
  - 同时写 `gateway_error_code`/`gateway_error_msg`。
- 若新 state 是成功态，则 `lastSuccessPaymentState = currentPaymentStateName` 一并落库（供 BR-252 的重试恢复）。

**含义**：`payment_transactions` 中存在过 `UNKNOWN` 的中间态行；最终状态取决于插件回包。若进程在插件调用后崩溃，交易会停留在 `UNKNOWN`，由 Janitor 收敛（见 BR-258）。

## BR-255 支付失败默认重试计划（8,8,8）的精确计算

- **类型**: 业务规则
- **同义词**: 重试计划, 重试天数计算, retry days, 8 8 8, next retry date, 第几次重试, payment failure retry
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:592-610`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:630-639`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:31-39`

**规则**：属性 `org.killbill.payment.retry.days`，默认 `8,8,8`（列表长度=最大重试次数，元素=间隔天数）。计算（`getNextRetryDateForPaymentFailure`）：

- `attemptsInState` = 该 payment 下所有 `PURCHASE` 交易中 `TransactionStatus = PAYMENT_FAILURE` 的条数；
- `retryCount = max(attemptsInState - 1, 0)`；
- 若 `retryCount < retryDays.size()` → 下次重试时间 = `internalContext.getCreatedDate() + retryDays.get(retryCount)` 天；
- 否则返回 `null`（不再重试）。

**默认时间点（首次失败起算）**：第 1 次重试在 **8 天**后，第 2 次在再 **8 天**后，第 3 次在再 **8 天**后；之后不再重试。

**例外/边界**：`retryCount` 由**历史失败次数**决定，而非当前会话——同一 payment 若历史已有 N 次 `PAYMENT_FAILURE`，本次失败直接跳到第 N+1 个间隔。

## BR-256 插件失败（网关宕机）的指数退避重试

- **类型**: 业务规则
- **同义词**: 网关失败重试, 指数退避, plugin failure retry, 300 秒, multiplier, 最大 8 次, gateway down
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:612-628`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:41-59`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:82-90`

**规则**：当最后一次 `PURCHASE` 交易状态为 `PLUGIN_FAILURE`（插件失败）时走指数退避（`getNextRetryDateForPluginFailure`）：

- `attemptsInState` = 该 payment 下 `PURCHASE` 中 `PLUGIN_FAILURE` 的条数；`retryAttempt = max(attemptsInState - 1, 0)`；
- 若 `retryAttempt >= org.killbill.payment.failure.retry.max.attempts`（默认 `8`）→ 返回 `null`（不再重试）；
- 否则 `nbSec = start × multiplier^(retryAttempt-1)`，其中 `start = org.killbill.payment.failure.retry.start.sec`（默认 `300`）、`multiplier = org.killbill.payment.failure.retry.multiplier`（默认 `2`）；通过循环 `while (--remainingAttempts > 0) nbSec *= multiplier`（`remainingAttempts` 初值=retryAttempt）实现：
  - `retryAttempt=1` → `300s`
  - `retryAttempt=2` → `600s`
  - `retryAttempt=3` → `1200s` …；
- 下次重试时间 = `createdDate + nbSec` 秒。

**含义**：`PAYMENT_FAILURE`（卡被拒）按"天"重试，`PLUGIN_FAILURE`（网关/连接失败）按"秒"指数退避——两条完全独立的计划。

## BR-257 失败类型决定是否重试：UNKNOWN 不重试、API 支付默认不重试

- **类型**: 业务规则
- **同义词**: 是否重试, 不重试情形, unknown not retried, api payment retry, IPCD_RETRIES, 重试判定分支
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:567-590`, `payment/src/main/java/org/killbill/billing/payment/core/sm/control/DefaultControlCompleted.java:91-106`

**规则**：`computeNextRetryDate` 的分支判定，以该 payment 下**最后一个 PURCHASE 交易**的状态为准：

| 最后 PURCHASE 状态 | 是否重试 | 依据 |
|---|---|---|
| `PAYMENT_FAILURE` | 是，按 `org.killbill.payment.retry.days`（默认 8,8,8） | BR-255 |
| `PLUGIN_FAILURE` | 是，按指数退避（默认 300s×2^n，最多 8 次） | BR-256 |
| `UNKNOWN` 或其他 | **否**（返回 null） | 代码 default 分支 |
| 无 PURCHASE 交易 | 否 | `purchasedTransactions.size()==0` |

**另外两条例外**：
- **API 发起的支付默认不重试**：`if (!ipcdRetries && isApiPayment) return null;`，除非控制插件属性 `IPCD_RETRIES=true`（默认 false）。
- **即使算出了重试日期，若交易处于 UNKNOWN 也不会真的入队**：`DefaultControlCompleted.enteringState` 中 `if (retriedState.equals(state) && !isUnknownTransaction())` 才 `scheduleRetry`，避免坏插件造成无限重试（UNKNOWN 交给 Janitor）。

## BR-258 Janitor 处理范围：只修 PENDING / UNKNOWN，且 UNKNOWN 不改状态

- **类型**: 业务规则
- **同义词**: janitor 处理范围, PENDING 修复, UNKNOWN 修复, incomplete transaction, 未决交易, 回查
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentTransactionTask.java:63`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentTransactionTask.java:119-155`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentTransactionTask.java:224-229`

**规则**：
- 常量 `TRANSACTION_STATUSES_TO_CONSIDER = [PENDING, UNKNOWN]`——只有这两种状态的交易会被 Janitor 巡检；其它状态直接返回当前状态（no-op）。
- 巡检时先对 account 加锁（`LockerType.ACCNT_INV_PAY`），锁内重新读交易（防止竞态），再次确认状态属于 `[PENDING, UNKNOWN]`。
- 插件回查 `getPaymentInfo` 得到结果后：若映射出的 `TransactionStatus` 仍是 `UNKNOWN`，则**保留原状态不变**（避免把 PENDING 错误降级）；匹配不到插件交易时用 `DefaultNoOpPaymentInfoPlugin(..., UNDEFINED)` 兜底。

## BR-259 Janitor 修复映射与写入（交易状态 → 支付状态）

- **类型**: 业务规则
- **同义词**: janitor 状态映射, 修复支付状态, repair state, errored state, failure state, pending state
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentTransactionTask.java:158-222`, `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:121-203`, `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentAutomatonDAOHelper.java:139-231`

**规则**：Janitor 得到新的 `TransactionStatus` 后按下表决定 `payments.state_name`（针对该交易的 transactionType）：

| 新 TransactionStatus | 目标 payment state |
|---|---|
| `SUCCESS` | `getSuccessfulStateForTransaction(type)` = `<TYPE>_SUCCESS` |
| `PENDING` | `getPendingStateForTransaction(type)` = `<TYPE>_PENDING` |
| `PAYMENT_FAILURE` | `getFailureStateForTransaction(type)` = `<TYPE>_FAILED` |
| `PLUGIN_FAILURE` | `getErroredStateForTransaction(type)` = `<TYPE>_ERRORED` |
| `UNKNOWN` | 跳过，不写库（无法从插件得到有用信息） |

**写入前提**：仅当新旧状态**确实不同**时才 `processPaymentInfoPlugin`（"Repairing..." 日志）；状态相同则只安排下一次回查通知（见 BR-261）。写入通过 `PaymentAutomatonDAOHelper.processPaymentInfoPlugin` 同时更新 `payments` 与 `payment_transactions`，并写 `processed_amount/processed_currency`、`gateway_error_*`；若新 state 是成功态则同时更新 `last_success_state_name`。

**身份**：修复调用使用 `CallOrigin.INTERNAL + UserType.SYSTEM`，调用方名 `IncompletePaymentTransactionTask`。

## BR-260 重试通知的键、队列与"成功后取消重试"

- **类型**: 业务规则
- **同义词**: 重试通知, retry notification, notification key, 取消重试, cancel scheduled retry, retry queue
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/retry/PaymentRetryNotificationKey.java:29-47`, `payment/src/main/java/org/killbill/billing/payment/retry/BaseRetryService.java:116-164`, `payment/src/main/java/org/killbill/billing/payment/retry/DefaultRetryService.java:31-46`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:159-205`, `payment/src/main/java/org/killbill/billing/payment/core/sm/control/CompletionControlOperation.java:101-108`

**规则**：
- retry 队列名 = `retry`（`DefaultRetryService.QUEUE_NAME`），服务名 = `payment-service-retry`；通知负载 `PaymentRetryNotificationKey{attemptId, paymentControlPluginNames}`（只有这两个字段，重试时靠 attemptId 回查其余参数）。
- 入队 API：`RetryServiceScheduler.scheduleRetry(objectType, objectId, attemptId, tenantRecordId, pluginNames, timeOfRetry)`；`null` 时间不排期。
- **成功即取消**：支付成功后 `CompletionControlOperation` 调用 `paymentProcessor.cancelScheduledPaymentTransaction(attemptId, ctx)`，从 retry 队列移除该 attemptId 的所有未来通知（`retryQueue.removeNotification(recordId)`）。
- 对外 getPayment 的 `withAttempts=true` 会把未来重试通知投影为 state=`SCHEDULED` 的虚拟 attempt（见 ENT-054）。

## BR-261 Janitor 通知调度、重试耗尽与锁失败重排

- **类型**: 业务规则
- **同义词**: janitor 通知, attemptNumber, 重试耗尽, 不再回查, lock failed, 重新排队, janitor schedule
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:378-418`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:129-148`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:61-79`

**规则**：
- 每次回查未修复时，`insertNewNotificationForUnresolvedTransactionIfNeeded` 将 `newAttemptNumber = attemptNumber + 1`，构造 `JanitorNotificationKey(paymentTransactionId, IncompletePaymentTransactionTask.class, isApiPayment, newAttemptNumber)` 后入队。
- 下次时间 `getNextNotificationTime(status, attemptNumber)`：`UNKNOWN → org.killbill.payment.janitor.unknown.retries`（默认 `5m,1h,1d,1d,1d,1d,1d`）；`PENDING → org.killbill.payment.janitor.pending.retries`（默认 `1h, 1d`）；取第 `attemptNumber-1` 个延迟；**若 `attemptNumber > 表长度` → 返回 null，不再入队（重试耗尽）**。
- 其它非 PENDING/UNKNOWN 状态会出现 log.warn "Unexpected transactionStatus from janitor, ignore..." 且 `retries` 为空 → 不再回查。
- **锁失败重排**：`processNotification` 捕获 `LockFailedException` 后，若交易仍是 PENDING/UNKNOWN，则以**同一个 attemptNumber** 重新走 `insertNewNotificationForUnresolvedTransactionIfNeeded`（内部再 +1），即继续下一次回查而不是丢弃。
- 负载中的 `isApiPayment` 会一路传递；老数据为 null 时按 **false** 处理。

**耗尽后的结果**：不再有新的 janitor 回查；交易停留在 `PENDING`/`UNKNOWN`；若之后插件侧状态变化，只能由新的操作（`PaymentProcessor.performOperation` 前的 on-the-fly Janitor）或 attempt 侧收尾再触发。

## BR-262 重试金额由 attempt.amount 驱动（而非 processedAmount）

- **类型**: 业务规则
- **同义词**: 重试金额, attempt amount, 使用请求金额, processed amount, 重试驱动金额, retry amount
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/control/DefaultControlCompleted.java:64-74`, `payment/src/main/java/org/killbill/billing/payment/core/PluginControlPaymentProcessor.java:315-331`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentRefresher.java:568-582`

**规则**：
- 每次状态流转时，`DefaultControlCompleted.enteringState` 用 `paymentStateContext.getAmount()`（**请求金额**，可能已被 priorCall 调整）更新 attempt，而**不是** `processedAmount`——因为请求金额才是驱动后续重试的金额（代码注释明确）。
- 重试执行时，`PluginControlPaymentProcessor.retryPaymentTransaction` 明确以 `attempt.getAmount()` 作为新交易的金额传给状态机（注释："payment attempt 上的金额驱动新支付交易的金额"）。
- 失败的交易 `processedAmount` 会被写成 `ZERO`（BR-254），因此如果误用 processedAmount 重试会变成 0 元——所以必须用 attempt.amount。

**含义**：`payment_attempts.amount` 是重试语义上的"应付金额"；`payment_transactions.processed_amount` 是"插件实收金额"，两者不可互换。

## BR-263 支付配置的全局属性 vs 租户级覆盖

- **类型**: 业务规则
- **同义词**: 全局配置, 租户配置, per-tenant config, tenant override, system property, payment config, 覆盖配置
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/config/MultiTenantPaymentConfig.java:45-141`, `util/src/main/java/org/killbill/billing/util/config/tenant/MultiTenantConfigBase.java:85-103`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:31-105`

**规则**：
- **全局**：通过系统属性（skife `@Config`）设置，如 `-Dorg.killbill.payment.retry.days=8,8,8`；见 `PaymentConfig` 各 `@Config`/`@Default`。
- **租户级覆盖**：`MultiTenantPaymentConfig` 实现带 `InternalTenantContext` 的重载；`getStringTenantConfig(methodName, tenantContext)` 以**方法名**为键从 `CacheConfig` 的 per-tenant 配置中取值 → 命中则覆盖静态值，未命中回退全局默认。
- **可租户级覆盖的支付属性**（有 `(InternalTenantContext)` 重载）：`getPaymentFailureRetryDays`、`getPluginFailureInitialRetryInSec`、`getPluginFailureRetryMultiplier`、`getUnknownTransactionsRetries`、`getPendingTransactionsRetries`、`getPluginFailureRetryMaxAttempts`、`getPaymentControlPluginNames`。
- **只能全局配置**（无租户重载）：`getJanitorRunningRate`、`getIncompleteAttemptsTimeSpanDelay`、`getDefaultPaymentProvider`、`getPaymentPluginTimeout`、`getPaymentPluginNb`、`getMaxGlobalLockRetries`、`isAllowedToOverwritePaymentMethodId`、`allowEmptyInvoice`。
- 列表值按分隔符拆分后再转类型（时间用 `TimeSpan::new`，天数为 `Integer::valueOf`）。

**含义**：同一个 Kill Bill 实例不同租户可以有**不同的重试计划/重试上限/默认控制插件**；但 Janitor 调度频率、超时等是进程级的。

## BR-264 priorCall 的链式执行、结果传递与短路

- **类型**: 业务规则
- **同义词**: 控制插件链, 插件顺序, priorCall 链, abort, 短路, plugin chain, 覆盖支付方式
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/control/ControlPluginRunner.java:64-156`, `payment/src/main/java/org/killbill/billing/payment/core/sm/control/OperationControlCallback.java:262-286`

**规则**：
- 按 `paymentControlPluginNames` 列表**顺序**逐个调用 `priorCall`；每个插件看到的是**上一个插件调整后**的 `paymentMethodId`/金额/币种/插件属性（结果逐级传递）。
- 插件名为**未注册**时：log.warn "Skipping unknown payment control plugin" 并 `continue`（不报错）。
- 任一插件返回 `isAborted()==true` → 立即抛 `PaymentControlApiAbortException(pluginName)`，后续插件不再执行。
- 全部执行完后，用最后一个结果 + 累积的 `inputPaymentMethodId/Amount/Currency/Properties` 重建 `DefaultPriorPaymentControlResult` 返回。
- **覆盖支付方式限制**：若插件返回 `AdjustedPaymentMethodId` 且原 `paymentMethodId != null`，而 `org.killbill.payment.method.overwrite=false`（默认）→ 抛 `PaymentControlApiException` 拒绝覆盖；仅当该配置为 true 才允许。
- `OperationControlCallback.adjustStateContextForPriorCall` 把最终调整写回状态上下文：`amount`、`currency`、`paymentMethodId`、`properties`（**`AdjustedPluginName` 不写回状态上下文**，只影响 runner 内部传给下一个插件的 `pluginName`）。

## BR-265 控制插件 abort 与 exception 的不同结果（ABORTED vs ERRORED/RETRIED）

- **类型**: 业务规则
- **同义词**: abort 结果, 控制插件异常, PAYMENT_PLUGIN_API_ABORTED, operation result, 中止状态, 422
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/control/OperationControlCallback.java:110-160`, `payment/src/main/java/org/killbill/billing/payment/core/sm/control/OperationControlCallback.java:172-176`, `payment/src/main/resources/org/killbill/billing/payment/retry/RetryStates.xml:29-67`

**规则**：

| 场景 | 抛出/动作 | OperationResult | 控制状态机结果 | 对外错误 |
|---|---|---|---|---|
| 插件 `priorCall` abort | `PaymentControlApiAbortException` → 包成 `PAYMENT_PLUGIN_API_ABORTED` | `EXCEPTION` | attempt → `ABORTED` | HTTP `422` |
| 插件 `priorCall` 抛 `PaymentControlApiException` | 直接包成 `OperationException` | `EXCEPTION` | attempt → `ABORTED` | 依 cause 映射 |
| 支付调用抛 `PaymentApiException` | 走 `onFailureCall` | `retryDate!=null ? FAILURE : EXCEPTION` | 有重试日期→`RETRIED`，否则→`ABORTED` | 依 cause |
| 支付调用抛其它 `RuntimeException` | 走 `onFailureCall` | 同上 | 同上 | 依 cause |

**关键**：`getOperationResultOnException` 用"是否存在 nextRetryDate"区分 FAILURE 与 EXCEPTION——**能重试才算"失败"（RETRIED），不能重试算"异常"（ABORTED）**。

## BR-266 控制插件的激活来源与顺序（per-request + 默认 + 发票强制）

- **类型**: 业务规则
- **同义词**: 控制插件激活, 插件列表来源, paymentControlPluginNames, 默认控制插件, invoice plugin, 插件优先级
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/api/DefaultApiBase.java:40-58`, `payment/src/main/java/org/killbill/billing/payment/api/svcs/InvoicePaymentPaymentOptions.java:37-55`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:92-100`, `payment/src/main/java/org/killbill/billing/payment/bus/PaymentBusEventHandler.java:86-123`

**规则**（`toPaymentControlPluginNames`）：
1. 读取全局/租户默认 `org.killbill.payment.invoice.plugin`（`getPaymentControlPluginNames`，默认空列表）；
2. 若调用方传入的 `paymentOptions.getPaymentControlPluginNames()` 为**空列表**且默认列表非空 → 返回 **默认插件列表**（特殊 JAX-RS 发票端点路径）；
3. 若调用方传入**非空** → 直接使用调用方列表（覆盖默认）；
4. 否则返回空列表（无控制插件）。

**发票端点的强制顺序**：`InvoicePaymentPaymentOptions.create` 调用 `addInvoicePaymentControlPlugin`，先把内置 `__INVOICE_PAYMENT_CONTROL_PLUGIN__` **放在列表首位**，再追加用户插件（若用户列表里已含则去重跳过）。

**自动扣款触发**：`PaymentBusEventHandler` 订阅 `InvoiceCreationInternalEvent`，以 `isApiPayment=false` 调用 `createPurchaseForInvoicePayment`，控制插件列表取 `paymentConfig.getPaymentControlPluginNames(internalContext)`（默认空 → 无控制插件时不自动扣款）。

**含义**：per-request 参数 > 全局/租户默认；发票支付永远先执行内置发票控制插件再执行其它控制插件。kb2 `ROLE-008` 的"未找到消费位置"由此补全。

## BR-267 PURCHASE（发票支付）金额分摊规则

- **类型**: 业务规则
- **同义词**: 发票支付金额, 部分支付, 余额上限, 分摊, invoice payment allocation, partial payment, invoice balance, validate amount
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:710-728`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:362-374`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:179-199`

**规则**（`validateAndComputePaymentAmount`）：
- 发票余额 ≤ 0 → 返回 `0`（再由空发票策略决定是否中止，见 kb2 BR-234）。
- 若为 **API 支付**且显式传入金额 > 发票余额 → 抛错 `PAYMENT_PLUGIN_EXCEPTION` "Invalid amount ... invoice balance is ..."。
- 否则返回 `min(inputAmount, invoice.getBalance())`；输入为 null 时返回发票余额（即"付清余额"）。

**记账金额（onSuccessCall）**：
- 若 `processedCurrency == invoice currency` → 发票入账金额 = `processedAmount`（支持部分支付/网关实收不同）。
- 若 `processedCurrency != invoice currency` → log.warn 并**假定为全额支付**，入账金额 = 请求 `amount`。

**两阶段**：priorCall 中先 `recordPaymentAttemptInit`（0 金额 INIT 记录）再真正扣款（见 WF-031）；成功后用 `recordPaymentAttemptCompletion` 把金额、processedCurrency 写回发票。

## BR-268 InvoicePaymentStatus 与 TransactionStatus 的映射

- **类型**: 业务规则
- **同义词**: 发票支付状态, invoice payment status, INIT, SUCCESS, PENDING, 状态映射
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:321-330`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:170-199`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:273-309`

**规则**（`toInvoicePaymentStatus`）：

| TransactionStatus | InvoicePaymentStatus |
|---|---|
| `SUCCESS` | `SUCCESS` |
| `PENDING` | `PENDING` |
| 其它（PAYMENT_FAILURE / PLUGIN_FAILURE / UNKNOWN） | `INIT` |

**使用**：
- `onSuccessCall`（PURCHASE）用该映射调用 `recordPaymentAttemptCompletion(..., status, ...)`；
- `onFailureCall`（PURCHASE）以 **amount=0** 且 `InvoicePaymentStatus.INIT` 调用 `recordPaymentAttemptCompletion`，即失败尝试在发票上留一条 INIT 记录但不增余额。

**含义**：发票侧的 `InvoicePaymentStatus` 只有 3 个值，任何失败/未知都收敛为 `INIT`。

## BR-269 REFUND 分摊与发票项调整（onSuccess/prior 双端）

- **类型**: 业务规则
- **同义词**: 退款分摊, recordRefund, 发票项调整, refund allocation, invoice item adjustment, isAdjusted, refund with adjustments
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:438-478`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:202-207`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultInvoicePaymentApi.java:93-119`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultInvoicePaymentApi.java:210-224`

**规则**：
- **参数组装**：`DefaultInvoicePaymentApi.createRefundForInvoicePayment` 注入 `IPCD_REFUND_WITH_ADJUSTMENTS=isAdjusted` 与 `IPCD_REFUND_IDS_AMOUNTS=adjustments`（若非 null）。
- **priorCall（`getPluginRefundResult`）**：
  - 请求金额为 0/null 且未给发票项 → 抛错中止；
  - `computeRefundAmount` 计算上限：显式退款金额必须 > 0（否则"需要指定正数退款金额"）；未显式时按 `idWithAmount` 逐项累加——每项可为 null（取该项原始金额）或显式金额（必须 > 0 且 ≤ 该项原始金额，否则"需要指定合法发票项金额"）；
  - 可退金额为 0 且为 API 支付 → 抛错中止；
  - 若 `isAdjusted=true` → 先 `validateInvoiceItemAdjustments(paymentId, idWithAmount)` 校验，失败则中止（退款前先校验）。
- **onSuccessCall**：调用 `invoiceApi.recordRefund(paymentId, attemptId, amount, isAdjusted, idWithAmount, transactionExternalKey, status, ctx)`，status 由 BR-268 映射。
- **不重试**：REFUND/CREDIT 的 `onFailureCall` 不设 `nextRetryDate`（见 kb2 WF-026）。

## BR-270 CHARGEBACK 分摊：不支持部分拒付

- **类型**: 业务规则
- **同义词**: 拒付分摊, chargeback amount, 部分拒付, no partial chargeback, 拒付金额, recordChargeback
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:209-232`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:147-148`

**规则**：
- CHARGEBACK 的 `priorCall` 直接允许（`DefaultPriorPaymentControlResult(false, amount)`），**不做发票前置校验**。
- `onSuccessCall`：先查是否已存在 chargeback（`getInvoicePaymentForChargeback`），若存在则跳过（**不支持部分拒付**，一笔支付只能拒付一次）。
- 拒付金额/币种优先级：
  1. `linkedInvoicePayment.currency == processedCurrency` 且 `processedAmount != null` → 用 `processedAmount/processedCurrency`；
  2. 否则 `linkedInvoicePayment.currency == currency` 且 `amount != null` → 用 `amount/currency`；
  3. 否则回退到 `linkedInvoicePayment` 自身的金额/币种。
- 成功调用 `recordChargeback(paymentId, attemptId, transactionExternalKey, amount, currency)`；失败调用 `recordChargebackReversal(...)` 冲销。

## BR-271 CREDIT 分摊（贷记复用退款接口 + legacy IPCD_PAYMENT_ID）

- **类型**: 业务规则
- **同义词**: 贷记分摊, credit allocation, recordRefund for credit, IPCD_PAYMENT_ID, 贷记无校验, credit TODO
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:234-250`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:480-483`, `payment/src/main/java/org/killbill/billing/payment/api/DefaultInvoicePaymentApi.java:122-154`

**规则**：
- `getPluginCreditResult`（priorCall）目前是 **TODO/无校验**：直接 `return new DefaultPriorPaymentControlResult(false, paymentControlPluginContext.getAmount())`——不校验金额/发票项。
- `onSuccessCall`（CREDIT）：读 `IPCD_REFUND_WITH_ADJUSTMENTS`、`IPCD_REFUND_IDS_AMOUNTS`，并读 legacy `IPCD_PAYMENT_ID` 作为关联的原始支付 id（缺省用当前 paymentId），最终调用与退款相同的 `invoiceApi.recordRefund(...)`。
- 组装入口 `DefaultInvoicePaymentApi.createCreditForInvoicePayment` 额外注入 `IPCD_PAYMENT_ID = originalPaymentId`。

**含义**：贷记在发票侧与退款走同一条 `recordRefund` 路径；区别在于关联的是"原始支付"而非被退交易，且前置校验薄弱（可能需人工关注）。

## BR-272 不完整发票支付的自动修复规则

- **类型**: 业务规则
- **同义词**: 发票支付修复, incomplete invoice payment, 半完成支付, repair, paymentCookieId, 状态纠正
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:655-708`

**规则**（`getAndSanitizeInvoice` → `checkForIncompleteInvoicePaymentAndRepair`）：
- 取发票所有 `InvoicePayment`，找第一条 `type == ATTEMPT && status != SUCCESS` 的"不完整"记录；
- 用该记录的 `paymentCookieId` 查 `payment_transactions`，找是否存在 `TransactionStatus == SUCCESS` 的交易；
- **若存在** → 认为"支付其实成功了、发票侧漏记"，调用 `recordPaymentAttemptCompletion(invoiceId, 成功交易的 amount, currency, processedCurrency, paymentId, attemptPaymentId, transactionExternalKey, createdDate, SUCCESS)` 修复，然后**重新拉取发票**继续后续校验；
- **若不存在** → 不修复，继续正常支付流程。

**已知局限（代码注释）**：若匹配交易处于 `UNKNOWN`/`PENDING`，当前实现会**忽略该场景**——因为"修可能没付、不修可能双付"，代码选择忽略，可能导致极端场景下的双扣（需人工退款）。

## BR-273 AUTO_PAY_OFF 的持久化表与解除后的重排

- **类型**: 业务规则
- **同义词**: auto pay off 记录, 自动支付关闭持久化, 解除自动支付关闭, removal reschedule, invoice_payment_control_plugin_auto_pay_off
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:312-319`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:730-745`, `payment/src/main/java/org/killbill/billing/payment/invoice/dao/InvoicePaymentControlDao.java:46-97`, `payment/src/main/resources/org/killbill/billing/payment/ddl.sql:213-229`

**规则**：
- **挂起时**：非 API 支付且账户带 AUTO_PAY_OFF → `insert_AUTO_PAY_OFF_ifRequired` 向表 `invoice_payment_control_plugin_auto_pay_off` 插一条 `(attempt_id, payment_external_key, transaction_external_key, account_id, plugin_name, payment_id, amount, currency, created_by, created_date)`，中止支付（见 kb2 BR-231）。
- **查询**：`getAutoPayOffEntry(accountId)` 仅取 `is_active = TRUE` 的记录。
- **解除时**（`process_AUTO_PAY_OFF_removal`）：对每条挂起记录调用 `retryServiceScheduler.scheduleRetry(ObjectType.ACCOUNT, accountId, cur.getAttemptId(), tenantRecordId, List.of(PLUGIN_NAME), internalCallContext.getCreatedDate())`，然后 `removeAutoPayOffEntry(accountId)`（软删除，`is_active = FALSE`）。
- **注意**：重排时传入的 `timeOfRetry = createdDate`（即**立即**），且控制插件列表固定为 `[__INVOICE_PAYMENT_CONTROL_PLUGIN__]`（TODO 注释指出未保留原始插件列表）。

## BR-274 单支付未决(PENDING)交易的并发保护

- **类型**: 业务规则
- **同义词**: 并发支付, pending 保护, 重复扣款, pending transaction, completion candidate, 未决交易
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:352-385`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:145-157`

**规则**：
- 构建状态上下文时，对 AUTHORIZE / PURCHASE / CREDIT：若同一 payment 下已存在 `PENDING` 交易，且本次调用**未携带**该交易的 id 或 externalKey → 抛 `PAYMENT_INVALID_OPERATION`（防并发重复扣款）。
- 若调用携带了交易 id/key 但该交易状态为 `UNKNOWN` → 直接抛 `PAYMENT_INVALID_OPERATION`（因为 UNKNOWN 在状态机中无法定位，且 UNKNOWN 与 PLUGIN_FAILURE 都被视为 EXCEPTION）。
- 若交易 id/key 对应 PENDING/UNKNOWN → 作为**完成候选**（completion candidate）加入，最多允许 1 个（`Preconditions` 校验），用于把未决交易推进到终态。
- `notifyPendingPaymentOfStateChanged`：只接受 `PENDING` 的交易，否则抛 `PAYMENT_NO_SUCH_SUCCESS_PAYMENT`；根据 `isSuccess` 用 `OperationResult.SUCCESS/FAILURE` 覆盖插件结果并 `runJanitor=false` 重跑。

## BR-275 外部支付插件不提供 getPaymentInfo，因而不被 Janitor 修正

- **类型**: 业务规则
- **同义词**: 外部支付回查, getPaymentInfo 空, no plugin info, external payment refresh, 默认支付提供者
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/provider/ExternalPaymentProviderPlugin.java:88-96`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentTransactionTask.java:231-258`, `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:112-116`

**规则**：
- `ExternalPaymentProviderPlugin.getPaymentInfo(...)` 恒返回**空列表**；`searchPayments` 也返回空分页。
- `IncompletePaymentTransactionTask.getLatestPaymentTransactionInfoPlugin` 在插件结果里按 `kbTransactionPaymentId` 匹配，匹配不到时用 `DefaultNoOpPaymentInfoPlugin(..., UNDEFINED)` 兜底 → 得到 `UNKNOWN` → Janitor 保留原状态、不修复。
- 因此绑定到 `__EXTERNAL_PAYMENT__` 的支付**不参与插件回查**；其记录型支付天然是终态。
- `org.killbill.payment.provider.default` 默认 `__external_payment__` 指定默认支付提供者。

## BR-276 on-the-fly Janitor 的触发点与例外

- **类型**: 业务规则
- **同义词**: 即时 janitor, on-the-fly, 查询前修复, GET 修复, refresh before read, 触发时机
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/PaymentRefresher.java:113-124`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentRefresher.java:126-161`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentRefresher.java:463-489`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:282-290`

**规则**：
- 任何 GET（`getPayment`/`getPaymentByExternalKey`/`getAccountPayments`/`getPayments`）在把 DAO 交易转换为 API 对象前，都会对每条交易调用 `invokeJanitor`（on-the-fly），用**当次已取得的插件信息**修正本地状态；若发生修正则重新读 payment/transaction。
- 支付操作（`performOperation`）除 `notifyPendingPaymentOfStateChanged`（`runJanitor=false`）外，都会在推进状态机**之前**调用 Janitor（`payment/src/main/java/org/killbill/billing/payment/core/PaymentProcessor.java:286-290`）。
- on-the-fly Janitor **不插入**下一次通知（`attemptNumber == null` 时 `shouldInsertNotification=false`），只有带 attemptNumber 的队列路径才会排下一次回查。
- 批量路径为避免重复修正，会把转换结果 `List.copyOf` 固定。

**含义**：状态修正的入口有两个——**读/写时即时修正**与**后台队列回查**；即时路径不产生后续调度。

## BR-277 支付内部事件驱动 Janitor 入队（attemptNumber=0→1）

- **类型**: 业务规则
- **同义词**: 支付事件, payment internal event, janitor 事件触发, processPaymentEvent, bus event, 异步回查
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/Janitor.java:147-149`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:150-162`, `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:378-399`, `payment/src/main/java/org/killbill/billing/payment/bus/PaymentBusEventHandler.java:146-152`

**规则**：
- `PaymentBusEventHandler.processPaymentEvent` 订阅 `PaymentInternalEvent`，交给 `janitor.processPaymentEvent(event)` → `IncompletePaymentAttemptTask.processPaymentEvent`。
- 若事件状态**不属于** `[PENDING, UNKNOWN]` → 直接返回（不排期）。
- 若是 → 以 `attemptNumber = 0` 调用 `insertNewNotificationForUnresolvedTransactionIfNeeded`；内部 `newAttemptNumber = 0 + 1 = 1`，即第一次回查对应延迟表的第 1 个元素（UNKNOWN 为 `5m`，PENDING 为 `1h`）。
- 事件的 `isApiPayment` 透传到通知键；`searchKey1/searchKey2` 作 accountRecordId/tenantRecordId。

**含义**：PENDING/UNKNOWN 交易一旦产生对应 bus 事件，就会自动排入 janitor 队列回查；`attemptNumber` 从 1 开始计数。

## BR-278 CHARGEBACK_PENDING 状态不存在于状态机 XML（不一致）

- **类型**: 业务规则
- **同义词**: 拒付 pending, CHARGEBACK_PENDING, 缺失状态, gap, 状态不一致, chargeback pending
- **模块**: payment
- **置信度**: 🟡 inferred
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:63`, `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:142-161`, `payment/src/main/resources/org/killbill/billing/payment/PaymentStates.xml:379-409`

**说明**：`PaymentStateMachineHelper` 定义了常量 `CHARGEBACK_PENDING`，且 `getPendingStateForTransaction(CHARGEBACK)` 会返回 `"CHARGEBACK_PENDING"`；但 `PaymentStates.xml` 的 `CHARGEBACK` 子状态机只有 `CHARGEBACK_INIT` / `CHARGEBACK_SUCCESS` / `CHARGEBACK_FAILED` / `CHARGEBACK_ERRORED`，**没有 `CHARGEBACK_PENDING` 状态**，也没有 `PENDING` 的转移。

**影响**：由于 CHARGEBACK 交易在状态机层面无法进入 PENDING，实践中不会触发 `getPendingStateForTransaction(CHARGEBACK)`；但该常量的存在意味着若未来给 CHARGEBACK 增加 PENDING 转移，此处已预留。标为 🟡（由代码与 XML 对比推断，非直接异常）。

## BR-279 内置发票控制插件只接受 4 种交易类型

- **类型**: 业务规则
- **同义词**: 发票控制插件交易类型, PURCHASE REFUND CHARGEBACK CREDIT, 校验断言, unsupported transaction, Preconditions
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:133-153`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:159-164`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:255-257`

**规则**：
- `priorCall` 与 `onSuccessCall` 都用 `Preconditions.checkArgument` 断言交易类型 ∈ `{PURCHASE, REFUND, CHARGEBACK, CREDIT}`，且 `PaymentApiType == PAYMENT_TRANSACTION`；否则抛 `IllegalArgumentException`。
- `priorCall` 分派：PURCHASE→`getPluginPurchaseResult`、REFUND→`getPluginRefundResult`、CHARGEBACK→直接允许、CREDIT→`getPluginCreditResult`（TODO）。
- `onSuccessCall` 分派：PURCHASE→`recordPaymentAttemptCompletion`、REFUND→`recordRefund`、CHARGEBACK→`recordChargeback`、CREDIT→`recordRefund`。
- **异常吞掉**：`onSuccessCall` 内 `InvoiceApiException` 只 log.warn，不抛出（记账失败不回滚支付）；`onFailureCall` 内 CHARGEBACK reversal 的 `InvoiceApiException` 也只 log.warn。

## BR-280 isApiPayment 语义及其对重试/事件的影响

- **类型**: 业务规则
- **同义词**: isApiPayment, API 支付标识, 重试必须 true, 内部调用, 系统扣款, payment origin
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentAttemptTask.java:205-218`, `payment/src/main/java/org/killbill/billing/payment/core/sm/payments/PaymentEnteringStateCallback.java:59-82`, `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:567-572`

**规则**：
- `isApiPayment` 表示该支付是否由外部 API 调用发起（true）还是系统/内部触发（false，如自动扣款、Janitor、重试）。
- **重试前提**：`isApiPayment` 必须为 true 才会真正重试（Kill Bill issue #880）——Janitor 的 attempt 收尾以 `isApiPayment=true` 触发时才能让失败支付进入重试。
- 影响一：API 支付失败默认不重试（除非 `IPCD_RETRIES=true`）；
- 影响二：`PaymentEnteringStateCallback` 中若"无交易可更新"（如缺少默认支付方式）且 `isApiPayment=false`，会发送 `DefaultPaymentErrorEvent`（bus `PAYMENT_ERROR`，消息 "Early abortion of payment transaction"）；API 支付则不发。
- Janitor 重试/收尾内部调用用 `isApiPayment=false`，但注意代码注释指出：由控制插件触发、却以 INIT 崩溃的 API 支付在 attempt Janitor 循环里可能被当作非 API 修复（边缘情况）。

## BR-281 支付尝试插件属性的序列化与敏感信息擦除

- **类型**: 业务规则
- **同义词**: attempt 属性, 插件属性序列化, plugin_properties, 敏感信息擦除, CVV, serialize properties
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/sm/control/DefaultControlInitiated.java:119-134`, `payment/src/main/java/org/killbill/billing/payment/core/sm/control/DefaultControlCompleted.java:64-74`, `payment/src/main/java/org/killbill/billing/payment/dao/PaymentAttemptModelDao.java:118-124`, `payment/src/main/resources/org/killbill/billing/payment/ddl.sql:16-17`

**规则**：
- attempt 创建（`DefaultControlInitiated`）时**不序列化任何插件属性**（`PluginPropertySerializer.serialize(Collections.emptyList())`），避免把敏感信息（如 CVV）落库；
- 只有当 attempt 进入 `RETRIED`（即控制插件给出了重试日期）时，`DefaultControlCompleted.enteringState` 才把当时的 `paymentStateContext.getProperties()` 序列化写入 `payment_attempts.plugin_properties`（mediumblob）；
- 设计契约：**任何设置了重试日期的控制插件有责任在此之前擦除敏感信息**（代码注释明确说明）；
- 重试/收尾时（attempt Janitor、`retryPaymentTransaction`、`notifyPendingPaymentOfStateChanged`）通过 `PluginPropertySerializer.deserialize(attempt.getPluginProperties())` 还原属性。

## BR-282 跟踪号幂等去重

- **类型**: 业务规则
- **同义词**: 跟踪号去重, 幂等, 重复提交拦截, usage dedup, tracking id duplicate, idempotency, 重复用量
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:74-82`, `usage/src/main/java/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.java:36-39`

**规则**：调用方传入非空 `trackingId` 时，先查该订阅下是否已存在相同 `trackingId` 的行（`recordsWithTrackingIdExist`，SQL `select 1 ... where subscription_id=? and tracking_id=? ... limit 1`）。若已存在 → 抛 `UsageApiException(ErrorCode.USAGE_RECORD_TRACKING_ID_ALREADY_EXISTS, trackingId)`，整批用量不落库。

**范围**：去重键是 `(subscription_id, tracking_id, tenant_record_id)`（索引 `rolled_up_usage_tracking_id_subscription_id_tenant_record_id`）。因此同一 trackingId 在**不同订阅**下互不影响。

---

## BR-283 未提供跟踪号时自动生成

- **类型**: 业务规则
- **同义词**: 自动跟踪号, 随机跟踪号, 默认trackingId, auto tracking id, generated tracking id, random tracking id
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:74-82`

**规则**：若 `record.getTrackingId()` 为 `null` 或空字符串，则本次提交生成一个随机 UUID 作为 `trackingId`。此时该批次不具备调用方可控的幂等键（每次提交都会是新值，无法借此拦截重复）。

---

## BR-284 同一批提交共用同一跟踪号

- **类型**: 业务规则
- **同义词**: 批量共用跟踪号, 同批trackingId, batch tracking id, shared tracking id, 同批次幂等
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:85-91`

**规则**：`recordRolledUpUsage` 对入参中所有 `UnitUsageRecord` × 所有 `UsageRecord` 展开出的每一行，都写入**同一个** `trackingIds` 变量值（要么是调用方给的，要么是生成的随机值）。因此去重探测的粒度是「整批」，只要有任意一行已存在该 trackingId，整批都会被拒。

---

## BR-285 订阅用量查询：半开区间 [start, end) + 单位类型过滤

- **类型**: 业务规则
- **同义词**: 用量查询时间范围, 半开区间, 用量区间, usage query range, start end date, record_date filter
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:37-48`, `usage/src/main/java/org/killbill/billing/usage/dao/DefaultRolledUpUsageDao.java:55-58`

**规则**：`getUsageForSubscription` 的 SQL 条件为 `record_date >= :startDate AND record_date < :endDate AND unit_type = :unitType` 且租户匹配。即左闭右开；结束时刻当刻的用量不计入。

**注意**：`unitType` 是**必须精确匹配**的过滤条件（非空时），无法用它做模糊/多值查询。查询单一单位类型用此方法。

---

## BR-286 账户原始用量查询：闭区间 [start, end]（开票唯一查询）

- **类型**: 业务规则
- **同义词**: 账户用量查询, 开票用量查询, 闭区间, 含退订日, raw usage for account, account usage, invoicing usage query
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:62-73`, `usage/src/main/java/org/killbill/billing/usage/api/svcs/DefaultInternalUserApi.java:63-84`

**规则**：`getRawUsageForAccount` 的 SQL 条件为 `account_record_id = :accountRecordId AND record_date >= :startDate AND record_date <= :endDate`（**右闭**），且租户匹配。模板注释明确说明：「这是唯一用于开票的查询，因此使用 `<= :endDate` 以便处理退订当日的用量数据」。

**含义**：订阅维度的查询用 `< endDate`，而开票维度的账户查询用 `<= endDate`，两者边界语义不同，不能混用。

**范围**：该方法按 `account_record_id` 跨该账户下所有订阅查询，返回全部单位类型的明细（无 `unit_type` 过滤）。

---

## BR-287 用量按单位类型汇总求和

- **类型**: 业务规则
- **同义词**: 用量汇总, 求和, 聚合, rollup sum, aggregate usage, sum by unit type
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:158-168`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:136-156`

**规则**：无论数据来自 DB（`getRolledUpUnits`）还是插件（`getRolledUpUnitsForRawPluginUsage`），都用一个 `Map<String, BigDecimal>` 以 `unitType` 为键累加 `amount`（`currentAmount.add(cur.getAmount())`），最后映射为 `RolledUpUnit` 列表。

**含义**：查询结果是**同一区间内同单位类型的数值之和**；重复日期、多行记录都会被累加，不会保留明细。

**插件分支的额外过滤**：插件返回的原始记录会先按 `subscriptionId` 过滤（不等则跳过），再在指定 `unitType` 时按单位类型过滤，之后才求和。

---

## BR-288 查询结果排序：按 record_id 升序（提交顺序）

- **类型**: 业务规则
- **同义词**: 用量排序, 查询顺序, 提交顺序, order by record_id, usage ordering, insertion order
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:46-47`, `util/src/main/resources/org/killbill/billing/util/entity/dao/EntitySqlDao.sql.stg:31-33`

**规则**：所有用量查询都带 `<defaultOrderBy("")>`，展开为 `order by record_id ASC`。`record_id` 是自增 serial 主键，故返回顺序即**落库（提交）先后顺序**，而非按 `record_date` 排序。

**注意**：不要假设结果按日期升序；如需按日期处理，调用方须自行排序（开票侧 `RawUsageOptimizer` 即自行按 endDate 排序）。

---

## BR-289 同一 (订阅, 单位类型, 日期) 重复提交会累加，不覆盖

- **类型**: 业务规则
- **同义词**: 重复用量, 用量覆盖, 用量累加, duplicate usage, overwrite, additive, 重复记录
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/ddl.sql:18`, `usage/src/main/java/org/killbill/billing/usage/api/user/DefaultUsageUserApi.java:158-168`, `usage/src/test/java/org/killbill/billing/usage/dao/TestDefaultRolledUpUsageDao.java:139-169`

**规则**：`rolled_up_usage` 唯一的唯一索引建在 `id`（随机 UUID）上，**没有** `(subscription_id, unit_type, record_date)` 的业务键唯一约束。因此：
- 用不同 `trackingId` 对同一订阅、同一单位类型、同一日期再次提交，会新增行，查询时被求和 → **数值翻倍（累加而非覆盖）**。
- 没有任何「更新/覆盖」用量的 API；用量是**只追加（append-only）**的（DAO 无 update 方法，实体 `getHistoryTableName()` 为 `null`）。
- 测试 `testDuplicateRecords` 展示的是「把同一批 `RolledUpUsageModelDao`（含固定 `id`）插入两次」会因唯一索引 `rolled_up_usage_id` 冲突抛 `UnableToExecuteStatementException`——即只有**相同记录 ID**才会被拒。

**业务结论**：去重的唯一可靠手段是 `trackingId`（见 BR-282）；不要依赖系统对「同日期重复上报」自动去重。

---

## BR-290 插件优先：插件返回非 null（含空列表）即不查库

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

---

## BR-291 插件越界数据仅告警，不拒绝

- **类型**: 业务规则
- **同义词**: 插件数据校验, 越界告警, plugin out of range, usage warning, date range warning
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/api/BaseUserApi.java:77-90`

**规则**：对插件返回的每条 `RawUsageRecord`，若其 `date` 落在请求区间之外（`date < startDate || date >= endDate`），仅记录 `warn` 日志（"Usage plugin returned usage data with date {}, not in the specified range"），**仍然原样返回给调用方**，不做过滤或拒绝。

**含义**：插件数据可能包含区间外的点，过滤责任在下游（开票侧按自己的区间切分）。这是 `>= endDate` 的右开判断，与 BR-285 的半开区间一致。

---

## BR-292 聚合语义：CAPACITY 取最大值，CONSUMABLE 求和

- **类型**: 业务规则
- **同义词**: 容量取最大, 消费求和, 用量聚合, capacity max, consumable sum, usage aggregation, 峰值计费, 累加计费, 用量合并
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:539-548`

**规则**（开票侧聚合，用量数据的使用方语义）：对同一单位类型在一段计费区间内的多次观测值 `computeUpdatedAmount(current, new)`：
- `UsageType.CAPACITY` → 返回 `max(current, new)`（区间峰值）。
- 否则（`UsageType.CONSUMABLE`）→ 返回 `current.add(new)`（多点累加）。
- 任一侧为 `null` 视为 `ZERO` 再参与运算。

**用量侧关联**：用量模块本身按 BR-287 对查询区间求和；CAPACITY 的「取最大」发生在开票消费这些原始/汇总数据时（`SubscriptionUsageInArrear` 按 usageType 选择不同 interval 实现，见 `invoice/.../SubscriptionUsageInArrear.java:188-193`）。

---

## BR-293 单位类型来源：CAPACITY→limit，CONSUMABLE→tier block

- **类型**: 业务规则
- **同义词**: 单位类型映射, 目录单位, capacity limit unit, consumable tier unit, unit type catalog link
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:34-87`

**规则**（目录→开票的映射，用量 `unitType` 必须与之对齐）：
- CONSUMABLE IN_ARREAR：单位类型集合 = 各 tier 的 `TieredBlock.getUnit().getName()`；取价时对每个 tier 找匹配 `unitType` 的 block，且要求每个 tier 都有该 unit 的定义（否则 `Preconditions.checkState` 失败）。
- CAPACITY IN_ARREAR：单位类型集合 = 各 tier 的 `Limit.getUnit().getName()`。

**对用量模块的含义**：写入的 `unitType` 是字符串，若与目录声明的 unit 名不匹配，则开票无法定价；此一致性不由用量模块强制（见 BR-295）。

---

## BR-294 用量存储层不区分 CONSUMABLE / CAPACITY

- **类型**: 业务规则
- **同义词**: 存储不区分类型, 用量类型无关存储, usage type agnostic storage, storage semantics
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/dao/RolledUpUsageModelDao.java:30-36`, `usage/src/main/resources/org/killbill/billing/usage/ddl.sql:4-16`

**规则**：`rolled_up_usage` 表与 `RolledUpUsageModelDao` **没有**任何字段表示 usageType/billingMode。无论消费型还是容量型，用量记录都写同样的列（`subscription_id`/`unit_type`/`record_date`/`amount`/`tracking_id`）。

**含义**：CAPACITY vs CONSUMABLE 的差异完全由（a）目录定义与（b）开票聚合决定，用量模块只提供中立的事实数据。回答「某一用量是消费型还是容量型」时，不能从用量表判断，必须查目录中的 usage 定义。

---

## BR-295 未在目录中定义的用量：可 park 账户（配置驱动）

- **类型**: 业务规则
- **同义词**: 未知用量, 未定义用量, park账户, unknown usage, park accounts, usage not in catalog, 未知用量挂起, park account, 挂起账户, parkAccountsWithUnknownUsage, 账户暂停
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:205-213`

**规则**：系统属性 `org.killbill.invoice.parkAccountsWithUnknownUsage`（默认 `false`）控制：当账户记录了目录中未定义的用量数据时，是否将该账户 park（暂停自动开票，直到人工介入）。

**含义**：这是用量数据与目录一致性问题（BR-293）的兜底策略，由开票侧读取，用量模块不读取该配置。

---

## BR-296 用量提交的必填校验

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

---

## BR-297 退订后不得记录晚于生效结束日的用量

- **类型**: 业务规则
- **同义词**: 退订用量校验, 生效结束日, cancel usage, effective end date, usage after cancellation
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/UsageResource.java:134-141`, `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/UsageResource.java:150-158`

**规则**：记录用量前，先按 `subscriptionId` 取订阅（entitlement）；若其 `getEffectiveEndDate()` 非 null（即已退订/已结束），则取本次提交中所有用量记录的**最大 `recordDate`**；若 `effectiveEndDate < highestRecordDate` → 返回 400 Bad Request。

**含义**：不允许为已结束订阅记录结束日之后的用量。注意这是 API 层校验，不写在 `DefaultUsageUserApi` 内。

---

## BR-298 用量相关系统属性（配置项清单）

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

---

## BR-299 CAPACITY 档位选择：取第一个「所有单位都 ≤ max」的档

- **类型**: 业务规则
- **同义词**: 容量选档, 峰值选档, 容量取档, capacity tier selection, first matching tier, 档位匹配
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalCapacityUsageInArrear.java:104-153`

**规则**：按 catalog 中 tiers 的顺序遍历。对每个候选档：

1. 对每个参与计价的单位类型 `ro`，取该档中单位名匹配的 `limit`（`getTierLimit`；若该档缺该单位的 limit → `checkState(false)`，视为目录错误，见 BR-316）。
2. 若该单位的峰值（`RolledUpUnit.amount`；区间内 CAPACITY 取最大值，见既有 BR-292）`> limit.max` 且 `max ≠ -1` → 本档不满足，进入下一档。
3. 所有单位都满足 → **命中该档并立即返回**（取第一个命中档）。

**含义**：CAPACITY 的「峰值」是**区间内每个单位类型各自取 max**（而非各单位的和），然后选取能同时容纳所有单位峰值的**最低档**。档位必须连续（注释说明：因此只看 max、忽略 min）。

---

## BR-300 CAPACITY 金额 = 命中档的 recurringPrice；忽略 min；支持 $0

- **类型**: 业务规则
- **同义词**: 容量计价, 容量价格, capacity pricing, recurringPrice 计价, 档位价格, 忽略min
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalCapacityUsageInArrear.java:123-147`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:109-112`

**规则**：命中档的应计金额 = 该档 `recurringPrice.getPrice(getCurrency())`（**不是** `fixedPrice`，**也不是**「单价 × 单位数」）。代码注释明确：忽略 min，只看 max，因为档位应当连续。

**$0 支持**：若所有参与单位的量都 `≤ 0`（`allUnitAmountToZero`），则将金额置为 `0`，以便生成 $0 usage 项（见 BR-313）。

**明细**：为每个单位类型各记一条 `UsageInArrearTierUnitDetail(tierNum, unitType, tierPrice=命中档价格, quantity=观测峰值)`（每个单位类型只记一次，`perUnitTypeDetailTierLevel` 去重）。

---

## BR-301 哨兵值 -1 / 缺省 = 「无上限」

- **类型**: 业务规则
- **同义词**: 无上限, 无限制, 哨兵值, sentinel max, unlimited, -1 max, 无限档, 最后档
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalCapacityUsageInArrear.java:132-136`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:239-241`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogSafetyInitializer.java:36-38`

**规则**：`limit.max` 或 `tieredBlock.max` 等于 `-1` 表示**无上限**，代码用常量 `new BigDecimal("-1")` 比较。由于 `CatalogSafetyInitializer` 会把 catalog 中未配置的 `BigDecimal` 字段统一填为 `-1`，**「未写 max」等价于无上限**。

**分支语义**：

- CAPACITY：`max == -1` 时该单位恒满足，不再比较（常用于最后一档，使配置校验通过）。
- CONSUMABLE `ALL_TIERS`：`max == -1` 时不封顶，该档消费全部剩余单位。
- CONSUMABLE `TOP_TIER`：`tmp > max` 中 `max=-1` 恒成立（注意其后果，见 BR-303）。

---

## BR-302 CONSUMABLE · ALL_TIERS：逐档分块累进计价

- **类型**: 业务规则
- **同义词**: 累进计价, 阶梯计价, 逐档分块, all tiers, progressive pricing, block tiering, 分档计费
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:219-266`

**规则**（对每个单位类型独立计算；`units` 为该区间用量）：

1. 从第 1 档开始，对每档的 `tieredBlock`：`tmp = ceil(remainingUnits / size)`（`divideAndRemainder`，余数非 0 则商 +1）。
2. 若 `max ≠ -1` 且 `tmp > max` → 本档用满 `max` 块，`remainingUnits -= max × size`，继续下一档；否则本档用 `tmp` 块，`remainingUnits = 0`。
3. 每档金额 = `tierPrice × nbUsedTierBlocks`；总金额 = 各档金额之和（`UsageConsumableInArrearAggregate`）。
4. 生成明细的条件：`tierNum == 1`（即使 0 块也生成，用以支持 $0）或本档 `nbUsedTierBlocks > 0`。

**含义**：这是**累进/阶梯**计价——每档只计价落入自己区间的块数。例如 size=1000、max=10（即 ≤10000 单位）在 0.5/块，超出部分进入下一档按该档价计。

---

## BR-303 CONSUMABLE · TOP_TIER：整段用量按命中的单一档计价

- **类型**: 业务规则
- **同义词**: 顶档计价, 单档计价, 命中档计价, top tier, flat tier pricing, 最高档
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:268-299`

**规则**：

1. 顺序遍历档，累减 `remainingUnits`：对每档计算 `tmp = ceil(remainingUnits / size)`；若 `tmp > max` → `remainingUnits -= max × size` 并继续；否则 `targetTier = 本档`、停止。
2. 默认 `targetTier` = 最后一档（遍历未命中时）。
3. 最终**块数用「总 units」而非剩余量**计算：`nbBlocks = ceil(units / targetTier.size)`；`amount = targetTier.price × nbBlocks`。

**含义**：整段用量按所落的**那一个档**的单价计算（非累进），即「达到某档后整量按该档计费」。

**注意**：由于 `tmp > max` 在 `max=-1` 时恒成立，配置为无上限（-1）的档在循环中**会被跳过**；只有循环自然结束才回落到最后一档。因此 TOP_TIER 的最后一档通常应配置为 -1。

---

## BR-304 金额按货币精度舍入（KillBillMoney.of）

- **类型**: 业务规则
- **同义词**: 金额取整, 货币精度, 金额舍入, rounding, KillBillMoney, 四舍五入
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:322-326`

**规则**：分档/分块算出的原始金额 `toBeBilledUsageUnrounded` 乘以/相加得到后，先用 `KillBillMoney.of(amount, currency)` 按该货币的小数精度舍入，得到 `toBeBilledUsage`（对应 killbill issue #1124）。**所有后续冲抵、输出均使用舍入后的金额**。

---

## BR-305 已开票金额冲抵：实际开票 = 应计 − 已开票

- **类型**: 业务规则
- **同义词**: 冲抵, 已开票扣减, 重复计费防护, reconcile, billed usage offset, amountToBill
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:561-598`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalCapacityUsageInArrear.java:78-96`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:88-101`

**规则**：

- `computeBilledUsage` 把同一 usage 段、同一区间、**已存在的 USAGE 发票项的金额相加**（按金额，而非按量）。
- `getBilledItems` 只挑出同 usage 名、且 `[startDate,endDate]` 被已有项完全覆盖的 USAGE 项；长度为 0 的同日项会被排除（避免同日换套餐重复）。
- 实际开票金额 `amountToBill = 应计(toBeBilledUsage) − 已开票(billedUsage)`。

**负值处理**：`amountToBill < 0` 时——dry-run 或 `org.killbill.invoice.usage.missing.lenient=true` → 静默跳过；否则抛 `InvoiceApiException`（`ILLEGAL INVOICING STATE: Usage period start=..., end=..., amountToBill=...`）。

**何时不生成项**：已开票过该区间且 `amountToBill == 0` → 不生成（除非从未开票）。

---

## BR-306 明细模式 + ALL_TIERS 下改用「按档扣减」而非金额冲抵

- **类型**: 业务规则
- **同义词**: 明细不冲抵, 分档对账, detail offset, ALL_TIERS reconcile, 按档扣减
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:78-121`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:156-197`

**规则**：当 `tierBlockPolicy == ALL_TIERS` **且**历史发票项都带 `itemDetails`（`areAllBilledItemsWithDetails`）时，`amountToBill` 直接等于应计金额（**不再减** `billedUsage`）——因为冲抵转为「按档减历史量」：`getBilledDetailsForUnitType` 从历史发票项的 `itemDetails` 中抽取该单位类型的各档 quantity，用 `TreeMap`（按档号升序）合并，同档用 `updateQuantityAndAmount` 累加，随后在分档计算时从 `nbUsedTierBlocks` 中扣除（见 BR-307）。TOP_TIER 与非明细历史仍走 BR-305 的金额冲抵。

**DETAIL vs AGGREGATE 的历史解析差异**：DETAIL 下 `itemDetails` 是**单条** `UsageConsumableInArrearTierUnitAggregate`，quantity 取发票项自身的 `quantity`（并补上 `bi.getRate()` 作 tierPrice，对应 issue #1325）；AGGREGATE 下 `itemDetails` 是 `UsageConsumableInArrearAggregate`，需展开其 `tierDetails`。

---

## BR-307 分档扣减历史用量；历史缺失时报错（或按配置放宽）

- **类型**: 业务规则
- **同义词**: 历史用量扣减, 缺失历史用量, missing usage, previous usage, 补开用量, 用量缺失
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalConsumableUsageInArrear.java:246-260`

**规则**（ALL_TIERS，且存在历史用量 `previousUsage` 时）：本档 `nbUsedTierBlocks` 减去历史同档 quantity。存在两个断言：

- `tierNum < lastPreviousUsageTier`（历史中间档）时，`nbUsedTierBlocks` 必须与历史 quantity **完全相等**（历史必须已把该档用满）。
- 落在最后一历史档时，`nbUsedTierBlocks − previousQuantity ≥ 0`（当前用量不得少于历史）。

当历史记录不完整（例如过去某区间的用量未上报/未开票）时，断言失败会抛异常。**放宽条件**：`isDryRun == true` 或 `org.killbill.invoice.usage.missing.lenient == true` 时跳过这两个断言。

**含义**：这是防止「历史用量丢失导致重复计费或漏计」的对账护栏；与该配置对应的宽松语义见 BR-312/BR-314。

---

## BR-308 未知单位类型：park 账户或忽略并移除其 trackingId

- **类型**: 业务规则
- **同义词**: 未知单位, 未定义单位, 目录外单位, unknown unit type, park accounts, 忽略单位
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:481-506`

**规则**：聚合区间用量时，若某 `unitType` **不在当前 billing event 已收集到的单位类型集合**内（即目录中未定义）：

- 若 `org.killbill.invoice.parkAccountsWithUnknownUsage == true` → 抛 `InvoiceApiException`（`ILLEGAL INVOICING STATE: unit type ... is not defined in the catalog ...`），使账户被 park（见既有 BR-295）。
- 否则仅记 `warn` 并跳过该单位类型；同时把该 unitType 对应的 trackingId 从本次结果中**移除**，避免它被当作「已开票」而掩盖未定义用量。

**对比**：若 unitType 是目录中已知的、但不属于**当前 usage 段**（`unitTypes.contains` 为 false），则安全忽略，不告警、不影响 trackingId。

---

## BR-309 开票侧原始用量按复合键排序（非落库顺序）

- **类型**: 业务规则
- **同义词**: 用量排序, 开票排序, raw usage sort, composite comparator, 排序键
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/SubscriptionUsageInArrear.java:61-88`, `invoice/src/main/java/org/killbill/billing/invoice/usage/SubscriptionUsageInArrear.java:143-146`

**规则**：开票前，先按 `subscriptionId` 过滤该订阅的原始用量，再按复合比较器升序排序：`(subscriptionId, recordDate, unitType, amount, trackingId)`。区间消费算法依赖此顺序（见 WF-038）。

**与既有 BR-288 的区别**：DB 查询返回顺序是 `order by record_id`（提交顺序，见既有 BR-288）；开票侧**不依赖**它，而是自行按日期排序，从而保证区间切分与到达顺序无关。

---

## BR-310 缺省档位策略 = ALL_TIERS（逐档累进）

- **类型**: 业务规则
- **同义词**: 默认档位策略, 默认计价策略, default tier policy, ALL_TIERS default
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/CatalogSafetyInitializer.java:60-72`

**规则**：catalog 未显式写 `tierBlockPolicy` 时，初始化阶段填入 `TierBlockPolicy.ALL_TIERS`。即**默认采用逐档累进计价**（见 BR-302），而非 TOP_TIER。若要单档计价必须显式写 `tierBlockPolicy="TOP_TIER"`。

---

## BR-311 计费区间按 (usage 名, 目录生效日) 分段；目录变更即为边界

- **类型**: 业务规则
- **同义词**: 目录版本分段, usage 段分段, 目录变更边界, catalog version boundary, usage key, 分段计价
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/SubscriptionUsageInArrear.java:160-227`, `invoice/src/main/java/org/killbill/billing/invoice/usage/SubscriptionUsageInArrear.java:283-316`

**规则**：计费区间以键 `(usageName, catalogEffectiveDate)` 标识（`UsageKey`，catalogVersion 用 `compareTo == 0` 判等）。遍历订阅的 billing events：

- 若某 billing event 引用同一 `UsageKey` → 沿用「在途区间」（`inFlightInArrearUsageIntervals`），追加该 event。
- 若某 `UsageKey` 不再被任何 event 引用（usage 段被移除，或目录版本变化产生新 key）→ 关闭该区间（`build(true)`）。
- 遍历结束后仍在途的区间以 `targetDate` 收尾（`build(false)`）。

**含义**：同一订阅可能产生**多个** `ContiguousIntervalUsageInArrear`，各自用其边界时刻的目录版本定价；每个区间独立计算发票项。

---

## BR-312 回溯窗口：readMaxRawUsagePreviousPeriod（默认 2）

- **类型**: 业务规则
- **同义词**: 回溯窗口, 回看周期, 历史用量窗口, lookback window, readMaxRawUsagePreviousPeriod, 晚到用量
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:124-132`, `invoice/src/main/java/org/killbill/billing/invoice/usage/RawUsageOptimizer.java:77-137`

**规则**：拉取原始用量的起点 `optimizedStartDate`：

- 若 `org.killbill.invoice.readMaxRawUsagePreviousPeriod`（**默认 2**，单位=计费周期数）`< 0` → 不做优化，取 `firstEventStartDate`。
- 否则：按 catalog 中所有 usage 的 `billingPeriod` 分组，取各周期最近一次已开票 USAGE 项的 `endDate`（`getBillingPeriodMinDate1`），向前回退该配置数量的周期，取最早者作为起点（但不早于 `firstEventStartDate`）。
- 特例：若 `org.killbill.invoice.disable.usage.zero.amount == true`（`isUsageZeroAmountDisabled`），改用 `getBillingPeriodMinDate2`：以 `min(UTC today, targetDate)` 为基准回退 1 个周期（假设开票已跟上，简化逻辑）。

**晚到/乱序用量的后果**：该窗口决定「多久以前的上报仍会被拉取」。**早于窗口且此前未开票的用量记录不会被拉取/计费**（可能漏计）；窗口设得越大越安全但越慢。因此该值必须覆盖最大延迟上报跨度。

**终点**：拉取终点用 `targetDate` 当天末刻（账户时区转 UTC），查询为右闭（见 BR-317）。

---

## BR-313 $0 用量项：生成与过滤

- **类型**: 业务规则
- **同义词**: 零金额用量, 空用量项, $0 usage, zero amount, disable.usage.zero.amount, 用量为零, 零金额用量过滤, filterZeroUsageItems, quantity 大于0, 保留零金额用量
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceWithMetadata.java:92-112`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:516-530`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalCapacityUsageInArrear.java:127-146`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:84-92`

**生成侧**：系统刻意支持「无/零用量区间」的 $0 项——

- 完全没有原始用量时，`getEmptyRolledUpUsage` 为每个单位类型构造一个 `amount=0` 的区间（取最后两个转换点）。
- CAPACITY 的 `allUnitAmountToZero` 分支把金额置 0。
- CONSUMABLE 第 1 档即使 0 块也生成明细。

**过滤侧**：系统属性 `org.killbill.invoice.disable.usage.zero.amount`（**默认 false**）控制是否**移除** $0 USAGE 项。为 true 时，`InvoiceWithMetadata.build()` 过滤掉 `type == USAGE` 且 `amount == 0` 且（`quantity == null` 或 `quantity ≤ 0`）的项；若过滤后发票无任何项 → **发票变为 null**（不生成空发票）。

**双重影响**：该开关同时改变回溯窗口算法（见 BR-312），开启后需保证开票及时，否则可能漏计旧周期。

---

## BR-314 IN_ADVANCE 用量计费：目录可定义，但开票路径未实现

- **类型**: 业务规则
- **同义词**: 预付用量未实现, 预付费用量, IN_ADVANCE 未支持, not implemented, unsupported billing mode
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/UsageInvoiceItemGenerator.java:229-244`, `invoice/src/main/java/org/killbill/billing/invoice/generator/UsageInvoiceItemGenerator.java:147-151`

**规则**：

- 目录允许定义 `IN_ADVANCE` 的 CAPACITY/CONSUMABLE（见既有 BR-013），但**用量开票只处理 `IN_ARREAR`**：`findUsageInArrearUsages` 显式跳过非 `IN_ARREAR` 的 usage 段。
- `updatePerSubscriptionNextNotificationUsageDate` 在 `IN_ADVANCE` 分支直接 `throw new IllegalStateException("Not implemented Yet)")`。

**结论**：**今日实际可被计费的用量只有 `IN_ARREAR`**；`IN_ADVANCE` 的 usage 定义不会产生用量发票项。

---

## BR-315 档级目录校验：IN_ARREAR CAPACITY 需 limits、CONSUMABLE 需 blocks

- **类型**: 业务规则
- **同义词**: 档位校验, 档级校验, tier validation, IN_ARREAR limits, IN_ARREAR blocks
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `catalog/src/main/java/org/killbill/billing/catalog/DefaultTier.java:148-159`

**规则**（`DefaultTier.validate`，在 catalog 加载时执行）：

- `IN_ARREAR` + `CAPACITY` 且 `limits.length == 0` → 报错「needs to define some limits」。
- `IN_ARREAR` + `CONSUMABLE` 且 `blocks.length == 0` → 报错「needs to define some blocks」。

**与既有 BR-013 的分工**：既有 BR-013 是 **usage 段级**校验（`DefaultUsage.validate`：IN_ADVANCE+CAPACITY 需 limits、IN_ADVANCE+CONSUMABLE 需 blocks、IN_ARREAR 需 tiers）；本条是**档级**校验。二者共同决定一个合法的 in-arrear usage 目录结构。

---

## BR-316 每个档必须为每个单位定义 limit/block；否则定价报错

- **类型**: 业务规则
- **同义词**: 档位单位缺失, 单位必须定义, missing tier block, missing limit, 目录缺单位
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageUtils.java:34-54`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalCapacityUsageInArrear.java:104-112`

**规则**：

- CONSUMABLE：`getConsumableInArrearTieredBlocks` 对**每个档**查找与 `unitType` 同名的 `tieredBlock`；若某档缺失 → `Preconditions.checkState` 失败（"Missing tierBlock definition for unit ..."）。返回的列表顺序与档顺序一一对应（供逐档计算）。
- CAPACITY：`getTierLimit` 对每档查找同名 `limit`；缺失 → `checkState(false)`。

**含义**：一个 usage 段内，**每个档都必须为每个参与计价的单位各定义一个 block/limit**，不能只在一部分档里定义；否则开票直接抛异常（目录错误，非运行时数据问题）。

---

## BR-317 时间边界：账户时区日界 + usage.tz.mode（默认 FIXED）

- **类型**: 业务规则
- **同义词**: 时区, 日边界, 夏令时, day boundary, account timezone, usage tz mode, end of day, FIXED, VARIABLE
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/UsageClockUtil.java:50-90`, `util/src/main/java/org/killbill/billing/util/config/definition/InvoiceConfig.java:185-193`

**规则**：计费区间边界按账户时区换算，再转 UTC：

- 区间起点：`toDateTimeAtStartOfDay`（当天 00:00:00.000）。
- 区间终点：`toDateTimeAtEndOfDay`（次日 00:00:00.000 − 1ms）。

`org.killbill.invoice.usage.tz.mode`（**默认 `FIXED`**）控制偏移计算：

- `FIXED`：使用账户创建时的固定偏移（`context.getFixedOffsetTimeZone()`），与其它发票项一致。
- `VARIABLE`：按事件日期重新计算偏移（`context.getAccountTimeZone()`），使「相同 TZ、相同订阅、相同用量点」的账户在夏令时下得到一致结果（对应 killbill issue #1934）。

**关联**：拉取原始用量的终点即 `targetDate` 当天末刻（见 BR-312、既有 WF-036）。

---

## BR-318 已完全覆盖的区间直接跳过（防 blocking 重复计费）

- **类型**: 业务规则
- **同义词**: 区间已开票跳过, 完全覆盖, covered period skip, isContainedIntoExistingUsage, 防重复
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:300-307`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:333-356`

**规则**：对每个待计费区间，若已存在同 usage 名、同类型的 USAGE 发票项**完全包含**该区间（`usageInput.start ≤ 区间start 且 区间end < usageInput.end`，或 `usageInput.start < 区间start 且 区间end ≤ usageInput.end`；两者取其一），则**整段跳过**并记 warn（"Ignoring usage ... as it has already been invoiced"）。

**例外**：当区间起止同日（`startDate == endDate`，例如同日换套餐）时禁用该检查，交由后续金额/按档对账处理。

**含义**：blocking event 重算可能导致区间起止与已开票项不同；此检查避免对已覆盖区间重复计费。

---

## BR-319 发票级去重：TrackingRecordId 相似判定（不含 invoiceId）

- **类型**: 业务规则
- **同义词**: 用量发票去重, tracking 去重, 发票级幂等, TrackingRecordId, isSimilarRecord, 相似记录, 用量记录相似, 跨发票去重
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceWithMetadata.java:181-256`, `invoice/src/main/java/org/killbill/billing/invoice/usage/ContiguousIntervalUsageInArrear.java:286-292`, `invoice/src/main/java/org/killbill/billing/invoice/generator/InvoiceWithMetadata.java:181-234`

**规则**：开票侧为每条被消费的用量记录构造 `TrackingRecordId(trackingId, invoiceId, subscriptionId, unitType, recordDate)`。判定「相似」时**忽略 invoiceId**，只比较 `(trackingId, subscriptionId, unitType, recordDate)`。本次新用量 = 所有用量 trackingId 中**不存在相似已开票记录**者。

**含义**：即使同一用量记录被重新挂到另一张发票（invoiceId 不同），只要这四个键相同就视为已开票，不会被重复计费。这补齐了既有 BR-282（提交侧幂等）之外的**开票侧幂等**。

**补充（身份 vs 相似）**：`TrackingRecordId.equals`/`hashCode` **包含** `invoiceId`（精确身份，用于区分挂到不同发票的记录）；仅 `isSimilarRecord` 忽略 `invoiceId`（用于跨发票去重）。

---
