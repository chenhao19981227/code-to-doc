package com.acme.mall.pricing;

import com.acme.mall.common.AmountUtils;
import com.acme.mall.coupon.Coupon;
import com.acme.mall.coupon.CouponService;
import com.acme.mall.loyalty.MemberLevel;
import com.acme.mall.shipping.ShippingFeeCalculator;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.List;

@Service
public class PriceCalculator {

    private final DiscountService discountService;
    private final CouponService couponService;
    private final ShippingFeeCalculator shippingFeeCalculator;

    public PriceCalculator(DiscountService discountService,
                           CouponService couponService,
                           ShippingFeeCalculator shippingFeeCalculator) {
        this.discountService = discountService;
        this.couponService = couponService;
        this.shippingFeeCalculator = shippingFeeCalculator;
    }

    /**
     * 完整试算：先算商品净额，再决定优惠，最后叠加运费。
     */
    public Quote quote(BigDecimal gross, MemberLevel lvl, boolean promoItem,
                       List<Coupon> coupons, String regionCode) {
        BigDecimal rate = promoItem ? BigDecimal.ONE : discountService.rateOf(lvl);
        BigDecimal goodsNet = discountService.apply(gross, lvl, promoItem);
        BigDecimal couponCut = couponService.bestReduction(goodsNet, coupons, rate);
        BigDecimal afterCoupon = AmountUtils.normalize(goodsNet.subtract(couponCut));
        BigDecimal shipFee = shippingFeeCalculator.fee(afterCoupon, lvl, regionCode);
        BigDecimal payableAmt = AmountUtils.chargeable(afterCoupon.add(shipFee));
        return new Quote(goodsNet, couponCut, shipFee, payableAmt);
    }
}
