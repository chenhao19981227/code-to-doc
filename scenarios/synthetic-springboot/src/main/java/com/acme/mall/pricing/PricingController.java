package com.acme.mall.pricing;

import com.acme.mall.coupon.Coupon;
import com.acme.mall.loyalty.MemberLevel;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/api/pricing")
public class PricingController {

    private final PriceCalculator priceCalculator;

    public PricingController(PriceCalculator priceCalculator) {
        this.priceCalculator = priceCalculator;
    }

    @PostMapping("/quote")
    public Quote quote(@RequestBody QuoteRequest req) {
        return priceCalculator.quote(req.getGross(), req.getLevel(), req.isPromoItem(),
                req.getCoupons(), req.getRegionCode());
    }

    /** 试算入参 */
    public static class QuoteRequest {
        private BigDecimal gross;
        private MemberLevel level;
        private boolean promoItem;
        private List<Coupon> coupons;
        private String regionCode;

        public BigDecimal getGross() {
            return gross;
        }

        public MemberLevel getLevel() {
            return level;
        }

        public boolean isPromoItem() {
            return promoItem;
        }

        public List<Coupon> getCoupons() {
            return coupons;
        }

        public String getRegionCode() {
            return regionCode;
        }
    }
}
