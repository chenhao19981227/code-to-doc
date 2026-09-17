package com.acme.mall.pricing;

import java.math.BigDecimal;

/**
 * 结算试算结果。
 */
public class Quote {

    private final BigDecimal goodsNet;
    private final BigDecimal couponCut;
    private final BigDecimal shipFee;
    private final BigDecimal payableAmt;

    public Quote(BigDecimal goodsNet, BigDecimal couponCut, BigDecimal shipFee, BigDecimal payableAmt) {
        this.goodsNet = goodsNet;
        this.couponCut = couponCut;
        this.shipFee = shipFee;
        this.payableAmt = payableAmt;
    }

    public BigDecimal getGoodsNet() {
        return goodsNet;
    }

    public BigDecimal getCouponCut() {
        return couponCut;
    }

    public BigDecimal getShipFee() {
        return shipFee;
    }

    public BigDecimal getPayableAmt() {
        return payableAmt;
    }
}
