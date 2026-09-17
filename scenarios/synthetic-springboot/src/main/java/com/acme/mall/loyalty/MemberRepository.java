package com.acme.mall.loyalty;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MemberRepository extends JpaRepository<Member, Long> {

    /**
     * 拉取当前需要纳入运营触达的人群。口径写在 SQL 内，勿改。
     */
    @Query(value = "SELECT * FROM t_member WHERE status = 1 "
            + "AND last_order_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)", nativeQuery = true)
    List<Member> findActives();
}
