# Phase 2 — 핵심 엔진 `[재설계 완료]`

> Quick/Deep 모드 자유 제안 + AI 상호 리뷰 + 리스크 기반 권고안 도출

**최초 완료일**: 2026-03-06
**재설계 착수**: 2026-03-09
**재설계 완료**: 2026-03-09
**상태**: ✅ 재설계 완료 (SKILL.md 기준)
**선행 조건**: Phase 1 전체 완료 ✅

---

## 재설계 배경

Phase 2 초기 구현(v0.5)은 `solutions.md` 12개 고정 목록 기반의 허용 목록 추천 방식과
가중치 채점(적합성 35% / 구현난이도 30% / 유지보수성 15% / 라이선스적합성 10% / 확장성 10%)으로
권고안을 도출했다.

재설계 이유:
- **고착화 문제**: solutions.md 목록 외 더 적합한 MS 솔루션 제안 불가
- **유연성 부족**: 새 MS 제품/기능 출시 시 목록 수동 업데이트 전까지 반영 불가
- **재컨설팅 부재**: 사용자 피드백 반영 구조 없음
- **리스크 정보 부재**: 구현/운영 리스크 및 고려사항 출력 없음
- **AI 상호 리뷰 부재**: Deep 모드에서 AI들이 채점만 하고 상호 피드백 없음

---

## 재설계 후 항목

| # | Skill / 모듈 | 파일 | 상태 | 스킬 타입 |
|---|---|---|---|---|
| 8 | `ms-solution-recommend` | `src/modules/ms_solution_recommender.py` | ✅ SKILL.md v3.0 완료 | project-specific |
| 9 | `ai-score-compare` | `src/modules/ai_score_compare.py` | ✅ SKILL.md v3.0 완료 | project-specific |
| - | `blocklist.md` (신규) | `references/blocklist.md` | ✅ 완료 | — |

---

## 8. ms-solution-recommend (재설계)

### 역할 변경

| 구분 | 기존 | 변경 후 |
|---|---|---|
| 역할 | 허용 목록(12개) 기반 추천 | Deep 모드 참고 데이터 제공 |
| Quick 모드 | solutions.md에서 후보 선별 | **미사용** |
| Deep 모드 | solutions.md 매칭 → 채점 | solutions.md 컨텍스트 제공 (참고만, 제약 아님) |
| solutions.md | 허용 목록 | 검증된 라이선스/구현난이도 데이터 창고 + 점진적 확장 |

### Deep 모드에서의 동작

```
solutions.md 컨텍스트 준비:
  "요구사항 기반으로 자유 제안 후,
   아래 검증 데이터가 있으면 참고로 활용하세요."

프롬프트 순서 원칙:
  ① 요구사항 먼저 → ② solutions.md 참고 나중
  (역순이면 solutions.md에 앵커링되어 자유 제안 효과 감소)

제안된 솔루션이 solutions.md에 있으면:
  → 검증된 라이선스/구현난이도/score_hints 활용

제안된 솔루션이 solutions.md에 없으면:
  → AI 추정값 + [미검증] 태그 표시
  → MS 지원 확인 단계에서 WebSearch로 보완
```

### solutions.md 역할 재정의

```
역할 1. 검증된 데이터 창고 (Enrichment DB)
  → 라이선스, 구현난이도, 구현 개요 참고 데이터 제공

역할 2. 점진적 지식 베이스 (Growing DB)
  → WebSearch 검증 완료된 신규 솔루션 추가 제안
  → 시간이 지날수록 DB가 풍부해짐
```

---

## 9. ai-score-compare (재설계)

### 역할 변경

| 구분 | 기존 | 변경 후 |
|---|---|---|
| Quick 방식 | Claude 단독 가중치 채점 | Claude 자유 분석 + 리스크 2패스 평가 |
| Deep 방식 | AI 3종 독립 채점 + 평균 | AI 3종 독립 제안 + Orchestrator 상호 리뷰 + 리스크 평가 |
| 권고안 기준 | 가중합 수치 순위 | 리스크 탈락 가능성 + 판정 |

### Quick 모드 프로세스

```
STEP 1 — Claude 자유 분석 (ms-solution-recommend 미사용)
  MS 생태계 내에서 요구사항 기반 자유 제안
  최대 3개 후보 도출

STEP 2 — blocklist.md 차단 체크
  deprecated / 사용 불가 제품 포함 시 즉시 제거

STEP 3 — 1패스: 후보별 리스크 평가
  질문: "이 리스크가 발생하면 이 솔루션이 탈락하는가?"
  탈락 가능성 YES            → Quick 필수 표시 (심각도 무관)
  탈락 가능성 NO + 심각도 높음 → Quick 표시
  탈락 가능성 NO + 심각도 중간/낮음 → Quick 생략

STEP 4 — 2패스: 권고안 확정
  리스크 평가 결과 반영해 최종 판정

STEP 5 — 출력 (공통 스키마)
  권장 1개 (필수)
  검토 필요 1~2개 (있으면)
  비추천 0~1개 (교육적 가치 있을 때만)
    → 맞아 보이지만 핵심 요구사항 미충족
    → 라이선스/운영 리스크가 있는 경우
```

### Deep 모드 프로세스

```
STEP 1 — AI 상태 확인
  3개 성공 → 정상 Deep 진행
  2개 성공 → 경고 후 사용자 선택 (계속 | Quick 전환)
  1개 성공 → Deep 중단, Quick 자동 전환
  실행 AI 수 산출물에 반드시 명시

STEP 2 — solutions.md 컨텍스트 준비 (ms-solution-recommend 호출)
  "요구사항 먼저, solutions.md 참고 나중" 순서로 프롬프트 구성
  blocklist.md 차단 목록 함께 전달

STEP 3 — 3 AI 순차 실행 (독립 제안서)
  공통 스키마 JSON 형식 강제 지정
  Codex → /tmp/codex_result.json
  Gemini → /tmp/gemini_result.json
  Claude → 자체 분석

  파싱 처리:
    JSON 파싱 성공 → 사용
    파싱 실패 → 정규화 1회 재시도
    그래도 실패 → 해당 AI 제외 + FALLBACK 이벤트 기록

STEP 4 — Claude Orchestrator: 상호 리뷰 구조화
  3개 제안서를 읽고 각 AI 입장에서 예상 반론 생성:
    - 강점
    - 약점
    - 누락 전제조건
    - 채택 의견

STEP 5 — 공통 강점 / 공통 리스크 추출

STEP 6 — 1패스 → 2패스 리스크 평가
  Quick과 동일 기준, 상세 형식 (영향도 + 발생조건/확인방법 + 대응방안)

STEP 7 — 최종 권고안 + 대안 도출

STEP 8 — 공통 스키마 + Deep 부록 출력
```

### 리스크 평가 2패스 구조

```
1패스 (권고안 미확정 상태)
  질문: "이 리스크가 발생하면 이 솔루션이 탈락하는가?"
  → 솔루션 탈락 가능성으로 평가 (권고안 변경 가능성 X)

2패스 (리스크 결과 반영 후)
  → 탈락 가능성 결과를 바탕으로 최종 권고안 확정
  → 권고안 기준으로 리스크 표시 여부 결정

Quick 표시 기준:
  탈락 가능성 YES → 반드시 표시
  탈락 가능성 NO + 심각도 높음 → 표시

Deep 표시 기준:
  높음 / 중간 / 낮음 전체 표시 + 대응 방안
```

---

## blocklist.md (신규)

### 목적
Quick/Deep 모드 모두에서 AI 제안 직후 차단 체크에 사용하는 사용 불가 목록.

### 포함 항목
- `status: deprecated` MS 제품
- 회사 정책으로 사용 불가한 제품
- 운영 중 문제가 확인된 솔루션

### 관리 방식
```
운영하면서 문제가 확인된 경우에만 추가
→ "사용이 안 되는 것만 파악해서 지정" 방향
```

---

## 공통 출력 스키마

Quick과 Deep 모두 동일한 기본 스키마 사용:

```
솔루션명
솔루션 ID   : 핵심 MS 제품 조합
              예) PowerAutomate+SharePointList+Outlook
              경량/전체 재컨설팅 구분 기준으로 사용
적용 이유
구현 개요   : 단계 목록
전제조건
한계점
리스크 및 고려사항
  (보안)    리스크명: 설명 / [탈락가능성] / 대응방안
  (라이선스) 리스크명: 설명 / [탈락가능성] / 대응방안
  (운영)    리스크명: 설명 / 대응방안
  고려사항  : 확인/결정 필요 사항
판정        : 권장 | 검토필요 | 비추천
```

**Deep 전용 부록:**
```
AI별 제안 비교 테이블
상호 리뷰 요약
공통 강점 / 공통 리스크
실행 AI: Codex ✅/❌ | Gemini ✅/❌ | Claude ✅
```

---

## 재컨설팅 연계

### 솔루션 ID 기준

```
솔루션 ID = 핵심 MS 제품 조합
  예) "PowerAutomate+Outlook"
      "PowerAutomate+SharePointList+Outlook"
      "AzureLogicApps+AzureFunctions"

경량 재컨설팅 (타입 A): 솔루션 ID 유지 + 조건 조정
  실행 시간 변경 / 알림 채널 변경 / 담당자 변경
  로그 저장 추가 / 예외 처리 추가 / 설명 보강

전체 재컨설팅 (타입 B): 솔루션 ID 변경
  핵심 제품 교체 / 데이터 소스 변경 / 트리거 방식 변경
  외부 시스템 추가/제거 / 요구사항 목표 변경
  보안/정책 조건 추가로 솔루션 구조가 바뀌는 경우
```

---

## MS 지원 확인 연계

```
권고안 선택 후 WebSearch 실행:
  "[제품명] [기능명] site:learn.microsoft.com"

결과 처리:
  정상 → 진행
  기능 변경 → Claude가 영향 범위 평가 → A/B 자동 분류
  deprecated → 타입 B 자동 분류

ms_verify_retry_count 별도 관리:
  최대 2회 초과 시 자동 재컨설팅 중단
  → MS Learn 링크 제공 + 수동 확인 안내
```

---

## Phase 2 스킬 범용/전용 분류

| 스킬 | 분류 | 이유 |
|---|---|---|
| `ms-solution-recommend` | project-specific | MS 생태계 참고 데이터 관리 특화 |
| `ai-score-compare` | project-specific | 리스크 평가 기준이 MS 컨설팅 도메인에 특화 |

---

## 의존성 구조

```
Phase 1 출력
└── ParsedRequirement + session_id
    │
    ├── Quick 모드
    │   └── ai-score-compare (Claude 자유 분석)
    │       └── blocklist.md 체크
    │           └── SolutionProposal (공통 스키마)
    │
    └── Deep 모드
        └── ms-solution-recommend (solutions.md 컨텍스트)
            └── ai-score-compare (3 AI + Orchestrator)
                └── blocklist.md 체크
                    └── SolutionProposal (공통 스키마 + Deep 부록)
                        └── Phase 3 입력
```

---

## 개발 시 주의사항

- Quick 모드에서 ms-solution-recommend를 절대 호출하지 않도록 설계
- Deep 모드 프롬프트 순서: 요구사항 먼저, solutions.md 나중 (앵커링 방지)
- AI 제안서 JSON 파싱 실패 시 정규화 1회 후 FALLBACK 처리 (재시도 금지)
- 1패스/2패스 평가를 반드시 분리 실행 (순환 의존 방지)
- 솔루션 ID는 공백 없는 "제품명+제품명" 형식으로 통일

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-03-06 | Phase 2 설계 초안 작성 |
| 2026-03-06 | Phase 2 전체 완료 — ms_solution_recommender.py (지식 베이스 8종, 매칭 알고리즘), ai_score_compare.py (가중합 계산, Quick/Deep/Fallback 모드) |
| 2026-03-09 | 전면 재설계 완료 — ms-solution-recommend v3.0(참고 데이터 역할), ai-score-compare v3.0(리스크 2패스 평가), blocklist.md 신규 생성 |
| 2026-03-09 | 전체 재설계 착수 — 자유 제안 방식, 리스크 2패스 평가, AI 상호 리뷰, 재컨설팅 연계, blocklist.md 신규 추가, solutions.md 역할 변경 |
