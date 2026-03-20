# MS 업무자동화 솔루션 컨설팅 CLI 에이전트

Microsoft 생태계 내 업무 자동화 솔루션을 분석·제안하고, AI 3종 의견 비교 및 최종 산출물 파일을 생성하는 CLI 에이전트.

> **구현 원칙**: Python 없음. SKILL.md + Reference 파일만으로 동작.
> 로깅은 Write/Edit 툴로 JSONL 직접 기록, 분석은 Claude LLM이 인라인 처리.

---

## 실행 환경

| 항목 | 내용 |
|---|---|
| OS | Windows 10 / macOS |
| IDE | VSCode + Claude Code |
| AI CLI | Codex CLI, Gemini CLI |
| 로그 포맷 | JSONL (UTF-8) |

---

## 사용법

모든 기능은 Claude Code 스킬로 실행한다.

```bash
# 컨설팅 시작 (전체 흐름 자동 진행)
/consult

# 요구사항 파싱만 실행
/parse-requirement

# 개발 로그 기록
/dev-log

# AI 다자 토론
/ai-multi-discussion [논의 주제]

# 이력 정리 (4주 이상 로그 아카이브)
/archive

# Word 사용자 매뉴얼 생성
/gen-manual
```

---

## `/consult` 실행 흐름

```
[사용자 입력] → 요구사항 파싱 → 적합성 판정 → 모드 선택(Quick/Deep)
     → AI 분석·권고안 도출 → 사용자 피드백(재컨설팅 가능)
     → MS 지원 확인 → 산출물 생성(.txt / .xlsx / PA 플로우)
```

- **Quick**: Claude 단독 분석, 빠른 권고안
- **Deep**: AI 3종(Claude + Codex + Gemini) 독립 제안 → 상호 리뷰 → 공통 강점/리스크 추출
- 재컨설팅, 세션 관리, 출력 스키마 상세 → [`consult/SKILL.md`](.claude/skills/consult/SKILL.md)

---

## 스킬 목록

### 범용(General) — 다른 프로젝트에도 이식 가능

| 스킬 | 설명 |
|---|---|
| `dev-log` | 에러/수정 이유/변경 내역 JSONL 기록 |
| `ai-analysis` | AI 호출·채점·세션 상태 이벤트 기록 |
| `readme-update` | README 자동 갱신 |
| `ai-multi-discussion` | AI 3자 의견 수집·비교·최적안 도출 |
| `archive` | 4주 이상 로그 아카이브 + CSV 요약 |
| `test-log` | 스킬 테스트 관찰사항 기록/조회 |
| `phase-doc` | Phase 상세 개발 문서 작성·갱신 |
| `skill-template` | 스킬 공통 표준 템플릿 |
| `gen-manual` | Word 사용자 매뉴얼 자동 생성 |

### 전용(Project-specific) — 이 프로젝트에 특화

| 스킬 | 설명 |
|---|---|
| `consult` | 전체 흐름 오케스트레이터 (파싱→분석→피드백→산출물) |
| `parse-requirement` | 요구사항 구조화 + session_id 생성 |
| `ai-score-compare` | Quick/Deep 리스크 2패스 평가 → 권고안 도출 |
| `ms-solution-recommend` | Deep 모드 참고 데이터 제공 (solutions.md) |
| `generate-output` | 산출물 파일 생성 (.txt / .xlsx) |

---

## 프로젝트 구조

```
AI_Consulting/
├── README.md
├── UserRequirement_Draft.md
│
├── logs/                           # 자동 생성 (.gitignore 권장)
│   ├── ai_analysis/
│   ├── dev/
│   ├── session/                    # 세션별 컨설팅 상태 파일
│   └── test/
│
├── archive/                        # 이력 아카이브 (.gitignore 권장)
│   ├── Consulting_Summary.csv      # 컨설팅 요약 누적 (영구 보존)
│   └── raw/                        # Cold Storage (1주 후 최종 삭제)
│
├── references/
│   ├── blocklist.md                # deprecated / 사용 불가 MS 제품 목록
│   ├── solutions.md                # 검증된 MS 솔루션 데이터 (Deep 참고용)
│   ├── reconsult-guide.md          # 재컨설팅 A/B/C 타입 판정 기준
│   ├── schema.md                   # 이벤트 스키마
│   └── skill-map.md                # 스킬 연동 관계
│
├── Word_Template/                  # Excel 보고서 생성
│   ├── 컨설팅결과_보고서_템플릿.xlsx
│   └── fill_excel_template.py
│
├── Phase/                          # Phase별 상세 개발 문서
│   ├── Phase1_기반구축.md
│   ├── Phase2_핵심엔진.md
│   ├── Phase3_산출물생성.md
│   ├── Phase4_품질검증.md
│   └── Phase5_PA플로우설계.md
│
└── .claude/skills/                 # Claude Code 스킬 정의
```

---

## 개발 현황

| Phase | 내용 | 상태 | 상세 문서 |
|---|---|---|---|
| 1 | 기반 구축 (로깅, 파싱, 세션) | ✅ 완료 | [Phase1](./Phase/Phase1_기반구축.md) |
| 2 | 핵심 엔진 (Quick/Deep 평가) | ✅ 완료 | [Phase2](./Phase/Phase2_핵심엔진.md) |
| 3 | 산출물 생성 + 흐름 통합 | ✅ 완료 | [Phase3](./Phase/Phase3_산출물생성.md) |
| 4 | 다국어/적합성 게이트/Excel/토큰 최적화/ROI | ✅ 완료 | [Phase4](./Phase/Phase4_품질검증.md) |
| 5 | PA 플로우 설계 생성 | ✅ 완료 | [Phase5](./Phase/Phase5_PA플로우설계.md) |

미착수: `generate-test-list`, Notion 연동, 웹 UI(보류)
골든 테스트 케이스는 충분한 사용자 테스트 후 생성 예정

---

## 참고 문서

- [UserRequirement.md](./UserRequirement.md) — 전체 요구사항
- [`references/skill-map.md`](./references/skill-map.md) — 스킬 연동 관계·트리거·Reference 사용 관계
- [`references/reconsult-guide.md`](./references/reconsult-guide.md) — 재컨설팅 A/B/C 판정 기준
- [`.claude/skills/`](.claude/skills/) — 각 스킬 SKILL.md (내부 스키마·규칙·세션 관리 상세)
