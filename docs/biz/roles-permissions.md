# 角色与权限 (roles-permissions)

本文件收录角色、权限点与资源可访问性卡。检索单元为每个 `## ROLE-xxx` 二级标题块。

## ROLE-001 方法级安全总开关（@PreAuthorize 生效前提）

- **类型**: 角色/权限
- **同义词**: 方法级权限, 方法安全, method security, prePostEnabled, @EnableGlobalMethodSecurity, 注解鉴权, 启用方法安全
- **模块**: app
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/MallApplication.java:7-8`

**说明**：应用以 `@SpringBootApplication` 启动，并通过 `@EnableGlobalMethodSecurity(prePostEnabled = true)` 开启方法级安全。因此本系统中出现的 `@PreAuthorize` 注解在方法调用时生效，是退款等接口鉴权的技术前提。

## ROLE-002 客服（CS）可代客发起退款

- **类型**: 角色/权限
- **同义词**: 客服, CS, 客服权限, 代客退款, customer service, 发起退款权限, 售后客服
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:20-23`

**说明**：角色 `CS` 或 `CS_LEAD` 可调用 `POST /api/refunds` 发起退款申请，方法注释「客服可代客发起退款」，权限表达式 `@PreAuthorize("hasAnyRole('CS', 'CS_LEAD')")`。

## ROLE-003 客服主管（CS_LEAD）审批退款

- **类型**: 角色/权限
- **同义词**: 客服主管, CS_LEAD, 主管, 主管审批, 退款审批权限, refund approval
- **模块**: refund
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/refund/RefundController.java:28-30`

**说明**：仅角色 `CS_LEAD` 可调用 `POST /api/refunds/{id}/approve` 审批退款，权限表达式 `@PreAuthorize("hasRole('CS_LEAD')")`。

**已知角色汇总**：`CS`（客服，可发起退款）、`CS_LEAD`（客服主管，可发起并审批退款）。除此之外代码未定义其它角色或 URL 级授权规则（见 questions.md）。
