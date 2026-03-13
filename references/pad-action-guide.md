# PAD 참조 데이터 (Power Automate Desktop 3.x)

> Cloud Flow 지원은 추후 필요 시 별도 가이드 파일로 추가 예정.

## 플로우 구조

| 구성 요소 | 설명 |
|---|---|
| Main 플로우 | 진입점. 서브플로우 호출 및 전체 흐름 제어 |
| 서브플로우 | 논리 단위 분리. Subflows 탭에서 추가. Main에서 "Run subflow"로 호출 |
| 스케줄링 | PAD 자체 스케줄 없음 → Windows 작업 스케줄러(Task Scheduler)로 PAD 플로우 실행 |

---

## 주요 액션 카테고리 및 공식 명칭

### 변수 (Variables)
| 액션명 | 용도 |
|---|---|
| Set variable | 변수 초기화 또는 값 할당 |
| Increase variable | 숫자형 변수 증가 |
| Decrease variable | 숫자형 변수 감소 |
| Create new list | 리스트 변수 생성 |
| Add item to list | 리스트에 항목 추가 |

### 조건 (Conditionals)
| 액션명 | 용도 |
|---|---|
| If / Else / End | 조건 분기 |
| Switch / Case / End | 다중 분기 |

### 반복 (Loops)
| 액션명 | 용도 |
|---|---|
| Loop | 횟수 기반 반복 |
| Loop condition | 조건 기반 반복 |
| For each | 리스트/데이터테이블 행 반복 |
| Exit loop | 반복 중단 |
| Next loop | 다음 반복으로 건너뜀 |

### 흐름 제어 (Flow control)
| 액션명 | 용도 |
|---|---|
| Run subflow | 서브플로우 호출 |
| Stop flow | 플로우 종료 |
| Wait | 대기 (초 단위) |
| Comment | 주석 추가 |

### UI 자동화 (UI Automation) — SAP GUI / MES 화면 조작
| 액션명 | 용도 |
|---|---|
| Click UI element in window | UI 요소 클릭 |
| Set text field in window | 입력 필드에 텍스트 입력 |
| Get detail of UI element in window | UI 요소 텍스트·속성 읽기 |
| Select menu option in window | 메뉴 항목 선택 |
| Get window | 특정 창 포커스 획득 |
| Focus window | 창 앞으로 가져오기 |
| Wait for UI element to appear | UI 요소 로딩 대기 |
| If UI element exists | UI 요소 존재 여부 조건 |
| Extract data from window | 창에서 데이터 추출 (테이블 등) |

### 시스템 (System)
| 액션명 | 용도 |
|---|---|
| Run application | 외부 프로그램 실행 (SAP GUI 실행 등) |
| Terminate process | 프로세스 강제 종료 |
| Get special folder | 시스템 폴더 경로 가져오기 |
| Get environment variable | 환경 변수 읽기 |

### 파일 (File)
| 액션명 | 용도 |
|---|---|
| Read text from file | 텍스트 파일 읽기 |
| Write text to file | 텍스트 파일 쓰기 |
| Copy file | 파일 복사 |
| Move file | 파일 이동 |
| Delete file | 파일 삭제 |
| If file exists | 파일 존재 조건 |
| Get files in folder | 폴더 내 파일 목록 조회 |

### Excel
| 액션명 | 용도 |
|---|---|
| Launch Excel | Excel 실행 또는 파일 열기 |
| Read from Excel worksheet | 셀·범위·전체 시트 읽기 |
| Write to Excel worksheet | 셀에 값 쓰기 |
| Get first free row on column from Excel worksheet | 마지막 행 번호 조회 |
| Close Excel | Excel 닫기 (저장 여부 선택) |

### 이메일 (Outlook / Exchange)
| 액션명 | 용도 |
|---|---|
| Launch Outlook | Outlook 실행 |
| Send email through Outlook | Outlook으로 이메일 발송 |
| Retrieve email messages from Outlook | Outlook에서 이메일 수신 |
| Send email | SMTP 기반 이메일 발송 (Outlook 불필요) |

### 웹 자동화 (Web — MES 웹 화면)
| 액션명 | 용도 |
|---|---|
| Launch new Chrome / Edge / Firefox | 브라우저 실행 |
| Go to web page | URL 이동 |
| Click link on web page | 링크 클릭 |
| Fill text field on web page | 입력 필드 값 입력 |
| Get details of element on web page | 웹 요소 텍스트·속성 읽기 |
| Extract data from web page | 웹 페이지 데이터 추출 (테이블 등) |
| Wait for web page to load | 페이지 로딩 대기 |

### HTTP (API 호출)
| 액션명 | 용도 |
|---|---|
| Invoke web service | REST API 호출 (GET/POST 등) |
| Invoke SOAP web service | SOAP API 호출 |

### 오류 처리
| 구성 | 설명 |
|---|---|
| On block error | 액션 블록 감싸기. 오류 발생 시 분기 처리 |
| Retry action | 지정 횟수만큼 재시도 |
| Get last error | 마지막 오류 메시지 변수로 캡처 |

---

## SAP GUI 연동 패턴

| 단계 | 액션 | 설명 |
|---|---|---|
| SAP 실행 | Run application | SAP GUI 실행 파일 경로 지정 |
| 로그인 대기 | Wait for UI element to appear | 로그인 화면 로딩 확인 |
| 로그인 입력 | Set text field in window | User ID / Password 입력 |
| 트랜잭션 이동 | Set text field in window | 커맨드 필드에 T-Code 입력 후 Click (Enter 버튼) |
| 화면 입력 | Set text field in window | 각 입력 필드에 값 입력 |
| 데이터 읽기 | Get detail of UI element / Extract data from window | 결과 화면 값 추출 |
| SAP 종료 | Click UI element / Terminate process | 로그아웃 또는 프로세스 종료 |

---

## MES 연동 패턴

| MES 유형 | 접근 방식 | 주요 액션 |
|---|---|---|
| 웹 기반 MES | Web 자동화 | Launch browser / Fill text field / Extract data from web page |
| 데스크탑 MES | UI 자동화 | Run application / Click UI element / Get detail of UI element |
| API 제공 MES | HTTP 호출 | Invoke web service (GET/POST) |
| 파일 기반 MES | 파일 처리 | Get files in folder / Read text from file / Read from Excel |

---

## 예외 처리 체크리스트 패턴

### 애플리케이션 실행 오류
- [ ] SAP/MES 실행 후 화면 로딩 대기 — Wait for UI element to appear 추가 (타임아웃 설정)
- [ ] 실행 실패 시 On block error → Send email (담당자 알림)

### 데이터 오류
- [ ] 빈값 처리 — If 조건으로 변수 빈값 체크 후 건너뜀 또는 오류 로깅
- [ ] 예상치 못한 화면 전환 — If UI element exists로 예상 화면 여부 확인

### 반복 처리 부분 실패
- [ ] For each 내부 On block error — 실패 항목 오류 목록 변수에 추가 후 계속 진행
- [ ] 반복 완료 후 오류 목록 이메일 발송

### 인증 / 세션 오류
- [ ] SAP 세션 만료 — Wait for UI element + If UI element exists로 재로그인 분기
- [ ] 자동 로그아웃 방지 — 장시간 작업 시 중간 화면 갱신 액션 추가

### 스케줄링
- [ ] Windows 작업 스케줄러 등록 — PAD 실행 파일 경로 + 플로우 이름 인자로 전달
- [ ] PC 재부팅 후 자동 재실행 여부 확인 — 트리거 조건에 "시작 시 실행" 추가
