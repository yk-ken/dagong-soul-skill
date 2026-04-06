# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指导。

## 项目概述

**打工魂·不灭.skill**（dagong-soul-skill）是一个 Claude Code Skill，帮助试用期被劝退的打工人收集证据、分析案情、生成维权策略。用户运行 `/create-dagong-soul` 创建案件后，skill 自动分析材料并生成独立的案件 Skill（证据库 + AI 律师顾问）。

## 架构

```
SKILL.md              ← 创建器入口。用户运行 /create-dagong-soul 时 Claude 读取此文件
  │                     路由到创建/列表/回滚/删除/进化操作
  │
  ├── prompts/         ← 分析模板（intake、case_analyzer、strategy_analyzer 等 13 个）
  ├── tools/           ← Python 工具（解析器 5 个 + 文件管理 + 版本管理）
  ├── cases/           ← 生成的案件 Skills（gitignored）
  └── docs/            ← PRD + 实施计划
```

## Git 提交规范

- **提交者统一为 `yk-ken <yk-ken@users.noreply.github.com>`**，禁止使用其他用户名或邮箱
- 当前 git 配置应保持：`user.name=yk-ken`、`user.email=yk-ken@users.noreply.github.com`

## 修改指南

- prompts/ 下的文件为 Markdown prompt 模板，直接编辑即可
- tools/ 下的 Python 脚本仅使用标准库，无第三方依赖
- SKILL.md 通过 `${CLAUDE_SKILL_DIR}/prompts/<name>.md` 引用模板
- SKILL.md 通过 Bash 调用 `python3 ${CLAUDE_SKILL_DIR}/tools/<name>.py` 执行工具
- cases/ 目录为运行时生成的用户数据，已 gitignored
