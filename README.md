# MS 업무자동화 솔루션 컨설팅 CLI 에이전트

Microsoft 생태계 내 업무 자동화 솔루션을 분석·제안하고, AI 3종 의견 비교 및 최종 산출물 파일을 생성하는 CLI 에이전트.

<video src="./assets/AIConsulting.mp4" width="100%" autoplay loop muted></video>

---

## 스킬 분류: 범용 vs 전용

### 범용(General) 스킬 — 다른 프로젝트에도 이식 가능

| 스킬 | 이유 |
|---|---|
| `dev-log` | 순수 로깅 — 프로젝트 독립적 |
| `ai-analysis` | AI 호출 추적 — 모델명/이벤트 타입만 바꾸면 범용 |
| `readme-update` | README 갱신 메커니즘은 어느 프로젝트에나 적용 가능 |
| `ai-multi-discussion` | 의사결정 논의 프레임워크 — AI 도구 설정만 외부화 |
| `archive` | JSONL 로그 보존 정책(기간/Cold Storage/CSV 요약) — CSV 컬럼만 교체하면 범용 |

### 전용(Project-specific) 스킬 — 이 프로젝트에 특화

| 스킬 | 이유 |
|---|---|
| `parse-requirement` | MS 제품 힌트, 도메인 분류가 MS 자동화 컨설팅에 특화 |
| `ms-solution-recommend` | Deep 모드 참고 데이터 제공 역할 (solutions.md 관리) |
| `generate-output` | 공통 스키마·재컨설팅 이력·Deep 부록 처리가 프로젝트 전용 |
| `consult` | 전체 오케스트레이션이 이 프로젝트 흐름에 종속 |

---

## Phase별 개발 계획

### Phase 1 — 기반 구축 `[완료]`
> 로깅, 세션 관리, 요구사항 파싱 등 모든 모듈이 공통으로 사용하는 기반 레이어

| # | Skill / 모듈 | 타입 | 상태 | 설명 |
|---|---|---|---|---|
| 1 | `dev-log` | general | ✅ 완료 | 에러 / 수정 이유 / 변경 내역 JSONL 기록 |
| 2 | `ai-analysis` | general | ✅ 완료 (v2.0) | AI 호출 이력 기록 — SESSION_STATE / REVISION / MODE_SWITCH / MS_VERIFY 4개 이벤트 타입 추가 |
| 3 | `readme-update` | general | ✅ 완료 | README 자동 갱신 스킬 |
| 4 | `parse-requirement` | project-specific | ✅ 완료 (v5.0) | 요구사항 파싱 — session_id 생성 및 세션 상태 파일 초기화 추가. v4.0: 입력 언어 자동 감지 (ko/en). v5.0: Q4 소요 시간 수집 (ROI 예측용) |
| 5 | `ai-multi-discussion` | general | ✅ 완료 | AI 3자(Codex/Gemini/Claude) 의견 수집·비교·최적안 도출 |
| 6 | `skill-template` | general | ✅ 완료 | 스킬 공통 표준 템플릿 |
| 7 | `phase-doc` | general | ✅ 완료 | Phase 상세 개발 문서 작성·갱신 스킬 |
| 8 | `test-log` | general | ✅ 완료 | 스킬 테스트 관찰사항 JSONL 기록/조회 (OBSERVATION / BUG / IMPROVEMENT / CONFIRMED) |

---

### Phase 2 — 핵심 엔진 `[재설계 완료]`
> Quick/Deep 모드 자유 제안 + AI 상호 리뷰 + 리스크 기반 권고안 도출

| # | Skill / 모듈 | 타입 | 상태 | 설명 |
|---|---|---|---|---|
| 8 | `ms-solution-recommend` | project-specific | ✅ 완료 (v3.0) | 역할 변경: 허용 목록 추천 → Deep 모드 참고 데이터 제공 |
| 9 | `ai-score-compare` | project-specific | ✅ 완료 (v3.0) | 역할 변경: 가중치 채점 → 리스크 2패스 평가 기반 권고안 도출 |
| - | `blocklist.md` (신규) | project-specific | ✅ 완료 | deprecated / 사용 불가 MS 제품 목록 (Quick/Deep 공통 참조) |

---

### Phase 3 — 산출물 생성 `[실행 검증 완료]`
> 최종 권고안을 공통 스키마로 출력하고 전체 흐름 통합

| # | Skill / 모듈 | 상태 | 설명 |
|---|---|---|---|
| 10 | `generate-output` | ✅ v1.7 완료 | 공통 스키마 + 부록 A/B + output_mode(integrated/user/developer/split) 지원. v1.6: 헤더 단순화. v1.7: ROI 블록 조건부 출력 (weekly_hours/send_volume 있을 때) |
| 11 | `consult` | ✅ v1.7 완료 | 전체 흐름 오케스트레이터. Quick/Deep 모드, 재컨설팅 A/B/C 분기, MS 지원 확인 (confirmed/changed) 실행 검증 완료. v1.6: STEP 3 요구사항 1줄 요약 규칙 추가. v1.7: 컨텍스트 압축 A/B/C(비선택안 최소 필드 유지, Evidence Summary 전용, 최소 필드 전달) |

---

### Phase 4 — 품질 검증 & 확장 `[완료]`
> 다국어 지원, 적합성 검증, 테스트 자동화 및 외부 서비스 연동 확장

| # | Skill / 모듈 | 상태 | 설명 |
|---|---|---|---|
| 12 | 다국어 지원 (영문 + 이중언어) | ✅ 구현 완료 | 영문 요구사항 자동 감지 + 영문 산출물 생성. en+ko 이중언어 옵션 추가(generate-output v1.4 / consult 언어 선택 업데이트) |
| 13 | `generate-test-list` | 🔲 미시작 | 유저 테스트 체크리스트 자동 생성 |
| 14 | Notion 연동 | 🔲 미시작 | 산출물을 Notion 페이지에 직접 생성 |
| 15 | 웹 UI | ⏸ 보류 | CLI 검증 이후 웹 인터페이스 제공 |
| 16 | 적합성 게이트 (Scope Gate) | ✅ 구현 완료 | parse 직후 MS 업무자동화 적합성 판정. 진행 가능(자동 진행) / 부분 지원(사용자 확인) / 지원 대상 아님(종료) 3단계 분기. consult v1.2 |
| 17 | 토큰 최적화 v1 | ✅ 구현 완료 | ai-score-compare v3.2: 기본 요약 출력 + 상세보기 트리거(-70%). consult v1.3: WebSearch Evidence Summary 압축(-95%) |
| 18 | `archive` 이력 보존 정책 | ✅ 구현 완료 | 4주 보존 + CSV 요약(날짜/세션ID/최종솔루션/산출물파일이름) + archive/raw/ Cold Storage 2단계 삭제 |
| 19 | Excel 보고서 생성 (.xlsx) | ✅ 구현 완료 | KR/EN 2시트 템플릿 + fill_excel_template.py (플레이스홀더 채우기·이탤릭 제거·행높이 자동조정) + consult STEP 7-E + output_language 연동 |
| 20 | 토큰 최적화 v2 | ✅ 구현 완료 | Reference 분리 6종 (excel-output-schema / deep-mode-guide / phase-template / label-map 등), consult·generate-output SKILL.md ~50% 압축, CLAUDE.md 중복 제거 (-600토큰/턴) |
| 21 | MS 제품 카탈로그 확장 | ✅ 구현 완료 | Forms/Planner/AI Builder solutions.md 추가(#13~15), ms-product-catalog.md 신규 — Quick/Deep 모두 전체 MS 제품군 인식 |
| 22 | 토큰 최적화 v3 (UX 간소화) | ✅ 구현 완료 | 헤더 단순화(generate-output v1.6), 요구사항 1줄 요약(consult v1.6), 채점표·리스크표 출력 금지(ai-score-compare v3.3) — 추가 ~1,350 토큰 절감 (~27%) |
| 23 | ROI 예측 | ✅ 구현 완료 | 소요 시간 수집(parse-requirement v5.0 Q4), ROI 블록 조건부 출력(generate-output v1.7), roi-estimation-guide.md 신규(도메인별 기준값+시나리오), Excel KR/EN 시트 ROI 섹션 추가 |
| 24 | 토큰 최적화 v4 (SKILL.md 압축 + 컨텍스트 압축) | ✅ 구현 완료 | label-map.md 58줄→18줄(#1, ~200토큰), ai-score-compare 중복 제거(#3, ~300토큰), parse-requirement 표 압축(#5, ~300토큰). consult v1.7: 컨텍스트 압축 A/B/C(비선택안 필드 드랍+전달 최소화+Evidence only, ~800~1,600토큰/사이클). CSV 파일명 고정(archive/Consulting_Summary.csv). excel-output-schema ROI 시나리오 3필드 제거(6필드로 정리) |

---

### Phase 5 — PA 플로우 설계 생성 `[완료]`
> Power Automate 권고안 확정 시 즉시 활용 가능한 플로우 설계 산출물 자동 생성

| # | Skill / 모듈 | 상태 | 설명 |
|---|---|---|---|
| 25 | 산출물 헤더 요구사항 요약 블록 추가 | ✅ 구현 완료 | generate-output v1.9: 공통 헤더에 자동화 대상/현재 도구/프로세스 3필드 (제약 조건 제외). 생성일시 날짜만 표기 |
| 26 | PA 플로우 설계 생성 | ✅ 구현 완료 | consult STEP 7-P: 플로우 다이어그램+Copilot 프롬프트+수동 구현 포인트+예외 처리 체크리스트. output/PA_Flow/.txt + logs/PA_log/.json(Blueprint). pa-flow-prompt-guide.md 신규. ~1,800토큰/실행 |

---

## 프로젝트 구조

> **구현 원칙**: Python 없음. SKILL.md + Reference 파일만으로 동작.
> 로깅은 Write/Edit 툴로 JSONL 직접 기록, 분석은 Claude LLM이 인라인 처리.

---

## 실행 환경

| 항목 | 내용 |
|---|---|
| OS | Windows 10 / macOS |
| IDE | VSCode + Claude Code |
| AI CLI | Codex CLI, Gemini CLI |
| 로그 포맷 | JSONL (UTF-8) |

---

## 사용법

모든 기능은 Claude Code 스킬로 실행한다.

```bash
# 컨설팅 시작 (전체 흐름 자동 진행)
/consult

# 요구사항 파싱만 실행
/parse-requirement

# 개발 로그 기록
/dev-log

# AI 다자 토론
/ai-multi-discussion [논의 주제]

# 이력 정리 (4주 이상 로그 아카이브)
/archive

# Word 사용자 매뉴얼 생성
/gen-manual
```

---

## `/consult` 실행 흐름

```
[사용자 입력] → 요구사항 파싱 → 적합성 판정 → 모드 선택(Quick/Deep)
     → AI 분석·권고안 도출 → 사용자 피드백(재컨설팅 가능)
     → MS 지원 확인 → 산출물 생성(.txt / .xlsx / PA 플로우)
```

- **Quick**: Claude 단독 분석, 빠른 권고안
- **Deep**: AI 3종(Claude + Codex + Gemini) 독립 제안 → 상호 리뷰 → 공통 강점/리스크 추출
- 재컨설팅, 세션 관리, 출력 스키마 상세 → [`consult/SKILL.md`](.claude/skills/consult/SKILL.md)

---

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

---

## 프로젝트 구조

```
AI_Consulting/
├── README.md
├── UserRequirement_Draft.md
│
├── logs/                           # 자동 생성 (.gitignore 권장)
│   ├── ai_analysis/
│   ├── dev/
│   ├── session/                    # 세션별 컨설팅 상태 파일
│   └── test/
│
├── archive/                        # 이력 아카이브 (.gitignore 권장)
│   ├── Consulting_Summary.csv      # 컨설팅 요약 누적 (영구 보존)
│   └── raw/                        # Cold Storage (1주 후 최종 삭제)
│
├── references/
│   ├── blocklist.md                # deprecated / 사용 불가 MS 제품 목록
│   ├── solutions.md                # 검증된 MS 솔루션 데이터 (Deep 참고용)
│   ├── reconsult-guide.md          # 재컨설팅 A/B/C 타입 판정 기준
│   ├── schema.md                   # 이벤트 스키마
│   └── skill-map.md                # 스킬 연동 관계
│
├── Word_Template/                  # Excel 보고서 생성
│   ├── 컨설팅결과_보고서_템플릿.xlsx
│   └── fill_excel_template.py
│
├── Phase/                          # Phase별 상세 개발 문서
│   ├── Phase1_기반구축.md
│   ├── Phase2_핵심엔진.md
│   ├── Phase3_산출물생성.md
│   ├── Phase4_품질검증.md
│   └── Phase5_PA플로우설계.md
│
└── .claude/skills/                 # Claude Code 스킬 정의
```

---

## 개발 현황

| Phase | 내용 | 상태 | 상세 문서 |
|---|---|---|---|
| 1 | 기반 구축 (로깅, 파싱, 세션) | ✅ 완료 | [Phase1](./Phase/Phase1_기반구축.md) |
| 2 | 핵심 엔진 (Quick/Deep 평가) | ✅ 완료 | [Phase2](./Phase/Phase2_핵심엔진.md) |
| 3 | 산출물 생성 + 흐름 통합 | ✅ 완료 | [Phase3](./Phase/Phase3_산출물생성.md) |
| 4 | 다국어/적합성 게이트/Excel/토큰 최적화/ROI | ✅ 완료 | [Phase4](./Phase/Phase4_품질검증.md) |
| 5 | PA 플로우 설계 생성 | ✅ 완료 | [Phase5](./Phase/Phase5_PA플로우설계.md) |

미착수: `generate-test-list`, Notion 연동, 웹 UI(보류)
골든 테스트 케이스는 충분한 사용자 테스트 후 생성 예정

---

## 참고 문서

- [UserRequirement.md](./UserRequirement.md) — 전체 요구사항
- [`references/skill-map.md`](./references/skill-map.md) — 스킬 연동 관계·트리거·Reference 사용 관계
- [`references/reconsult-guide.md`](./references/reconsult-guide.md) — 재컨설팅 A/B/C 판정 기준
- [`.claude/skills/`](.claude/skills/) — 각 스킬 SKILL.md (내부 스키마·규칙·세션 관리 상세)
