# MS 제품 카탈로그
# STEP 0에서 로드 — 솔루션 제안 전 전체 제품군 인식용
# 솔루션 제안 시 이 목록에서 요구사항에 맞는 제품을 자유롭게 조합할 것

---

## Microsoft 365 Business Standard 포함 제품

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

## Power Platform 추가 구독 필요

| 제품 | 라이선스 | 주요 자동화 용도 |
|---|---|---|
| Power BI | Pro 또는 Premium | 데이터 시각화, KPI 대시보드, 자동 리포트 |
| AI Builder | credits 필요 | OCR, 문서 인식·분류, 양식 데이터 자동 추출 |
| Copilot Studio | 별도 라이선스 | 챗봇·AI 에이전트, FAQ 자동 응답, 티켓 생성 |

---

## Azure (별도 구독 필요 — 구현 난이도 높음)

| 제품 | 주요 자동화 용도 |
|---|---|
| Azure Logic Apps | 엔터프라이즈 워크플로, ERP·SAP·레거시 API 연동 |
| Azure AI Services / OpenAI | LLM 기반 자동화, 문서 인텔리전스, OCR, 음성인식 |
| Azure Functions | 서버리스 코드 실행, 복잡한 데이터 처리 |
| Microsoft Fabric | 대용량 데이터 파이프라인, 데이터레이크 통합 분석 |

---

## 솔루션 제안 시 주의사항

- **solutions.md 미등재 제품** 제안 시 `[미검증]` 태그 필수
- **Azure 제품**: effort=높음, "Azure 구독 필요" 전제조건 명시
- **AI Builder**: "AI Builder credits 소진 시 추가 비용 발생" 리스크 명시
- **Copilot Studio**: "별도 라이선스 확인 필요" 전제조건 명시
- **단일 제품보다 조합**: 요구사항에 맞게 2~3개 제품을 조합한 솔루션 권장
