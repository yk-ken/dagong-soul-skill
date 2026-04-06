# 策略文件生成模板

本文件定义 `strategy.md` 的标准结构和生成规则。strategy_builder 消费 strategy_analyzer 输出的 JSON 结果，生成用户可读的完整维权策略文件。

---

## 生成原则

1. **语气要求：** 专业、理性、支持性。不过度乐观（"你一定能赢"），也不悲观（"算了没办法"）。使用"建议""可以""有机会"等中性但积极的措辞。
2. **结构清晰：** 严格按以下模板结构生成，不增减章节。
3. **个性化：** 所有 `{占位符}` 必须根据用户案情数据填充，不留空。
4. **可操作性：** 每个建议必须具体到"做什么""怎么做""什么时候做"。
5. **法律准确：** 引用的法条需与 legal_knowledge.md 核对一致。

---

## strategy.md 模板

```markdown
# 维权策略：{公司名}

> 生成时间：{YYYY-MM-DD HH:mm}
> 案件编号：{case_id}
> 免责声明：本策略基于您提供的信息和现行法律法规生成，仅供参考，不构成法律意见。

---

## 阶段感知

> 当前阶段：**{phase_display_name}** | 用户意愿：**{intention_display_name}**

{phase_description}

{如果阶段判断置信度不高，添加：}
> ⚠️ 阶段判断提示：{phase_confidence_reasoning}。如不准确，请告知您当前的实际状态，我会重新调整策略。

---

## 全局方向建议

{基于当前阶段和证据的理性分析，给出推荐方向。说明为什么这个方向最适合当前情况。}

{各分支详细策略如下。您当前推荐的分支为 **{recommended_branch_name}**。}

### 分支 A：协商离职（默认推荐）

**适用条件：** {branch_a_conditions}

**赔偿谈判策略：**

1. **目标金额：** {target_amount}（计算依据：{calculation_basis}）
2. **底线金额：** {floor_amount}（低于此金额不接受）
3. **理想金额：** {ideal_amount}（谈判起点）
4. **让步节奏：**
   - 第一轮报价：{ideal_amount}，附带理由
   - 如公司还价低于底线：坚持底线，出示法律依据
   - 如公司还价在底线以上：可考虑接受，但需确保条款明确
5. **谈判要点：**
   - {negotiation_point_1}
   - {negotiation_point_2}
   - {negotiation_point_3}

**协商注意事项：**
- {caution_1}
- {caution_2}
- {caution_3}

---

### 分支 B：坚决不离职

**适用条件：** {branch_b_conditions}

**反驳策略：**

1. **核心论点：** {core_argument}
2. **证据反击点：**
   - {counter_point_1}
   - {counter_point_2}
   - {counter_point_3}
3. **书面回复要点：**
   - 明确表示不同意解除决定
   - 要求公司提供具体的不符合录用条件的证据
   - 保留申请仲裁的权利

**风险提示：**
- {risk_1}
- {risk_2}

---

### 分支 C：已被动离职

**适用条件：** {branch_c_conditions}

**违法解除认定路径：**

1. **公司违法点分析：**
   - {violation_point_1}
   - {violation_point_2}
2. **可主张金额：**
   - 违法解除赔偿金（2N）：{amount_2n} 元
   - 试用期工资差额（如适用）：{wage_diff} 元
   - 其他可主张项目：{other_claims}
   - **合计：** {total_claim} 元
3. **恢复劳动关系选项：**
   - 如您希望恢复劳动关系，可主张继续履行劳动合同
   - 诉讼期间的工资公司也应补发

**仲裁准备要点：**
- {arbitration_point_1}
- {arbitration_point_2}
- {arbitration_point_3}

---

## 核心法律判断

### 公司行为合法性分析

**判定结果：{legality_result_display}**

{legality_detailed_analysis}

### 最有力法律依据

| 序号 | 法条 | 核心内容 | 与本案的关联 |
|------|------|---------|-------------|
| 1 | {article_1} | {content_1} | {relevance_1} |
| 2 | {article_2} | {content_2} | {relevance_2} |
| 3 | {article_3} | {content_3} | {relevance_3} |

### 胜诉概率评估

**胜诉概率：{win_probability_display}（{percentage_range}）**

**理由：**
{win_probability_reasoning}

**关键风险因素：**
{key_risk_factors_list}

---

## 证据策略

### 证据充分性评估

**当前评分：{sufficiency_score}/10 —— {sufficiency_level_display}**

{sufficiency_assessment}

### 已有证据清单

| 序号 | 证据名称 | 证据类型 | 证明目的 | 证明力评估 |
|------|---------|---------|---------|-----------|
| 1 | {evidence_1_name} | {evidence_1_type} | {evidence_1_purpose} | {evidence_1_strength} |

### 需补充证据清单

| 序号 | 证据名称 | 优先级 | 收集方式 | 收集指引 |
|------|---------|--------|---------|---------|
| 1 | {supplement_1_name} | {supplement_1_priority} | {supplement_1_method} | {supplement_1_guidance} |

### 证据链完善建议

{evidence_chain_suggestions_numbered_list}

---

## 行动方案

### 短期（1-7天）

| 序号 | 行动项 | 截止时间 | 优先级 | 具体操作 |
|------|--------|---------|--------|---------|
| 1 | {short_term_action_1} | {short_term_deadline_1} | {short_term_priority_1} | {short_term_details_1} |

### 中期（1-4周）

| 序号 | 行动项 | 截止时间 | 优先级 | 具体操作 |
|------|--------|---------|--------|---------|
| 1 | {mid_term_action_1} | {mid_term_deadline_1} | {mid_term_priority_1} | {mid_term_details_1} |

### 长期（1-6个月）

| 序号 | 行动项 | 截止时间 | 优先级 | 具体操作 |
|------|--------|---------|--------|---------|
| 1 | {long_term_action_1} | {long_term_deadline_1} | {long_term_priority_1} | {long_term_details_1} |

### 关键时间节点

| 时间节点 | 截止日期 | 错过后果 |
|---------|---------|---------|
| 1 | {deadline_1_name} | {deadline_1_date} | {deadline_1_consequence} |
| 2 | **仲裁时效** | **{arbitration_deadline}（1年时效）** | **超过时效将丧失胜诉权** |

---

## 应对策略

### 公司可能的话术及应对

{预测公司最可能使用的3-5种话术，每种给出应对建议和参考话术}

**话术 1：{predicted_tactic_1}**
- 可能性：{tactic_1_probability}
- 应对建议：{tactic_1_counter}
- 参考话术："{tactic_1_script}"

**话术 2：{predicted_tactic_2}**
- 可能性：{tactic_2_probability}
- 应对建议：{tactic_2_counter}
- 参考话术："{tactic_2_script}"

**话术 3：{predicted_tactic_3}**
- 可能性：{tactic_3_probability}
- 应对建议：{tactic_3_counter}
- 参考话术："{tactic_3_script}"

### 红线提醒

> 以下事项务必注意，违反可能导致维权失败或权益严重受损：

{red_lines_numbered_list}

---

## 文书准备清单

| 序号 | 文书名称 | 用途 | 优先级 | 是否有模板 | 当前状态 |
|------|---------|------|--------|-----------|---------|
| 1 | {doc_1_name} | {doc_1_purpose} | {doc_1_priority} | {doc_1_template} | {doc_1_status} |

---

## 附录：费用估算

### 预期收益/成本概览

| 项目 | 金额/说明 |
|------|----------|
| 违法解除赔偿金（2N） | {amount_2n} 元 |
| 经济补偿金（N） | {amount_n} 元 |
| 试用期工资差额 | {amount_diff} 元 |
| 其他可主张金额 | {amount_other} 元 |
| 仲裁费用 | 0 元（劳动仲裁不收费） |
| 律师费用（如请律师） | {lawyer_fee_estimate} |

### 维权路径对比

| 维度 | 协商 | 仲裁 | 诉讼 |
|------|------|------|------|
| 预期收益 | {negotiate_return} | {arbitrate_return} | {litigate_return} |
| 预计时间 | 1-2 周 | 45-60 天 | 3-6 个月 |
| 精力投入 | 低 | 中 | 高 |
| 胜诉概率 | N/A | {arbitrate_win_rate} | {litigate_win_rate} |
| 背调影响 | 无 | 可能有 | 较大可能 |

---

> 💡 **下一步建议：** {next_step_suggestion}
>
> 如有任何疑问或情况发生变化，请随时告诉我，我会及时调整策略。
```

---

## 模板填充规则

### 占位符填充说明

| 占位符类型 | 来源 | 填充规则 |
|-----------|------|---------|
| `{company_name}` | case.md | 直接取公司名称 |
| `{phase_*}` | strategy_analyzer JSON → phase_assessment | 根据阶段码映射显示名 |
| `{intention_*}` | 用户对话输入 | 映射：negotiate→协商，stay→不离职，arbitrate→仲裁，undecided→还没想好 |
| `{legality_*}` | strategy_analyzer JSON → legal_judgment | 映射显示名和详细分析 |
| `{win_probability_*}` | strategy_analyzer JSON → legal_judgment.win_probability | 使用 level 和 reasoning |
| `{evidence_*}` | strategy_analyzer JSON → evidence_strategy | 转为表格 |
| `{action_plan_*}` | strategy_analyzer JSON → action_plan | 按短期/中期/长期分表 |
| `{counter_strategy_*}` | strategy_analyzer JSON → counter_strategy | 逐一展开 |
| `{document_checklist_*}` | strategy_analyzer JSON → document_checklist | 转为表格 |
| 金额类 | 按计算公式生成 | 精确到元，附计算过程 |

### 阶段码到显示名映射

| 阶段码 | 显示名 |
|--------|--------|
| `negotiating` | 协商中 |
| `pressured` | 被施压 |
| `noticed` | 已收到解雇通知 |
| `separated` | 已离职 |
| `arbitrating` | 仲裁进行中 |
| `closed` | 已结案 |

### 意愿码到显示名映射

| 意愿码 | 显示名 |
|--------|--------|
| `negotiate` | 协商解决 |
| `stay` | 坚决不离职 |
| `arbitrate` | 申请仲裁 |
| `undecided` | 还没想好 |

### 金额计算规则

所有金额字段需附计算过程，格式如下：
```
违法解除赔偿金（2N）= 0.5 × 8,000 元 × 2 = 8,000 元
  工作年限：3个月（不满6个月按0.5年计）
  月平均工资：8,000 元（试用期实发3个月平均值）
  N = 0.5 × 8,000 = 4,000 元
  2N = 4,000 × 2 = 8,000 元
```

### 条件性内容

- 如用户处于 `negotiating` 或 `pressured` 阶段，分支 A 和 B 展开完整内容，分支 C 简略
- 如用户处于 `noticed` 或 `separated` 阶段，分支 C 展开完整内容，分支 A 和 B 简略
- 如用户选择 `undecided`，三条分支均完整展开

---

## 生成后自检

生成 strategy.md 后需检查：

1. 所有占位符是否已填充（无 `{` `}` 残留）
2. 金额计算是否正确且附带计算过程
3. 法条引用是否与 legal_knowledge.md 一致
4. 时间节点是否合理（不出现过去的时间作为未来截止日期）
5. 语气是否专业、理性、支持性
6. 红线提醒是否包含"不签自愿离职"等关键事项
7. 免责声明是否存在
