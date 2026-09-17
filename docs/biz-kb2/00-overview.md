# Kill Bill 业务知识库 — 系统概览


本知识库由五个模块（invoice / catalog / overdue / payment / usage）的 340 张原始知识卡合成，去重合并 11 组后得到 324 张全局唯一编号的卡片，覆盖订阅计费系统的目录定价、发票生成与结算、支付、用量计量与逾期催收。

## 系统概览

Kill Bill 是订阅与用量计费平台。catalog 定义可售的产品、计划、阶段、价格表与用量定价；subscription/entitlement 依据目录生成 billing events；invoice 依据 billing events 生成发票（含固定费、周期费、用量费），并处理余额、账户信用（CBA）、父子账户汇总、修复与作废；payment 负责对发票发起支付、重试与退款/拒付，并由 Janitor 修复未决交易；usage 负责用量数据的提交、查询与按单位类型汇总；overdue 以账户为单位评估逾期条件并施加 BlockingState 与催收策略。

## 模块清单

| 模块 | 源码根 | 卡片数 | 职责 |
|---|---|---|---|
| catalog | `catalog/src/main/java/org/killbill/billing/catalog/` | 74 | 产品目录：产品/计划/阶段/价格表/用量定价的定义与校验 |
| invoice | `invoice/src/main/java/org/killbill/billing/invoice/` | 96 | 发票：发票生成、余额与信用、父子账户汇总、用量计费落地、修复与作废 |
| overdue | `overdue/src/main/java/org/killbill/billing/overdue/` | 73 | 逾期催收（Dunning）：账户级逾期状态评估、BlockingState 施加与控制标签 |
| payment | `payment/src/main/java/org/killbill/billing/payment/` | 49 | 支付：支付交易状态机、重试与 Janitor、支付控制插件、退款/拒付 |
| usage | `usage/src/main/java/org/killbill/billing/usage/` | 45 | 用量：用量提交/查询/汇总、单位类型、跟踪号幂等、租户隔离 |

## 业务能力清单

### catalog — 产品目录：产品/计划/阶段/价格表/用量定价的定义与校验

**术语（21）**

- `TERM-001` 用量计费 (Usage)
- `TERM-002` 计划 (Plan)
- `TERM-003` 计划阶段 (Plan Phase)
- `TERM-004` 产品 (Product)
- `TERM-005` 产品类别 (Product Category)
- `TERM-006` 价格表 (Price List)
- `TERM-007` 用量类型 (UsageType : CONSUMABLE / CAPACITY)
- `TERM-008` 分层 (Tier)
- `TERM-009` 计费周期 (Billing Period)
- `TERM-010` 阶段类型 (Phase Type)
- `TERM-011` 计费模式 (BillingMode)
- `TERM-012` 限制 (Limit)
- `TERM-013` 计费对齐 (Billing Alignment)
- `TERM-014` 阶梯块策略 (Tier Block Policy)
- `TERM-015` 块类型 (Block Type)
- `TERM-016` 价格覆盖 (Price Override)
- `TERM-017` 目录版本 (Catalog Version)
- `TERM-018` 固定费类型 (Fixed Type)
- `TERM-019` 账单日 (BCD / Bill Cycle Day)
- `TERM-020` 计费动作策略 (BillingActionPolicy)
- `TERM-021` 简化计划描述符 (SimplePlanDescriptor)

**业务实体（12）**

- `ENT-001` 产品实体 (Product)
- `ENT-002` 计划实体 (Plan)
- `ENT-003` 计划阶段实体 (Plan Phase)
- `ENT-004` 价格表实体与价格表集合 (PriceList / PriceListSet)
- `ENT-005` 目录实体 (StandaloneCatalog / StaticCatalog)
- `ENT-006` 价格实体 (Price / InternationalPrice)
- `ENT-007` 时长实体 (Duration)
- `ENT-008` 周期费实体 (Recurring)
- `ENT-009` 块与阶梯块实体 (Block / TieredBlock)
- `ENT-010` 目录版本集合实体 (VersionedCatalog)
- `ENT-011` 规则集实体 (PlanRules)
- `ENT-012` 阶段计费项实体 (Fixed / Usage / Tier / Limit)

**业务规则（34）**

- `BR-001` 初始阶段不能是 EVERGREEN
- `BR-002` 最终阶段不能是 TRIAL 或 DISCOUNT
- `BR-003` 阶段必须至少定义一种计费项
- `BR-004` 阶段名与计划名互推规则
- `BR-005` EVERGREEN 必须 UNLIMITED，非 EVERGREEN 不得 UNLIMITED
- `BR-006` UNLIMITED 时长与 number 互斥
- `BR-007` 周期费与计费周期一致性
- `BR-008` 价格不得为负且币种必须受支持
- `BR-009` 指定币种无价格时抛 CAT_NO_PRICE_FOR_CURRENCY
- `BR-010` 用量各模式的必填结构校验
- `BR-011` Limit 的上下限判定
- `BR-012` effectiveDateForExistingSubscriptions 不得早于目录生效日
- `BR-013` 纯用量计划可不设 recurringBillingMode
- `BR-014` plansAllowedInBundle 的取值语义
- `BR-015` 默认价格表名 DEFAULT 为保留名
- `BR-016` 价格表解析与默认回退
- `BR-017` 计划缺省价格表的自动解析
- `BR-018` 目录版本按生效日期选取
- `BR-019` 版本生效日唯一且 catalogName 一致
- `BR-020` 跨版本同名计划形状必须一致
- `BR-021` 规则未命中时的默认策略/对齐值
- `BR-022` ILLEGAL 变更策略直接拒绝计划变更
- `BR-023` 规则集必须存在默认 case 且不得重复
- `BR-024` 产品自引用与 catalogName 校验
- `BR-025` TOP_UP 块必须定义 minTopUpCredit
- `BR-026` 规则 case 的匹配语义
- `BR-027` createOrFindPlan 的计划解析与异常
- `BR-028` 价格表查找的异常语义
- `BR-029` BCD 由首个非零周期费日期推算
- `BR-030` BCD 对齐的月末处理
- `BR-031` 账户 BCD 取最早的有计费 ACCOUNT 对齐事件
- `BR-032` ACCOUNT 对齐但账户 BCD 未设时回退 SUBSCRIPTION
- `BR-033` 简化计划只支持 EVERGREEN 与单 TRIAL
- `BR-034` ADD_ON 必须提供有效的可用基础产品

**业务流程（4）**

- `WF-001` 目录加载与校验流程
- `WF-002` 计划变更（换套餐/改价）决策流程
- `WF-003` 简化计划创建/更新流程
- `WF-004` 账户 BCD 计算流程

**状态机（2）**

- `SM-001` 计划阶段生命周期状态机
- `SM-002` 目录版本生效状态机

**角色/权限（1）**

- `ROLE-001` 目录管理的租户范围（无独立角色权限）

### invoice — 发票：发票生成、余额与信用、父子账户汇总、用量计费落地、修复与作废

**术语（10）**

- `TERM-007` 用量类型 (UsageType : CONSUMABLE / CAPACITY)
- `TERM-008` 分层 (Tier)
- `TERM-011` 计费模式 (BillingMode)
- `TERM-022` 发票项类型（InvoiceItemType）
- `TERM-023` 发票项（InvoiceItem）
- `TERM-024` 发票支付类型 (InvoicePaymentType)
- `TERM-025` 干跑类型（DryRunType）
- `TERM-026` 分比（Proration）
- `TERM-027` 展示名（pretty name）
- `TERM-028` 自动开票关闭标签 (AUTO_INVOICING_OFF)

**业务实体（8）**

- `ENT-013` 发票（Invoice）
- `ENT-014` 账户信用余额调整项（CreditBalanceAdjInvoiceItem / CBA）
- `ENT-015` 用量发票项（UsageInvoiceItem）
- `ENT-016` 父汇总发票项（ParentInvoiceItem / PARENT_SUMMARY）
- `ENT-017` 发票支付 (InvoicePayment)
- `ENT-018` 周期发票项（RecurringInvoiceItem）
- `ENT-019` 固定费用发票项（FixedPriceInvoiceItem）
- `ENT-020` 外部收费发票项（ExternalChargeInvoiceItem）

**业务规则（69）**

- `BR-035` 发票未来生成最大月数
- `BR-036` 用量重复计费防护（tracking id 去重 + 已开票区间跳过）
- `BR-037` 发票防重复计费安全检查
- `BR-038` 零金额用量项是否写出
- `BR-039` 缺失历史用量记录时的处理
- `BR-040` 每日每订阅最大发票项数
- `BR-041` 干跑发票通知提前时间
- `BR-042` 原始用量回看账期数（usage lookback）
- `BR-043` 全局锁获取最大重试次数
- `BR-044` 默认发票插件
- `BR-045` 发票创建邮件通知开关
- `BR-046` 发票系统总开关
- `BR-047` 用量聚合规则（CAPACITY 取峰值 / CONSUMABLE 累加）
- `BR-048` 父发票自动提交时间
- `BR-049` 发票项结果报告模式
- `BR-050` 用量时区偏移模式
- `BR-051` in-arrear 计划计费模式
- `BR-052` 目录中未定义的用量处理（可挂起账户）
- `BR-053` 不可恢复异常时挂起账户
- `BR-054` 发票生成最大回看时间
- `BR-055` 固定天数免分比
- `BR-056` 发票余额计算（balance）
- `BR-057` 发票余额为零的情形
- `BR-058` 发票已付金额（paid amount）
- `BR-059` 发票已退款金额（refunded amount）
- `BR-060` 发票计费金额组成（charged amount）
- `BR-061` 子发票金额（父账户汇总）
- `BR-062` 信用发票识别（CREDIT_ADJ + CBA_ADJ）
- `BR-063` 账户信用（CBA）生成与使用规则
- `BR-064` 账户信用按发票日期分配给未付发票
- `BR-065` 发票目标日期上限校验（未来 36 个月）
- `BR-066` 发票目标日期自动前推（避免回溯重复开票）
- `BR-067` 作废发票（VOID）的前置校验
- `BR-068` 提交草稿发票（commit）
- `BR-069` 外部收费与信用金额校验
- `BR-070` 账户余额与账户信用余额查询
- `BR-071` 子账户信用转给父账户
- `BR-072` 发票项调整（ITEM_ADJ）校验
- `BR-073` 发票核销（written off）标记
- `BR-074` 用量计费区间按 BCD 对齐
- `BR-075` 手动支付账户的发票渲染
- `BR-076` 发票优化时间边界（cutoff / maxInvoiceLimit）
- `BR-077` 建议开票项过滤（optimizer filterProposedItems）
- `BR-078` 用量仅支持后付费（IN_ARREAR）
- `BR-079` 父发票提交通知去重
- `BR-080` 发票系统关闭时挂起账户
- `BR-081` 已挂起账户跳过开票
- `BR-082` 发票生成的账户级全局锁
- `BR-083` 干跑通知仅余额大于 0 时发送
- `BR-084` 订阅 EXPIRED 事件不触发开票
- `BR-085` 哪些子发票可被父发票忽略
- `BR-086` 父发票的项调整传播
- `BR-087` 父发票余额为 0 时子发票的余额算法
- `BR-088` 修复项（REPAIR_ADJ）金额上限
- `BR-089` 分比计算（Proration）
- `BR-090` 原始用量优化的起始日期（用量回看）
- `BR-091` 发票配置支持多租户覆盖
- `BR-092` 迁移发票余额恒为 0
- `BR-093` 发票项类型与实现类映射
- `BR-094` 加锁失败时的重试时间表
- `BR-095` 未付发票的判定
- `BR-096` 发票状态变更的约束与副作用
- `BR-097` 完全修复项的剔除（InvoicePruner）
- `BR-098` 发票项调整金额取负
- `BR-099` 发票项调整的归属校验
- `BR-100` 固定费用发票项生成规则
- `BR-101` 周期发票项的分比生成规则
- `BR-102` 发票项安全检查边界（safety bounds）
- `BR-103` 下一次开票通知日期计算

**业务流程（7）**

- `WF-005` 发票生成流程（generateInvoice）
- `WF-006` 干跑发票流程（dryRun）
- `WF-007` 用量计费流程（in-arrear usage billing）
- `WF-008` 父发票自动提交流程（parent invoice auto-commit）
- `WF-009` 发票生成触发时机（when invoice is generated）
- `WF-010` 父子账户（HA）发票汇总流程
- `WF-011` 修复 / 套餐变更处理流程（Repair）

**状态机（1）**

- `SM-003` 发票状态机（DRAFT / COMMITTED / VOID）

**角色/权限（1）**

- `ROLE-002` 发票模块无内建权限注解

### overdue — 逾期催收（Dunning）：账户级逾期状态评估、BlockingState 施加与控制标签

**术语（14）**

- `TERM-028` 自动开票关闭标签 (AUTO_INVOICING_OFF)
- `TERM-029` 逾期催收（Overdue / Dunning）
- `TERM-030` 逾期状态（OverdueState）
- `TERM-031` 逾期条件（OverdueCondition）
- `TERM-032` 清算状态（Clear State / 未逾期）
- `TERM-033` 计费状态（BillingState）
- `TERM-034` 重新评估间隔（Reevaluation Interval）
- `TERM-035` 阻止变更（blockChanges）
- `TERM-036` 禁用权益并阻止变更（disableEntitlementAndChangesBlocked）
- `TERM-037` 外部消息（externalMessage）
- `TERM-038` 逾期强制关闭标签（OVERDUE_ENFORCEMENT_OFF）
- `TERM-039` 发票核销标签（WRITTEN_OFF）
- `TERM-040` 订阅取消策略（subscriptionCancellationPolicy）
- `TERM-041` 租户级逾期配置（tenant-level overdue config）

**业务实体（12）**

- `ENT-021` 逾期状态 OverdueState
- `ENT-022` 逾期条件 OverdueCondition
- `ENT-023` 账户逾期状态集 OverdueStatesAccount / OverdueStateSet
- `ENT-024` 计费状态 BillingState
- `ENT-025` 逾期配置根 OverdueConfig
- `ENT-026` 逾期包装器 OverdueWrapper
- `ENT-027` 计费状态计算器 BillingStateCalculator
- `ENT-028` 逾期状态施加器 OverdueStateApplicator
- `ENT-029` 逾期变更事件 OverdueChangeInternalEvent
- `ENT-030` 逾期通知键 OverdueCheckNotificationKey / OverdueAsyncBusNotificationKey
- `ENT-031` 逾期监听器 OverdueListener
- `ENT-032` 时长配置 DefaultDuration

**业务规则（36）**

- `BR-104` 逾期是账户级（跨订阅）规则
- `BR-105` 条件：未付发票数量达到阈值
- `BR-106` 条件：未付发票余额合计达到阈值
- `BR-107` 条件：最早未付发票距今时长达到阈值
- `BR-108` 条件：控制标签必须存在（controlTagInclusion）
- `BR-109` 条件：控制标签必须不存在（controlTagExclusion）
- `BR-110` 条件：上次失败支付响应（当前未真正实现）
- `BR-111` 多子条件为 AND，未配置的子条件被忽略
- `BR-112` 状态选择：按配置顺序取首个命中状态，否则 clear
- `BR-113` 状态升级顺序与「首状态」语义
- `BR-114` 状态未变化时为 no-op（但仍可能安排下次通知）
- `BR-115` blockChanges 动作映射到 BlockingState.blockChange
- `BR-116` disableEntitlementAndChangesBlocked 同时暂停权益与计费
- `BR-117` 订阅取消策略：NONE / IMMEDIATE / END_OF_TERM
- `BR-118` 自动维护 AUTO_INVOICING_OFF 标签（防多生成信用）
- `BR-119` 重新评估通知的调度规则（定时器语义）
- `BR-120` clear 状态清除未来通知
- `BR-121` OVERDUE_ENFORCEMENT_OFF 短路并触发 CLEAR
- `BR-122` 触发重新评估的事件集合
- `BR-123` 仅当存在带条件的状态时才运行逾期机制（优化）
- `BR-124` 父/子账户的级联与委派支付
- `BR-125` 账户级全局锁与重试（MAX_LOCK_RETRIES=50）
- `BR-126` autoReevaluationInterval 合法性校验
- `BR-127` initialReevaluationInterval 为无效值时不重试
- `BR-128` 状态名长度上限 50
- `BR-129` 默认配置只含 Clear 状态（等价于未启用催收）
- `BR-130` 配置加载失败/无效时逾期系统被禁用
- `BR-131` 通知去重：check 队列保留最早、async 队列有则跳过
- `BR-132` getOverdueStateFor 从 blocking state 名解析当前状态
- `BR-133` 租户配置上传会覆盖旧值并失效缓存
- `BR-134` 有效日与条件日期口径
- `BR-135` 取消动作只针对非 ADD_ON 基础订阅
- `BR-136` 逾期状态持久化为账户 BlockingState
- `BR-137` clear 路径的状态与通知处理
- `BR-138` 内部租户始终使用默认配置
- `BR-139` 逾期配置 URI 由 `org.killbill.overdue.uri` 控制

**业务流程（5）**

- `WF-012` 逾期评估与刷新流程（Refresh）
- `WF-013` 逾期状态评估周期（评估→施加→定时复评）
- `WF-014` 租户逾期配置上传流程
- `WF-015` 逾期豁免（CLEAR）流程
- `WF-016` 逾期服务生命周期启动流程

**状态机（2）**

- `SM-004` 账户逾期状态机
- `SM-005` 逾期异步通知动作状态机（REFRESH / CLEAR）

**角色/权限（4）**

- `ROLE-003` 内部系统角色 OverdueService（自动催收执行者）
- `ROLE-004` 租户管理员（租户级逾期配置上传）
- `ROLE-005` 运营/客服（控制标签操作权）
- `ROLE-006` 逾期状态查询者（读取当前状态与配置）

### payment — 支付：支付交易状态机、重试与 Janitor、支付控制插件、退款/拒付

**术语（10）**

- `TERM-024` 发票支付类型 (InvoicePaymentType)
- `TERM-042` 支付交易类型 (TransactionType)
- `TERM-043` Janitor (支付清理任务)
- `TERM-044` 支付重试 (Payment Retry)
- `TERM-045` AUTO_PAY_OFF（自动支付关闭标签）
- `TERM-046` MANUAL_PAY（手动支付标签）
- `TERM-047` __EXTERNAL_PAYMENT__（外部支付插件）
- `TERM-048` 支付控制插件 (Payment Control Plugin)
- `TERM-049` 支付尝试状态（attempt 状态机状态）
- `TERM-050` 支付插件状态 PaymentPluginStatus

**业务实体（5）**

- `ENT-017` 发票支付 (InvoicePayment)
- `ENT-033` 支付 Payment
- `ENT-034` 支付交易 PaymentTransaction
- `ENT-035` 支付方式 PaymentMethod
- `ENT-036` 支付尝试 PaymentAttempt

**业务规则（24）**

- `BR-140` 支付失败重试计划（默认 8,8,8 天）
- `BR-141` 插件失败重试参数（初始 300 秒 / 倍数 2 / 最多 8 次）
- `BR-142` Janitor 未完成交易重试计划（UNKNOWN / PENDING）
- `BR-143` AUTO_PAY_OFF 账户自动支付中止
- `BR-144` 未提交(非 COMMITTED)发票不允许支付
- `BR-145` 委托给父账户的子账户发票不自动支付
- `BR-146` 空发票(余额为 0)支付处理
- `BR-147` 支付金额不得超过发票余额
- `BR-148` 退款金额计算（按发票项或显式金额）
- `BR-149` 失败支付的下次重试日期计算
- `BR-150` 默认支付方式取自账户 (account.paymentMethodId)
- `BR-151` 插件状态(PluginStatus)到交易状态/操作结果的映射
- `BR-152` 单笔支付不允许并发的未决交易
- `BR-153` 执行交易前先调用 Janitor 修正状态
- `BR-154` Janitor 下次回查时间计算（UNKNOWN/PENDING 重试表）
- `BR-155` 支付控制插件可调整支付参数，默认禁止覆盖已有支付方式
- `BR-156` 支付插件按支付方式的 pluginName 查找
- `BR-157` 支付插件调用超时与线程配置
- `BR-158` 支付错误事件与插件错误事件
- `BR-159` 外部支付通过插件属性模拟失败（测试/演示语义）
- `BR-160` 外部支付（__EXTERNAL_PAYMENT__）的用途
- `BR-161` 各交易类型的插件操作与无金额操作
- `BR-162` 支付状态机 linkStateMachines：交易类型的先后约束
- `BR-163` 支付状态机成功态判定

**业务流程（4）**

- `WF-017` 发票支付流程（控制插件驱动）
- `WF-018` 退款流程
- `WF-019` 拒付(Chargeback)流程
- `WF-020` Janitor 修复未完成支付流程

**状态机（3）**

- `SM-006` 支付交易状态机
- `SM-007` 支付重试控制状态机 (PAYMENT_RETRY)
- `SM-008` Janitor 支付尝试(attempt)修复状态机

**角色/权限（3）**

- `ROLE-007` 系统内部用户（Janitor/重试以 SYSTEM 身份执行）
- `ROLE-008` 支付控制插件名称配置（org.killbill.payment.invoice.plugin）
- `ROLE-009` 支付插件注册表 / OSGI 服务名

### usage — 用量：用量提交/查询/汇总、单位类型、跟踪号幂等、租户隔离

**术语（10）**

- `TERM-001` 用量计费 (Usage)
- `TERM-007` 用量类型 (UsageType : CONSUMABLE / CAPACITY)
- `TERM-011` 计费模式 (BillingMode)
- `TERM-051` 用量记录（单日计量）
- `TERM-052` 单位类型（Unit Type）
- `TERM-053` 汇总用量（Rolled-Up Usage）
- `TERM-054` 原始用量（Raw Usage）
- `TERM-055` 跟踪号（Tracking Id）
- `TERM-056` 用量插件（Usage Plugin）
- `TERM-057` 用量上下文（UsageContext）

**业务实体（10）**

- `ENT-037` 用量记录实体 / rolled_up_usage 表
- `ENT-038` 汇总用量视图（RolledUpUsage）
- `ENT-039` 汇总单位（RolledUpUnit）
- `ENT-040` 订阅用量提交记录（SubscriptionUsageRecord）
- `ENT-041` 单位用量记录（UnitUsageRecord）
- `ENT-042` 用量记录值（UsageRecord）
- `ENT-043` 原始用量记录（RawUsageRecord / DefaultRawUsage）
- `ENT-044` 用量 DAO（RolledUpUsageDao / RolledUpUsageSqlDao）
- `ENT-045` 用量插件注册表（Usage Provider Registry）
- `ENT-046` 内部用量 API（InternalUserApi）

**业务规则（18）**

- `BR-010` 用量各模式的必填结构校验
- `BR-036` 用量重复计费防护（tracking id 去重 + 已开票区间跳过）
- `BR-047` 用量聚合规则（CAPACITY 取峰值 / CONSUMABLE 累加）
- `BR-052` 目录中未定义的用量处理（可挂起账户）
- `BR-164` 未提供跟踪号时自动生成
- `BR-165` 同一批提交共用同一跟踪号
- `BR-166` 订阅用量查询：半开区间 [start, end) + 单位类型过滤
- `BR-167` 账户原始用量查询：闭区间 [start, end]（开票唯一查询）
- `BR-168` 用量按单位类型汇总求和
- `BR-169` 查询结果排序：按 record_id 升序（提交顺序）
- `BR-170` 同一 (订阅, 单位类型, 日期) 重复提交会累加，不覆盖
- `BR-171` 插件优先：插件返回非 null（含空列表）即不查库
- `BR-172` 插件越界数据仅告警，不拒绝
- `BR-173` 单位类型来源：CAPACITY→limit，CONSUMABLE→tier block
- `BR-174` 用量存储层不区分 CONSUMABLE / CAPACITY
- `BR-175` 用量提交的必填校验
- `BR-176` 退订后不得记录晚于生效结束日的用量
- `BR-177` 用量相关系统属性（配置项清单）

**业务流程（4）**

- `WF-021` 记录（提交）用量流程
- `WF-022` 查询订阅单一单位类型用量
- `WF-023` 查询订阅全部用量（按转换时间分段）
- `WF-024` 开票侧拉取账户原始用量

**状态机（1）**

- `SM-009` 用量记录无状态生命周期（只追加）

**角色/权限（2）**

- `ROLE-010` 多租户隔离（tenant_record_id 强制过滤）
- `ROLE-011` 用量模块无显式权限注解

## 文件导航

- `glossary.md` — 术语卡（57）
- `entities.md` — 业务实体及关系（46）
- `rules.md` — 业务规则卡（177）
- `workflows.md` — 业务流程（24）
- `state-machines.md` — 状态机（9）
- `roles-permissions.md` — 角色与权限（11）
- `modules/catalog.md` — catalog 模块深度视图（74）
- `modules/invoice.md` — invoice 模块深度视图（96）
- `modules/overdue.md` — overdue 模块深度视图（73）
- `modules/payment.md` — payment 模块深度视图（49）
- `modules/usage.md` — usage 模块深度视图（45）
- `gaps.md` — 未确定项（2）
- `questions.md` — 待人工确认的问题
- `confidence-report.md` — 置信度统计

## 溯源与编号说明

本知识库由各模块的原始卡**合并/去重/重新编号**而来，编号规则与来源说明如下：

- 原始卡按固定前缀分组（TERM- / ENT- / BR- / WF- / SM- / ROLE-）后，在**全局**范围内从 001 连续编号；相同前缀在所有模块间共享同一编号空间，因此全局 ID 全局唯一。
- 每张卡的 `**模块**` 字段保留其来源模块；跨模块合并的卡其 `模块` 为来源模块的并集（如 `catalog, invoice, usage`），`同义词` 与 `溯源` 为各来源卡的并集，`置信度` 取最高（🟢 > 🟡 > 🔴）。
- 卡片正文中出现的其他卡 ID 引用（如「见 BR-005」）沿用**原始各模块的临时编号**，未随全局重编号改写，故可能与全局 ID 不一致；定位时请以 `模块` 字段与 `溯源` 路径为准。跨模块合并关系与「临时编号 → 全局编号」的映射见 `questions.md` 第三节。
- 溯源路径均相对 Kill Bill 仓库根；目标验证范围为 `benchmark/killbill`，模块范围 `invoice, overdue, catalog, payment, usage`。
