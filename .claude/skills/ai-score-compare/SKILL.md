---
name: ai-score-compare
version: 4.0
description: MS 생태계 내 자유 제안 + 리스크 2패스 평가로 권고안을 도출한다. Quick 모드는 Claude 단독 자유 분석, Deep 모드는 AI 3종 독립 제안 + Orchestrator 상호 리뷰 + 공통 강점/리스크 추출로 처리한다. parse-requirement 완료 후 모드 선택 시 자동 실행된다.
depends_on:
  - parse-requirement
  - ms-solution-recommend (Deep 모드만)
  - ai-analysis
produces:
  - SolutionProposal (공통 스키마 출력)
  - logs/ai_analysis_YYYYMMDD.jsonl (AI_CALL / FALLBACK / SCORE 기록)
---

# AI Score Compare Skill

MS 생태계 내에서 자유 제안된 솔루션에 대해 리스크 2패스 평가로 권고안을 도출한다.

- **Quick 모드**: Claude 자유 분석 → blocklist 체크 → 리스크 2패스 → 출력
- **Deep 모드**: AI 3종 자유 제안 → Orchestrator 리뷰 → 공통 강점/리스크 → 리스크 2패스 → 출력

---

## 공통 출력 스키마

Quick/Deep 모두 동일한 기본 스키마 사용:

```
솔루션명
솔루션 ID   : 핵심 MS 제품 조합 (공백 없는 "제품명+제품명" 형식)
              예) PowerAutomate+SharePointList+Outlook
적용 이유
구현 개요   : 단계 목록
전제조건
한계점
리스크 및 고려사항
  (보안)    리스크명: 설명 / [탈락가능성: YES|NO] / 대응방안
  (라이선스) 리스크명: 설명 / [탈락가능성: YES|NO] / 대응방안
  (운영)    리스크명: 설명 / 대응방안
  고려사항  : 확인/결정 필요 사항
판정        : 권장 | 검토필요 | 비추천
```

**리스크 출력 깊이·[미검증] 태그 규칙:**
→ STEP 0 인라인 리스크 평가 가이드 참조

---

## STEP 0 — 평가 참조 데이터 (인라인)

아래 데이터를 평가 시 참조한다. (별도 파일 로드 불필요)

### 리스크 평가 가이드

ai-score-compare 스킬이 리스크 평가 및 권고안 판정 시 참조하는
카테고리 정의, 탈락 기준, 판정 규칙.

---

#### 리스크 카테고리

| 카테고리 | 태그 | 해당 항목 |
|---|---|---|
| 보안 | `(보안)` | DLP 정책 차단, 데이터 접근 권한, 컴플라이언스, 외부 발송 제한 |
| 라이선스 | `(라이선스)` | 라이선스 부재, 추가 비용 발생, 플랜 제한, 구독 필요 |
| 운영 | `(운영)` | 유지보수 부담, 담당자 의존, 장애 대응, 실패 알림 부재 |

---

#### 1패스: 탈락 가능성 (drop_risk) 판단 기준

각 리스크에 대해 아래 질문으로 YES/NO 판정:

```
이 리스크가 실제로 발생하면 이 솔루션 자체가 탈락하는가?

  YES (drop_risk = true)
    - 솔루션 구현 자체가 불가능해지는 경우
    - 핵심 요구사항을 달성할 수 없게 되는 경우
    예) DLP 정책으로 외부 발송 완전 차단 → 메일 발송 자동화 목적 달성 불가

  NO (drop_risk = false)
    - 추가 작업이나 조건 충족으로 해소 가능한 경우
    - 인지하고 대응 방안을 적용하면 충분한 경우
    예) 발송 실패 시 알림 없음 → 별도 모니터링 구성으로 보완 가능
```

---

#### Quick 모드 리스크 표시 기준

```
drop_risk = YES                              → 반드시 표시 (심각도 무관)
drop_risk = NO + 심각도 높음                 → 표시
drop_risk = NO + 심각도 중간/낮음            → 생략
```

---

#### Deep 모드 리스크 표시 기준

drop_risk YES/NO 무관 모든 리스크 표시. 상세 형식 사용:

```
(카테고리) 리스크명:
  영향도      : 높음 / 중간 / 낮음
  발생 조건   : [구체적 발생 상황]
  확인 방법   : [사전 확인 방법]
  대응 방안   : [구체적 대응책]
  탈락 가능성 : YES / NO
```

---

#### 2패스: 판정 기준 (verdict)

리스크 평가 결과를 반영하여 최종 판정:

| 판정 | 조건 |
|---|---|
| `권장` | drop_risk = YES 리스크가 없거나 모두 대응 가능한 수준 |
| `검토필요` | drop_risk = YES 리스크가 있으나 조건부 해소 가능 (확인 필요) |
| `비추천` | 아래 조건 중 하나: 핵심 요구사항 충족 불가가 명확 / 라이선스·운영 리스크가 해소 불가 수준 |

#### 비추천안 포함 조건

```
교육적 가치가 있을 때만 포함 (optional):
  - "왜 이 방법은 안 되는지"를 설명할 수 있는 경우
  - 사용자가 이미 해당 방법을 고려했을 가능성이 있는 경우

비추천안도 없으면: 섹션 생략
```

---

#### 판정별 출력 깊이

| 판정 | Quick 출력 항목 | Deep 출력 항목 |
|---|---|---|
| `권장` | 전체 (이유·구현개요·전제조건·한계점·리스크·고려사항) | 동일 + 상호 리뷰 반영 내용 |
| `검토필요` | 솔루션명·ID·이유 2줄·판정사유 | 동일 |
| `비추천` | 솔루션명·ID·비추천이유 1줄 | 동일 |

---

#### 리스크 출력 깊이 (Quick vs Deep)

| 항목 | Quick | Deep |
|---|---|---|
| 설명 | 1줄 요약 | 상세 설명 |
| 영향도 | 생략 | 높음 / 중간 / 낮음 |
| 발생 조건 | 생략 | 구체적 발생 상황 + 확인 방법 |
| 대응 방안 | 짧게 (핵심만) | 상세 (단계적 대응책) |

---

#### blocklist 차단 처리

blocklist 차단 항목 포함 솔루션 처리:

```
차단 항목 포함 시:
  → 해당 솔루션 즉시 제거
  → 출력: "⛔ [제품명] — [코드]: [이유] (대체: [대체 제품])"
  → 나머지 후보로 계속 진행

차단 후 후보 0개 시:
  → "blocklist 차단으로 적합한 솔루션이 없습니다. 요구사항을 재검토해주세요."
```

---

#### [미검증] 태그 규칙

```
Quick 모드: solutions.md에 없는 제안 → [미검증] 태그 표시
  → MS 지원 확인(confirmed) 완료 후 자동 해제
  → MS 지원 확인 미실행 시 유지

Deep 모드: solutions.md 미등재 제안 → unverified = true 자동 설정
```

### MS 제품 카탈로그

솔루션 제안 시 이 목록에서 요구사항에 맞는 제품을 자유롭게 조합할 것.

---

#### Microsoft 365 Business Standard 포함 제품

| 제품 | 카테고리 | 주요 자동화 용도 |
|---|---|---|
| Power Automate | 워크플로 | 트리거 기반 업무 흐름 자동화, 시스템 간 연동 |
| Power Apps | 앱 개발 | 데이터 입력/조회 UI, 모바일·현장 앱 |
| Teams | 협업 | 알림 발송, 채널 관리, 챗봇, 승인 흐름 |
| SharePoint | 문서/데이터 | 문서 관리, 리스트(DB 대체), 포털, 버전관리 |
| Forms | 데이터 수집 | 설문·신청서·점검표·퀴즈 → 자동 집계/알림 |
| Outlook | 이메일 | 이메일 발송·수신·분류·자동 응답 |
| Excel + Office Scripts | 스프레드시트 | 데이터 가공·집계·보고서 생성 자동화 |
| Planner | 업무 관리 | 작업 생성·배정·진행 추적·완료 알림 |
| OneDrive | 파일 저장 | 파일 동기화·공유·백업 자동화 |
| Word | 문서 작성 | 템플릿 기반 보고서·계약서 자동 생성 |

---

#### Power Platform 추가 구독 필요

| 제품 | 라이선스 | 주요 자동화 용도 |
|---|---|---|
| Power BI | Pro 또는 Premium | 데이터 시각화, KPI 대시보드, 자동 리포트 |
| AI Builder | credits 필요 | OCR, 문서 인식·분류, 양식 데이터 자동 추출 |
| Copilot Studio | 별도 라이선스 | 챗봇·AI 에이전트, FAQ 자동 응답, 티켓 생성 |

---

#### Azure (별도 구독 필요 — 구현 난이도 높음)

| 제품 | 주요 자동화 용도 |
|---|---|
| Azure Logic Apps | 엔터프라이즈 워크플로, ERP·SAP·레거시 API 연동 |
| Azure AI Services / OpenAI | LLM 기반 자동화, 문서 인텔리전스, OCR, 음성인식 |
| Azure Functions | 서버리스 코드 실행, 복잡한 데이터 처리 |
| Microsoft Fabric | 대용량 데이터 파이프라인, 데이터레이크 통합 분석 |

---

#### 솔루션 제안 시 주의사항

- **solutions.md 미등재 제품** 제안 시 `[미검증]` 태그 필수
- **Azure 제품**: effort=높음, "Azure 구독 필요" 전제조건 명시
- **AI Builder**: "AI Builder credits 소진 시 추가 비용 발생" 리스크 명시
- **Copilot Studio**: "별도 라이선스 확인 필요" 전제조건 명시
- **단일 제품보다 조합**: 요구사항에 맞게 2~3개 제품을 조합한 솔루션 권장

---

## ━━ QUICK 모드 ━━

### Q-STEP 1 — Claude 자유 분석

ms-solution-recommend를 호출하지 않는다.
Claude가 ParsedRequirement를 기반으로 MS 생태계 내에서 자유롭게 솔루션을 도출한다.

```
[분석 지시]
요구사항: [ParsedRequirement 전체 내용]
제약: MS 생태계 내 솔루션만 제안

아래를 기준으로 최대 3개 솔루션을 자유롭게 제안하세요.
- 요구사항에 가장 적합한 MS 제품 조합
- 구현 가능성과 운영 편의성 고려
- 각 솔루션은 서로 다른 접근 방식이어야 함
- solutions.md 목록에 없는 제품도 자유롭게 제안 가능
```

최대 3개 후보 도출 (최소 1개 필수).

### Q-STEP 2 — blocklist 차단 체크

아래 인라인 차단 목록으로 체크한다.

### 차단 목록 (blocklist)

- Microsoft Stream (클래식) — B001, deprecated 2024-02, 대체: Microsoft Stream (SharePoint 기반)
- Skype for Business — B001, deprecated 2021-07, 대체: Microsoft Teams
- Microsoft Flow (구 명칭) — B001, deprecated 2019-11, 대체: Power Automate
- B002/B003: 현재 없음

차단 적용: 제안된 솔루션에 위 제품 포함 시 즉시 제거 + 사유 표시

각 후보의 제품 목록을 위 차단 목록과 대조.
→ STEP 0 인라인 blocklist 차단 처리 규칙 참조

### Q-STEP 3 — 1패스: 후보별 리스크 평가

각 후보에 대해 권고안 미확정 상태에서 리스크를 평가한다.

**평가 질문 및 카테고리, 표시 기준:**
→ STEP 0 인라인 리스크 평가 가이드 참조

### Q-STEP 4 — 2패스: 권고안 확정

**판정 기준:**
→ STEP 0 인라인 판정 기준 참조

### Q-STEP 4-5 — ROI 사전 계산 (Method F)

ParsedRequirement의 `weekly_hours`가 존재하면 권장안 난이도 기준으로 roi_calc를 계산한다.
(weekly_hours 없으면 이 단계 스킵)

```
effort=낮음 → 개선 후 잔여: 5~10분/주,  구축 소요: 4~8시간
effort=중간 → 개선 후 잔여: 10~20분/주, 구축 소요: 8~20시간
effort=높음 → 개선 후 잔여: 20~30분/주, 구축 소요: 20~40시간

roi_calc = {
  "current_weekly_min":  [weekly_hours × 60],
  "improved_weekly_min": [잔여 범위 중간값],
  "save_weekly_min":     [current - improved],
  "annual_save_hrs":     [save_weekly_min × 52 / 60],
  "build_time_hrs":      [구축 소요 범위 — "N~M시간"],
  "payback_weeks":       [build_time 최소 / save_weekly_min × 60 기준 추정 — "N~M주"]
}
→ 권장안 SolutionProposal에 roi_calc 첨부하여 generate-output에 전달
```

### Q-STEP 5 — 출력

기본 출력: 요약 포맷. 사용자가 "[N]안 상세보기" 요청 시 해당 솔루션 전체 형식 출력.

**[기본 — 요약 포맷]**
```
======================================================
  Quick 모드 솔루션 제안 | session: [session_id]
======================================================

### ✅ 1안: [솔루션명] [미검증 시 → [미검증]] — 권장
- 핵심 기능: [요구사항에서 자동화되는 핵심 업무 1줄]
- 구현 방식: [핵심 MS 제품 흐름 — 예: SharePoint 트리거 → Approval → Teams 알림]
- 난이도: [낮음|중간|높음] | 라이선스: [필요 라이선스]
- 주요 리스크: [핵심 리스크 1줄]

---

### ⚠️ 2안: [솔루션명] — 검토필요 (있으면)
- 핵심 기능: ...
- 구현 방식: ...
- 난이도: ... | 라이선스: ...
- 주요 리스크: ...

---

### ❌ 비추천: [솔루션명] (교육적 가치 있을 때만)
- 비추천 이유: [1줄]

======================================================
상세 분석이 필요한 항목을 말씀해주세요. (예: "1안 상세보기")
```

**[상세보기 요청 시 — 전체 형식]**
```
[N안 — 판정] 상세
솔루션명: [이름]
솔루션 ID: [제품조합ID]
적용 이유: ...
구현 개요:
  1. ...
  2. ...
전제조건:
  - ...
한계점:
  - ...
리스크 및 고려사항:
  (보안) [리스크명]: [1줄 설명] → 대응: [짧게]
  (라이선스) [리스크명]: [1줄 설명] → 대응: [짧게]
  (운영) [리스크명]: [1줄 설명]
  고려사항: [확인 필요 사항]
판정: [판정]
```

### Q-STEP 6 — ai-analysis 기록

각 후보별 SCORE 이벤트 기록:

```
[ai-analysis에 기록]
event_type    : SCORE
session_id    : [session_id]
module        : ai-score-compare
solution_id   : [솔루션 ID]
solution_name : [솔루션명]
mode          : Quick
risks         : {각 리스크별 탈락 가능성}
verdict       : [판정]
```

---

## ━━ DEEP 모드 ━━

### D-STEP 1 — AI 상태 확인

```bash
codex --version 2>/dev/null || echo "codex: 미설치"
gemini --version 2>/dev/null || echo "gemini: 미설치"
```

```
3개 성공 → 정상 Deep 진행
2개 성공 → 경고 표시 후 사용자 선택
             "Codex/Gemini 중 하나를 사용할 수 없습니다.
              1. 2 AI Deep으로 계속 진행
              2. Quick 모드로 전환"
1개 성공 → Deep 중단, Quick 자동 전환 + 안내
             "외부 AI CLI를 사용할 수 없어 Quick 모드로 전환합니다."

실행 AI 수는 최종 출력 및 산출물에 반드시 명시:
  실행 AI: Codex ✅/❌ | Gemini ✅/❌ | Claude ✅
```

→ Deep 진행 확정 시 아래 인라인 가이드 참조:

### Deep 모드 실행 가이드 (인라인)

#### D-STEP 3 프롬프트 구조

각 AI에게 동일한 구조의 프롬프트 전달. **순서 원칙 필수 준수:**
1. 요구사항 분석 및 자유 제안 지시
2. solutions.md 검증 데이터 (참고용)
3. blocklist.md 차단 목록

**output_language 분기:**
```
output_language = "ko" (기본) → 프롬프트 한국어, 응답 한국어 요청
output_language = "en"        → 프롬프트 영문 전환, 응답 영문 요청
  프롬프트 첫 줄에 추가: "Please respond entirely in English."
```

**공통 프롬프트 구조 (output_language = "ko" 기준):**
```
[요구사항]
도메인: [domain]
자동화 대상: [automation_targets]
현재 도구: [current_tools]
외부 시스템: [external_systems 또는 없음]
제약 조건: [constraints]
프로세스 유형: [process_type]

[지시]
MS 생태계 내에서 위 요구사항에 최적화된 솔루션을 1개 자유롭게 제안하세요.
아래 JSON 형식으로만 응답하세요:

{
  "solution_name": "",
  "solution_id": "핵심MS제품을+로연결",
  "reason": "",
  "implementation": ["단계1", "단계2"],
  "prerequisites": ["전제조건1"],
  "limitations": ["한계점1"],
  "risks": [
    {
      "category": "보안|라이선스|운영",
      "name": "",
      "description": "",
      "drop_risk": true,
      "mitigation": ""
    }
  ],
  "considerations": ["고려사항1"],
  "verdict": "권장|검토필요|비추천",
  "verified_in_solutions_md": true
}

[참고 데이터 — 제안을 제한하지 않음]
[solutions_context]

[차단 제품 — 포함 금지]
[blocklist_context]
```

#### Codex 호출
```bash
codex exec "[위 프롬프트]" > /tmp/codex_result.json
```

#### Gemini 호출
```bash
GEMINI_API_KEY=$(py -c "import json,os; d=json.load(open(os.path.expanduser('~/.gemini/settings.json'))); print(d.get('GEMINI_API_KEY',''))" 2>/dev/null || python3 -c "import json,os; d=json.load(open(os.path.expanduser('~/.gemini/settings.json'))); print(d.get('GEMINI_API_KEY',''))" 2>/dev/null) && \
GEMINI_API_KEY="$GEMINI_API_KEY" gemini -p "[위 프롬프트]" > /tmp/gemini_result.json
```

#### Claude 자체 분석
동일 프롬프트로 Claude가 직접 분석 (별도 CLI 호출 없음).

#### JSON 파싱 처리
```
파싱 성공 → 사용
파싱 실패 → 텍스트에서 JSON 추출 정규화 1회 재시도
재시도 실패 → 해당 AI 제외 + FALLBACK 이벤트 기록
```

#### D-STEP 5 Orchestrator 리뷰 형식

3개 제안서를 읽고 Claude가 각 AI 입장에서 예상 반론을 구조화한다.
(실제 Codex/Gemini 재호출 없음 — Claude가 시뮬레이션)

```
[Codex 제안 (솔루션 ID: XXX)에 대해]

  Gemini 입장 반론:
    강점:
    약점:
    누락 전제조건:
    채택 의견:

  Claude 입장 반론:
    강점:
    약점:
    누락 전제조건:
    채택 의견:

[Gemini 제안 (솔루션 ID: YYY)에 대해]
  ...

[Claude 제안 (솔루션 ID: ZZZ)에 대해]
  ...
```

### D-STEP 2 — solutions.md 컨텍스트 준비

ms-solution-recommend 스킬 호출:

```
ms-solution-recommend 실행
  → solutions_context 수신 (검증 데이터 참고용)
  → blocklist_context 수신 (차단 목록)
```

### D-STEP 3 — 3 AI 병렬 실행 (독립 제안서)

**⚡ 병렬 실행 최적화**: Codex와 Gemini를 동시에 실행한다.
1. Codex CLI 실행: `run_in_background: true` 파라미터 사용
2. Gemini CLI 실행: 즉시 실행 (포그라운드)
3. Gemini 완료 후 Codex 결과 수집: `TaskOutput` 도구로 Codex 결과 조회
4. Claude 자체 분석: 병렬 실행 중 또는 완료 후 즉시

→ 나머지는 인라인 Deep 모드 가이드 참조 (프롬프트 구조, JSON 파싱 등)

각 AI 호출마다 AI_CALL 이벤트 기록.

### D-STEP 4 — blocklist 차단 체크

3개 제안서 각각에 대해 blocklist 체크:
- 차단 제품 포함 시 해당 제안서 제외 + 사유 표시

### D-STEP 5 — Claude Orchestrator: 상호 리뷰 구조화

→ D-STEP 1 인라인 Deep 모드 가이드 참조 (Codex/Gemini/Claude 각 입장 반론 구조화 형식)
(실제 Codex/Gemini 재호출 없음 — Claude가 시뮬레이션)

### D-STEP 6 — 공통 강점 / 공통 리스크 추출

```
공통 강점: 2개 이상 AI가 동일하게 채택한 접근법
공통 리스크: 2개 이상 AI가 공통으로 언급한 리스크
차이점: AI별 고유 인사이트 (상호 리뷰에서 도출된 추가 요소)
```

### D-STEP 7 — 1패스 → 2패스 리스크 평가

Quick의 Q-STEP 3~4와 동일한 기준 적용.
단, Deep은 상세 형식 사용 (영향도 + 발생조건/확인방법 + 대응방안).

상호 리뷰에서 도출된 추가 리스크/전제조건도 포함.

### D-STEP 7-5 — ROI 사전 계산 (Method F)

Q-STEP 4-5와 동일한 roi_calc 계산 로직 적용.
권장안 난이도 기준, weekly_hours 존재 시에만 실행.

```
effort=낮음 → 잔여: 5~10분/주,  구축: 4~8시간
effort=중간 → 잔여: 10~20분/주, 구축: 8~20시간
effort=높음 → 잔여: 20~30분/주, 구축: 20~40시간

→ roi_calc 계산 후 권장안 SolutionProposal에 첨부
→ generate-output의 proposals[권장안].roi_calc로 전달 (roi-estimation-guide.md 로드 불필요)
```

### D-STEP 8 — 출력

기본 출력: 요약 포맷 + Deep 전용 AI 비교. 사용자가 "[N]안 상세보기" 요청 시 해당 솔루션 전체 형식 출력.

**[기본 — 요약 포맷]**
```
======================================================
  Deep 모드 솔루션 제안 | session: [session_id]
  실행 AI: Codex ✅ | Gemini ✅ | Claude ✅ (3/3)
======================================================

### ✅ 1안: [솔루션명] [미검증 시 → [미검증]] — 권장
- 핵심 기능: [요구사항에서 자동화되는 핵심 업무 1줄]
- 구현 방식: [핵심 MS 제품 흐름 — 예: SharePoint 트리거 → Approval → Teams 알림]
- 난이도: [낮음|중간|높음] | 라이선스: [필요 라이선스]
- 주요 리스크: [핵심 리스크 1줄]
- AI 합의: [3 AI 공통 채택 여부 — 예: "3/3 AI 공통 제안"]

---

### ⚠️ 2안: [솔루션명] — 검토필요 (있으면)
- 핵심 기능: ...
- 구현 방식: ...
- 난이도: ... | 라이선스: ...
- 주요 리스크: ...
- AI 합의: ...

---

[Deep 전용 부록]
AI별 제안 비교:
  항목         | Codex              | Gemini             | Claude
  ──────────────────────────────────────────────────────────────
  솔루션 ID    | [ID]               | [ID]               | [ID]
  특이점       | ...                | ...                | ...

공통 강점: ...
공통 리스크: ...

======================================================
상세 분석이 필요한 항목을 말씀해주세요. (예: "1안 상세보기")
```

**[상세보기 요청 시 — 전체 형식]**
```
[N안 — 판정] 상세
솔루션명: [이름]
솔루션 ID: [제품조합ID]
적용 이유: (3~5줄, 상호 리뷰 반영 내용 포함)
구현 개요:
  1. ...
전제조건:
  - ...
한계점:
  - ...
리스크 및 고려사항:
  (보안) [리스크명]:
    영향도: 높음/중간/낮음
    발생 조건/확인 방법: ...
    대응 방안: ...
    탈락 가능성: YES/NO
  (라이선스) ...
  (운영) ...
  고려사항: ...
판정: [판정]

상호 리뷰 요약:
  [이 솔루션에 대한 핵심 반론 요약]
```

### D-STEP 9 — ai-analysis 기록

```
AI_CALL: 각 AI 호출마다 (Codex / Gemini / Claude)
FALLBACK: CLI 실패 시
SCORE: 각 후보별
```

---

## 재컨설팅 연계

이 스킬은 재컨설팅 시 세션 상태를 참조해야 한다.

```
세션 상태 파일 READ: logs/session_YYYYMMDD_NNN.json
  → light_revision_count 확인 (3 초과 시 경고)
  → solution_id_current 확인 (타입 A/B 판단 기준)

재컨설팅 완료 후:
  → 세션 상태 파일 UPDATE
  → ai-analysis에 SESSION_STATE 이벤트 기록
```

---

## 실패 처리

| 실패 유형 | 처리 방법 |
|---|---|
| blocklist 데이터 누락 | 경고 표시 후 차단 체크 없이 진행 |
| Codex CLI 실패/타임아웃 | FALLBACK 기록 + Gemini+Claude 2자 비교로 진행 |
| Gemini CLI 실패/인증 오류 | FALLBACK 기록 + Codex+Claude 2자 비교로 진행 |
| JSON 파싱 2회 실패 | 해당 AI 제외 + FALLBACK 기록 + 나머지로 진행 |
| 전체 외부 CLI 실패 | Deep 중단 → Quick 자동 전환 + 사용자 알림 |
| 차단 후 후보 0개 | "요구사항 재정의 또는 blocklist 재검토" 안내 |

---

## 주의사항

- Quick 모드에서 ms-solution-recommend 절대 호출 금지
- Deep 모드 프롬프트 순서: 요구사항 자유 분석 먼저, solutions.md 참고 나중
- 1패스와 2패스를 반드시 순서대로 분리 실행 (순환 의존 방지)
- 솔루션 ID는 "제품명+제품명" 형식, 공백 없이 작성
- solutions.md에 없는 제안은 [미검증] 태그 필수
- 재컨설팅 후에도 동일 스키마로 출력 (판정 변경 시 변경 이유 명시)
- 사용자가 권고안을 선택하기 전까지 MS 지원 확인(WebSearch) 실행 금지
- 기본 출력은 요약 포맷. 상세 분석은 사용자 "[N]안 상세보기" 요청 시에만 출력
- **채점 표 / 리스크 비교 표 / 후보 분석 표 출력 금지** — Q-STEP 5 / D-STEP 8 요약 포맷만 사용
- **분석 중간 과정(자유 제안 목록, 점수 계산 과정) 출력 금지** — 최종 요약 포맷만 출력

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-09 | v3.0 | 최초 작성 |
| 2026-03-10 | v3.1 | output_language en/en+ko 지원 추가 |
| 2026-03-10 | v3.2 | 출력 포맷 요약화 — Q-STEP 5, D-STEP 8 기본 출력을 요약 포맷으로 변경. 상세보기 트리거("[N]안 상세보기") 추가. Deep 요약에 AI 합의 필드 추가 |
| 2026-03-11 | v3.3 | 표 출력 금지 규칙 추가 — 채점표/리스크표/분석 중간 과정 표 금지, 요약 포맷만 출력 (~800 토큰 절감) |
| 2026-03-11 | v3.4 | Method F — ROI 사전 계산 추가: Q-STEP 4-5, D-STEP 7-5에서 weekly_hours 기반 roi_calc 계산 후 권장안에 첨부. generate-output의 roi-estimation-guide.md 로드 제거 (~300 토큰 절감) |
| 2026-03-15 | v4.0 | 성능 최적화 — risk-evaluation-guide/ms-product-catalog/blocklist/deep-mode-guide 인라인 통합 (Read() 4회 제거), D-STEP 3 Codex+Gemini 병렬 실행 (~30-60초 절감) |
