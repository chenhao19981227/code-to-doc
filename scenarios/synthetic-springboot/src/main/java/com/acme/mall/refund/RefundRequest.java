package com.acme.mall.refund;

import java.math.BigDecimal;
import java.util.List;

/**
 * 退款申请入参。
 */
public class RefundRequest {

    private Long orderId;

    /** 申请退款的商品行；为空表示整单退款 */
    private List<Long> itemIds;

    /** 部分退款时对应商品的净额 */
    private BigDecimal goodsPortion;

    private String reason;

    public Long getOrderId() {
        return orderId;
    }

    public List<Long> getItemIds() {
        return itemIds;
    }

    public BigDecimal getGoodsPortion() {
        return goodsPortion;
    }

    public String getReason() {
        return reason;
    }
}
