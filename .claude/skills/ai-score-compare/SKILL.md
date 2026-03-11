---
name: ai-score-compare
version: 3.4
description: MS 생태계 내 자유 제안 + 리스크 2패스 평가로 권고안을 도출한다. Quick 모드는 Claude 단독 자유 분석, Deep 모드는 AI 3종 독립 제안 + Orchestrator 상호 리뷰 + 공통 강점/리스크 추출로 처리한다. parse-requirement 완료 후 모드 선택 시 자동 실행된다.
depends_on:
  - parse-requirement
  - ms-solution-recommend (Deep 모드만)
  - ai-analysis
produces:
  - SolutionProposal (공통 스키마 출력)
  - logs/ai_analysis_YYYYMMDD.jsonl (AI_CALL / FALLBACK / SCORE 기록)
---

# AI Score Compare Skill

MS 생태계 내에서 자유 제안된 솔루션에 대해 리스크 2패스 평가로 권고안을 도출한다.

- **Quick 모드**: Claude 자유 분석 → blocklist 체크 → 리스크 2패스 → 출력
- **Deep 모드**: AI 3종 자유 제안 → Orchestrator 리뷰 → 공통 강점/리스크 → 리스크 2패스 → 출력

---

## 공통 출력 스키마

Quick/Deep 모두 동일한 기본 스키마 사용:

```
솔루션명
솔루션 ID   : 핵심 MS 제품 조합 (공백 없는 "제품명+제품명" 형식)
              예) PowerAutomate+SharePointList+Outlook
적용 이유
구현 개요   : 단계 목록
전제조건
한계점
리스크 및 고려사항
  (보안)    리스크명: 설명 / [탈락가능성: YES|NO] / 대응방안
  (라이선스) 리스크명: 설명 / [탈락가능성: YES|NO] / 대응방안
  (운영)    리스크명: 설명 / 대응방안
  고려사항  : 확인/결정 필요 사항
판정        : 권장 | 검토필요 | 비추천
```

**리스크 출력 깊이·[미검증] 태그 규칙:**
→ `risk-evaluation-guide.md` 참조 (STEP 0에서 로드)

---

## STEP 0 — 사전 로드

평가 전 반드시 먼저 실행:

```
Read(".claude/skills/ai-score-compare/references/risk-evaluation-guide.md")
Read(".claude/skills/ai-score-compare/references/ms-product-catalog.md")
```

- `risk-evaluation-guide.md` → 리스크 카테고리, 탈락 가능성 판단 기준, 판정 기준
- `ms-product-catalog.md` → 제안 가능한 전체 MS 제품군 및 라이선스 확인

---

## ━━ QUICK 모드 ━━

### Q-STEP 1 — Claude 자유 분석

ms-solution-recommend를 호출하지 않는다.
Claude가 ParsedRequirement를 기반으로 MS 생태계 내에서 자유롭게 솔루션을 도출한다.

```
[분석 지시]
요구사항: [ParsedRequirement 전체 내용]
제약: MS 생태계 내 솔루션만 제안

아래를 기준으로 최대 3개 솔루션을 자유롭게 제안하세요.
- 요구사항에 가장 적합한 MS 제품 조합
- 구현 가능성과 운영 편의성 고려
- 각 솔루션은 서로 다른 접근 방식이어야 함
- solutions.md 목록에 없는 제품도 자유롭게 제안 가능
```

최대 3개 후보 도출 (최소 1개 필수).

### Q-STEP 2 — blocklist.md 차단 체크

```
Read("references/blocklist.md")
```

각 후보의 제품 목록을 blocklist.md와 대조.
→ 차단 처리 규칙: `risk-evaluation-guide.md — blocklist 차단 처리` 참조

### Q-STEP 3 — 1패스: 후보별 리스크 평가

각 후보에 대해 권고안 미확정 상태에서 리스크를 평가한다.

**평가 질문 및 카테고리, 표시 기준:**
→ `references/risk-evaluation-guide.md` 참조 (STEP 0에서 로드)

### Q-STEP 4 — 2패스: 권고안 확정

**판정 기준:**
→ `references/risk-evaluation-guide.md` 참조 (판정 기준, 비추천안 포함 조건)

### Q-STEP 4-5 — ROI 사전 계산 (Method F)

ParsedRequirement의 `weekly_hours`가 존재하면 권장안 난이도 기준으로 roi_calc를 계산한다.
(weekly_hours 없으면 이 단계 스킵)

```
effort=낮음 → 개선 후 잔여: 5~10분/주,  구축 소요: 4~8시간
effort=중간 → 개선 후 잔여: 10~20분/주, 구축 소요: 8~20시간
effort=높음 → 개선 후 잔여: 20~30분/주, 구축 소요: 20~40시간

roi_calc = {
  "current_weekly_min":  [weekly_hours × 60],
  "improved_weekly_min": [잔여 범위 중간값],
  "save_weekly_min":     [current - improved],
  "annual_save_hrs":     [save_weekly_min × 52 / 60],
  "build_time_hrs":      [구축 소요 범위 — "N~M시간"],
  "payback_weeks":       [build_time 최소 / save_weekly_min × 60 기준 추정 — "N~M주"]
}
→ 권장안 SolutionProposal에 roi_calc 첨부하여 generate-output에 전달
```

### Q-STEP 5 — 출력

기본 출력: 요약 포맷. 사용자가 "[N]안 상세보기" 요청 시 해당 솔루션 전체 형식 출력.

**[기본 — 요약 포맷]**
```
======================================================
  Quick 모드 솔루션 제안 | session: [session_id]
======================================================

### ✅ 1안: [솔루션명] [미검증 시 → [미검증]] — 권장
- 핵심 기능: [요구사항에서 자동화되는 핵심 업무 1줄]
- 구현 방식: [핵심 MS 제품 흐름 — 예: SharePoint 트리거 → Approval → Teams 알림]
- 난이도: [낮음|중간|높음] | 라이선스: [필요 라이선스]
- 주요 리스크: [핵심 리스크 1줄]

---

### ⚠️ 2안: [솔루션명] — 검토필요 (있으면)
- 핵심 기능: ...
- 구현 방식: ...
- 난이도: ... | 라이선스: ...
- 주요 리스크: ...

---

### ❌ 비추천: [솔루션명] (교육적 가치 있을 때만)
- 비추천 이유: [1줄]

======================================================
상세 분석이 필요한 항목을 말씀해주세요. (예: "1안 상세보기")
```

**[상세보기 요청 시 — 전체 형식]**
```
[N안 — 판정] 상세
솔루션명: [이름]
솔루션 ID: [제품조합ID]
적용 이유: ...
구현 개요:
  1. ...
  2. ...
전제조건:
  - ...
한계점:
  - ...
리스크 및 고려사항:
  (보안) [리스크명]: [1줄 설명] → 대응: [짧게]
  (라이선스) [리스크명]: [1줄 설명] → 대응: [짧게]
  (운영) [리스크명]: [1줄 설명]
  고려사항: [확인 필요 사항]
판정: [판정]
```

### Q-STEP 6 — ai-analysis 기록

각 후보별 SCORE 이벤트 기록:

```
[ai-analysis에 기록]
event_type    : SCORE
session_id    : [session_id]
module        : ai-score-compare
solution_id   : [솔루션 ID]
solution_name : [솔루션명]
mode          : Quick
risks         : {각 리스크별 탈락 가능성}
verdict       : [판정]
```

---

## ━━ DEEP 모드 ━━

### D-STEP 1 — AI 상태 확인

```bash
codex --version 2>/dev/null || echo "codex: 미설치"
gemini --version 2>/dev/null || echo "gemini: 미설치"
```

```
3개 성공 → 정상 Deep 진행
2개 성공 → 경고 표시 후 사용자 선택
             "Codex/Gemini 중 하나를 사용할 수 없습니다.
              1. 2 AI Deep으로 계속 진행
              2. Quick 모드로 전환"
1개 성공 → Deep 중단, Quick 자동 전환 + 안내
             "외부 AI CLI를 사용할 수 없어 Quick 모드로 전환합니다."

실행 AI 수는 최종 출력 및 산출물에 반드시 명시:
  실행 AI: Codex ✅/❌ | Gemini ✅/❌ | Claude ✅
```

→ Deep 진행 확정 시:
```
Read(".claude/skills/ai-score-compare/references/deep-mode-guide.md")
```
(D-STEP 3 AI 프롬프트 구조 + bash 호출, D-STEP 5 Orchestrator 리뷰 형식 포함)

### D-STEP 2 — solutions.md 컨텍스트 준비

ms-solution-recommend 스킬 호출:

```
ms-solution-recommend 실행
  → solutions_context 수신 (검증 데이터 참고용)
  → blocklist_context 수신 (차단 목록)
```

### D-STEP 3 — 3 AI 순차 실행 (독립 제안서)

→ deep-mode-guide.md 참조 (프롬프트 구조, output_language 분기, Codex/Gemini/Claude 호출, JSON 파싱)

각 AI 호출마다 AI_CALL 이벤트 기록.

### D-STEP 4 — blocklist 차단 체크

3개 제안서 각각에 대해 blocklist 체크:
- 차단 제품 포함 시 해당 제안서 제외 + 사유 표시

### D-STEP 5 — Claude Orchestrator: 상호 리뷰 구조화

→ deep-mode-guide.md 참조 (Codex/Gemini/Claude 각 입장 반론 구조화 형식)
(실제 Codex/Gemini 재호출 없음 — Claude가 시뮬레이션)

### D-STEP 6 — 공통 강점 / 공통 리스크 추출

```
공통 강점: 2개 이상 AI가 동일하게 채택한 접근법
공통 리스크: 2개 이상 AI가 공통으로 언급한 리스크
차이점: AI별 고유 인사이트 (상호 리뷰에서 도출된 추가 요소)
```

### D-STEP 7 — 1패스 → 2패스 리스크 평가

Quick의 Q-STEP 3~4와 동일한 기준 적용.
단, Deep은 상세 형식 사용 (영향도 + 발생조건/확인방법 + 대응방안).

상호 리뷰에서 도출된 추가 리스크/전제조건도 포함.

### D-STEP 7-5 — ROI 사전 계산 (Method F)

Q-STEP 4-5와 동일한 roi_calc 계산 로직 적용.
권장안 난이도 기준, weekly_hours 존재 시에만 실행.

```
effort=낮음 → 잔여: 5~10분/주,  구축: 4~8시간
effort=중간 → 잔여: 10~20분/주, 구축: 8~20시간
effort=높음 → 잔여: 20~30분/주, 구축: 20~40시간

→ roi_calc 계산 후 권장안 SolutionProposal에 첨부
→ generate-output의 proposals[권장안].roi_calc로 전달 (roi-estimation-guide.md 로드 불필요)
```

### D-STEP 8 — 출력

기본 출력: 요약 포맷 + Deep 전용 AI 비교. 사용자가 "[N]안 상세보기" 요청 시 해당 솔루션 전체 형식 출력.

**[기본 — 요약 포맷]**
```
======================================================
  Deep 모드 솔루션 제안 | session: [session_id]
  실행 AI: Codex ✅ | Gemini ✅ | Claude ✅ (3/3)
======================================================

### ✅ 1안: [솔루션명] [미검증 시 → [미검증]] — 권장
- 핵심 기능: [요구사항에서 자동화되는 핵심 업무 1줄]
- 구현 방식: [핵심 MS 제품 흐름 — 예: SharePoint 트리거 → Approval → Teams 알림]
- 난이도: [낮음|중간|높음] | 라이선스: [필요 라이선스]
- 주요 리스크: [핵심 리스크 1줄]
- AI 합의: [3 AI 공통 채택 여부 — 예: "3/3 AI 공통 제안"]

---

### ⚠️ 2안: [솔루션명] — 검토필요 (있으면)
- 핵심 기능: ...
- 구현 방식: ...
- 난이도: ... | 라이선스: ...
- 주요 리스크: ...
- AI 합의: ...

---

[Deep 전용 부록]
AI별 제안 비교:
  항목         | Codex              | Gemini             | Claude
  ──────────────────────────────────────────────────────────────
  솔루션 ID    | [ID]               | [ID]               | [ID]
  특이점       | ...                | ...                | ...

공통 강점: ...
공통 리스크: ...

======================================================
상세 분석이 필요한 항목을 말씀해주세요. (예: "1안 상세보기")
```

**[상세보기 요청 시 — 전체 형식]**
```
[N안 — 판정] 상세
솔루션명: [이름]
솔루션 ID: [제품조합ID]
적용 이유: (3~5줄, 상호 리뷰 반영 내용 포함)
구현 개요:
  1. ...
전제조건:
  - ...
한계점:
  - ...
리스크 및 고려사항:
  (보안) [리스크명]:
    영향도: 높음/중간/낮음
    발생 조건/확인 방법: ...
    대응 방안: ...
    탈락 가능성: YES/NO
  (라이선스) ...
  (운영) ...
  고려사항: ...
판정: [판정]

상호 리뷰 요약:
  [이 솔루션에 대한 핵심 반론 요약]
```

### D-STEP 9 — ai-analysis 기록

```
AI_CALL: 각 AI 호출마다 (Codex / Gemini / Claude)
FALLBACK: CLI 실패 시
SCORE: 각 후보별
```

---

## 재컨설팅 연계

이 스킬은 재컨설팅 시 세션 상태를 참조해야 한다.

```
세션 상태 파일 READ: logs/session_YYYYMMDD_NNN.json
  → light_revision_count 확인 (3 초과 시 경고)
  → solution_id_current 확인 (타입 A/B 판단 기준)

재컨설팅 완료 후:
  → 세션 상태 파일 UPDATE
  → ai-analysis에 SESSION_STATE 이벤트 기록
```

---

## 실패 처리

| 실패 유형 | 처리 방법 |
|---|---|
| blocklist.md 로드 실패 | 경고 표시 후 차단 체크 없이 진행 |
| Codex CLI 실패/타임아웃 | FALLBACK 기록 + Gemini+Claude 2자 비교로 진행 |
| Gemini CLI 실패/인증 오류 | FALLBACK 기록 + Codex+Claude 2자 비교로 진행 |
| JSON 파싱 2회 실패 | 해당 AI 제외 + FALLBACK 기록 + 나머지로 진행 |
| 전체 외부 CLI 실패 | Deep 중단 → Quick 자동 전환 + 사용자 알림 |
| 차단 후 후보 0개 | "요구사항 재정의 또는 blocklist 재검토" 안내 |

---

## 주의사항

- Quick 모드에서 ms-solution-recommend 절대 호출 금지
- Deep 모드 프롬프트 순서: 요구사항 자유 분석 먼저, solutions.md 참고 나중
- 1패스와 2패스를 반드시 순서대로 분리 실행 (순환 의존 방지)
- 솔루션 ID는 "제품명+제품명" 형식, 공백 없이 작성
- solutions.md에 없는 제안은 [미검증] 태그 필수
- 재컨설팅 후에도 동일 스키마로 출력 (판정 변경 시 변경 이유 명시)
- 사용자가 권고안을 선택하기 전까지 MS 지원 확인(WebSearch) 실행 금지
- 기본 출력은 요약 포맷. 상세 분석은 사용자 "[N]안 상세보기" 요청 시에만 출력
- **채점 표 / 리스크 비교 표 / 후보 분석 표 출력 금지** — Q-STEP 5 / D-STEP 8 요약 포맷만 사용
- **분석 중간 과정(자유 제안 목록, 점수 계산 과정) 출력 금지** — 최종 요약 포맷만 출력

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-09 | v3.0 | 최초 작성 |
| 2026-03-10 | v3.1 | output_language en/en+ko 지원 추가 |
| 2026-03-10 | v3.2 | 출력 포맷 요약화 — Q-STEP 5, D-STEP 8 기본 출력을 요약 포맷으로 변경. 상세보기 트리거("[N]안 상세보기") 추가. Deep 요약에 AI 합의 필드 추가 |
| 2026-03-11 | v3.3 | 표 출력 금지 규칙 추가 — 채점표/리스크표/분석 중간 과정 표 금지, 요약 포맷만 출력 (~800 토큰 절감) |
| 2026-03-11 | v3.4 | Method F — ROI 사전 계산 추가: Q-STEP 4-5, D-STEP 7-5에서 weekly_hours 기반 roi_calc 계산 후 권장안에 첨부. generate-output의 roi-estimation-guide.md 로드 제거 (~300 토큰 절감) |
