<!--
  ⚠️ 미사용 파일 (UNUSED)
  이 파일은 어떤 스킬에서도 참조되지 않습니다.

  동일 파일 없음: 스킬 폴더 내 대응 파일이 존재하지 않습니다.
  이 파일은 개발 참고용 문서로만 존재합니다.
-->

# 스킬 맵 — 트리거 · 프로세스 · 연동 관계

---

## 1. 스킬 전체 목록

### 컨설팅 스킬

| 스킬 | 버전 | 역할 | 타입 |
|---|---|---|---|
| `consult` | v2.0 | 전체 흐름 오케스트레이터 | project-specific |
| `parse-requirement` | v5.0 | 요구사항 구조화 + session_id 생성 + 언어 감지 + ROI 소요시간 수집 | project-specific |
| `ai-score-compare` | v4.0 | 솔루션 자유 제안 + 리스크 2패스 평가 + 요약 출력 | project-specific |
| `ms-solution-recommend` | v3.1 | solutions.md 검증 데이터 + blocklist_context 참고 제공 (Deep 전용) | project-specific |
| `generate-output` | v2.0 | 최종 산출물 파일 생성 (ko/en/en+ko) + 구조 검증 + CSV 이력 | project-specific |

### 로깅 스킬

| 스킬 | 버전 | 역할 | 타입 |
|---|---|---|---|
| `ai-analysis` | v2.0 | 컨설팅 세션 이벤트 기록/조회 | general |
| `dev-log` | v1.1 | 개발 이력 기록/조회 | general |
| `test-log` | v1.0 | 테스트 관찰사항 기록/조회 | general |

### 개발 보조 스킬

| 스킬 | 버전 | 역할 | 타입 |
|---|---|---|---|
| `readme-update` | v1.0 | README.md 자동 갱신 | general |
| `phase-doc` | v1.0 | Phase 문서 기록/갱신 | general |
| `ai-multi-discussion` | v1.0 | AI 3종 의견 수집·비교·합의 | general |
| `skill-template` | v1.0 | 스킬 공통 표준 템플릿 | general |
| `archive` | v1.1 | 이력 보존 정책 (4주 보존 + CSV + Cold Storage) | general |
| `gen-manual` | v1.1 | Word 사용자 매뉴얼 자동 생성 (ko/en) | general |
| `github-push` | v1.0 | GitHub 커밋 + 푸시 자동화 | general |

---

## 2. 컨설팅 흐름 — 스킬 연동 다이어그램

```
사용자 요청
    │
    ▼
[consult] ─────────────────────────────────────────────────────
    │
    ├─ STEP 1 ────► [parse-requirement]
    │                    │ reads: parsing-guide.md
    │                    │ 입력 언어 자동 감지 (ko / en)
    │                    │ produces: ParsedRequirement + input_language
    │                    │           logs/session/session_YYYYMMDD_NNN.json
    │                    └─ calls ──► [dev-log] (INFO: 파싱 완료)
    │
    ├─ STEP 1-5 ──► 적합성 게이트 (Scope Gate)
    │                    ├─ 진행 가능    → 안내만 출력 후 자동으로 STEP 2 진행
    │                    ├─ 부분 지원   → 지원 범위 표시 + 사용자 확인 (예/아니오)
    │                    └─ 지원 대상 아님 → 안내 후 종료
    │                    세션 파일 갱신: scope_gate / scope_limited / scope_exclusions
    │
    ├─ STEP 2 ────► 모드 선택 (Quick | Deep)
    │
    ├─ STEP 3 ────► [ai-score-compare]
    │                    │
    │               Quick│  reads: blocklist.md
    │                    │  Claude 자유 분석 → blocklist 체크 → 2패스 리스크
    │                    │  출력: 요약 포맷 (상세보기 요청 시 전체 형식)
    │                    │
    │               Deep │  calls ──► [ms-solution-recommend]
    │                    │                 reads: solutions.md, blocklist.md
    │                    │                 returns: solutions_context, blocklist_context
    │                    │  Codex/Gemini/Claude 자유 제안 → Orchestrator 리뷰
    │                    │  → 공통 강점/리스크 → 2패스 리스크
    │                    │  출력: 요약 포맷 + AI 합의 필드 (상세보기 요청 시 전체 형식)
    │                    │
    │                    └─ calls ──► [ai-analysis]
    │                                     AI_CALL × N / FALLBACK / SCORE × 제안 수
    │
    ├─ STEP 3-5 ──► reads: reconsult-guide.md (재컨설팅 타입 판정 기준)
    │
    ├─ STEP 4 ────► 사용자 피드백 → 재컨설팅 분기
    │                    │
    │                    ├─ 타입 A ──► [ai-score-compare] 재실행
    │                    │             calls ──► [ai-analysis] REVISION + SESSION_STATE
    │                    │
    │                    ├─ 타입 B ──► 사용자 확인 후 [ai-score-compare] 재실행
    │                    │             calls ──► [ai-analysis] REVISION + SESSION_STATE
    │                    │
    │                    ├─ 타입 C ──► 설명 응답만 (스킬 호출 없음)
    │                    │
    │                    └─ 모드전환 ► [ai-score-compare] Deep으로 재실행
    │                                  calls ──► [ai-analysis] MODE_SWITCH + SESSION_STATE
    │
    ├─ STEP 5 ────► MS 지원 확인 (WebSearch)
    │                    │ STEP 5-1-5: WebSearch 원문 → Evidence Summary 압축
    │                    │   (기능지원/라이선스/deprecated/출처 4개 필드로 압축 후 평가)
    │                    └─ calls ──► [ai-analysis] MS_VERIFY + SESSION_STATE
    │
    ├─ STEP 6 ────► 사용자 최종 확인 + 산출물 옵션 선택
    │                    STEP 6-A: PowerAutomate 포함 여부 판단
    │                    STEP 6-1: output_mode (integrated|user|developer|split)
    │                    STEP 6-2: output_language (ko|en|en+ko)
    │                    STEP 6-3: generate_excel (true|false)
    │                    STEP 6-4: generate_pa_flow (true|false, PA 포함 시만)
    │
    ├─ STEP 7 ────► [generate-output]
    │                    STEP 5-5: 구조 검증 체크리스트 (솔루션명/ID/리스크/판정/구현개요)
    │                    reads: logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl (REVISION 조회)
    │                    produces: output/Archive/YYYYMMDD_[도메인]_[session_id]_자동화_컨설팅.txt
    │                    STEP 6-5: archive/Consulting_Summary.csv 이력 추가
    │
    ├─ STEP 7-E ──► Excel 보고서 생성 (generate_excel=true 시만)
    │                    reads: consult/references/excel-output-schema.md
    │                    produces: output/Archive/[파일명].xlsx
    │
    ├─ STEP 7-P ──► PA 플로우 설계 생성 (generate_pa_flow=true 시만)
    │                    produces: output/PA_Flow/[날짜]_[session_id]_PA_Flow.txt
    │                              logs/PA_log/[날짜]_[session_id]_PA_Flow.json
    │
    └─ STEP 8 ────► 완료 보고
```

---

## 3. 스킬별 상세 — 트리거 · 입력 · 출력

### consult (v2.0)

| 항목 | 내용 |
|---|---|
| **트리거** | "컨설팅 시작해줘", "자동화 방법 알려줘", "업무 자동화 컨설팅", "자동화하고 싶어" 등 14개 패턴 |
| **입력** | 사용자 자유 형식 요구사항 |
| **호출 스킬** | parse-requirement → ai-score-compare → ai-analysis → generate-output |
| **reads** | `.claude/skills/consult/references/reconsult-guide.md` (피드백 시에만 지연 로드) |
| **출력** | 최종 산출물 파일 경로 + 완료 보고 |
| **세션 파일** | context_snapshot 포함 (requirement_summary, selected_proposal, last_step, last_feedback) |
| **주요 변경** | v1.2: 적합성 게이트, v1.3: Evidence Summary 압축, v1.6: 컨텍스트 압축, v2.0: reconsult-guide 지연 로드 + context_snapshot |

---

### parse-requirement (v5.0)

| 항목 | 내용 |
|---|---|
| **트리거** | consult STEP 1에서 호출 / "요구사항 분석해줘" 직접 호출 |
| **입력** | 사용자 자유 형식 요구사항 텍스트 |
| **호출 스킬** | dev-log (INFO 기록) |
| **reads** | parsing-guide.md 인라인 통합 (v5.0에서 Read 제거) |
| **출력** | ParsedRequirement 구조체 + `logs/session/session_YYYYMMDD_NNN.json` |
| **주요 변경** | v4.0: 언어 자동 감지, v5.0: Q4 소요 시간 수집 (ROI 예측용) + parsing-guide 인라인 통합 |

---

### ai-score-compare (v4.0)

| 항목 | 내용 |
|---|---|
| **트리거** | consult STEP 3에서 모드 선택 후 자동 실행 / 재컨설팅 시 재실행 |
| **입력** | ParsedRequirement + mode (quick/deep) + scope_limited 컨텍스트 + blocklist_context |
| **호출 스킬** | ms-solution-recommend (Deep 모드만) / ai-analysis |
| **reads** | risk-evaluation-guide, blocklist, deep-mode-guide 모두 인라인 통합 (v4.0) |
| **출력** | SolutionProposal 목록 + roi_calc (기본: 요약 포맷) |
| **주요 변경** | v3.2: 출력 요약화, v3.3: 채점표 출력 금지, v4.0: Reference 4종 인라인 통합 + Codex/Gemini 병렬 실행 |

**Quick 내부 흐름:**
```
Claude 자유 분석 (최대 3개)
→ blocklist.md 차단 체크
→ 1패스: 리스크별 탈락가능성 판정
→ 2패스: 권장/검토필요/비추천 확정
→ 요약 출력 + ai-analysis 기록
```

**Deep 내부 흐름:**
```
AI 상태 확인 (3/2/1개 분기)
→ ms-solution-recommend 호출 → solutions_context + blocklist_context 수신
→ Codex/Gemini/Claude 순차 자유 제안
→ blocklist.md 차단 체크
→ Orchestrator 상호 리뷰 → 공통 강점/리스크 추출
→ 1패스 → 2패스 리스크 평가
→ 요약 출력 (AI 합의 필드 포함) + ai-analysis 기록
```

---

### ms-solution-recommend (v3.1)

| 항목 | 내용 |
|---|---|
| **트리거** | ai-score-compare Deep 모드에서 내부 호출 (Quick에서는 절대 호출 안 함) |
| **입력** | ParsedRequirement + blocklist_context (v3.1: 파라미터 수신) |
| **호출 스킬** | 없음 |
| **reads** | `.claude/skills/ms-solution-recommend/references/solutions.md` |
| **출력** | solutions_context + blocklist_context → ai-score-compare에 반환 |
| **역할** | solutions.md의 검증 데이터를 참고용으로만 제공. 솔루션 선택 제한 없음 |

---

### generate-output (v2.0)

| 항목 | 내용 |
|---|---|
| **트리거** | consult STEP 7에서 사용자 최종 확인 후 호출 |
| **입력** | session_id, mode, SolutionProposal 목록, output_mode, output_language, generate_excel |
| **호출 스킬** | 없음 |
| **reads** | `logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl` (REVISION 이벤트, session_id 필터) |
| **출력** | `output/Archive/YYYYMMDD_[도메인]_[session_id]_자동화_컨설팅.txt` + CSV 이력 |
| **구조 검증** | STEP 5-5: 파일 쓰기 전 5개 항목 체크 (솔루션명/ID/리스크 존재/판정/구현개요 3단계 이상). FAIL 시 자동 보완 |
| **주요 변경** | v1.4: en+ko, v1.7: ROI 블록, v1.8: Method D/E/F 최적화, v1.9: 헤더 요구사항 요약, v2.0: label-map 인라인 + 구조 검증 |

**출력 모드:**
```
integrated  — 사용자 요약 + 개발자 상세 (기본)
user        — 비기술 요약만 (_user suffix)
developer   — 기술 상세만 (_developer suffix)
split       — user + developer 2개 파일 생성
```

**부록 생성 조건:**
```
부록 A: total_revision_count > 0일 때만
부록 B: mode == "deep"일 때만
```

**STEP 6-5 CSV 이력:** 파일 쓰기 완료 후 `archive/Consulting_Summary.csv`에 자동 추가

---

### ai-analysis (v2.0)

| 항목 | 내용 |
|---|---|
| **트리거** | ai-score-compare / consult에서 이벤트 발생 시 / "세션 로그 보여줘" 직접 호출 |
| **입력** | 이벤트 타입 + 이벤트 데이터 |
| **호출 스킬** | 없음 |
| **reads** | `.claude/skills/ai-analysis/references/schema.md` |
| **출력** | `logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl` (JSONL 한 줄 추가) |

**기록 이벤트 타입:**
```
AI_CALL       — AI 모델 호출 (성공/실패)
FALLBACK      — 호출 실패로 모델 전환
SCORE         — 리스크 평가 완료 (제안별 1건)
SESSION_STATE — 카운터 상태 저장 (변경 시마다)
REVISION      — 재컨설팅 발생 (A/B 타입)
MODE_SWITCH   — Quick→Deep 전환
MS_VERIFY     — MS 지원 확인 완료
```

---

### dev-log (v1.1)

| 항목 | 내용 |
|---|---|
| **트리거** | parse-requirement STEP 7에서 호출 / "로그 남겨줘" 직접 호출 |
| **입력** | 이벤트 타입 (ERROR/CHANGE/INFO) + 내용 |
| **호출 스킬** | 없음 |
| **reads** | `.claude/skills/dev-log/references/schema.md` |
| **출력** | `logs/dev/dev_YYYYMMDD.jsonl` |

---

### archive (v1.0)

| 항목 | 내용 |
|---|---|
| **트리거** | "이력 정리해줘", "아카이브 실행해줘", "오래된 로그 정리해줘" |
| **입력** | 없음 (자동으로 logs/ 폴더 스캔) |
| **호출 스킬** | 없음 |
| **reads** | `logs/session/`, `logs/ai_analysis/`, `logs/dev/`, `output/` |
| **출력** | `archive/YYYYMM_summary.csv` + `archive/raw/` (cold storage) |
| **보존 정책** | JSONL/세션 파일 4주 보존 → archive/raw/ 이동 → 1주 후 최종 삭제 |
| **영구 보존** | `output/*.txt` — 절대 삭제·이동 금지 |

---

## 4. Reference 파일 ↔ 스킬 사용 관계

> 실제 사용 경로는 각 스킬의 `references/` 서브폴더. `references/` 루트 파일은 개발 참고용.

| Reference 파일 (실제 경로) | 사용 스킬 | 용도 |
|---|---|---|
| `parse-requirement/references/parsing-guide.md` | parse-requirement | 도메인 분류 기준, 신뢰도 공식 |
| `ms-solution-recommend/references/solutions.md` | ms-solution-recommend | 검증된 MS 솔루션 데이터 (참고용) |
| `ms-solution-recommend/references/blocklist.md` | ms-solution-recommend | 사용 불가 MS 제품 목록 |
| `ai-score-compare/references/blocklist.md` | ai-score-compare | 사용 불가 MS 제품 목록 (Quick 모드) |
| `ai-score-compare/references/risk-evaluation-guide.md` | ai-score-compare | 리스크 카테고리, 탈락 가능성 판단 기준 |
| `ai-analysis/references/schema.md` | ai-analysis | 이벤트 스키마 정의 |
| `dev-log/references/schema.md` | dev-log | 이벤트 스키마 정의 |
| `consult/references/reconsult-guide.md` | consult | A/B/C 재컨설팅 타입 판정 기준 |

---

## 5. 로그/아카이브 파일 ↔ 스킬 사용 관계

| 파일/폴더 | 쓰기 | 읽기 |
|---|---|---|
| `logs/session/session_YYYYMMDD_NNN.json` | parse-requirement (초기화), consult (갱신) | consult (세션 복원) |
| `logs/ai_analysis/ai_analysis_YYYYMMDD.jsonl` | ai-analysis | generate-output (REVISION 조회) |
| `logs/dev/dev_YYYYMMDD.jsonl` | dev-log | dev-log (조회 시) |
| `logs/test/test_YYYYMMDD.jsonl` | test-log | test-log (조회 시) |
| `archive/Consulting_Summary.csv` | generate-output (STEP 6-5) | 사용자 직접 열람, archive (참조) |
| `output/Archive/*.xlsx` | consult STEP 7-E (fill_excel_template.py) | 사용자 직접 열람 |
| `output/PA_Flow/*.txt` | consult STEP 7-P | 사용자 직접 열람 |
| `logs/PA_log/*.json` | consult STEP 7-P | 사용자 직접 열람 |
| `archive/raw/` | archive (이동) | archive (삭제 시) |
| `output/*.txt` | generate-output | archive (파일명 참조만, 내용 변경 없음) |

---

## 6. 재컨설팅 분기별 스킬 호출 패턴

| 재컨설팅 타입 | 스킬 호출 | 카운터 변화 |
|---|---|---|
| **타입 A** (경량) | ai-score-compare 재실행 → ai-analysis (REVISION+SESSION_STATE) | light+1, total+1 |
| **타입 B** (전체) | ai-score-compare 전체 재실행 → ai-analysis (REVISION+SESSION_STATE) | light 리셋, total+1 |
| **타입 B + Override** | ai-score-compare 재실행 → ai-analysis (REVISION user_override=true) | light+1, total+1 |
| **타입 C** (설명) | 스킬 호출 없음 | 변화 없음 |
| **모드 전환** | ai-score-compare Deep 재실행 → ai-analysis (MODE_SWITCH+SESSION_STATE) | light 리셋, total+1 |

---

## 7. 개발 보조 스킬 (컨설팅 흐름 외)

| 스킬 | 트리거 | 역할 |
|---|---|---|
| `readme-update` | "readme 업데이트해줘" | README.md 자동 갱신 |
| `phase-doc` | "Phase 문서 업데이트해줘" | Phase/*.md 기록/갱신 |
| `ai-multi-discussion` | "A에 대해 다른 AI와 논의해 협의해 와" | Codex/Gemini/Claude 3 AI 의견 수집·합의 |
| `skill-template` | 새 스킬 작성 시 참고 | 스킬 공통 표준 템플릿 |
| `archive` | "이력 정리해줘" | 4주 이상 로그 CSV 요약 + Cold Storage 정리 |
| `test-log` | "테스트 관찰 기록해줘" | 테스트 관찰사항 JSONL 기록/조회 |

이 스킬들은 컨설팅 흐름과 독립적으로 동작하며 서로를 호출하지 않는다.

---

## 변경 이력

| 날짜 | 내용 |
|---|---|
| 2026-03-09 | 최초 생성 — 전체 스킬 맵 문서화 |
| 2026-03-10 | 전면 업데이트 — 적합성 게이트(STEP 1-5), Evidence Summary 압축(STEP 5-1-5), 출력 요약화(v3.2), output_language(ko/en/en+ko), archive 스킬, test-log, 로그 경로 서브폴더 확정, Reference 실제 경로 반영 |
| 2026-03-20 | 버전 현행화 — consult v2.0(context_snapshot, 지연 로드), generate-output v2.0(STEP 5-5 구조 검증, CSV 이력), ai-score-compare v4.0(인라인 통합, 병렬 실행), parse-requirement v5.0(ROI 소요시간), ms-solution-recommend v3.1(blocklist_context 파라미터). STEP 6 세분화(6-A~6-4), STEP 7-E/7-P 추가, gen-manual/github-push 스킬 추가, 로그 파일 관계 보완 |
