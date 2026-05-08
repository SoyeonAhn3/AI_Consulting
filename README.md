🌐 [한국어](./README_ko.md) | [English](./README.md)

# MS Work Automation Consulting CLI Agent

> A CLI agent that analyzes and recommends Microsoft ecosystem work automation solutions, compares opinions from 3 AI models, and generates final deliverable files.

## Overview

Organizations spend significant time manually evaluating which MS tools fit their automation needs. This CLI agent, built entirely on Claude Code skills, accepts free-form work automation requirements and delivers structured consulting reports with risk-assessed solution recommendations.

It operates in two modes: **Quick** (Claude solo analysis) and **Deep** (3-AI independent proposals with cross-review), producing text reports, Excel spreadsheets, and Power Automate flow designs.

https://github.com/user-attachments/assets/bdbe956b-0d4d-4b26-9e3f-67c9856180af

## Table of Contents

- [Workflow](#workflow)
- [Technology Stack](#technology-stack)
- [AI Components](#ai-components)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Current Status](#current-status)
- [Skill List](#skill-list)
- [Documentation](#documentation)
- [Limitations](#limitations)
- [Future Plans](#future-plans)

## Workflow

```
[User Input] → Requirement Parsing → Scope Gate → Mode Selection (Quick/Deep)
     → AI Analysis & Risk Evaluation → User Feedback (re-consultation available)
     → MS Support Verification → Output Generation (.txt / .xlsx / PA Flow)
```

- **Quick**: Claude solo free-form analysis → blocklist check → two-pass risk evaluation → recommendation
- **Deep**: 3 AI (Claude + Codex + Gemini) independent proposals → Orchestrator cross-review → common strengths/risks extraction → two-pass risk evaluation → recommendation

## Technology Stack

| Technology | Role | Why |
|---|---|---|
| Claude Code Skills | Core runtime & skill engine | Skill-based architecture without traditional code; LLM handles analysis inline |
| Claude (Anthropic) | Primary AI / Orchestrator | Drives risk evaluation, solution analysis, and report generation |
| Codex CLI (OpenAI) | Deep mode AI #2 | Independent solution proposals for cross-AI comparison |
| Gemini CLI (Google) | Deep mode AI #3 | Independent solution proposals for cross-AI comparison |
| JSONL | Log format | Lightweight, append-only, date-partitioned for session tracking |
| Python (openpyxl) | Excel template processing | Placeholder-based fill with auto row-height adjustment |
| WebSearch | MS product verification | Real-time validation against MS Learn documentation |

## AI Components

| Component | What AI Handles | What Rules Handle |
|---|---|---|
| Requirement Parsing | Clarification questions, confidence scoring | Domain keyword matching, MS product hint extraction |
| Solution Proposal | Free-form MS solution recommendations | Blocklist filtering, scope gate validation |
| Risk Evaluation | Two-pass risk assessment per solution | Risk category tagging (security/license/operations) |
| Cross-Review (Deep) | Orchestrator generates expected rebuttals per AI | Common strengths/risks extraction logic |
| MS Verification | Impact assessment of WebSearch results | Evidence Summary compression (4-field format) |
| Output Generation | Content composition per schema | File naming, encoding rules, structure validation |

- **Model selection**: Quick uses Claude only. Deep runs Codex CLI and Gemini CLI alongside Claude, with fallback to 2-AI or Claude-only if external CLIs fail.
- **AI failure handling**: JSON parse failure triggers one normalization retry, then FALLBACK event logging and exclusion.
- **AI results are advisory**: final recommendations require user confirmation before output generation.

## Quick Start

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- [Codex CLI](https://github.com/openai/codex) (optional, for Deep mode)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) (optional, for Deep mode)
- Python 3.8+ with `openpyxl` (for Excel report generation)

### Setup

```bash
git clone https://github.com/Ihatespeedlimit/AI_Consulting.git
cd AI_Consulting
```

### Usage

All features run as Claude Code skills:

```bash
# Start a full consulting session
/consult

# Parse requirements only
/parse-requirement

# Multi-AI discussion on a topic
/ai-multi-discussion [topic]

# Generate Word user manual
/gen-manual

# Archive old logs (4+ weeks)
/archive

# Record dev log
/dev-log
```

### Environment Variables

```bash
# Required for Excel report generation
pip install openpyxl
```

No API keys or `.env` file required — AI model access is handled through the respective CLI tools.

## Project Structure

```
AI_Consulting/
├── README.md                       # English
├── README_ko.md                    # Korean
├── UserRequirement_Draft.md        # Requirements draft
│
├── .claude/
│   ├── settings.json               # Claude Code settings
│   ├── hooks/guard_output.py       # Output folder write protection
│   └── skills/                     # Claude Code skill definitions (14 skills)
│       ├── consult/                # Main orchestrator
│       ├── parse-requirement/      # Requirement parsing
│       ├── ai-score-compare/       # Solution evaluation engine
│       ├── ms-solution-recommend/  # MS solution reference data
│       ├── generate-output/        # Output file generation
│       ├── ai-analysis/            # AI call event logging
│       ├── dev-log/                # Development logging
│       ├── test-log/               # Test observation logging
│       ├── ai-multi-discussion/    # Multi-AI discussion framework
│       ├── gen-manual/             # User manual generation
│       ├── readme-update/          # README auto-update
│       ├── phase-doc/              # Phase documentation
│       ├── github-push/            # Git push automation
│       └── skill-template/         # Skill standard template
│
├── Phase/                          # Phase development docs
│   ├── Phase1_기반구축.md
│   ├── Phase2_핵심엔진.md
│   ├── Phase3_산출물생성.md
│   ├── Phase4_품질검증.md
│   └── Phase5_PA플로우설계.md
│
├── Word_Template/                  # Excel report tools
│   ├── 컨설팅결과_보고서_템플릿.xlsx  # KR+EN 2-sheet template
│   └── fill_excel_template.py      # Placeholder fill + auto row height
│
├── references/                     # Dev reference docs
├── manuals/                        # Generated user manuals
├── assets/                         # Media files
│
├── logs/                           # Auto-generated (gitignored)
│   ├── session/                    # Session state files
│   ├── ai_analysis/                # AI call event logs
│   ├── dev/                        # Development logs
│   ├── test/                       # Test observation logs
│   └── PA_log/                     # PA flow blueprints
│
├── output/                         # Consulting outputs
│   ├── Archive/                    # .txt and .xlsx reports
│   └── PA_Flow/                    # PA flow design files
│
└── archive/                        # History archive
    ├── Consulting_Summary.csv      # Cumulative consulting summary
    └── raw/                        # Cold storage (pre-deletion)
```

## Current Status

| Phase | Description | Status | Deliverable |
|---|---|---|---|
| Phase 1 — Foundation | Logging, parsing, session management | ✅ Done | dev-log, ai-analysis, parse-requirement, 8 base skills |
| Phase 2 — Core Engine | Quick/Deep evaluation engine | ✅ Done | Two-pass risk evaluation, AI cross-review, blocklist |
| Phase 3 — Output Generation | Report generation + flow integration | ✅ Done | generate-output (.txt), consult orchestrator |
| Phase 4 — Quality & Extension | Multilingual, scope gate, Excel, ROI, token optimization | ✅ Done | en/ko/en+ko support, Excel reports, ROI estimation, 4 rounds of token optimization |
| Phase 5 — PA Flow Design | Power Automate flow design generation | ✅ Done | PA flow diagrams, Copilot prompts, exception checklists |

Not started: `generate-test-list`, Notion integration, Web UI (on hold)

## Skill List

### General — Portable to other projects

| Skill | Description |
|---|---|
| `dev-log` | Error/change/info event JSONL logging |
| `ai-analysis` | AI call, scoring, session state event logging |
| `readme-update` | README auto-update |
| `ai-multi-discussion` | 3-AI opinion collection, comparison, consensus |
| `archive` | 4-week log archive + CSV summary |
| `test-log` | Test observation logging |
| `phase-doc` | Phase development documentation |
| `skill-template` | Skill standard template |
| `gen-manual` | Word user manual generation |

### Project-specific — Specialized for this project

| Skill | Description |
|---|---|
| `consult` | Full-flow orchestrator (parsing → analysis → feedback → output) |
| `parse-requirement` | Requirement structuring + session_id generation |
| `ai-score-compare` | Quick/Deep two-pass risk evaluation → recommendation |
| `ms-solution-recommend` | Deep mode reference data provider (solutions.md) |
| `generate-output` | Output file generation (.txt / .xlsx) |

## Documentation

| Document | Description |
|---|---|
| [Phase1_기반구축.md](./Phase/Phase1_기반구축.md) | Foundation — logging, parsing, session |
| [Phase2_핵심엔진.md](./Phase/Phase2_핵심엔진.md) | Core engine — Quick/Deep evaluation |
| [Phase3_산출물생성.md](./Phase/Phase3_산출물생성.md) | Output generation + flow integration |
| [Phase4_품질검증.md](./Phase/Phase4_품질검증.md) | Quality — multilingual, Excel, ROI, optimization |
| [Phase5_PA플로우설계.md](./Phase/Phase5_PA플로우설계.md) | PA flow design generation |
| [skill-map.md](./references/skill-map.md) | Skill interconnection diagram |
| [User Manual (.docx)](./manuals/20260316_MS업무자동화컨설팅_매뉴얼.docx) | End-user manual |

## Limitations

- **CLI only**: No web UI — all interaction through Claude Code terminal
- **No test suite**: Manual verification only; golden test cases planned after sufficient user testing
- **External CLI dependency**: Deep mode requires Codex CLI and Gemini CLI installed separately
- **MS ecosystem scope**: Only recommends Microsoft product-based solutions; non-MS automation is out of scope
- **Local execution**: No cloud deployment or multi-user support

## Future Plans

- `generate-test-list`: Automated user test checklist generation
- Notion integration: Publish consulting outputs directly to Notion pages
- Web UI: Under consideration after CLI stability is confirmed

---

<p align="center">Made with AI-assisted development</p>
