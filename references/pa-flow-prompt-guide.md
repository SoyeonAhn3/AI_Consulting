# PA Copilot 프롬프트 가이드

## 트리거 유형별 프롬프트 패턴

| 트리거 | PA 공식 명칭 | 프롬프트 패턴 |
|---|---|---|
| 이메일 수신 | Microsoft Outlook | "When an email with [keyword] in the subject arrives in Outlook..." |
| 일정 기반 | Recurrence | "Every [N] days/hours at [time], ..." |
| SharePoint 항목 추가 | SharePoint | "When a new item is added to the [list name] list in SharePoint..." |
| SharePoint 파일 추가 | SharePoint | "When a new file is added to the [library] library in SharePoint..." |
| Forms 응답 제출 | Microsoft Forms | "When a new response is submitted to [form name]..." |
| 수동 트리거 | Manually trigger a flow | "When I manually trigger this flow with [input fields]..." |
| Teams 메시지 | Microsoft Teams | "When a message containing [keyword] is posted in [channel]..." |
| HTTP 요청 | When an HTTP request is received | "When an HTTP POST request is received, ..." |

## PA Copilot 프롬프트 작성 규칙

1. **트리거부터 시작**: "When [이벤트] / Create a flow that monitors [서비스]..."
2. **조건 명시**: "If [조건], then [액션A], otherwise [액션B]"
3. **공식 커넥터 명칭 사용**: 아래 커넥터 표 참조
4. **플레이스홀더 처리**: 경로·채널 등 환경 종속 값은 `[SharePoint 사이트 URL]` 형식으로 표기 → 사용자가 Copilot 결과에서 직접 수정
5. **복잡도 분할**: 액션 5개 초과 시 단락 분리 또는 Child Flow 명시

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

## 복잡도 가이드

| 분기 수 | 액션 수 | 권장 처리 |
|---|---|---|
| 0~1 | ~5 | 단일 프롬프트 |
| 2~3 | 5~10 | 프롬프트 2~3 단락으로 분리 |
| 4+ | 10+ | Child Flow 분할 권장 — Copilot 프롬프트에 "Use child flows for [단계명]" 명시 |

## 예외 처리 체크리스트 패턴

### 발송 실패
- [ ] 이메일 발송 실패 시 담당자 알림 추가 — Scope 액션으로 Send email을 감싸고 "Configure run after → has failed" 분기 추가
- [ ] 플로우 실행 히스토리 주기적 확인 — Power Automate → 내 플로우 → 28일 실행 기록 검토

### 빈값 / 데이터 오류
- [ ] 수신 이메일 필드 빈값 행 필터링 — Get items 후 Filter array 액션 추가: `수신 이메일 is not empty`
- [ ] 목록 항목 0건 처리 — Get items 직후 Condition 추가: `length(body('Get_items')?['value']) is greater than 0`, 0건이면 플로우 조기 종료

### 중복 실행 방지
- [ ] 발송 상태 컬럼 조건 추가 — Apply to each 내부 Condition: `발송 상태 is not equal to '발송 완료'` 인 항목만 발송
- [ ] 수동 테스트 시 실 발송 방지 — 테스트 전용 수신 이메일 행 추가 후 조건 분기, 또는 To 필드를 임시 테스트 계정으로 고정

### 인증 / 연결 오류
- [ ] SharePoint / Outlook 커넥터 연결 만료 확인 — Power Automate → 연결 메뉴에서 연결 상태 주기적 점검
- [ ] 공용 계정(Shared Mailbox) 사용 시 위임 권한 설정 확인 — Exchange 관리자에게 Send As 또는 Send on Behalf 권한 요청

### Apply to each 부분 실패
- [ ] 일부 항목 실패 시 나머지 계속 처리 여부 확인 — Apply to each 설정에서 "Concurrency Control" 및 오류 허용 옵션 확인
- [ ] 실패한 항목 별도 로깅 — 실패 분기에서 SharePoint 오류 목록에 항목 추가 또는 Teams/이메일로 실패 목록 전송

## 프롬프트 예시

### 이메일 첨부 파일 → SharePoint 저장 → Teams 알림
```
Create a flow that monitors Outlook for emails with '[키워드]' in the subject.
When such an email arrives:
1. Get all attachments from the email.
2. Save each attachment to a SharePoint document library at [사이트URL]/Shared Documents/[폴더명].
3. Post a message to the [채널명] channel in Microsoft Teams with the sender name, email subject, and number of files saved.
```

### Forms 응답 → SharePoint 목록 저장 → 승인 요청
```
When a new response is submitted to the Microsoft Forms form named '[양식명]':
1. Create a new item in the SharePoint list '[목록명]' with the form response fields.
2. Start an approval request in Approvals, send it to [승인자 이메일], with the title '[양식명] 승인 요청'.
3. If approved, update the SharePoint list item status to '승인'. If rejected, update to '반려' and send an email notification to the form respondent.
```

### 정기 실행 → Excel 데이터 읽기 → 이메일 발송
```
Every Monday at 9:00 AM:
1. Get all rows from the Excel Online file at [OneDrive 경로]/[파일명].xlsx, sheet '[시트명]'.
2. Filter rows where the '상태' column equals '미완료'.
3. Send an email from Outlook to [담당자 이메일] with the list of unfinished items in the email body.
```
