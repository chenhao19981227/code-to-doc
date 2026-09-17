# 待人工确认的问题

### 推断项（🟡 inferred）

- `BR-039` **计费状态快照的构造与限制**（模块 overdue）：由源码/注释推断，需验证。溯源：`overdue/src/main/java/org/killbill/billing/overdue/calculator/BillingStateCalculator.java:67-84`

### 缺证据项（🔴 gap）

- `ROLE-001` **发票模块的权限控制位置**（模块 invoice）：缺少直接代码证据，需人工补充。
- `ROLE-002` **逾期模块的权限控制位置**（模块 overdue）：缺少直接代码证据，需人工补充。

### 其它待确认

- `BR-039`(overdue)：源码将上次支付失败响应硬编码为 `INSUFFICIENT_FUNDS`，请确认生产环境是否接入真实支付响应。
- `ROLE-001` / `ROLE-002`：两模块均无模块内权限注解，请确认鉴权由 jaxrs/安全模块承担的具体权限点。
- Kill Bill 核心领域枚举来自外部 `killbill-api` 构件，本仓库无其定义文件；相关状态/类型的完整取值需对照该构件。
