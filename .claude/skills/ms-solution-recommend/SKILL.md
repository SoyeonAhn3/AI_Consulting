---
name: ms-solution-recommend
version: 3.1
description: Deep 모드에서 solutions.md의 검증된 라이선스/구현난이도 데이터를 AI 3종에게 참고 컨텍스트로 제공한다. 솔루션을 추천하거나 제한하지 않으며, AI가 자유 제안 후 참고할 수 있도록 데이터만 공급한다. Deep 모드 실행 시 ai-score-compare가 내부적으로 호출한다.
depends_on:
  - parse-requirement
produces:
  - solutions_context (Deep 모드 AI 프롬프트용 참고 데이터)
  - blocklist_context (차단 제품 목록)
---

# MS Solution Reference Skill

**Deep 모드 전용** — Quick 모드에서는 이 스킬을 호출하지 않는다.

ParsedRequirement를 받아 solutions.md의 검증된 데이터와 blocklist.md의 차단 목록을
AI 3종 프롬프트에 포함할 컨텍스트로 준비한다.
솔루션을 선별하거나 점수를 매기지 않으며, AI의 자유 제안을 제한하지 않는다.
blocklist_context를 ai-score-compare에서 수신하여 사용한다.

---

## 역할 변경 배경

| 구분 | 구버전 (v2.x) | 현버전 (v3.0) |
|---|---|---|
| 역할 | solutions.md 12개 중 허용 목록 기반 추천 | 검증 데이터 참고 제공 |
| Quick 모드 | solutions.md 직접 로드 후 후보 선별 | **미사용** |
| Deep 모드 | 매칭 점수 계산 후 상위 3개 선별 | 참고 컨텍스트만 제공 |
| solutions.md | 허용 목록 (이 중에서만 선택) | 검증 데이터 창고 (제약 아님) |

---

## 사전 조건

- parse-requirement 완료 → ParsedRequirement 확정
- Deep 모드 선택 완료

---

## STEP 1 — blocklist_context 수신

ai-score-compare에서 전달받은 `blocklist_context`를 사용한다.
(별도 Read("references/blocklist.md") 불필요 — 중복 로드 방지)

blocklist_context가 미전달된 경우에만 fallback:
```
Read("references/blocklist.md")
```

---

## STEP 2 — solutions.md 로드

```
Read("references/solutions.md")
```

로드 후 각 솔루션의 메타 필드 상태 확인:

```
verified_date 6개월 초과 → [⚠️ 정보 오래됨] 태그 추가
status = "beta"          → [BETA] 태그 추가
status = "deprecated"    → blocklist_context에 추가 (B001 처리)
```

오래됨 기준: 오늘 날짜 기준 verified_date가 6개월 이상 지난 경우.

---

## STEP 3 — 참고 컨텍스트 구성

AI 3종 프롬프트에 포함할 `solutions_context`를 구성한다.

### 프롬프트 순서 원칙
```
① 요구사항 분석 및 자유 제안 (solutions.md 참조 없이)
② 제안한 솔루션이 아래 검증 데이터에 있으면 해당 데이터 활용 가능
```

**순서가 반드시 지켜져야 한다.** 순서가 바뀌면 AI가 solutions.md 목록에 앵커링되어
자유 제안이 아닌 목록 내 선택이 되어버린다.

### solutions_context 형식

```
[MS 솔루션 검증 데이터 — 참고용]
※ 아래 데이터는 제안을 제한하지 않습니다.
  자유롭게 MS 생태계 솔루션을 제안하되,
  제안한 솔루션이 아래 목록에 있으면 검증된 데이터를 활용하세요.

솔루션: [ms_products 조합명]
  라이선스     : [license]
  구현 난이도  : [effort_level]
  검증일       : [verified_date] [태그]
  구현 개요 힌트: [구현 개요 요약]

솔루션: ...
```

### blocklist_context 형식

```
[차단 제품 목록 — 아래 제품이 포함된 솔루션은 제안 금지]
- [제품명] (B001: deprecated, 대체: [대체 제품])
- [제품명] (B002: 회사 정책 불가)
```

---

## STEP 4 — 컨텍스트 반환

`ai-score-compare`에 아래를 반환:

```
{
  "solutions_context": "[STEP 3 구성 내용]",
  "blocklist_context": "[STEP 3 차단 목록]",
  "stale_warnings": ["[정보 오래됨 솔루션 목록]"]
}
```

별도 출력 없음 — ai-score-compare가 프롬프트에 통합해서 사용한다.

---

## 실패 처리

| 실패 유형 | 처리 방법 |
|---|---|
| solutions.md 로드 실패 | 경고 표시 후 solutions_context 없이 진행 (AI 자유 제안만으로 처리) |
| blocklist_context 미수신 + blocklist.md 로드 실패 | 경고 표시 후 blocklist_context 없이 진행 + "차단 목록 확인 불가" 안내 |
| 모든 솔루션 deprecated | "solutions.md 업데이트 필요" 안내 후 빈 solutions_context 반환 |

---

## 주의사항

- **Quick 모드에서 절대 호출하지 말 것** — Quick은 Claude 단독 자유 분석
- solutions.md 데이터는 참고용이며 AI 제안을 제한하지 않음
- 프롬프트 순서: 요구사항/자유 제안 먼저 → solutions.md 참고 나중
- solutions.md에 없는 솔루션을 AI가 제안하면 [미검증] 태그 표시 후 MS 지원 확인 단계에서 보완
- verified_date 업데이트는 solutions.md 직접 수정 (6개월 주기 권장)

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-03-15 | v3.1 | 성능 최적화 — blocklist_context를 ai-score-compare에서 파라미터로 수신 (중복 Read() 제거) |
