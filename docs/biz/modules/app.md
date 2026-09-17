# 模块：app

## 模块概述

`app` 模块为应用入口，仅含 `MallApplication`（`com.acme.mall`，`src/main/java/com/acme/mall/MallApplication.java`）。它不承载业务逻辑，但通过 `@EnableGlobalMethodSecurity(prePostEnabled = true)` 决定整个系统的注解式鉴权是否生效，因此与角色/权限域相关。

**本模块能力**：方法级安全启用（@PreAuthorize 生效）。

---

## ROLE-001 方法级安全总开关（@PreAuthorize 生效前提）

- **类型**: 角色/权限
- **同义词**: 方法级权限, 方法安全, method security, prePostEnabled, @EnableGlobalMethodSecurity, 注解鉴权, 启用方法安全
- **模块**: app
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/MallApplication.java:7-8`

**说明**：应用以 `@SpringBootApplication` 启动，并通过 `@EnableGlobalMethodSecurity(prePostEnabled = true)` 开启方法级安全。因此本系统中出现的 `@PreAuthorize` 注解在方法调用时生效，是退款等接口鉴权的技术前提。
