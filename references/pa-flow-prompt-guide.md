# PA 참조 데이터

## 트리거 유형 → PA 플로우 유형 매핑

| 트리거 유형 | PA 플로우 유형 | PA 공식 트리거 액션명 | 필수 설정값 |
|---|---|---|---|
| 이메일 수신 | Automated cloud flow | When a new email arrives (V3) | Folder / Subject Filter / Only with Attachments |
| SharePoint 항목 추가 | Automated cloud flow | When an item is created | Site Address / List Name |
| SharePoint 파일 추가 | Automated cloud flow | When a file is created (properties only) | Site Address / Library Name / Folder |
| Forms 응답 제출 | Automated cloud flow | When a new response is submitted | Form Id → 이후 Get response details 필수 |
| Teams 메시지 수신 | Automated cloud flow | When a new message is added to a channel | Team / Channel |
| HTTP 요청 수신 | Automated cloud flow | When an HTTP request is received | Method / Request Body JSON Schema |
| 일정 기반 | Scheduled cloud flow | Recurrence | Interval / Frequency / Start time / Time zone |
| 수동 실행 | Instant cloud flow | Manually trigger a flow | Input fields (Text / Number / Date 등) |

---

## 주요 커넥터 공식 명칭 및 라이선스

| 기능 | 공식 커넥터 명칭 | 등급 |
|---|---|---|
| 이메일 | Microsoft Outlook | Standard |
| 팀 협업·알림 | Microsoft Teams | Standard |
| 문서 라이브러리·목록 | SharePoint | Standard |
| 개인 파일 | OneDrive for Business | Standard |
| 설문·양식 | Microsoft Forms | Standard |
| 할 일·작업 관리 | Microsoft Planner | Standard |
| 엑셀 읽기·쓰기 | Excel Online (Business) | Standard |
| 일정 관리 | Microsoft Outlook (Calendar) | Standard |
| 승인 워크플로 | Approvals | Standard |
| HTTP 요청·웹훅 | HTTP | Premium |
| AI 문서 처리·OCR | AI Builder | Premium |
| ERP 연동 | SAP ERP | Premium |
| DB 직접 조회 | SQL Server | Premium |

---

## 액션별 공식 명칭 및 필수 설정값

| 액션 유형 | 커넥터 | 공식 액션명 | 필수 설정값 |
|---|---|---|---|
| 이메일 발송 | Microsoft Outlook | Send an email (V2) | To / Subject / Body |
| 이메일 첨부 목록 조회 | Microsoft Outlook | Get attachments (V2) | Message Id |
| 이메일 첨부 내용 조회 | Microsoft Outlook | Get attachment content (V2) | Message Id / Attachment Id |
| SP 항목 조회 | SharePoint | Get items | Site Address / List Name / Filter Query(선택) |
| SP 항목 생성 | SharePoint | Create item | Site Address / List Name / 각 컬럼값 |
| SP 항목 수정 | SharePoint | Update item | Site Address / List Name / Id / 수정 컬럼값 |
| SP 파일 생성 | SharePoint | Create file | Site Address / Folder Path / File Name / File Content |
| Teams 메시지 | Microsoft Teams | Post message in a chat or channel | Post as / Post in / Team / Channel / Message |
| Excel 행 조회 | Excel Online (Business) | List rows present in a table | Location / Document Library / File / Table |
| Forms 응답 상세 | Microsoft Forms | Get response details | Form Id / Response Id |
| 승인 요청 | Approvals | Start and wait for an approval | Approval type / Title / Assigned to |
| 조건 분기 | Control | Condition | 좌측값 / 연산자 / 우측값 |
| 반복 처리 | Control | Apply to each | Select An Output From Previous Steps |
| 배열 필터 | Data Operation | Filter array | From / 조건식 |
| 변수 초기화 | Variable | Initialize variable | Name / Type / Value |
| Scope (오류 그룹) | Control | Scope | — (내부에 액션 포함) |

---

## 복잡도 가이드

| 분기 수 | 액션 수 | 권장 처리 |
|---|---|---|
| 0~1 | ~5 | 단일 플로우로 구성 |
| 2~3 | 5~10 | Scope 액션으로 논리 그룹화 |
| 4+ | 10+ | Child Flow 분할 — 부모에서 "Run a Child Flow" 액션으로 호출 |

---

## 예외 처리 체크리스트 패턴

### 발송 실패
- [ ] 이메일 발송 실패 시 담당자 알림 — Scope로 Send email 감싸고 "Configure run after → has failed" 분기
- [ ] 플로우 실행 히스토리 주기 확인 — Power Automate → 내 플로우 → 28일 실행 기록

### 빈값 / 데이터 오류
- [ ] 빈값 행 필터링 — Get items 후 Filter array: `[필드] is not empty`
- [ ] 0건 처리 — Get items 직후 Condition: `length(body('Get_items')?['value']) greater than 0`, 0건이면 조기 종료

### 중복 실행 방지
- [ ] 상태 컬럼 조건 — Apply to each 내 Condition: `[상태 컬럼] is not equal to '[완료값]'`인 항목만 처리
- [ ] 테스트 시 실 발송 방지 — To 필드를 임시 테스트 계정으로 고정 후 검증

### 인증 / 연결 오류
- [ ] 커넥터 연결 만료 확인 — Power Automate → 연결 메뉴 → 연결 상태 점검
- [ ] Shared Mailbox 위임 권한 — Exchange 관리자에게 Send As / Send on Behalf 요청

### Apply to each 부분 실패
- [ ] 부분 실패 허용 여부 — Apply to each → Concurrency Control 설정 확인
- [ ] 실패 항목 로깅 — 실패 분기에서 SP 오류 목록 항목 추가 또는 Teams 알림
