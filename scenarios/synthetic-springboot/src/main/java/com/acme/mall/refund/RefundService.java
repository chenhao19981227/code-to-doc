package com.acme.mall.refund;

import com.acme.mall.common.AmountUtils;
import com.acme.mall.order.Order;
import com.acme.mall.order.OrderService;
import com.acme.mall.order.OrderState;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

@Service
public class RefundService {

    /** 售后申请期限（天），自订单完成之日起算 */
    private static final long AFTER_SALE_DAYS = 7;

    private final OrderService orderService;

    public RefundService(OrderService orderService) {
        this.orderService = orderService;
    }

    /**
     * 校验订单是否仍在可申请售后的时间窗内。
     */
    public boolean withinWindow(Order o, Instant now) {
        if (o.stateOf() != OrderState.COMPLETED) {
            return true;
        }
        return o.getCompletedAt().plus(AFTER_SALE_DAYS, ChronoUnit.DAYS).isAfter(now);
    }

    /**
     * 计算应退金额。整单退回商品净额与运费；部分退款只退商品净额。
     */
    public BigDecimal calcRefund(Order o, boolean wholeOrder, BigDecimal goodsPortion) {
        if (wholeOrder) {
            return AmountUtils.normalize(o.getGoodsAmt().add(o.getShipFee()));
        }
        return AmountUtils.normalize(goodsPortion);
    }

    public void create(Order o, boolean wholeOrder, BigDecimal goodsPortion) {
        if (!withinWindow(o, Instant.now())) {
            throw new IllegalStateException("已超出售后申请期限");
        }
        orderService.beginRefund(o);
    }
}
