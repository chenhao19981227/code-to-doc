# overdue（逾期催收 / Dunning）业务知识卡 · 补全篇（Supplement）

<!-- module: overdue | source_root: overdue/src/main/java/org/killbill/billing/overdue | kb3 supplement: exact enumerations/defaults/conditional behaviour -->
<!-- 本文件仅补充 .bizdoc-kb2/cards/overdue.md 未覆盖的精确细节，不重复已有卡片。 -->

## TERM-O1 逾期状态配置元素全集（XML 名称 / 默认值 / 可空性）

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

## TERM-O2 时长配置 DefaultDuration：unit/number 语义与 -1 默认陷阱

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

## TERM-O3 内建清算状态对象（Built-in Clear State）与保留名

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

## TERM-O4 订阅取消策略枚举 OverdueCancellationPolicy

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
**作用条件**：该动作**只在状态名发生变化时**才会执行（见 BR-O11 的 no-op 短路），并且取消列表先经 BR-O18 的范围过滤。

## TERM-O5 两个同名的 OverdueConfig（XML 配置对象 vs 属性/多租户接口）

- **类型**: 术语
- **同义词**: OverdueConfig 命名冲突, 配置对象与属性接口, two OverdueConfig types, org.killbill.billing.overdue.api.OverdueConfig, util.config.definition.OverdueConfig, MultiTenantOverdueConfig
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueConfig.java:35-52`, `overdue/src/main/java/org/killbill/billing/overdue/config/MultiTenantOverdueConfig.java:34-47`, `overdue/src/main/java/org/killbill/billing/overdue/glue/DefaultOverdueModule.java:82-88`

**含义**：代码里有两个不同包下的 `OverdueConfig`，容易混淆：
1. **XML 配置对象** `org.killbill.billing.overdue.api.OverdueConfig`：由 `DefaultOverdueConfig` 实现，`@XmlRootElement(name="overdueConfig")`，承载 `<accountOverdueStates>`；也就是租户上传/缓存的业务规则。
2. **属性接口** `org.killbill.billing.util.config.definition.OverdueConfig`：由 `MultiTenantOverdueConfig` 实现（继承 `MultiTenantLockAwareConfigBase`），用于从 killbill 配置提供 `getRescheduleIntervalOnLock(context)` 等运行时属性，并作为 `@Named(STATIC_CONFIG)` 的静态来源。
**绑定关系**：`DefaultOverdueModule.installConfig()` 把静态 `OverdueConfig` 绑定为 `STATIC_CONFIG`，再把无注解的 `OverdueConfig` 绑定到 `MultiTenantOverdueConfig`（82-88 行）。两个同名字符串常量跨包引用，是本模块最易踩坑处之一。

## TERM-O6 逾期变更事件 OverdueChangeInternalEvent 字段与转移布尔

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

## ENT-O1 配置状态实体 DefaultOverdueState（全字段与 getter 映射）

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

## ENT-O2 逾期配置缓存 DefaultOverdueConfigCache（默认配置两阶段加载）

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

## ENT-O3 多租户配置基类 MultiTenantOverdueConfig

- **类型**: 业务实体
- **同义词**: 多租户配置基类, 租户配置, MultiTenantOverdueConfig, tenant config base, MultiTenantLockAwareConfigBase
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/MultiTenantOverdueConfig.java:34-47`, `overdue/src/main/java/org/killbill/billing/overdue/glue/DefaultOverdueModule.java:82-88`

**关键字段/关系**：继承 `MultiTenantLockAwareConfigBase`，构造注入 `@Named(STATIC_CONFIG) OverdueConfig staticConfig` 与 `CacheConfig`。
- `getConfigClass()` 返回 `org.killbill.billing.util.config.definition.OverdueConfig.class`，即**租户级属性覆盖**的目标类。
- 它是「无注解 `OverdueConfig` 绑定」的实现，因此运行时代码注入到的是它；静态默认由 `STATIC_CONFIG` 提供。
**意义**：租户可覆盖的是**属性型配置**（如锁重排间隔），而逾期规则 XML（`accountOverdueStates`）走 ENT-O2/BR-O22 的租户 KV 缓存，两条路径彼此独立。

## ENT-O4 逾期运行时 API 实现 DefaultOverdueApi

- **类型**: 业务实体
- **同义词**: 逾期API实现, 运行时接口, DefaultOverdueApi, overdue runtime API, getOverdueStateFor, uploadOverdueConfig
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:42-58`, `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:60-104`

**关键字段/关系**：实现 `OverdueApi`，依赖 `OverdueConfigCache`、`TenantUserApi`、`BlockingInternalApi`、`InternalCallContextFactory`。对外 4 个方法：
- `getOverdueConfig(TenantContext)` → 返回该租户的 `OverdueConfig`（走缓存，未命中回退默认）。
- `uploadOverdueConfig(String xml, CallContext)` → 覆盖租户 `OVERDUE_CONFIG` 并失效缓存（见 BR-O22）。
- `uploadOverdueConfig(OverdueConfig, CallContext)` → 先 `XMLWriter.writeXML` 序列化再上传；序列化异常 → `OVERDUE_INVALID_FOR_TENANT`。
- `getOverdueStateFor(UUID accountId, TenantContext)` → 解析该账户当前逾期状态（见 WF-O2）。
**注意**：`createInternalTenantContext` 只填 tenantRecordId（注释强调：「important to always create the (ehcache) key the same way」），而 `getOverdueStateFor` 使用带 accountId 的重载以填充 accountRecordId。

## ENT-O5 通知去重策略对象 OverdueCheckPoster / OverdueAsyncBusPoster

- **类型**: 业务实体
- **同义词**: 通知投递器, 去重策略, OverdueCheckPoster, OverdueAsyncBusPoster, notification poster, dedup strategy
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueCheckPoster.java:48-85`, `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusPoster.java:47-57`, `overdue/src/main/java/org/killbill/billing/overdue/notification/DefaultOverduePosterBase.java:61-88`

**关键字段/关系**：两者都继承 `DefaultOverduePosterBase`，仅覆盖 `cleanupFutureNotificationsFormTransaction`，即「插入前如何清理既有未来通知」的策略：
- `OverdueCheckPoster`：查询结果按 effectiveDate 升序；只看**第 0 条**（最早）与待插入时间比较，决定是否插入并删除其余（保留最早策略）。
- `OverdueAsyncBusPoster`：只要已存在任意未来通知（`size != 0`）就不插入。
**共用流程**（`DefaultOverduePosterBase.insertOverdueNotification` 61-88）：在**同一事务**内查询该账户未来通知 → 调用策略 → 若允许则 `recordFutureNotificationFromTransaction`。查询按 `context.accountRecordId + tenantRecordId` 过滤（120-126 行）。

## ENT-O6 唯一配置属性 OverdueProperties

- **类型**: 业务实体
- **同义词**: 逾期属性, 配置项, OverdueProperties, org.killbill.overdue.uri, config property
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/OverdueProperties.java:25-30`

**关键字段/关系**：接口 `OverdueProperties extends KillbillConfig`，仅声明一个属性：
- `@Config("org.killbill.overdue.uri")`，`@Default("NoOverdueConfig.xml")`，描述为「配置位置：classpath 或文件系统」。
**用途**：`DefaultOverdueService.loadConfig` 以 `properties.getConfigURI()` 作为默认配置来源；除该项外，overdue 模块没有其它自有配置键（租户/业务规则均通过 XML 与租户 KV 提供）。

## BR-O1 状态声明顺序即匹配优先级；无 condition 的状态永不胜出

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

## BR-O2 状态名命名约束（@XmlID 唯一性 + XML ID 合法性 + 50 上限 + 保留名）

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
5. 名字影响业务：状态名即持久化到 BlockingState 的状态名，改名会破坏既有数据的可解析性（见 BR-O4）。

## BR-O3 getFirstState() = 最后一个声明状态；空数组会越界

- **类型**: 业务规则
- **同义词**: 首状态, 入门级状态, 最后声明, getFirstState, first state, entry level overdue state, empty states array
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:87-95`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:109-113`

**规则**：`getFirstState()` 返回 `getStates()[size()-1]`，即数组**最后一个**元素。
- 由 BR-O1 的「最严重在前」契约可知，最后一个元素是**最轻/入门级**状态（如 OD1）。
- 该值在 applicator 里用于判断「尚未进入首状态但有欠费仍需复检」：`conditionForNextNotfication = !next.isClearState() || (firstOverdueState != null && billingState.getDateOfEarliestUnpaidInvoice() != null)`（109-113 行）。
**边界行为**：若状态数组为空，`size()-1 = -1`，`getStates()[-1]` 抛 `ArrayIndexOutOfBoundsException`。实际运行中由 `OverdueWrapper.refresh` 的 `size() < 1` 早退（BR-O28）以及 `OverdueWrapperFactory` 返回空状态集共同规避，application 层不会以空集调用 `getFirstState()`。

## BR-O4 配置 isClearState 标志不决定清算；内建 clearState 是唯一出口

- **类型**: 业务规则
- **同义词**: isClearState 标志, 清算标志, 内建清算状态, configured isClearState flag, built-in clear state, clear state resolution
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:37-57`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:69-85`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`

**规则**：`DefaultOverdueStatesAccount` **不**从其配置状态里挑选 `isClearState=true` 的状态作为清算状态。清算状态恒为状态集内建的 `clearState`（BR-O1/TERM-O3）：
- `calculateOverdueState` 未命中时返回内建 clearState；
- `findState` 对保留名特判返回内建 clearState；
- `getClearState()` 直接返回内建 clearState。
**用户配置 `<isClearState>true</isClearState>` 的真实影响**：仅当该状态**自身被 condition 命中**而成为 next 时，`nextOverdueState.isClearState()` 为真，从而影响 `OverdueStateApplicator.getReevaluationInterval`（用状态集级 `initialReevaluationInterval` 而非状态级 `autoReevaluationInterval`）以及「是否清空未来通知」的判断（applicator 123-125 行）。它**不会**让该状态成为兜底状态。
**校验死分支**：`DefaultOverdueStateSet.validate` 里对 `CAT_MISSING_CLEAR_STATE` 的检查（78-80 行）在现状下不可达——因为 `getClearState()` 从不抛异常。

## BR-O5 时间条件为「含等于」（inclusive）：triggerDate <= now

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

## BR-O6 时间/间隔单位仅 DAYS/WEEKS/MONTHS/YEARS；UNLIMITED 非法

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

## BR-O7 时间条件缺省 number=-1 会立即命中（反直觉默认）

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

## BR-O8 数值条件：发票数量用 >=，余额用 BigDecimal.compareTo（scale 无关）

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

## BR-O9 控制标签条件仅限 ControlTagType 枚举，按 tagDefinitionId 比对

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

## BR-O10 apply 动作执行顺序（通知 → no-op → 取消 → 标签 → 存状态 → 事件）

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

## BR-O11 状态名不变 = no-op：跳过取消/标签/持久化/事件

- **类型**: 业务规则
- **同义词**: 状态同名无操作, 幂等短路, no-op on same state name, name equality short circuit
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:127-132`

**规则**：`apply` 中唯一的变化判定是 `previousOverdueState.getName().equals(nextOverdueState.getName())`（127 行）。
- 相同 → log.debug 后 `return`；**不**取消订阅、**不**切换 AUTO_INVOICING_OFF、**不**写 BlockingState、**不**发 `OverdueChangeInternalEvent`。
- 不同 → 继续执行全部动作。
**推论（精确）**：判定只比较**名字**，不比较状态的其它属性。因此若运营只改了某状态的 `blockChanges`/`externalMessage`/`subscriptionCancellationPolicy` 而**状态名保持不变**，已有账户**不会**被重新施加动作；配置变更只对「未来发生状态名迁移」的账户生效。这解释了为何修改配置后需要账户发生真实状态迁移才能观察副作用。

## BR-O12 clear 路径动作顺序（先写 clear 状态，与 apply 相反）

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

## BR-O13 blockBilling 转移判定基于 disableEntitlement 标志，而非状态名

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

## BR-O14 AUTO_INVOICING_OFF 仅在 block/unblock billing 转移时切换

- **类型**: 业务规则
- **同义词**: 自动开票标签切换, AUTO_INVOICING_OFF 开关时机, toggle timing, avoid extra credit, tag transition
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:176-183`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:237-253`

**规则**：
- 若 `isBlockBillingTransition` → `tagApi.addTag(accountId, ObjectType.ACCOUNT, ControlTagType.AUTO_INVOICING_OFF.getId(), ctx)`（237-243 行），避免继续开票产生多余信用。
- 若 `isUnblockBillingTransition` → `tagApi.removeTag(...)`；若标签不存在，捕获 `TagApiException` 且仅当错误码 `TAG_DOES_NOT_EXIST` 时忽略，其它错误包装成 `OverdueApiException`（245-253 行）。
- 其余情况（无 block billing 状态变化）**完全不触碰**该标签。
**与 BR-O11/BR-O13 的关系**：该切换只在「状态名变化」后执行，且只在 `disableEntitlement` 导致 blockBilling 翻转时发生。clear 路径同样调用它（从 block billing → clear 会移除标签）。

## BR-O15 复评通知基期 = effectiveDate；间隔来源随 next 是否 clear 切换

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
- **基期**：`createFutureNotification` 使用 `effectiveDate.plus(reevaluationInterval)`（121 行），即**事件生效时间**，而非 `context.getCreatedDate()`（注意：条件评估用的是 CreatedDate 的 LocalDate，见 BR-O25）。
- **清空条件**：`else if (nextOverdueState.isClearState())` → `clearFutureNotification`（123-125 行），删除该账户所有未来 check 通知（按 accountRecordId/tenantRecordId 检索）。
- **间隔与「是否时间驱动」无关**：即使条件没有任何时间项，只要 next 非 clear，也会按其 `autoReevaluationInterval` 定时复评。

## BR-O16 非法复评间隔：仅 OVERDUE_NO_REEVALUATION_INTERVAL 被吞成 null

- **类型**: 业务规则
- **同义词**: 复评间隔异常, 无间隔错误码, invalid interval handling, OVERDUE_NO_REEVALUATION_INTERVAL swallow, OverdueException
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueState.java:119-125`

**规则**：`getReevaluationInterval` 捕获 `OverdueApiException` 后：
- 若 `e.getCode() == ErrorCode.OVERDUE_NO_REEVALUATION_INTERVAL.getCode()` → 返回 `null`（applicator 上游据此不插入通知）。
- **其它任何错误码** → 包装成 `OverdueException(e)` 抛出，中止本次 apply。
`OVERDUE_NO_REEVALUATION_INTERVAL` 由 `DefaultOverdueState.getAutoReevaluationInterval()` 在 `null`/`UNLIMITED`/`number==0` 时抛出（121-123 行）。
**注意**：clear 分支的 `getInitialReevaluationInterval()` **不抛异常**——它在 `DefaultOverdueStatesAccount` 内直接返回 null（见 BR-O6），所以该 catch 的错误码分支主要服务于非 clear 状态。

## BR-O17 check 队列去重：保留最早；新到期时间 <= 已有最早时新通知胜出

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

## BR-O18 async 队列去重：已有任意未来通知则跳过（REFRESH/CLEAR 混排不确定）

- **类型**: 业务规则
- **同义词**: async 队列去重, 有则跳过, 刷新清除混排, async queue dedup, skip if any, nondeterministic REFRESH CLEAR
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/notification/OverdueAsyncBusPoster.java:47-57`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:168-177`

**规则**：`OverdueAsyncBusPoster.cleanupFutureNotificationsFormTransaction` 直接返回 `Iterables.size(futureNotifications) == 0`：
- 该账户**已有任意未来通知** → **跳过**插入新通知（不区分该通知是 REFRESH 还是 CLEAR，也不比较时间）。
- 无任何未来通知 → 插入。
**源码自述的近似性**（52-54 行注释）：可能出现「已有 REFRESH 又来了 CLEAR」却插入失败的情况；若真发生，说明逾期状态变化极快、行为本就非确定。
**调度时间**：`OverdueListener.insertBusEventIntoNotificationQueue` 以 `callContext.getCreatedDate()` 作为未来通知时间（177 行）。**对照**：check 队列由 applicator 以 `effectiveDate+interval` 调度（BR-O15），两者基期不同。

## BR-O19 订阅取消：范围（非 ADD_ON）、查询上下文与批处理

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

## BR-O20 取消策略 → BillingActionPolicy 映射与未知值异常

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
**触发时机**：仅在状态名变化后（BR-O11）执行；取消前先做 BR-O19 的范围过滤。

## BR-O21 全局锁：ACCNT_INV_PAY + 账户 UUID，最多 50 次，失败以 reschedule 间隔重排

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
**与通知键的对照**：通知按 `accountRecordId + tenantRecordId` 检索/去重（ENT-O5），锁按**账户 UUID**；两者键口径不同。

## BR-O22 配置加载两阶段与失败降级（保留内建默认，Overdue system disabled）

- **类型**: 业务规则
- **同义词**: 配置加载两阶段, 加载失败降级, 保留内建默认, config bootstrap, load failure fallback, Overdue system disabled
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:53-66`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:68-86`, `overdue/src/main/java/org/killbill/billing/overdue/service/DefaultOverdueService.java:91-101`

**规则**：
1. **阶段一（构造期）**：无条件加载 classpath `NoOverdueConfig.xml` 得到 `defaultOverdueConfig`；若失败则 `new DefaultOverdueConfig()`（空 accountOverdueStates → 状态数组为空）并记 `error`。
2. **阶段二（service LOAD_CATALOG）**：`DefaultOverdueService.loadConfig` 调 `loadDefaultOverdueConfig(properties.getConfigURI())`；`configURI` 为 null/空或解析抛异常 → `missingOrCorruptedDefaultConfig=true`，**不覆盖**当前 `defaultOverdueConfig`（即仍保留阶段一的内建 NoOverdue 配置），仅 `log.warn("Overdue system disabled: unable to load the overdue config from uri='{}'")`，`isConfigLoaded` 保持 false。
**关键结论**：配置加载失败**不会**清空为 null，而是**回退到阶段一的内建默认（等价于不催收）**；「禁用」只是日志语义，运行期行为即 clear。`loadDefaultOverdueConfig` 内部自行捕获所有异常，因此 service 侧的 `catch(OverdueApiException)` 实为防御性死分支。

## BR-O23 租户配置读取：内部租户恒默认、未命中回退默认、非法转 OVERDUE_INVALID_FOR_TENANT

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

## BR-O24 上传逾期配置不即时校验，错误延迟到读取时暴露

- **类型**: 业务规则
- **同义词**: 上传不校验, 延迟校验, 延迟失败, upload without validation, deferred validation, lazy parse
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:66-89`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:115-132`

**规则**：
- `uploadOverdueConfig(String overdueXML, CallContext)` 的步骤仅为：查旧值非空则 `deleteTenantKey("OVERDUE_CONFIG")` → `addTenantKeyValue("OVERDUE_CONFIG", overdueXML)` → `overdueConfigCache.clearOverdueConfig(ctx)`。**全程不解析、不校验 XML**（无 XMLLoader 调用）。
- `uploadOverdueConfig(OverdueConfig, CallContext)` 只是先 `XMLWriter.writeXML` 序列化，再走上面的 String 版本。
- 因此：上传**成功返回**不代表配置合法；非法 XML 会在后续**读取/缓存加载**时抛 `OVERDUE_INVALID_FOR_TENANT`（BR-O23）。
**对照**：主流程的 `DefaultOverdueState.validate`（名字长度等）只在 XMLLoader 解析时触发，同样属于「读取期校验」。

## BR-O25 父账户委派：仅计算上下文用父，被评估账户对象仍是子

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

## BR-O26 BillingStateCalculator 的日期口径、排序 tie-break 与余额求和

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

## BR-O27 监听器门控：BusDispatcherOptimizer + 标签 objectType 精确匹配

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

## BR-O28 refresh 早退：配置状态数 < 1 直接返回

- **类型**: 业务规则
- **同义词**: 刷新早退, 空配置不处理, refresh early return, no configuration, size < 1
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:89-92`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapperFactory.java:95-119`

**规则**：`OverdueWrapper.refresh` 第一行判断 `if (overdueStateSet.size() < 1) return;`——**取锁之前**即返回，不计算、不加锁、不写状态。
`OverdueWrapperFactory.getOverdueStateSet` 在配置描述为 null、或其 `accountOverdueStates` 为 null 时，返回一个**匿名空状态集**（`getStates()` 返回空数组、`getInitialReevaluationInterval()` 返回 null），其 `size()==0` 正好触发早退。
**与 clear 的差异**：`clear(...)` **没有** size<1 早退（129-142 行）——即使配置为空也可执行清算（写 clear 状态、清通知）。

## WF-O1 默认逾期配置加载与生效流程（构造 → 属性 → 校验 → 缓存）

- **类型**: 业务流程
- **同义词**: 默认配置加载流程, 配置引导, config bootstrap flow, default overdue config loading, NoOverdueConfig
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:53-66`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:68-91`, `overdue/src/main/java/org/killbill/billing/overdue/service/DefaultOverdueService.java:91-101`, `overdue/src/main/resources/NoOverdueConfig.xml:20-27`

**步骤**：
1. `DefaultOverdueConfigCache` 构造：尝试 classpath 加载 `NoOverdueConfig.xml`（内含单个 `<state name="Clear"><isClearState>true</isClearState></state>`，无条件）作为 `defaultOverdueConfig`；异常则退化为 `new DefaultOverdueConfig()`。
2. `DefaultOverdueService.loadConfig`（生命周期 `LOAD_CATALOG`，`synchronized`，仅当 `!isConfigLoaded`）：读取 `properties.getConfigURI()`（默认 `NoOverdueConfig.xml`，可由 `org.killbill.overdue.uri` 覆盖）。
3. `loadDefaultOverdueConfig(configURI)`：null/空/解析异常 → 记 warn「Overdue system disabled」并**保留阶段一默认**；成功 → 覆盖 `defaultOverdueConfig`（`XMLLoader` 会执行 `validate` 链，名字长度等校验在此触发）。
4. 成功时 `isConfigLoaded=true`；失败时保持 false（该标志此后不再被用于重试，因为生命周期只跑一次）。
5. 运行期 `getOverdueConfig`：内部租户直接返回默认；普通租户查 `TENANT_OVERDUE_CONFIG` 缓存，未命中回退默认。

```mermaid
flowchart TD
  A[Cache 构造] --> B{加载 classpath NoOverdueConfig.xml}
  B -- 成功 --> C[defaultOverdueConfig = Clear 配置]
  B -- 失败 --> D[defaultOverdueConfig = new DefaultOverdueConfig 空配置]
  C --> E[LOAD_CATALOG: loadConfig getConfigURI]
  D --> E
  E -- 解析成功 --> F[覆盖 defaultOverdueConfig; isConfigLoaded=true]
  E -- 空/异常 --> G[warn Overdue system disabled; 保留既有默认]
  F --> H[运行期 getOverdueConfig]
  G --> H
```

## WF-O2 运行时查询账户当前逾期状态流程

- **类型**: 业务流程
- **同义词**: 查询逾期状态流程, 当前状态解析, runtime overdue state query, getOverdueStateFor flow, resolve current state
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:91-99`, `overdue/src/main/java/org/killbill/billing/overdue/wrapper/OverdueWrapper.java:115-119`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:41-52`

**步骤**：
1. 客户端调用 `OverdueApi.getOverdueStateFor(accountId, tenantContext)`。
2. 以 accountId + tenant 构造 `InternalTenantContext`（`createInternalTenantContext` 的重载，填充 accountRecordId）。
3. `blockingInternalApi.getBlockingStateForService(accountId, BlockingStateType.ACCOUNT, "overdue-service", ctx)` 读取账户级 BlockingState。
4. `stateName = blockingState != null ? blockingState.getStateName() : OverdueWrapper.CLEAR_STATE_NAME`。
5. 读取该租户 `OverdueConfig` → `getOverdueStatesAccount()` → `states.findState(stateName)`。
6. 返回解析到的 `OverdueState`（携带该状态的 `name`、`externalMessage`、`blockChanges`、`disableEntitlement`、`subscriptionCancellationPolicy`、`isClearState`）。
**失败路径**：若持久化的 stateName 在当前配置中不存在（例如配置被改名/删除），且它不是保留名 → `findState` 抛 `OverdueApiException(CAT_NO_SUCH_OVERDUE_STATE, stateName)`。同一映射也被 `OverdueWrapper.refreshWithLock`/`clearWithLock` 使用，因此配置改名会让 refresh/clear 一并失败。

## WF-O3 租户逾期配置上传与「延迟校验」流程

- **类型**: 业务流程
- **同义词**: 上传配置流程, 延迟校验, tenant config upload flow, deferred validation, OVERDUE_CONFIG
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:66-89`, `overdue/src/main/java/org/killbill/billing/overdue/caching/OverdueCacheInvalidationCallback.java:39-43`, `overdue/src/main/java/org/killbill/billing/overdue/caching/DefaultOverdueConfigCache.java:115-132`

**步骤**：
1. 调用 `uploadOverdueConfig(String)` 或 `uploadOverdueConfig(OverdueConfig)`（后者先 `XMLWriter.writeXML`）。
2. 若租户键 `OVERDUE_CONFIG` 已有值 → `deleteTenantKey` 删除旧值。
3. `addTenantKeyValue("OVERDUE_CONFIG", overdueXML)` 写入新 XML（**不解析**）。
4. `overdueConfigCache.clearOverdueConfig(internalTenantContext)` 清除该租户缓存（内部租户 no-op）。
5. 另经 `TenantKey.OVERDUE_CONFIG` 的 `CacheInvalidationCallback`（`OverdueCacheInvalidationCallback.invalidateCache`）再次清除租户缓存。
6. **首次读取时**才由缓存加载器解析 XML；解析失败 → `OVERDUE_INVALID_FOR_TENANT`（上传时无感知）。
**异常语义**：`OverdueConfig` 对象序列化失败 → `OVERDUE_INVALID_FOR_TENANT`；`TenantApiException` → 包装为 `OverdueApiException`。

## SM-O1 状态选择 / 清算判定状态机（配置态 + 内建 CLEAR）

- **类型**: 状态机
- **同义词**: 状态选择状态机, 清算判定, state selection machine, config state vs built-in clear, calculateOverdueState
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueStateSet.java:37-67`, `overdue/src/main/java/org/killbill/billing/overdue/config/DefaultOverdueCondition.java:69-84`, `api/src/main/java/org/killbill/billing/overdue/config/api/OverdueStateSet.java:24-44`

**说明**：每次评估（refresh 或定时复评）都从 BillingState 重新计算目标状态；**不是事件驱动的迁移图，而是「按声明顺序取首个命中，否则内建 CLEAR」的函数式选择**。配置状态之间不需要（也没有）显式迁移边；从任意状态到任意状态都合法，只要条件命中。无 `<condition>` 的配置状态在此图中不可达。

```mermaid
stateDiagram-v2
  [*] --> 评估
  评估 --> 第1个状态: 按声明顺序遍历
  第1个状态 --> 第2个状态: condition=false 或 condition 为空
  第2个状态 --> 内建CLEAR: 全部未命中
  第1个状态 --> 命中: condition=true
  第2个状态 --> 命中: condition=true
  命中 --> [*]
  内建CLEAR --> [*]
```

**注**：内建 `<state name="Clear" isClearState="true">`（NoOverdueConfig）只是配置里的普通状态且**无 condition**，因此它自身永不作为选择结果出现；真正的清算出口是状态集内建的 `__KILLBILL__CLEAR__OVERDUE_STATE__`（BR-O4）。

## SM-O2 复评通知调度决策状态机

- **类型**: 状态机
- **同义词**: 通知调度状态机, 复评决策, notification scheduling machine, reevaluation decision, schedule vs clear
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:109-125`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:160-174`, `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:275-283`

**说明**：由「next 是否 clear」与「是否有欠费」共同决定是调度、跳过还是清空未来通知。

```mermaid
flowchart TD
  A[apply] --> B{next 非 clear?}
  B -- 是 --> C[取状态级 autoReevaluationInterval]
  B -- 否 --> D{有 firstState 且有最早未付发票日期?}
  D -- 是 --> E[取状态集级 initialReevaluationInterval]
  D -- 否 --> F[clearFutureNotification 清空该账户全部未来通知]
  C --> G{interval == null?}
  E --> G
  G -- 是 --> H[不插入通知]
  G -- 否 --> I["createFutureNotification(effectiveDate + interval)"]
```

**可能产生通知间隔为 null 的情形**：非 clear 状态的 `autoReevaluationInterval` 缺省/`number==0`/`UNLIMITED`（BR-O16）；或状态集未配置 `initialReevaluationInterval`（BR-O6）。此时即使处于催收状态也不会有定时复评。

<!-- module: overdue | supplement cards | 补全 kb2 未覆盖的精确枚举/默认值/条件行为 | extracted from source reads -->


