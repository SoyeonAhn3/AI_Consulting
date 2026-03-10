# Parsing Guide

parse-requirement 스킬이 요구사항 파싱 시 참조하는 분류 기준, 신뢰도 공식, 도메인별 파라미터 정의.

---

## 도메인 분류 목록

| 도메인 | 키워드 예시 |
|---|---|
| 이메일/발송 | 메일, 이메일, 발송, 수신, 알림, 뉴스레터, 공지 |
| 문서/결재 | 결재, 승인, 보고서, 기안, 계약서, 문서 관리 |
| 데이터/분석 | 데이터 취합, 집계, 리포트, 대시보드, 통계, 분석 |
| 일정/회의 | 회의, 일정, 캘린더, 예약, 미팅 |
| 구매/조달 | 발주, 구매, 조달, 견적, 납품 |
| 재무/회계 | 전표, 마감, 정산, 비용, 예산, 급여 |
| HR/인사 | 온보딩, 휴가, 근태, 채용, 인사 |
| 고객/영업 | 고객, CRM, 영업, 수주, 견적, 고객사 |
| 재고/물류 | 재고, 입출고, 배송, 물류, 창고 |
| IT/시스템 | 모니터링, 알람, 배포, 백업, 시스템 연동 |

복수 도메인 감지 시: 후보 목록 표시 후 사용자 선택 요청.

---

## 프로세스 유형 (process_type) 키워드 매핑

| 유형 | 키워드 |
|---|---|
| 정기실행 | 매일, 매주, 매월, 정기, 주기, 반복, 자동으로, 오전 N시, 월요일마다 |
| 이벤트기반 | ~하면, ~발생 시, ~등록되면, ~변경되면, ~제출되면, 트리거 |
| 수동트리거 | 요청 시, 클릭하면, 버튼, 수동, 필요할 때 |
| 복합 | 위 유형이 2개 이상 혼재 |

---

## 신뢰도 계산 공식

```
domain 확인됨                                     → +40점
automation_targets 1개 이상 추출                  → +30점
current_tools 1개 이상 추출                       → +15점
ms_products_hint 또는 external_systems 1개 이상  → +15점

합계 / 100 = confidence (0.0 ~ 1.0)
```

### 경고 조건

| 조건 | 경고 메시지 |
|---|---|
| confidence < 0.5 | "파싱 정확도가 낮습니다. 보완 후 재파싱을 권장합니다." |
| 복합 도메인 감지 | "복합 도메인 감지: [후보 목록] 중 1개를 선택해주세요." |
| automation_targets 불명확 | "자동화 대상이 불명확합니다. 구체적인 업무 프로세스를 추가해주세요." |
| external_systems 존재 | "[시스템명] 연동 필요. 기술 검토가 필요할 수 있습니다." |

---

## operational_params 도메인별 수집 기준

### 이메일/발송 도메인

| 파라미터 | 설명 | 값 예시 |
|---|---|---|
| send_volume | 발송 규모 | "소규모" (100건 이하) / "대규모" (100건 초과) |
| has_attachment | 첨부파일 여부 | true / false |
| needs_retry | 발송 실패 시 재시도 필요 여부 | true / false |
| needs_send_log | 발송 이력 저장 필요 여부 | true / false |

### 문서/결재 도메인

| 파라미터 | 설명 | 값 예시 |
|---|---|---|
| needs_version_control | 버전 관리 필요 여부 | true / false |
| needs_access_control | 접근 권한 관리 필요 여부 | true / false |

### 데이터/분석 도메인

| 파라미터 | 설명 | 값 예시 |
|---|---|---|
| data_refresh_cycle | 데이터 갱신 주기 | "실시간" / "일별" / "주별" / "월별" |
| data_volume | 데이터 규모 | "소규모" / "대규모" |

---

## 외부 시스템 분류 기준

current_tools에서 아래 항목은 external_systems로 별도 분류:
- SAP, ERP (Oracle ERP, Microsoft Dynamics 등)
- CRM (Salesforce, HubSpot 등)
- 그룹웨어 (더존, iCUBE, Workday 등)
- 레거시 시스템 / 사내 자체 개발 시스템
- 물류/SCM 시스템

external_systems 존재 시 ms_products_hint에 Azure Logic Apps 포함 고려.

---

## ms_products_hint 추론 기준

| 상황 | 추천 힌트 |
|---|---|
| external_systems 존재 | Azure Logic Apps |
| 정기 발송 | Power Automate |
| 문서 결재 | Power Automate + SharePoint |
| 데이터 집계/리포트 | Power BI + Power Automate |
| 이메일 발송 | Power Automate + Outlook |
| 대용량 데이터 | Azure Data Factory |

---

## 직접 입력 폼 (2회 수정 후에도 신뢰도 50% 미만 시)

직접 입력값 사용 시 confidence = 1.0 설정.
