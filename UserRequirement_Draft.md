# MS 업무자동화 솔루션 컨설팅 CLI 에이전트 요구사항 문서

## 1. 문서 개요

### 1.1 프로젝트명
MS 업무자동화 솔루션 컨설팅 CLI 에이전트

### 1.2 문서 목적
본 문서는 사용자가 VSCode 환경에서 Claude Code를 통해 업무 자동화 관련 요구사항을 입력하면, AI가 이를 분석하여 Microsoft Software 중심의 자동화 방안을 제안하고, 여러 AI의 의견 비교 및 최종 산출물 파일 생성을 지원하는 프로젝트의 요구사항을 정의한다.

### 1.3 문서 이력
| 버전 | 날짜 | 변경 내용 |
|---|---|---|
| v1.0 | 2026-03-06 | 최초 작성 |
| v1.1 | 2026-03-06 | AI 3자 검토 반영: 근거 중심 권고안 구조 추가, MS Graph API + RAG 연동 추가 |
| v1.2 | 2026-03-06 | AI 3자 2차 검토 반영: 유저 테스트 skill, 토큰 최적화, 가중치 점수표(100% 수정), AI 수집 모드 분리, 지식 소스 분리 아키텍처, 이중 산출물 구조 추가 |
| v2.0 | 2026-03-20 | 구현 현행화: 실제 구현 상태 반영, 미구현/보류/설계 변경 항목 명시 |

### 1.4 구현 상태 범례
| 표시 | 의미 |
|---|---|
| ✅ 구현 완료 | 현재 동작 중 |
| ✅ 설계 변경 | 구현 완료이나 초기 설계와 다르게 변경됨 |
| 🔲 미착수 | 아직 개발 시작하지 않음 |
| ⏸ 보류 | 검토 후 필요 시 착수 예정 |

---

## 2. 프로젝트 목표

### 2.1 핵심 목표

- ✅ 사용자의 업무 자동화 요구사항을 구조적으로 분석한다.
- ✅ Microsoft Software 중심으로 적절한 자동화 방안을 제안한다.
- ✅ **설계 변경**: ~~GPT, Gemini, Claude의 의견을 비교하고 가중치 점수표 기반 단일 최종 권고안 + 대안 형식으로 제공한다.~~ → Codex CLI, Gemini CLI, Claude의 의견을 비교하고 **리스크 2패스 평가** 기반 권고안(권장/검토필요/비추천)을 제공한다.
- ✅ 사용자가 최종안을 선택하면 비개발자용 요약 + 개발자용 상세 섹션으로 구성된 산출물 파일을 생성한다.
- ⏸ 보류: ~~MS Graph API + Power Platform RAG로 최신성을 확보한다.~~ → 현재 WebSearch(MS Learn) + references/solutions.md로 대체 운영 중. RAG 도입은 보류.
- ✅ 개발 과정의 에러/수정/변경 이유를 별도 로깅 구조로 관리한다.

---

## 3. 범위 정의

### 3.1 포함 범위 (구현 상태)

| 항목 | 상태 | 비고 |
|---|---|---|
| CLI 기반 입력/출력 | ✅ 구현 완료 | Claude Code 스킬 기반 |
| 업무 자동화 요구사항 분석 | ✅ 구현 완료 | parse-requirement v5.0 |
| MS Software 중심 솔루션 제안 | ✅ 구현 완료 | ai-score-compare v4.0 |
| MS Graph API + Power Platform RAG | ⏸ 보류 | WebSearch + solutions.md로 대체 |
| AI별 의견 비교 및 비평 | ✅ 구현 완료 | Deep 모드: AI 3종 상호 리뷰 |
| 가중치 점수표 기반 권고안 | ✅ 설계 변경 | 리스크 2패스 평가로 변경 |
| 산출물 파일 생성 (이중 섹션) | ✅ 구현 완료 | .txt + .xlsx, output_mode 4종 |
| 개발용 에러/수정 로그 관리 | ✅ 구현 완료 | dev-log + ai-analysis |
| 유저 테스트 항목 자동 생성 | 🔲 미착수 | generate-test-list |
| AI 의견 수집 모드 분리 (Quick/Deep) | ✅ 구현 완료 | Fallback 로직 포함 |
| 적합성 게이트 | ✅ 구현 완료 | 초기 문서에 없었으나 추가 구현 |
| 다국어 지원 (ko/en/en+ko) | ✅ 구현 완료 | 초기 문서에 없었으나 추가 구현 |
| Excel 보고서 (.xlsx) | ✅ 구현 완료 | 초기 문서에 없었으나 추가 구현 |
| PA 플로우 설계 생성 | ✅ 구현 완료 | 초기 문서에 없었으나 추가 구현 |
| ROI 예측 | ✅ 구현 완료 | 초기 문서에 없었으나 추가 구현 |
| 이력 아카이브 | ✅ 구현 완료 | 초기 문서에 없었으나 추가 구현 |

### 3.2 제외 범위

- 웹 UI 개발 — ⏸ 보류 (CLI 검증 이후 검토)
- 복잡한 권한 관리 및 다중 사용자 협업 기능

---

## 4. 사용자 시나리오

### 4.1 기본 시나리오 (현재 구현 기준)

1. 사용자가 VSCode에서 Claude Code를 실행한다.
2. 사용자가 `/consult` 또는 자연어로 업무 자동화 요구사항을 입력한다.
3. 시스템은 요구사항을 파싱하여 도메인/자동화 대상/현재 도구/제약 조건으로 구조화한다. (parse-requirement)
4. 시스템은 적합성 게이트를 통해 MS 업무자동화 범위 적합성을 판정한다.
5. 사용자가 모드를 선택한다 (Quick / Deep).
6. 시스템은 리스크 2패스 평가로 권고안을 도출한다. (ai-score-compare)
7. 사용자가 피드백을 제공하면 재컨설팅(A/B/C)을 수행한다.
8. MS 지원 확인 후 산출물 옵션(형식/언어/Excel/PA 플로우)을 선택한다.
9. 시스템이 산출물 파일을 생성한다. (generate-output)

### 4.2 보완 시나리오

- 요구사항이 불명확한 경우 누락된 항목 또는 확인이 필요한 질문을 제시한다.
- 복수 대안을 권장/검토필요/비추천으로 분류하여 보여준다.
- ✅ **설계 변경**: ~~txt 또는 docx 파일 형식 선택~~ → txt 기본 + xlsx 선택적 생성
- AI 호출 일부 실패 시 Fallback 로직으로 자동 전환되며, 사용자에게 품질 저하 여부를 명시한다.

---

## 5. 기능 요구사항

### 5.1 요구사항 분석 — ✅ 구현 완료

- 사용자 입력을 파싱하여 업무 도메인, 자동화 대상 프로세스, 현재 사용 도구 등을 구조화한다.
- 입력이 불명확한 경우 추가 질문을 통해 요구사항을 보완한다.
- **추가 구현**: 입력 언어 자동 감지 (ko/en), 소요 시간 수집 (ROI 예측용)

---

### 5.2 MS 솔루션 추천 및 지식 소스 — ✅ 설계 변경

#### 5.2.1 솔루션 추천 — ✅ 구현 완료
- Microsoft 제품군(Power Automate, Teams, SharePoint, Power BI, Azure 등) 중심으로 솔루션을 제안한다.
- ✅ **설계 변경**: ~~MS 라이선스/정책 제약을 Requirement Analyzer에서 사전 필터링~~ → blocklist.md로 deprecated 제품 차단 + solutions.md로 검증된 데이터 참고 (Deep 모드)

#### 5.2.2 지식 소스 — ⏸ 보류

~~두 가지 지식 소스를 역할에 따라 분리하여 운영한다.~~

| 초기 설계 | 상태 | 현재 대체 |
|---|---|---|
| MS Graph API (조직 컨텍스트) | ⏸ 보류 | 사용자 입력으로 조직 환경 파악 |
| Power Platform RAG (제품 지식) | ⏸ 보류 | WebSearch(MS Learn) + solutions.md |
| KnowledgeRouter | ⏸ 보류 | 불필요 (RAG 미도입) |
| ContextMerger | ⏸ 보류 | 불필요 (RAG 미도입) |

> 현재 WebSearch + solutions.md 조합으로 충분히 동작 중. RAG 도입은 데이터 최신성 유지 비용 대비 효과를 검토 후 결정.

---

### 5.3 AI 의견 비교 및 권고안 도출 — ✅ 설계 변경

#### 5.3.1 AI 의견 수집 모드 — ✅ 구현 완료

| 모드 | 구성 | 상태 |
|---|---|---|
| **Quick** | Claude 단독 분석 + blocklist 체크 | ✅ 구현 완료 |
| **Deep** | Codex CLI + Gemini CLI + Claude 3종 독립 제안 + Orchestrator 상호 리뷰 | ✅ 구현 완료 |
| **Fallback** | 실패 AI 제외 후 자동 진행 (2개→경고+선택, 1개→Quick 자동 전환) | ✅ 구현 완료 |

**설계 변경 사항**:
- ~~asyncio 기반 비동기 오케스트레이터~~ → Claude Code 도구 호출 기반 실행
- ~~GPT~~ → Codex CLI로 변경
- Deep 모드에서 Codex/Gemini 병렬 실행 적용 (~30-60초 절감)

#### 5.3.2 권고안 도출 — ✅ 설계 변경

~~가중치 점수표 기반 정량 평가~~ → **리스크 2패스 평가**로 변경

| 패스 | 내용 |
|---|---|
| 1패스 | 리스크 평가 (보안/라이선스/운영 카테고리별 탈락 가능성 판단) |
| 2패스 | 1패스 결과 기반 최종 판정 (권장 / 검토필요 / 비추천) |

> 변경 이유: 가중치 점수표는 LLM이 일관된 점수를 매기기 어렵고, 리스크 중심 평가가 실무적으로 더 유용한 결과를 생성함.

**설계 변경 사항**:
- ~~Pydantic 모델 ScoringResult~~ → SKILL.md 규칙 기반 출력 스키마
- ~~가중합 계산~~ → 리스크 카테고리별 정성 평가 + 판정

---

### 5.4 산출물 파일 생성 — ✅ 구현 완료 (설계 변경 포함)

#### 출력 모드 (output_mode)

| 모드 | 내용 |
|---|---|
| integrated | 사용자 요약 + 개발자 상세 통합본 (기본) |
| user | 비기술 요약만 |
| developer | 기술 상세만 |
| split | 사용자용 + 개발자용 파일 2개 |

#### 지원 포맷

| 포맷 | 상태 | 비고 |
|---|---|---|
| .txt | ✅ 구현 완료 | 기본 산출물 |
| .xlsx | ✅ 구현 완료 | 선택적 생성 (KR/EN 2시트) |
| .docx | 🔲 미착수 | 초기 요구사항이었으나 .txt + .xlsx로 대체 |
| Notion | 🔲 미착수 | 추후 확장 |

#### 추가 구현 (초기 문서에 없던 항목)

- 다국어 출력: ko / en / en+ko (이중언어)
- 부록 A: 재컨설팅 이력 (있을 때만)
- 부록 B: Deep AI 비교 (Deep 모드만)
- ROI 예측 블록 (소요 시간 데이터 있을 때만)
- PA 플로우 설계 산출물 (PowerAutomate 포함 시 선택적)

**설계 변경 사항**:
- ~~어댑터 패턴 File Generator~~ → SKILL.md 규칙 + Claude Code Write 도구로 직접 생성
- ~~Pydantic 모델 기반 데이터 흐름~~ → JSON 스키마 규칙만 SKILL.md에 정의

---

### 5.5 개발 로그 관리 — ✅ 구현 완료 (설계 변경 포함)

- ✅ 에러, 수정 이유, 변경 이력을 구조화된 형식으로 기록한다.
- ✅ **설계 변경**: ~~structlog + JSONL~~ → Claude Code Write 도구로 JSONL 직접 기록
- ✅ AI 의견 수집 모드 전환 이력도 함께 기록한다. (ai-analysis: SESSION_STATE, MODE_SWITCH 등)

---

### 5.6 유저 테스트 리스트 자동 생성 — 🔲 미착수

generate-test-list 스킬로 계획되어 있으나 아직 개발 시작하지 않음.

초기 설계:
- UserRequirement.md 파싱 → Given-When-Then 형식 테스트 시나리오 생성
- `기능명 / 테스트 조건 / 기대 결과 / 우선순위` 체크리스트 출력

---

### 5.7 토큰 소모량 최적화 — ✅ 구현 완료 (설계 변경 포함)

초기 설계와 실제 적용된 전략 비교:

| 초기 설계 전략 | 상태 | 실제 적용 |
|---|---|---|
| 모드 분리 (Quick/Deep) | ✅ 구현 완료 | 그대로 적용 |
| 프롬프트 캐싱 | ⏸ 보류 | SKILL.md 인라인 통합으로 대체 |
| RAG 청크 요약 전달 | ⏸ 보류 | RAG 미도입으로 불필요 |
| 모델별 역할 분리 | ✅ 설계 변경 | Deep 모드에서 AI 3종 독립 제안 + Orchestrator 리뷰 |
| 중간 결과 캐싱 | ⏸ 보류 | 세션 상태 파일로 부분 대체 |
| max_tokens 제한 | ✅ 구현 완료 | 출력 형식 규칙으로 제어 |

**실제 적용된 최적화** (v1~v4):
- Reference 파일 SKILL.md 인라인 통합 (Read() 호출 7~10회 → 1~2회)
- 비선택 안 즉시 축약 (컨텍스트 압축)
- WebSearch 원문 드랍 → Evidence Summary만 유지
- reconsult-guide.md 지연 로드 (피드백 시에만)
- Deep 모드 Codex/Gemini 병렬 실행

---

## 6. 비기능 요구사항

| 항목 | 초기 요구사항 | 현재 상태 |
|---|---|---|
| 실행 환경 | VSCode + Codex CLI | ✅ VSCode + Claude Code (변경) |
| 응답 시간 (Quick) | 20~40초 | ✅ 달성 |
| 응답 시간 (Deep) | 60~120초 | ✅ 병렬 실행으로 ~90초 |
| 확장성 | 출력 어댑터 패턴 | ✅ 설계 변경: SKILL.md 규칙 기반 |
| 신뢰성 | Fallback 자동 전환 | ✅ 구현 완료 |
| 유지보수성 | Pydantic 모델 인터페이스 | ✅ 설계 변경: SKILL.md + Reference 파일 |
| 보안 | MS Graph OAuth 토큰 관리 | ⏸ 보류 (Graph API 미도입) |

---

## 7. 시스템 구조 — ✅ 설계 변경

### 7.1 구현 원칙
~~모듈형 오케스트레이션 구조~~ → **SKILL.md + Reference 파일만으로 동작하는 코드 없는 에이전트**.
Python 백엔드 없이 Claude Code의 도구 호출(Read/Write/Edit/Bash/WebSearch)만으로 전체 흐름을 구현.

### 7.2 모듈 구성 (초기 → 현재 매핑)

| 초기 모듈 | 현재 대응 | 상태 |
|---|---|---|
| Input Parser | parse-requirement 스킬 | ✅ 구현 완료 |
| Requirement Analyzer | parse-requirement + 적합성 게이트 | ✅ 구현 완료 |
| KnowledgeRouter | — | ⏸ 보류 |
| MS Graph Connector | — | ⏸ 보류 |
| Power Platform RAG | WebSearch + solutions.md | ✅ 설계 변경 |
| ContextMerger | — | ⏸ 보류 |
| AI Comparison Orchestrator | ai-score-compare 스킬 | ✅ 구현 완료 |
| Recommendation Engine | ai-score-compare (리스크 2패스) | ✅ 설계 변경 |
| Output Formatter | consult 스킬 (터미널 출력) | ✅ 구현 완료 |
| File Generator | generate-output 스킬 | ✅ 구현 완료 |
| Test Skill | generate-test-list | 🔲 미착수 |
| Dev Log Manager | dev-log + ai-analysis 스킬 | ✅ 구현 완료 |

### 7.3 현재 아키텍처 흐름

```
[사용자 입력] → /consult 또는 자연어 트리거
     │
     ▼
[parse-requirement]     요구사항 파싱 + session_id 생성 + 언어 감지
     │
     ▼
[적합성 게이트]         MS 업무자동화 범위 판정 (proceed/partial/rejected)
     │
     ├── Quick ──→ Claude 단독 + blocklist 체크 + 리스크 2패스 ──┐
     └── Deep ───→ AI 3종 독립 제안 + 상호 리뷰 + 리스크 2패스 ──┤
                                                                   │
     ┌─────────────────────────────────────────────────────────────┘
     ▼
[사용자 피드백]         재컨설팅 A/B/C 분기
     │
     ▼
[MS 지원 확인]          WebSearch → Evidence Summary
     │
     ▼
[generate-output]       .txt (+ .xlsx + PA 플로우)
```

---

## 8. 추후 확장 계획

| 기능 | 상태 | 설명 |
|---|---|---|
| generate-test-list | 🔲 미착수 | 유저 테스트 체크리스트 자동 생성 |
| Notion 연동 | 🔲 미착수 | 산출물을 Notion 페이지에 직접 생성 |
| 웹 UI | ⏸ 보류 | CLI 검증 이후 검토 |
| MS Graph API 연동 | ⏸ 보류 | 조직 컨텍스트 자동 조회 (OAuth 2.0) |
| Power Platform RAG | ⏸ 보류 | MS 공식 문서 벡터 검색 (최신성 유지 비용 검토 필요) |
| 다중 사용자 협업 | ⏸ 보류 | 팀 단위 권한 및 이력 관리 |
| 가중치 커스터마이징 | ⏸ 보류 | 리스크 2패스로 변경되어 재설계 필요 |
| 컨설팅 이력 기반 유사 케이스 추천 | 🔲 미착수 | CSV 누적 데이터 활용 |
| 산출물 diff 비교 | 🔲 미착수 | 재컨설팅 시 변경점 명시 |
| 컨설팅 만족도 수집 | 🔲 미착수 | STEP 8 후 1~5점 피드백 → 스킬 개선 루프 |

---

## 9. 용어 정의

| 용어 | 정의 |
|---|---|
| SKILL.md | Claude Code 스킬 정의 파일. 스킬의 동작 규칙, 입출력, 실행 흐름을 Markdown으로 정의 |
| Reference 파일 | SKILL.md가 참조하는 외부 데이터 파일 (blocklist.md, solutions.md 등) |
| Quick 모드 | Claude 단독 분석으로 빠른 권고안을 제공하는 실행 모드 |
| Deep 모드 | AI 3종(Codex CLI + Gemini CLI + Claude) 독립 제안 + 상호 리뷰로 상세 결과를 제공하는 모드 |
| Fallback | 일부 AI 호출 실패 시 성공한 모델만으로 자동 진행하는 복구 로직 |
| 리스크 2패스 평가 | 1패스(리스크 카테고리별 탈락 가능성) + 2패스(최종 판정: 권장/검토필요/비추천) |
| 적합성 게이트 | 요구사항이 MS 업무자동화 범위에 적합한지 판정하는 사전 검증 단계 |
| session_id | 컨설팅 세션 식별자. `consult_YYYYMMDD_NNN` 형식 |
| blocklist.md | deprecated 또는 사용 불가한 MS 제품 목록. 권고안에서 즉시 차단 |
| solutions.md | 검증된 MS 솔루션 라이선스·구현난이도 데이터. Deep 모드에서 참고용으로 제공 |
| Evidence Summary | MS Learn WebSearch 결과를 4필드(기능지원/라이선스/Deprecated/출처)로 압축한 요약 |
| context_snapshot | 세션 파일에 저장되는 대화 복원용 컨텍스트 스냅샷 |
| RAG | Retrieval-Augmented Generation. 외부 문서를 검색하여 LLM 응답의 정확성을 높이는 기법 |
| MS Graph API | Microsoft 365 서비스에 접근하는 통합 API |
| Power Platform | Power Automate, Power Apps, Power BI 등을 포함하는 MS 저코드 플랫폼 |
