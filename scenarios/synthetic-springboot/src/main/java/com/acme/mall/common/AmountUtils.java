package com.acme.mall.common;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * 金额处理工具。所有对外可见的金额都必须经过此处归一化。
 */
public final class AmountUtils {

    /** 系统可收取的最小金额（元） */
    private static final BigDecimal MIN_CHARGE = new BigDecimal("0.01");

    private AmountUtils() {
    }

    /**
     * 将内部计算值归一化为对外金额。
     */
    public static BigDecimal normalize(BigDecimal raw) {
        if (raw == null) {
            return BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP);
        }
        return raw.setScale(2, RoundingMode.HALF_UP);
    }

    /**
     * 计算最终可收取金额。系统不接受零元或负价订单。
     */
    public static BigDecimal chargeable(BigDecimal amount) {
        BigDecimal n = normalize(amount);
        if (n.compareTo(MIN_CHARGE) < 0) {
            return MIN_CHARGE;
        }
        return n;
    }
}
