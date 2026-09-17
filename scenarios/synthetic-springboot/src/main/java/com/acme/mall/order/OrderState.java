package com.acme.mall.order;

/**
 * 订单状态。序号持久化于 t_order.state。
 */
public enum OrderState {
    PENDING,
    PAID,
    SHIPPED,
    COMPLETED,
    REFUNDING,
    REFUNDED,
    CANCELLED
}
