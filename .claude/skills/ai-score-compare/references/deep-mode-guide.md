# Deep 모드 실행 가이드
# Deep 모드 진입(D-STEP 1) 확정 시 로드

---

## D-STEP 3 — 3 AI 순차 실행 (독립 제안서)

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

---

## D-STEP 5 — Claude Orchestrator: 상호 리뷰 구조화

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
