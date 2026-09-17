# L4 端到端问答报告 (qa_eval)

- 生成时间: 2026-09-17T01:03:21.792396+00:00
- 知识库: `D:\openCodeProject\code-to-doc\docs\biz-kb2`
- 黄金集: `D:\openCodeProject\code-to-doc\benchmark\golden-set\killbill-invoice-80.yaml`
- top-k: 12
- 索引片段数: 696
- 题目数: 85
- LLM: provider=deepseek model=deepseek-chat base_url=https://api.deepseek.com

## 指标

- **answer_accuracy: 53.1%**
- **faithfulness: 100.0%**
- **retrieval_hit_rate: 92.2%**
- **refusal_correctness: 95.2%**
- answer_score_weighted: 69.5%

## 逐题结果

| 题号 | 类型 | 判定 | 检索命中 | 忠实 | 问题 |
|---|---|---|---|---|---|
| KB-Q001 | positive | partial | 是 | 是 | 订购服务的试用期结束后会自动开始扣费吗？ |
| KB-Q002 | positive | correct | 是 | 是 | 计划（Plan）的阶段（Phase）可以配置成哪几种类型？ |
| KB-Q003 | positive | correct | 是 | 是 | Kill Bill 里的产品品类（Product Category）有哪些？ |
| KB-Q004 | positive | correct | 是 | 是 | 同一个订阅包（Bundle）里可以有多个基础（BASE）订阅吗？ |
| KB-Q005 | positive | correct | 是 | 是 | Kill Bill 的计费对齐（Billing Alignment）规则支持哪几种方式？ |
| KB-Q006 | positive | correct | 是 | 是 | 为什么新订阅的第一张发票有时金额会被按比例折算（proration）？ |
| KB-Q007 | positive | correct | 否 | 是 | 一次性固定费用（FIXED 项目）会被按比例折算吗？ |
| KB-Q008 | positive | partial | 是 | 是 | 用户升级计划时，系统怎么算旧计划没用完的那部分费用？ |
| KB-Q009 | positive | correct | 是 | 是 | Kill Bill 的发票项目（Invoice Item）都有哪些类型？ |
| KB-Q010 | positive | correct | 是 | 是 | Kill Bill 的发票是什么时候生成的？ |
| KB-Q011 | positive | partial | 是 | 是 | 什么叫信用余额调整（CBA，credit balance adjustment）？ |
| KB-Q012 | positive | partial | 否 | 是 | 发票余额在哪些情况下会是 0？ |
| KB-Q013 | positive | correct | 是 | 是 | 一张发票可以同时包含多个订阅的费用吗？ |
| KB-Q014 | positive | correct | 是 | 是 | Kill Bill 支持哪些用量计费（Usage Billing）类型？ |
| KB-Q015 | positive | correct | 是 | 是 | 用量计费的 ALL_TIER 和 TOP_TIER 两种策略有什么区别？ |
| KB-Q016 | positive | correct | 是 | 是 | 系统默认会回溯多少个计费周期来重算用量费用？可以改吗？ |
| KB-Q017 | positive | correct | 是 | 是 | Kill Bill 提供哪些发票试算（Dry Run）方式？ |
| KB-Q018 | positive | partial | 是 | 是 | 管理员给账户加一笔 20 美元的信用（credit），在发票层面会怎么体现？ |
| KB-Q019 | positive | correct | 是 | 是 | 系统默认会在发票生成后自动扣款吗？什么情况下不会自动扣款？ |
| KB-Q020 | positive | wrong | 是 | 是 | 可以用一笔支付同时支付多张发票吗？ |
| KB-Q021 | positive | correct | 是 | 是 | 发票支付发生后如果退款（refund），在发票-支付记录里如何体现？ |
| KB-Q022 | positive | partial | 是 | 是 | 支付插件返回 ERROR（例如余额不足）时，Kill Bill 会把交易置为哪个状态、返回什么 HTTP 码？ |
| KB-Q023 | positive | correct | 是 | 是 | 对于处于 PENDING 或 UNKNOWN 的支付交易，Kill Bill 怎么最终确定它的状态？ |
| KB-Q024 | positive | correct | 是 | 是 | 如果客户用支票在系统外付款，Kill Bill 怎么把这笔款记到发票上？ |
| KB-Q025 | positive | partial | 是 | 是 | Kill Bill 默认安装后就自带某个支付网关（比如 Stripe）的插件吗？ |
| KB-Q026 | positive | correct | 是 | 是 | 逾期（Overdue / 催收）状态是按订阅判断还是按账户判断？ |
| KB-Q027 | positive | correct | 是 | 是 | 逾期配置里，判断是否进入某个逾期状态可以基于哪些条件？ |
| KB-Q028 | positive | partial | 是 | 是 | 一个逾期状态可以配置哪些系统行为？ |
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
| KB-Q032 | positive | correct | 是 | 是 | 发票的计费金额（charged amount）到底由哪些类型的项目加总而来？哪些类型的项目不计入？ |
| KB-Q033 | positive | partial | 是 | 是 | 发票余额（invoice balance）的计算公式是什么？ |
| KB-Q034 | positive | correct | 是 | 是 | Kill Bill 的发票一共有哪几种状态？ |
| KB-Q035 | positive | correct | 是 | 是 | 一张发票的余额在什么情况下一定为 0？VOID 状态算不算？ |
| KB-Q036 | positive | wrong | 是 | 是 | 对一张已经付清的发票再做一次发票项目调整（item adjustment），系统会额外生成什么项目？如果这张发票还没付，结果一样吗？ |
| KB-Q037 | positive | partial | 是 | 是 | 给一张已付发票退款时，“带发票项目调整”和“不带发票项目调整”两种做法，对发票余额的影响有什么不同？ |
| KB-Q038 | positive | partial | 否 | 是 | 启用父子账户（Hierarchical Accounts）后，子账户的发票和父账户的汇总发票之间是怎么联动的？ |
| KB-Q039 | positive | correct | 否 | 是 | 父账户的汇总发票上包含什么样的发票项目？ |
| KB-Q040 | positive | partial | 是 | 是 | 管理员给账户加 20 美元信用，这张“信用发票”上具体有哪两条项目、金额各是多少？它的计费金额和余额分别是多少？ |
| KB-Q041 | positive | wrong | 是 | 是 | 用发票试算（dry run）模拟把一个年付订阅改成月付，返回的预测发票通常由哪三类项目组成？各自的作用是什么？ |
| KB-Q042 | positive | partial | 是 | 是 | 支付插件返回 CANCELED（例如网关根本没被调用、插件硬失败）时，交易状态、支付状态和 HTTP 返回码分别是什么？系统会尝试修复吗？ |
| KB-Q043 | positive | partial | 是 | 是 | 如果一笔支付被 control plugin 中止（abort），系统会记录下什么？返回什么 HTTP 码？ |
| KB-Q044 | positive | partial | 是 | 是 | 一笔支付失败并重试时，会产生几个 payment transaction、几个 payment attempt？重试后这些记录分别处于什么状态？ |
| KB-Q045 | positive | partial | 否 | 是 | Kill Bill 默认的失败支付重试日程是什么？可以怎么改？ |
| KB-Q046 | positive | correct | 是 | 是 | 支付重试系统（Payment Retry）和逾期系统（Overdue）是一回事吗？它们怎么配合？ |
| KB-Q047 | positive | partial | 是 | 是 | 客户发起拒付（chargeback）后，发票-支付记录里会多出什么类型的记录，金额符号是怎样的？ |
| KB-Q048 | positive | correct | 是 | 是 | 账户的默认支付方式在收款时怎么被使用？能不能临时改用别的支付方式扣款？ |
| KB-Q049 | positive | correct | 是 | 是 | Kill Bill 通过什么机制在支付执行前后修改支付行为（比如中止支付、改金额/币种、改支付方式、安排重试）？怎么启用它？ |
| KB-Q050 | positive | wrong | 是 | 是 | 写 overdue.xml 时，状态定义的排列顺序有要求吗？状态名有什么限制？ |
| KB-Q051 | positive | partial | 是 | 是 | overdue 配置里 initialReevaluationInterval 和每个状态里的 autoReevaluationInterval 分别是什么？ |
| KB-Q052 | positive | correct | 是 | 是 | 账户打了 OVERDUE_ENFORCEMENT_OFF 控制标签会怎样？移除标签后呢？ |
| KB-Q053 | positive | correct | 是 | 是 | 如果不配置 overdue.xml，Kill Bill 默认的逾期行为是什么？ |
| KB-Q054 | positive | partial | 是 | 是 | 逾期状态里的 isClearState 是做什么的？查询账户逾期状态会返回哪些关键字段？ |
| KB-Q055 | positive | correct | 是 | 是 | Kill Bill 怎么表示 catalog（目录）的版本？想改价格但让现有订阅晚些时候才生效，怎么实现？ |
| KB-Q056 | positive | wrong | 是 | 是 | 目录里 plan/phase 的 name 有什么命名限制？name 和 prettyName 有什么区别？ |
| KB-Q057 | positive | partial | 是 | 是 | 附加组件（ADD_ON）通常使用哪种计费对齐方式？如果 BCD 落在当月不存在的日期（比如 4 月 31 日）会怎么处理？ |
| KB-Q058 | positive | correct | 是 | 是 | 目录规则里计划变更时机（changePolicy）可以取哪些值？ILLEGAL 表示什么？ |
| KB-Q059 | positive | wrong | 是 | 是 | 新增附加组件时，怎样让它和基础计划共用一个试用期结束时间？ |
| KB-Q060 | positive | wrong | 是 | 是 | 订阅取消时，entitlement（权限）和 billing（计费）为什么可能不一致？CTD 是什么？ |
| KB-Q061 | positive | correct | 是 | 是 | 用量计费支持哪些 billingMode？预付费（IN_ADVANCE）现在支持吗？ |
| KB-Q062 | positive | partial | 是 | 是 | CAPACITY 用量模式下，多个 unit 的峰值是怎么决定用哪一档价格的？它和 CONSUMABLE 的本质区别是什么？ |
| KB-Q063 | positive | wrong | 是 | 是 | 用量阶梯（tier）定义里，max 设为 -1 代表什么？tieredBlock 里的 size 又是什么意思？ |
| KB-Q064 | positive | correct | 是 | 是 | 用量发票默认是每个阶梯输出一条 USAGE 项目，还是汇总成一条？如果要按明细输出，怎么开关？ |
| KB-N010 | negative | refused | - | 是 | 能不能让同一张发票里同时包含美元和欧元两种货币的费用项目？ |
| KB-N011 | negative | refused | - | 是 | Kill Bill 内置了基于机器学习的支付欺诈检测和风控评分吗？ |
| KB-N012 | negative | refused | - | 是 | Kill Bill 核心能自动生成符合 ASC 606 的收入确认（递延收入摊销）报表吗？ |
| KB-N013 | negative | refused | - | 是 | 客户能在结账时输入一个折扣码（coupon code），系统自动校验并打折吗？ |
| KB-N014 | negative | refused | - | 是 | 能不能根据客户活跃用户数自动增减订阅的席位数（seats）并按席位自动计费？ |
| KB-N015 | negative | refused | - | 是 | Kill Bill 能自动开具采购订单（PO 编号）并做采购单/收货单/发票的三单匹配吗？ |
| KB-N016 | negative | refused | - | 是 | Kill Bill 能自动向税务机关申报并代缴增值税吗？ |
| KB-N017 | negative | hallucinated | - | 是 | 能不能在 Kill Bill 里发起并跟踪一起来自支付网关的拒付争议（dispute）处理流程？ |
| KB-N018 | negative | refused | - | 是 | Kill Bill 能自动计算坏账准备并生成应收账款账龄分析（aging）报表吗？ |
| KB-N019 | negative | refused | - | 是 | Kill Bill 内置了 ACH 直接借记授权书（mandate）的采集、存储和合规管理吗？ |
| KB-N020 | negative | refused | - | 是 | 能否配置一个多级发票审批工作流：发票生成后必须经主管审批通过才允许提交给客户？ |
| KB-N021 | negative | refused | - | 是 | Kill Bill 能做价格 A/B 测试：对同一个产品按用户随机分配不同价格吗？ |
