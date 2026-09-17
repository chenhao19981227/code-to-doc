# Kill Bill 权限、角色与访问控制知识库 (RBAC)

> 范围：Kill Bill 的权限模型（Permission）、角色（Role）、用户（User）、访问控制（Shiro/RBAC）。
> 引用路径均相对于 Kill Bill 源码根目录 `benchmark/killbill/`。

## ROLE-001 Kill Bill 权限模型总览（基于 Apache Shiro 的 RBAC）

- **类型**: 角色/权限
- **同义词**: 权限模型, 角色权限, 访问控制, 权限体系, RBAC, permission model, role-based access control, access control, authorization
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `profiles/killbill/src/main/resources/shiro.ini:19-29`, `util/src/main/java/org/killbill/billing/util/glue/KillBillShiroModule.java:50-74`

Kill Bill 的权限模型基于 **Apache Shiro**，采用经典三层 RBAC：**用户(User) → 角色(Role) → 权限(Permission)**。
一个用户可绑定多个角色，一个角色可聚合多个权限；登录后由 Shiro 的 `Subject` 执行权限判定。

RBAC 是**默认开启**的，可通过系统属性 `-Dkillbill.server.rbac=false` 关闭（`KillBillShiroModule.isRBACEnabled()` 默认返回 `true`）。Shiro 配置默认从 `classpath:shiro.ini` 加载，可用 `-Dorg.killbill.security.shiroResourcePath` 指定自定义文件。

## ROLE-002 权限（Permission）的命名格式：`group:value`

- **类型**: 角色/权限
- **同义词**: 权限, 权限点, 权限名, 权限命名, permission, permission name, permission string, group:value
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:265-304`, `util/src/test/java/org/killbill/billing/util/security/shiro/realm/TestKillBillJdbcRealm.java:141-150`

权限以字符串形式表达，格式为 **`group:value`**（全小写），例如枚举 `Permission.INVOICE_CAN_CREDIT` 的 `toString()` 是 `invoice:credit`（见 `TestKillBillJdbcRealm.java:179`）。

规则（`DefaultSecurityApi#sanitizePermissions`）：
- 允许 1 段或 2 段，冒号分隔；超过 2 段视为非法，抛 `SECURITY_INVALID_PERMISSIONS`（`TestKillBillJdbcRealm.java:136-138` 用 `account:credit:vvvv` 验证）。
- `group`（仅 1 段，如 `account`）或 `group:*`（如 `account:*`）会被规范化为该组的**全通配** `group:*`。
- 单字符 `*` 是**全局通配**，直接返回 `*` 且不再展开。
- 同一组内若同时出现具体值与通配，通配覆盖具体值（`TestKillBillJdbcRealm.java:148-149`：`account:charge, account:credit, account:*` → 仅保留 `account:*`）。

## ROLE-003 权限枚举常量（Permission）与权限组

- **类型**: 角色/权限
- **同义词**: 权限列表, 内置权限, 权限枚举, permission enum, Permission, 权限常量, permission group
- **模块**: security
- **置信度**: 🟡 inferred
- **溯源**: `util/src/test/java/org/killbill/billing/util/security/shiro/realm/TestKillBillJdbcRealm.java:152-233`, `entitlement/src/test/java/org/killbill/billing/entitlement/EntitlementTestSuiteWithEmbeddedDB.java:172-177`, `util/src/test/java/org/killbill/billing/util/UtilTestSuiteNoDB.java:125-126`

权限常量来自 `org.killbill.billing.security.Permission` 枚举。⚠️ **该枚举源码不在本源码 checkout 中**（包 `org.killbill.billing.security` 由外部依赖 `killbill-api` 提供，仓库内 `api/` 无 `security` 目录），故本卡仅列出**代码中实际引用到**的常量（均可在测试/注解中溯源）：

| 权限组 | 权限常量 | 字符串形式（推断） |
|---|---|---|
| account | `ACCOUNT_CAN_CREATE`, `ACCOUNT_CAN_CHARGE` | `account:create`, `account:charge` |
| entitlement | `ENTITLEMENT_CAN_CREATE`, `ENTITLEMENT_CAN_CHANGE_PLAN`, `ENTITLEMENT_CAN_PAUSE_RESUME`, `ENTITLEMENT_CAN_TRANSFER`, `ENTITLEMENT_CAN_CANCEL` | `entitlement:create` … |
| invoice | `INVOICE_CAN_CREDIT`, `INVOICE_CAN_ITEM_ADJUST`, `INVOICE_CAN_DELETE_CBA` | `invoice:credit`, `invoice:item_adjust`, `invoice:delete_cba` |
| payment | `PAYMENT_CAN_REFUND` | `payment:refund` |
| tag | `TAG_CAN_CREATE_TAG_DEFINITION`, `TAG_CAN_DELETE_TAG_DEFINITION` | `tag:create_tag_definition`, `tag:delete_tag_definition` |

除内置权限外，系统**允许自定义权限**（任意 `group:value`），例如 `invoice:write_off`、`acme:kb_dev`（`TestKillBillJdbcRealm.java:153-160`）。

## ROLE-004 角色聚合权限（`roles_permissions` 表）

- **类型**: 角色/权限
- **同义词**: 角色定义, 角色权限关联, role definition, role permissions, roles_permissions, 角色有哪些权限
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/shiro/dao/DefaultUserDao.java:107-146`, `util/src/main/java/org/killbill/billing/util/security/shiro/dao/RolesPermissionsSqlDao.java:36-52`, `util/src/main/java/org/killbill/billing/util/security/shiro/realm/KillBillJdbcRealm.java:32-56`

角色与权限是多对多关系，持久化在 **`roles_permissions`** 表（列 `role_name`、`permission`、`is_active`）。
- 新增角色定义：`addRoleDefinition(role, permissions, ...)`；若角色已存在抛 `SECURITY_ROLE_ALREADY_EXISTS`。
- 更新角色定义：`updateRoleDefinition(...)` 做差量更新——旧权限置为 `is_active=false`（`unactiveEvent`，审计类型 DELETE），新权限插入。
- 空权限列表表示**清空该角色所有权限**。
- 查询角色定义：`getRoleDefinition(role)`；列出所有角色：`getAvailableRoles()`（聚合为 `Map<roleName, List<permission>>`）。

## ROLE-005 用户聚合角色（`user_roles` 表）

- **类型**: 角色/权限
- **同义词**: 用户角色, 用户绑定角色, user roles, 给用户分配角色, user_roles, 用户权限来源
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/shiro/dao/DefaultUserDao.java:69-103`, `util/src/main/java/org/killbill/billing/util/security/shiro/dao/DefaultUserDao.java:180-204`, `util/src/main/java/org/killbill/billing/util/security/shiro/dao/UserRolesSqlDao.java:30-47`

用户与角色是多对多关系，持久化在 **`user_roles`** 表（列 `username`、`role_name`、`is_active`）。
- 创建用户：`insertUser(username, password, roles, ...)`，密码经加盐哈希后写入 `users` 表，同时为每个角色写 `user_roles`；用户已存在抛 `SECURITY_USER_ALREADY_EXISTS`。
- 更新用户角色：`updateUserRoles(...)` 差量更新——移除的角色 `invalidate`（`is_active=false`），新增的角色插入。
- 作废用户：`invalidateUser(username)` 将用户置为 inactive 并注销当前 `JSESSIONID`。
- 用户角色查询：`getUserRoles(username)`，返回角色名列表。

## ROLE-006 权限检查的执行入口（SecurityApi / Shiro Subject）

- **类型**: 角色/权限
- **同义词**: 权限校验, 权限检查, 鉴权, permission check, authorization check, checkCurrentUserPermissions, 如何判断有没有权限
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:177-204`, `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:128-175`

权限检查由 `DefaultSecurityApi#checkCurrentUserPermissions(permissions, logical, context)` 执行：
- 取当前 Shiro `Subject`，调用 `subject.checkPermission(...)`（单个权限）或 `subject.checkPermissions(...)`（多个）。
- `Logical.AND`：要求**全部**权限；`Logical.OR`：只要有**任一**权限即可（逐个 `isPermitted` 探测，全不满足时才故意触发异常）。
- 权限不足抛 Shiro `AuthorizationException`，并包装为 `SecurityApiException(SECURITY_NOT_ENOUGH_PERMISSIONS)`。
- `getCurrentUserPermissions(context)` 会遍历所有 Shiro Realm，汇总其 `getAuthorizationInfo` 返回的对象权限（`getObjectPermissions`）与字符串权限（`getStringPermissions`）。注意注释指出：**当前权限是跨租户的（cross tenants）**（`SecurityResource.java:98-103`）。

## ROLE-007 注解式权限校验 `@RequiresPermissions`

- **类型**: 角色/权限
- **同义词**: 注解鉴权, 方法级权限, RequiresPermissions, 权限注解, annotation-based authorization
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/PermissionAnnotationHandler.java:36-66`, `util/src/main/java/org/killbill/billing/util/security/PermissionAnnotationMethodInterceptor.java:47-64`, `util/src/test/java/org/killbill/billing/util/security/TestPermissionAnnotationMethodInterceptor.java:51-68`

方法/接口可用 `@RequiresPermissions(Permission.X)` 声明所需权限，由 Shiro AOP 拦截器强制校验：
- `PermissionAnnotationHandler#assertAuthorized` 把注解值转交 `securityApi.checkCurrentUserPermissions(...)`；失败时把 `SecurityApiException` 还原为 Shiro `AuthorizationException`。
- `PermissionAnnotationMethodInterceptor#assertAuthorized` 在异常缺少 cause 时补充“Not authorized to invoke method: …”。
- 特殊开关 `org.killbill.security.skipAuthForPlugins=true` 时，若调用方 `CallContext` 的 `callOrigin=INTERNAL` 且 `userType=ADMIN`，则**跳过**鉴权（供内部插件调用）。默认关闭。
- 效果：匿名用户调用受保护方法抛 `UnauthenticatedException`；已认证但无权限抛 `AuthorizationException`。

## ROLE-008 内置 root 角色（superadmin 通配权限）

- **类型**: 角色/权限
- **同义词**: 超级管理员, 超级管理员角色, root角色, 管理员权限, superadmin, root role, 通配权限, wildcard permission
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `profiles/killbill/src/main/resources/shiro.ini:19-29`, `util/src/test/java/org/killbill/billing/util/security/shiro/realm/TestKillBillJdbcRealm.java:80-83`

默认 `shiro.ini` 内置：
- 用户 `admin`，密码 `password`，角色 `root`（`[users]` 段）。
- 角色 `root = *:*`（`[roles]` 段），即**通配全部权限**。
- 也可在 DB 中显式创建：`addRoleDefinition("root", List.of("*"), ...)` 后 `addUserRoles(username, password, List.of("root"), ...)`。单字符 `*` 表示全局通配（`TestKillBillJdbcRealm.java:141-143, 235-276`）。
- 注意：默认凭据仅用于开发/测试，生产应通过 `-Dorg.killbill.security.shiroResourcePath` 替换。

## ROLE-009 租户级凭据认证 vs 用户级 RBAC

- **类型**: 角色/权限
- **同义词**: 租户认证, api_key, api_secret, tenant authentication, 多租户鉴权, tenant filter, 租户与用户区别
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `profiles/killbill/src/main/java/org/killbill/billing/server/security/TenantFilter.java:66-114`, `profiles/killbill/src/main/java/org/killbill/billing/server/security/KillbillJdbcTenantRealm.java:42-91`

Kill Bill 有两套相互独立的认证平面：
1. **租户认证（多租户）**：`TenantFilter` 从请求头 `X-Killbill-ApiKey` / `X-Killbill-ApiSecret` 取凭据，用 `KillbillJdbcTenantRealm` 校验（SQL：`select api_secret, api_salt from tenants where api_key = ?`）。缺少或错误凭据返回 **401**；若该接口不需要租户信息或为 metrics GET，则放行。校验通过后把 `Tenant` 放入 request 属性 `killbill_tenant`。
2. **用户 RBAC（权限）**：Shiro `Subject` 只用于 RBAC 权限判定（`TenantFilter` 注释：“We use Shiro to verify the api credentials - but the Shiro Subject is only used for RBAC”）。

因此，租户 `api_key/api_secret` 决定“能操作哪个租户”，用户/角色/权限（RBAC）决定“能执行哪些操作”。

## ROLE-010 权限模型的数据库表结构

- **类型**: 角色/权限
- **同义词**: 权限表结构, RBAC表, users表, user_roles表, roles_permissions表, RBAC tables, database schema
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/resources/org/killbill/billing/util/ddl.sql:263-306`

RBAC 由三张表支撑：
- **`users`**：`username`、`password`（加盐哈希后的 Base64）、`password_salt`、`is_active`；`username` 唯一索引。
- **`user_roles`**：`username`、`role_name`、`is_active`；索引 `(username, role_name)`。
- **`roles_permissions`**：`role_name`、`permission`、`is_active`；索引 `(role_name, permission)`。

三张表都带 `created_date`/`created_by`/`updated_date`/`updated_by` 审计列。角色/用户关系用 `is_active=false` 逻辑删除而非物理删除。

## ROLE-011 Security REST API（用户与角色管理端点）

- **类型**: 角色/权限
- **同义词**: 权限接口, 角色管理接口, SecurityResource, security API, 用户角色API, RBAC接口
- **模块**: security (jaxrs)
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/SecurityResource.java:70-267`

`SecurityResource`（Swagger tag：`Security` / “Information about RBAC”）暴露：
| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/security/permissions` | 列出当前用户权限（跨租户） |
| GET | `/security/subject` | 当前用户信息 |
| POST | `/security/users` | 新增用户并绑定角色 |
| PUT | `/security/users/{username}/password` | 修改用户密码 |
| GET | `/security/users/{username}/roles` | 查询用户角色 |
| PUT | `/security/users/{username}/roles` | 更新用户角色 |
| DELETE | `/security/users/{username}` | 作废用户 |
| GET | `/security/roles/{role}` | 查询角色定义 |
| POST | `/security/roles` | 新增角色定义 |
| PUT | `/security/roles` | 更新角色定义 |
| GET | `/security/roles` | 列出所有角色定义 |

## ROLE-012 权限通配符语义（`*` 与 `group:*`）

- **类型**: 角色/权限
- **同义词**: 通配权限, 权限通配符, 星号权限, wildcard permission, 全部权限, group wildcard
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:265-304`, `util/src/test/java/org/killbill/billing/util/security/shiro/realm/TestKillBillJdbcRealm.java:235-321`

- **`*`（全局通配）**：代表所有权限；存储时**不展开**，`getCurrentUserPermissions` 会原样返回 `*`，Shiro 判定时匹配一切。注意：即使数据库后续新增角色，持有 `*` 的用户权限集仍是 `*`。
- **`group:*`（组通配）**：代表某权限组的全部权限，如 `account:*`、`invoice:*`、`catalog:*`、`acme:*`；写入时规范化为 `group:*`。
- **单段组名**（如 `account`、`invoice`、`payment`、`user`）：等价于 `group:*`。
- `skipAuthForPlugins` 与通配无关。

## ROLE-013 多 Realm 的权限聚合（getCurrentUserPermissions）

- **类型**: 角色/权限
- **同义词**: 多Realm, 权限来源聚合, realm aggregation, 权限从哪来, Shiro realm
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:128-175`, `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:320-347`

`DefaultSecurityApi` 通过反射调用每个 `AuthorizingRealm` 的 `getAuthorizationInfo`，把各 Realm 返回的 **对象权限** 与 **字符串权限** 合并去重，作为当前用户的完整权限集合。这意味着同一用户可同时从多个 Realm（JDBC/INI/LDAP/Okta/Auth0）获得权限，最终取并集。

## ROLE-014 外部身份源：LDAP 组 → 权限映射

- **类型**: 角色/权限
- **同义词**: LDAP, LDAP权限, LDAP组映射, JNDI, KillBillJndiLdapRealm, group-to-permission
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/shiro/realm/KillBillJndiLdapRealm.java:152-224`, `util/src/main/java/org/killbill/billing/util/config/definition/SecurityConfig.java:55-70`

启用 LDAP（`-Dkillbill.server.ldap=true`）时，`KillBillJndiLdapRealm`：
- 从 LDAP 组（默认属性 `memberOf`）解析用户所属组；
- 按 `org.killbill.security.ldap.permissionsByGroup` 把**组名映射为权限**。

默认映射（`SecurityConfig.java:66-68`）：
```
admin   = *:*
finance = invoice:*, payment:*
support = entitlement:*, invoice:item_adjust
```
即 LDAP 组 `admin` 拥有全部权限；`finance` 拥有发票与支付组权限；`support` 拥有权益组权限与发票明细调整。

## ROLE-015 外部身份源：Okta 组 → 权限映射

- **类型**: 角色/权限
- **同义词**: Okta, Okta权限, Okta组映射, KillBillOktaRealm, SSO权限
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/shiro/realm/KillBillOktaRealm.java:93-104`, `util/src/main/java/org/killbill/billing/util/security/shiro/realm/KillBillOktaRealm.java:225-234`, `util/src/main/java/org/killbill/billing/util/config/definition/SecurityConfig.java:114-119`

启用 Okta（`-Dkillbill.server.okta=true`）时，`KillBillOktaRealm` 通过 Okta API 认证用户，并拉取其 Okta 组，按 `org.killbill.security.okta.permissionsByGroup` 映射为权限。默认映射与 LDAP 相同（`admin=*:*`、`finance=invoice:*,payment:*`、`support=entitlement:*,invoice:item_adjust`）。

## ROLE-016 外部身份源：Auth0（JWT）

- **类型**: 角色/权限
- **同义词**: Auth0, JWT权限, Auth0 realm, KillBillAuth0Realm, OIDC
- **模块**: security
- **置信度**: 🟡 inferred
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/shiro/realm/KillBillAuth0Realm.java:84-130`, `util/src/main/java/org/killbill/billing/util/config/definition/SecurityConfig.java:123-156`

启用 Auth0（`-Dkillbill.server.auth0=true`）时，`KillBillAuth0Realm` 用 JWT（校验 issuer/audience/签名、允许时钟偏移）认证用户。相关配置键：`org.killbill.security.auth0.url/clientId/clientSecret/apiIdentifier/issuer/audience/usernameClaim` 等。⚠️ 该 Realm 的权限映射细节（组→权限）需以完整实现为准，本卡仅确认其认证与配置存在。

## ROLE-017 Shiro Realm 装配与 RBAC 开关

- **类型**: 角色/权限
- **同义词**: Shiro模块, RBAC开关, realm装配, KillBillShiroModule, rbac enable, 关闭权限
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/glue/KillBillShiroModule.java:55-140`, `util/src/main/java/org/killbill/billing/util/glue/KillBillShiroAopModule.java:47-78`

- RBAC 开关：`KillBillShiroModule.isRBACEnabled()` 读取 `-Dkillbill.server.rbac`（默认 `true`）。
- JDBC Realm 始终注册；LDAP/Okta/Auth0 仅在对应 `killbill.server.*` 属性为 true 时注册（`configureJDBCRealm/configureLDAPRealm/configureOktaRealm/configureAuth0Realm`）。
- Realm 集合来源：优先使用 `shiro.ini` 解析出的 security manager；测试场景回退为 `IniRealm`。
- `KillBillShiroAopModule` 在 RBAC 关闭时**不注册**权限拦截器，即方法级注解鉴权失效。

## ROLE-018 密码哈希与凭据校验

- **类型**: 角色/权限
- **同义词**: 密码哈希, 密码加盐, SHA-512, 凭据校验, password hashing, credentials matcher
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/shiro/KillbillCredentialsMatcher.java:26-41`, `util/src/main/java/org/killbill/billing/util/config/definition/SecurityConfig.java:33-36`, `util/src/main/java/org/killbill/billing/util/security/shiro/dao/DefaultUserDao.java:69-93`

- 算法：**SHA-512**（`Sha512Hash.ALGORITHM_NAME`），Base64 存储（非 hex）。
- 加盐：每用户随机 salt，存于 `users.password_salt`。
- 迭代次数：`org.killbill.security.shiroNbHashIterations`，默认 **200000**。
- 认证 SQL：`select password, password_salt from users where username = ? and is_active = TRUE`。

## ROLE-019 Shiro AOP 权限拦截与注解解析

- **类型**: 角色/权限
- **同义词**: AOP鉴权, 拦截器, 注解解析, ShiroAopModule, 接口注解, method interceptor
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/glue/KillBillShiroAopModule.java:52-78`, `util/src/main/java/org/killbill/billing/util/security/AnnotationHierarchicalResolver.java:52-123`

- `KillBillShiroAopModule` 注册 `PermissionAnnotationMethodInterceptor`，并绑定一个自定义 `AnnotationHierarchicalResolver`，使其能沿**类继承与接口**查找 `@RequiresPermissions`（Shiro 默认不继承方法注解）。
- `KillBillShiroAopModule.bindShiroInterceptorWithHierarchy` 让拦截器匹配任何“在其类层次上带该注解”的方法。

## ROLE-020 权限相关错误码与异常

- **类型**: 角色/权限
- **同义词**: 权限错误, 错误码, SecurityApiException, SECURITY错误, 权限异常, error code
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:201-203`, `util/src/main/java/org/killbill/billing/util/security/shiro/dao/DefaultUserDao.java:62-67`, `util/src/main/java/org/killbill/billing/util/security/shiro/dao/DefaultUserDao.java:86-88`, `util/src/main/java/org/killbill/billing/util/security/shiro/dao/DefaultUserDao.java:111-114`

`org.killbill.billing.ErrorCode` 中与安全相关的错误码（枚举源码位于外部 `killbill-api`，仓库内可见其使用点）：
- `SECURITY_NOT_ENOUGH_PERMISSIONS` — 当前用户缺少所需权限（`DefaultSecurityApi` 捕获 Shiro `AuthorizationException` 后抛出；`DefaultEntitlement` 亦使用）。
- `SECURITY_INVALID_PERMISSIONS` — 权限字符串格式非法（超过 2 段）。
- `SECURITY_INVALID_USER` — 用户不存在。
- `SECURITY_USER_ALREADY_EXISTS` — 用户已存在。
- `SECURITY_ROLE_ALREADY_EXISTS` — 角色定义已存在。

## ROLE-021 业务代码中的显式权限检查（DefaultEntitlement）

- **类型**: 角色/权限
- **同义词**: 显式权限检查, checkForPermissions, 订阅权限, entitlement权限, 取消订阅权限, 变更套餐权限
- **模块**: entitlement / security
- **置信度**: 🟢 confirmed
- **溯源**: `entitlement/src/main/java/org/killbill/billing/entitlement/api/DefaultEntitlement.java:904-919`, `entitlement/src/main/java/org/killbill/billing/entitlement/api/DefaultEntitlement.java:334-480`, `entitlement/src/main/java/org/killbill/billing/entitlement/api/DefaultEntitlement.java:560-759`

订阅对象（`DefaultEntitlement`）不总是由 Guice 注入，因此**不能**完全依赖 `@RequiresPermissions` AOP，而是显式调用 `checkForPermissions(Permission, TenantContext)`：
- 仅当 `securityApi.isSubjectAuthenticated()` 为 true 时才检查（匿名调用由上层 HTTP 认证兜底）。
- 取消订阅需要 `ENTITLEMENT_CAN_CANCEL`；变更套餐需要 `ENTITLEMENT_CAN_CHANGE_PLAN`；不足抛 `EntitlementApiException(SECURITY_NOT_ENOUGH_PERMISSIONS)`。

## ROLE-022 用户角色变更后的授权缓存失效

- **类型**: 角色/权限
- **同义词**: 缓存失效, 权限缓存, shiro缓存, authorization cache, invalidate, 角色变更生效
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:306-318`, `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:216-227`

- `updateUserRoles` 后会调用 `invalidateJDBCAuthorizationCache(username)`：从 `DefaultSecurityManager` 找到 `KillBillJdbcRealm`，用 `SimplePrincipalCollection` 清除该用户的缓存授权信息，使新角色立即生效。
- `invalidateUser` 除置用户 inactive 外，还会 `logout()` 注销当前 `JSESSIONID`。
- 测试强调：只有正确的 Shiro 缓存失效才能让角色变更即时生效（`TestSecurity.java:170-173`）。

## ROLE-023 RBAC 会话超时配置

- **类型**: 角色/权限
- **同义词**: 会话超时, session timeout, 登录超时, RbacConfig, 会话失效
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/config/definition/RbacConfig.java:25-31`

`org.killbill.rbac.globalSessionTimeout`（默认 `1h`）：任意会话在闲置超过该时长后过期。

## ROLE-024 示例/内置角色集合

- **类型**: 角色/权限
- **同义词**: 内置角色, 示例角色, admin, creditor, refunder, entitlement角色, built-in roles, 默认角色
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `profiles/killbill/src/test/resources/org/killbill/billing/server/shiro.ini:21-29`, `util/src/test/java/org/killbill/billing/util/UtilTestSuiteNoDB.java:124-126`, `entitlement/src/test/java/org/killbill/billing/entitlement/EntitlementTestSuiteWithEmbeddedDB.java:172-177`

代码中出现的角色定义（测试/默认配置，用于说明角色如何组合权限）：
- `admin` / `root` = `*:*`（全部权限）。
- `creditor` = `invoice:credit, invoice:item_adjust`（用户 `pierre`）。
- `refunder` = `payment:refund`（用户 `stephane`）。
- `entitlement` = `account:create, entitlement:create, entitlement:change_plan, entitlement:pause_resume, entitlement:transfer, entitlement:cancel`。
- 其它测试角色：`restricted`/`newRestricted`、`writer_off`、`for this user`、`sanity1/2/3`、`admin`(tenant:add/update)、`finance`(invoice:credit) 等，均为**用户自定义角色**。

## ROLE-025 自定义权限与自定义权限组

- **类型**: 角色/权限
- **同义词**: 自定义权限, 扩展权限, custom permission, 自定义角色权限, acme权限, 非内置权限
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/test/java/org/killbill/billing/util/security/shiro/realm/TestKillBillJdbcRealm.java:152-160`, `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:279-295`

除枚举内置权限外，`roles_permissions.permission` 可存任意 `group:value`：
- 内置组的自定义值：`invoice:write_off`（`invoice` 为内置组，`write_off` 为自定义值）。
- 完全自定义组与值：`acme:kb_dev`、`customx:customy`（仅当角色显式包含时才授予）。
- 自定义权限与内置权限使用同一套 `group:value` 校验与通配规则。

## ROLE-026 未认证（401）与权限不足的行为差异

- **类型**: 角色/权限
- **同义词**: 401, 未认证, 403, 权限不足, unauthorized, 登录失败, authentication vs authorization
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `profiles/killbill/src/test/java/org/killbill/billing/jaxrs/TestSecurity.java:46-65`, `profiles/killbill/src/test/java/org/killbill/billing/jaxrs/TestSecurity.java:98-136`, `profiles/killbill/src/main/java/org/killbill/billing/server/security/TenantFilter.java:149-154`

- **未认证/凭据错误**：请求缺少或带错 `X-Killbill-ApiKey`/`X-Killbill-ApiSecret` → 401（`TenantFilter.sendAuthError`）；登出后调用 `/security/permissions` 也返回 401。
- **已认证但权限不足**：抛出 `AuthorizationException`（AOP）或 `SecurityApiException(SECURITY_NOT_ENOUGH_PERMISSIONS)`，接口调用失败（如无 `catalog:config_upload` 时上传 catalog 抛 “Unauthorized”）。
- 测试样例：持有除 `user` 组外所有权限的用户无法新增用户/角色（`testUserPermission`），说明 `user` 组权限用于保护 RBAC 管理接口本身。

## TERM-001 权限（Permission）

- **类型**: 术语
- **同义词**: 权限, 权限点, 操作许可, permission, permission point, privilege
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/api/DefaultSecurityApi.java:177-204`, `util/src/main/java/org/killbill/billing/util/security/shiro/realm/KillBillJdbcRealm.java:32-34`

**权限（Permission）**：对某项具体操作的许可，表示为 `group:value` 字符串（如 `invoice:credit`），由 `org.killbill.billing.security.Permission` 枚举定义内置值，也允许自定义。权限被授予**角色**，而非直接授予用户。

## TERM-002 角色（Role）

- **类型**: 术语
- **同义词**: 角色, role, 角色定义, role definition, 权限集合
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `util/src/main/java/org/killbill/billing/util/security/shiro/dao/DefaultUserDao.java:106-154`, `util/src/main/resources/org/killbill/billing/util/ddl.sql:294-306`

**角色（Role）**：一组权限的命名集合，存于 `roles_permissions` 表。用户通过 `user_roles` 关联角色，从而间接获得权限。角色是权限与用户之间的聚合点。

## TERM-003 RBAC / 访问控制

- **类型**: 术语
- **同义词**: RBAC, 基于角色的访问控制, 访问控制, 授权, role-based access control, authorization, 权限体系
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `jaxrs/src/main/java/org/killbill/billing/jaxrs/resources/SecurityResource.java:70-73`, `util/src/main/java/org/killbill/billing/util/glue/KillBillShiroModule.java:50-74`

**RBAC（Role-Based Access Control）**：Kill Bill 基于 Apache Shiro 实现的“用户→角色→权限”授权体系，默认开启，可用 `-Dkillbill.server.rbac=false` 关闭。

## TERM-004 超级管理员 / root（superadmin）

- **类型**: 术语
- **同义词**: 超级管理员, 超级用户, superadmin, super admin, root, 管理员, admin user, 全能权限
- **模块**: security
- **置信度**: 🟢 confirmed
- **溯源**: `profiles/killbill/src/main/resources/shiro.ini:23-29`, `util/src/test/java/org/killbill/billing/util/security/shiro/realm/TestKillBillJdbcRealm.java:141-143`

**超级管理员**：拥有 `*` 或 `*:*` 通配权限的用户/角色（默认 `admin` 用户 + `root` 角色）。在 Kill Bill 中并非独立的内置“超级管理员”概念，而是通过**通配权限**实现的等效能力；且它是**用户级 RBAC**，与租户级 `api_key/api_secret` 认证相互独立。
