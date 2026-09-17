package com.acme.mall.coupon;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;

@Entity
@Table(name = "t_coupon")
public class Coupon {

    @Id
    private Long id;

    /** 券类型，对应 CouponType 序号 */
    @Column(name = "coup_type")
    private int coupType;

    /** 满减/现金券的面额 */
    @Column(name = "face_value")
    private BigDecimal faceValue;

    /** 折扣券的比例值，如 0.88 */
    @Column(name = "rate_value")
    private BigDecimal rateValue;

    /** 满减券的使用门槛 */
    @Column(name = "threshold")
    private BigDecimal threshold;

    /** true=可用, false=已冻结 */
    @Column(name = "usable_flag")
    private boolean usableFlag;

    @Column(name = "expire_at")
    private Instant expireAt;

    public CouponType type() {
        return CouponType.values()[coupType];
    }

    public Long getId() {
        return id;
    }

    public BigDecimal getFaceValue() {
        return faceValue;
    }

    public BigDecimal getRateValue() {
        return rateValue;
    }

    public BigDecimal getThreshold() {
        return threshold;
    }

    public boolean isUsableFlag() {
        return usableFlag;
    }

    public Instant getExpireAt() {
        return expireAt;
    }
}
