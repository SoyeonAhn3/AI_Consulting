# Phase 5 — PA 플로우 설계 생성 `[완료]`

> 컨설팅 권고안에 Power Automate가 포함된 경우, 사용자가 즉시 활용할 수 있는
> 플로우 설계 산출물(txt + Blueprint JSON)을 자동 생성한다.

**상태**: ✅ 완료 (2026-03-11)
**선행 조건**: Phase 4 완료 ✅ (2026-03-11)

---

## 개요

Phase 4까지는 컨설팅 결과를 문서(txt/xlsx)로 제공하는 데 그쳤다.
Phase 5에서는 Power Automate 권고안에 대해 **즉시 활용 가능한 플로우 설계 산출물**을 추가 생성한다.

---

## 완료 예정 항목

| # | 항목 | 상태 | 설명 |
|---|---|---|---|
| 25 | 산출물 헤더 요구사항 요약 블록 추가 | ✅ 구현 완료 | generate-output v1.9: 공통 헤더 자동화 대상/현재 도구/프로세스 3필드. 생성일시 날짜만 표기 |
| 26 | PA 플로우 설계 생성 | ✅ 구현 완료 | consult v1.8 STEP 7-P: 4섹션 구성 + 예외 처리 체크리스트. pa-flow-prompt-guide.md 신규 |

---

## 25. 산출물 헤더 요구사항 요약 블록 추가 ✅

### 목적
output.txt 파일만 봐도 어떤 요구사항에 대한 컨설팅인지 즉시 파악할 수 있도록
공통 헤더에 요구사항 요약 블록을 추가한다.

### 구현 파일
- `.claude/skills/generate-output/SKILL.md` (v1.9)

### 변경 내용

섹션 3-0 공통 헤더에 요구사항 요약 블록 추가:

```
──────────────────────────────────────────────────────────────
요구사항 요약
  자동화 대상 : [automation_targets 핵심 1~2줄]
  현재 도구   : [current_tools]
  프로세스    : [process_type]
──────────────────────────────────────────────────────────────
```

- 제약 조건 필드 제외 (3필드만 표시)
- consult STEP 7에서 이미 전달하는 `parsed_requirement` 데이터 재사용 — 추가 토큰 없음

---

## 26. PA 플로우 설계 생성 ✅

### 목적
컨설팅 권고안에 Power Automate가 포함된 경우, 사용자가 즉시 활용할 수 있는
플로우 설계 산출물(txt + Blueprint JSON)을 자동 생성한다.

### 설계 확정 내용

#### 진입 조건
`solution_id`에 "PowerAutomate" 포함 시 STEP 7-P 트리거

#### 사용자 확인 (consult STEP 6 ④)
```
PowerAutomate가 권고안에 포함되어 있습니다.
PA 플로우 설계 산출물을 생성할까요?
1. 아니오 (기본)   2. 예
```

#### 생성 산출물 (2개)

| 파일 | 경로 | 내용 |
|---|---|---|
| `[날짜]_[session_id]_PA_Flow.txt` | `output/PA_Flow/` | 플로우 다이어그램(ASCII) + PA Copilot 프롬프트 + 수동 구현 포인트 |
| `[날짜]_[session_id]_PA_Flow.json` | `logs/PA_log/` | Blueprint JSON (기록·구조화용, import 아님) |

#### PA_Flow.txt 구성 (4섹션)

```
╔══════════════════════════════════════════════════════════════╗
║           Power Automate 플로우 설계                         ║
╚══════════════════════════════════════════════════════════════╝

세션 ID  : consult_YYYYMMDD_NNN
솔루션   : [solution_name]
생성일시 : YYYY-MM-DD          ← 날짜만 표기 (시간 제외)

══ 1. 플로우 다이어그램 ══

[트리거] ...
     ↓
[조건] 항목 수 > 0?  ← 빈값 예외 반영
     ├─ 예 → [Apply to each]
     │         ├─ [조건] 중복 방지  ← 중복 예외 반영
     │         ├─ [액션] 발송
     │         │    └─ 실패 시 알림  ← 실패 예외 반영
     │         └─ [액션] 이력 기록
     └─ 아니오 → 종료

══ 2. PA Copilot 프롬프트 ══

Create a flow that ... (예외 조건 포함한 자연어)

══ 3. 수동 구현 포인트 ══

필요 커넥터   : [공식 명칭 + 라이선스 등급]
핵심 액션 설정: ① 트리거 / ② 조건 / ③ 액션 / ④ 실패 분기
라이선스      : Standard | Premium
사용자 설정   : [ ] 체크리스트

══ 4. 예외 처리 체크리스트 ══      ← 신규 섹션

[발송 실패]   Scope + Configure run after / 실행 히스토리
[빈값 오류]   Filter array / 0건 조기 종료 Condition
[중복 실행]   발송 상태 컬럼 조건 / 테스트 시 실 발송 방지
[인증 오류]   커넥터 연결 만료 / Shared Mailbox 권한
[부분 실패]   Continue on error / 실패 항목 로깅
```

#### Blueprint JSON 구조
```json
{
  "session_id": "consult_YYYYMMDD_NNN",
  "flow_name": "[솔루션명]",
  "trigger": {
    "type": "[트리거 유형]",
    "connector": "[공식 커넥터명]",
    "filter": {}
  },
  "actions": [
    { "step": 1, "type": "[액션 유형]", "connector": "[커넥터명]", "params": {} }
  ],
  "connectors_required": [],
  "license_tier": "Standard | Premium"
}
```

#### 아키텍처 위치

```
[STEP 7]   generate-output  → .txt / .xlsx
[STEP 7-P] PA 플로우 설계   ← 신규 (PowerAutomate 포함 시만)
     │
     ├─ PowerAutomate 미포함 → 스킵
     └─ PowerAutomate 포함
           │
           ▼
        사용자 확인 (1.아니오 / 2.예)
           │
           └─ 예
                 ↓
              Read("references/pa-flow-prompt-guide.md")
                 ↓
         ┌──────────────────────────────┐
         │  consult 컨텍스트 재사용      │
         │  solution_id / implementation│
         │  automation_targets          │
         │  prerequisites               │
         └──────────────────────────────┘
                 ↓
        txt + JSON 병행 생성
                 ↓
        output/PA_Flow/[날짜]_[session_id]_PA_Flow.txt
        logs/PA_log/[날짜]_[session_id]_PA_Flow.json

[STEP 8]   완료 보고  ← PA 파일명 추가
```

#### 토큰 소요 예측

| 구분 | 토큰 |
|---|---|
| pa-flow-prompt-guide.md 로드 | ~600 |
| 생성 지시 (SKILL.md STEP 7-P) | ~300 |
| 출력 (txt + JSON) | ~900 |
| **합계** | **~1,800 / 실행** |

기존 스텝 대비 부담 없는 수준. 사용자가 "아니오" 선택 시 0 토큰.

### 구현 예정 파일

| 파일 | 작업 |
|---|---|
| `.claude/skills/consult/SKILL.md` | STEP 6 ④ 추가 + STEP 7-P 신규 + STEP 8 완료 보고 2줄 추가 |
| `references/pa-flow-prompt-guide.md` | 신규 생성 (트리거 패턴 / 커넥터 명칭 / 복잡도 가이드) |

### pa-flow-prompt-guide.md 설계

```markdown
## 트리거 유형별 프롬프트 패턴

| 트리거 | PA 공식 명칭 | 프롬프트 패턴 |
|---|---|---|
| 이메일 수신 | Microsoft Outlook | "When an email with [keyword] arrives..." |
| 일정 기반 | Recurrence | "Every [N] days at [time]..." |
| SharePoint 항목 | SharePoint | "When a new item is added to [list]..." |
| Forms 응답 | Microsoft Forms | "When a new response is submitted to [form]..." |
| 수동 트리거 | Manually trigger a flow | "When I manually trigger this flow..." |
| Teams 메시지 | Microsoft Teams | "When a message containing [keyword] is posted..." |

## PA Copilot 프롬프트 작성 규칙
1. 트리거부터 시작: "When / Create a flow that monitors..."
2. 조건은 명시적으로: "If [조건], then [액션], otherwise [액션]"
3. 공식 커넥터 명칭 사용
4. 저장 경로 등은 [placeholder]로 표기
5. 액션 5개 초과 시 단락 분리 권장

## 주요 커넥터 공식 명칭 및 라이선스

| 커넥터 | 공식 명칭 | 등급 |
|---|---|---|
| 이메일 | Microsoft Outlook | Standard |
| 팀 협업 | Microsoft Teams | Standard |
| 문서 저장 | SharePoint | Standard |
| 개인 파일 | OneDrive for Business | Standard |
| 설문 | Microsoft Forms | Standard |
| 할 일 | Microsoft Planner | Standard |
| ERP 연동 | SAP (RFC/BAPI) | Premium |
| HTTP | HTTP | Premium |
| AI 처리 | AI Builder | Premium |

## 복잡도 가이드

| 분기 수 | 액션 수 | 권장 처리 |
|---|---|---|
| 0~1 | ~5 | 단일 프롬프트 |
| 2~3 | 5~10 | 프롬프트 2~3 단락 분리 |
| 4+ | 10+ | Child Flow 분할 권장 — "Use child flows" 명시 |
```

---

## Phase 5 스킬 분류

| 항목 | 타입 | 비고 |
|---|---|---|
| 산출물 헤더 요구사항 요약 | project-specific | generate-output 확장 |
| PA 플로우 설계 생성 | project-specific | consult 인라인 STEP 7-P |
| pa-flow-prompt-guide.md | project-specific | PA 커넥터/트리거 패턴 |

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-03-11 | Phase 5 설계 확정 — #25/#26 항목 정의, 아키텍처 및 토큰 예측 완료 |
| 2026-03-11 | #25 산출물 헤더 요구사항 요약 블록 ✅ 완료 — generate-output v1.9(3필드, 날짜만 표기) |
| 2026-03-11 | #26 PA 플로우 설계 생성 ✅ 완료 — consult v1.8(STEP 6 ④ + STEP 7-P 4섹션), pa-flow-prompt-guide.md 신규(트리거 8종/커넥터표/복잡도/예외처리 패턴/예시 3종), Blueprint JSON exception_handling 필드 추가, 생성일시 날짜만 표기 |
| 2026-03-11 | Phase 5 완료 처리 |
