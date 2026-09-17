# 模块：loyalty

## 模块概述

`loyalty` 模块负责会员与用户分层，含枚举 `MemberLevel`、实体 `Member` 与仓储 `MemberRepository`。它定义了会员等级取值、会员基本属性，以及"活跃会员/运营触达人群"的取数口径。

**本模块能力**：会员等级建模、会员属性（分层/状态/累计消费/最近下单）、活跃会员筛选口径。

---

## TERM-006 会员等级 / 用户分层

- **类型**: 术语
- **同义词**: 会员等级, 用户分层, 会员分层, 会员级别, 等级, 会员, VIP等级, member level, vip level, MemberLevel, vipLvl
- **模块**: loyalty
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/loyalty/MemberLevel.java:3-10`, `src/main/java/com/acme/mall/loyalty/Member.java:17-19`

**说明**：用户分层枚举 `MemberLevel`，常量顺序 `NORMAL`、`SILVER`、`GOLD`、`PLATINUM`。代码注释「顺序与 t_member.vip_lvl 的取值一一对应」；`Member.vipLvl` 字段注释为「用户分层值，对应 MemberLevel 的序号」，`Member.level()` 用 `MemberLevel.values()[vipLvl]` 还原。

## TERM-007 会员等级中文称谓

- **类型**: 术语
- **同义词**: 普通会员, 银卡会员, 金卡会员, 白金会员, 普通, 银卡, 金卡, 白金, normal, silver, gold, platinum
- **模块**: loyalty
- **置信度**: 🟡 inferred
- **溯源**: `src/main/java/com/acme/mall/loyalty/MemberLevel.java:6-10`

**说明（推断）**：代码仅给出英文常量 `NORMAL/SILVER/GOLD/PLATINUM`，未出现中文等级名。按命名惯例推断对应「普通 / 银卡 / 金卡 / 白金」。
**缺失证据**：源代码与注释中无官方的中文称谓映射。

## ENT-002 会员 Member

- **类型**: 业务实体
- **同义词**: 会员, 用户, 客户, 会员信息, member, user, t_member
- **模块**: loyalty
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/loyalty/Member.java:10-29`

**说明**：数据库实体，表名 `t_member`。字段：`vipLvl`（分层序号）、`status`（1=启用，0=注销，语义来自字段注释）、`lastOrderAt`（最近下单时间）、`totalSpent`（累计消费）。
**约束/关系**：无 ORM 关联；`memberId` 在 Order 中逻辑引用会员。
**注意**：源码中未发现写入 `status` / `lastOrderAt` / `totalSpent` 的逻辑（见 BR-011）。

## BR-010 活跃会员口径：启用且 365 天内有下单

- **类型**: 业务规则
- **同义词**: 活跃会员, 活跃用户, 运营触达人群, 触达人群, 365天, 一年内有下单, active members, findActives, 活跃口径
- **模块**: loyalty
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/loyalty/MemberRepository.java:12-17`

**规则**：`findActives` 选取 `status = 1` 且 `last_order_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)` 的会员。注释「拉取当前需要纳入运营触达的人群。口径写在 SQL 内，勿改」。
**例外**：口径以原生 SQL 硬编码，任何变更需改 SQL。

## BR-011 会员累计消费与最近下单时间的更新规则缺失

- **类型**: 业务规则
- **同义词**: 累计消费更新, totalSpent, lastOrderAt, 最近下单时间, 会员字段更新
- **模块**: loyalty
- **置信度**: 🔴 gap
- **溯源**: `src/main/java/com/acme/mall/loyalty/Member.java:25-29`, `src/main/java/com/acme/mall/order/OrderService.java:20-34`

**缺失点**：`Member.totalSpent` 与 `Member.lastOrderAt` 仅声明与读取，代码中未发现任何写入点（OrderService 的 pay/ship/confirm 均不更新会员）。这两个字段由谁、在何时更新无法确定，需人工确认（可能由本代码库之外的结算/会员系统负责）。
