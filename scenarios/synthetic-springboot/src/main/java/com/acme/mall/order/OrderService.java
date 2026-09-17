package com.acme.mall.order;

import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.EnumSet;
import java.util.Set;

@Service
public class OrderService {

    /** 待支付订单的保留时长（分钟） */
    private static final long PAY_TIMEOUT_MINUTES = 30;

    /** 允许进入退款流程的状态 */
    private static final Set<OrderState> REFUNDABLE =
            EnumSet.of(OrderState.SHIPPED, OrderState.COMPLETED);

    public void pay(Order o) {
        guard(o, OrderState.PENDING);
        o.setState(OrderState.PAID);
    }

    public void ship(Order o) {
        guard(o, OrderState.PAID);
        o.setState(OrderState.SHIPPED);
    }

    public void confirm(Order o) {
        guard(o, OrderState.SHIPPED);
        o.setState(OrderState.COMPLETED);
        o.setCompletedAt(Instant.now());
    }

    /**
     * 取消订单。已支付订单一律不允许直接取消。
     */
    public void cancel(Order o) {
        if (o.stateOf() != OrderState.PENDING) {
            throw new IllegalStateException("已支付订单不可直接取消，请走退款流程");
        }
        o.setState(OrderState.CANCELLED);
    }

    public void beginRefund(Order o) {
        if (!REFUNDABLE.contains(o.stateOf())) {
            throw new IllegalStateException("当前状态不支持退款");
        }
        o.setState(OrderState.REFUNDING);
    }

    public void finishRefund(Order o) {
        guard(o, OrderState.REFUNDING);
        o.setState(OrderState.REFUNDED);
    }

    /**
     * 判断待支付订单是否已超时。
     */
    public boolean expired(Order o, Instant now) {
        return o.stateOf() == OrderState.PENDING
                && o.getCreatedAt().plus(PAY_TIMEOUT_MINUTES, ChronoUnit.MINUTES).isBefore(now);
    }

    private void guard(Order o, OrderState expected) {
        if (o.stateOf() != expected) {
            throw new IllegalStateException("非法状态流转: " + o.stateOf() + " -> " + expected);
        }
    }
}
