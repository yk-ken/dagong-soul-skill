# 打工魂·不灭.skill 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现完整的"打工魂·不灭" Claude Code skill，用户可以通过 `/create-dagong-soul` 创建个人维权案件 skill。

**Architecture:** Meta-skill 模式——创建器收集用户信息，分析后生成独立的案件 skill。遵循 AgentSkills 开放标准，参考同事.skill 的双层架构（案情档案 + 维权策略），但将产出目标从"模拟对话"变为"维权顾问 + 证据库"。

**Tech Stack:** Markdown (prompts) + Python 3.9+ (tools/parsers) + Claude Code Skill 标准 (SKILL.md frontmatter)

**项目路径:** `D:/workspace/dagong-soul-skill/`

---

## 并行化策略

```
Phase 1: 全并行（5 个 Agent 同时开发）
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Agent A    │ │  Agent B    │ │  Agent C    │ │  Agent D    │ │  Agent E    │
│ 法律+策略    │ │ 案情分析     │ │ 特殊功能     │ │ Python工具   │ │ 文档        │
│ 5个prompt   │ │ 4个prompt   │ │ 4个prompt   │ │ 7个.py      │ │ 3个文件     │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
         │              │              │              │              │
         └──────────────┴──────────────┴──────────────┴──────────────┘
                                    ↓
Phase 2: 串行（依赖 Phase 1 全部完成）
┌─────────────────────────────────────────────────────────────────┐
│  Agent F: SKILL.md（编排层，引用所有 prompts 和 tools）            │
└─────────────────────────────────────────────────────────────────┘
                                    ↓
Phase 3: 集成验证
┌─────────────────────────────────────────────────────────────────┐
│  Agent G: 集成测试 + 首次提交                                     │
└─────────────────────────────────────────────────────────────────┘
```

**为什么这样分组：**
- Phase 1 的 5 组之间**零依赖**——prompts 之间互不引用，tools 之间互不调用
- Phase 2 的 SKILL.md 是**编排层**，必须知道所有 prompts/tools 的接口才能正确编写
- Phase 3 依赖所有文件就位后才能做端到端验证

---

## Phase 1: 并行开发（5 个 Agent 同时执行）

---

### Task 1 [Agent A]: 法律知识 + 策略相关 Prompts

**Files:**
- Create: `D:/workspace/dagong-soul-skill/prompts/legal_knowledge.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/strategy_analyzer.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/strategy_builder.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/phase_router.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/cost_calculator.md`

- [ ] **Step 1: 写 `prompts/legal_knowledge.md`**

内置核心劳动法知识库，供 SKILL.md 和策略分析引用。内容必须包含：

1. **核心法条清单**（劳动合同法 + 劳动法，每条写明：法条号 + 核心内容 + 一句话解读 + 适用场景）
   - 劳动合同法第 19/20/21/39/40/46/47/48/87 条
   - 劳动法第 25/28/77-84 条
   - 相关司法解释核心条款

2. **常见维权场景判定表**（场景 | 合法性 | 维权方向 | 关键法条引用 | 用户应该做什么）
   - 试用期无理由辞退
   - 以"不符合录用条件"辞退但无标准
   - 有标准但未提前告知
   - 有标准+考核不达标+已告知
   - 公司以"团队调整"辞退
   - 试用期超法定时长
   - 试用期工资低于 80%
   - 未签劳动合同
   - 强制签"自愿离职"

3. **举证责任分配**（谁举证什么，什么情况下举证责任倒置）

4. **仲裁流程指引**（6 步流程 + 时间节点 + 时效）

5. **经济补偿金/赔偿金计算公式**（N / 2N / 工资基数定义）

- [ ] **Step 2: 写 `prompts/strategy_analyzer.md`**

策略分析的 prompt 模板，用于从案情档案 + 法律知识中提取维权策略。内容必须包含：

1. **分析流程**：
   - 输入：案情档案(case.md) + 法律知识(legal_knowledge.md) + 用户原始材料
   - 输出：结构化策略分析结果（供 strategy_builder.md 使用）

2. **分析维度**（按 PRD 第七节 Layer 0-7 的分层结构）：
   - 阶段感知判定规则
   - 公司行为合法性分析框架
   - 证据充分性评估标准
   - 胜诉可能性评估方法（高/中/低 + 判断依据）
   - 行动方案生成规则
   - 应对策略生成规则

3. **用户意愿处理逻辑**：
   - 默认推荐协商离职的场景和理由
   - 用户选择"不离职"时的分析切换
   - 用户选择"仲裁"时的分析切换
   - 用户"还没想好"时的分析展开

4. **输出格式规范**：JSON 结构，字段与 strategy_builder.md 的输入对应

- [ ] **Step 3: 写 `prompts/strategy_builder.md`**

策略文件生成模板，将 strategy_analyzer 的输出转为 strategy.md。内容必须包含：

1. **模板结构**（对应 PRD Layer 0-7）：
   ```
   # 维权策略：{公司名}

   ## Layer 0 — 阶段感知与全局方向
   ## Layer 1 — 全局方向决策树
     ### 分支 A：协商离职
     ### 分支 B：坚决不离职
     ### 分支 C：已被动离职
   ## Layer 2 — 核心法律判断
   ## Layer 3 — 证据策略
   ## Layer 4 — 行动方案
   ## Layer 5 — 应对策略
   ## Layer 6 — 文书模板
   ## Layer 7 — Correction 记录
   ```

2. **每个 Layer 的填充规则**：什么数据填什么位置，留什么占位

3. **语气要求**：专业、理性、支持性，避免过度乐观或悲观

- [ ] **Step 4: 写 `prompts/phase_router.md`**

阶段感知与策略路由规则。内容必须包含：

1. **阶段定义**（6 个阶段 + 进入条件 + 退出条件）：
   - `negotiating` / `pressured` / `noticed` / `separated` / `arbitrating` / `closed`

2. **每个阶段对应的策略重心**：
   - 协商中 → 谈判话术 + 底线设定 + 暗中收集证据
   - 被施压 → 红线提醒 + 录音建议 + 记录模板
   - 已通知 → 书面回复模板 + 证据保全
   - 已离职 → 仲裁申请书 + 证据清单 + 时效提醒
   - 仲裁中 → 陈述词 + 答辩策略
   - 已结案 → 强制执行 + 经验沉淀

3. **阶段转换触发条件**：什么事件导致从一个阶段进入下一阶段

4. **用户意愿优先决策树**：先推荐 → 再问 → 按选择执行 → 随时可切换

- [ ] **Step 5: 写 `prompts/cost_calculator.md`**

代价计算器 prompt，用于生成协商 vs 仲裁的量化对比。内容必须包含：

1. **计算维度**：
   - 经济收益：N / 2N / 补发工资 / 年假折算 / 加班费
   - 时间成本：各路径的时间预估
   - 机会成本：影响找工作的时间窗口
   - 背调风险：仲裁记录的影响评估
   - 心理成本：长期对抗的精神压力

2. **计算公式**：
   - 协商离职预期值 = 赔偿金额 × 100% / 时间投入
   - 仲裁维权预期值 = 预期赔偿 × 胜诉率 / (时间投入 × 机会成本系数)

3. **输出格式**：Unicode 方框表格（协商 vs 仲裁 vs 诉讼 三列对比）

4. **原则**：先给理性分析，再尊重用户选择

---

### Task 2 [Agent B]: 案情分析相关 Prompts

**Files:**
- Create: `D:/workspace/dagong-soul-skill/prompts/intake.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/case_analyzer.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/case_builder.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/emotion_tracker.md`

- [ ] **Step 1: 写 `prompts/intake.md`**

对话式信息录入的 prompt 模板。内容必须包含：

1. **问题序列**（3 轮对话收集）：

   **第 1 轮 — 基本信息（必填项）**：
   - 公司名称 → 自动生成 slug 建议
   - 入职日期
   - 目前进展阶段（6 选 1：约谈中/已收通知/已离职/仲裁中/已结案/其他）

   **第 2 轮 — 详细信息（可跳过）**：
   - 试用期约定时长 + 截止日期
   - 岗位 + 职级
   - 合同约定薪资 + 试用期薪资比例
   - 合同类型 + 合同总期限

   **第 3 轮 — 争议信息（可跳过）**：
   - 被通知的日期
   - 公司给出的理由（7 个常见理由标签 + 自定义）
   - 你认为是否合理
   - 简述发生了什么（自由文本）

2. **跳过逻辑**：用户说"跳过"/"不知道"时如何处理

3. **确认摘要**：收集完后展示确认信息，用户确认后才进入下一步

4. **语言**：中文，友好、简洁、不咄咄逼人

- [ ] **Step 2: 写 `prompts/case_analyzer.md`**

案情分析的 prompt 模板，用于从原始材料中提取结构化案情。内容必须包含：

1. **分析流程**：
   - 输入：intake 收集的基础信息 + 用户上传的原始材料（截图/PDF/聊天记录等）
   - 输出：结构化案情分析结果（供 case_builder.md 使用）

2. **提取维度**（6 大维度）：
   - ① 劳动关系确认：合同条款、时间线、薪资约定
   - ② 工作表现记录：成果清单、绩效结果、正面反馈、工作量
   - ③ 考勤记录：出勤、加班、请假
   - ④ 争议事件时间线：按时间排列 + 证据编号
   - ⑤ 证据清单：编号 | 名称 | 类型 | 来源 | 证明目的 | 强度评级（强/中/弱）
   - ⑥ 风险点识别：不利证据、公司反驳角度、需补充证据

3. **材料权重规则**（分析优先级）：
   - 书面通知 > HR 聊天记录 > 劳动合同 > 绩效评估 > 考勤记录 > 日常聊天

4. **输出格式**：JSON 结构，字段与 case_builder.md 的输入对应

- [ ] **Step 3: 写 `prompts/case_builder.md`**

案情文件生成模板，将 case_analyzer 的输出转为 case.md。内容必须包含：

1. **模板结构**：
   ```markdown
   # 案情档案：{公司名}

   ## 一、劳动关系确认
   ## 二、工作表现记录
   ## 三、考勤记录
   ## 四、争议事件时间线
   ## 五、证据清单
   ## 六、风险点识别
   ## 七、情绪时间线
   ## Correction 记录
   ```

2. **每个章节的填充规则**：
   - 时间线用表格（日期 | 事件 | 证据编号 | 备注）
   - 证据清单用表格（编号 | 名称 | 类型 | 来源 | 证明目的 | 强度）
   - 风险点分三级（高/中/低风险）

3. **证据强度评级标准**：
   - 强：书面文件、官方记录、带签名文件
   - 中：聊天截图、邮件、证人证言
   - 弱：口头描述、无原始载体的截图

4. **留白处理**：用户未提供的维度，标注"暂未提供，建议补充收集"

- [ ] **Step 4: 写 `prompts/emotion_tracker.md`**

情绪时间线生成的 prompt。内容必须包含：

1. **情绪提取规则**：
   - 从用户口述中提取心理状态（震惊/焦虑/愤怒/无力/理性/平静）
   - 从聊天记录中推断情绪变化（语气变化、回复频率变化）
   - 标注公司的不当施压行为（精神胁迫、冷暴力、孤立排挤、威胁背调等）

2. **时间线格式**：
   ```
   {日期}  {情绪emoji}  {情绪标签} — {事件描述}
   ```

3. **情绪标签库**：😐 正常 / 😰 震惊 / 😟 焦虑 / 😤 愤怒 / 😢 悲伤 / 😨 恐惧 / 🧘 理性 / 💪 坚定 / 🤔 困惑

4. **施压行为标注**：用 `[施压]` 标签标注公司的具体不当行为

5. **用途说明**：解释这条时间线在仲裁中的价值（证明公司不当行为模式）

---

### Task 3 [Agent C]: 特殊功能 + 进化机制 Prompts

**Files:**
- Create: `D:/workspace/dagong-soul-skill/prompts/hr_tactics.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/document_templates.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/merger.md`
- Create: `D:/workspace/dagong-soul-skill/prompts/correction_handler.md`

- [ ] **Step 1: 写 `prompts/hr_tactics.md`**

HR 常见话术库，用于对抗模拟功能。内容必须包含：

1. **话术分类**（每类 3-5 条，含 HR 原话 + 意图分析 + 用户应对建议）：

   **施压类**：
   - "公司认为你不太适合这个岗位"
   - "你还是主动辞职吧，这样不影响你背调"
   - "试用期双方都可以随时解除"
   - "你仲裁也赢不了的，别浪费时间"

   **利诱类**：
   - "我们给你 N+1 已经很客气了"
   - "你主动离职的话，我们可以给你多缴一个月社保"
   - "我帮你写好离职证明，不会影响你找工作"

   **恐吓类**：
   - "你要是不签，我们就按违纪处理"
   - "你在这个行业的圈子很小"
   - "我们会通知你未来的雇主"

   **模糊类**：
   - "公司觉得你价值观不太匹配"
   - "团队觉得你融入得不太好"
   - "你的产出没有达到预期"

2. **每条话术的拆解模板**：
   - HR 原话
   - 真实意图（HR 到底想达到什么目的）
   - 法律分析（这话在法律上站不站得住）
   - 应对话术（用户应该怎么回复，给出 2-3 个选项）
   - 红线提醒（绝对不要说/做的事情）

- [ ] **Step 2: 写 `prompts/document_templates.md`**

法律文书模板。内容必须包含以下 4 个模板：

1. **劳动仲裁申请书模板**：
   - 格式：申请人信息 → 被申请人信息 → 仲裁请求 → 事实与理由 → 证据清单 → 此致 XXX 仲裁委
   - 填充规则：哪些字段从 case.md 提取，哪些从 strategy.md 提取

2. **证据目录模板**：
   - 格式：编号 | 证据名称 | 证据形式 | 证明目的 | 页数 | 原件/复印件
   - 自动从 case.md 的证据清单生成

3. **法律条文引用清单模板**：
   - 格式：序号 | 法条全称 | 具体条款 | 引用目的 | 在申请书中的位置
   - 自动从 legal_knowledge.md 和 strategy.md 提取

4. **催告函 / 要求继续履行劳动合同通知模板**：
   - 格式：致 XXX 公司 → 事实陈述 → 法律依据 → 我方要求 → 期限 → 签名

每个模板都要标注：`{{placeholder}}` 格式的占位符，说明从哪里取值填充。

- [ ] **Step 3: 写 `prompts/merger.md`**

增量 merge 逻辑，用于追加新证据时更新已有文件。内容必须包含：

1. **merge 规则**：
   - 新证据 → 分析属于哪个维度 → 追加到 case.md 对应章节
   - 新证据影响策略判断 → 更新 strategy.md 对应 Layer
   - 两者都有 → 分别更新
   - **原则：只追加增量，不覆盖已有结论**

2. **冲突处理**：
   - 新信息与已有结论矛盾 → 保留两者，标注矛盾，等待用户确认
   - 新信息补充已有结论 → 追加，不覆盖

3. **版本管理触发**：
   - 每次 merge 前先备份当前版本
   - merge 后更新 meta.json 的 version 和 updated_at

4. **输出格式**：变更摘要（新增了什么、修改了什么、建议用户确认什么）

- [ ] **Step 4: 写 `prompts/correction_handler.md`**

对话纠正处理的 prompt。内容必须包含：

1. **纠正意图识别**：识别用户的纠正模式
   - 事实纠正："不对，我的试用期是 6 个月不是 3 个月"
   - 策略纠正："公司还有一条理由没说到"
   - 偏好纠正："我更倾向于协商而不是仲裁"

2. **纠正分类**：判断属于哪个文件的修改
   - 案情事实类 → 更新 case.md
   - 策略方向类 → 更新 strategy.md
   - 阶段变化类 → 更新 meta.json 的 current_phase

3. **Correction 记录格式**：
   ```markdown
   ### Correction #{n}
   - **场景**: {什么情况下发现的错误}
   - **错误信息**: {之前的错误判断}
   - **正确信息**: {用户提供的正确信息}
   - **影响范围**: {这个纠正影响了哪些结论}
   - **时间**: {ISO 时间}
   ```

4. **策略重评规则**：纠正后需要重新评估哪些 Layer

---

### Task 4 [Agent D]: Python 工具脚本

**Files:**
- Create: `D:/workspace/dagong-soul-skill/tools/skill_writer.py`
- Create: `D:/workspace/dagong-soul-skill/tools/version_manager.py`
- Create: `D:/workspace/dagong-soul-skill/tools/wechat_parser.py`
- Create: `D:/workspace/dagong-soul-skill/tools/dingtalk_parser.py`
- Create: `D:/workspace/dagong-soul-skill/tools/feishu_parser.py`
- Create: `D:/workspace/dagong-soul-skill/tools/email_parser.py`
- Create: `D:/workspace/dagong-soul-skill/tools/attendance_parser.py`

- [ ] **Step 1: 写 `tools/skill_writer.py`**

Skill 文件管理工具。支持以下命令行参数：

```bash
# 列出所有案件
python3 tools/skill_writer.py --action list --base-dir ./cases

# 创建案件目录结构
python3 tools/skill_writer.py --action create --slug {slug} --base-dir ./cases

# 更新 meta.json 字段
python3 tools/skill_writer.py --action update-meta --slug {slug} --key {key} --value {value} --base-dir ./cases
```

实现要点：
- `--action list`：扫描 cases/ 下所有 meta.json，输出表格（slug | 公司 | 阶段 | 创建时间）
- `--action create`：创建 `cases/{slug}/` 目录 + 子目录（evidence/contracts, chats, emails, attendance, performance, work-products, disputes, versions）
- `--action update-meta`：读取 meta.json，更新指定字段，写回
- 使用 argparse，返回 JSON 格式输出方便 SKILL.md 解析
- 无第三方依赖，仅用标准库（json, os, argparse, datetime）

- [ ] **Step 2: 写 `tools/version_manager.py`**

版本存档与回滚工具。支持以下命令行参数：

```bash
# 备份当前版本
python3 tools/version_manager.py --action backup --slug {slug} --base-dir ./cases

# 列出历史版本
python3 tools/version_manager.py --action list --slug {slug} --base-dir ./cases

# 回滚到指定版本
python3 tools/version_manager.py --action rollback --slug {slug} --version {version} --base-dir ./cases
```

实现要点：
- `--action backup`：将 case.md + strategy.md + emotion_timeline.md + meta.json 复制到 `versions/{current_version}/`，更新 meta.json 的 version +1
- `--action list`：列出 versions/ 下所有版本目录
- `--action rollback`：将指定版本的内容恢复到主目录
- 自动清理：保留最近 10 个版本，超出则删除最旧的
- 无第三方依赖

- [ ] **Step 3: 写 `tools/wechat_parser.py`**

微信聊天记录解析工具。支持以下命令行参数：

```bash
python3 tools/wechat_parser.py --file {path} --target "{name}" --output {output_path} --format auto
```

实现要点：
- 支持 WeChatMsg 导出的 txt 格式（最常见）
- 支持纯文本粘贴格式（用户手动复制的聊天记录）
- 提取维度：时间、发送者、消息内容、消息类型（文字/图片/语音/系统消息）
- 过滤规则：只保留目标人物的消息 + 你与目标的对话上下文
- 输出格式：结构化文本，按时间排序
- 输出头部包含统计信息（总消息数、时间范围、目标消息数）
- 无第三方依赖（txt/纯文本不需要额外库）

- [ ] **Step 4: 写 `tools/dingtalk_parser.py`**

钉钉聊天记录解析工具。支持以下命令行参数：

```bash
python3 tools/dingtalk_parser.py --file {path} --target "{name}" --output {output_path}
```

实现要点：
- 支持钉钉导出的 txt/CSV 格式
- 支持纯文本粘贴
- 提取维度同 wechat_parser
- 钉钉特有：支持解析"已读"状态、DING 消息
- 无第三方依赖

- [ ] **Step 5: 写 `tools/feishu_parser.py`**

飞书聊天记录 JSON 导出解析工具。支持以下命令行参数：

```bash
python3 tools/feishu_parser.py --file {path} --target "{name}" --output {output_path}
```

实现要点：
- 支持飞书消息导出的 JSON 格式（官方导出格式）
- 解析飞书 JSON 结构（items 数组 → 每条消息的 sender/body/create_time）
- 提取维度同 wechat_parser
- 过滤：只保留目标人物消息 + 对话上下文
- 无第三方依赖（json 为标准库）

- [ ] **Step 6: 写 `tools/email_parser.py`**

邮件解析工具。支持以下命令行参数：

```bash
python3 tools/email_parser.py --file {path} --target "{name}" --output {output_path}
```

实现要点：
- 支持 .eml 格式（单封邮件）
- 支持 .mbox 格式（邮件归档）
- 使用标准库 `email` 模块解析
- 提取：发件人、收件人、日期、主题、正文（纯文本优先，HTML 转 plaintext）
- 过滤：只保留与目标人物相关的邮件（发件人或收件人匹配）
- 无第三方依赖（email 为标准库）

- [ ] **Step 7: 写 `tools/attendance_parser.py`**

考勤记录解析工具。支持以下命令行参数：

```bash
python3 tools/attendance_parser.py --file {path} --output {output_path}
```

实现要点：
- 支持 CSV 格式（最常见的考勤导出格式）
- 支持纯文本粘贴（表格复制）
- 提取：日期、上班打卡、下班打卡、状态（正常/迟到/早退/缺卡/休息）
- 统计：总出勤天数、迟到次数、早退次数、缺卡次数、加班时长估算
- 输出：结构化考勤摘要 + 月度统计
- 无第三方依赖（csv 为标准库）

---

### Task 5 [Agent E]: 项目文档

**Files:**
- Create: `D:/workspace/dagong-soul-skill/README.md`
- Create: `D:/workspace/dagong-soul-skill/README_EN.md`
- Create: `D:/workspace/dagong-soul-skill/requirements.txt`

- [ ] **Step 1: 写 `requirements.txt`**

内容极简（目前所有工具只用标准库，无第三方依赖）：
```
# 打工魂·不灭.skill — Python 依赖
# 目前所有工具仅使用 Python 标准库，无需额外安装
# Python 3.9+
```

- [ ] **Step 2: 写 `README.md`**

中文 README，参考同事.skill 的风格。必须包含：

1. **头部**：项目名 + slogan + 徽章（MIT License / Python 3.9+ / Claude Code / AgentSkills）
2. **痛点描述**（3-4 行引发共鸣）：
   - 试用期被通知不通过，不知道怎么应对？
   - HR 劝你主动离职，说"这样不影响背调"？
   - 想维权但不知道怎么收集证据、引用什么法律？
   - **留下你的打工魂。**
3. **产品描述**：一句话概括 + 功能亮点（5-6 个）
4. **安装**（Claude Code + 全局安装两种方式）
5. **使用**：`/create-dagong-soul` 入口 + 管理命令表格
6. **功能特性**：
   - 生成内容结构（案情档案 + 维权策略）
   - 阶段感知策略路由
   - 代价计算器
   - 情绪时间线
   - HR 对抗模拟
   - 法律文书一键生成
   - 进化机制（追加/纠正/版本管理）
   - 多公司支持
7. **数据来源支持表**
8. **安全边界**
9. **项目结构**
10. **致敬**：致敬同事.skill 和前任.skill 的开源精神
11. **同系列项目**：列出同事.skill 和前任.skill 的链接
12. **MIT License**

- [ ] **Step 3: 写 `README_EN.md`**

英文版 README，与中文版内容完全对应，适当调整英语表达习惯。

---

## Phase 2: 串行开发（依赖 Phase 1 全部完成）

---

### Task 6 [Agent F]: SKILL.md 主入口（编排层）

**依赖：** Task 1-5 全部完成（需要知道所有 prompts 和 tools 的确切接口）

**Files:**
- Create: `D:/workspace/dagong-soul-skill/SKILL.md`

- [ ] **Step 1: 写 SKILL.md frontmatter + 基础信息**

SKILL.md 是整个项目的入口。结构必须遵循 AgentSkills 标准：

```yaml
---
name: create-dagong-soul
description: "打工魂·不灭 — 把试用期工作证据蒸馏成 AI 维权顾问..."
argument-hint: "[company-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---
```

- [ ] **Step 2: 写触发条件**

定义所有触发词：
- `/create-dagong-soul` — 创建新案件
- `/list-cases` — 列出所有案件
- 进化模式触发："我有新证据" / "不对" / "公司说" / "模拟对抗"

- [ ] **Step 3: 写工具使用规则表**

参考同事.skill 的格式，列出所有工具映射：
- 读取 PDF/图片 → Read
- 解析微信 → Bash python3 ${CLAUDE_SKILL_DIR}/tools/wechat_parser.py
- 解析钉钉 → Bash python3 ${CLAUDE_SKILL_DIR}/tools/dingtalk_parser.py
- ...（所有 7 个工具）
- 写入文件 → Write/Edit
- 版本管理 → Bash python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py
- 案件管理 → Bash python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py

- [ ] **Step 4: 写主流程（Step 1-5）**

完整定义创建新案件 Skill 的 5 步流程：
- Step 1: 基础信息录入（引用 intake.md）
- Step 2: 原材料导入（列出所有数据源选项 + 对应工具命令）
- Step 3: 自动分析（引用 case_analyzer.md + strategy_analyzer.md + emotion_tracker.md）
- Step 4: 生成预览（展示摘要 + 用户确认）
- Step 5: 写入文件（skill_writer.py 创建目录 + Write 写入 case.md/strategy.md/emotion_timeline.md/meta.json/SKILL.md）

- [ ] **Step 5: 写生成案件 SKILL.md 的模板**

这是最关键的部分——定义生成的案件 SKILL.md 的结构。必须包含：
- frontmatter（name: {slug}, description, user-invocable: true）
- 身份定义（你是{用户}在{公司}的打工魂，同时也是高级劳动法律师）
- PART A：案情档案（引用 case.md 全文）
- PART B：维权策略（引用 strategy.md 全文）
- 情绪时间线（引用 emotion_timeline.md）
- 内置法律知识（引用 legal_knowledge.md 核心法条）
- 运行规则（阶段感知 + 用户意愿优先 + 模拟对抗 + 进化模式）

- [ ] **Step 6: 写进化模式**

- 追加证据进化（引用 merger.md）
- 对话纠正进化（引用 correction_handler.md）
- 版本管理（引用 version_manager.py）

- [ ] **Step 7: 写管理命令**

- `/list-cases` → skill_writer.py --action list
- `/dagong-rollback {slug} {version}` → version_manager.py --action rollback
- `/delete-case {slug}` → 确认后 rm -rf cases/{slug}

- [ ] **Step 8: 写特殊模式**

- 对抗模拟模式（引用 hr_tactics.md）
- 文书生成模式（引用 document_templates.md）
- 代价计算器模式（引用 cost_calculator.md）
- 阶段路由（引用 phase_router.md）

---

## Phase 3: 集成验证

---

### Task 7 [Agent G]: 集成测试 + 首次提交

**依赖：** Task 6 完成

**Files:**
- Verify: `D:/workspace/dagong-soul-skill/` 下所有文件

- [ ] **Step 1: 文件完整性检查**

验证所有文件存在且非空：
```
D:/workspace/dagong-soul-skill/
├── SKILL.md
├── README.md
├── README_EN.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── prompts/ (13 个 .md 文件)
├── tools/ (7 个 .py 文件)
├── cases/ (空目录)
└── docs/PRD.md
```

- [ ] **Step 2: Python 语法检查**

```bash
cd D:/workspace/dagong-soul-skill
python3 -m py_compile tools/skill_writer.py
python3 -m py_compile tools/version_manager.py
python3 -m py_compile tools/wechat_parser.py
python3 -m py_compile tools/dingtalk_parser.py
python3 -m py_compile tools/feishu_parser.py
python3 -m py_compile tools/email_parser.py
python3 -m py_compile tools/attendance_parser.py
```

- [ ] **Step 3: Python 工具功能测试**

```bash
# 测试 skill_writer
python3 tools/skill_writer.py --action list --base-dir ./cases

# 测试 version_manager
python3 tools/version_manager.py --action list --slug test --base-dir ./cases
```

- [ ] **Step 4: SKILL.md frontmatter 检查**

验证 SKILL.md 的 YAML frontmatter 格式正确：
- name 字段存在
- description 字段存在
- user-invocable: true
- allowed-tools 列出 Read, Write, Edit, Bash

- [ ] **Step 5: 首次 Git 提交**

```bash
cd D:/workspace/dagong-soul-skill
git add -A
git commit -m "feat: 打工魂·不灭.skill v1.0 — 完整实现

- 创建器 SKILL.md 主流程（信息录入→证据导入→分析→生成）
- 13 个 prompt 模板（法律知识、案情分析、策略、阶段路由等）
- 7 个 Python 工具（解析器、文件管理、版本管理）
- 特色功能：情绪时间线、代价计算器、阶段感知、HR 对抗模拟
- 中英文 README

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 并行执行摘要

| Agent | 任务 | 文件数 | 依赖 | 阶段 |
|-------|------|--------|------|------|
| Agent A | 法律+策略 prompts | 5 | 无 | Phase 1 |
| Agent B | 案情分析 prompts | 4 | 无 | Phase 1 |
| Agent C | 特殊功能+进化 prompts | 4 | 无 | Phase 1 |
| Agent D | Python 工具脚本 | 7 | 无 | Phase 1 |
| Agent E | 项目文档 | 3 | 无 | Phase 1 |
| Agent F | SKILL.md 编排层 | 1 | Task 1-5 | Phase 2 |
| Agent G | 集成测试+提交 | 0 (验证) | Task 6 | Phase 3 |

**总文件数：** 24 个文件（13 prompts + 7 tools + SKILL.md + README.md + README_EN.md + requirements.txt + .gitignore + LICENSE + docs/PRD.md）

**预计加速：** Phase 1 的 5 个 Agent 并行，相比串行开发节省约 60-70% 时间。
