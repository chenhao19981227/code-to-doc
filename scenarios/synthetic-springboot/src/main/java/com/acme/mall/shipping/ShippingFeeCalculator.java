package com.acme.mall.shipping;

import com.acme.mall.common.AmountUtils;
import com.acme.mall.loyalty.MemberLevel;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

@Component
public class ShippingFeeCalculator {

    private static final BigDecimal BASE_FEE = new BigDecimal("12.00");
    private static final BigDecimal FREE_LINE = new BigDecimal("99.00");
    private static final BigDecimal REMOTE_SURCHARGE = new BigDecimal("15.00");

    /** 偏远地区编码 */
    private static final List<String> REMOTE_REGIONS = Arrays.asList("XZ", "XJ", "NM", "QH");

    /**
     * 计算本单运费。
     *
     * @param netAmount  商品折后净额
     * @param lvl        用户分层
     * @param regionCode 收货地区编码
     */
    public BigDecimal fee(BigDecimal netAmount, MemberLevel lvl, String regionCode) {
        BigDecimal fee = BASE_FEE;
        if (lvl == MemberLevel.PLATINUM || netAmount.compareTo(FREE_LINE) >= 0) {
            fee = BigDecimal.ZERO;
        }
        if (REMOTE_REGIONS.contains(regionCode)) {
            fee = fee.add(REMOTE_SURCHARGE);
        }
        return AmountUtils.normalize(fee);
    }
}
