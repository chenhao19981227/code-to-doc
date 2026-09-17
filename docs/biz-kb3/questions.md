# 待人工确认的问题（Questions）

> 由 🟡 `inferred`（推断待验证）与 🔴 `gap`（缺证据）卡片，以及消歧项汇总。共 13 张待确认卡 + 消歧条目。

---

### 1. 推断待验证（🟡 inferred）

- **BR-278** CHARGEBACK_PENDING 状态不存在于状态机 XML（不一致）（模块 payment）— 由命名/模式推断，未验证；溯源: `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:63`, `payment/src/main/java/org/killbill/billing/payment/core/sm/PaymentStateMachineHelper.java:142-161`, `payment/src/main/resources/org/killbill/billing/payment/PaymentStates.xml:379-409`
- **ROLE-003** 租户管理员（租户级逾期配置上传）（模块 overdue）— 由命名/模式推断，未验证；溯源: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:66-89`
- **ROLE-004** 运营/客服（控制标签操作权）（模块 overdue）— 由命名/模式推断，未验证；溯源: `overdue/src/main/java/org/killbill/billing/overdue/applicator/OverdueStateApplicator.java:334-349`, `overdue/src/main/java/org/killbill/billing/overdue/listener/OverdueListener.java:96-119`
- **ROLE-005** 逾期状态查询者（读取当前状态与配置）（模块 overdue）— 由命名/模式推断，未验证；溯源: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:60-64`, `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:91-99`
- **ROLE-006** 目录管理的租户范围（无独立角色权限）（模块 catalog）— 由命名/模式推断，未验证；溯源: `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/CatalogResource.java:143-263`
- **ROLE-011** 用量模块无显式权限注解（模块 usage）— 由命名/模式推断，未验证；溯源: `usage/src/main/java/org/killbill/billing/usage/glue/UsageModule.java:40-64`
- **TERM-056** 计费周期 BillingPeriod 枚举（catalog 内可证取值）（模块 catalog）— 由命名/模式推断，未验证；溯源: `catalog/src/main/java/org/killbill/billing/catalog/DefaultPlan.java:234-237`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultRecurring.java:90-111`, `catalog/src/main/resources/EmptyCatalog.xml:53-64`
- **TERM-060** 固定费类型 FixedType 枚举（模块 catalog）— 由命名/模式推断，未验证；溯源: `catalog/src/main/java/org/killbill/billing/catalog/DefaultFixed.java:41-45`, `catalog/src/main/java/org/killbill/billing/catalog/DefaultFixed.java:75-82`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogSafetyInitializer.java:58-65`
- **TERM-062** 计划对齐枚举 PlanAlignmentCreate / PlanAlignmentChange（模块 catalog）— 由命名/模式推断，未验证；溯源: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:125-129`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:166-170`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:338-348`
- **TERM-063** 计费对齐 BillingAlignment 全枚举与回退（模块 catalog）— 由命名/模式推断，未验证；溯源: `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultPlanRules.java:137-141`, `catalog/src/main/java/org/killbill/billing/catalog/rules/DefaultCasePhase.java:43-49`, `catalog/src/main/java/org/killbill/billing/catalog/CatalogUpdater.java:350-352`
- **TERM-071** MANUAL_PAY（手动支付标签）（模块 payment）— 由命名/模式推断，未验证；溯源: `payment/src/main/java/org/killbill/billing/payment/invoice/InvoicePaymentControlPluginApi.java:376-380`

### 2. 缺证据（🔴 gap）

- **ROLE-001** 发票模块无内建权限注解（模块 invoice）— 无法确定，需人工确认；溯源: 无（在 `invoice/src/main/java` 范围内未发现 `@RequiresPermissions` / `SecurityApi` / `PermissionType` 等权限判定）
- **ROLE-008** 支付控制插件名称配置（org.killbill.payment.invoice.plugin）（模块 payment）— 无法确定，需人工确认；溯源: `util/src/main/java/org/killbill/billing/util/config/definition/PaymentConfig.java:92-100`

### 3. 消歧项（同名/同词不同上下文）

- **同词跨模块**：TERM-005 用量类型（UsageType: CAPACITY / CONSUMABLE）（invoice）；TERM-042 用量类型 (Usage Type)（catalog）
- **同词跨模块**：TERM-010 计费模式（BillingMode: IN_ADVANCE / IN_ARREAR）（invoice）；TERM-040 计费模式 (Billing Mode)（catalog）
- **卡内记录的歧义**：BR-190 跨版本同名计划形状必须一致（模块 catalog）
- **卡内记录的歧义**：BR-206 同名条目在目录内「后写覆盖」而非报错（唯一性陷阱）（模块 catalog）
- **卡内记录的歧义**：TERM-031 两个同名的 OverdueConfig（XML 配置对象 vs 属性/多租户接口）（模块 overdue）

### 4. 合并映射（已合并的重复卡）

- BR-292 ← BR-038(invoice)
- BR-295 ← BR-016(invoice)
- BR-180 ← BR-013(usage)
- TERM-092 ← TERM-C14(catalog)
- TERM-094 ← TERM-C08(catalog)
- BR-319 ← BR-I21(invoice)
- BR-313 ← BR-I20(invoice)