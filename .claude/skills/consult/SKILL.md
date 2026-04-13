---
name: consult
version: 2.0
description: MS 업무 자동화 컨설팅 전체 흐름을 오케스트레이션한다. parse-requirement → 적합성 게이트 → 모드 선택 → ai-score-compare → 사용자 피드백 → 재컨설팅(A/B/C) → MS 지원 확인 → generate-output 순서로 실행한다. "컨설팅 시작해줘", "자동화 방법 알려줘", "업무 자동화 컨설팅", "어떻게 자동화할 수 있어", "어떻게 자동화 할 지 알려줘", "자동화하고 싶어", "자동으로 하고 싶어", "업무를 자동화", "~를 자동화", "자동화 가능해?", "어떻게 하면 자동화", "업무 효율화", "반복 업무 줄이고 싶어", "자동으로 처리하고 싶어" 등 업무 자동화 관련 요청 시 트리거한다.

depends_on:
  - parse-requirement
  - ai-score-compare
  - ms-solution-recommend
  - ai-analysis
  - generate-output
produces:
  - output/[날짜]_[도메인]_[session_id]_자동화_컨설팅.txt
  - logs/session/session_YYYYMMDD_NNN.json
  - logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl
---

# Consult Skill

## 전체 흐름

```
[1]   parse-requirement   → ParsedRequirement + session_id
[1-5] 적합성 게이트        → proceed(자동) / partial(확인) / rejected(종료)
[2]   모드 선택            → Quick | Deep
[3]   ai-score-compare    → SolutionProposal 목록
[4]   사용자 피드백        → 재컨설팅 분기 (A/B/C/모드전환)
[5]   MS 지원 확인
[6]   사용자 최종 확인     → output_mode / output_language / generate_excel 선택
[7]   generate-output     → .txt (+ .xlsx if generate_excel=true)
[8]   완료 보고
```

---

## STEP 1 — 요구사항 파싱

parse-requirement 스킬 실행 → ParsedRequirement + session_id 생성 + 세션 파일 초기화.
사용자 확정 전까지 다음 단계 진행 금지.

---

## STEP 1-5 — 적합성 게이트

ParsedRequirement 확정 직후 실행.

### 판정 규칙

| 판정 | 조건 |
|---|---|
| 지원 대상 아님 | automation_targets 핵심이 HW/PLC/설비 제어 OR domain이 제조현장·의료기기·산업자동화이고 MS 접점 없음 OR external_systems 메인이고 MS 연결 불가 |
| 부분 지원 가능 | external_systems(ERP/SAP/레거시)이 핵심이나 MS가 후처리 담당 가능 OR targets 일부만 MS로 커버 |
| 진행 가능 | 위 조건 모두 해당 없음 |

### 분기 처리

**진행 가능**: 메시지 출력 후 즉시 STEP 2 (대기 없음)
```
[ko] 이 요구사항은 MS 업무자동화 범위에 적합합니다. [주요 제품 힌트] 중심으로 진행합니다.
[en] This request is within MS automation scope. Proceeding with [MS product hints].
```
세션 저장: `{"scope_gate": "proceed"}`

**부분 지원 가능**: 지원 가능/제외 범위 명시 후 사용자 확인 (예/아니오)
- 예: automation_targets를 지원 범위로 제한, scope_exclusions 기록, STEP 2 진행
  세션 저장: `{"scope_gate": "partial", "scope_limited": true, "scope_exclusions": "..."}`
- 아니오: 컨설팅 종료

**지원 대상 아님**: 판정 이유 설명 후 종료.
세션 저장: `{"scope_gate": "rejected"}`
**⚠️ rejected 시 이후 단계 절대 진행 금지**

---

## STEP 2 — 모드 선택

parse-requirement STEP 6 완료 후 수신. 1→Quick, 2→Deep.
세션 저장: `{"mode": "quick"|"deep"}`

---

## STEP 3 — ai-score-compare 실행

mode 전달하여 실행. scope_limited=true면 제한 범위 컨텍스트 추가 전달.
ai-analysis 기록: AI_CALL × N, FALLBACK(실패 시), SCORE × 제안 수

**요구사항 컨텍스트 전달 규칙**: ai-score-compare 호출 전 요구사항을 아래 1줄로 요약 출력. 표 형식 출력 금지.
```
[요구사항] [domain] / [automation_targets 핵심 1줄] / 도구: [current_tools] / [process_type]
```

---

## STEP 3-5 — 재컨설팅 타입 판정 가이드 (지연 로드)

reconsult-guide.md는 사용자가 피드백을 제공할 때만 로드한다.
사용자가 "이대로 진행"을 선택하면 로드하지 않는다. (~522 토큰 절감)

```
[STEP 4에서 피드백 수신 시에만]
Read("references/reconsult-guide.md")
```

---

## STEP 4 — 사용자 피드백

결과 표시 후 선택지 제시: 1.이대로 진행→STEP5 / 2.피드백(재컨설팅) / 3.Quick→Deep전환

### 재컨설팅 타입 판정 및 처리

| 타입 | 조건 | 처리 |
|---|---|---|
| A — 경량 | 솔루션 ID 유지, 파라미터·조건만 변경 | ai-score-compare 재실행. light+1, total+1. 상태파일 즉시 저장 |
| B — 전체 | 솔루션 ID 변경 필요 | 사용자 확인 후 전체 재실행. light=0, total+1 |
| C — 설명 | 질문·설명 요청 | 설명만 응답. 카운터 변동 없음 |
| 모드전환 | Quick→Deep 요청 | mode="deep", light=0, total+1. ai-score-compare Deep 재실행 |

**타입 A 출력**: 변경된 안은 전체 형식 + "(Rev.N)" / 미변경 안은 "(변경 없음)" 표시

**타입 B 처리**:
- 수락: 전체 재실행, REVISION(type=B, user_override=false)
- 거부(경량 강행): REVISION(type=B, user_override=true) + 경고 표시
  `"⚠️ 전체 재컨설팅 없이 경량 진행. 결과 일관성이 낮을 수 있으며 산출물에 기록됩니다."`

**light_revision_count == 3 도달 시**:
`"경량 재컨설팅 3회 도달. 전체 재컨설팅 전환 권장. → 1.전체전환 2.현재유지"`

**타입 C → A 암묵적 전환**: 변경 의도 감지 시 먼저 설명 후 `"[변경내용] 방향으로 조정할까요? (예/아니오)"` 확인 후에만 A 실행

**ai-analysis 기록**: 카운터 변경 시 REVISION + SESSION_STATE

### 선택 확정 후 컨텍스트 압축 (토큰 최적화)

사용자가 "이대로 진행(STEP 5)"을 선택하는 순간:

**비선택 안(검토필요/비추천)은 아래 최소 필드만 남기고 상세 내용을 즉시 드랍한다.**

| 판정 | 유지 필드 | 드랍 필드 |
|---|---|---|
| 검토필요 | solution_name, solution_id, reason(2줄 요약), verdict_reason, implementation(1줄 요약), risks(drop_risk=true 항목명만) | prerequisites 상세, limitations, considerations, risks 상세(drop_risk=false) |
| 비추천 | solution_name, solution_id, verdict_reason(1줄) | 나머지 전체 |

→ 권장안 full detail은 그대로 유지.

---

## STEP 5 — MS 지원 확인

사용자가 권고안 선택 후 실행.

### 5-1. 검색

```
WebSearch: "[제품명] [기능명] site:learn.microsoft.com" (기능별)
```

### 5-1-5. Evidence Summary 압축 (원문 버리고 이것만 사용)

```
[MS 지원 확인 요약 — {솔루션명}]
├─ 기능 지원: ✅/❌/⚠️  [한 줄 — 지원 여부 + 핵심 조건]
├─ 라이선스: [주의 사항 또는 "특이사항 없음"]
├─ Deprecated: 없음 / [있으면 대체 기능명]
└─ 출처: [URL]
```

Evidence Summary 작성 완료 후, WebSearch 결과 원문은 이후 컨텍스트에서 참조하지 않는다. 이후 모든 단계는 Evidence Summary만 사용한다.

### 5-2. 결과 평가 및 분류

| 결과 | 의미 | 처리 |
|---|---|---|
| confirmed | 기능 지원 확인 | 추가 조건 발견 시 전제조건에 반영 후 사용자 안내 |
| changed | 동작/제약 변경 | 핵심 기능 유지→타입A / 핵심 제품 교체 필요→타입B |
| deprecated | 기능 deprecated | 타입B 자동 분류 |

분류 불명확 시 사용자에게 A/B 선택 요청.

### 5-3. 재시도 관리

ms_verify_retry_count 초과(>2) 시 수동 확인 안내 + MS Learn URL 제공.

**ai-analysis 기록**: MS_VERIFY (result, action, ms_verify_retry_count)
**세션 저장**: ms_verify_retry_count 변경 시 즉시

---

## STEP 6 — 사용자 최종 확인

```
최종 권고안: [솔루션명]
MS 지원 확인: [confirmed | changed | deprecated]

산출물 파일을 생성하시겠습니까?  → 1.예 2.아니오(추가 조정)
```

아니오 → STEP 4 복귀

예 → **STEP 6-A: solution_id 확인** (분기 결정)

### STEP 6-A — PowerAutomate 포함 여부 확인

```
if "PowerAutomate" in solution_id:
  BRANCH = "with_pa"     # ① ② ③ ④ 모두 표시
else:
  BRANCH = "without_pa"  # ① ② ③만 표시, ④ 스킵
```

초기값:
```
output_mode = null
output_language = null
generate_excel = false        (기본값)
generate_pa_flow = false      (기본값, ④ 미표시 시 유지)
```

---

### STEP 6-1 — output_mode 선택 (필수)

```
1. 통합본     — 사용자 요약 + 개발자 상세 (기본)
2. 사용자용   — 비기술 요약만
3. 개발자용   — 기술 상세만
4. 분리본     — 사용자용 + 개발자용 파일 2개
```

**매핑**:
- 1 또는 생략 → `output_mode = "integrated"`
- 2 → `output_mode = "user"`
- 3 → `output_mode = "developer"`
- 4 → `output_mode = "split"`

---

### STEP 6-2 — output_language 선택 (필수)

| input_language | 선택지 | 매핑 |
|---|---|---|
| ko | 1.한국어(기본) / 2.English / 3.English+한국어 | ko / en / en+ko |
| en | 1.English(default) / 2.한국어 / 3.English+Korean | en / ko / en+ko |

**저장**: `session_state["output_language"] = [user_selection]`

---

### STEP 6-3 — Excel 생성 여부 (선택)

```
[ko] Excel 보고서(.xlsx)도 함께 생성할까요?
     1.아니오 — .txt만 생성 (기본)  2.예 — .txt + .xlsx 함께 생성
[en] Would you also like to generate an Excel report (.xlsx)?
     1.No (default)  2.Yes
```

**매핑**:
- 1 또는 생략 → `generate_excel = false`
- 2 → `generate_excel = true`

**Excel 언어**: output_language 그대로 적용
- ko → KR시트만
- en → EN시트만
- en+ko → 둘 다

---

### STEP 6-4 — PA 플로우 설계 생성 여부 (조건부 선택)

**조건 분기**: BRANCH == "with_pa"인 경우에만 표시

```
[ko] PowerAutomate가 권고안에 포함되어 있습니다.
     PA 플로우 설계 산출물을 생성할까요?
     1.아니오 (기본)  2.예 — 플로우 다이어그램 + Copilot 프롬프트 + Blueprint JSON 생성
[en] PowerAutomate is included in the recommendation.
     Would you like to generate a PA flow design?
     1.No (default)  2.Yes
```

**매핑**:
- 1 또는 생략 → `generate_pa_flow = false`
- 2 → `generate_pa_flow = true`

**BRANCH == "without_pa"인 경우**: 이 질문 표시 안 함, `generate_pa_flow = false` 자동 설정

---

### STEP 6 최종 확인 (generate-output 전달 전)

**반드시 확인할 값들:**
```
✓ output_mode     : [integrated|user|developer|split]
✓ output_language : [ko|en|en+ko]
✓ generate_excel  : [true|false]
✓ generate_pa_flow: [true|false] (STEP 6-4 결과)
```

모든 값이 설정되어야 STEP 7 진행.

---

## STEP 7 — generate-output 실행

```
generate-output 호출 (필수 필드):

  session_id       : [session_id]
  mode             : [mode]
  domain           : [domain]
  parsed_requirement: domain / automation_targets / current_tools / process_type 만 전달
                      (constraints·ms_products_hint·technical_unknowns 생략)
  selected_proposal: 권장안 full SolutionProposal
  other_proposals  : 비선택 안은 축약 필드만 (STEP 4 압축 결과 그대로)
  ms_verify_result : Evidence Summary만 (WebSearch 원문 제외)
  deep_meta        : common_strengths / common_risks / orchestrator_review 만 전달
                     (ai_proposals 각 AI 전체 제안 내용 제외)
  output_mode      : [output_mode]       ← STEP 6-1 결과
  output_language  : [output_language]   ← STEP 6-2 결과
  generate_excel   : [generate_excel]    ← STEP 6-3 결과
```

**STEP 6-4 결과 처리**:
- generate_pa_flow 값은 generate-output 호출에 포함하지 않음 (generate-output은 .txt/.xlsx만 생성)
- generate_pa_flow=true인 경우만 아래 STEP 7-P 실행

---

## STEP 7-E / STEP 7-P — 선택적 산출물 생성

generate-output 완료 후 아래 조건에 따라 추가 실행:

### STEP 7-E — Excel 보고서 생성 ← **generate_excel=true인 경우만 실행**

```
Read("references/excel-output-schema.md")
```
(파일명 규칙, JSON 플레이스홀더 전체 목록, 저장·호출·실패처리 포함)

---

### STEP 7-P — PA 플로우 설계 생성 ← **generate_pa_flow=true인 경우만 실행**

```
조건: generate_pa_flow=true (STEP 6-4 사용자 선택 결과)

[1] 디렉토리 확인
    output/PA_Flow/ 없으면 Bash: mkdir -p "output/PA_Flow"
    logs/PA_log/    없으면 Bash: mkdir -p "logs/PA_log"

[2] 아래 4개 섹션으로 PA_Flow.txt 구성 (consult 컨텍스트 재사용):
    입력: solution_id / implementation[] / automation_targets / prerequisites / output_language

    **출력 원칙**: Copilot 프롬프트·AI 생성 방식 안내 금지.
    개발자가 PA 포털(make.powerautomate.com)을 처음 열어도 순서대로 따라할 수 있는
    Step-by-step UI 설정 매뉴얼만 작성한다.

    섹션 1 — 플로우 다이어그램 (ASCII)
      트리거 → 서브플로우(또는 액션 그룹) → 조건 → 액션 순서로 시각화
      역할별로 서브플로우/스코프로 구조화하여 표현
      조건 분기(성공/실패)가 있으면 분기선(├─/└─)으로 명시

    섹션 2 — 사전 준비
      make.powerautomate.com 접속 및 로그인 확인
      필요 커넥터 목록 (공식 명칭 + 라이선스 등급 Standard/Premium)
      커넥터 연결(계정 인증) 방법: 커넥터 탭 → [커넥터명] → 연결 추가 → 계정 선택
      Office Scripts 사용 시: IT 관리자 활성화 선행 항목 명시

    섹션 3 — 단계별 설정 가이드 (Step-by-step)
      규칙:
        - "Step N. [메뉴/탭 위치] → [클릭할 항목] → [입력값]" 형식 엄수
        - 각 Step은 1개 액션만 기술 (복합 동작 분리)
        - 동적 콘텐츠 참조 시 변수명 명시 (예: %CurrentFile['Id']%)
        - 환경 종속 값은 [플레이스홀더] 형식으로 표기
        - 역할 단위로 서브플로우/스코프 구분선 삽입
      구성 순서:
        ① 플로우 생성 (이름·트리거 설정)
        ② 커넥터별 액션 추가 (트리거 → 데이터 조회 → 핵심 처리 → 알림 순)
        ③ 조건 분기 설정 (성공/실패 경로 각각)
        ④ 변수 설정 및 동적 콘텐츠 매핑
        ⑤ 저장 및 테스트 실행

    섹션 4 — 예외 처리 설정 가이드
      오류 유형별로 PA에서 실제 설정하는 방법을 Step 형식으로 기술:
        - 스크립트/액션 실패 시: Scope + Configure run after 설정 방법
        - 빈값/0건 처리: Condition 액션 설정 방법
        - 중복 실행 방지: 조건 컬럼 확인 로직 설정
        - 인증 만료: 커넥터 재연결 방법
        - 실패 항목 누적 알림: 변수 초기화 → append → 완료 후 알림 설정
      각 항목은 체크리스트 [ ] 형식으로 출력

[3] Blueprint JSON 구성
    {
      "session_id": "[session_id]",
      "flow_name": "[solution_name]",
      "trigger": { "type": "...", "connector": "...", "filter": {} },
      "actions": [{ "step": N, "type": "...", "connector": "...", "params": {} }],
      "connectors_required": [...],
      "license_tier": "Standard | Premium"
    }

[4] 파일 저장
    Write: output/PA_Flow/[YYYYMMDD]_[session_id]_PA_Flow.txt
    Write: logs/PA_log/[YYYYMMDD]_[session_id]_PA_Flow.json
```

**실패 처리**: 저장 실패 시 경고 출력 후 STEP 8 계속 진행

---

## STEP 8 — 완료 보고

**반드시 확인 사항:**
- output_mode, output_language, generate_excel, generate_pa_flow 모두 설정됨
- generate-output 완료 여부 (STEP 7)
- generate_excel=true인 경우 STEP 7-E 완료 여부
- generate_pa_flow=true인 경우 STEP 7-P 완료 여부

```
컨설팅 완료

세션 ID      : [session_id]
산출물 (필수)  : output/[파일명].txt
산출물 (선택)  :
  ✓ generate_excel=true   : output/[파일명].xlsx
  ✓ generate_pa_flow=true : output/PA_Flow/[날짜]_[session_id]_PA_Flow.txt
                           logs/PA_log/[날짜]_[session_id]_PA_Flow.json
출력 형식   : [통합본|사용자용|개발자용|분리본]
언어       : [한국어|English|English+한국어]
모드       : [Quick|Deep]
최종 권고   : [솔루션명]
재컨설팅    : [N회]

추가 컨설팅이 필요하면 언제든 말씀해주세요.
```

---

## 세션 상태 파일

**경로**: `logs/session/session_YYYYMMDD_NNN.json`

| 필드 | 기본값 | 설명 |
|---|---|---|
| session_id | — | `consult_YYYYMMDD_NNN` |
| mode | — | quick \| deep |
| input_language / output_language | — | ko \| en \| en+ko |
| current_revision | 0 | 현재 재컨설팅 단계 |
| solution_id_current | null | 선택 솔루션 ID |
| light_revision_count | 0 | 경량 재컨설팅 횟수 |
| total_revision_count | 0 | 전체 재컨설팅 횟수 |
| ms_verify_retry_count | 0 | MS 지원 확인 재시도 |
| scope_gate | "proceed" | proceed \| partial \| rejected |
| scope_limited | false | 범위 제한 여부 |
| scope_exclusions | "" | 제외 범위 요약 |
| context_snapshot | null | 대화 복원용 컨텍스트 스냅샷 (아래 참조) |
| created_at / updated_at | ISO 8601 | created_at은 최초 1회만 |

### context_snapshot 구조

대화 단절 시 최소한의 맥락 복원을 위해 아래 시점에 스냅샷을 저장한다.

```json
"context_snapshot": {
  "requirement_summary": "domain / automation_targets 핵심 1줄 / current_tools",
  "selected_proposal": "솔루션명 + solution_id (권고안 선택 시)",
  "last_step": "STEP N",
  "last_feedback": "사용자 마지막 피드백 1줄 요약 (재컨설팅 시)"
}
```

**저장 시점**: STEP 1 완료(requirement_summary) / STEP 4 선택 확정(selected_proposal) / 재컨설팅 시(last_feedback) / 매 STEP 전환(last_step)

**즉시 저장 시점**: 재컨설팅 카운터 변경 / 모드 전환 / ms_verify_retry_count 변경 / solution_id_current 변경 / scope_gate 판정 완료 / context_snapshot 갱신

---

## 재컨설팅 타입 요약

| 상황 | 타입 | 처리 |
|---|---|---|
| 솔루션 ID 유지, 파라미터 변경 | A | 경량 재컨설팅 |
| 솔루션 ID 변경 필요 | B | 전체 재컨설팅 권장, 사용자 확인 |
| 설명/질문 요청 | C | 설명만, 카운터 변경 없음 |
| Quick→Deep 전환 | 모드전환 | 전체 재컨설팅 + 모드 변경 |
| light_revision_count 3 초과 | A→B 권장 | 전체 전환 안내 |
| MS 지원 확인 failed | A 또는 B | 변경 범위에 따라 자동 분류 |

---

## 실패 처리

| 실패 유형 | 처리 |
|---|---|
| parse-requirement 실패 | 오류 표시 후 중단 |
| ai-score-compare 실패 (Quick) | 오류 표시 + 재시도 여부 확인 |
| ai-score-compare 실패 (Deep, 전체) | "Quick 모드로 전환하시겠습니까?" |
| MS 지원 확인 2회 실패 | 수동 확인 안내 + MS Learn URL |
| 상태 파일 저장 실패 | 사용자 알림 + 컨텍스트에서만 관리 |
| generate-output 실패 | 오류 표시 + 본문 직접 출력 |

## 주의사항

- 재컨설팅 카운터는 세션 파일에 즉시 저장 (컨텍스트 압축 대비)
- 타입 B user_override는 로그 및 산출물 부록A에 반드시 기록
- MS 지원 확인은 권고안 선택 후 1회만 (ms_verify_retry_count ≤ 2)
- ai-analysis SESSION_STATE는 카운터 변경 시마다 기록 (중복 허용)
- 세션 재개 시 상태 파일에서 카운터 복원 후 진행
- scope_gate="rejected" 시 이후 단계 절대 진행 금지

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-09 | v1.0 | 최초 작성 |
| 2026-03-10 | v1.1 | output_language 선택 추가 |
| 2026-03-10 | v1.2 | 적합성 게이트(STEP 1-5) 추가 |
| 2026-03-10 | v1.3 | MS 지원 확인 Evidence Summary 압축 추가 |
| 2026-03-11 | v1.4 | Excel 보고서 생성 추가 (STEP 6 Excel 질문, STEP 7-E) |
| 2026-03-11 | v1.5 | 토큰 최적화 — 전체 구조 표/간결 형식으로 압축 (-50%) |
| 2026-03-11 | v1.5-1 | STEP 3 요구사항 컨텍스트 1줄 요약 규칙 추가 — 중간 표 출력 금지 (~250 토큰 절감) |
| 2026-03-11 | v1.6 | 컨설팅 결과 컨텍스트 압축 3종 — A:비선택 안 즉시 축약(STEP 4), B:generate-output 최소 필드 전달(STEP 7), C:WebSearch 원문 드랍(STEP 5) (~800~1,600 토큰/사이클 절감) |
| 2026-03-11 | v1.8 | Phase 5 #26 PA 플로우 설계 생성 구현 — STEP 6 ④ PA 생성 여부 확인(PowerAutomate 포함 시만), STEP 7-P 신규(pa-flow-prompt-guide.md 로드, ASCII 다이어그램+Copilot 프롬프트+수동 구현 포인트, Blueprint JSON), STEP 8 완료 보고 PA 파일명 추가 |
| 2026-03-15 | v2.0 | 성능 최적화 — reconsult-guide.md 지연 로드 (피드백 시에만, ~522토큰 절감), ai-score-compare에서 blocklist_context 전달 구조 반영 |
| 2026-03-17 | v2.0.1 | STEP 6 분기 로직 구조화 — STEP 6-A 추가 (solution_id에서 "PowerAutomate" 포함 여부 판단), STEP 6-1~4 명시적 순서 정의, STEP 6 최종 확인 체크리스트 추가, STEP 7 generate_excel/generate_pa_flow 전달 명시, STEP 7-E/7-P 조건부 실행 강조, STEP 8 확인 사항 추가. 목표: PA 플로우 자동 생성 방지, 사용자 확인 필수화 |
| 2026-03-17 | v2.1.0 | STEP 7-P 전면 재설계 — PA Copilot 프롬프트 섹션 제거, 섹션 구성을 Step-by-step UI 설정 매뉴얼 방식으로 전환. 섹션2=사전준비(커넥터 연결), 섹션3=Step N 형식 단계별 설정 가이드(플로우생성→액션추가→조건분기→변수매핑→테스트), 섹션4=오류 유형별 PA 설정 방법(Scope+Configure run after 등). pa-flow-prompt-guide.md 의존성 제거. |
