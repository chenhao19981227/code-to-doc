package com.acme.mall.refund;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/refunds")
public class RefundController {

    private final RefundService refundService;

    public RefundController(RefundService refundService) {
        this.refundService = refundService;
    }

    /** 客服可代客发起退款申请 */
    @PostMapping
    @PreAuthorize("hasAnyRole('CS', 'CS_LEAD')")
    public Long create(@RequestBody RefundRequest req) {
        refundService.create(null, req.getItemIds() == null, req.getGoodsPortion());
        return req.getOrderId();
    }

    /** 退款须经客服主管审批后方可执行 */
    @PostMapping("/{id}/approve")
    @PreAuthorize("hasRole('CS_LEAD')")
    public void approve(@PathVariable("id") Long id) {
        // 审批后由结算系统出款
    }
}
