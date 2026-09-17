package com.acme.mall.order;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;

@Entity
@Table(name = "t_order")
public class Order {

    @Id
    private Long id;

    @Column(name = "member_id")
    private Long memberId;

    /** 商品折后净额 */
    @Column(name = "goods_amt")
    private BigDecimal goodsAmt;

    /** 运费 */
    @Column(name = "ship_fee")
    private BigDecimal shipFee;

    /** 实付金额 */
    @Column(name = "paid_amt")
    private BigDecimal paidAmt;

    @Column(name = "state")
    private int state;

    @Column(name = "created_at")
    private Instant createdAt;

    @Column(name = "completed_at")
    private Instant completedAt;

    public OrderState stateOf() {
        return OrderState.values()[state];
    }

    public Long getId() {
        return id;
    }

    public Long getMemberId() {
        return memberId;
    }

    public BigDecimal getGoodsAmt() {
        return goodsAmt;
    }

    public BigDecimal getShipFee() {
        return shipFee;
    }

    public BigDecimal getPaidAmt() {
        return paidAmt;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getCompletedAt() {
        return completedAt;
    }

    public void setState(OrderState next) {
        this.state = next.ordinal();
    }

    public void setCompletedAt(Instant completedAt) {
        this.completedAt = completedAt;
    }
}
