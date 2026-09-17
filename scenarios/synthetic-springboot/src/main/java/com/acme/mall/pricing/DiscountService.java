package com.acme.mall.pricing;

import com.acme.mall.common.AmountUtils;
import com.acme.mall.loyalty.MemberLevel;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;

@Service
public class DiscountService {

    private static final BigDecimal NORMAL_RATE = new BigDecimal("1.00");
    private static final BigDecimal SILVER_RATE = new BigDecimal("0.95");
    private static final BigDecimal GOLD_RATE = new BigDecimal("0.90");
    private static final BigDecimal PLATINUM_RATE = new BigDecimal("0.85");

    /**
     * 依据用户分层返回结算系数。
     */
    public BigDecimal rateOf(MemberLevel lvl) {
        switch (lvl) {
            case PLATINUM:
                return PLATINUM_RATE;
            case GOLD:
                return GOLD_RATE;
            case SILVER:
                return SILVER_RATE;
            default:
                return NORMAL_RATE;
        }
    }

    /**
     * 计算折后金额。活动商品按原价结算，不适用分层系数。
     */
    public BigDecimal apply(BigDecimal gross, MemberLevel lvl, boolean promoItem) {
        if (promoItem) {
            return AmountUtils.normalize(gross);
        }
        return AmountUtils.normalize(gross.multiply(rateOf(lvl)));
    }
}
