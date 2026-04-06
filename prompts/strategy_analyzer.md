# 策略分析 Prompt 模板

本文件定义策略分析引擎的输入输出规范和分析流程。strategy_analyzer 负责对用户案情进行多维度分析，输出结构化结果供 strategy_builder 生成最终策略文件。

---

## 一、输入定义

策略分析引擎接受以下输入：

| 输入项 | 文件/来源 | 说明 |
|--------|----------|------|
| 案情档案 | `cases/{case_id}/case.md` | 用户的完整案情记录，包含基本信息、事件经过、证据清单等 |
| 法律知识库 | `prompts/legal_knowledge.md` | 内置劳动法知识，作为分析的法律依据 |
| 阶段信息 | `cases/{case_id}/meta.json` → `current_phase` | 用户当前所处阶段（negotiating/pressured/noticed/separated/arbitrating/closed） |
| 用户意愿 | 用户对话输入 | 用户期望的解决方向（协商/不离职/仲裁/没想好） |
| 原始材料 | `cases/{case_id}/evidence/` | 用户上传的原始证据文件（截图、录音转写、文档等） |

### case.md 必要字段检查

分析前需验证 case.md 包含以下关键字段，缺失则提示用户补充：

- [ ] 公司名称与基本信息
- [ ] 入职日期与合同期限
- [ ] 试用期约定期限
- [ ] 岗位名称与转正工资
- [ ] 试用期实发工资
- [ ] 被约谈/辞退的具体经过
- [ ] 公司给出的辞退理由
- [ ] 是否签署"自愿离职"等文件
- [ ] 当前状态（是否仍在职）

---

## 二、输出定义

策略分析输出为 JSON 结构，供 strategy_builder.md 直接消费：

```json
{
  "case_id": "string",
  "analysis_timestamp": "ISO 8601",
  "phase_assessment": {
    "current_phase": "negotiating|pressured|noticed|separated|arbitrating|closed",
    "phase_confidence": "high|medium|low",
    "phase_reasoning": "string"
  },
  "global_direction": {
    "recommended_branch": "A|B|C",
    "recommendation_reasoning": "string",
    "user_intention": "negotiate|stay|arbitrate|undecided",
    "branch_suitability": {
      "A_score": 0.0,
      "B_score": 0.0,
      "C_score": 0.0
    }
  },
  "legal_judgment": {
    "company_action_legality": "legal|questionable|illegal",
    "legality_reasoning": "string",
    "strongest_legal_basis": [
      {
        "article": "string",
        "content_summary": "string",
        "applicability": "string"
      }
    ],
    "win_probability": {
      "level": "high|medium|low",
      "percentage_range": "70-90%|40-70%|10-40%",
      "reasoning": "string",
      "key_risk_factors": ["string"]
    }
  },
  "evidence_strategy": {
    "sufficiency_score": 0.0,
    "sufficiency_level": "sufficient|partially_sufficient|insufficient",
    "existing_evidence_assessment": "string",
    "evidence_to_supplement": [
      {
        "evidence_type": "string",
        "description": "string",
        "priority": "critical|high|medium|low",
        "collection_guidance": "string"
      }
    ],
    "evidence_chain_suggestions": ["string"]
  },
  "action_plan": {
    "short_term": [
      {
        "action": "string",
        "deadline": "string",
        "priority": "critical|high|medium|low",
        "details": "string"
      }
    ],
    "mid_term": [
      {
        "action": "string",
        "deadline": "string",
        "priority": "high|medium|low",
        "details": "string"
      }
    ],
    "long_term": [
      {
        "action": "string",
        "deadline": "string",
        "priority": "medium|low",
        "details": "string"
      }
    ],
    "key_deadlines": [
      {
        "deadline_name": "string",
        "date": "ISO 8601 or relative",
        "consequence_of_missing": "string"
      }
    ]
  },
  "counter_strategy": {
    "predicted_company_tactics": [
      {
        "tactic": "string",
        "probability": "high|medium|low",
        "counter_response": "string",
        "script_suggestion": "string"
      }
    ],
    "red_lines": [
      {
        "red_line": "string",
        "reason": "string",
        "what_to_do": "string"
      }
    ]
  },
  "document_checklist": [
    {
      "document_name": "string",
      "purpose": "string",
      "priority": "critical|high|medium|low",
      "template_available": true
    }
  ]
}
```

---

## 三、分析维度（7 层）

### Layer 0：阶段感知

**输入：** `meta.json` 的 `current_phase` 字段

**处理逻辑：**
1. 读取 meta.json 中的 current_phase
2. 结合 case.md 中的最新事件判断阶段是否准确
3. 如发现阶段与实际不符，标记 phase_confidence 为 low 并给出修正建议
4. 阶段判定规则参考 `phase_router.md`

**输出：** `phase_assessment` 对象

---

### Layer 1：全局方向决策树

**处理逻辑：**

根据当前阶段和用户意愿，在三条分支中确定推荐方向：

```
开始
 │
 ├─ 用户当前在职？
 │   ├─ 是 → 公司是否已发出正式解雇通知？
 │   │        ├─ 否 → 分支 A：协商离职（默认推荐）
 │   │        │        或 分支 B：坚决不离职（用户选择时）
 │   │        └─ 是 → 分支 A：协商最优解
 │   │                 或 分支 C：准备仲裁
 │   └─ 否 → 已离职
 │            ├─ 离职未超 1 年 → 分支 C：仲裁准备
 │            └─ 离职超 1 年 → 时效风险提示
 │
 └─ 用户意愿优先：
     ├─ "协商" → 走分支 A 分析
     ├─ "不离职" → 走分支 B 分析
     ├─ "仲裁" → 走分支 C 分析
     └─ "没想好" → 三条分支均做分析并对比
```

**输出：** `global_direction` 对象

---

### Layer 2：核心法律判断

**分析步骤：**

1. **公司行为合法性判定：**
   - 将 case.md 中的辞退理由与劳动合同法第 39、40、21 条逐条比对
   - 检查公司是否满足法定解除条件
   - 判定结果：`legal`（完全合法）/ `questionable`（存在争议）/ `illegal`（明显违法）

2. **最有力法律依据提取：**
   - 从 legal_knowledge.md 中匹配最直接适用的法条
   - 优先选择：劳动合同法第 39 条第 1 款（不符合录用条件）相关条款
   - 补充适用：第 48、87 条（违法解除赔偿）
   - 每条法条需说明适用性

3. **胜诉概率评估：**
   - 高（70-90%）：公司明显违法，证据充分（如无理由辞退+有录音+有书面通知）
   - 中（40-70%）：公司存在违法嫌疑，但证据有一定不足
   - 低（10-40%）：公司行为可能合法，或用户证据严重不足
   - 需列出影响胜诉概率的关键因素

**输出：** `legal_judgment` 对象

---

### Layer 3：证据策略

**分析步骤：**

1. **充分性评估：**
   - 清点 case.md 中列出的已有证据
   - 按证据类型分类：书面证据 / 电子证据 / 录音录像 / 证人证言
   - 评估证据链完整性（0-10 分制）
   - 判定等级：sufficient（≥8分）/ partially_sufficient（4-7分）/ insufficient（<4分）

2. **需补充清单：**
   - 根据公司辞退理由，确定公司需要举证的内容
   - 列出用户应对应准备的反击证据
   - 按优先级排列：critical > high > medium > low
   - 每项证据给出具体的收集指引

3. **证据链完善建议：**
   - 梳理现有证据的逻辑关系
   - 指出证据链中的断点
   - 给出补链建议

**关键证据类型检查清单：**

| 证据类型 | 具体内容 | 收集方式 | 证明目的 |
|---------|---------|---------|---------|
| 劳动关系证明 | 劳动合同、工牌、社保记录 | 自有/公司索取/社保局打印 | 证明存在劳动关系 |
| 工资标准证明 | 银行流水、工资条、offer 邮件 | 银行App截图/HR索取 | 确定工资基数 |
| 辞退事实证明 | 解除通知、辞退录音、聊天记录 | 要求书面通知/录音 | 证明公司做出了解除行为 |
| 辞退理由证明 | HR谈话录音、微信聊天、邮件 | 录音/截图保存 | 确定公司主张的解除理由 |
| 录用条件证明 | 录用条件文件、岗位说明书 | 要求公司提供 | 反驳"不符合录用条件" |
| 考核过程证明 | 考核表、绩效评分记录 | 要求公司提供 | 审查考核是否公正 |
| 在职表现证明 | 工作成果、同事评价、表扬记录 | 自行整理 | 反证工作能力达标 |

**输出：** `evidence_strategy` 对象

---

### Layer 4：行动方案

**短期（1-7天）：**
- 紧急证据保全行动
- 对公司辞退行为的书面回应
- 关键沟通的应对准备
- 时效相关的时间节点标注

**中期（1-4周）：**
- 与公司正式协商或准备仲裁材料
- 证据补充完善
- 法律文书起草
- 专业咨询（如需要）

**长期（1-6个月）：**
- 仲裁/诉讼程序推进
- 执行阶段准备
- 新工作过渡

**关键时间节点：**
- 仲裁时效（1年）倒计时
- 举证期限
- 答辩期限
- 各类通知的回复期限

**输出：** `action_plan` 对象

---

### Layer 5：应对策略

**公司可能的话术及应对：**

| 公司话术 | 应对策略 | 参考话术 |
|---------|---------|---------|
| "你试用期不合格" | 要求提供具体的录用条件和考核标准 | "请问我的录用条件是什么？有书面文件吗？我什么时候签字确认过？" |
| "团队调整不需要你了" | 指出这不是试用期法定解除理由 | "试用期解除只能依据第39条的规定，团队调整不属于法定理由" |
| "签了这个离职申请，给你多一个月工资" | 拒签自愿离职，协商解除需明确条款 | "如果是协商解除，请出具正式的协商解除协议，注明补偿金额和支付时间" |
| "你不签也没用，公司说了算" | 坚持立场，申请仲裁 | "我不同意这个决定。如公司坚持解除，请出具书面解除通知" |
| "你还在试用期，公司随时可以让你走" | 纠正法律误解 | "试用期不是随意解除期，公司需要证明我不符合录用条件" |
| "你的表现大家都有目共睹" | 要求提供具体、量化的考核数据 | "请提供具体的考核标准和我的考核结果，包括评分依据和评分过程" |

**红线提醒（绝对不可做的事）：**

1. **不签"自愿离职"** —— 签了等于放弃大部分权利
2. **不口头同意离职** —— 口头同意也可能被利用
3. **不拒绝签收解除通知** —— 签收不等于同意，但拒绝签收可能导致无法举证
4. **不删除任何工作记录** —— 离职前后保留所有证据
5. **不在未录音的情况下与 HR 单独谈话** —— 重要谈话务必录音
6. **不逾期未申请仲裁** —— 超过1年时效将丧失胜诉权

**输出：** `counter_strategy` 对象

---

### Layer 6：文书准备

**常见需要的法律文书清单：**

| 文书名称 | 用途 | 优先级 | 何时需要 |
|---------|------|--------|---------|
| 解除劳动合同通知书（公司出具） | 证明解除事实 | critical | 立即要求公司出具 |
| 书面回复函（回复公司解除通知） | 表明不同意解除的立场 | critical | 收到通知后3日内 |
| 协商解除协议（如协商） | 明确补偿金额和条款 | high | 协商达成一致时 |
| 仲裁申请书 | 启动仲裁程序 | high | 决定仲裁时 |
| 证据清单 | 仲裁举证 | high | 提交仲裁申请时 |
| 劳动关系证明材料 | 证明劳动关系 | critical | 始终需要 |
| 工资流水记录 | 确定工资基数 | critical | 始终需要 |
| 陈述词/代理词 | 仲裁庭陈述 | medium | 开庭前准备 |

**输出：** `document_checklist` 对象

---

## 四、用户意愿处理逻辑

### 默认行为：基于阶段和证据的理性推荐

无论用户意愿如何，策略分析首先给出基于当前阶段、证据充分度、胜诉概率的**理性推荐方向**。

### 意愿分支处理

**用户选择"协商"（分支 A）：**
- 重点分析：协商谈判策略
- 设定：合理底线和目标金额
- 准备：谈判话术和让步节奏
- 同时准备：协商失败的 Plan B（仲裁路径）

**用户选择"不离职"（分支 B）：**
- 切换到反驳策略分析
- 重点：如何用证据证明自己符合录用条件
- 准备：书面回复模板、反驳话术
- 同时提示：公司可能强制解除的风险和应对

**用户选择"仲裁"（分支 C）：**
- 切换到仲裁准备分析
- 重点：仲裁申请书撰写、证据清单整理
- 准备：陈述词、答辩策略
- 同时评估：胜诉概率和时间成本

**用户选择"没想好"：**
- 三条分支均做分析
- 输出各路径的对比表格
- 包含：预期收益、时间成本、精力成本、风险等级
- 引导用户根据自身情况选择
- 参考 `cost_calculator.md` 进行量化对比

### 意愿切换机制

用户可在任何时候切换意愿，策略分析引擎应：
1. 记录意愿变化历史
2. 保留之前分支的分析结果
3. 以新意愿为主重新调整推荐
4. 不丢弃已完成的分支分析（便于用户比较）

---

## 五、分析质量保障

### 自检清单

每次分析完成后，需检查：

- [ ] 所有 7 层分析是否完整
- [ ] 法律条文引用是否准确（与 legal_knowledge.md 核对）
- [ ] 胜诉概率评估是否有充分理由支撑
- [ ] 证据补充清单是否具体可执行
- [ ] 行动方案是否有明确时间节点
- [ ] 应对策略是否覆盖公司最可能的话术
- [ ] 红线提醒是否充分
- [ ] 文书清单是否完整

### 免责声明

每份分析报告末尾需附带：

> **免责声明：** 本分析基于用户提供的案情信息和现行法律法规生成，仅供参考，不构成法律意见。具体案件建议咨询专业劳动法律师。法律法规可能随时更新，请以最新版本为准。
