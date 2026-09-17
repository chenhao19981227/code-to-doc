---
name: biz-doc-scan
description: 机械式盘点目标代码根目录，输出模块/类/枚举/公开方法/权限注解/数据库实体/HTTP端点/状态型枚举的结构化清单（JSON+Markdown）。不做任何业务语义解释。不直接面向用户，供 biz-doc command 的 subAgent 调用。
---

# Biz Doc Scan - 代码骨架机械盘点 Skill

本 skill 只做一件事：**对目标代码根目录做机械式结构盘点，产出可被下游 skill 稳定消费的清单文件。** 它不理解业务、不生成知识卡、不下业务结论。

## 输入

调用方（subAgent）会提供：
- `target_root`：待盘点的代码根目录（如 `<代码根>`）
- `workdir`：工作目录（= 项目根 `code-to-doc`）
- `work_dir`：工作输出目录，默认 `.bizdoc/`（相对于 `workdir`）

## 执行步骤

### 1. 确认目标与语言

1. 使用 Bash 校验 `target_root` 存在（`Test-Path -LiteralPath`）。不存在则报错停止。
2. 识别主要语言与构建文件（`pom.xml` / `build.gradle` / `package.json` / `pyproject.toml` 等）。本 skill 以 Java/Spring 为首要支持目标，其他语言按相同字段结构尽力盘点，无法确认的字段填 `null` 并记录原因。

### 2. 盘点模块（modules）

以构建文件的 `<module>` 及一级源码包目录为准，列出模块清单。每个模块记录：
- `name`：模块名（如 `pricing`）
- `path`：模块相对路径
- `source_files`：源码文件数
- `language`：主要语言

### 3. 盘点类与枚举（classes / enums）

用 Glob 收集 `**/*.java`（及目标语言源文件），对每个类型记录：
- `name`、`fqn`、`module`、`file`（相对 `target_root` 的路径）、`start_line`、`end_line`
- `kind`：`class` / `interface` / `enum` / `record` / `annotation`
- `stereotype`：从类级注解机械识别（`@Service` / `@Repository` / `@Controller` / `@RestController` / `@Entity` / `@Component` …），无则 `null`
- `annotations`：类级注解原始列表

**枚举额外记录** `constants`（枚举常量名列表）。若常量集合呈现顺序/阶段特征（如 `PENDING/PAID/SHIPPED/CANCELLED`、`CREATED→ACTIVE→CLOSED`），标记 `state_like: true`，否则 `false`。

### 4. 盘点公开方法（public_methods）

对每个类，机械提取 `public` 方法：
- `class`、`name`、`signature`、`returns`、`params`（name/type）、`annotations`
- `file`、`start_line`、`end_line`

只做语法层提取（可用 AST 工具或 Grep 定位后 Read 确认），**不推断方法业务含义**。

### 5. 盘点权限/认证注解（permission_annotations）

用 Grep 机械搜索并逐条定位 `file:line`：
- `@Secured`、`@PreAuthorize`、`@PostAuthorize`、`@RolesAllowed`、`@PermitAll`、`@DenyAll`
- Spring Security 配置类中的 `requestMatchers(...).hasRole/hasAuthority/authenticated/permitAll`
- 常见自定义注解（`@RequiresPermissions`、`@RequiresRoles`、`@SaCheckPermission` 等）

记录：`annotation`、`value`（原始表达式）、`target`（类或方法名）、`file`、`line`。

### 6. 盘点数据库实体（db_entities）

机械提取 JPA 实体/ORM 模型：
- `entity_class`、`table_name`（`@Table(name=…)`，缺省按类名 snake_case 推断并标注 `table_name_source`）
- `file`、`start_line`、`end_line`
- `fields[]`：`field_name`、`java_type`、`column_name`、`annotations`、`nullable`
- `relations[]`：`@OneToMany` / `@ManyToOne` / `@OneToOne` / `@ManyToMany` 及其 `@JoinColumn`/`@JoinTable`

### 7. 盘点 HTTP 端点（http_endpoints）

机械提取 Controller 路由：
- `http_method`、`path`（类级前缀 + 方法级路径拼接）、`handler`（`Class.method`）
- `file`、`line`、`auth_annotations`（该端点直接挂载的权限注解）

### 8. 汇总状态型枚举（state_like_enums）

把第 3 步中 `state_like: true` 的枚举汇总为独立数组，便于下游生成状态机卡。仅记录常量与 `file:line`，**不推断流转关系**。

### 9. 写出产物

1. 创建 `work_dir`（默认 `.bizdoc/`，不存在则 `mkdir`）。
2. 写 `.bizdoc/inventory.json`（结构见「输出格式」）。
3. 写 `.bizdoc/inventory.md`（人类可读摘要：模块表、各类计数、端点表、状态型枚举列表）。
4. 写 `.bizdoc/scan-meta.json`：`target_root`、`scanned_at`、`stats`、`unsupported[]`（无法盘点的部分及原因）。

## 输出格式

### `.bizdoc/inventory.json`

```json
{
  "root": "<代码根>",
  "scanned_at": "2026-01-01T00:00:00Z",
  "languages": ["java"],
  "modules": [
    { "name": "pricing", "path": "src/main/java/com/example/pricing", "source_files": 6, "language": "java" }
  ],
  "classes": [
    {
      "name": "DiscountService",
      "fqn": "com.example.pricing.DiscountService",
      "module": "pricing",
      "file": "src/main/java/com/example/pricing/DiscountService.java",
      "start_line": 1,
      "end_line": 58,
      "kind": "class",
      "stereotype": "Service",
      "annotations": ["@Service"]
    }
  ],
  "enums": [
    {
      "name": "MemberLevel",
      "fqn": "com.example.pricing.MemberLevel",
      "module": "pricing",
      "file": "src/main/java/com/example/pricing/MemberLevel.java",
      "start_line": 1,
      "end_line": 12,
      "constants": ["BRONZE", "SILVER", "GOLD", "PLATINUM"],
      "state_like": false
    }
  ],
  "public_methods": [
    {
      "class": "com.example.pricing.DiscountService",
      "name": "calculateDiscount",
      "signature": "public BigDecimal calculateDiscount(MemberLevel level, BigDecimal amount)",
      "returns": "BigDecimal",
      "params": [{ "name": "level", "type": "MemberLevel" }],
      "annotations": [],
      "file": "src/main/java/com/example/pricing/DiscountService.java",
      "start_line": 42,
      "end_line": 58
    }
  ],
  "permission_annotations": [
    {
      "annotation": "@PreAuthorize",
      "value": "hasRole('ADMIN')",
      "target": "OwnerController.delete",
      "file": "src/main/java/com/example/owner/OwnerController.java",
      "line": 142
    }
  ],
  "db_entities": [
    {
      "entity_class": "Owner",
      "table_name": "owners",
      "table_name_source": "@Table",
      "file": "src/main/java/com/example/owner/Owner.java",
      "start_line": 1,
      "end_line": 90,
      "fields": [
        { "field_name": "id", "java_type": "Integer", "column_name": "id", "annotations": ["@Id", "@GeneratedValue"], "nullable": false }
      ],
      "relations": [
        { "type": "OneToMany", "target": "Pet", "mappedBy": "owner" }
      ]
    }
  ],
  "http_endpoints": [
    {
      "http_method": "GET",
      "path": "/owners/{ownerId}",
      "handler": "OwnerController.showOwner",
      "file": "src/main/java/com/example/owner/OwnerController.java",
      "line": 66,
      "auth_annotations": []
    }
  ],
  "state_like_enums": [
    {
      "name": "OrderStatus",
      "fqn": "com.example.order.OrderStatus",
      "file": "src/main/java/com/example/order/OrderStatus.java",
      "constants": ["PENDING", "PAID", "SHIPPED", "CANCELLED", "REFUNDED"]
    }
  ],
  "stats": {
    "modules": 1,
    "classes": 12,
    "enums": 3,
    "public_methods": 40,
    "endpoints": 8,
    "db_entities": 4,
    "permission_annotations": 2,
    "state_like_enums": 1
  },
  "unsupported": []
}
```

### `.bizdoc/inventory.md`

按模块分节的摘要表格，至少包含：模块 → 类数 / 枚举数 / 端点数 / 实体数；全量端点表；状态型枚举列表。

## 约束

- **只做机械盘点**：不撰写业务描述，不推断业务规则、流程、角色职责。任何"业务含义"都留给 `biz-doc-extract`。
- **不做任何写操作**：不修改 `target_root` 下任何源码文件，只读取。
- **文件路径一律相对 `target_root`**，行号以源码实际行号为准（`file_name:line`）。
- **行号必须来自真实读取**：不能凭搜索命中行号臆造范围，范围需 Read 确认。
- **无法确认的字段填 `null`**，并在 `unsupported[]` 记录原因，不得编造。
- 所有输出仅写入 `work_dir`（默认 `.bizdoc/`），不写到其他位置。
