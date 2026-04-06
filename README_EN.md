<div align="center">

# dagong-soul.skill

> *"Keep your working soul alive."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Told you didn't pass probation? HR pressuring you to "resign voluntarily"?<br>
Don't know what evidence to collect, which laws apply, or how to negotiate?<br>
Feel powerless against professional HR tactics?<br>

**Keep your working soul alive.**

<br>

Take everything from your probation period — work records, attendance logs, chat histories, emails, deliverables —<br>
and distill it into an **AI legal advisor**. It's your evidence vault, and your personal senior attorney avatar for this stage.

[Features](#features) · [Installation](#installation) · [Usage](#usage) · [Examples](#examples) · [中文](README.md)

</div>

---

### 🌟 Related Projects

- **[colleague.skill](https://github.com/titanwings/colleague-skill)** — Distill a colleague into an AI Skill
- **[ex.skill](https://github.com/therealXiaomanChu/ex-skill)** — Distill an ex-partner into an AI Skill
- **dagong-soul.skill** — Distill yourself into a legal rights advisor

Colleague left? Use colleague.skill. Ex left? Use ex.skill. HR pushing you to resign? Use **dagong-soul.skill**.

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Case Profile** | Automatically extract employment relationship, work performance, evidence list, and timeline from materials |
| 2 | **Rights Protection Strategy** | Generate targeted legal strategies (three branches: negotiate / refuse resignation / arbitration) |
| 3 | **Stage Awareness** | Auto-match strategy based on current progress (being talked to → pressured → notified → terminated → arbitrating → closed) |
| 4 | **HR Sparring Simulation** | Practice negotiations with a virtual HR, with common tactics breakdown and counter-strategies |
| 5 | **Cost Calculator** | Quantitative comparison of negotiation vs. arbitration (compensation / time / risk / emotional cost) |
| 6 | **Emotion Timeline** | Track psychological state changes and company pressure behavior patterns |
| 7 | **Legal Document Generation** | One-click generation of arbitration applications, evidence catalogs, and legal citation lists |
| 8 | **Multi-company Support** | Each company gets an independent case file, completely isolated |

## Supported Data Sources

| Source | Format | Processing |
|--------|--------|------------|
| WeChat chat history | WeChatMsg / LiHen export | Python parser |
| DingTalk chat history | Screenshots / exports | Python parser |
| Feishu (Lark) messages | JSON export | Python parser |
| Email | .eml / .mbox | Python parser |
| Employment contract | Photo / PDF | Read tool |
| Attendance records | Screenshots / CSV | Python parser |
| Pay stubs | Photo / PDF / screenshot | Read tool |
| Performance reviews | Screenshots / PDF | Read tool |
| Work deliverables | Documents / screenshots | Read / verbal |
| Company policies | PDF / screenshots | Read tool |
| Bank statements | PDF / screenshots | Read tool |
| Verbal narration | Plain text | Direct use |

### Recommended WeChat Export Tools

These are independent open-source projects. This repository does not include their code — only parsers adapted to their export formats:

| Tool | Platform | Description |
|------|----------|-------------|
| [WeChatMsg](https://github.com/LC044/WeChatMsg) | Windows | WeChat chat export, multiple formats |
| [PyWxDump](https://github.com/xaoyaoo/PyWxDump) | Windows | WeChat database decryption and export |
| [LiHen](https://github.com/greyovo/留痕) | macOS | WeChat chat export (recommended for Mac) |

---

## Installation

### Claude Code

> **Important**: Claude Code looks for skills in `.claude/skills/` under the **git repository root**. Make sure you're in the right directory.

```bash
# Install into current project (run from git repo root)
mkdir -p .claude/skills
git clone https://github.com/yk-ken/dagong-soul-skill .claude/skills/create-dagong-soul

# Or install globally (available in all projects)
git clone https://github.com/yk-ken/dagong-soul-skill ~/.claude/skills/create-dagong-soul
```

### Dependencies (Optional)

```bash
pip3 install -r requirements.txt
```

> No additional dependencies required — all tools use only the Python standard library.

---

## Usage

In Claude Code, type:

```
/create-dagong-soul
```

Follow the prompts to enter the company name, hire date, and current situation, then choose to upload materials or narrate verbally. All fields are skippable — you can add more later.

Once created, use `/{slug}` to invoke the case Skill.

### Management Commands

| Command | Description |
|---------|-------------|
| `/create-dagong-soul` | Create a new case |
| `/list-cases` | List all cases |
| `/{slug}` | View case profile + legal strategy |
| `/{slug}-sim` | HR sparring simulation |
| `/{slug}-docs` | Generate legal documents |
| `/{slug}-cost` | Cost calculator |
| `/case-rollback {slug} {version}` | Roll back to a previous version |
| `/delete-case {slug}` | Delete a case |

---

## Examples

> Input: `A tech company, started Jan 2025, 3-month probation, told at end of March that I didn't meet requirements`

### Example 1: First Consultation

```
You          ❯ I was told I didn't pass probation. The company says I don't meet the hiring criteria and wants me to resign voluntarily.

dagong-soul  ❯ Don't panic, and don't sign anything yet. Let me break down your situation:

              Under Article 39 of the Labor Contract Law, terminating an employee during probation
              for "not meeting hiring criteria" requires three conditions to be met simultaneously:

              1. The hiring criteria were clearly communicated to you at onboarding (with written records)
              2. The company has objective evidence that you failed to meet those criteria
              3. The termination decision was made within the probation period

              Did you sign any "probation hiring criteria confirmation" or similar document when you joined?

You          ❯ No, I only signed an employment contract that stated a 3-month probation period.

dagong-soul  ❯ That's the first point in your favor.

              Without written confirmation of specific hiring criteria, the company's claim of
              "not meeting criteria" is very difficult to uphold in arbitration. HR says "not meeting"
              but can't produce criteria you signed off on — that's a failure of proof on their part.

              A few key follow-up questions:
              - How many people were present during the meeting? Did you record it?
              - Did they give you any written notice?
              - What's your salary structure and social insurance situation?

You          ❯ HR and my direct manager were there — two people. I didn't record it. No written notice either, just verbal.

dagong-soul  ❯ Follow these recommendations, in priority order:

              【Immediate Actions】
              1. From now on, communicate everything in writing (WeChat/DingTalk), avoid verbal-only
              2. If called into another meeting, start a voice recording on your phone beforehand (pocket is fine)
              3. Do NOT sign any "voluntary resignation" or "mutual termination" documents

              【Evidence Preservation】
              4. Screenshot your attendance records and work deliverable submission records
              5. Export chat histories with your manager/HR
              6. Gather anything that proves your work performance (weekly reports, deliverable confirmations, etc.)

              You can upload any existing materials to me now, and I'll do a comprehensive evidence assessment.
```

### Example 2: HR Sparring Simulation

```
You          ❯ Start HR sparring simulation

dagong-soul  ❯ HR sparring simulation activated. I will play your HR, using common pressure tactics.
              Practice your responses — I'll evaluate each round and provide advice.
              Type "end simulation" to exit.

              -------

              🏢 HR (Simulated):
              "Hey, have a seat. I wanted to chat with you about your probation assessment.
              As you know, the team has some concerns about your performance — your manager
              feels there's a gap between expectations and where you are. The company wants to
              give you a graceful exit, though. If you resign voluntarily, it'll look better
              on your record than being terminated during probation. Just something to think about."

You          ❯ I believe my performance has been satisfactory. Could you be specific about what I didn't meet?

dagong-soul  ❯ 📊 Response Evaluation: Excellent

              This counter-question is very well played:
              - It shifts the burden of proof back to the company (they say "not meeting" — specifically what?)
              - No emotional reaction, staying calm and professional
              - Implicitly signals you won't accept vague "not meeting" claims

              💡 Things to watch for:
              - If HR can't give specific examples, their "not meeting criteria" claim lacks basis
              - If HR produces a performance evaluation, check whether you signed it
              - HR may pivot to "the company is doing this for your benefit" — don't let them set the frame

              -------

              🏢 HR (Simulated):
              "Specifics... your manager says you were slow to ramp up and didn't integrate well with the team.
              But that's not the point — the point is the company is offering you a clean exit.
              Think about it: if your record says 'terminated during probation,' how's that going to look
              in background checks at your next job? We'll write 'personal reasons' — everybody wins."

You          ❯ I need some time to think about this. I can't give you an answer right now.

dagong-soul  ❯ 📊 Response Evaluation: Good

              Not rejecting outright but not agreeing either — a fundamentally sound strategy.
              "I need to think" buys you time.

              💡 Improvement tips:
              - Be more decisive: "I'll consider this carefully and get back to you"
              - Avoid a hesitant tone that might signal you're wavering
              - After the meeting, immediately document everything (time, place, attendees, what was said)

              Regarding HR's "background check" scare tactic, here's the breakdown:
              - This is a classic pressure tactic exploiting information asymmetry to create fear
              - In reality, the reason for departure is rarely a dealbreaker in background checks
              - "Voluntary resignation" means giving up all legal rights — the loss far outweighs any "embarrassment"
```

### Example 3: Evidence Augmentation

```
You          ❯ I got a screenshot of my probation performance review — my manager rated me B (meets expectations)

dagong-soul  ❯ This is a critical piece of evidence. Let me analyze the impact:

              📋 Evidence Assessment:

              【Direct Impact】
              - "B (meets expectations)" directly contradicts the company's "not meeting hiring criteria" claim
              - If this review came from the company's official evaluation system, it carries strong weight in arbitration
              - Timeline check needed: was this evaluation done before or after the termination meeting?

              【Strategic Impact】
              1. If evaluation was done BEFORE the meeting → The company knew you met expectations but terminated
                 anyway → illegal termination → you can claim 2N compensation (2 months' salary)
              2. If evaluation was done AFTER the meeting → Possibly retroactive — need to verify evaluation
                 process compliance (did you sign it? were criteria published in advance?)

              【Recommended Next Steps】
              - Confirm whether the evaluation has your manager's signature or is a system screenshot
              - If there was an email notification, save the full email (including sender, timestamp, headers)
              - When screenshotting, make sure the system interface shows timestamps and URLs

              Want to send me the screenshot so I can update your case profile and strategy?

You          ❯ Sent. I also have DingTalk messages where my manager praised my work.

dagong-soul  ❯ Even better — these two pieces of evidence complement each other:

              1. Official performance review (B) → Proves the company's formal assessment found you satisfactory
              2. Manager's DingTalk praise → Proves your direct supervisor's subjective evaluation was also positive

              Together, it becomes nearly impossible for the company to prove "not meeting hiring criteria" in arbitration.

              I've updated your case file:
              - Evidence list: 2 new items added, X total evidence items
              - Strategy adjusted from "negotiation first" to "arbitration has strong prospects"
              - Estimated compensation: ¥X (N+1 or 2N scenario)

              Next steps:
              If the company hasn't sent a formal written termination notice yet, your options are:
              A. Continue working normally, wait for written notice (stronger evidence)
              B. Proactively negotiate with HR, using the evaluation results as leverage

              Which direction are you leaning?
```

---

## Generated Skill Structure

Each case generates the following files:

```
cases/{slug}/
├── SKILL.md                 # Skill entry point (official frontmatter)
├── case.md                  # Case profile (employment relationship, timeline, evidence list)
├── strategy.md              # Legal strategy (three branches: negotiate / refuse / arbitrate)
├── emotion_timeline.md      # Emotion timeline (psychological state + company pressure patterns)
├── meta.json                # Metadata (company name, stage, version number)
├── evidence/                # Raw evidence files (chat logs, screenshots, documents)
└── versions/                # Historical version archives (rollback supported)
```

Execution logic: `Receive question → Detect current stage → Match legal strategy → Invoke legal knowledge + evidence vault → Output recommendation`

---

## Safety Boundaries

1. **For Reference Only**: Legal analysis and strategic advice provided by this tool do not constitute formal legal counsel and cannot replace professional attorney consultation.
2. **No Malicious Arbitration**: Use this tool only when your legitimate rights have been infringed. Baseless or malicious claims are not supported.
3. **Privacy Protection**: All data is stored locally only — nothing is uploaded to any cloud service. Case data supports encrypted storage.
4. **Emotional Support**: Being terminated during probation is a common workplace experience — it is not your fault. If you experience persistent anxiety or depression, please seek professional counseling.
5. **No Fabricated Evidence**: This tool only helps organize and analyze existing materials. It will never assist in fabricating or tampering with evidence.

---

## Important Notes

- **Material quality determines strategy quality**: chat records + work documents > verbal narration only
- Recommended collection priority: **termination notice / meeting records** > **employment contract** > **work deliverables** > **attendance records**
- Arbitration statute of limitations is 1 year — the earlier you collect evidence, the better
- This project does not replace an attorney. For significant disputes, consult a professional lawyer.

---

## Acknowledgements

The architecture of this project was inspired by **[colleague.skill](https://github.com/titanwings/colleague-skill)** (by [titanwings](https://github.com/titanwings)) and **[ex.skill](https://github.com/therealXiaomanChu/ex-skill)** (by [therealXiaomanChu](https://github.com/therealXiaomanChu)). Colleague.skill pioneered the "distill a person into an AI Skill" dual-layer architecture, ex.skill adapted it for romantic relationships, and dagong-soul.skill adapts it for labor rights protection. Hats off to the original authors for their creativity and open-source spirit.

---

<div align="center">

MIT License © [yk-ken](https://github.com/yk-ken)

</div>
