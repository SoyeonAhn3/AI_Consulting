# Phase 4 — 품질 검증 & 확장 `[진행 중]`

> 다국어 지원, 적합성 검증, 테스트 자동화 및 외부 서비스 연동 확장

**상태**: 🚧 진행 중
**선행 조건**: Phase 3 전체 완료 ✅ (2026-03-10)

---

## 개요

Phase 3 실행 검증 완료를 바탕으로 다국어 지원(영문 요구사항 인식·영문 산출물 생성),
테스트 자동화, 외부 서비스 연동 확장을 진행한다.
웹 UI는 CLI 검증 완료 이후 별도 판단.

---

## 완료 예정 항목

| # | Skill / 모듈 | 상태 | 스킬 타입 |
|---|---|---|---|
| 12 | 다국어 지원 (영문 + 이중언어) | ✅ 구현 완료 | project-specific |
| 13 | `generate-test-list` | 🔲 미시작 | project-specific |
| 14 | Notion 연동 | 🔲 미시작 | general (어댑터) |
| 15 | 웹 UI | ⏸ 보류 | — |
| 16 | 적합성 게이트 (Scope Gate) | ✅ 구현 완료 | project-specific |
| 19 | Excel 보고서 생성 (.xlsx) | ✅ 구현 완료 | project-specific |
| 20 | 토큰 최적화 v2 | ✅ 구현 완료 | — |
| 21 | MS 제품 카탈로그 확장 | ✅ 구현 완료 | project-specific |

---

## 12. 다국어 지원 (영문 + 이중언어) ✅

### 목적
영문으로 입력된 요구사항을 자동 감지하여 분석하고, 영문 산출물을 생성한다.
한국어 요구사항에서도 영문 산출물 생성이 가능하다.
`en+ko` 이중언어 옵션 추가 — 영문 본문 먼저, 이어서 한국어 번역이 한 파일에 포함된다.

### 구현 파일
- `.claude/skills/parse-requirement/SKILL.md` (v4.0)
- `.claude/skills/generate-output/SKILL.md` (v1.4 — en+ko 이중언어 추가)
- `.claude/skills/consult/SKILL.md` (v1.1 — 언어 선택 en+ko 옵션 추가)
- `.claude/skills/ai-score-compare/SKILL.md` (v3.1)

### 핵심 흐름

```
[1] parse-requirement v4.0
    STEP 1-5: 입력 텍스트 언어 감지 (한국어 문자 포함 → "ko", 영문 전용 → "en")
    STEP 2  : 영문 키워드 파싱 추가 (automation/process/scheduled/when 등)
    STEP 4  : 입력 언어별 이중 확인 화면 (ko 화면 / en 화면 분리)
    세션 파일: input_language 필드 저장

[2] consult v1.1
    STEP 6 언어 선택 추가:
      - input_language 기본값으로 선택 화면 표시
      - 사용자 override 가능 (한국어 요구사항 → 영문 산출물 가능)
      - output_language를 세션 파일에 저장 + generate-output에 전달

[3] ai-score-compare v3.1 (Deep 모드)
    output_language = "en" 시 외부 AI 프롬프트 영문 전환
    프롬프트 첫 줄에 "Please respond entirely in English." 추가

[4] generate-output v1.3
    output_language 파라미터 수신
    영문 레이블 매핑표(45개 항목) 적용
    파일명: _EN suffix + _user/_developer suffix (영문 모드)
    모든 텍스트 콘텐츠 영문 생성
```

### 세션 파일 추가 필드

```json
{
  "input_language": "ko",   ← parse-requirement 감지
  "output_language": "en"   ← consult STEP 6 사용자 선택
}
```

### 스킬 타입
project-specific — 컨설팅 도메인 레이블(영문 매핑표)이 프로젝트 전용

---

## 13. generate-test-list (예정)

### 목적
Phase 1~3 개발 완료 후 각 기능을 검증하기 위한 유저 테스트 체크리스트를
자동으로 생성한다.

### 예정 구현 파일
- `.claude/skills/generate-test-list/SKILL.md`

### 출력 형식 (설계 예정)

```markdown
# 유저 테스트 체크리스트 — [날짜]

## Phase 1: 기반 구축
- [ ] dev-log: ERROR 이벤트 기록 및 조회
- [ ] dev-log: CHANGE 이벤트 기록 및 조회
- [ ] dev-log: summary() 집계 확인
- [ ] ai-analysis: AI_CALL 성공/실패 기록
- [ ] ai-analysis: FALLBACK 전환 기록
- [ ] ai-analysis: SCORE 가중합 계산 확인
- [ ] parse-requirement: 신뢰도 80% 이상 파싱 확인
- [ ] parse-requirement: clarification_needed 질문 생성 확인

## Phase 2: 핵심 엔진
- [ ] ms-solution-recommend: 솔루션 후보 3개 생성 확인
- [ ] ai-score-compare: Quick 모드 채점 완료
- [ ] ai-score-compare: Deep 모드 3자 채점 완료
- [ ] ai-score-compare: Fallback 모드 동작 확인

## Phase 3: 산출물 생성
- [ ] generate-output: .txt 파일 생성 확인
- [ ] generate-output: Part 1(비개발자) 섹션 포함 확인
- [ ] generate-output: Part 2(개발자) 섹션 포함 확인
- [ ] consult: 엔드투엔드 흐름 완주 확인
```

### 설계 고려 사항
- 각 Phase 문서(`Phase/PhaseN_*.md`)를 읽어 체크리스트 자동 생성
- 테스트 케이스는 SKILL.md의 "출력 형식" 섹션 기반으로 추출
- **스킬 타입**: project-specific (테스트 항목이 이 프로젝트 스킬 구조에 종속)

---

## 10. Notion 연동 (예정)

### 목적
`generate-output`의 `.txt` 산출물을 Notion 페이지로 직접 발행한다.
Phase 3의 `TxtAdapter`와 동일한 인터페이스의 `NotionAdapter`를 추가한다.

### 예정 구현 파일
- `.claude/skills/notion-export/SKILL.md`
- Notion API 연동 설정: 환경변수 `NOTION_TOKEN`, `NOTION_DATABASE_ID`

### 연동 방법 (설계 예정)

```
generate-output 완료 후 선택적으로 실행:
  notion-export 스킬 호출
    → generate-output 산출물(.txt) 읽기
    → Notion API로 페이지 생성
    → 결과 URL 반환
```

### 필요 환경
- Notion Integration 생성 및 토큰 발급
- 대상 Notion 데이터베이스 공유 설정

### 설계 고려 사항
- **어댑터 패턴**: Phase 3의 `OutputGenerator`에 어댑터만 교체하여 Notion 연동
- **general 스킬 가능성**: Notion 연동 자체는 범용이지만 페이지 구조는 프로젝트 전용
- **스킬 타입**: 최종 확정 전 검토 필요

---

## 11. 웹 UI `[보류]`

### 보류 이유
CLI 에이전트의 안정성과 기능 완성도를 먼저 검증한 후 웹 UI 전환 여부 결정.
현재 우선순위에서 제외.

### 검토 예정 기술
- FastAPI + React (SPA)
- Streamlit (빠른 프로토타이핑)
- CLI 결과를 웹에서 시각화하는 형태로 전환

---

---

## 19. Excel 보고서 생성 (.xlsx) ✅

### 목적
컨설팅 완료 후 `.txt` 산출물과 함께 Excel 보고서를 생성한다.
KR / EN 2시트 구조로 `output_language` 설정에 따라 자동으로 시트를 선택·채운다.

### 구현 파일
- `Word_Template/컨설팅결과_보고서_템플릿.xlsx` — KR + EN 2시트 템플릿 (`{{PLACEHOLDER}}` 형식)
- `Word_Template/fill_excel_template.py` — JSON payload → 템플릿 복사 → 플레이스홀더 채우기 → 저장
- `.claude/skills/consult/SKILL.md` (v1.5) — STEP 6 Excel 생성 질문, STEP 7-E 로직
- `.claude/skills/consult/references/excel-output-schema.md` — JSON 스키마 (generate_excel=true 시 로드)

### 핵심 흐름

```
consult STEP 6: "Excel 보고서도 생성할까요?" → generate_excel=true/false
consult STEP 7: generate-output(.txt) 완료 후 generate_excel=true이면
  Read("references/excel-output-schema.md")
  → JSON 구성 (ko/en/en+ko 섹션 + revisions)
  → Write: output/temp_[session_id].json
  → Bash: py "Word_Template/fill_excel_template.py" "output/temp_[session_id].json"
  → [OK] 확인 후 temp JSON 삭제
```

### fill_excel_template.py 주요 기능
- `{{KEY}}` → regex 치환 (누락 키는 빈 문자열 자동 처리)
- `remove_italic()` — 템플릿 이탤릭 전체 제거
- `auto_adjust_row_heights()` — 내용 기준 행 높이 자동 계산 (병합 셀 포함)
- `_insert_extra_revision_rows()` — revision 3건 초과 시 동적 행 삽입

---

## 20. 토큰 최적화 v2 ✅

### 목적
SKILL.md 상시 로딩 토큰을 줄이기 위해 조건부로만 필요한 콘텐츠를 Reference 파일로 분리한다.

### 구현 내용

| 분리 파일 | 원본 위치 | 로드 조건 | 절감 |
|---|---|---|---|
| `excel-output-schema.md` | consult STEP 7-E (100줄) | generate_excel=true | ~100줄 |
| `deep-mode-guide.md` | ai-score-compare D-STEP 3+5 (100줄) | Deep 모드 확정 시 | ~100줄 |
| `phase-template.md` | phase-doc STEP 2-A (58줄) | 신규 Phase 생성 시 | ~58줄 |
| `label-map.md` | generate-output 영문 레이블표 (45항목) | output_language=en/en+ko | ~50줄 |
| `CLAUDE.md` (AI_Consulting/) | 전역 규칙 중복 (43줄) | — (제거) | ~600토큰/턴 |

추가로 consult / generate-output SKILL.md 전체를 표 형식으로 압축 (~50% 감축).
`fill_excel_template.py` `_fill_cell()` → regex 치환으로 누락 키 처리, JSON 빈 필드 생략 가능.

---

## 21. MS 제품 카탈로그 확장 ✅

### 목적
솔루션 제안이 Excel/VBA/Power BI 위주로 편향되는 문제를 해결한다.
전체 MS 제품군을 AI가 항상 인식하도록 카탈로그를 도입하고 누락 솔루션을 보강한다.

### 구현 내용
- `ai-score-compare/references/ms-product-catalog.md` 신규 — Business Standard 포함 10종, 추가 구독 3종, Azure 4종 목록. STEP 0에서 Quick/Deep 모두 항상 로드.
- `solutions.md` 솔루션 3종 추가:
  - #13 Forms + Power Automate (설문·데이터 수집, effort=낮음)
  - #14 Planner + Power Automate (작업 관리, effort=낮음)
  - #15 AI Builder + Power Automate (OCR·문서 인식, effort=중간)

---

## 16. 적합성 게이트 (Scope Gate) ✅

### 목적
컨설팅 시작 전, 요구사항이 MS 업무자동화 범위에 적합한지 자동 판정한다.
범위를 벗어난 요청은 조기에 안내하여 엉뚱한 권고안이 나오는 것을 방지한다.

### 구현 위치
`consult/SKILL.md` 내 **STEP 1-5** (parse-requirement 완료 직후, 모드 선택 전)

```
STEP 1   → parse-requirement 실행
STEP 1-5 → [신규] 적합성 게이트 판정   ← 여기
STEP 2   → 모드 선택 (Quick | Deep)
```

### 판정 로직

판정에 사용하는 ParsedRequirement 필드:
```
domain            → 사무 도메인인가? (제조설비/의료기기 → 거절 방향)
automation_targets → MS 제품으로 실현 가능한가?
external_systems  → 핵심이 MS 외부 시스템인가? (ERP 내부 로직, PLC 등)
current_tools     → 현재 도구가 MS 생태계인가?
```

### 3단계 분기

```
[진행 가능]
  조건: automation_targets 전체가 MS 생태계 내 해결 가능
  처리: 사용자에게 묻지 않고 자동으로 STEP 2(모드 선택)로 진행
        (안내 메시지는 출력하되 확인 대기 없음)

[부분 지원 가능]
  조건: external_systems이 핵심이지만 MS가 후처리(알림/보고/문서화) 담당 가능
        automation_targets 중 일부만 MS로 커버 가능한 경우
  처리: 지원 가능 범위 / 지원 제외 범위 표시 후 사용자 선택 대기
        → 예: ParsedRequirement.automation_targets를 지원 가능 범위로 축소 후 진행
        → 아니오: 안내 메시지 출력 후 종료

[지원 대상 아님]
  조건: automation_targets 핵심이 하드웨어/설비/PLC 제어
        의료기기·산업 자동화 도메인 + MS 접점 없음
        external_systems이 메인이고 MS 연결 불가
  처리: 안내 메시지 출력 후 종료 (재입력 유도 없음)
```

### 출력 포맷

```
[진행 가능 — 자동 진행, 확인 불필요]
이 요구사항은 MS 업무자동화 범위에 적합합니다.
[주요 제품 힌트] 중심으로 검토를 진행합니다.
(다음 단계로 자동 진행)

[부분 지원 가능 — 사용자 확인 필요]
이 요구사항은 MS만으로 전체 해결하기는 어렵지만,
일부 업무 단계는 지원 가능합니다.

지원 가능 범위: [MS로 처리 가능한 automation_targets]
지원 제외 범위: [MS로 처리 불가한 영역]

이 범위로 진행할까요? (예 / 아니오)

[지원 대상 아님 — 종료]
이 요구사항은 [판정 이유] 중심으로,
현재 도구의 MS 업무자동화 지원 범위를 벗어납니다.
따라서 본 도구로는 적절한 컨설팅을 제공하기 어렵습니다.
```

### "부분 지원 가능" → 예 선택 후 처리

```
1. ParsedRequirement.automation_targets를 지원 가능 범위로 제한
2. 세션 파일에 scope_limited: true 기록
3. ai-score-compare 실행 시 "지원 범위 제한" 컨텍스트 전달
   → 제외 범위는 솔루션 분석에서 명시적으로 스킵
```

### 구현 파일
- `.claude/skills/consult/SKILL.md` → STEP 1-5 신규 추가 (v1.2 예정)

### 스킬 타입
project-specific — MS 업무자동화 도메인 기준에 종속

---

## Phase 4 스킬 범용/전용 분류 (잠정)

| 스킬 | 분류 | 비고 |
|---|---|---|
| `generate-test-list` | project-specific | 이 프로젝트 스킬 구조에 종속 |
| Notion 연동 | 검토 필요 | 연동 자체는 general, 페이지 구조는 project-specific |
| 웹 UI | 보류 | 미정 |
| 적합성 게이트 | project-specific | MS 업무자동화 도메인 기준에 종속, consult 내 인라인 구현 |

---

## 개발 시 주의사항

- Phase 3 `consult` 엔드투엔드 테스트 완료 후 Phase 4 착수
- Notion 연동은 외부 API 의존성 있음 → 네트워크 오류 처리 필수
- 스킬 SKILL.md 작성 시 `skill-template` 기준 템플릿 적용

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-03-06 | Phase 4 설계 초안 작성 (미시작 상태) |
| 2026-03-10 | #12 이중언어(en+ko) 추가 — generate-output v1.4, consult 언어 선택 업데이트 |
| 2026-03-10 | #16 적합성 게이트 설계 확정 — 3단계 분기(진행 가능 자동 / 부분 지원 확인 / 지원 대상 아님 종료), consult STEP 1-5 신규, v1.2 구현 예정 |
| 2026-03-11 | #16 적합성 게이트 ✅ 완료 확인 (consult v1.2에 구현됨, Phase4 문서 미반영 상태였음) |
| 2026-03-11 | #19 Excel 보고서 생성 ✅ 완료 — 템플릿 2시트, fill_excel_template.py, consult STEP 7-E, excel-output-schema.md |
| 2026-03-11 | #20 토큰 최적화 v2 ✅ 완료 — Reference 분리 6종, SKILL.md 압축, CLAUDE.md 중복 제거 |
| 2026-03-11 | #21 MS 제품 카탈로그 확장 ✅ 완료 — ms-product-catalog.md 신규, Forms/Planner/AI Builder solutions.md 추가 |
