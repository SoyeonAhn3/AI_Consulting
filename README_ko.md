🌐 [한국어](./README_ko.md) | [English](./README.md)

# MS 업무자동화 솔루션 컨설팅 CLI 에이전트

> Microsoft 생태계 내 업무 자동화 솔루션을 분석·제안하고, AI 3종 의견 비교 및 최종 산출물 파일을 생성하는 CLI 에이전트.

## 개요

조직에서 업무 자동화에 적합한 MS 도구를 평가하는 데 많은 시간과 전문 지식이 필요합니다. 이 CLI 에이전트는 Claude Code 스킬 기반으로 구축되어, 자유 형식의 업무 자동화 요구사항을 입력받아 리스크가 평가된 솔루션 권고안이 포함된 구조화된 컨설팅 보고서를 제공합니다.

**Quick** 모드(Claude 단독 분석)와 **Deep** 모드(AI 3종 독립 제안 + 상호 리뷰) 두 가지로 운영되며, 텍스트 보고서, Excel 스프레드시트, Power Automate 플로우 설계를 산출합니다.

https://github.com/user-attachments/assets/bdbe956b-0d4d-4b26-9e3f-67c9856180af

## 목차

- [동작 흐름](#동작-흐름)
- [기술 스택](#기술-스택)
- [AI 구성 요소](#ai-구성-요소)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [현재 상태](#현재-상태)
- [스킬 목록](#스킬-목록)
- [문서](#문서)
- [한계점](#한계점)
- [향후 계획](#향후-계획)

## 동작 흐름

```
[사용자 입력] → 요구사항 파싱 → 적합성 판정 → 모드 선택 (Quick/Deep)
     → AI 분석 & 리스크 평가 → 사용자 피드백 (재컨설팅 가능)
     → MS 지원 확인 → 산출물 생성 (.txt / .xlsx / PA 플로우)
```

- **Quick**: Claude 단독 자유 분석 → blocklist 체크 → 2패스 리스크 평가 → 권고안
- **Deep**: AI 3종(Claude + Codex + Gemini) 독립 제안 → Orchestrator 상호 리뷰 → 공통 강점/리스크 추출 → 2패스 리스크 평가 → 권고안

## 기술 스택

| Technology | Role | Why |
|---|---|---|
| Claude Code Skills | 코어 런타임 & 스킬 엔진 | 전통적 코드 없이 스킬 기반 아키텍처; LLM이 분석을 인라인 처리 |
| Claude (Anthropic) | 주 AI / Orchestrator | 리스크 평가, 솔루션 분석, 보고서 생성 담당 |
| Codex CLI (OpenAI) | Deep 모드 AI #2 | 교차 AI 비교를 위한 독립 솔루션 제안 |
| Gemini CLI (Google) | Deep 모드 AI #3 | 교차 AI 비교를 위한 독립 솔루션 제안 |
| JSONL | 로그 포맷 | 경량, 추가 전용, 세션 추적을 위한 날짜별 파티셔닝 |
| Python (openpyxl) | Excel 템플릿 처리 | 플레이스홀더 기반 채우기 + 행 높이 자동 조정 |
| WebSearch | MS 제품 검증 | MS Learn 문서 기반 실시간 검증 |

## AI 구성 요소

| 구성 요소 | AI 처리 영역 | 규칙 기반 처리 영역 |
|---|---|---|
| 요구사항 파싱 | 보완 질문, 신뢰도 산정 | 도메인 키워드 매칭, MS 제품 힌트 추출 |
| 솔루션 제안 | MS 솔루션 자유 추천 | Blocklist 필터링, 적합성 게이트 검증 |
| 리스크 평가 | 솔루션별 2패스 리스크 평가 | 리스크 카테고리 태깅 (보안/라이선스/운영) |
| 상호 리뷰 (Deep) | Orchestrator가 AI별 예상 반론 생성 | 공통 강점/리스크 추출 로직 |
| MS 지원 확인 | WebSearch 결과 영향 평가 | Evidence Summary 압축 (4필드 형식) |
| 산출물 생성 | 스키마 기반 콘텐츠 구성 | 파일명, 인코딩 규칙, 구조 검증 |

- **모델 선택**: Quick은 Claude만 사용. Deep은 Codex CLI, Gemini CLI를 Claude와 함께 실행하며, 외부 CLI 실패 시 2-AI 또는 Claude 단독으로 폴백.
- **AI 실패 처리**: JSON 파싱 실패 시 정규화 1회 재시도 후 FALLBACK 이벤트 기록 및 제외.
- **AI 결과는 참고용**: 최종 권고안은 산출물 생성 전 사용자 확인 필수.

## 빠른 시작

### 사전 요구사항

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 설치 및 설정
- [Codex CLI](https://github.com/openai/codex) (선택, Deep 모드용)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) (선택, Deep 모드용)
- Python 3.8+ 및 `openpyxl` (Excel 보고서 생성용)

### 설치

```bash
git clone https://github.com/Ihatespeedlimit/AI_Consulting.git
cd AI_Consulting
```

### 사용법

모든 기능은 Claude Code 스킬로 실행합니다:

```bash
# 컨설팅 시작 (전체 흐름 자동 진행)
/consult

# 요구사항 파싱만 실행
/parse-requirement

# AI 다자 토론
/ai-multi-discussion [논의 주제]

# Word 사용자 매뉴얼 생성
/gen-manual

# 이력 정리 (4주 이상 로그 아카이브)
/archive

# 개발 로그 기록
/dev-log
```

### 환경 변수

```bash
# Excel 보고서 생성에 필요
pip install openpyxl
```

API 키나 `.env` 파일이 필요 없습니다 — AI 모델 접근은 각 CLI 도구를 통해 처리됩니다.

## 프로젝트 구조

```
AI_Consulting/
├── README.md                       # 영어
├── README_ko.md                    # 한국어
├── UserRequirement_Draft.md        # 요구사항 초안
│
├── .claude/
│   ├── settings.json               # Claude Code 설정
│   ├── hooks/guard_output.py       # output 폴더 쓰기 보호
│   └── skills/                     # Claude Code 스킬 정의 (14개)
│       ├── consult/                # 메인 오케스트레이터
│       ├── parse-requirement/      # 요구사항 파싱
│       ├── ai-score-compare/       # 솔루션 평가 엔진
│       ├── ms-solution-recommend/  # MS 솔루션 참고 데이터
│       ├── generate-output/        # 산출물 파일 생성
│       ├── ai-analysis/            # AI 호출 이벤트 로깅
│       ├── dev-log/                # 개발 로깅
│       ├── test-log/               # 테스트 관찰 로깅
│       ├── ai-multi-discussion/    # 멀티 AI 토론 프레임워크
│       ├── gen-manual/             # 사용자 매뉴얼 생성
│       ├── readme-update/          # README 자동 갱신
│       ├── phase-doc/              # Phase 문서 관리
│       ├── github-push/            # Git push 자동화
│       └── skill-template/         # 스킬 공통 템플릿
│
├── Phase/                          # Phase별 상세 개발 문서
│   ├── Phase1_기반구축.md
│   ├── Phase2_핵심엔진.md
│   ├── Phase3_산출물생성.md
│   ├── Phase4_품질검증.md
│   └── Phase5_PA플로우설계.md
│
├── Word_Template/                  # Excel 보고서 도구
│   ├── 컨설팅결과_보고서_템플릿.xlsx  # KR+EN 2시트 템플릿
│   └── fill_excel_template.py      # 플레이스홀더 채우기 + 행 높이 자동 조정
│
├── references/                     # 개발 참고 문서
├── manuals/                        # 생성된 사용자 매뉴얼
├── assets/                         # 미디어 파일
│
├── logs/                           # 자동 생성 (.gitignore 권장)
│   ├── session/                    # 세션 상태 파일
│   ├── ai_analysis/                # AI 호출 이벤트 로그
│   ├── dev/                        # 개발 로그
│   ├── test/                       # 테스트 관찰 로그
│   └── PA_log/                     # PA 플로우 Blueprint
│
├── output/                         # 컨설팅 산출물
│   ├── Archive/                    # .txt 및 .xlsx 보고서
│   └── PA_Flow/                    # PA 플로우 설계 파일
│
└── archive/                        # 이력 아카이브
    ├── Consulting_Summary.csv      # 컨설팅 요약 누적
    └── raw/                        # Cold Storage (삭제 전 보관)
```

## 현재 상태

| Phase | 내용 | 상태 | Deliverable |
|---|---|---|---|
| Phase 1 — 기반 구축 | 로깅, 파싱, 세션 관리 | ✅ 완료 | dev-log, ai-analysis, parse-requirement 외 8개 기반 스킬 |
| Phase 2 — 핵심 엔진 | Quick/Deep 평가 엔진 | ✅ 완료 | 2패스 리스크 평가, AI 상호 리뷰, blocklist |
| Phase 3 — 산출물 생성 | 보고서 생성 + 흐름 통합 | ✅ 완료 | generate-output (.txt), consult 오케스트레이터 |
| Phase 4 — 품질 검증 | 다국어, 적합성 게이트, Excel, ROI, 토큰 최적화 | ✅ 완료 | en/ko/en+ko 지원, Excel 보고서, ROI 예측, 4차 토큰 최적화 |
| Phase 5 — PA 플로우 설계 | Power Automate 플로우 설계 생성 | ✅ 완료 | PA 플로우 다이어그램, Copilot 프롬프트, 예외 처리 체크리스트 |

미착수: `generate-test-list`, Notion 연동, 웹 UI (보류)

## 스킬 목록

### 범용(General) — 다른 프로젝트에도 이식 가능

| 스킬 | 설명 |
|---|---|
| `dev-log` | 에러/수정 이유/변경 내역 JSONL 기록 |
| `ai-analysis` | AI 호출·채점·세션 상태 이벤트 기록 |
| `readme-update` | README 자동 갱신 |
| `ai-multi-discussion` | AI 3자 의견 수집·비교·최적안 도출 |
| `archive` | 4주 이상 로그 아카이브 + CSV 요약 |
| `test-log` | 스킬 테스트 관찰사항 기록/조회 |
| `phase-doc` | Phase 상세 개발 문서 작성·갱신 |
| `skill-template` | 스킬 공통 표준 템플릿 |
| `gen-manual` | Word 사용자 매뉴얼 자동 생성 |

### 전용(Project-specific) — 이 프로젝트에 특화

| 스킬 | 설명 |
|---|---|
| `consult` | 전체 흐름 오케스트레이터 (파싱→분석→피드백→산출물) |
| `parse-requirement` | 요구사항 구조화 + session_id 생성 |
| `ai-score-compare` | Quick/Deep 리스크 2패스 평가 → 권고안 도출 |
| `ms-solution-recommend` | Deep 모드 참고 데이터 제공 (solutions.md) |
| `generate-output` | 산출물 파일 생성 (.txt / .xlsx) |

## 문서

| 문서 | 설명 |
|---|---|
| [Phase1_기반구축.md](./Phase/Phase1_기반구축.md) | 기반 구축 — 로깅, 파싱, 세션 |
| [Phase2_핵심엔진.md](./Phase/Phase2_핵심엔진.md) | 핵심 엔진 — Quick/Deep 평가 |
| [Phase3_산출물생성.md](./Phase/Phase3_산출물생성.md) | 산출물 생성 + 흐름 통합 |
| [Phase4_품질검증.md](./Phase/Phase4_품질검증.md) | 품질 — 다국어, Excel, ROI, 최적화 |
| [Phase5_PA플로우설계.md](./Phase/Phase5_PA플로우설계.md) | PA 플로우 설계 생성 |
| [skill-map.md](./references/skill-map.md) | 스킬 연동 관계 다이어그램 |
| [사용자 매뉴얼 (.docx)](./manuals/20260316_MS업무자동화컨설팅_매뉴얼.docx) | 최종 사용자 매뉴얼 |

## 한계점

- **CLI 전용**: 웹 UI 없음 — 모든 상호작용은 Claude Code 터미널을 통해 수행
- **테스트 미작성**: 수동 검증만 진행; 충분한 사용자 테스트 후 골든 테스트 케이스 생성 예정
- **외부 CLI 의존**: Deep 모드는 Codex CLI, Gemini CLI 별도 설치 필요
- **MS 생태계 한정**: Microsoft 제품 기반 솔루션만 추천; 비 MS 자동화는 범위 밖
- **로컬 실행**: 클라우드 배포 및 다중 사용자 지원 없음

## 향후 계획

- `generate-test-list`: 유저 테스트 체크리스트 자동 생성
- Notion 연동: 산출물을 Notion 페이지에 직접 발행
- 웹 UI: CLI 안정성 확인 후 검토 예정

---

<p align="center">Made with AI-assisted development</p>
