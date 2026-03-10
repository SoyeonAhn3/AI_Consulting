# Phase 1 — 기반 구축 `[완료]`

> 로깅, 요구사항 파싱 등 모든 모듈이 공통으로 사용하는 기반 레이어

**완료일**: 2026-03-06
**상태**: ✅ 전체 완료

---

## 개요

Phase 1은 이후 모든 Phase에서 공통으로 사용하는 기반 인프라를 구축한다.
개발 이력 기록, AI 호출 추적, README 자동 갱신, 요구사항 파싱의 4가지 핵심 기능을 완성했다.

---

## 완료 항목

| # | Skill / 모듈 | 파일 | 스킬 타입 | 상태 |
|---|---|---|---|---|
| 1 | `dev-log` | `src/modules/dev_log.py` | general | ✅ 완료 |
| 2 | `ai-analysis` | `src/modules/ai_analysis_log.py` | general | ✅ SKILL.md v2.0 완료 |
| 3 | `readme-update` | `.claude/skills/readme-update/SKILL.md` | general | ✅ 완료 |
| 4 | `parse-requirement` | `src/modules/requirement_parser.py` | project-specific | ✅ SKILL.md v3.0 완료 |
| 공통 | `ai-multi-discussion` | `.claude/skills/ai-multi-discussion/SKILL.md` | general | ✅ 완료 |
| 공통 | `skill-template` | `.claude/skills/skill-template/SKILL.md` | general | ✅ 완료 |

---

## 1. dev-log

### 목적
개발 중 발생하는 에러, 수정 이유, 변경 내역을 JSONL 형식으로 날짜별 파일에 기록하고 조회한다.

### 구현 파일
- `src/modules/dev_log.py`
- `.claude/skills/dev-log/SKILL.md`

### 핵심 클래스 / 구조

```python
class EventType(str, Enum):
    ERROR  = "ERROR"   # 에러 발생
    CHANGE = "CHANGE"  # 수정 이유 + 변경 내역
    INFO   = "INFO"    # 일반 실행 흐름 메모

class DevLogger:
    # 싱글턴 패턴 — 모든 모듈이 동일 session_id 공유
    _instance: Optional[DevLogger] = None

    def error(module, message, **kwargs)
    def change(module, message, before, after, reason, **kwargs)
    def info(module, message, **kwargs)
    def view(event_type, module, limit, date)   # 조회
    def summary(date)                           # 집계 요약
```

### JSONL 스키마

```json
{
  "timestamp": "2026-03-06T14:32:01+00:00",
  "session_id": "a1b2c3d4",
  "module": "MSGraphConnector",
  "event_type": "ERROR",
  "message": "OAuth 토큰 만료",
  "data": { "error_code": 401 }
}
```

### 로그 파일 위치
```
logs/dev_YYYYMMDD.jsonl   (날짜별 자동 분리)
```

### 설계 결정 사항
- **싱글턴 패턴**: 하나의 세션에서 모든 모듈이 동일한 `session_id`를 공유하여 호출 추적이 가능하도록 설계
- **Windows CP949 대응**: `sys.stdout.buffer.write(...encode("utf-8"))` 로 직접 출력하여 터미널 한글 깨짐 방지
- **날짜별 파일 분리**: 장기 운영 시 파일 크기 관리 및 날짜 기반 필터 조회를 위해 `dev_YYYYMMDD.jsonl` 패턴 채택

### 사용 예시

```python
from src.modules.dev_log import DevLogger
logger = DevLogger.get_instance()

logger.error("MSGraphConnector", "OAuth 토큰 만료", error_code=401)
logger.change("RecommendationEngine", "가중치 수정",
              before="적합성 40%", after="적합성 35%", reason="합산 오류 수정")
logger.info("InputParser", "파싱 완료", input_length=320)
```

```bash
py -c "from src.modules.dev_log import DevLogger; DevLogger.get_instance().view()"
py -c "from src.modules.dev_log import DevLogger; DevLogger.get_instance().view(event_type='ERROR')"
py -c "from src.modules.dev_log import DevLogger; DevLogger.get_instance().summary()"
```

---

## 2. ai-analysis

### 목적
AI 모델 호출 이력(AI_CALL), 가중치 채점 결과(SCORE), Fallback 전환 이력(FALLBACK)을 JSONL 형식으로 기록하고 조회한다.

### 구현 파일
- `src/modules/ai_analysis_log.py`
- `.claude/skills/ai-analysis/SKILL.md`

### 핵심 클래스 / 구조

```python
class AIEventType(str, Enum):
    SCORE    = "SCORE"     # 가중치 채점 결과
    AI_CALL  = "AI_CALL"   # AI 모델 호출 이력
    FALLBACK = "FALLBACK"  # Fallback 전환 이력

class AIAnalysisLogger:
    # 싱글턴 패턴
    def ai_call(module, model, mode, tokens_used, success, latency_ms)
    def fallback(module, failed_model, reason, fallback_to)
    def score(module, solution_name, scores, weighted_total, rank)
    def view(event_type, module, limit, date)
    def summary(date)   # 토큰 소모량 + Fallback 횟수 포함
```

### JSONL 스키마

```json
{
  "timestamp": "2026-03-06T14:32:01+00:00",
  "session_id": "a1b2c3d4",
  "module": "AIOrchestrator",
  "event_type": "AI_CALL",
  "message": "AI 호출 성공: gpt-4o [Deep]",
  "data": {
    "model": "gpt-4o",
    "mode": "Deep",
    "tokens_used": 1240,
    "success": true,
    "latency_ms": 4200
  }
}
```

### 로그 파일 위치
```
logs/ai_analysis_YYYYMMDD.jsonl   (날짜별 자동 분리)
```

### 설계 결정 사항
- **3가지 이벤트 타입 분리**: AI_CALL / SCORE / FALLBACK을 별도 메서드로 분리하여 호출 목적 명확화
- **summary()에 토큰 집계 추가**: 비용 최적화 모니터링을 위해 `총 토큰 소모` 항목 포함
- **Fallback 카운터**: `summary()`에서 Fallback 발생 횟수를 별도 집계하여 안정성 지표로 활용

### 가중치 점수 기준 (SCORE 기록 시 참조)

| 평가 항목 | 가중치 |
|---|---|
| 적합성 | 35% |
| 구현 난이도 | 30% |
| 유지보수성 | 15% |
| 라이선스 적합성 | 10% |
| 확장성 | 10% |

### 사용 예시

```python
from src.modules.ai_analysis_log import AIAnalysisLogger
logger = AIAnalysisLogger.get_instance()

logger.ai_call("AIOrchestrator", model="gpt-4o", mode="Deep",
               tokens_used=1240, success=True, latency_ms=4200)
logger.fallback("AIOrchestrator", failed_model="gemini",
                reason="timeout", fallback_to="claude-sonnet-4-6")
logger.score("RecommendationEngine", solution_name="Power Automate + Teams",
             scores={"적합성": 4.5, "구현난이도": 4.0, "유지보수성": 3.5,
                     "라이선스적합성": 5.0, "확장성": 3.0},
             weighted_total=4.175, rank=1)
```

---

## 3. readme-update

### 목적
프로젝트 방향성/구조/개발 로직 변경 또는 개발 Status 업데이트 시 README.md를 자동으로 갱신한다.

### 구현 파일
- `.claude/skills/readme-update/SKILL.md` (Claude Code 스킬)

### 동작 방식
Python 모듈 없이 Claude Code가 직접 실행하는 스킬.
Claude가 Read → Edit → dev-log 기록 순서로 README를 업데이트한다.

### 스킬 실행 절차
1. `README.md`, `UserRequirement.md`, `src/modules/`, `.claude/skills/` 현재 상태 확인
2. 변경 유형 분류 (완료/방향성변경/구조변경/Phase변경/전체갱신)
3. Edit 도구로 해당 섹션만 수정 (전체 재작성 금지)
4. `dev-log`에 변경 이력 기록

### 상태 표기 규칙
```
✅ 완료   🚧 진행 중   🔲 미시작   ⏸ 보류
[완료] [진행 중] [미시작] [보류]
```

---

## 4. parse-requirement

### 목적
사용자의 자유 형식 업무 자동화 요구사항을 구조화된 `ParsedRequirement`로 변환한다.
불명확한 항목은 추가 질문 목록(`clarification_needed`)으로 반환한다.

### 구현 파일
- `src/modules/requirement_parser.py`
- `.claude/skills/parse-requirement/SKILL.md`

### 핵심 데이터 구조

```python
@dataclass
class ParsedRequirement:
    domain: str                    # 업무 도메인
    automation_targets: list[str]  # 자동화 대상 프로세스 목록
    current_tools: list[str]       # 현재 사용 중인 도구 목록
    constraints: list[str]         # 제약 조건 목록
    ms_products_hint: list[str]    # 추론된 MS 제품 힌트 (MS 전용)
    clarification_needed: list[str]# 추가 질문 필요 항목
    raw_input: str                 # 사용자 원본 입력
    confidence: float              # 파싱 신뢰도 (0.0 ~ 1.0)
```

### 파싱 규칙 구조

| 파싱 단계 | 방법 | 키워드/패턴 |
|---|---|---|
| 1. 업무 도메인 추출 | 키워드 빈도 매칭 | 인사/HR, 구매/조달, 영업/CRM 등 10개 도메인 |
| 2. MS 제품 힌트 추출 | 키워드 매칭 | Power Automate, Teams, SharePoint 등 8개 제품 |
| 3. 자동화 대상 추출 | 트리거 키워드 + 문장 분리 | "자동", "매주", "취합", "발송" 등 23개 트리거 |
| 4. 현재 도구 추출 | 알려진 도구명 직접 탐지 + 정규식 | Excel, SAP, Slack 등 14개 알려진 도구 |
| 5. 제약 조건 추출 | 키워드 매칭 | "라이선스", "보안", "예산" 등 12개 키워드 |
| 6. 신뢰도 계산 | 항목별 가중 점수 합산 | domain(40) + targets(30) + tools(15) + hint(15) |

### 신뢰도 기준

| 신뢰도 | 의미 | 권장 액션 |
|---|---|---|
| 80%+ | 충분히 파싱됨 | 다음 단계(`ms-solution-recommend`) 진행 |
| 50~79% | 일부 불명확 | `clarification_needed` 항목 질문 후 재파싱 |
| 50% 미만 | 파싱 불충분 | 전체 `clarification_needed` 질문 필수 |

### 설계 결정 사항
- **규칙 기반 1차 파싱**: LLM 없이 순수 Python 규칙으로 동작 → Phase 2에서 LLM 보정 추가 예정
- **순수 함수 설계**: `parse_requirement()`는 동일 입력에 동일 결과 보장 (테스트 용이)
- **재파싱 지원**: `raw_input`에 추가 답변을 이어붙인 후 재파싱하는 패턴으로 보완

### 사용 예시

```python
from src.modules.requirement_parser import parse_requirement

req = parse_requirement("""
매주 월요일마다 구매팀에서 각 담당자에게 발주 현황을 엑셀로 취합하고
Teams로 알림을 보내는 작업을 자동화하고 싶습니다.
""")

req.display()
print(req.to_json())
```

```bash
# 대화형 실행
py -c "from src.modules.requirement_parser import interactive_parse; interactive_parse()"
```

---

## 5. ai-multi-discussion (기존 스킬)

### 목적
주어진 주제에 대해 Codex CLI, Gemini CLI, Claude 세 AI의 의견을 병렬 수집하고,
비교 분석 후 최적안을 도출한다. 사용자가 선택한 안을 To-do로 확정한다.

### 구현 파일
- `.claude/skills/ai-multi-discussion/SKILL.md` (Claude Code 스킬)

### 실행 절차
1. Codex CLI / Gemini CLI 버전 자동 감지
2. 세 AI 의견 병렬 수집 (각 타임아웃 120초)
3. 비교 테이블 출력
4. 베스트 조합안 도출
5. 사용자 선택 대기 (자동 진행 금지)
6. 선택된 안으로 최종 To-do 확정

### Fallback 정책
- Codex 미설치/실패 → Gemini + Claude 2자 비교로 진행
- Gemini 미설치/실패 → Codex + Claude 2자 비교로 진행
- 전체 외부 CLI 실패 → Claude 단독 의견으로 진행

---

## 6. skill-template (공통 기준 템플릿)

### 목적
Phase 2부터 신규 개발하는 모든 스킬이 따르는 공통 표준 템플릿.

### 표준 헤더 구조

```yaml
---
name: [스킬명]
type: general | project-specific
version: 1.0
description: [트리거 조건 포함 설명]
required_environment:
  - Python 3.8+
depends_on: []
produces: []
---
```

### 표준 본문 섹션 순서
1. 사전 조건
2. 실행 절차 (STEP N)
3. 출력 형식
4. 실패 처리
5. 주의사항

### 공통 실패 처리 정책

| 실패 유형 | 처리 방법 |
|---|---|
| Python 모듈 import 실패 | 에러 메시지 + 설치 명령 안내 후 중단 |
| 파일 I/O 실패 (읽기) | 경로 재확인 요청 후 중단 |
| 파일 I/O 실패 (쓰기) | `logs/error_YYYYMMDD.jsonl` 기록 후 중단 |
| 외부 CLI 호출 실패 | Fallback 모드 전환 + 사용자 알림 |
| 신뢰도 50% 미만 (parse-requirement) | 전체 clarification 질문 후 재파싱 1회 |

---

## Phase 1 스킬 범용/전용 분류 결과

| 스킬 | 분류 | 이유 |
|---|---|---|
| `dev-log` | general | 순수 로깅 — 프로젝트 독립적 |
| `ai-analysis` | general | 모델명/가중치만 바꾸면 범용 |
| `readme-update` | general | README 갱신 메커니즘은 어느 프로젝트에나 적용 가능 |
| `ai-multi-discussion` | general | 의사결정 논의 프레임워크 — AI 도구 설정만 외부화 |
| `parse-requirement` | project-specific | MS 제품 힌트, 도메인 분류가 MS 자동화 컨설팅에 특화 |

---

---

## Phase 2 재설계에 따른 수정 완료 사항

### parse-requirement 수정 완료 (v3.0)

**추가 기능: session_id 생성 + 상태 파일 초기화**

```python
# parse-requirement 실행 시 자동 처리
session_id = generate_session_id()  # consult_YYYYMMDD_NNN 형식

# 상태 파일 초기화
session_state = {
    "session_id": session_id,
    "mode": None,
    "current_revision": 0,
    "solution_id_current": None,
    "light_revision_count": 0,
    "total_revision_count": 0,
    "ms_verify_retry_count": 0,
    "created_at": now(),
    "updated_at": now()
}
save_to_file(f"logs/session_{date}_{seq}.json", session_state)
```

**상태 파일 위치:** `logs/session_YYYYMMDD_NNN.json`

---

### ai-analysis 수정 완료 (v2.0)

**신규 이벤트 타입 추가:**

| 이벤트 타입 | 설명 | 기록 시점 |
|---|---|---|
| `SESSION_STATE` | 세션 카운터 상태 스냅샷 | 재컨설팅 발생 시마다 |
| `REVISION` | 재컨설팅 이력 | 경량/전체 재컨설팅 시 |
| `MODE_SWITCH` | Quick→Deep 전환 | 모드 전환 시 |
| `MS_VERIFY` | MS 지원 확인 결과 | 권고안 선택 후 검증 시 |

**REVISION 이벤트 스키마:**
```json
{
  "event_type": "REVISION",
  "session_id": "consult_20260309_001",
  "revision": 1,
  "type": "A",
  "prev_solution_id": "PowerAutomate+Outlook",
  "new_solution_id": "PowerAutomate+SharePointList+Outlook",
  "change_reason": "고객사 목록 관리 편의를 위해 SharePoint List 추가",
  "user_override": false,
  "timestamp": "..."
}
```

**MODE_SWITCH 이벤트 스키마:**
```json
{
  "event_type": "MODE_SWITCH",
  "session_id": "consult_20260309_001",
  "from": "quick",
  "to": "deep",
  "seed_revision": 2,
  "light_revision_count_reset": true,
  "timestamp": "..."
}
```

**MS_VERIFY 이벤트 스키마:**
```json
{
  "event_type": "MS_VERIFY",
  "session_id": "consult_20260309_001",
  "solution_id": "PowerAutomate+SharePointList+Outlook",
  "result": "confirmed | changed | deprecated",
  "action": "A | B | none",
  "timestamp": "..."
}
```

**로그 조회 시 session_id 필터 필수:**
```python
# generate-output에서 REVISION 이벤트 조회 시
revisions = [e for e in log_entries
             if e["session_id"] == current_session_id
             and e["event_type"] == "REVISION"]
# → 세션 간 재컨설팅 이력 혼입 방지
```

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-03-06 | Phase 1 착수 (dev-log, ai-analysis, readme-update) |
| 2026-03-06 | parse-requirement 개발 완료, ai-multi-discussion 통합 |
| 2026-03-06 | 스킬 설계 개선 — 범용/전용 분류, skill-template 생성, 전체 SKILL.md 표준화 |
| 2026-03-09 | Phase 2 재설계 반영 — parse-requirement(session_id 생성), ai-analysis(신규 이벤트 타입 4종) 수정 예정 사항 추가 |
| 2026-03-09 | parse-requirement v3.0 완료, ai-analysis v2.0 완료 — SKILL.md 재설계 적용 |
