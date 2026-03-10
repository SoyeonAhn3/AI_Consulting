---
name: parse-requirement
version: 4.0
description: 사용자의 자유 형식 업무 자동화 요구사항을 업무 도메인/자동화 대상/현재 도구/제약 조건으로 구조화하고 불명확 항목은 추가 질문으로 보완한다. 입력 언어(한국어/영문)를 자동 감지하여 동일 언어로 파싱 결과를 반환한다. session_id를 생성하고 세션 상태 파일을 초기화한다.
depends_on: []
produces:
  - ParsedRequirement 구조체
  - logs/session/session_YYYYMMDD_NNN.json (세션 상태 파일 신규 생성)
  - logs/dev/dev_YYYYMMDD.jsonl (파싱 완료 INFO 기록)
---

# Parse Requirement Skill

사용자의 자유 형식 업무 자동화 요구사항을 Claude LLM이 직접 분석하여 구조화된 `ParsedRequirement`로 변환한다.
파싱 확정 시 session_id를 생성하고 세션 상태 파일을 초기화한다.
스키마 및 도메인 분류 기준은 `references/parsing-guide.md`를 참고한다.

---

## 출력 구조 (ParsedRequirement)

| 필드 | 설명 | 예시 |
|---|---|---|
| `session_id` | 세션 식별자 (자동 생성) | "consult_20260309_001" |
| `domain` | 업무 도메인 | "재무/회계" |
| `automation_targets` | 자동화 대상 프로세스 목록 | ["월마감 데이터 취합", "SAP 전표 입력"] |
| `current_tools` | 현재 사용 중인 도구 목록 | ["Excel", "SAP"] |
| `constraints` | 제약 조건 목록 | ["Microsoft 365 E3 보유"] |
| `ms_products_hint` | 추론된 MS 제품 힌트 | ["Power Automate", "Azure Logic Apps"] |
| `external_systems` | 연동이 필요한 외부 시스템 | ["SAP", "ERP"] |
| `process_type` | 프로세스 실행 유형 | "정기실행" \| "이벤트기반" \| "수동트리거" \| "복합" |
| `technical_unknowns` | 기술 불명확 항목 | ["SAP API 접근 권한 미확인"] |
| `operational_params` | 도메인별 운영 파라미터 (조건부) | `{"send_volume": "소규모", "has_attachment": false}` |
| `clarification_needed` | 추가 질문 필요 항목 | ["현재 사용 중인 라이선스가 있나요?"] |
| `confidence` | 파싱 신뢰도 (0.0 ~ 1.0) | 0.75 |
| `input_language` | 입력 언어 (자동 감지) | `"ko"` \| `"en"` |

`operational_params`는 도메인에 따라 조건부 수집:
- 이메일/발송 도메인: `send_volume` / `has_attachment` / `needs_retry` / `needs_send_log`
- 문서/결재 도메인: `needs_version_control` / `needs_access_control`
- 데이터/분석 도메인: `data_refresh_cycle` / `data_volume`

---

## STEP 1 — 파싱 가이드 로드

파싱 전 반드시 먼저 실행:

```
Read(".claude/skills/parse-requirement/references/parsing-guide.md")
```

→ 도메인 분류 기준, 신뢰도 계산 공식, 경고 조건 확인

---

## STEP 1-5 — 입력 언어 감지

STEP 2 파싱 전 입력 텍스트의 언어를 감지한다.

```
[언어 감지 규칙]
- 한국어 문자(가-힣) 포함 → input_language = "ko"
- 영문 전용 (라틴 문자 주체) → input_language = "en"
- 혼합 시 → 주요 언어 기준으로 판단 (한국어 단어 3개 이상이면 "ko")

→ 이후 모든 파싱 결과, 확인 화면, 질문, 오류 메시지를 input_language 언어로 출력
```

---

## STEP 2 — Claude가 요구사항 파싱

아래 기준으로 Claude가 사용자 입력을 분석한다.
**모든 출력 텍스트는 input_language 언어로 작성한다.**

```
입력 텍스트를 읽고 아래 항목을 추출하세요.

[domain]
- parsing-guide.md의 도메인 목록에서 가장 적합한 1개 선택
- 영문 입력 시 영문 도메인명 사용 가능 (예: "Finance/Accounting", "Sales/CRM")
- 복수 도메인이 감지되면 domain에 후보 목록 나열 (사용자 선택 필요)

[automation_targets]
- 한국어: "자동화하고 싶다", "~하는 작업", "~처리", "~발송" 등
- 영문: "automate", "process", "send", "generate" 등의 동사 패턴
- 여러 개면 개별 항목으로 분리

[current_tools]
- 현재 사용 중인 도구/시스템 추출 (Excel, SAP, 이메일 등)

[constraints]
- 라이선스, 보안 정책, 기간, 예산 등 제약 조건 추출

[external_systems]
- current_tools 중 MS 제품이 아닌 외부 엔터프라이즈 시스템 별도 분류
- SAP, ERP, CRM, Salesforce, Oracle 등

[ms_products_hint]
- external_systems가 있으면 Azure Logic Apps 포함 고려
- 요구사항에서 명시된 MS 제품 + 도메인/패턴에서 추론

[process_type]
- 한국어: "매주", "매일", "정기" → 정기실행 / "~하면", "~발생 시" → 이벤트기반
- 영문: "every day/week", "scheduled", "recurring" → Scheduled
         "when", "triggered by", "on event" → Event-based
         "on request", "manually" → Manual trigger
- 복수 패턴 혼합 → 복합 / Mixed

[technical_unknowns]
- 기술 구현에 불명확한 부분 (API 접근 권한, 데이터 형식, 시스템 연동 가능 여부 등)

[clarification_needed]
- 위 항목을 채우는 데 필요한 추가 정보가 있으면 질문으로 기재
- 영문 입력이면 영문 질문으로 작성
```

---

## STEP 3 — 신뢰도 계산

parsing-guide.md의 신뢰도 공식으로 계산:

```
domain 확인됨       → +40점
automation_targets  → +30점 (1개 이상 존재)
current_tools       → +15점 (1개 이상 존재)
ms_products_hint 또는 external_systems → +15점 (1개 이상 존재)
합계 / 100 = confidence (0.0 ~ 1.0)
```

---

## STEP 4 — 확인 화면 출력 (항상 표시)

파싱 결과를 아래 형식으로 출력하고 사용자 확인을 요청한다.
**사용자가 응답하기 전까지 절대 다음 단계로 진행하지 말 것.**
**확인 화면 전체를 input_language 언어로 출력한다.**

```
[input_language = "ko" 시]
=== 요구사항 파싱 결과 ===

  업무 도메인     : [domain]
  자동화 대상     : [automation_targets 목록]
  현재 도구       : [current_tools 목록]
  외부 시스템     : [external_systems 목록 또는 "(없음)"]
  프로세스 유형   : [process_type]
  제약 조건       : [constraints 또는 "(없음)"]
  MS 제품 힌트    : [ms_products_hint 목록]
  기술 불명확     : [technical_unknowns 목록 또는 "(없음)"]
  파싱 신뢰도     : [confidence × 100]%
  입력 언어       : 한국어 (ko)

  [⚠️ 경고] (해당 항목만 표시)
  - 신뢰도 50% 미만: 파싱 정확도가 낮습니다. 보완 후 재파싱을 권장합니다.
  - 복합 도메인 감지: [후보 도메인 목록] 중 1개를 선택해주세요.
  - 자동화 대상 불명확: 구체적인 업무 프로세스를 추가해주세요.
  - 외부 시스템 감지: [external_systems] 연동 필요. 기술 검토가 필요할 수 있습니다.

  [추가 확인 필요]
  Q1. [clarification_needed[0]]
  Q2. [clarification_needed[1]]
  ...

---
## ❓ 이 결과가 맞나요?
1. 네, 맞습니다 → 모드 선택으로 진행 (Quick / Deep)
2. 아니오, 수정이 필요합니다 → 아래에 수정 내용을 입력해주세요
---

[input_language = "en" 시]
=== Requirement Parsing Result ===

  Business Domain   : [domain]
  Automation Target : [automation_targets list]
  Current Tools     : [current_tools list]
  External Systems  : [external_systems list or "(none)"]
  Process Type      : [process_type]
  Constraints       : [constraints or "(none)"]
  MS Products Hint  : [ms_products_hint list]
  Tech Unknowns     : [technical_unknowns list or "(none)"]
  Parse Confidence  : [confidence × 100]%
  Input Language    : English (en)

  [⚠️ Warning] (show only applicable items)
  - Confidence below 50%: Parsing accuracy is low. Please add more detail.
  - Multiple domains detected: Please select one from [candidate list].
  - Automation target unclear: Please specify the exact business process.
  - External system detected: [external_systems] integration may require technical review.

  [Clarification Needed]
  Q1. [clarification_needed[0]]
  Q2. [clarification_needed[1]]
  ...

---
## ❓ Does this look correct?
1. Yes, proceed → Mode selection (Quick / Deep)
2. No, I need to correct something → Please enter your corrections below
---
```

---

## STEP 5 — 수정 처리 (최대 2회)

사용자가 "아니오"를 선택하거나 수정 내용을 입력하면:

1. 사용자 입력을 원본 요구사항에 추가하여 STEP 2부터 재파싱
2. 재파싱 후 STEP 4 확인 화면 재출력
3. **수정 루프는 최대 2회** — 2회 초과 시 아래 직접 입력 폼으로 전환

```
[직접 입력 폼]
2회 수정 후에도 파싱이 정확하지 않습니다.
아래 항목을 직접 입력해주세요:

  도메인 (예: 재무/회계, 구매/조달):
  자동화 대상 (쉼표 구분):
  현재 사용 도구 (쉼표 구분):
  외부 시스템 (SAP/ERP 등, 없으면 빈칸):
  제약 조건 (없으면 빈칸):
  MS 제품 선호 (없으면 빈칸):
```

직접 입력값을 그대로 ParsedRequirement에 반영하고 confidence = 1.0으로 설정.

---

## STEP 6 — session_id 생성 및 상태 파일 초기화

사용자가 파싱 결과를 확정(STEP 4에서 "네, 맞습니다")한 직후 실행.

### session_id 생성 규칙

```
형식: consult_YYYYMMDD_NNN
  YYYYMMDD : 오늘 날짜
  NNN      : 오늘 날짜 기준 세션 순번 (001부터 시작)

순번 결정:
  1. logs/session/ 디렉토리에서 오늘 날짜의 session_*.json 파일 수 확인
  2. 파일 수 + 1이 순번
  예) logs/session/session_20260309_001.json 이미 존재 → 새 세션은 002
```

### 상태 파일 초기화

```
파일 경로: logs/session/session_YYYYMMDD_NNN.json

{
  "session_id": "consult_20260309_001",
  "mode": null,
  "input_language": "ko",        ← parse-requirement에서 감지한 언어 ("ko" | "en")
  "output_language": null,       ← consult STEP 6에서 사용자 선택 후 설정
  "current_revision": 0,
  "solution_id_current": null,
  "light_revision_count": 0,
  "total_revision_count": 0,
  "ms_verify_retry_count": 0,
  "created_at": "[현재 ISO 시각]",
  "updated_at": "[현재 ISO 시각]"
}
```

생성 후 아래 안내 출력:

```
세션 ID: consult_20260309_001

어떤 모드로 컨설팅을 진행할까요?

1. Quick 모드 — Claude 단독 분석 (빠름, ~1분)
2. Deep 모드  — AI 3종 분석 + 상호 리뷰 (정확, ~5분)

번호로 답변해주세요.
```

---

## STEP 7 — dev-log 기록

세션 초기화 완료 후 dev-log 스킬로 기록:

```
[dev-log에 기록할 내용]
event_type : INFO
module     : parse-requirement
message    : 요구사항 파싱 완료 및 세션 초기화
data:
  session_id        : [생성된 session_id]
  domain            : [domain]
  targets_count     : [automation_targets 개수]
  confidence        : [confidence]
  external_systems  : [external_systems 목록]
  process_type      : [process_type]
  clarification_cnt : [clarification_needed 개수]
  revision_count    : [수정 횟수 0~2, 또는 "direct_input"]
```

---

## 실패 처리

| 실패 유형 | 처리 방법 |
|---|---|
| 신뢰도 50% 미만 (첫 파싱) | 경고 표시 후 STEP 4 확인 화면에서 수정 유도 |
| 2회 수정 후에도 신뢰도 50% 미만 | 직접 입력 폼으로 전환 |
| 복합 도메인 감지 | 확인 화면에서 경고 표시 + 사용자 선택 요청 |
| logs/ 디렉토리 없음 | Bash로 `mkdir -p logs/session && mkdir -p logs/dev` 후 재시도 |
| 상태 파일 생성 실패 | 사용자에게 알림 후 session_id 없이 계속 진행 (파싱 결과는 반환) |
| dev-log 기록 실패 | 파싱 결과는 반환, dev-log 스킵 후 사용자 알림 |
| parsing-guide.md 로드 실패 | 경로 확인 요청 후 중단 |

---

## 주의사항

- 사용자가 STEP 4에서 확정하기 전까지 session_id 생성 금지
- 사용자가 STEP 4에서 확정하기 전까지 모드 선택 화면 표시 금지
- external_systems는 current_tools와 별도 필드로 관리 (중복 저장 가능)
- process_type이 "복합"이면 technical_unknowns에 복잡도 관련 항목 추가
- 직접 입력 폼 사용 시 confidence를 1.0으로 설정 (사용자가 직접 확인한 값)
- session_id는 이후 모든 로그 이벤트에 반드시 포함
- input_language는 세션 파일에 저장하여 이후 consult 흐름에서 output_language 기본값으로 활용

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-09 | v3.0 | session_id 생성 + 세션 상태 파일 초기화 추가 |
| 2026-03-10 | v4.0 | 다국어 지원 추가 — STEP 1-5 입력 언어 자동 감지(ko/en), STEP 2 영문 키워드 파싱, STEP 4 이중 언어 확인 화면, 세션 파일 input_language/output_language 필드 추가 |
