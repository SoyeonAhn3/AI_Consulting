# 월 마감 보고 자동화

## 사전 준비

```bash
pip install xlwings pandas openpyxl
```

## 매달 실행 순서

1. **SAP 데이터 붙여넣기** (수동)
   → 보고 템플릿의 `SAP download` 시트에 SAP 데이터 붙여넣기

2. **config.py 수정**
   ```python
   MONTH = "03"   # 실행 월만 변경
   ```

3. **스크립트 실행**
   ```bash
   python monthly_report.py
   ```

## 파일 구조

```
excel_automation/
├── config.py          ← 매달 MONTH 변경
├── monthly_report.py  ← 메인 실행 파일
└── README.md
```

## 자동화 단계

| 단계 | 작업 | 비고 |
|------|------|------|
| Step 2 | PVOT 피벗 새로고침 | Excel 피벗테이블 API 사용 |
| Step 3 | Summary 수식 재계산 | 수식 직접 계산 방식 가정 |
| Step 4 | Compability 값 붙여넣기 | Summary → Compability |
| Step 5 | MA Reporting 업데이트 | Compability 수식 참조 가정 |
| Step 6 | input 파일 GM1 H열 업데이트 | A열 식별자 매칭 |

## 수정이 필요한 경우

### Summary가 수식이 아닌 경우
`monthly_report.py`의 `update_summary()` 함수 내 TODO 주석 참고

### MA Reporting이 Compability 수식 참조가 아닌 경우
`update_ma_reporting()` 함수 내 TODO 주석 참고

### 컬럼 위치가 다른 경우
`config.py`에서 해당 컬럼 알파벳 또는 숫자 수정
