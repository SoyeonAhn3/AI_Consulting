# Excel 출력 스키마
# generate_excel=true 시 로드

## 7-E-1. Excel 파일명

Excel은 `output/Archive/` 가 아닌 `output/` 에 저장한다.

xlsx_base = `output/YYYYMMDD_[도메인]_[session_id]_자동화_컨설팅`  (txt_base의 `output/Archive/` → `output/` 로 대체)

| output_language | 파일명 |
|---|---|
| ko | `[xlsx_base]_보고서.xlsx` |
| en | `[xlsx_base]_report.xlsx` |
| en+ko | `[xlsx_base]_report_bilingual.xlsx` |

---

## 7-E-2. 데이터 JSON 구성

**공통 필드** (ko/en 동일):
```
SESSION_ID, MODE("Quick"|"Deep"), CREATED_AT(YYYY-MM-DD HH:MM +09:00),
MS_VERIFY("confirmed ✅"|"changed ⚠️"|"deprecated ❌"|"미실행 —"),
PARSE_CONFIDENCE(confidence×100 또는 "N/A")
```

**ko 섹션** (output_language="ko" 또는 "en+ko"):

세션/요구사항:
```
DOMAIN, REQ_DOMAIN, REQ_TARGET(줄바꿈 연결), REQ_CURRENT_TOOL,
REQ_EXT_SYSTEM("없음" if 없음), REQ_PROCESS_TYPE,
REQ_SCALE, REQ_ATTACHMENT, REQ_HISTORY_SAVE (operational_params에서, 없으면 "해당 없음"),
REQ_CONSTRAINTS("없음" if 없음)
```

솔루션 (verdict별 첫 번째 항목, 없으면 "" 기입):
```
[권장 — verdict="권장"]
SOL_REC_NAME, SOL_REC_ID
SOL_REC_REASON       : reason 비기술 요약 1~2줄
SOL_REC_FLOW         : implementation 단계 "1. ...\n2. ..." (기술 용어 최소화)
SOL_REC_PREREQ       : prerequisites 사용자 준비 항목
SOL_REC_CAUTION      : risks drop_risk=true 1줄 요약
SOL_REC_TECH_REASON  : reason 기술 상세
SOL_REC_IMPL_OVERVIEW: implementation 전체
SOL_REC_PREREQ_TECH  : prerequisites 전체
SOL_REC_LIMITS       : limitations 줄바꿈 연결
SOL_REC_CONSIDERATIONS: considerations 줄바꿈 연결

[검토필요 — verdict="검토필요"] SOL_REV_NAME/ID/REASON/FLOW/PREREQ/CAUTION/TECH_REASON/JUDGMENT
[비추천   — verdict="비추천"]   SOL_NOT_NAME/ID/REASON/TECH_REASON/JUDGMENT
```

리스크 (권장안 risks에서 카테고리별 첫 번째, 없으면 "해당 없음"):
```
RISK_SEC_CONDITION, RISK_SEC_ACTION
RISK_LIC_CONDITION, RISK_LIC_ACTION
RISK_OPS_CONDITION, RISK_OPS_ACTION
```

AI 분석:
```
AI_OVERVIEW     : deep_meta.orchestrator_review | "Quick 모드 — AI 정밀 분석 미제공"
AI_FINDINGS     : deep_meta.common_strengths 줄바꿈 연결 | ""
AI_RECOMMENDATIONS: 권장안 considerations 줄바꿈 연결
AI_EXTRA_RISK_OPP : deep_meta.common_risks 줄바꿈 연결 | ""
```

ROI 필드 (weekly_hours 또는 send_volume 있을 때만 포함, 없으면 필드 생략):
```
ROI_CURRENT_TIME   : "일 1시간" | "주 3시간" | "월 2시간" | "년 12회 58시간" | "미입력"
ROI_IMPROVED_TIME  : "주간 약 10분" (effort 기준 자동 산출)
ROI_SAVE_PERIOD    : "주간 약 2시간 50분" | "" (미입력 시 공백)
ROI_ANNUAL_SAVE    : "연간 약 147시간" | "" (미입력 시 공백)
ROI_PAYBACK        : "약 1~2주" | "약 4개월" | "약 2회차" | "" (미입력 시 공백)
ROI_BUILD_TIME     : "약 4~8시간" (effort 기준)
```

**en 섹션** (output_language="en" 또는 "en+ko"):
ko 섹션과 동일 키·구조, 모든 텍스트 값을 영문으로 생성.
- SESSION_ID, PARSE_CONFIDENCE, MS_VERIFY 값은 ko와 동일
- AI_OVERVIEW(Quick): "Quick mode — AI deep analysis not available"

**Revision 공통 필드** (ko/en 외부, 언어 무관):
```json
"revisions": [{"NO":"Rev.1","TYPE":"A — 경량","PREV":"...","NEW":"...","REASON":"..."},...],
"rev_total": N, "rev_light": N, "rev_full": N
```
en+ko일 때 revisions는 영문 기준 작성 (KR/EN 시트 공용)

---

## 7-E-3. JSON 저장 및 스크립트 호출

```
1. Write: output/temp_[session_id].json
   {
     "output_language": "...",
     "output_path": "output/[xlsx_base에서 파일명 부분]",   ← output/ 직접 저장 (Archive/ 아님)
     "ko": {...},   ← ko 또는 en+ko일 때만
     "en": {...},   ← en 또는 en+ko일 때만
     "revisions": [...], "rev_total": N, "rev_light": N, "rev_full": N
   }
   ※ 빈 값("") 필드는 JSON에서 생략 가능 (스크립트가 missing key를 ""로 처리)

2. Bash: py "Word_Template/fill_excel_template.py" "output/temp_[session_id].json"

3. "[OK]" 확인 후 temp JSON 삭제:
   Bash: rm "output/temp_[session_id].json"
```

---

## 7-E-4. 실패 처리

| 실패 | 처리 |
|---|---|
| 스크립트 오류 | 사용자 안내. .txt는 이미 생성됨 고지 |
| 템플릿 없음 | "Word_Template/컨설팅결과_보고서_템플릿.xlsx 확인 요청" |
| 쓰기 실패 | output/ 디렉토리 권한 확인 안내 |
