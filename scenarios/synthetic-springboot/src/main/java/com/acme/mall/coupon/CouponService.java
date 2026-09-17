package com.acme.mall.coupon;

import com.acme.mall.common.AmountUtils;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;

@Service
public class CouponService {

    /**
     * 从用户可用券中挑出本单抵扣最多的一张。
     * 一张订单只会应用一张券。
     */
    public BigDecimal bestReduction(BigDecimal netAmount, List<Coupon> coupons, BigDecimal memberRate) {
        BigDecimal best = BigDecimal.ZERO;
        for (Coupon c : coupons) {
            if (!c.isUsableFlag() || c.getExpireAt() == null || c.getExpireAt().isBefore(Instant.now())) {
                continue;
            }
            BigDecimal cut = reductionOf(netAmount, c);
            if (cut.compareTo(best) > 0) {
                best = cut;
            }
        }
        // 券与会员折扣不可叠加：谁更划算就用谁，用券则牺牲会员折扣。
        BigDecimal memberBenefit = netAmount.multiply(BigDecimal.ONE.subtract(memberRate));
        if (memberBenefit.compareTo(best) >= 0) {
            return BigDecimal.ZERO;
        }
        return best;
    }

    /**
     * 计算单张券的抵扣额。
     */
    public BigDecimal reductionOf(BigDecimal netAmount, Coupon c) {
        switch (c.type()) {
            case DISCOUNT:
                return AmountUtils.normalize(netAmount.multiply(BigDecimal.ONE.subtract(c.getRateValue())));
            case FULL_REDUCTION:
                return netAmount.compareTo(c.getThreshold()) >= 0 ? c.getFaceValue() : BigDecimal.ZERO;
            case CASH:
                return c.getFaceValue();
            default:
                return BigDecimal.ZERO;
        }
    }
}
