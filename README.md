# MS 업무자동화 솔루션 컨설팅 CLI 에이전트

Microsoft 생태계 내 업무 자동화 솔루션을 분석·제안하고, AI 3종 의견 비교 및 최종 산출물 파일을 생성하는 CLI 에이전트.

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
| 4 | `parse-requirement` | project-specific | ✅ 완료 (v4.0) | 요구사항 파싱 — session_id 생성 및 세션 상태 파일 초기화 추가. v4.0: 입력 언어 자동 감지 (ko/en) |
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
| 10 | `generate-output` | ✅ v1.3 완료 | 공통 스키마 + 부록 A/B + output_mode(integrated/user/developer/split) 지원. v1.3: output_language 파라미터 + 영문 레이블 매핑표 45개 + 영문 파일명 규칙(_EN suffix) |
| 11 | `consult` | ✅ 실행 검증 완료 | 전체 흐름 오케스트레이터. Quick/Deep 모드, 재컨설팅 A/B/C 분기, MS 지원 확인 (confirmed/changed) 실행 검증 완료 |

---

### Phase 4 — 품질 검증 & 확장 `[진행 중]`
> 다국어 지원, 적합성 검증, 테스트 자동화 및 외부 서비스 연동 확장

| # | Skill / 모듈 | 상태 | 설명 |
|---|---|---|---|
| 12 | 다국어 지원 (영문 + 이중언어) | ✅ 구현 완료 | 영문 요구사항 자동 감지 + 영문 산출물 생성. en+ko 이중언어 옵션 추가(generate-output v1.4 / consult 언어 선택 업데이트) |
| 13 | `generate-test-list` | 🔲 미시작 | 유저 테스트 체크리스트 자동 생성 |
| 14 | Notion 연동 | 🔲 미시작 | 산출물을 Notion 페이지에 직접 생성 |
| 15 | 웹 UI | ⏸ 보류 | CLI 검증 이후 웹 인터페이스 제공 |
| 16 | 적합성 게이트 (Scope Gate) | ✅ 구현 완료 | parse 직후 MS 업무자동화 적합성 판정. 진행 가능(자동 진행) / 부분 지원(사용자 확인) / 지원 대상 아님(종료) 3단계 분기. consult v1.2 |
| 17 | 토큰 최적화 | ✅ 구현 완료 | ai-score-compare v3.2: 기본 요약 출력 + 상세보기 트리거(-70%). consult v1.3: WebSearch Evidence Summary 압축(-95%) |
| 18 | `archive` 이력 보존 정책 | ✅ 구현 완료 | 4주 보존 + CSV 요약(날짜/세션ID/최종솔루션/산출물파일이름) + archive/raw/ Cold Storage 2단계 삭제 |

---

## 프로젝트 구조

> **구현 원칙**: Python 없음. SKILL.md + Reference 파일만으로 동작.
> 로깅은 Write/Edit 툴로 JSONL 직접 기록, 분석은 Claude LLM이 인라인 처리.

```
n8n/
├── README.md
├── UserRequirement_Draft.md        # 요구사항 문서
│
├── logs/                           # 자동 생성 (.gitignore 권장)
│   ├── ai_analysis/
│   │   └── ai_analysis_YYYYMMDD.jsonl
│   ├── dev/
│   │   └── dev_YYYYMMDD.jsonl
│   ├── session/
│   │   └── session_YYYYMMDD_NNN.json   # 세션별 컨설팅 상태 파일
│   └── test/
│       └── test_YYYYMMDD.jsonl
│
├── archive/                        # 이력 아카이브 (.gitignore 권장)
│   ├── YYYYMM_summary.csv          # 월별 컨설팅 요약 (영구 보존)
│   └── raw/                        # Cold Storage — 4주 이상 JSONL (1주 후 최종 삭제)
│
├── references/
│   ├── blocklist.md                # deprecated / 사용 불가 MS 제품 목록
│   ├── solutions.md                # 검증된 MS 솔루션 데이터 (Deep 모드 참고용)
│   ├── parsing-guide.md            # 도메인 분류 기준 / 신뢰도 공식
│   ├── schema.md                   # ai-analysis / dev-log 이벤트 스키마
│   ├── reconsult-guide.md          # 재컨설팅 A/B/C 타입 판정 기준 + 경계 케이스 예시
│   └── skill-map.md                # 스킬 연동 관계 / 트리거 / Reference 사용 관계
│
├── Phase/                          # Phase별 상세 개발 문서
│   ├── Phase1_기반구축.md           # ✅ 완료
│   ├── Phase2_핵심엔진.md           # ✅ 재설계 완료
│   ├── Phase3_산출물생성.md         # ✅ 실행 검증 완료
│   └── Phase4_품질검증.md           # 🚧 진행 중
│
└── .claude/
    └── skills/
        ├── skill-template/SKILL.md        # ✅ 공통 기준 템플릿
        ├── dev-log/SKILL.md               # ✅ Phase 1 [general]
        ├── ai-analysis/SKILL.md           # ✅ Phase 1 완료 v2.0 [general]
        ├── readme-update/SKILL.md         # ✅ Phase 1 [general]
        ├── parse-requirement/SKILL.md     # ✅ Phase 1 완료 v4.0 [project-specific]
        ├── ai-multi-discussion/SKILL.md   # ✅ 공통 [general]
        ├── phase-doc/SKILL.md             # ✅ 공통 [general]
        ├── ms-solution-recommend/SKILL.md # ✅ Phase 2 완료 v3.0 [project-specific]
        ├── ai-score-compare/SKILL.md      # ✅ Phase 2 완료 v3.2 [project-specific]
        ├── generate-output/SKILL.md       # ✅ Phase 3 완료 v1.4 [project-specific]
        ├── consult/SKILL.md               # ✅ Phase 3 완료 v1.3 [project-specific]
        │   └── references/reconsult-guide.md
        ├── test-log/SKILL.md              # ✅ Phase 1 완료 [general]
        └── archive/SKILL.md               # ✅ Phase 4 완료 v1.0 [general]
```

---

## 시스템 아키텍처

```
[User Input]
     │
     ▼
[parse-requirement]           Phase 1 — 요구사항 파싱 + session_id 생성 + 상태 파일 초기화
     │
     ▼
[적합성 게이트]               Phase 4 #16 — MS 업무자동화 범위 판정 (consult STEP 1-5)
     ├── 진행 가능     → 자동 진행 (안내만 출력)
     ├── 부분 지원 가능 → 지원 범위 표시 + 사용자 확인
     └── 지원 대상 아님 → 안내 후 종료
     │
     ├──── Quick 모드 ─────────────────────────────────────────────────────┐
     │      Claude 자유 분석 (ms-solution-recommend 미사용)                 │
     │      blocklist.md 차단 체크                                          │
     │      1패스: 리스크 평가 (탈락 가능성 기준)                            │
     │      2패스: 권고안 확정                                               │
     │      출력: 권장 1 / 검토필요 1~2 / 비추천 0~1                         │
     │                                                                      │
     └──── Deep 모드 ──────────────────────────────────────────────────────┤
            AI 상태 확인 (3개→정상 / 2개→경고+선택 / 1개→Quick 자동 전환)    │
            solutions.md 참고 준비 (요구사항 먼저, solutions.md 나중)         │
            3 AI 순차 실행 → JSON 파싱 → FALLBACK 처리                       │
            Claude Orchestrator: 각 AI 입장 예상 반론 구조화                  │
            공통 강점 / 공통 리스크 추출                                       │
            1패스 → 2패스 리스크 평가                                         │
            출력: 공통 스키마 + Deep 부록                                      │
     ┌───────────────────────────────────────────────────────────────────────┘
     │
     ▼
[사용자 피드백 → 재컨설팅 분기]
     ├── 타입 A (솔루션 ID 유지 + 조건 조정) → 경량 재컨설팅 (최대 3회)
     ├── 타입 B (핵심 MS 제품 조합 변경)     → 사용자 확인 후 전체 재컨설팅
     ├── 타입 C (설명 요청)                  → 설명 응답만 + 안내 문구
     └── Quick→Deep 전환                    → 전체 재컨설팅 처리 + 최신 revision 시드
     │
     ▼
[MS 지원 확인]              WebSearch — 권고안 선택 후 실행
     │                       결과 → 자동 A/B 분류 (ms_verify_retry 최대 2회)
     │
     ▼
[generate-output]           Phase 3 — 산출물 파일 생성
     ├── 본문: 최종 권고안 (공통 스키마)
     ├── 부록 A: 재컨설팅 이력 (session_id 필터 기반, 있을 때만)
     └── 부록 B: Deep AI 비교 (Deep 모드만)

[dev-log]       ◄── 전 Phase 공통: ERROR / CHANGE / INFO
[ai-analysis]   ◄── 전 Phase 공통: AI_CALL / SCORE / FALLBACK
                               + SESSION_STATE / REVISION / MODE_SWITCH / MS_VERIFY (신규)
```

---

## 공통 출력 스키마

Quick과 Deep 모두 동일한 기본 스키마를 사용한다.

```
[공통 기본 출력]
  솔루션명
  솔루션 ID   : 핵심 MS 제품 조합 (예: PowerAutomate+SharePointList+Outlook)
  적용 이유
  구현 개요   : 단계 목록
  전제조건
  한계점
  리스크 및 고려사항
    (보안)    리스크명: 설명 / 대응 방안
    (라이선스) 리스크명: 설명 / 대응 방안
    (운영)    리스크명: 설명 / 대응 방안
    고려사항  : 확인/결정 필요 사항
  판정        : 권장 | 검토필요 | 비추천

[Deep 전용 부록]
  AI별 제안 비교 테이블
  상호 리뷰 요약
  공통 강점 / 공통 리스크
  실행 AI: Codex ✅/❌ | Gemini ✅/❌ | Claude ✅
```

**리스크 출력 깊이:**

| 항목 | Quick | Deep |
|---|---|---|
| 설명 | 1줄 요약 | 상세 설명 |
| 영향도 | 생략 | 높음/중간/낮음 |
| 발생 조건 | 생략 | 발생 조건 + 확인 방법 |
| 대응 방안 | 짧게 | 상세 |

---

## 세션 관리

```
session_id 형식: consult_YYYYMMDD_NNN
생성 시점: parse-requirement 실행 시 자동 생성

상태 파일: logs/session/session_YYYYMMDD_NNN.json
{
  "session_id": "consult_20260309_001",
  "mode": "quick | deep",
  "current_revision": 0,
  "solution_id_current": "핵심MS제품조합",
  "light_revision_count": 0,      ← 전체 재컨설팅/모드 전환 시 리셋
  "total_revision_count": 0,      ← 절대 리셋 안 함
  "ms_verify_retry_count": 0,     ← 최대 2회, 초과 시 수동 확인 안내
  "created_at": "...",
  "updated_at": "..."
}
```

---

## solutions.md / blocklist.md 역할

| 파일 | Quick | Deep | 역할 |
|---|---|---|---|
| `blocklist.md` | 차단 체크 | 차단 체크 | deprecated / 사용 불가 제품 즉시 차단 |
| `solutions.md` | 미사용 | 참고만 | 검증된 라이선스·구현난이도 데이터 제공 (제약 아님) |

---

## 재컨설팅 규칙

| 타입 | 기준 | 처리 | 카운터 |
|---|---|---|---|
| A | 솔루션 ID 유지 + 조건 조정 | 경량 재컨설팅 | light +1, total +1 |
| B | 핵심 MS 제품 조합 변경 | 사용자 확인 후 전체 재컨설팅 | light 리셋, total +1 |
| C | 설명 요청 | 설명 응답만 | 변동 없음 |
| 모드 전환 | Quick→Deep | 전체 재컨설팅 처리 | light 리셋, total +1 |

- 경량 재컨설팅 3회 초과 시 전체 재컨설팅 권장 안내
- 타입 B 사용자 거부(override) 허용: 경고 표시 + 로그 기록 + 산출물 부록 명시

---

## 실행 환경

| 항목 | 내용 |
|---|---|
| OS | Windows 10 / macOS |
| IDE | VSCode |
| AI CLI | Codex CLI, Gemini CLI |
| 로그 포맷 | JSONL (UTF-8) |

---

## 스킬 실행 방법

모든 기능은 Claude Code 스킬로 실행한다. Python 코드 직접 실행 없음.

```bash
# 컨설팅 시작
/consult

# 요구사항 파싱만 실행
/parse-requirement

# 개발 로그 기록
/dev-log

# AI 다자 토론
/ai-multi-discussion [논의 주제]

# 이력 정리 (4주 이상 로그 아카이브)
/archive
```

---

## Phase 상세 문서

| 문서 | 상태 | 내용 |
|---|---|---|
| [Phase1_기반구축.md](./Phase/Phase1_기반구축.md) | ✅ 완료 / 🔄 일부 수정 예정 | dev-log, ai-analysis, readme-update, parse-requirement, ai-multi-discussion, skill-template |
| [Phase2_핵심엔진.md](./Phase/Phase2_핵심엔진.md) | ✅ 재설계 완료 | ms-solution-recommend v3.0, ai-score-compare v3.0, blocklist.md |
| [Phase3_산출물생성.md](./Phase/Phase3_산출물생성.md) | ✅ 실행 검증 완료 | generate-output v1.2, consult v1.0 / Quick·Deep 전체 흐름 + 재컨설팅 A/B/C 분기 실행 검증 완료 |
| [Phase4_품질검증.md](./Phase/Phase4_품질검증.md) | 🚧 진행 중 | 다국어 지원(영문) SKILL.md 구현 완료 (#12). generate-test-list, Notion 연동 미시작 |

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-06 | v0.1 | README 최초 작성, Phase 1 착수 (dev-log, ai-analysis, readme-update) |
| 2026-03-06 | v0.2 | Phase 1 완료 — parse-requirement 개발 완료, Phase 구조 도입 |
| 2026-03-06 | v0.3 | 스킬 설계 개선 — 범용/전용 분류, 공통 템플릿(skill-template) 생성, 전체 SKILL.md 표준화 |
| 2026-03-06 | v0.4 | Phase 상세 문서 생성 (Phase/ 디렉토리), phase-doc 스킬 생성, README 완료 모듈 사용법 보완 |
| 2026-03-06 | v0.5 | Phase 2 완료 — ms_solution_recommender.py (지식 베이스 8종), ai_score_compare.py (Quick/Deep/Fallback), SKILL.md 2개 |
| 2026-03-09 | v0.6 | 전체 아키텍처 재설계 — Quick/Deep 모드 분리, 자유 제안 방식, 리스크 기반 평가, 재컨설팅 시스템, 세션 관리, MS 지원 확인, 공통 출력 스키마 확정 |
| 2026-03-09 | v0.7 | 전 스킬 재설계 완료 — parse-requirement v3.0, ai-analysis v2.0, ms-solution-recommend v3.0, ai-score-compare v3.0, generate-output v1.0(신규), consult v1.0(신규) / 신규 참조 파일: reconsult-guide.md, skill-map.md |
| 2026-03-09 | v0.8 | Python 제거 — src/ 디렉토리 전체 삭제. 모든 스킬이 SKILL.md + Reference 파일만으로 동작하도록 확정. 구현 원칙: Reference 우선, Python은 불가피한 경우만 허용 |
| 2026-03-09 | v0.9 | 전체 테스트 실행 및 개선 — test-log 스킬 신규 생성, generate-output v1.1(요구사항 요약 섹션·출력 깊이 규칙·Quick/Deep 리스크 분기 추가), consult SKILL.md 개선(타입 C→A 전환 명시·타입 A 재출력 규칙·confirmed 추가 조건 처리), logs/ 4개 하위 폴더 분리(ai_analysis/dev/session/test), 전 스킬 경로 수정 |
| 2026-03-10 | v1.0 | Phase 3 실행 검증 완료 — Quick 모드(재고 취합) + Deep 모드(권한 전처리) 전체 흐름 실행. generate-output v1.2(output_mode 파라미터: integrated/user/developer/split). 재컨설팅 A/B/C 분기 검증 완료(타입 C 설명응답·타입 A Rev.1 파라미터 변경·타입 B 전체재컨설팅·타입 B user_override). Codex CLI --skip-git-repo-check 버그 수정. skill references 구조화(blocklist.md → ai-score-compare/ms-solution-recommend, reconsult-guide.md → consult/references/). skill-template references 생성 가이드 추가. |
| 2026-03-10 | v1.1 | Phase 4 착수 — 다국어 지원(영문) #12 SKILL.md 구현 완료. parse-requirement v4.0(입력 언어 자동 감지 ko/en, 이중 확인 화면, session 파일 input_language 필드). generate-output v1.3(output_language 파라미터, 영문 레이블 매핑표 45개, 파일명 _EN suffix). consult STEP 6 언어 선택 추가. ai-score-compare Deep 모드 영문 프롬프트 분기. |
| 2026-03-10 | v1.2 | #12 이중언어(en+ko) 추가 — generate-output v1.4(_BILINGUAL suffix, 영문 본문+한국어 번역 단일 파일), consult 언어 선택 옵션 3번 추가. #16 적합성 게이트 설계 확정 — Phase 4 신규 항목, consult STEP 1-5 3단계 분기(진행 가능 자동/부분 지원 확인/지원 대상 아님 종료), v1.2 구현 예정. |
| 2026-03-10 | v1.3 | #16 적합성 게이트 구현 완료(consult v1.2). #17 토큰 최적화 — ai-score-compare v3.2(기본 요약 출력+상세보기 트리거, -70%), consult v1.3(WebSearch Evidence Summary 압축, -95%). #18 archive 스킬 v1.0 신규(4주 보존+CSV 요약+Cold Storage 2단계 삭제). 경로 오류 수정 — dev-log/ai-analysis/parse-requirement mkdir 서브폴더 경로 수정. 범용 스킬에 archive 추가. |

---

## 참고 문서

- [UserRequirement.md](./UserRequirement.md) — 전체 요구사항
- `.claude/skills/` — Claude Code 스킬 정의
- `references/blocklist.md` — deprecated / 사용 불가 MS 제품 목록
- `references/reconsult-guide.md` — 재컨설팅 A/B/C 타입 판정 기준 및 경계 케이스 예시
- `references/skill-map.md` — 전체 스킬 연동 관계, 트리거, Reference 사용 관계 정리
