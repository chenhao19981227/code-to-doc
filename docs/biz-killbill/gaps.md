# 未确定项（gaps）

共 2 条 🔴 gap 卡。

### ROLE-001 发票模块的权限控制位置

- **模块**: invoice
- **缺失点**: 发票模块的权限控制位置
- **说明**: invoice 模块内部**未发现** `@Secured`/`@PreAuthorize`/`@RequiresPermissions` 等权限注解（全仓库仅 util 测试类出现 `@RequiresPermissions`）。发票 API 的鉴权应由 jaxrs 层或外部安全模块承担，但本模块源码无法证实具体权限点，需人工确认。
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:282-306`

### ROLE-002 逾期模块的权限控制位置

- **模块**: overdue
- **缺失点**: 逾期模块的权限控制位置
- **说明**: overdue 模块内部**未发现**任何方法级/类级权限注解（`@Secured`/`@PreAuthorize`/`@RequiresPermissions` 等）。逾期配置上传等操作的鉴权应由 jaxrs 层或外部安全模块承担，但本模块源码无法证实具体权限点，需人工确认。
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:42-58`
