# 角色与权限（Roles & Permissions）

> Kill Bill 业务知识库 v3（合并 kb2 既有卡 + kb3 补充卡）；共 11 张卡。

---

## ROLE-001 发票模块无内建权限注解

- **类型**: 角色/权限
- **同义词**: 发票权限, invoice permission, 权限控制, 访问控制, authorization
- **模块**: invoice
- **置信度**: 🔴 gap
- **溯源**: 无（在 `invoice/src/main/java` 范围内未发现 `@RequiresPermissions` / `SecurityApi` / `PermissionType` 等权限判定）

**说明**：通读 invoice 模块主源码未发现任何角色/权限注解或权限判定逻辑，授权（谁能开票/作废/退款）不在此模块实现，推测由上层（JAX-RS / 平台安全层）负责。**需人工确认**权限点清单与所属角色——本模块无法给出确定结论。

## ROLE-002 内部系统角色 OverdueService（自动催收执行者）

- **类型**: 角色/权限
- **同义词**: 系统角色, 内部用户, 催收服务账号, OverdueService system user, SYSTEM user, INTERNAL call origin
- **模块**: overdue
- **置信度**: 🟢 confirmed
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:159-166`, `overdue/src/main/java/org/killbill/billing/overdue/notification/DefaultOverdueNotifierBase.java:120-122`

**角色**：逾期自动化以 `CallOrigin.INTERNAL` + `UserType.SYSTEM` 的内部调用身份执行，creator 标识固定为字符串 `"OverdueService"`，携带事件的原始 `userToken`。该身份用于构造 InternalCallContext 并驱动 refresh/clear、写 BlockingState、投递事件——即所有非人工触发的催收动作都以系统身份完成。

## ROLE-003 租户管理员（租户级逾期配置上传）

- **类型**: 角色/权限
- **同义词**: 租户管理员, 配置管理员, 上传逾期配置权限, tenant admin, upload overdue config, OVERDUE_CONFIG permission
- **模块**: overdue
- **置信度**: 🟡 inferred
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:66-89`

**角色/权限**：通过 `OverdueApi.uploadOverdueConfig` 上传/替换租户的逾期规则 XML，底层写租户 KV（`TenantUserApi`）。源码只体现了 API 行为，**未见权限注解**；「谁能调用该 API（租户管理员/运营）」由外部认证授权层决定，故标 inferred。需要人工确认 Kill Bill 的权限模型。

## ROLE-004 运营/客服（控制标签操作权）

- **类型**: 角色/权限
- **同义词**: 运营, 客服, 打标签权限, 催收豁免操作, control tag operator, OVERDUE_ENFORCEMENT_OFF permission, WRITTEN_OFF permission
- **模块**: overdue
- **置信度**: 🟡 inferred
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:334-349`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-119`

**角色/权限**：运营人员通过给账户打/摘 `OVERDUE_ENFORCEMENT_OFF` 来豁免或恢复催收；通过给发票打/摘 `WRITTEN_OFF` 来核销并触发重评。模块本身**不定义权限注解**，只响应标签事件；「谁有权打标签」属外部 tag 权限体系，故标 inferred。

## ROLE-005 逾期状态查询者（读取当前状态与配置）

- **类型**: 角色/权限
- **同义词**: 查询逾期状态, 读取逾期配置, view overdue state, getOverdueStateFor, getOverdueConfig
- **模块**: overdue
- **置信度**: 🟡 inferred
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:60-64`, `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:91-99`

**角色/权限**：读接口包括 `getOverdueConfig(tenantContext)` 与 `getOverdueStateFor(accountId, tenantContext)`（返回该账户当前逾期状态；无 blocking state 时解析为 clear）。源码只展示 API 契约，未包含权限注解；访问控制由上层（jaxrs/权限体系）承担，故标 inferred。

<!-- module: overdue | cards: 63 | extracted_at: 2026-09-16 -->

## ROLE-006 目录管理的租户范围（无独立角色权限）

- **类型**: 角色/权限
- **同义词**: 目录权限, 谁能上传目录, catalog permission, tenant scope, 租户目录, 目录访问控制
- **模块**: catalog
- **置信度**: 🟡 inferred
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/CatalogResource.java:143-263`

**说明**：catalog 模块与 `CatalogResource` 中**未发现**任何 `@RequiresPermissions`/角色注解；目录的读取与上传（`GET/POST /1.0/kb/catalog/xml`）通过 `TenantContext` / `CallContext` 限定在**租户**范围内，具体鉴权由上层安全过滤器统一处理。

**缺口**：无法从本模块代码确定具体角色名、权限点或资源可访问性矩阵，需结合安全/权限模块确认（标 🟡）。

<!-- === CARDS END === -->

<!-- module: catalog | cards: 74 | extracted_at: 2026-09-16 -->

## ROLE-007 系统内部用户（Janitor/重试以 SYSTEM 身份执行）

- **类型**: 角色/权限
- **同义词**: 系统用户, 内部调用, SYSTEM, internal call, 自动任务身份, 重试身份
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/core/janitor/IncompletePaymentTransactionTask.java:197-202`, `payment/src/main/java/org/killbill/billing/payment/retry/BaseRetryService.java:79-82`

**定义**：Janitor 修复交易与重试服务触发重试时，均以内部调用身份执行：`CallOrigin.INTERNAL` + `UserType.SYSTEM`，调用方名称为 `IncompletePaymentTransactionTask` / `payment-service-retry`。这表示这些操作不受终端用户 API 权限约束，由系统自动完成。

## ROLE-008 支付控制插件名称配置（org.killbill.payment.invoice.plugin）

- **类型**: 角色/权限
- **同义词**: 控制插件配置, 默认控制插件, payment control plugin names, invoice plugin, 插件白名单
- **模块**: payment
- **置信度**: 🔴 gap
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:92-100`

**说明**：系统属性 `org.killbill.payment.invoice.plugin`（默认空字符串）用于配置默认的支付控制插件名列表（`getPaymentControlPluginNames`）。但本模块源码中未直接看到该配置被消费的具体位置（可能在下游 dispatcher 或 jaxrs 层），因此其确切作用/权限语义需人工确认，置信度标为 🔴。

## ROLE-009 支付插件注册表 / OSGI 服务名

- **类型**: 角色/权限
- **同义词**: 插件注册表, OSGI 服务, plugin registry, OSGIServiceRegistration, payment plugin registry
- **模块**: payment
- **置信度**: 🟢 confirmed
- **溯源**: `payment/src/main/java/org/killbill/billing/payment/glue/PaymentModule.java:151-154`, `payment/src/main/java/org/killbill/billing/payment/core/PaymentPluginServiceRegistration.java:85-90`

**定义**：支付插件通过 OSGI 服务注册表（`OSGIServiceRegistration<PaymentPluginApi>`，由 `DefaultPaymentProviderPluginRegistryProvider` 提供）按 **插件名**（服务名）注册与查找；控制插件同理（`OSGIServiceRegistration<PaymentControlPluginApi>`）。插件名即支付方式记录中的 `pluginName`，内置值包括 `__EXTERNAL_PAYMENT__`（外部支付）与 `__INVOICE_PAYMENT_CONTROL_PLUGIN__`（发票支付控制）。

<!-- module: payment | incremental build | cards appended in batches -->

## ROLE-010 多租户隔离（tenant_record_id 强制过滤）

- **类型**: 角色/权限
- **同义词**: 租户隔离, 多租户, 租户过滤, tenant isolation, multi-tenancy, tenant_record_id
- **模块**: usage
- **置信度**: 🟢 confirmed
- **溯源**: `usage/src/main/resources/org/killbill/billing/usage/dao/RolledUpUsageSqlDao.sql.stg:26-73`, `util/src/main/resources/org/killbill/billing/util/entity/dao/EntitySqlDao.sql.stg:133-135`

**规则**：所有用量 SQL（去重探测、订阅查询、账户查询）都附加 `AND_CHECK_TENANT`，展开为 `and tenant_record_id = :tenantRecordId`。`rolled_up_usage` 表另有 `(tenant_record_id, account_record_id)` 索引。

**含义**：用量数据严格按租户隔离，跨租户不可见；读取上下文中的 `tenantRecordId` 来自 `InternalTenantContext`（由订阅或账户+调用上下文解析）。

---

## ROLE-011 用量模块无显式权限注解

- **类型**: 角色/权限
- **同义词**: 用量权限, 权限点, permissions, roles, access control, 谁可以记录用量
- **模块**: usage
- **置信度**: 🟡 inferred
- **溯源**: `usage/src/main/java/org/killbill/billing/usage/glue/UsageModule.java:40-64`

**观察**：对 `usage/src/main/java` 全量检索未发现任何 `@RequiresPermissions`、`@RolesAllowed`、`Permission` 或 Spring/Shiro 风格的安全注解；`UsageModule` 仅做依赖装配，无安全绑定。

**推断**：用量模块本身不实现角色/权限点校验；访问控制依赖（a）多租户隔离（ROLE-010）与（b）上层 API/服务容器（REST 层）的认证与授权设施。具体「哪个角色能记录/查询用量」在本模块源码中**无法确定**，需人工确认上层安全配置。因此标 🟡，不作为 🟢 结论。

<!-- module: usage | cards: 47 | extracted_at: 2026-09-16 -->
