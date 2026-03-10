---
name: ai-analysis
version: 2.0
description: AI 모델 호출 이력(AI_CALL), 채점/평가 결과(SCORE), Fallback 전환(FALLBACK), 세션 상태(SESSION_STATE), 재컨설팅 이력(REVISION), 모드 전환(MODE_SWITCH), MS 지원 확인(MS_VERIFY)을 JSONL 형식으로 기록하고 조회한다. "AI 호출 기록해줘", "재컨설팅 기록해줘", "세션 로그 보여줘" 등의 요청 시 트리거한다.
depends_on: []
produces:
  - logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl
---

# AI Analysis Logger Skill

AI 모델 실행 이력 및 컨설팅 세션 전체 이벤트를 JSONL 파일에 기록하고 조회한다.
스키마 및 포맷 상세는 `references/schema.md`를 참고한다.

---

## 이 스킬을 호출하는 스킬

| 스킬 | 기록 시점 | 이벤트 타입 |
|---|---|---|
| `parse-requirement` | 세션 상태 파일 초기화 후 | SESSION_STATE |
| `ai-score-compare` | Codex/Gemini/Claude 호출 시마다 | AI_CALL |
| `ai-score-compare` | 외부 CLI 호출 실패 시 | FALLBACK |
| `ai-score-compare` | 리스크 평가 + 권고안 확정 후 | SCORE (후보별 1건) |
| `consult` | 재컨설팅 발생 시 (타입 A/B) | REVISION |
| `consult` | Quick→Deep 모드 전환 시 | MODE_SWITCH |
| `consult` | MS 지원 확인 완료 시 | MS_VERIFY |
| `consult` | 재컨설팅 카운터 변경 시마다 | SESSION_STATE |

사용자가 직접 기록 요청 시에도 동일하게 처리한다.

---

## STEP 1 — 스키마 로드

기록 또는 조회 전 반드시 먼저 실행:

```
Read(".claude/skills/ai-analysis/references/schema.md")
```

→ 이벤트 타입별 data 구조, message 형식, 출력 포맷 확인

---

## STEP 2 — 기록

1. 오늘 날짜 기준 파일 경로 결정: `logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl`
2. `logs/ai_analysis/` 디렉토리 없으면 Bash로 생성: `mkdir -p logs/ai_analysis`
3. 파일 없으면 Write로 신규 생성, 있으면 Edit으로 마지막 줄 뒤에 추가
4. 아래 이벤트 타입 판단 기준으로 JSON 한 줄 작성

---

## 이벤트 타입 판단 기준

```
AI 모델을 호출했다 (성공·실패 무관)        → AI_CALL
호출 실패로 다른 모델로 전환했다            → AI_CALL(실패) + FALLBACK 순서로 연속 기록
리스크 평가 + 권고안 확정이 완료됐다        → SCORE (후보 수만큼 반복)
세션 카운터 상태를 저장해야 한다            → SESSION_STATE
재컨설팅이 발생했다 (타입 A 또는 B)         → REVISION
Quick→Deep 모드 전환이 발생했다            → MODE_SWITCH
MS 지원 확인(WebSearch)이 완료됐다          → MS_VERIFY
```

---

## 이벤트 스키마

### AI_CALL
```json
{
  "timestamp": "2026-03-09T10:00:00+09:00",
  "session_id": "consult_20260309_001",
  "module": "ai-score-compare",
  "event_type": "AI_CALL",
  "message": "AI 호출 성공: codex [Deep]",
  "data": {
    "model": "codex",
    "mode": "Deep",
    "tokens_used": 1240,
    "success": true,
    "latency_ms": 4200
  }
}
```

### FALLBACK
```json
{
  "timestamp": "...",
  "session_id": "consult_20260309_001",
  "module": "ai-score-compare",
  "event_type": "FALLBACK",
  "message": "Fallback 전환: codex → claude",
  "data": {
    "failed_model": "codex",
    "reason": "timeout",
    "fallback_to": "claude"
  }
}
```

### SCORE
```json
{
  "timestamp": "...",
  "session_id": "consult_20260309_001",
  "module": "ai-score-compare",
  "event_type": "SCORE",
  "message": "리스크 평가 완료: PowerAutomate+SharePointList+Outlook",
  "data": {
    "solution_id": "PowerAutomate+SharePointList+Outlook",
    "solution_name": "Power Automate + SharePoint List + Outlook",
    "mode": "Quick",
    "risks": {
      "보안": {"description": "DLP 정책 차단 가능", "drop_risk": true},
      "라이선스": {"description": "M365 Business Basic 필요", "drop_risk": true},
      "운영": {"description": "발송 실패 알림 없음", "drop_risk": false}
    },
    "verdict": "권장"
  }
}
```

### SESSION_STATE
```json
{
  "timestamp": "...",
  "session_id": "consult_20260309_001",
  "module": "consult",
  "event_type": "SESSION_STATE",
  "message": "세션 상태 저장",
  "data": {
    "light_revision_count": 1,
    "total_revision_count": 1,
    "ms_verify_retry_count": 0,
    "current_revision": 1,
    "solution_id_current": "PowerAutomate+SharePointList+Outlook",
    "mode": "quick"
  }
}
```

### REVISION
```json
{
  "timestamp": "...",
  "session_id": "consult_20260309_001",
  "module": "consult",
  "event_type": "REVISION",
  "message": "경량 재컨설팅 — 타입 A",
  "data": {
    "revision": 1,
    "type": "A",
    "prev_solution_id": "PowerAutomate+Outlook",
    "new_solution_id": "PowerAutomate+SharePointList+Outlook",
    "change_reason": "고객사 목록 관리 편의를 위해 SharePoint List 추가",
    "user_override": false
  }
}
```

타입 B + 사용자 override 시:
```json
{
  "data": {
    "revision": 2,
    "type": "B",
    "prev_solution_id": "PowerAutomate+SharePointList+Outlook",
    "new_solution_id": "AzureLogicApps+Outlook",
    "change_reason": "DLP 정책으로 Power Automate 차단 확인",
    "user_override": true,
    "override_warning": "타입 B(전체 재컨설팅 권장) → 사용자 요청으로 경량 진행"
  }
}
```

### MODE_SWITCH
```json
{
  "timestamp": "...",
  "session_id": "consult_20260309_001",
  "module": "consult",
  "event_type": "MODE_SWITCH",
  "message": "모드 전환: quick → deep",
  "data": {
    "from": "quick",
    "to": "deep",
    "seed_revision": 2,
    "light_revision_count_reset": true,
    "total_revision_count_after": 3
  }
}
```

### MS_VERIFY
```json
{
  "timestamp": "...",
  "session_id": "consult_20260309_001",
  "module": "consult",
  "event_type": "MS_VERIFY",
  "message": "MS 지원 확인 완료: confirmed",
  "data": {
    "solution_id": "PowerAutomate+SharePointList+Outlook",
    "searched_features": [
      "Power Automate schedule trigger",
      "Power Automate Outlook connector external"
    ],
    "result": "confirmed",
    "action": "none",
    "ms_verify_retry_count": 0
  }
}
```

`result` 값:
- `confirmed` — 지원 확인, 진행
- `changed` — 기능 변경 감지, A/B 분류 후 재컨설팅
- `deprecated` — deprecated 확인, 타입 B 자동 분류

---

## STEP 3 — 조회

1. 해당 날짜 JSONL 파일 Read
2. **반드시 session_id 필터 적용**: `event.session_id == current_session_id`
3. 요청된 추가 필터 적용 (event_type / module)
4. schema.md의 출력 포맷에 맞게 표시

### session_id 필터 적용 이유
같은 날 여러 컨설팅 세션이 로그에 혼재하므로,
조회 시 반드시 현재 session_id로 필터링해야 다른 세션 데이터가 섞이지 않는다.

### 요약 조회 항목
- `AI_CALL`의 `tokens_used` 합산 → 총 토큰
- `FALLBACK` 건수 + 전환 내역
- `REVISION` 이력 요약 (revision 번호 / 타입 / 변경 이유)
- `SESSION_STATE` 최신 값 → 현재 카운터 상태

---

## 실패 처리

| 실패 유형 | 처리 방법 |
|---|---|
| `logs/ai_analysis/` 디렉토리 없음 | Bash로 `mkdir -p logs/ai_analysis` 후 재시도 |
| 파일 읽기 실패 | 경로 재확인 후 사용자에게 알림 |
| 파일 쓰기 실패 | 사용자에게 실패 내용 직접 출력 후 중단 |
| schema.md 로드 실패 | schema.md 경로 확인 요청 후 중단 |
| session_id 없음 (조회 시) | 전체 로그 반환하되 "세션 필터 미적용" 경고 표시 |

---

## 주의사항

- JSONL 특성상 JSON 한 줄로 기록 — 줄바꿈 없이 작성
- `session_id`는 parse-requirement에서 생성된 값을 모든 이벤트에 일관 적용
- AI_CALL 실패 시 `tokens_used`는 반드시 `0` (추정값 기입 금지)
- SCORE는 후보 솔루션마다 개별 기록
- SESSION_STATE는 재컨설팅 카운터가 변경될 때마다 즉시 기록 (컨텍스트 압축 대비)
- 조회 시 session_id 필터 생략 금지 (세션 간 데이터 혼입 방지)
- `logs/` 디렉토리는 `.gitignore`에 추가
