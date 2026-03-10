# MS 솔루션 지식 베이스

> 이 파일은 Deep 모드에서 AI에게 참고 데이터로 제공된다. 솔루션 선택을 제한하지 않음.

## must_have_conditions 규칙
하나도 충족하지 못하면 자동 탈락. 탈락 코드: M001(기능미충족) M002(라이선스) M003(deprecated) M004(기술제약)

---

## 솔루션 1: Power Automate + Teams 알림 자동화
```
status: active | verified: 2025-08 | effort: 낮음
license: Microsoft 365 Business Basic 이상
ms_products: ["Power Automate", "Teams"]
domains: ["구매/조달", "인사/HR", "문서/행정", "프로젝트 관리", "고객지원", "영업/CRM"]
keywords: ["알림", "발송", "승인", "취합", "집계", "자동", "정기", "매주", "매일"]
compatible_tools: ["Excel", "Outlook", "Teams"]
must_have(M001): Teams 채널/개인 메시지 발송 또는 MS365 내부 알림·승인 흐름이 자동화 대상
```

---

## 솔루션 2: Power Automate + SharePoint 문서 관리
```
status: active | verified: 2025-08 | effort: 중간
license: Microsoft 365 Business Standard 이상
ms_products: ["Power Automate", "SharePoint"]
domains: ["문서/행정", "구매/조달", "인사/HR", "프로젝트 관리"]
keywords: ["문서", "결재", "보고서", "양식", "저장", "업로드", "공유", "버전"]
compatible_tools: ["Excel", "Word", "SharePoint"]
must_have(M001): 문서 생성·저장·공유·버전관리가 자동화 대상
```

---

## 솔루션 3: Power Apps + SharePoint 맞춤 업무 앱
```
status: active | verified: 2025-08 | effort: 중간
license: Microsoft 365 Business Standard 이상
ms_products: ["Power Apps", "SharePoint"]
domains: ["문서/행정", "인사/HR", "구매/조달", "고객지원", "영업/CRM"]
keywords: ["앱", "입력", "등록", "양식", "폼", "조회", "모바일", "현장"]
compatible_tools: ["Excel", "SharePoint"]
must_have(M001): 사용자가 직접 데이터를 입력/조회하는 UI 앱 또는 현장/모바일 데이터 수집 앱 필요
```

---

## 솔루션 4: Power BI + Excel 데이터 대시보드
```
status: active | verified: 2025-08 | effort: 중간
license: Power BI Pro 또는 Microsoft 365 E3 이상
ms_products: ["Power BI", "Excel"]
domains: ["데이터/분석", "재무/회계", "영업/CRM", "마케팅", "구매/조달"]
keywords: ["대시보드", "분석", "리포트", "집계", "통계", "시각화", "kpi", "현황"]
compatible_tools: ["Excel", "SharePoint", "Teams"]
must_have(M001): 데이터 시각화·대시보드·보고서 생성이 주요 목적
```

---

## 솔루션 5: Power Automate + Outlook 이메일 자동화
```
status: active | verified: 2025-08 | effort: 낮음
license: Microsoft 365 Business Basic 이상
ms_products: ["Power Automate", "Outlook"]
domains: ["영업/CRM", "고객지원", "마케팅", "인사/HR", "문서/행정"]
keywords: ["이메일", "메일", "발송", "알림", "답변", "수신", "전달", "첨부", "자동"]
compatible_tools: ["Outlook", "Excel", "Teams"]
must_have(M001): 이메일 자동 발송·수신·분류·응답이 자동화 대상
```

---

## 솔루션 6: SharePoint + Power Automate 문서 승인 워크플로
```
status: active | verified: 2025-08 | effort: 중간
license: Microsoft 365 Business Standard 이상
ms_products: ["SharePoint", "Power Automate", "Teams"]
domains: ["문서/행정", "구매/조달", "인사/HR", "재무/회계"]
keywords: ["승인", "결재", "검토", "기안", "공문", "계약", "서명", "반려"]
compatible_tools: ["Word", "Excel", "SharePoint", "Teams"]
must_have(M001): 다단계 승인·결재·검토 프로세스가 자동화 대상
```

---

## 솔루션 7: Azure Logic Apps 엔터프라이즈 자동화
```
status: active | verified: 2025-08 | effort: 높음
license: Azure 구독(종량제), Microsoft 365 Business Standard 이상
ms_products: ["Azure Logic Apps", "Teams", "SharePoint"]
domains: ["IT/시스템", "재무/회계", "데이터/분석", "영업/CRM"]
keywords: ["api", "연동", "시스템", "통합", "자동화", "스케줄", "복잡", "대량"]
compatible_tools: ["SAP", "ERP", "CRM", "Salesforce", "Oracle"]
must_have(M001/M004): external_systems(SAP/ERP/CRM/Oracle) API 연동 필요 또는 Power Automate 처리 불가 복잡한 엔터프라이즈 자동화
참고: external_systems 있으면 이 솔루션 우선 고려
```

---

## 솔루션 8: Power Apps + Power Automate 모바일 업무 앱
```
status: active | verified: 2025-08 | effort: 중간
license: Microsoft 365 Business Standard 이상
ms_products: ["Power Apps", "Power Automate", "Teams"]
domains: ["인사/HR", "구매/조달", "고객지원", "프로젝트 관리"]
keywords: ["모바일", "현장", "점검", "체크", "입력", "등록", "사진", "위치", "바코드"]
compatible_tools: ["Excel", "SharePoint", "Teams"]
must_have(M001): 현장·모바일 환경에서의 데이터 수집·입력이 자동화 대상
```

---

## 솔루션 9: Excel + Office Scripts + Power Automate 이메일 자동화
```
status: active | verified: 2025-08 | effort: 중간
license: Microsoft 365 Business Standard 이상 (Office Scripts 포함)
ms_products: ["Excel", "Power Automate", "Outlook"]
domains: ["영업/CRM", "마케팅", "재무/회계", "구매/조달", "문서/행정"]
keywords: ["이메일", "메일", "발송", "개인화", "취합", "엑셀", "excel", "데이터", "자동"]
compatible_tools: ["Excel", "Outlook", "SharePoint"]
must_have(M001): Excel 데이터 기반 개인화 이메일 발송 또는 Excel 데이터 변환·집계 후 이메일 자동 발송 필요
```

---

## 솔루션 10: SharePoint List + Power Automate + Outlook 개인화 이메일
```
status: active | verified: 2025-08 | effort: 낮음
license: Microsoft 365 Business Basic 이상
ms_products: ["SharePoint", "Power Automate", "Outlook"]
domains: ["영업/CRM", "마케팅", "고객지원", "인사/HR"]
keywords: ["이메일", "메일", "발송", "개인화", "고객", "수신자", "목록", "리스트", "자동"]
compatible_tools: ["SharePoint", "Excel", "Outlook", "Teams"]
must_have(M001): 수신자 목록 기반 개인화 이메일 자동 발송 + 수신자 정보를 SharePoint/Excel로 관리
```

---

## 솔루션 11: Microsoft Copilot Studio + Teams 챗봇 자동화
```
status: beta | verified: 2025-08 | effort: 중간
license: Microsoft 365 Business Standard + Copilot Studio 라이선스
ms_products: ["Copilot Studio", "Teams", "Power Automate"]
domains: ["고객지원", "인사/HR", "IT/시스템", "문서/행정"]
keywords: ["챗봇", "bot", "자동응답", "faq", "문의", "질문", "대화", "ai", "코파일럿"]
compatible_tools: ["SharePoint", "Teams", "Excel"]
must_have(M001): 대화형 인터페이스(챗봇) 자동화 또는 FAQ 자동 응답·티켓 생성·안내 자동화가 목적
```

---

## 솔루션 12: Microsoft Fabric + Power BI 대용량 데이터 분석
```
status: active | verified: 2025-08 | effort: 높음
license: Microsoft Fabric 구독 (F SKU 또는 Power BI Premium)
ms_products: ["Microsoft Fabric", "Power BI", "Azure"]
domains: ["데이터/분석", "재무/회계", "영업/CRM", "IT/시스템"]
keywords: ["대용량", "실시간", "데이터레이크", "etl", "파이프라인", "분석", "대시보드", "통합"]
compatible_tools: ["Excel", "Azure", "SAP", "SQL", "Teams"]
must_have(M001/M002): 대용량 데이터(수십만 건 이상)/실시간 파이프라인 또는 복수 외부 시스템 통합 분석 필요
```
