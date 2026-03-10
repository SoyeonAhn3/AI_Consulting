---
name: generate-output
version: 1.3
description: ai-score-compare의 최종 권고안(SolutionProposal)을 공통 스키마 기반 본문 + 재컨설팅 이력 부록(A) + Deep AI 비교 부록(B)으로 구성된 산출물 파일을 생성한다. output_mode에 따라 통합본(기본) / 사용자용 / 개발자용 / 분리본으로 출력한다. consult 스킬에서 사용자 최종 확인 후 호출한다.
depends_on:
  - ai-score-compare
  - ai-analysis
produces:
  - output/[날짜]_[도메인]_[session_id]_자동화_컨설팅.txt          # integrated (기본)
  - output/[날짜]_[도메인]_[session_id]_자동화_컨설팅_사용자.txt   # user 또는 split
  - output/[날짜]_[도메인]_[session_id]_자동화_컨설팅_개발자.txt   # developer 또는 split
---

# Generate Output Skill

`ai-score-compare`가 확정한 `SolutionProposal` 목록을 받아
산출물 파일을 생성한다.

- **요구사항 요약**: 파싱된 사용자 요구사항 (항상 포함)
- **본문**: 권장/검토필요/비추천 구분 최종 권고안 (Quick/Deep 동일)
- **부록 A**: 재컨설팅 이력 — `total_revision_count > 0`일 때만 포함
- **부록 B**: Deep AI 비교 — Deep 모드일 때만 포함

---

## 입력 파라미터

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `session_id` | string | 현재 세션 ID (`consult_YYYYMMDD_NNN`) |
| `mode` | string | `"quick"` \| `"deep"` |
| `domain` | string | 업무 도메인 (파일명에 사용) |
| `parsed_requirement` | object | parse-requirement 출력 구조체 (요구사항 요약용) |
| `proposals` | list | SolutionProposal 목록 (ai-score-compare 출력) |
| `deep_meta` | object \| null | Deep 모드 메타 (AI 실행 현황, 상호 리뷰 요약) — Deep 모드만 |
| `ms_verify_result` | string \| null | MS 지원 확인 결과 (`confirmed` \| `changed` \| `deprecated` \| null) |
| `output_mode` | string | `"integrated"`(기본) \| `"user"` \| `"developer"` \| `"split"` |
| `output_language` | string | `"ko"`(기본) \| `"en"` \| `"en+ko"` — 산출물 언어. 미전달 시 `input_language` 값 사용 |

### output_mode 동작 규칙

```
integrated  : 단일 파일. 사용자 섹션 → 개발자 섹션 순서로 통합 출력 (기본값)
user        : 단일 파일. 사용자 섹션만 출력
developer   : 단일 파일. 개발자 섹션만 출력
split       : 파일 2개 생성 (_사용자.txt + _개발자.txt)
```

`output_mode`가 전달되지 않으면 `integrated`로 처리한다.

---

## SolutionProposal 필드 구조

proposals 목록의 각 항목:

```
solution_name      : 솔루션 이름
solution_id        : 핵심 MS 제품 조합 (예: PowerAutomate+Outlook+Excel)
verdict            : "권장" | "검토필요" | "비추천"
reason             : 적용 이유
implementation     : 구현 개요 단계 목록
prerequisites      : 전제조건 목록 (MS 지원 확인에서 추가된 조건 포함)
limitations        : 한계점 목록
risks              : 리스크 목록 [{category, name, description, drop_risk, mitigation}]
considerations     : 고려사항 목록
unverified         : true | false (solutions.md 미등재 여부)
verdict_reason     : 검토필요·비추천인 경우 사유 1줄
```

---

## deep_meta 필드 구조

Deep 모드에서 consult가 ai-score-compare 완료 후 수집·조립:

```
ai_status          : {codex: true/false, gemini: true/false, claude: true}
fallbacks          : [{failed_model, reason, fallback_to}] (없으면 [])
ai_proposals       : {codex: {solution_id, highlights}, gemini: {...}, claude: {...}}
common_strengths   : ["공통 강점 항목1", ...]
common_risks       : ["공통 리스크 항목1", ...]
orchestrator_review: 상호 리뷰 요약 텍스트
```

---

## STEP 1 — 출력 디렉토리 확인

```
output/ 디렉토리 없으면 Bash로 생성: mkdir -p output
```

---

## STEP 1-5 — output_language 결정

```
output_language 파라미터가 전달된 경우 → 그 값 사용
output_language 미전달 시 → parsed_requirement.input_language 값 사용
parsed_requirement도 없을 경우 → "ko" 기본값 사용

output_language = "en"이면:
  - 모든 고정 레이블을 아래 영문 레이블 매핑표로 교체
  - 파일명에 _EN suffix 추가
  - 권고안 본문 전체를 영문으로 생성 지시

output_language = "en+ko"이면:
  - [1단계] 영문 전체 본문 생성 (영문 레이블 매핑표 적용)
  - [2단계] 아래 구분선 삽입 후 동일 내용을 한국어로 번역하여 이어서 생성
  - 파일명에 _BILINGUAL suffix 추가
  - 구분선 형식:
    ════════════════════════════════════════════════════════════
      ■ 한국어 번역 (Korean Translation)
    ════════════════════════════════════════════════════════════
```

### 영문 레이블 매핑표 (output_language = "en" 시 적용)

| 한국어 레이블 | 영문 레이블 |
|---|---|
| MS 업무 자동화 컨설팅 결과 | MS Automation Consulting Report |
| 세션 ID | Session ID |
| 모드 | Mode |
| 생성일시 | Generated |
| 도메인 | Domain |
| 요구사항 요약 | Requirement Summary |
| 업무 도메인 | Business Domain |
| 자동화 대상 | Automation Target |
| 현재 도구 | Current Tools |
| 외부 시스템 | External Systems |
| 프로세스 유형 | Process Type |
| 제약 조건 | Constraints |
| 운영 파라미터 | Operational Params |
| 파싱 신뢰도 | Parse Confidence |
| MS 지원 확인 | MS Support Check |
| [사용자용] 권고 요약 | [User] Recommendation Summary |
| [개발자용] 기술 상세 | [Developer] Technical Details |
| [권장안] | [Recommended] |
| [검토 필요안] | [Review Required] |
| [비추천안] | [Not Recommended] |
| 솔루션명 | Solution Name |
| 솔루션 ID | Solution ID |
| 추천 이유 | Reason |
| 구현 흐름 | Implementation Flow |
| 준비사항 | Prerequisites |
| 주의사항 | Cautions |
| 적용 이유 | Technical Rationale |
| 구현 개요 | Implementation Overview |
| 전제조건 | Prerequisites |
| 한계점 | Limitations |
| 리스크 상세 | Risk Details |
| 고려사항 | Considerations |
| 판정 | Verdict |
| 권장 | Recommended |
| 검토 필요 | Review Required |
| 비추천 | Not Recommended |
| [미검증] | [Unverified] |
| 부록 A: 재컨설팅 이력 | Appendix A: Revision History |
| 타입 | Type |
| 이전 권고 | Previous Recommendation |
| 새 권고 | New Recommendation |
| 변경 이유 | Change Reason |
| 총 재컨설팅 | Total Revisions |
| 경량 | Light |
| 전체 | Full |
| 부록 B: Deep AI 비교 | Appendix B: Deep AI Comparison |
| 실행 AI | AI Agents |
| 특이 제안 / 강조점 | Key Proposal / Highlight |
| 공통 강점 | Common Strengths |
| 공통 리스크 | Common Risks |
| (없음) | (none) |
| 미실행 | Not executed |

---

## STEP 2 — 파일명 결정

```
base (output_language = "ko"):    YYYYMMDD_[도메인]_[session_id]_자동화_컨설팅
base (output_language = "en"):    YYYYMMDD_[domain]_[session_id]_automation_consulting_EN
base (output_language = "en+ko"): YYYYMMDD_[domain]_[session_id]_automation_consulting_BILINGUAL

output_mode별 파일명 (한국어):
  integrated  → output/[base].txt
  user        → output/[base]_사용자.txt
  developer   → output/[base]_개발자.txt
  split       → output/[base]_사용자.txt + output/[base]_개발자.txt

output_mode별 파일명 (영문, _EN suffix):
  integrated  → output/[base].txt
  user        → output/[base]_user.txt
  developer   → output/[base]_developer.txt
  split       → output/[base]_user.txt + output/[base]_developer.txt

output_mode별 파일명 (이중언어, _BILINGUAL suffix):
  integrated  → output/[base].txt
  user        → output/[base]_user.txt
  developer   → output/[base]_developer.txt
  split       → output/[base]_user.txt + output/[base]_developer.txt

도메인 문자열 처리:
- 공백 → 언더스코어
- 슬래시(/) → 언더스코어
```

---

## 섹션 콘텐츠 분류 기준

권장안 내 각 항목을 사용자용/개발자용으로 분류:

| 항목 | 사용자용 | 개발자용 |
|---|---|---|
| 솔루션명 | ✅ | ✅ |
| 솔루션 ID | — | ✅ |
| 추천 이유 (비기술적 1~2줄) | ✅ | — |
| 적용 이유 (기술적 상세) | — | ✅ |
| 구현 흐름 (단계, 기술용어 최소화) | ✅ | — |
| 구현 개요 (기술적 상세 단계) | — | ✅ |
| 전제조건 — 사용자 준비사항 (계정·라이선스) | ✅ | ✅ |
| 전제조건 — 기술 조건 (API·설정·권한) | — | ✅ |
| 한계점 | — | ✅ |
| 리스크 1줄 요약 + 주의사항 | ✅ | — |
| 리스크 상세 (영향도·발생조건·대응) | — | ✅ |
| 고려사항 | — | ✅ |
| 판정 | ✅ | ✅ |

검토필요·비추천안은 output_mode 관계없이 동일 형식(간략/최소) 유지.

---

## STEP 3 — 본문 구성

### 3-0. 공통 헤더 (output_mode 무관)

```
╔══════════════════════════════════════════════════════════════╗
║           MS 업무 자동화 컨설팅 결과                         ║
╚══════════════════════════════════════════════════════════════╝

세션 ID  : [session_id]
모드     : [Quick | Deep]
생성일시 : [YYYY-MM-DD HH:MM +09:00]
도메인   : [domain]

══════════════════════════════════════════════════════════════
  요구사항 요약
══════════════════════════════════════════════════════════════

  업무 도메인   : [parsed_requirement.domain]
  자동화 대상   : [automation_targets 목록]
  현재 도구     : [current_tools 목록]
  외부 시스템   : [external_systems 목록 또는 "(없음)"]
  프로세스 유형 : [process_type]
  제약 조건     : [constraints 목록 또는 "(없음)"]
  운영 파라미터 : [operational_params 항목 — 해당 값만 표시]
  파싱 신뢰도   : [confidence × 100]%

══════════════════════════════════════════════════════════════
  MS 지원 확인  : [confirmed ✅ | changed ⚠️ | deprecated ❌ | 미실행 —]
══════════════════════════════════════════════════════════════
```

---

### 3-1. 사용자 섹션 (output_mode: integrated / user / split)

```
══════════════════════════════════════════════════════════════
  [사용자용] 권고 요약
══════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────
[권장안]  ← verdict = "권장"인 제안

  솔루션명  : [solution_name] [[미검증]]
  추천 이유 : [reason의 비기술적 요약 — 1~2줄, 업무 효과 중심]

  구현 흐름 :
    1. [단계 — 기술 용어 최소화, 사용자 행동 중심]
    2. [단계]
    ...

  준비사항 :  ← 전제조건 중 사용자가 준비할 항목만
    - [항목 예: M365 라이선스 확인, Excel 파일 OneDrive 이동 등]

  주의사항 :  ← 리스크 1줄 요약 (탈락 위험 있는 항목 우선)
    - [항목 예: DLP 정책으로 외부 발송이 차단될 수 있습니다]

  판정: 권장

──────────────────────────────────────────────────────────────
[검토 필요안]  ← 없으면 섹션 생략

  솔루션명  : [solution_name] [[미검증]]
  추천 이유 : [reason — 2줄 이내]
  판정      : 검토 필요 — [verdict_reason]

──────────────────────────────────────────────────────────────
[비추천안]  ← 없으면 섹션 생략

  솔루션명  : [solution_name]
  비추천 이유: [drop_risk = true인 리스크 1줄 요약]

──────────────────────────────────────────────────────────────
```

---

### 3-2. 개발자 섹션 (output_mode: integrated / developer / split)

```
══════════════════════════════════════════════════════════════
  [개발자용] 기술 상세
══════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────
[권장안]  ← verdict = "권장"인 제안

  솔루션명  : [solution_name] [[미검증]]
  솔루션 ID : [solution_id]
  적용 이유 : [reason — 기술적 상세]

  구현 개요 :
    1. [단계 — 기술 설정·API·커넥터 등 상세 포함]
    2. [단계]
    ...

  전제조건 :  ← 전제조건 전체 (사용자 준비사항 + 기술 조건)
    - [항목]  ← MS 지원 확인에서 추가된 조건 포함

  한계점 :
    - [항목]

  리스크 상세 :
    (보안)     [리스크명]: [설명]
               영향도: [높음|중간|낮음] / 발생조건: [조건]
               대응: [mitigation 상세]
    (라이선스) [리스크명]: [설명]
               영향도: [...] / 발생조건: [...]
               대응: [...]
    (운영)     [리스크명]: [설명]
               영향도: [...] / 발생조건: [...]
               대응: [...]

  고려사항  : [considerations 목록]

  판정: 권장

──────────────────────────────────────────────────────────────
[검토 필요안]  ← 없으면 섹션 생략

  솔루션명  : [solution_name] [[미검증]]
  솔루션 ID : [solution_id]
  적용 이유 : [reason — 2줄 이내]
  판정      : 검토 필요 — [verdict_reason]

──────────────────────────────────────────────────────────────
[비추천안]  ← 없으면 섹션 생략

  솔루션명  : [solution_name]
  솔루션 ID : [solution_id]
  비추천 이유: [drop_risk = true인 리스크 요약]

──────────────────────────────────────────────────────────────
```

---

### 3-3. output_mode별 조합 규칙

```
integrated : 헤더 + 사용자 섹션 + 개발자 섹션 (단일 파일)
user       : 헤더 + 사용자 섹션만 (단일 파일)
developer  : 헤더 + 개발자 섹션만 (단일 파일)
split      : 헤더 + 사용자 섹션 → _사용자.txt
             헤더 + 개발자 섹션 → _개발자.txt
```

### 출력 깊이 규칙

| 판정 | 사용자 섹션 | 개발자 섹션 |
|---|---|---|
| 권장 | 추천이유·구현흐름·준비사항·주의사항·판정 | 전체 (적용이유·구현개요·전제조건·한계점·리스크상세·고려사항·판정) |
| 검토 필요 | 솔루션명·추천이유 2줄·판정사유 | 솔루션명·ID·적용이유 2줄·판정사유 |
| 비추천 | 솔루션명·비추천이유 1줄 | 솔루션명·ID·비추천이유 |

### [미검증] 태그 규칙

```
Quick 모드: unverified = true인 경우만 표시
  → MS 지원 확인(confirmed) 후 자동 해제
  → MS 지원 확인 미실행 시 유지

Deep 모드: solutions.md에 없는 제안 → unverified = true 자동 설정
```

### 리스크 출력 깊이 (Quick vs Deep) — 개발자 섹션 적용

| 항목 | Quick | Deep |
|---|---|---|
| 설명 | 1줄 요약 | 상세 설명 |
| 영향도 | 생략 | 높음/중간/낮음 |
| 발생 조건 | 생략 | 상세 기재 |
| 대응 방안 | 짧게 | 상세 |

---

## STEP 4 — 부록 A: 재컨설팅 이력

**생성 조건**: `total_revision_count > 0`일 때만 생성

### 4-1. REVISION 이벤트 조회

```
오늘 날짜 기준 JSONL 파일 Read: logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl
session_id 필터 적용:
  event.session_id == current_session_id AND event.event_type == "REVISION"
revision 번호 오름차순 정렬
```

**주의**: session_id 필터 생략 금지 — 같은 날 다른 세션 이력 혼입 방지

### 4-2. 부록 A 형식

```
══════════════════════════════════════════════════════════════
  부록 A: 재컨설팅 이력
══════════════════════════════════════════════════════════════

  Rev.[N]
    타입      : [A — 경량 | B — 전체 | B-Override — 사용자 거부]
    이전 권고  : [prev_solution_id]
    새 권고   : [new_solution_id]
    변경 이유  : [change_reason]
    [user_override = true인 경우만 표시]
    ※ 주의: 타입 B(전체 재컨설팅) 권장 → 사용자 요청으로 경량 진행
             결과 일관성이 낮을 수 있습니다.

  Rev.[N+1]
    ...

  총 재컨설팅 : [total_revision_count]회
  (경량: [light]회 | 전체: [full]회)
```

---

## STEP 5 — 부록 B: Deep AI 비교

**생성 조건**: `mode == "deep"`일 때만 생성

```
══════════════════════════════════════════════════════════════
  부록 B: Deep AI 비교
══════════════════════════════════════════════════════════════

  실행 AI: Codex [✅|❌] | Gemini [✅|❌] | Claude ✅  ([N]/3 성공)
  [Fallback 발생 시] Fallback: [실패 모델] → [대체 모델]

  [AI별 제안 비교]

  항목              | Codex         | Gemini        | Claude
  ──────────────────────────────────────────────────────────
  솔루션 ID         | [id or "—"]   | [id or "—"]   | [id]
  특이 제안 / 강조점 | [요약]        | [요약]        | [요약]

  [상호 리뷰 요약]
  공통 강점 :
    · [항목]
  공통 리스크:
    · [항목]
```

`deep_meta`에서 읽는 필드:
- `ai_status`, `fallbacks`, `ai_proposals`, `common_strengths`, `common_risks`

---

## STEP 6 — 파일 쓰기

```
output_mode에 따라 조합 후 Write 도구로 저장:

integrated:
  헤더 + 사용자 섹션(3-1) + 개발자 섹션(3-2) + 부록 A(조건부) + 부록 B(조건부)
  → output/[base].txt

user:
  헤더 + 사용자 섹션(3-1) + 부록 A(조건부)
  → output/[base]_사용자.txt (ko) / output/[base]_user.txt (en / en+ko)

developer:
  헤더 + 개발자 섹션(3-2) + 부록 A(조건부) + 부록 B(조건부)
  → output/[base]_개발자.txt (ko) / output/[base]_developer.txt (en / en+ko)

split:
  헤더 + 사용자 섹션(3-1) + 부록 A(조건부) → output/[base]_사용자.txt (ko) / output/[base]_user.txt (en / en+ko)
  헤더 + 개발자 섹션(3-2) + 부록 A(조건부) + 부록 B(조건부) → output/[base]_개발자.txt (ko) / output/[base]_developer.txt (en / en+ko)

[output_language = "en+ko" 추가 처리]
  위 조합 완료 후, 각 파일의 맨 끝에 구분선 + 한국어 번역 블록을 이어 붙여 저장:

  구분선:
  ════════════════════════════════════════════════════════════
    ■ 한국어 번역 (Korean Translation)
  ════════════════════════════════════════════════════════════

  번역 범위: 헤더부터 부록 A/B(존재 시)까지 전체
  번역 순서: 헤더 → 사용자 섹션 → 개발자 섹션 → 부록 A → 부록 B
  split 모드: 각 파일(_user.txt / _developer.txt)에 개별 번역 블록 추가

인코딩: UTF-8, 줄바꿈: LF, BOM 없음
```

---

## STEP 7 — 완료 보고

```
산출물 생성 완료

파일    : output/[파일명] (split이면 2개 파일 모두 표시)
출력    : [통합본 | 사용자용 | 개발자용 | 분리본(사용자+개발자)]
모드    : [Quick | Deep]
권장안  : [솔루션명] [또는 "(없음)"]
재컨설팅: [N회 포함 | 없음]
Deep AI : [포함 | 미포함]
```

---

## 실패 처리

| 실패 유형 | 처리 방법 |
|---|---|
| `output/` 디렉토리 없음 | Bash로 `mkdir -p output` 후 재시도 |
| JSONL 파일 없음 (부록 A) | 부록 A 생략 + "재컨설팅 이력 파일 없음" 안내 |
| session_id 필터 후 REVISION 0건 | 부록 A 생략 (이력 없음) |
| proposals 비어 있음 | 경고 출력 후 중단: "권고안 없음 — ai-score-compare 결과를 확인해주세요" |
| parsed_requirement 없음 | 요구사항 요약 섹션 생략 + "요구사항 정보 없음" 표시 |
| 파일 쓰기 실패 | 사용자에게 경고 + 본문 터미널 직접 출력 |

---

## 주의사항

- 부록 A REVISION 조회 시 session_id 필터 생략 금지
- user_override = true 이력은 ※ 주의 메시지 반드시 포함
- [미검증] 태그는 솔루션명 바로 뒤에만 표시
- 검토 필요안은 간략 형식, 비추천안은 최소 형식으로 출력
- 비추천안 섹션은 "비추천" verdict가 있을 때만 생성
- 부록 B는 deep_meta가 null이거나 mode = "quick"이면 생략
- MS 지원 확인에서 발견된 추가 조건은 권고안 전제조건에 반영 후 산출물에 포함
- confirmed 후 unverified 태그 자동 해제
- 파일 인코딩: UTF-8 / LF / BOM 없음

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-09 | v1.0 | 최초 작성 |
| 2026-03-09 | v1.1 | 테스트 관찰사항 반영 — parsed_requirement 추가(요구사항 요약 섹션), ms_verify_result 파라미터 추가, SolutionProposal·deep_meta 필드 명세 추가, 출력 깊이 규칙(권장/검토필요/비추천) 명시, Quick/Deep 리스크 출력 포맷 분기, unverified 태그 규칙 확정, 파일 인코딩 규칙 추가 |
| 2026-03-09 | v1.2 | 사용자용/개발자용 섹션 분리 — output_mode 파라미터 추가(integrated 기본/user/developer/split), 섹션 콘텐츠 분류 기준 정의, 사용자 섹션(비기술적 요약·구현흐름·준비사항·주의사항)·개발자 섹션(기술 상세·리스크 상세·한계점·고려사항) 포맷 확정, split 모드 파일 2개 생성 지원 |
| 2026-03-10 | v1.3 | 다국어 지원 추가 — output_language 파라미터(ko 기본/en), STEP 1-5 언어 결정 로직, 영문 레이블 매핑표(45개 항목), 영문 파일명 규칙(_EN suffix, _user/_developer suffix), input_language 기반 기본값 자동 결정 |
| 2026-03-10 | v1.4 | 이중언어(en+ko) 지원 추가 — output_language = "en+ko" 옵션, _BILINGUAL suffix 파일명 규칙, 영문 본문 먼저 + 구분선 + 한국어 번역 블록 순서 구성, STEP 1-5/2/6 en+ko 처리 로직 추가 |
