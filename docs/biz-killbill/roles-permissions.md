# 角色/权限（ROLE）

> 来源模块：invoice, overdue。检索单元 = 每个 `## ` 二级标题块。

## ROLE-001 发票模块的权限控制位置

- **类型**: 角色/权限
- **同义词**: 发票权限, 接口鉴权, invoice permissions, access control
- **模块**: invoice
- **置信度**: 🔴 gap
- **溯源**: `invoice/src/main/java/org/killbill/billing/invoice/InvoiceDispatcher.java:282-306`

**缺口**：invoice 模块内部**未发现** `@Secured`/`@PreAuthorize`/`@RequiresPermissions` 等权限注解（全仓库仅 util 测试类出现 `@RequiresPermissions`）。发票 API 的鉴权应由 jaxrs 层或外部安全模块承担，但本模块源码无法证实具体权限点，需人工确认。

<!-- module: invoice | cards: 46 | extracted_at: 2026-09-16T00:00:00Z -->

## ROLE-002 逾期模块的权限控制位置

- **类型**: 角色/权限
- **同义词**: 逾期权限, 催收鉴权, overdue permissions, access control
- **模块**: overdue
- **置信度**: 🔴 gap
- **溯源**: `overdue/src/main/java/org/killbill/billing/overdue/api/DefaultOverdueApi.java:42-58`

**缺口**：overdue 模块内部**未发现**任何方法级/类级权限注解（`@Secured`/`@PreAuthorize`/`@RequiresPermissions` 等）。逾期配置上传等操作的鉴权应由 jaxrs 层或外部安全模块承担，但本模块源码无法证实具体权限点，需人工确认。

<!-- module: overdue | cards: 32 | extracted_at: 2026-09-16T00:00:00Z -->
