# L4 端到端问答报告 (qa_eval)

- 生成时间: 2026-09-16T16:12:42.447252+00:00
- 知识库: `D:\openCodeProject\code-to-doc\docs\biz-kb2`
- 黄金集: `D:\openCodeProject\code-to-doc\benchmark\golden-set\killbill-invoice.yaml`
- top-k: 12
- 索引片段数: 696
- 题目数: 40
- LLM: provider=deepseek model=deepseek-chat base_url=https://api.deepseek.com

## 指标

- **answer_accuracy: 67.7%**
- **faithfulness: 97.5%**
- **retrieval_hit_rate: 93.5%**
- **refusal_correctness: 100.0%**
- answer_score_weighted: 80.6%

## 逐题结果

| 题号 | 类型 | 判定 | 检索命中 | 忠实 | 问题 |
|---|---|---|---|---|---|
| KB-Q001 | positive | partial | 是 | 是 | 订购服务的试用期结束后会自动开始扣费吗？ |
| KB-Q002 | positive | correct | 是 | 是 | 计划（Plan）的阶段（Phase）可以配置成哪几种类型？ |
| KB-Q003 | positive | correct | 是 | 是 | Kill Bill 里的产品品类（Product Category）有哪些？ |
| KB-Q004 | positive | correct | 是 | 是 | 同一个订阅包（Bundle）里可以有多个基础（BASE）订阅吗？ |
| KB-Q005 | positive | correct | 是 | 是 | Kill Bill 的计费对齐（Billing Alignment）规则支持哪几种方式？ |
| KB-Q006 | positive | correct | 是 | 是 | 为什么新订阅的第一张发票有时金额会被按比例折算（proration）？ |
| KB-Q007 | positive | partial | 否 | 是 | 一次性固定费用（FIXED 项目）会被按比例折算吗？ |
| KB-Q008 | positive | partial | 是 | 是 | 用户升级计划时，系统怎么算旧计划没用完的那部分费用？ |
| KB-Q009 | positive | correct | 是 | 是 | Kill Bill 的发票项目（Invoice Item）都有哪些类型？ |
| KB-Q010 | positive | correct | 是 | 是 | Kill Bill 的发票是什么时候生成的？ |
| KB-Q011 | positive | correct | 是 | 是 | 什么叫信用余额调整（CBA，credit balance adjustment）？ |
| KB-Q012 | positive | partial | 否 | 是 | 发票余额在哪些情况下会是 0？ |
| KB-Q013 | positive | correct | 是 | 是 | 一张发票可以同时包含多个订阅的费用吗？ |
| KB-Q014 | positive | correct | 是 | 是 | Kill Bill 支持哪些用量计费（Usage Billing）类型？ |
| KB-Q015 | positive | correct | 是 | 是 | 用量计费的 ALL_TIER 和 TOP_TIER 两种策略有什么区别？ |
| KB-Q016 | positive | correct | 是 | 是 | 系统默认会回溯多少个计费周期来重算用量费用？可以改吗？ |
| KB-Q017 | positive | correct | 是 | 是 | Kill Bill 提供哪些发票试算（Dry Run）方式？ |
| KB-Q018 | positive | correct | 是 | 否 | 管理员给账户加一笔 20 美元的信用（credit），在发票层面会怎么体现？ |
| KB-Q019 | positive | partial | 是 | 是 | 系统默认会在发票生成后自动扣款吗？什么情况下不会自动扣款？ |
| KB-Q020 | positive | wrong | 是 | 是 | 可以用一笔支付同时支付多张发票吗？ |
| KB-Q021 | positive | correct | 是 | 是 | 发票支付发生后如果退款（refund），在发票-支付记录里如何体现？ |
| KB-Q022 | positive | partial | 是 | 是 | 支付插件返回 ERROR（例如余额不足）时，Kill Bill 会把交易置为哪个状态、返回什么 HTTP 码？ |
| KB-Q023 | positive | correct | 是 | 是 | 对于处于 PENDING 或 UNKNOWN 的支付交易，Kill Bill 怎么最终确定它的状态？ |
| KB-Q024 | positive | correct | 是 | 是 | 如果客户用支票在系统外付款，Kill Bill 怎么把这笔款记到发票上？ |
| KB-Q025 | positive | partial | 是 | 是 | Kill Bill 默认安装后就自带某个支付网关（比如 Stripe）的插件吗？ |
| KB-Q026 | positive | correct | 是 | 是 | 逾期（Overdue / 催收）状态是按订阅判断还是按账户判断？ |
| KB-Q027 | positive | partial | 是 | 是 | 逾期配置里，判断是否进入某个逾期状态可以基于哪些条件？ |
| KB-Q028 | positive | correct | 是 | 是 | 一个逾期状态可以配置哪些系统行为？ |
| KB-Q029 | positive | correct | 是 | 是 | 逾期配置里的 autoReevaluationInterval 是做什么用的？ |
| KB-Q030 | positive | wrong | 是 | 是 | Kill Bill 核心系统会在发票上自动计算并添加税额（TAX）吗？ |
| KB-Q031 | positive | correct | 是 | 是 | Kill Bill 中权限（Permissions）、角色（User Role）和用户（User）是什么关系？ |
| KB-N001 | negative | refused | - | 是 | Kill Bill 能自动生成符合中国税务规定的增值税专用发票（含纳税人识别号、发票代码）吗？ |
| KB-N002 | negative | refused | - | 是 | Kill Bill 会为我的客户提供一个手机 App（iOS/Android），让客户自己查看和支付发票吗？ |
| KB-N003 | negative | refused | - | 是 | Kill Bill 内置了自动拨打催收电话或群发催款短信的功能吗？ |
| KB-N004 | negative | refused | - | 是 | Kill Bill 能把发票数据导出成会计总账（General Ledger）或符合 GAAP 的财务报表吗？ |
| KB-N005 | negative | refused | - | 是 | 发票逾期后，系统会自动按天加收滞纳金或罚息吗？ |
| KB-N006 | negative | refused | - | 是 | Kill Bill 支持信用卡分期付款（比如分 12 期）吗？ |
| KB-N007 | negative | refused | - | 是 | 如果客户名下已经生成了两张独立的未付发票，可以把它们合并成一张发票吗？ |
| KB-N008 | negative | refused | - | 是 | Kill Bill 能把发票导出成 PDF 文件并自动邮件发给客户吗？ |
| KB-N009 | negative | refused | - | 是 | Kill Bill 支持对发票做数字签名或区块链存证以防篡改吗？ |
