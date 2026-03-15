---
name: generate-output
version: 2.0
description: ai-score-compare의 최종 권고안(SolutionProposal)을 공통 스키마 기반 본문 + 재컨설팅 이력 부록(A) + Deep AI 비교 부록(B)으로 구성된 산출물 파일을 생성한다. output_mode에 따라 통합본(기본) / 사용자용 / 개발자용 / 분리본으로 출력한다. consult 스킬에서 사용자 최종 확인 후 호출한다.
depends_on:
  - ai-score-compare
  - ai-analysis
produces:
  - output/Archive/[날짜]_[도메인]_[session_id]_자동화_컨설팅.txt
---

# Generate Output Skill

## 입력 파라미터

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `session_id` | string | 현재 세션 ID |
| `mode` | string | `"quick"` \| `"deep"` |
| `domain` | string | 업무 도메인 |
| `parsed_requirement` | object | 요구사항 파싱 결과 |
| `proposals` | list | SolutionProposal 목록 |
| `deep_meta` | object\|null | Deep 모드 메타 |
| `ms_verify_result` | string\|null | `confirmed` \| `changed` \| `deprecated` \| null |
| `output_mode` | string | `"integrated"`(기본) \| `"user"` \| `"developer"` \| `"split"` |
| `output_language` | string | `"ko"`(기본) \| `"en"` \| `"en+ko"` — 미전달 시 `input_language` 사용 |

**output_mode 규칙**: integrated=사용자+개발자 단일파일 / user=사용자만 / developer=개발자만 / split=파일2개

## SolutionProposal 필드

```
solution_name, solution_id, verdict("권장"|"검토필요"|"비추천"), reason,
implementation[], prerequisites[], limitations[], risks[{category,name,description,drop_risk,mitigation}],
considerations[], unverified(bool), verdict_reason
```

## deep_meta 필드 (Deep 모드)

```
ai_status{codex,gemini,claude}, fallbacks[], ai_proposals{codex,gemini,claude},
common_strengths[], common_risks[], orchestrator_review
```

---

## STEP 1 — 출력 디렉토리 확인

```
output/Archive/ 없으면 Bash: mkdir -p output/Archive
```

## STEP 1-5 — output_language 결정

```
전달값 있으면 사용 → 없으면 parsed_requirement.input_language → 없으면 "ko"

"en"    : 아래 인라인 레이블 매핑으로 모든 고정 레이블 교체. 파일명에 _EN suffix. 본문 영문 생성.
"en+ko" : [1] 영문 전체 본문 생성 → [2] 아래 구분선 + 한국어 번역 이어붙임. 파일명 _BILINGUAL suffix.
          구분선: ════════════════════ ■ 한국어 번역 (Korean Translation) ════════════════════

### 영문 레이블 매핑 (인라인)
## 헤더/메타
MS 업무 자동화 컨설팅 결과→MS Automation Consulting Report | 세션 ID→Session ID | 모드→Mode | 생성일시→Generated | 도메인→Domain | MS 지원 확인→MS Support Check

## 섹션 레이블
요구사항 요약→Requirement Summary | 업무 도메인→Business Domain | 자동화 대상→Automation Target | 현재 도구→Current Tools | 외부 시스템→External Systems | 프로세스 유형→Process Type | 제약 조건→Constraints | 운영 파라미터→Operational Params | 파싱 신뢰도→Parse Confidence

## 권고 구분
[사용자용] 권고 요약→[User] Recommendation Summary | [개발자용] 기술 상세→[Developer] Technical Details | [권장안]→[Recommended] | [검토 필요안]→[Review Required] | [비추천안]→[Not Recommended]

## 솔루션 필드
솔루션명→Solution Name | 솔루션 ID→Solution ID | 추천 이유→Reason | 구현 흐름→Implementation Flow | 준비사항→Prerequisites | 주의사항→Cautions | 적용 이유→Technical Rationale | 구현 개요→Implementation Overview | 전제조건→Prerequisites | 한계점→Limitations | 리스크 상세→Risk Details | 고려사항→Considerations

## 판정
판정→Verdict | 권장→Recommended | 검토 필요→Review Required | 비추천→Not Recommended | [미검증]→[Unverified]

## 부록
부록 A: 재컨설팅 이력→Appendix A: Revision History | 타입→Type | 이전 권고→Previous Recommendation | 새 권고→New Recommendation | 변경 이유→Change Reason | 총 재컨설팅→Total Revisions | 경량→Light | 전체→Full
부록 B: Deep AI 비교→Appendix B: Deep AI Comparison | 실행 AI→AI Agents | 특이 제안 / 강조점→Key Proposal / Highlight | 공통 강점→Common Strengths | 공통 리스크→Common Risks | (없음)→(none) | 미실행→Not executed

[ROI — Method F]
proposals[권장안].roi_calc 값을 그대로 사용한다. (roi_calc는 ai-score-compare에서 항상 제공됨)

[Excel 병렬 로드 — Method D]
generate_excel=true 시: consult STEP 7-E에서 excel-output-schema.md를 로드한다.
```

## STEP 2 — 파일명 결정

| output_language | base |
|---|---|
| ko | `output/Archive/YYYYMMDD_[도메인]_[session_id]_자동화_컨설팅` |
| en | `output/Archive/YYYYMMDD_[domain]_[session_id]_automation_consulting_EN` |
| en+ko | `output/Archive/YYYYMMDD_[domain]_[session_id]_automation_consulting_BILINGUAL` |

| output_mode | 파일명 (ko) | 파일명 (en/en+ko) |
|---|---|---|
| integrated | `[base].txt` | `[base].txt` |
| user | `[base]_사용자.txt` | `[base]_user.txt` |
| developer | `[base]_개발자.txt` | `[base]_developer.txt` |
| split | `[base]_사용자.txt` + `[base]_개발자.txt` | `[base]_user.txt` + `[base]_developer.txt` |

도메인 문자열: 공백·슬래시 → 언더스코어

---

## STEP 3 — 본문 구성

### 섹션 콘텐츠 분류

| 항목 | 사용자 | 개발자 |
|---|---|---|
| 솔루션명 | ✅ | ✅ |
| 솔루션 ID | — | ✅ |
| 추천 이유 (비기술 1~2줄) | ✅ | — |
| 적용 이유 (기술 상세) | — | ✅ |
| 구현 흐름 (기술 용어 최소화) | ✅ | — |
| 구현 개요 (기술 상세) | — | ✅ |
| 전제조건 — 사용자 준비 | ✅ | ✅ |
| 전제조건 — 기술 조건 | — | ✅ |
| 한계점 | — | ✅ |
| 리스크 1줄 요약 + 주의사항 | ✅ | — |
| 리스크 상세 (영향도·발생조건·대응) | — | ✅ |
| 고려사항 | — | ✅ |
| 판정 | ✅ | ✅ |

**출력 깊이**: 권장=전체 / 검토필요=1줄 요약+판정사유 / 비추천=솔루션명+1줄 (Method E)

**리스크 출력 (개발자 섹션)**: Quick=1줄요약·영향도생략 / Deep=상세(영향도·발생조건·대응)

### 3-0. 공통 헤더

```
╔══════════════════════════════════════════════════════════════╗
║           MS 업무 자동화 컨설팅 결과                         ║
╚══════════════════════════════════════════════════════════════╝

세션 ID  : [session_id]
모드     : [Quick | Deep]
생성일시 : [YYYY-MM-DD]
도메인   : [domain]
MS 지원  : [confirmed ✅ | changed ⚠️ | deprecated ❌ | 미실행 —]

──────────────────────────────────────────────────────────────
요구사항 요약
  자동화 대상 : [automation_targets 핵심 1~2줄]
  현재 도구   : [current_tools]
  프로세스    : [process_type]
──────────────────────────────────────────────────────────────
```

### 3-1. 사용자 섹션

```
══════════════════════════════════════════════════════════════
  [사용자용] 권고 요약
══════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────
[권장안]

  솔루션명  : [solution_name] [[미검증]]
  추천 이유 : [reason 비기술 요약 1~2줄]
  구현 흐름 : 1. [단계] / 2. [단계] ...
  준비사항  : - [사용자 준비 항목]
  주의사항  : - [리스크 1줄, drop_risk 우선]
  판정: 권장

──────────────────────────────────────────────────────────────
[검토 필요안]  ← 없으면 생략
  솔루션명 / 추천이유 2줄 / 판정: 검토 필요 — [verdict_reason]

──────────────────────────────────────────────────────────────
[비추천안]  ← 없으면 생략
  솔루션명 / 비추천이유 1줄

──────────────────────────────────────────────────────────────
[ROI 예측]  ← weekly_hours 또는 send_volume 있을 때만 출력

[weekly_hours 입력된 경우]
  현재 작업 시간    : [입력 단위 그대로] (직접 입력)
  개선 후 예상 시간 : [effort 기준 잔여 시간] (모니터링·예외처리 포함)
  ─────────────────────────────────────────
  절감 효과         : [입력 단위 기준 절감량]
                      연간 약 [연간 절감시간] ([빈도·단위 기준])
                      구축 소요 약 [effort범위] → ROI 달성 약 [N단위]

  ※ 개선 후 예상 시간은 추정값입니다.

[weekly_hours = null (모름) 인 경우]
  현재 작업 시간    : 미입력
  개선 후 예상 시간 : [effort 기준 잔여 시간]

  절감 효과 시나리오 (현재 업무 시간에 가장 가까운 항목을 참고하세요)

    보수적 (주 1시간 기준) : 연간 약 [52h-잔여] 절감 / ROI 달성 약 [N]주
    중간   (주 3시간 기준) : 연간 약 [156h-잔여] 절감 / ROI 달성 약 [N]주
    적극적 (주 5시간 기준) : 연간 약 [260h-잔여] 절감 / ROI 달성 약 [N]주

  ※ 실제 소요 시간을 알고 계시면 "ROI 재산출: [시간]" 으로 말씀해주세요.
```

### 3-2. 개발자 섹션

```
══════════════════════════════════════════════════════════════
  [개발자용] 기술 상세
══════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────
[권장안]

  솔루션명  : [solution_name] [[미검증]]
  솔루션 ID : [solution_id]
  적용 이유 : [reason 기술 상세]
  구현 개요 : 1. [단계] / 2. [단계] ...
  전제조건  : - [전체 항목 + MS 지원 확인 추가 조건]
  한계점    : - [항목]
  리스크 상세:
    (보안)     [명]: [설명] / 영향도: [...] / 발생조건: [...] / 대응: [...]
    (라이선스) [명]: [설명] / ...
    (운영)     [명]: [설명] / ...
  고려사항  : [목록]
  판정: 권장

──────────────────────────────────────────────────────────────
[검토 필요안]  솔루션명/ID / 적용이유 2줄 / 판정사유
[비추천안]     솔루션명/ID / 비추천이유
```

### 3-3. output_mode 조합

| mode | 파일 구성 |
|---|---|
| integrated | 헤더 + 사용자 + 개발자 |
| user | 헤더 + 사용자 |
| developer | 헤더 + 개발자 |
| split | 헤더+사용자 → _사용자.txt / 헤더+개발자 → _개발자.txt |

---

## STEP 4 — 부록 A: 재컨설팅 이력

**조건**: `total_revision_count > 0`일 때만 생성

```
JSONL Read: logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl
필터: event.session_id == current_session_id AND event.event_type == "REVISION"
정렬: revision 번호 오름차순
```

**⚠️ session_id 필터 생략 금지**

```
══════════════════════════════════════════════════════════════
  부록 A: 재컨설팅 이력
══════════════════════════════════════════════════════════════

  Rev.[N]
    타입     : [A — 경량 | B — 전체 | B-Override — 사용자 거부]
    이전 권고 : [prev_solution_id]
    새 권고  : [new_solution_id]
    변경 이유 : [change_reason]
    [user_override=true 시] ※ 주의: 타입 B 권장 → 사용자 요청으로 경량 진행. 결과 일관성 낮을 수 있음.

  총 재컨설팅 : [total]회 (경량: [light]회 | 전체: [full]회)
```

## STEP 5 — 부록 B: Deep AI 비교

**조건**: `mode == "deep"`일 때만 생성

```
══════════════════════════════════════════════════════════════
  부록 B: Deep AI 비교
══════════════════════════════════════════════════════════════

  실행 AI: Codex [✅|❌] | Gemini [✅|❌] | Claude ✅  ([N]/3 성공)
  [Fallback 발생 시] Fallback: [실패 모델] → [대체 모델]

  항목              | Codex       | Gemini      | Claude
  ──────────────────────────────────────────────────────
  솔루션 ID         | [id or "—"] | [id or "—"] | [id]
  특이 제안 / 강조점 | [요약]      | [요약]      | [요약]

  공통 강점 : · [항목]
  공통 리스크: · [항목]
```

## STEP 6 — 파일 쓰기 + Excel JSON 병행 구성 (Method D)

```
Write 도구로 저장. 인코딩: UTF-8 / LF / BOM 없음
저장 경로: output/Archive/

integrated : 헤더 + 사용자 + 개발자 + 부록A(조건부) + 부록B(조건부) → [base].txt
user       : 헤더 + 사용자 + 부록A(조건부) → [base]_사용자.txt
developer  : 헤더 + 개발자 + 부록A(조건부) + 부록B(조건부) → [base]_개발자.txt
split      : user 파일 + developer 파일 각각 생성

en+ko: 각 파일 맨 끝에 구분선 + 한국어 번역 블록 추가 (헤더~부록 전체 번역)

[Method D — txt 구성과 동시에 Excel JSON 딕셔너리 병행 구성]
generate_excel=true 시:
  txt 본문 섹션을 작성하면서 excel-output-schema.md 필드값을 인메모리로 동시 수집
  SOL_REC_REASON → txt 사용자 섹션 reason과 동일 텍스트 재사용
  SOL_REC_FLOW   → txt 구현 흐름과 동일 텍스트 재사용
  RISK_*         → txt 리스크에서 추출한 텍스트 재사용
  txt Write 완료 직후 바로 JSON Write 실행 (별도 재구성 없음)
```

## STEP 6-5 — CSV 이력 기록

파일 쓰기 완료 후 `archive/Consulting_Summary.csv`에 한 줄 추가.

```
CSV 경로: archive/Consulting_Summary.csv  (고정 파일명)

컬럼 (헤더):
  날짜, 세션ID, 최종솔루션, 난이도, ROI연간절감, 산출물파일이름

값 추출:
  날짜         : 생성일시 앞 10자 (YYYY-MM-DD)
  세션ID       : session_id
  최종솔루션   : verdict="권장"인 proposal의 solution_id
  난이도       : verdict="권장"인 proposal의 effort ("낮음"|"중간"|"높음", 없으면 "미확인")
  ROI연간절감  : ROI_ANNUAL_SAVE 계산값 (weekly_hours 없으면 "")
  산출물파일이름: 생성된 파일명 (split이면 쉼표로 연결)

처리:
  archive/ 없으면 Bash: mkdir -p archive
  파일 없으면 Write로 헤더+행 신규 생성
  파일 있으면 Edit으로 마지막 줄 뒤에 데이터 행만 추가 (헤더 중복 금지)
```

**실패 시**: 경고 출력 후 STEP 7 계속 진행 (CSV 실패가 산출물 생성을 막지 않음)

---

## STEP 7 — 완료 보고

```
산출물 생성 완료

파일   : output/[파일명] (split이면 2개)
출력   : [통합본 | 사용자용 | 개발자용 | 분리본]
모드   : [Quick | Deep]
권장안 : [솔루션명]
재컨설팅: [N회 포함 | 없음]
Deep AI : [포함 | 미포함]
```

---

## [미검증] 태그 규칙

- Quick: `unverified=true`인 경우만, MS 지원 확인(confirmed) 후 자동 해제
- Deep: solutions.md 미등재 → `unverified=true` 자동 설정

## 실패 처리

| 실패 유형 | 처리 |
|---|---|
| output/ 없음 | `mkdir -p output` 후 재시도 |
| JSONL 없음 (부록A) | 부록A 생략 |
| REVISION 0건 | 부록A 생략 |
| proposals 비어 있음 | 경고 후 중단 |
| parsed_requirement 없음 | 요구사항 섹션 생략 |
| 파일 쓰기 실패 | 경고 + 터미널 직접 출력 |

## 주의사항

- 부록A REVISION 조회 시 session_id 필터 생략 금지
- user_override=true 이력은 ※ 주의 메시지 필수
- [미검증] 태그는 솔루션명 바로 뒤에만
- 부록B는 deep_meta=null 또는 mode=quick이면 생략
- MS 지원 확인 추가 조건은 권고안 전제조건에 반영 후 산출물 포함

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-09 | v1.0 | 최초 작성 |
| 2026-03-09 | v1.1 | parsed_requirement, ms_verify_result, SolutionProposal 명세 추가 |
| 2026-03-09 | v1.2 | output_mode 파라미터 추가 (integrated/user/developer/split) |
| 2026-03-10 | v1.3 | output_language 파라미터(ko/en), 영문 레이블 매핑표, 파일명 규칙 |
| 2026-03-10 | v1.4 | en+ko 이중언어 지원 추가 |
| 2026-03-11 | v1.5 | 토큰 최적화 — 영문 레이블 매핑표를 references/label-map.md로 분리. 전체 구조 표 형식으로 압축 |
| 2026-03-11 | v1.6 | 헤더 단순화 — 요구사항 요약 섹션 제거, 세션ID/모드/생성일시/도메인/MS지원만 표시 (~300 토큰 절감) |
| 2026-03-11 | v1.7 | ROI 블록 조건부 출력 추가 (weekly_hours/send_volume 있을 때), STEP 6-5 CSV 이력 기록 추가 (archive/Consulting_Summary.csv 자동 append) |
| 2026-03-11 | v1.8 | 토큰 최적화 D/E/F — D: txt+Excel JSON 병행 구성(별도 재생성 제거, ~400토큰+10~15초 절감), E: 검토필요=1줄+판정사유/비추천=솔루션명+1줄(~150~300토큰 절감), F: roi_calc 사전 수신 시 roi-estimation-guide.md 로드 생략(~200토큰 절감) |
| 2026-03-11 | v1.9 | 헤더에 요구사항 요약 블록 추가 — 자동화 대상 / 현재 도구 / 프로세스 3필드 (제약 조건 제외) |
| 2026-03-15 | v2.0 | 성능 최적화 — label-map.md 인라인 통합 (Read() 1회 제거), roi-estimation-guide.md 로드 제거 (roi_calc 항상 사전 제공) |
