# 模块：shipping

## 模块概述

`shipping` 模块负责运费计算，仅含 `ShippingFeeCalculator`。它定义基础运费、包邮门槛、白金会员免邮与偏远地区附加费，被 pricing 试算调用。

**本模块能力**：基础运费、免运费条件、偏远地区加收。

---

## TERM-014 运费

- **类型**: 术语
- **同义词**: 运费, 邮费, 物流费, 快递费, shipping fee, shipFee, freight, 配送费
- **模块**: shipping
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:11-19`, `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:28-37`

**说明**：由 `ShippingFeeCalculator.fee` 计算，基础运费 `BASE_FEE`=12.00 元，包邮线 `FREE_LINE`=99.00 元，偏远加收 `REMOTE_SURCHARGE`=15.00 元。

## TERM-015 偏远地区

- **类型**: 术语
- **同义词**: 偏远地区, 偏远附加费, 偏远加收, 偏远运费, remote region, surcharge, 地区编码, XZ, XJ, NM, QH
- **模块**: shipping
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:16-19`, `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:33-35`

**说明**：`REMOTE_REGIONS = ["XZ", "XJ", "NM", "QH"]`（西藏/新疆/内蒙古/青海的地区编码），命中即加收 15.00 元。

## BR-026 运费基础与免运费规则

- **类型**: 业务规则
- **同义词**: 运费规则, 包邮, 免运费, 满99包邮, 白金包邮, free shipping, BASE_FEE, FREE_LINE, 基础运费
- **模块**: shipping
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:14-15`, `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:28-32`

**规则**：基础运费 `BASE_FEE`=12.00 元；若会员为 `PLATINUM` 或商品净额 `netAmount >= FREE_LINE`(99.00)，则运费置为 0。
**例外**：免运费只免基础运费，偏远加收仍会另加（见 BR-027）。

## BR-027 偏远地区加收 15 元

- **类型**: 业务规则
- **同义词**: 偏远加收, 偏远附加费, 偏远运费, remote surcharge, 15元, 加收运费
- **模块**: shipping
- **置信度**: 🟢 confirmed
- **溯源**: `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:16-19`, `src/main/java/com/acme/mall/shipping/ShippingFeeCalculator.java:33-35`

**规则**：若 `regionCode` 属于 `{XZ, XJ, NM, QH}`，在（可能已置 0 的）运费基础上再加 `REMOTE_SURCHARGE`=15.00 元。
