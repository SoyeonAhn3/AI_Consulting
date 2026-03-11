---
name: consult
version: 1.5
description: MS 업무 자동화 컨설팅 전체 흐름을 오케스트레이션한다. parse-requirement → 적합성 게이트 → 모드 선택 → ai-score-compare → 사용자 피드백 → 재컨설팅(A/B/C) → MS 지원 확인 → generate-output 순서로 실행한다. "컨설팅 시작해줘", "자동화 방법 알려줘", "업무 자동화 컨설팅" 등의 요청 시 트리거한다.
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

## STEP 3-5 — 재컨설팅 타입 판정 가이드 로드

```
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

예 → 순서대로 선택:

**① output_mode 선택** (기본: 통합본)
```
1. 통합본     — 사용자 요약 + 개발자 상세 (기본)
2. 사용자용   — 비기술 요약만
3. 개발자용   — 기술 상세만
4. 분리본     — 사용자용 + 개발자용 파일 2개
```
매핑: 1/생략→integrated / 2→user / 3→developer / 4→split

**② output_language 선택**

| input_language | 선택지 | 매핑 |
|---|---|---|
| ko | 1.한국어(기본) / 2.English / 3.English+한국어 | ko / en / en+ko |
| en | 1.English(default) / 2.한국어 / 3.English+Korean | en / ko / en+ko |

세션 저장: `{"output_language": "ko"|"en"|"en+ko"}`

**③ Excel 생성 여부**
```
[ko] Excel 보고서(.xlsx)도 함께 생성할까요?
     1.아니오 — .txt만 생성 (기본)  2.예 — .txt + .xlsx 함께 생성
[en] Would you also like to generate an Excel report (.xlsx)?
     1.No (default)  2.Yes
```
매핑: 1/생략→generate_excel=false / 2→generate_excel=true

Excel 언어: output_language 그대로 적용 (ko→KR시트만 / en→EN시트만 / en+ko→둘 다)

---

## STEP 7 — generate-output 실행

```
generate-output 호출:
  session_id, mode, domain, parsed_requirement, proposals,
  deep_meta, ms_verify_result, output_mode, output_language
```

generate-output 완료 후, **generate_excel=true인 경우** 추가 실행:

### STEP 7-E — Excel 보고서 생성

```
Read("references/excel-output-schema.md")
```
(파일명 규칙, JSON 플레이스홀더 전체 목록, 저장·호출·실패처리 포함)

---

## STEP 8 — 완료 보고

```
컨설팅 완료

세션 ID  : [session_id]
산출물   : output/[파일명].txt
         [generate_excel=true] output/[파일명].xlsx
출력     : [통합본|사용자용|개발자용|분리본]
언어     : [한국어|English|English+한국어]
모드     : [Quick|Deep]
최종 권고: [솔루션명]
재컨설팅 : [N회]
총 소요  : 세션 시작 ~ 완료

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
| created_at / updated_at | ISO 8601 | created_at은 최초 1회만 |

**즉시 저장 시점**: 재컨설팅 카운터 변경 / 모드 전환 / ms_verify_retry_count 변경 / solution_id_current 변경 / scope_gate 판정 완료

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
| 2026-03-11 | v1.6 | STEP 3 요구사항 컨텍스트 1줄 요약 규칙 추가 — 중간 표 출력 금지 (~250 토큰 절감) |
