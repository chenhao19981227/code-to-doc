# 模块：common

## 模块概述

`common` 模块提供跨域共享的金额处理能力，仅含 `AmountUtils`（`src/main/java/com/acme/mall/common/AmountUtils.java`）。它定义了系统的金额精度契约与最低可收取金额下限，被 pricing、refund、shipping 等模块复用。

**本模块能力**：金额归一化（两位小数四舍五入）、最小可收取金额下限。

---

## TERM-001 金额归一化

- **类型**: 术语
- **同义词**: 金额归一化, 金额处理, 金额规整, 保留两位小数, 金额精度, amount normalization, normalize, AmountUtils, 金额工具
- **模块**: common
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/common/AmountUtils.java:6-8`, `src/main/java/com/acme/mall/common/AmountUtils.java:20-25`

**说明**：AmountUtils 为金额处理工具，注释明确「所有对外可见的金额都必须经过此处归一化」。内部计算值经归一化后作为对外金额。

## BR-001 金额归一化：四舍五入保留两位小数

- **类型**: 业务规则
- **同义词**: 保留两位小数, 两位小数, 四舍五入, 金额取整, 金额精度, HALF_UP, rounding, 金额归一
- **模块**: common
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/common/AmountUtils.java:20-25`

**规则**：`normalize(raw)` 使用 `raw.setScale(2, RoundingMode.HALF_UP)` 将金额保留两位小数、四舍五入。
**例外**：当 `raw` 为 `null` 时返回 `BigDecimal.ZERO.setScale(2, HALF_UP)`（即 0.00）。

## BR-002 最低可收取金额 0.01 元

- **类型**: 业务规则
- **同义词**: 最低收款, 最小金额, 最低金额, 0.01, 不接受零元订单, 不接受负价订单, minimum charge, MIN_CHARGE, chargeable
- **模块**: common
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/common/AmountUtils.java:11-12`, `src/main/java/com/acme/mall/common/AmountUtils.java:30-36`

**规则**：`chargeable(amount)` 先归一化金额；若结果小于 `MIN_CHARGE`（0.01 元），则返回 0.01。系统不接受零元或负价订单。
**例外**：该下限作用于最终可收取金额（试算中的应付金额 payableAmt），见 pricing 模块。
