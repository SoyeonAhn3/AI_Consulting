# Phase 3 — 산출물 생성 `[실행 검증 완료]`

> 최종 권고안을 공통 스키마 기반 산출물로 출력하고 전체 흐름을 세션·재컨설팅 포함하여 통합

**스킬 설계 완료**: 2026-03-09
**실행 검증 완료**: 2026-03-10
**상태**: ✅ 실행 검증 완료
**선행 조건**: Phase 2 재설계 완료 ✅

---

## 개요

Phase 2에서 도출된 권고안(`SolutionProposal`)을 공통 스키마 기반 산출물로 생성하고,
재컨설팅 이력(부록 A)과 Deep AI 비교(부록 B)를 포함한다.
`consult`는 세션 관리, 모드 분기, 재컨설팅 분기, MS 지원 확인을 포함한
전체 흐름을 오케스트레이션한다.

---

## 완료 항목

| # | Skill / 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 10 | `generate-output` | ✅ v1.2 실행 검증 완료 | project-specific |
| 11 | `consult` | ✅ v1.0 실행 검증 완료 | project-specific |
| - | `reconsult-guide.md` | ✅ 완료 (consult/references/) | — |
| - | `skill-map.md` | ✅ 완료 (references/) | — |

---

## 10. generate-output ✅ (v1.2)

### 목적
최종 권고안을 공통 스키마 기반 본문 + 재컨설팅 이력 부록 + Deep AI 비교 부록으로 구성된
산출물 파일을 생성한다.

### 구현 파일
- `.claude/skills/generate-output/SKILL.md`

### 출력 파일 구조

```
output/
└── [날짜]_[도메인]_[session_id]_자동화_컨설팅.txt
```

### 산출물 구성

```
=== 본문: 최종 권고안 ===

[권장안]
  솔루션명      :
  솔루션 ID     :
  적용 이유     :
  구현 개요     :
  전제조건      :
  한계점        :
  리스크 및 고려사항:
    (보안)    리스크명: 설명 / 대응방안
    (라이선스) 리스크명: 설명 / 대응방안
    (운영)    리스크명: 설명 / 대응방안
    고려사항  : 확인/결정 필요 사항
  판정          : 권장

[검토 필요안] (있을 경우)
  ...

[비추천안] (있을 경우)
  ...

=== 부록 A: 재컨설팅 이력 (재컨설팅이 있었을 때만) ===

  Rev.1
    타입     : A (경량) | B (전체) | B-Override (사용자 거부)
    이전 권고 : [솔루션명]
    새 권고  : [솔루션명]
    변경 이유 : ...
    ※ Override: 타입 B 권장 → 사용자 요청으로 경량 진행 (결과 일관성 낮을 수 있음)

  Rev.2 ...

=== 부록 B: Deep AI 비교 (Deep 모드만) ===

  실행 AI: Codex ✅ | Gemini ✅ | Claude ✅ (3/3)

  [AI별 제안 비교]
  항목         | Codex | Gemini | Claude
  ─────────────────────────────────────
  솔루션 ID    | ...   | ...    | ...
  특이점       | ...   | ...    | ...

  [상호 리뷰 요약]
  공통 강점 : ...
  공통 리스크: ...
```

### 핵심 설계

**session_id 필터 기반 로그 조회:**
```
# REVISION 이벤트 조회 시 반드시 session_id 필터 적용
# 다른 세션의 재컨설팅 이력 혼입 방지
event.session_id == current_session_id AND event.event_type == "REVISION"
```

**v1.1 추가 사항:**
- 산출물 본문 최상단에 `요구사항 요약` 섹션 추가 (ParsedRequirement 기반)
- 출력 깊이 규칙: 권장(전체) / 검토필요(간략) / 비추천(최소)
- Quick/Deep 리스크 출력 포맷 분기 (Deep는 영향도·발생조건·상세 대응)
- [미검증] 태그: MS 지원 확인 전 unverified=true 솔루션에 표시, confirmed 후 해제
- MS 지원 확인 결과 헤더 반영 (`confirmed ✅ | changed ⚠️ | deprecated ❌ | 미실행 —`)
- 파일 인코딩: UTF-8 / LF / BOM 없음 명시

**v1.2 추가 사항 (실행 검증 반영):**
- `output_mode` 파라미터 추가: `integrated`(기본) / `user` / `developer` / `split`
- `integrated`: 사용자 섹션 + 개발자 섹션 단일 파일
- `user`: 비기술적 요약만 (담당자 보고용)
- `developer`: 기술 상세 + 부록 B (구현 담당자용)
- `split`: 사용자용·개발자용 파일 2개 동시 생성
- 파일명 규칙: `[base]_사용자.txt` / `[base]_개발자.txt` (split/user/developer 모드)

**리스크 카테고리 태그:**
- `(보안)` — DLP, 데이터 접근 권한, 컴플라이언스
- `(라이선스)` — 라이선스 부재, 추가 비용 발생
- `(운영)` — 유지보수, 담당자, 변경 시 대응

**부록 생성 조건:**
- 부록 A: `light_revision_count > 0` 또는 `total_revision_count > 0`일 때만 생성
- 부록 B: 실행 모드가 Deep일 때만 생성
- user_override 이력은 부록 A에 반드시 표시

### 스킬 타입
project-specific — 공통 스키마·부록 구조·session_id 필터가 이 프로젝트 전용

---

## 11. consult ✅

### 목적
세션 관리, 모드 분기, 재컨설팅 분기, MS 지원 확인을 포함한
Phase 1~3 전체 흐름을 오케스트레이션한다.

### 구현 파일
- `.claude/skills/consult/SKILL.md`

### 전체 흐름

```
[consult 진입점]
      │
      ▼
[1] parse-requirement
      session_id 생성: consult_YYYYMMDD_NNN
      상태 파일 초기화: logs/session_YYYYMMDD_NNN.json
      ParsedRequirement 확정 + 사용자 확인
      │
      ▼
[2] 모드 선택 (Quick | Deep)
      │
      ├── Quick ──────────────────────────────────────────────────┐
      │     ai-score-compare (Claude 자유 분석)                   │
      │     blocklist.md 체크                                     │
      │     1패스 리스크 평가 → 2패스 권고안 확정                  │
      │     공통 스키마 출력                                       │
      │                                                           │
      └── Deep ───────────────────────────────────────────────────┤
            AI 상태 확인 → 3/2/1개 분기                           │
            ms-solution-recommend (solutions.md 참고 준비)         │
            3 AI 순차 실행 → 파싱 → FALLBACK 처리                 │
            Orchestrator 상호 리뷰 → 공통 강점/리스크 추출         │
            1패스 → 2패스 리스크 평가                             │
            공통 스키마 + Deep 부록 출력                          │
      ┌──────────────────────────────────────────────────────────┘
      │
      ▼
[3] 사용자 피드백 → 재컨설팅 분기
      │
      ├── 타입 A (솔루션 ID 유지)
      │     경량 재컨설팅 실행
      │     light_revision_count +1 → 상태 파일 즉시 저장
      │     3회 초과 시 전체 재컨설팅 권장 안내
      │
      ├── 타입 B (솔루션 ID 변경)
      │     "타입 B 판단. 전체 재컨설팅 권장합니다. 진행하시겠습니까?"
      │     → 수락: 전체 재컨설팅 / light_revision_count 리셋
      │     → 거부: 경량 진행 + 경고 + user_override 로그 기록
      │
      ├── 타입 C (설명 요청)
      │     설명 응답만 제공
      │     "추가 조정이 필요하면 말씀해주세요.
      │      조건 변경이면 재컨설팅으로 이어서 반영할 수 있습니다."
      │
      └── Quick→Deep 전환
            전체 재컨설팅으로 처리
            시드: 현재 최신 revision 기준
            light_revision_count 리셋
            MODE_SWITCH 이벤트 기록
      │
      ▼
[4] 권고안 선택 → MS 지원 확인
      WebSearch: "[제품명] [기능명] site:learn.microsoft.com"
      결과 → Claude가 A/B 영향 범위 평가
      ms_verify_retry_count 관리 (최대 2회)
      2회 초과 시: 수동 확인 안내 + MS Learn 링크 제공
      │
      ▼
[5] 사용자 최종 확인
      │
      ▼
[6] generate-output
      본문: 최종 권고안 (공통 스키마, 최신 revision 기준)
      부록 A: 재컨설팅 이력 (session_id 필터, 있을 때만)
      부록 B: Deep AI 비교 (Deep 모드만)
      │
      ▼
[7] 완료 보고 + 파일 경로 출력
```

### 상태 파일 관리

```
상태 파일 경로: logs/session/session_YYYYMMDD_NNN.json

즉시 저장 시점 (컨텍스트 압축 대비):
- 재컨설팅 카운터 변경 시마다
- 모드 전환 시
- ms_verify_retry_count 변경 시
- solution_id_current 변경 시
```

**v1.0 개선 사항 (테스트 반영):**
- 타입 C → 타입 A 암묵적 전환 시 명시적 사용자 확인 요구 (카운터 증가 전 확인)
- 타입 A 재컨설팅 출력: 변경된 안 전체 재출력 + "(Rev.N)" 표시, 변경 없는 안 "(변경 없음)"
- confirmed 결과 추가 조건 자동 반영 + 사용자에게 명시
- changed 결과 A/B 자동 분류 기준 명확화
- created_at/updated_at ISO 8601 기록 규칙 추가

### 스킬 타입
project-specific — 세션 관리, 재컨설팅 분기, MS 지원 확인이 이 프로젝트 흐름에 종속

---

## Phase 3 실행 검증 결과 (2026-03-10)

### 검증 세션

| 세션 | 모드 | 요구사항 | 산출물 |
|---|---|---|---|
| consult_20260310_001 | Quick | 재고 현황 Excel 취합·보고서 자동화 | 통합본 (integrated) |
| consult_20260310_002 | Deep | 연간 권한 Check — 8개 앱 CSV+Excel 전처리 | 개발자용 (developer) + 부록 B |

### 검증 결과 요약

| 항목 | 결과 |
|---|---|
| Quick 전체 흐름 (parse→분석→MS확인→산출물) | ✅ 정상 |
| Deep 전체 흐름 (Codex+Gemini+Claude→산출물) | ✅ 정상 |
| MS 지원 확인 confirmed 케이스 | ✅ 추가 조건 전제조건 자동 반영 |
| MS 지원 확인 changed → Type A 분류 | ✅ 정상 분류 및 전제조건 반영 |
| 재컨설팅 타입 C (설명 요청) | ✅ 카운터 변화 없음 확인 |
| 재컨설팅 타입 A (파라미터 변경) | ✅ light+1/total+1, Rev.N 표시, SESSION_STATE 기록 |
| 재컨설팅 타입 B 수락 (전체 재컨설팅) | ✅ light 리셋/total+1, solution_id 교체 |
| 재컨설팅 타입 B 거부 (user_override) | ✅ 경고 표시, override 로그 기록 |
| output_mode: integrated / developer / 부록 B | ✅ 정상 생성 |

### 발견 버그 및 조치

| 버그 | 조치 |
|---|---|
| Codex CLI: trusted directory 오류 (exit 1) | `--skip-git-repo-check` 플래그 + 프로젝트 디렉토리 내 실행으로 해결 |

### 개선 관찰 사항 (test-log #7)

- Deep 모드에서 3 AI 모두 동일 접근(Power Query)으로 수렴하는 현상 발견
- 향후 개선: Deep 모드 프롬프트에 다양한 접근 방식 탐색 지시 추가 검토

---

## Phase 3 스킬 범용/전용 분류

| 스킬 | 분류 | 이유 |
|---|---|---|
| `generate-output` | project-specific | 공통 스키마·부록 구조·session_id 필터가 프로젝트 전용 |
| `consult` | project-specific | 세션·재컨설팅·MS 지원 확인 오케스트레이션이 프로젝트 흐름에 종속 |

---

## 의존성 구조

```
Phase 2 출력
└── SolutionProposal (공통 스키마)
    └── generate-output
        ├── 본문: 최종 권고안
        ├── 부록 A: 재컨설팅 이력 (session_id 필터)
        └── 부록 B: Deep AI 비교

└── consult (오케스트레이터)
    ├── parse-requirement (STEP 1)
    ├── ai-score-compare / ms-solution-recommend (STEP 2)
    ├── 재컨설팅 분기 로직 (STEP 3)
    ├── MS 지원 확인 / WebSearch (STEP 4)
    └── generate-output (STEP 6)
```

---

## 개발 시 주의사항

- `generate-output`은 반드시 session_id 필터로 REVISION 이벤트 조회 (다른 세션 혼입 방지)
- user_override 이력은 부록 A에 명시적으로 표시 (책임 추적)
- `consult`는 상태 파일을 컨텍스트가 아닌 파일로 관리 (컨텍스트 압축 대비)
- 재컨설팅 카운터는 매 변경 시 즉시 파일에 저장
- `consult` 개발은 generate-output 인터페이스 확정 후 마지막에 진행

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-03-06 | Phase 3 설계 초안 작성 (미시작 상태) |
| 2026-03-09 | 설계 전면 갱신 — 공통 스키마 기반 출력, 재컨설팅 이력 부록, Deep AI 비교 부록, session_id 필터, consult 오케스트레이션 상세화 |
| 2026-03-09 | SKILL.md 완료 — generate-output v1.0, consult v1.0 / 신규 Reference: reconsult-guide.md(A/B/C 판정 기준), skill-map.md(전체 스킬 연동 관계) |
| 2026-03-09 | 테스트 실행 후 개선 — generate-output v1.1(요구사항 요약 섹션·출력 깊이 규칙·Quick/Deep 리스크 분기·[미검증] 태그·MS 지원 확인 헤더 추가), consult(타입 C→A 전환 명시·타입 A 전체 재출력 규칙·confirmed 추가 조건·changed A/B 분류 기준 추가), Python 코드 블록 → SKILL.md 방식으로 대체, logs/ 하위 폴더 분리(session/ 경로 수정) |
| 2026-03-10 | Phase 3 실행 검증 완료 — Quick(consult_20260310_001) + Deep(consult_20260310_002) 전체 흐름 실행 검증. generate-output v1.2(output_mode: integrated/user/developer/split 파라미터 추가). 재컨설팅 타입 A/B/C + user_override 4개 시나리오 검증. Codex CLI 버그(trusted directory) 발견 및 --skip-git-repo-check 플래그로 해결. test-log 14건 기록. skill references 구조화(blocklist.md → 스킬 하위/reconsult-guide.md → consult/references/). skill-template references 생성 가이드 추가. |
