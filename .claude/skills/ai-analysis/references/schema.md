# AI Analysis 스키마 정의

## 파일 경로 규칙

```
logs/ai_analysis_YYYYMMDD.jsonl
```

- 날짜는 로컬 시각 기준 (예: 2026-03-09 → `ai_analysis_20260309.jsonl`)
- `logs/` 디렉토리가 없으면 Bash로 생성: `mkdir -p logs`
- 파일이 없으면 Write로 신규 생성, 있으면 Edit으로 마지막 줄 뒤에 추가

---

## JSONL 엔트리 구조

각 라인은 JSON 객체 1개. 필드 순서는 아래를 따를 것.

```json
{
  "timestamp": "2026-03-09T10:32:01+00:00",
  "session_id": "a1b2c3d4",
  "module": "ai-score-compare",
  "event_type": "AI_CALL",
  "message": "AI 호출 성공: codex [Deep]",
  "data": { "model": "codex", "mode": "Deep", "tokens_used": 1240, "success": true, "latency_ms": 4200 }
}
```

| 필드 | 타입 | 규칙 |
|---|---|---|
| `timestamp` | string | ISO 8601 형식. 현재 시각 기준 |
| `session_id` | string | 한 대화 내에서 동일값 유지 (8자리 hex 권장) |
| `module` | string | 기록을 요청한 스킬명 (예: "ai-score-compare") |
| `event_type` | string | `AI_CALL` / `FALLBACK` / `SCORE` 중 하나만 사용 |
| `message` | string | 한 줄 요약 (50자 이내 권장) |
| `data` | object | 이벤트 타입별 필수 데이터 (아래 참고) |

---

## 이벤트 타입별 규칙

### AI_CALL — AI 모델 호출 이력

언제: Codex / Gemini / Claude 호출 시마다 기록 (성공·실패 모두)

`message` 형식:
```
성공: "AI 호출 성공: {model} [{mode}]"
실패: "AI 호출 실패: {model} [{mode}]"
```

`data` 필드:
```json
{
  "model":       "codex",
  "mode":        "Deep",
  "tokens_used": 1240,
  "success":     true,
  "latency_ms":  4200
}
```

| 필드 | 값 규칙 |
|---|---|
| `model` | `"codex"` / `"gemini"` / `"claude-sonnet-4-6"` |
| `mode` | `"Quick"` / `"Deep"` / `"Fallback"` |
| `tokens_used` | 실패 시 `0` |
| `success` | `true` / `false` |
| `latency_ms` | 응답까지 걸린 시간 (밀리초) |

예시:
```jsonl
{"timestamp":"2026-03-09T10:32:01+00:00","session_id":"a1b2c3d4","module":"ai-score-compare","event_type":"AI_CALL","message":"AI 호출 성공: codex [Deep]","data":{"model":"codex","mode":"Deep","tokens_used":1240,"success":true,"latency_ms":4200}}
{"timestamp":"2026-03-09T10:32:31+00:00","session_id":"a1b2c3d4","module":"ai-score-compare","event_type":"AI_CALL","message":"AI 호출 실패: gemini [Deep]","data":{"model":"gemini","mode":"Deep","tokens_used":0,"success":false,"latency_ms":30000}}
```

---

### FALLBACK — Fallback 모드 전환 이력

언제: 호출 실패로 다른 모델로 전환할 때. AI_CALL(실패) 기록 직후에 이어서 기록

`message` 형식:
```
"Fallback 전환: {failed_model} → {fallback_to}"
```

`data` 필드 (3개 필드 모두 필수):
```json
{
  "failed_model": "gemini",
  "reason":       "API timeout 30s 초과",
  "fallback_to":  "claude-sonnet-4-6"
}
```

예시:
```jsonl
{"timestamp":"2026-03-09T10:32:32+00:00","session_id":"a1b2c3d4","module":"ai-score-compare","event_type":"FALLBACK","message":"Fallback 전환: gemini → claude-sonnet-4-6","data":{"failed_model":"gemini","reason":"API timeout 30s 초과","fallback_to":"claude-sonnet-4-6"}}
```

---

### SCORE — 가중치 채점 결과

언제: ai-score-compare 채점 완료 후. 후보 솔루션마다 1건씩 기록

`message` 형식:
```
"채점 완료: {solution_name} (점수: {weighted_total})"
```

`data` 필드:
```json
{
  "solution_name":  "Power Automate + Teams 알림 자동화",
  "scores": {
    "적합성":         4.5,
    "구현난이도":     4.5,
    "유지보수성":     4.0,
    "라이선스적합성": 4.5,
    "확장성":         4.0
  },
  "weighted_total": 4.375,
  "rank":           1
}
```

| 필드 | 값 규칙 |
|---|---|
| `scores` | 5개 항목 모두 포함. 값은 1.0 ~ 5.0 (0.5 단위) |
| `weighted_total` | 소수점 4자리 반올림 |
| `rank` | 1 = 권고안, 2 = 대안, 0 = 미결정 |

예시:
```jsonl
{"timestamp":"2026-03-09T10:35:00+00:00","session_id":"a1b2c3d4","module":"ai-score-compare","event_type":"SCORE","message":"채점 완료: Power Automate + Teams 알림 자동화 (점수: 4.375)","data":{"solution_name":"Power Automate + Teams 알림 자동화","scores":{"적합성":4.5,"구현난이도":4.5,"유지보수성":4.0,"라이선스적합성":4.5,"확장성":4.0},"weighted_total":4.375,"rank":1}}
```

---

### ELIMINATED — 솔루션 자동 탈락 기록

언제: must_have_conditions 미충족으로 채점 전 탈락 처리될 때

`message` 형식:
```
"솔루션 탈락: {solution_name} ({elimination_code})"
```

`data` 필드 (3개 필드 모두 필수):
```json
{
  "solution_name":     "Power BI + Excel 데이터 대시보드",
  "elimination_code":  "M001",
  "elimination_reason":"이메일 발송 기능 없음. 시각화 도구로 요구사항 미충족",
  "unmet_conditions":  ["이메일 자동 발송이 자동화 대상인 경우"]
}
```

| 탈락 코드 | 의미 |
|---|---|
| M001 | 필수 기능 미충족 |
| M002 | 라이선스 조건 불일치 |
| M003 | 서비스 deprecated |
| M004 | 기술적 제약 (external_systems 연동 불가 등) |

예시:
```jsonl
{"timestamp":"2026-03-09T10:33:00+00:00","session_id":"a1b2c3d4","module":"ai-score-compare","event_type":"ELIMINATED","message":"솔루션 탈락: Power BI + Excel 데이터 대시보드 (M001)","data":{"solution_name":"Power BI + Excel 데이터 대시보드","elimination_code":"M001","elimination_reason":"이메일 발송 기능 없음. 시각화 도구로 요구사항 미충족","unmet_conditions":["이메일 자동 발송이 자동화 대상인 경우"]}}
```

---

## 조회 출력 포맷

`view` 요청 시 아래 형식으로 출력:

```
[2026-03-09 10:32:01] [SESSION:a1b2c3d4] [AI_CALL] ai-score-compare
  메시지: AI 호출 성공: codex [Deep]
  데이터: {"model": "codex", "mode": "Deep", "tokens_used": 1240, "success": true, "latency_ms": 4200}

[2026-03-09 10:32:32] [SESSION:a1b2c3d4] [FALLBACK] ai-score-compare
  메시지: Fallback 전환: gemini → claude-sonnet-4-6
  데이터: {"failed_model": "gemini", "reason": "API timeout 30s 초과", "fallback_to": "claude-sonnet-4-6"}

[2026-03-09 10:35:00] [SESSION:a1b2c3d4] [SCORE] ai-score-compare
  메시지: 채점 완료: Power Automate + Teams 알림 자동화 (점수: 4.375)
  데이터: {"solution_name": "Power Automate + Teams 알림 자동화", "scores": {...}, "weighted_total": 4.375, "rank": 1}

─── 총 3건 | 날짜: 20260309 ───
```

---

## 요약 출력 포맷

`summary` 요청 시 (토큰·Fallback 집계 포함):

```
=== AI Analysis 요약 [20260309] ===
  AI_CALL   : 3건
  FALLBACK  : 1건
  SCORE     : 2건
  ELIMINATED: 4건
  합계      : 10건
  총 토큰  : 2,340토큰
  Fallback : 1회 (gemini → claude-sonnet-4-6)
```

총 토큰: AI_CALL 이벤트의 `data.tokens_used` 합산
Fallback: FALLBACK 이벤트 건수 + 각 `failed_model → fallback_to` 나열

---

## 기록 순서 (AI_CALL 실패 시)

```
① AI_CALL 기록 (success: false, tokens_used: 0)
② FALLBACK 기록 (failed_model, reason, fallback_to)
③ 대체 모델로 재호출
④ AI_CALL 기록 (success: true)
```

---

## 주의사항

- JSONL 특성상 JSON 한 줄로 기록 — 줄바꿈 없이 작성
- `session_id`는 한 대화 내에서 동일값 유지
- `tokens_used`는 실패 시 반드시 `0` (추정값 기입 금지)
- SCORE는 후보 솔루션 수만큼 개별 기록 (3개 후보 → 3건)
- `logs/` 디렉토리는 `.gitignore`에 추가
