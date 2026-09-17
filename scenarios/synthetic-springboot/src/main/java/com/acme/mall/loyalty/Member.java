package com.acme.mall.loyalty;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import java.math.BigDecimal;
import java.time.Instant;

@Entity
@Table(name = "t_member")
public class Member {

    @Id
    private Long id;

    /** 用户分层值，对应 MemberLevel 的序号 */
    @Column(name = "vip_lvl")
    private int vipLvl;

    /** 1=启用, 0=注销 */
    @Column(name = "status")
    private int status;

    @Column(name = "last_order_at")
    private Instant lastOrderAt;

    @Column(name = "total_spent")
    private BigDecimal totalSpent;

    public MemberLevel level() {
        return MemberLevel.values()[vipLvl];
    }

    public Long getId() {
        return id;
    }

    public int getVipLvl() {
        return vipLvl;
    }

    public int getStatus() {
        return status;
    }

    public Instant getLastOrderAt() {
        return lastOrderAt;
    }

    public BigDecimal getTotalSpent() {
        return totalSpent;
    }
}
