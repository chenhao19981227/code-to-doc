# 待人工确认的问题 (Questions)


> 需要人工确认的事项：🟡 inferred（推断待验证）、🔴 gap（缺证据）、以及消歧项。共 8 张卡 + 1 个消歧项。

## 一、推断待验证 / 缺证据卡片

### ROLE-001 目录管理的租户范围（无独立角色权限）（🟡）

**待确认**：**说明**：catalog 模块与 `CatalogResource` 中**未发现**任何 `@RequiresPermissions`/角色注解；目录的读取与上传（`GET/POST /1.0/kb/catalog/xml`）通过 `TenantContext` / `CallContext` 限定在**租户**范围内，具体鉴权由上层安全过滤器统一处理。

**缺口**：无法从本模块代码确定具体角色名、权限点或资源可访问性矩阵，需结合安全/权限模块确认（标 🟡）。

### ROLE-002 发票模块无内建权限注解（🔴）

**待确认**：**说明**：通读 invoice 模块主源码未发现任何角色/权限注解或权限判定逻辑，授权（谁能开票/作废/退款）不在此模块实现，推测由上层（JAX-RS / 平台安全层）负责。**需人工确认**权限点清单与所属角色——本模块无法给出确定结论。

### ROLE-004 租户管理员（租户级逾期配置上传）（🟡）

**待确认**：**角色/权限**：通过 `OverdueApi.uploadOverdueConfig` 上传/替换租户的逾期规则 XML，底层写租户 KV（`TenantUserApi`）。源码只体现了 API 行为，**未见权限注解**；「谁能调用该 API（租户管理员/运营）」由外部认证授权层决定，故标 inferred。需要人工确认 Kill Bill 的权限模型。

### ROLE-005 运营/客服（控制标签操作权）（🟡）

**待确认**：**角色/权限**：运营人员通过给账户打/摘 `OVERDUE_ENFORCEMENT_OFF` 来豁免或恢复催收；通过给发票打/摘 `WRITTEN_OFF` 来核销并触发重评。模块本身**不定义权限注解**，只响应标签事件；「谁有权打标签」属外部 tag 权限体系，故标 inferred。

### ROLE-006 逾期状态查询者（读取当前状态与配置）（🟡）

**待确认**：**角色/权限**：读接口包括 `getOverdueConfig(tenantContext)` 与 `getOverdueStateFor(accountId, tenantContext)`（返回该账户当前逾期状态；无 blocking state 时解析为 clear）。源码只展示 API 契约，未包含权限注解；访问控制由上层（jaxrs/权限体系）承担，故标 inferred。

### ROLE-008 支付控制插件名称配置（org.killbill.payment.invoice.plugin）（🔴）

**待确认**：**说明**：系统属性 `org.killbill.payment.invoice.plugin`（默认空字符串）用于配置默认的支付控制插件名列表（`getPaymentControlPluginNames`）。但本模块源码中未直接看到该配置被消费的具体位置（可能在下游 dispatcher 或 jaxrs 层），因此其确切作用/权限语义需人工确认，置信度标为 🔴。

### ROLE-011 用量模块无显式权限注解（🟡）

**待确认**：**观察**：对 `usage/src/main/java` 全量检索未发现任何 `@RequiresPermissions`、`@RolesAllowed`、`Permission` 或 Spring/Shiro 风格的安全注解；`UsageModule` 仅做依赖装配，无安全绑定。

**推断**：用量模块本身不实现角色/权限点校验；访问控制依赖（a）多租户隔离（ROLE-001）与（b）上层 API/服务容器（REST 层）的认证与授权设施。具体「哪个角色能记录/查询用量」在本模块源码中**无法确定**，需人工确认上层安全配置。因此标 🟡，不作为 🟢 结论。

### TERM-046 MANUAL_PAY（手动支付标签）（🟡）

**待确认**：**定义**：与 `AUTO_PAY_OFF` 配套的账户控制标签，用于标记账户需人工发起支付。本次溯源仅在 invoice 控制插件中直接看到 `AUTO_PAY_OFF` 的判定逻辑（`ControlTagType.isAutoPayOff`），`MANUAL_PAY` 的定义在 util 模块的 `ControlTagType` 中，未在本模块代码直接引用，故置信度标为 🟡。


## 二、消歧项（同名词不同义，未合并）

### DefaultDuration / Duration 的同名歧义

- **A**: catalog ENT-007 时长实体 (Duration)：目录阶段时长定义（unit+number）
- **B**: overdue ENT-012 时长配置 DefaultDuration：逾期配置中的时长（重新评估间隔等）
- **处理**: 同名类位于不同包/语义域，未合并；运行时需按模块上下文区分。


## 三、合并决策记录（跨模块去重，供人工复核）

### MERGE-01 计费模式 (BillingMode) → TERM-011

- **合并来源**: catalog/TERM-008, invoice/TERM-010, usage/TERM-009, usage/TERM-010

### MERGE-02 用量类型 (UsageType : CONSUMABLE / CAPACITY) → TERM-007

- **合并来源**: catalog/TERM-010, invoice/TERM-005, usage/TERM-007, usage/TERM-008

### MERGE-03 用量计费 (Usage) → TERM-001

- **合并来源**: catalog/TERM-009, usage/TERM-001

### MERGE-04 分层 (Tier) → TERM-008

- **合并来源**: catalog/TERM-011, invoice/TERM-006

### MERGE-05 发票支付类型 (InvoicePaymentType) → TERM-024

- **合并来源**: invoice/TERM-003, payment/TERM-010

### MERGE-06 自动开票关闭标签 (AUTO_INVOICING_OFF) → TERM-028

- **合并来源**: invoice/TERM-009, overdue/TERM-011

### MERGE-07 发票支付 (InvoicePayment) → ENT-017

- **合并来源**: invoice/ENT-008, payment/ENT-005

### MERGE-08 用量聚合规则（CAPACITY 取峰值 / CONSUMABLE 累加） → BR-047

- **合并来源**: invoice/BR-038, usage/BR-011

### MERGE-09 用量重复计费防护（tracking id 去重 + 已开票区间跳过） → BR-036

- **合并来源**: invoice/BR-039, usage/BR-001

### MERGE-10 目录中未定义的用量处理（可挂起账户） → BR-052

- **合并来源**: invoice/BR-016, invoice/BR-040, usage/BR-015

### MERGE-11 用量各模式的必填结构校验 → BR-010

- **合并来源**: catalog/BR-010, usage/BR-013
