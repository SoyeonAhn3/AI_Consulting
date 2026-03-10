---
name: consult
version: 1.2
description: MS 업무 자동화 컨설팅 전체 흐름을 오케스트레이션한다. parse-requirement → 적합성 게이트 → 모드 선택 → ai-score-compare → 사용자 피드백 → 재컨설팅(A/B/C) → MS 지원 확인 → generate-output 순서로 실행한다. "컨설팅 시작해줘", "자동화 방법 알려줘", "업무 자동화 컨설팅" 등의 요청 시 트리거한다.
depends_on:
  - parse-requirement
  - ai-score-compare
  - ms-solution-recommend
  - ai-analysis
  - generate-output
produces:
  - output/[날짜]_[도메인]_[session_id]_자동화_컨설팅.txt
  - logs/session/session_YYYYMMDD_NNN.json (상태 갱신)
  - logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl (이벤트 기록)
---

# Consult Skill

MS 업무 자동화 컨설팅의 진입점이자 오케스트레이터.
Phase 1~3 전체 흐름을 세션 관리, 재컨설팅 분기, MS 지원 확인을 포함해 통합 실행한다.

---

## 전체 흐름 요약

```
[1]   parse-requirement          → ParsedRequirement + session_id 생성
[1-5] 적합성 게이트               → 진행 가능(자동) / 부분 지원(확인) / 지원 대상 아님(종료)
[2]   모드 선택 (Quick | Deep)
[3]   ai-score-compare           → SolutionProposal 목록
[4]   사용자 피드백               → 재컨설팅 분기 (A/B/C/모드전환)
[5]   권고안 선택 → MS 지원 확인
[6]   사용자 최종 확인
[7]   generate-output            → 산출물 파일
[8]   완료 보고
```

---

## STEP 1 — 요구사항 파싱

```
parse-requirement 스킬 실행
→ ParsedRequirement 확정
→ session_id 생성 (consult_YYYYMMDD_NNN)
→ logs/session/session_YYYYMMDD_NNN.json 초기화
```

사용자가 확정하기 전까지 다음 단계로 진행하지 않는다.

---

## STEP 1-5 — 적합성 게이트 (Scope Gate)

ParsedRequirement 확정 직후 실행. MS 업무자동화 범위에 적합한지 판정한다.

### 판정 기준 필드

```
domain            → 사무 도메인인가? (제조설비/의료기기/산업자동화 → 거절 방향)
automation_targets → MS 제품으로 실현 가능한가?
external_systems  → 핵심이 MS 외부 시스템인가? (ERP 내부 로직, PLC 직접 제어 등)
current_tools     → 현재 도구가 MS 생태계인가?
```

### 판정 규칙

```
[지원 대상 아님] — 아래 중 하나라도 해당
  · automation_targets의 핵심이 하드웨어/설비/PLC 직접 제어
  · domain이 제조 현장 자동화, 의료기기 제어, 산업 자동화이고 MS 접점 없음
  · external_systems이 메인이고 MS와 연결 불가한 구조

[부분 지원 가능] — 아래 중 하나라도 해당
  · external_systems(ERP/SAP/레거시 등)이 핵심이지만
    MS가 후처리(알림·보고·문서화)를 담당할 수 있는 경우
  · automation_targets 중 일부는 MS로 커버 가능하고 일부는 불가능한 경우

[진행 가능] — 위 조건 모두 해당 없음
  · automation_targets 전체를 MS 생태계 내에서 해결 가능
```

### 분기 처리

#### 진행 가능 — 사용자 확인 없이 자동 진행

```
아래 메시지 출력 후 즉시 STEP 2로 진행 (대기 없음):

[input_language = "ko"]
이 요구사항은 MS 업무자동화 범위에 적합합니다.
[ParsedRequirement에서 감지된 주요 제품 힌트] 중심으로 검토를 진행합니다.

[input_language = "en"]
This request is within the scope of MS automation consulting.
Proceeding with analysis focused on [detected MS product hints].
```

세션 파일 갱신:
```json
{"scope_gate": "proceed", "updated_at": "[현재 ISO 시각]"}
```

#### 부분 지원 가능 — 사용자 확인 후 진행

```
[input_language = "ko"]
이 요구사항은 MS만으로 전체 해결하기는 어렵지만,
일부 업무 단계는 지원 가능합니다.

지원 가능 범위: [MS로 처리 가능한 automation_targets 항목]
지원 제외 범위: [MS로 처리 불가한 영역]

이 범위로 진행할까요? (예 / 아니오)

[input_language = "en"]
This request cannot be fully addressed with MS tools alone,
but some workflow steps are supported.

Supported scope : [MS-compatible automation_targets]
Excluded scope  : [areas outside MS coverage]

Proceed with this scope? (Yes / No)
```

예 선택 시:
```
1. ParsedRequirement.automation_targets → 지원 가능 범위만 남기도록 제한
2. scope_exclusions에 제외 범위 기록
3. 세션 파일 갱신:
   {"scope_gate": "partial", "scope_limited": true,
    "scope_exclusions": "[제외된 범위 요약]", "updated_at": "..."}
4. STEP 2로 진행
```

아니오 선택 시:
```
[ko] 요구사항 범위를 재정의하거나 다른 도구의 활용을 검토해보시기 바랍니다.
[en] Please consider redefining the scope or exploring other tools.
→ 컨설팅 종료
```

#### 지원 대상 아님 — 종료

```
[input_language = "ko"]
이 요구사항은 [판정 이유 — 예: PLC/설비 제어 중심] 으로,
현재 도구의 MS 업무자동화 지원 범위를 벗어납니다.
따라서 본 도구로는 적절한 컨설팅을 제공하기 어렵습니다.

[input_language = "en"]
This request focuses on [reason — e.g., PLC/equipment control],
which is outside the scope of MS automation consulting.
This tool is not able to provide appropriate recommendations.

→ 컨설팅 종료 (세션 파일에 scope_gate: "rejected" 기록)
```

---

## STEP 2 — 모드 선택

parse-requirement STEP 6 완료 후 사용자 응답 수신:

```
1 → mode = "quick"
2 → mode = "deep"
```

상태 파일 갱신:
```json
{"mode": "quick" | "deep", "updated_at": "[현재 ISO 시각]"}
```

---

## STEP 3 — ai-score-compare 실행

```
ai-score-compare 스킬 실행 (mode 전달)
→ Quick: Claude 자유 분석 → blocklist 체크 → 2패스 리스크 평가
→ Deep:  AI 3종 + Orchestrator → 2패스 리스크 평가
→ SolutionProposal 목록 반환
→ deep_meta (Deep 모드만)
```

scope_limited = true인 경우 추가 컨텍스트 전달:
```
[분석 범위 제한 안내]
이 컨설팅은 아래 범위로 제한됩니다:
  지원 가능 범위: [scope_exclusions에 기록된 제외 범위 제외한 targets]
  지원 제외 범위: [scope_exclusions]
제외 범위는 솔루션 분석에서 스킵하고, 지원 가능 범위에만 집중하여 제안하세요.
```

ai-analysis 기록 (ai-score-compare 내부에서 처리):
- `AI_CALL` × N (각 AI 호출)
- `FALLBACK` (실패 시)
- `SCORE` × 제안 수

---

## STEP 3-5 — 재컨설팅 타입 판정 가이드 로드

피드백 수신 전, 타입 판정 기준 로드:

```
Read("references/reconsult-guide.md")
```

→ A/B/C 분류 기준, 경계 케이스 예시, 판정 순서도 확인

---

## STEP 4 — 사용자 피드백 수신

ai-score-compare 출력 화면 표시 후 대기:

```
현재 권고안에 대해 어떻게 생각하시나요?

1. 이대로 진행 (MS 지원 확인 단계로)
2. 피드백 있음 (재컨설팅)
3. Quick → Deep 전환

번호 또는 자유롭게 말씀해주세요.
```

### 4-1. "이대로 진행" → STEP 5로

### 4-2. 피드백 있음 → 재컨설팅 분기

피드백 내용을 분석해 타입 판정:

```
[타입 A — 경량 재컨설팅]
  판정 기준: 현재 솔루션 ID를 유지한 채 조건/파라미터만 조정
  예) "발송 주기를 매일로 바꿔줘", "SharePoint 대신 OneDrive로 변경"
      솔루션 ID 핵심 MS 제품 조합은 그대로 유지됨

[타입 B — 전체 재컨설팅]
  판정 기준: 솔루션 ID가 바뀔 수밖에 없는 변경
  예) "Power Automate 말고 다른 걸로", "DLP 문제로 Power Automate 못 써"

[타입 C — 설명 요청]
  판정 기준: 추가 실행 없이 설명만 필요
  예) "이 리스크가 무슨 뜻이야?", "구현 개요 더 자세히 설명해줘"
```

#### 타입 A 처리

```
1. 피드백 반영하여 ai-score-compare 재실행 (현재 솔루션 ID 기준)
2. light_revision_count += 1
3. total_revision_count += 1
4. 상태 파일 즉시 저장
5. ai-analysis 기록: REVISION (type=A) + SESSION_STATE

[카운터 초과 처리]
light_revision_count == 3 도달 시:
  "경량 재컨설팅 3회에 도달했습니다.
   전체 재컨설팅(Deep 재분석)으로 전환을 권장합니다.
   → 1. 전체 재컨설팅으로 전환  2. 현재 결과 유지"
```

#### 타입 A 재컨설팅 출력 규칙

```
출력 원칙: 변경된 솔루션만 업데이트하여 전체 목록 재출력.

[변경된 안]
  → 수정된 내용 반영하여 전체 형식으로 출력
  → 헤더에 "(Rev.N)" 표시

[변경되지 않은 안]
  → 이전 결과 그대로 출력
  → 헤더에 "(변경 없음)" 표시

예시:
  [1안 — 권장 (Rev.1)]   ← 변경됨
    솔루션명: ...
    ...
  [2안 — 검토 필요 (변경 없음)]  ← 변경 없음
    솔루션명: ...
    ...

이유: 변경된 안만 표시하면 사용자가 전체 맥락을 잃음.
     전체 재출력하되 변경 여부를 명확히 표시.
```

#### 타입 B 처리

```
1. 사용자에게 확인 요청:
   "타입 B (전체 재컨설팅)으로 판단됩니다.
    전체 재컨설팅을 진행하시겠습니까?
    → 1. 예, 전체 재컨설팅 진행  2. 아니오, 경량으로 진행"

수락 (1):
  - ai-score-compare 전체 재실행
  - light_revision_count = 0 (리셋)
  - total_revision_count += 1
  - 상태 파일 즉시 저장
  - ai-analysis 기록: REVISION (type=B, user_override=false) + SESSION_STATE

거부 (2):
  - 경량 재컨설팅 진행 (타입 A와 동일)
  - user_override = true 로 기록
  - ai-analysis 기록: REVISION (type=B, user_override=true,
      override_warning="타입 B(전체 재컨설팅 권장) → 사용자 요청으로 경량 진행")
  - 사용자에게 경고 표시:
    "⚠️ 전체 재컨설팅 없이 경량 진행합니다.
     결과 일관성이 낮을 수 있으며 최종 산출물에 기록됩니다."
```

#### 타입 C 처리

```
1. 요청 내용에 대한 설명 응답
2. 재컨설팅 카운터 변경 없음
3. 안내 문구 추가:
   "추가 조정이 필요하면 말씀해주세요.
    조건 변경이면 재컨설팅으로 이어서 반영할 수 있습니다."
```

#### 타입 C → 타입 A 암묵적 전환 처리

타입 C 응답 중 사용자 피드백이 변경 의도를 포함하는 경우
(예: "Teams 폴더로 해도 되는지 파악해줘" → 가능하다면 변경 의사 내포):

```
1. 타입 C로 먼저 설명 응답
2. 변경 가능 여부 확인 후 명시적으로 전환 여부 질문:
   "[변경 내용] 방향으로 조정할까요? (예 / 아니오)"
3. 사용자가 "예" 응답 후에만 타입 A 재컨설팅 실행
   → 카운터 증가 (light +1, total +1)
   → 상태 파일 저장
   → ai-analysis 기록: REVISION (type=A) + SESSION_STATE
4. 사용자가 "아니오" → 타입 C로 종료, 카운터 변경 없음

규칙: 사용자 명시적 확인 없이 카운터 증가 금지
```

### 4-3. Quick → Deep 전환

```
1. 전체 재컨설팅으로 처리
2. mode = "deep"으로 변경
3. 시드(seed): 현재 최신 revision_id 기준
4. light_revision_count = 0 (리셋)
5. total_revision_count += 1
6. 상태 파일 즉시 저장
7. ai-analysis 기록: MODE_SWITCH + SESSION_STATE
8. ai-score-compare Deep 모드로 재실행
```

---

## STEP 5 — MS 지원 확인

사용자가 권고안을 선택한 후 실행.

### 5-1. 검색 실행

```
선택된 솔루션의 주요 기능별로 WebSearch 실행:
  "[제품명] [기능명] site:learn.microsoft.com"
  예) "Power Automate schedule trigger site:learn.microsoft.com"
      "Power Automate Outlook connector external recipients site:learn.microsoft.com"
```

### 5-1-5. Evidence Summary 압축

WebSearch 원문을 아래 구조로 압축한다. 원문은 버리고 이 요약만 5-2 평가에 사용.

```
[MS 지원 확인 요약 — {솔루션명}]
├─ 기능 지원: ✅/❌/⚠️  [한 줄 — 지원 여부 + 핵심 조건]
├─ 라이선스: [주의 사항 또는 "특이사항 없음"]
├─ Deprecated: 없음 / [있으면 대체 기능명]
└─ 출처: [URL]
```

기능이 여러 개인 경우 기능별로 반복:
```
[MS 지원 확인 요약 — {솔루션명}]
├─ [기능 A] 지원: ✅ ...
├─ [기능 B] 지원: ⚠️ ... (제약: ...)
├─ 라이선스: ...
├─ Deprecated: 없음
└─ 출처: [URL1], [URL2]
```

### 5-2. 결과 평가

Claude가 Evidence Summary를 기반으로 아래 3가지 중 하나로 판정:

```
confirmed  — 기능 지원 확인, 진행 가능
changed    — 동작 방식/제약 변경 감지 → 아래 A/B 분류 기준 적용
deprecated — 기능 deprecated 확인 → 타입 B 자동 분류
```

#### confirmed 결과 추가 조건 처리

```
검색 결과에서 구현에 영향을 주는 기술 조건 발견 시:
  → 해당 조건을 권고안 전제조건에 즉시 반영
  → 사용자에게 추가 내용 명시:
    "MS 지원 확인에서 아래 조건이 추가되었습니다:
     · [추가 조건]"
  → 솔루션 ID 변경 없음 (전제조건 보완이므로 타입 A 수준)
```

#### changed 결과 A/B 자동 분류 기준

```
타입 A로 분류 (경량 재컨설팅):
  - 기능 자체는 유지되나 제약/조건이 추가된 경우
    예) "외부 발송 시 승인 단계 필요" / "파일 크기 제한 25MB"
  - 솔루션 ID의 핵심 제품은 그대로 유지 가능

타입 B로 분류 (전체 재컨설팅):
  - 핵심 기능 자체가 변경/제거된 경우
    예) "해당 커넥터 더 이상 외부 발송 미지원"
  - 솔루션 ID의 핵심 제품을 교체해야 하는 경우

분류 불명확 시:
  → 사용자에게 변경 내용 설명 후 A/B 선택 요청
```

### 5-3. ms_verify_retry_count 관리

```
검색 1회 실행 시 ms_verify_retry_count += 1
2회 초과 시:
  "MS Learn에서 자동 확인이 어렵습니다.
   아래 링크를 직접 확인해주세요: [관련 MS Learn URL]
   확인 후 진행 여부를 알려주세요."
  → 수동 확인 후 사용자 응답 대기
```

### 5-4. ai-analysis 기록

```
ai-analysis 기록: MS_VERIFY
  result: confirmed | changed | deprecated
  action: none | A | B
  ms_verify_retry_count: [현재 값]
```

### 5-5. 상태 파일 갱신

```
ms_verify_retry_count 변경 시 즉시 저장
```

---

## STEP 6 — 사용자 최종 확인

```
최종 권고안 요약 출력 후 대기:

"최종 권고안: [솔루션명]
 MS 지원 확인: [confirmed | changed | deprecated]

 산출물 파일을 생성하시겠습니까?
 → 1. 예, 생성  2. 아니오, 추가 조정 필요"
```

"아니오" 선택 시 → STEP 4로 복귀 (재컨설팅 분기)

"예" 선택 시 → 산출물 형식 선택:

```
산출물 형식을 선택해주세요. (기본: 통합본)

1. 통합본     — 사용자 요약 + 개발자 상세를 하나의 파일로 (기본)
2. 사용자용   — 비기술적 요약만 (담당자 보고용)
3. 개발자용   — 기술 상세만 (구현 담당자용)
4. 분리본     — 사용자용 + 개발자용 파일 2개 생성

번호로 답변하거나 엔터(생략)로 통합본을 선택합니다.
```

선택값 → output_mode 매핑:
```
1 또는 생략 → "integrated"
2           → "user"
3           → "developer"
4           → "split"
```

output_mode 선택 후 → 산출물 언어 선택:

```
[input_language = "ko" 인 경우]
산출물 언어를 선택해주세요. (기본: 한국어)

1. 한국어 (기본)
2. English
3. English + 한국어   — 영문 본문 먼저, 이어서 한국어 번역 (한 파일)

번호로 답변하거나 엔터(생략)로 한국어를 선택합니다.

[input_language = "en" 인 경우]
Please select the output language. (default: English)

1. English (default)
2. 한국어
3. English + Korean   — English first, Korean translation follows in the same file

Enter a number or press Enter to use English.
```

선택값 → output_language 매핑:
```
[ko 기본 시]  1 또는 생략 → "ko" / 2 → "en" / 3 → "en+ko"
[en 기본 시]  1 또는 생략 → "en" / 2 → "ko" / 3 → "en+ko"
```

output_language를 세션 파일에 즉시 저장:
```json
{"output_language": "ko" | "en" | "en+ko", "updated_at": "[현재 ISO 시각]"}
```

---

## STEP 7 — generate-output 실행

```
generate-output 스킬 호출:
  session_id        : [현재 session_id]
  mode              : [quick | deep]
  domain            : [ParsedRequirement.domain]
  parsed_requirement: [ParsedRequirement 구조체]
  proposals         : [SolutionProposal 목록]
  deep_meta         : [deep_meta 또는 null]
  ms_verify_result  : [confirmed | changed | deprecated | null]
  output_mode       : [integrated | user | developer | split]
  output_language   : [ko | en | en+ko]  ← STEP 6에서 사용자 선택값
```

---

## STEP 8 — 완료 보고

```
컨설팅 완료

세션 ID  : [session_id]
산출물   : output/[파일명].txt
모드     : [Quick | Deep]
최종 권고: [솔루션명]
재컨설팅 : [N회]
총 소요  : 세션 시작 ~ 완료

추가 컨설팅이 필요하면 언제든 말씀해주세요.
```

---

## 세션 상태 파일 관리

```json
// 읽기: 세션 재개 시 또는 컨텍스트 압축 후
{
  "session_id": "consult_20260309_001",
  "mode": "quick",
  "current_revision": 2,
  "solution_id_current": "PowerAutomate+Outlook",
  "light_revision_count": 1,
  "total_revision_count": 2,
  "ms_verify_retry_count": 0,
  "scope_gate": "proceed | partial | rejected",
  "scope_limited": false,
  "scope_exclusions": "",
  "created_at": "...",
  "updated_at": "..."
}
```

**scope 필드 기본값:**
```
scope_gate      : "proceed"  ← 게이트 미실행 시 기본값 (기존 세션 호환)
scope_limited   : false
scope_exclusions: ""
```

**즉시 저장 시점** (컨텍스트 압축 대비):
- 재컨설팅 카운터 변경 시마다
- 모드 전환 시
- ms_verify_retry_count 변경 시
- solution_id_current 변경 시
- scope_gate 판정 완료 시 (proceed / partial / rejected)

**시각 기록 규칙**:
```
created_at / updated_at 형식: ISO 8601 (예: 2026-03-09T10:00:00+09:00)
created_at: 세션 파일 최초 생성 시 1회만 기록, 이후 변경 금지
updated_at: 상태 파일 저장 시마다 현재 시각으로 갱신
```

---

## 재컨설팅 타입 판정 요약표

| 상황 | 타입 | 처리 |
|---|---|---|
| 솔루션 ID 유지, 파라미터 변경 | A | 경량 재컨설팅 |
| 솔루션 ID 변경 필요 | B | 전체 재컨설팅 권장, 사용자 확인 |
| 설명/질문 요청 | C | 설명만 응답, 카운터 변경 없음 |
| Quick→Deep 전환 | 모드전환 | 전체 재컨설팅 + 모드 변경 |
| light_revision_count 3 초과 | A→B 권장 | 전체 재컨설팅 전환 안내 |
| MS 지원 확인 failed | A 또는 B | 변경 범위에 따라 자동 분류 |

---

## 실패 처리

| 실패 유형 | 처리 방법 |
|---|---|
| parse-requirement 실패 | 오류 메시지 표시 후 중단 |
| ai-score-compare 실패 (Quick) | 오류 메시지 표시 + 재시도 여부 확인 |
| ai-score-compare 실패 (Deep, 3 AI 모두) | "AI 연결 불가. Quick 모드로 전환하시겠습니까?" |
| MS 지원 확인 2회 실패 | 수동 확인 안내 + MS Learn URL 제공 |
| 상태 파일 저장 실패 | 사용자에게 알림 + 컨텍스트에서만 관리 |
| generate-output 실패 | 오류 표시 + 본문 직접 출력 |

---

## 주의사항

- 재컨설팅 카운터는 세션 상태 파일에 즉시 저장 (컨텍스트 압축 대비)
- 타입 B user_override는 반드시 로그 및 산출물 부록 A에 기록
- MS 지원 확인은 권고안 선택 후 1회만 실행 (ms_verify_retry_count ≤ 2)
- ai-analysis SESSION_STATE는 카운터 변경 시마다 기록 (중복 기록 허용)
- 동일 세션의 모든 이벤트에 동일한 session_id 사용
- 세션 재개 시 반드시 상태 파일에서 카운터 복원 후 진행
- 적합성 게이트 판정 결과는 세션 파일에 즉시 저장 (scope_gate 필드)
- scope_gate = "rejected" 시 이후 단계 절대 진행 금지
- scope_gate = "partial" + 사용자 "아니오" 선택 시도 종료 처리
- 진행 가능(proceed) 판정 시 사용자 확인 없이 자동으로 STEP 2 진행

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-09 | v1.0 | 최초 작성 |
| 2026-03-10 | v1.1 | 언어 선택 추가 — STEP 6에 output_language 선택 프롬프트(ko/en), en+ko 이중언어 옵션(3번) 추가. STEP 7 output_language 파라미터 반영 |
| 2026-03-10 | v1.2 | 적합성 게이트 추가 — STEP 1-5 신규. 판정 기준(domain/automation_targets/external_systems), 3단계 분기(proceed 자동/partial 확인/rejected 종료), 이중언어 출력 메시지, scope 세션 필드(scope_gate/scope_limited/scope_exclusions), STEP 3 scope_limited 컨텍스트 전달 로직 |
| 2026-03-10 | v1.3 | MS 지원 확인 Evidence Summary 압축 추가 — STEP 5-1-5 신규. WebSearch 원문을 기능지원/라이선스/deprecated/출처 4개 필드로 압축 후 평가에 사용. 5-2 평가 기준을 Evidence Summary 기반으로 변경 |
