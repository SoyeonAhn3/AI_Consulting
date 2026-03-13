# ============================================================
# 월 마감 보고 자동화 - 설정 파일
# 매달 이 파일의 MONTH만 변경하면 됩니다
# ============================================================

# ── 실행 월 설정 ──────────────────────────────────────────
MONTH = "03"  # 실행 월 (e.g., "01", "02", "03" ...)
YEAR  = "2026"

# ── 파일 경로 설정 ────────────────────────────────────────
# 보고용 템플릿 파일 (SAP download 시트에 데이터 붙여넣기 완료 후 실행)
TEMPLATE_PATH = r"C:\Users\sy.ahn\OneDrive - Bosch Group\월마감\보고_템플릿.xlsx"

# input 파일 폴더 및 파일명 패턴 (e.g., 파일명_03_2026.xlsx)
INPUT_FOLDER  = r"C:\Users\sy.ahn\OneDrive - Bosch Group\월마감\input"
INPUT_PATTERN = f"*_{MONTH}_*.xlsx"  # 파일명 패턴 → 실제 패턴에 맞게 수정

# ── 시트명 설정 ───────────────────────────────────────────
SHEET_SAP        = "SAP download"
SHEET_PVOT       = "PVOT"
SHEET_SUMMARY    = "Summary"
SHEET_COMPAT     = "Compability"
SHEET_MA         = "MA Reporting"
SHEET_INPUT_GM1  = "GM1"

# ── SAP download 시트 컬럼 설정 ───────────────────────────
SAP_COL_MONTH    = "A"   # Month 컬럼 → 실제 컬럼으로 수정
SAP_COL_CUST     = "B"   # 고객번호 컬럼 → 실제 컬럼으로 수정
SAP_AUTO_COLS    = ["F", "G", "H"]  # 자동수식 컬럼 (건드리지 않음)

# ── Summary 시트 설정 ─────────────────────────────────────
SUMMARY_DATA_ROWS     = 17    # Summary 상단 고객사 데이터 행 수
SUMMARY_START_ROW     = 2     # 데이터 시작 행 (1행 = 헤더 가정)
SUMMARY_COL_GUBUN     = "A"   # 구분 컬럼
SUMMARY_COL_CUST      = "B"   # 고객사명 컬럼
SUMMARY_COL_DATA_START = "C"  # 월별 데이터 시작 컬럼 → 실제 컬럼으로 수정
SUMMARY_COL_DATA_END  = "N"   # 월별 데이터 끝 컬럼 (12개월 기준) → 실제 컬럼으로 수정

# ── Compability 시트 설정 ────────────────────────────────
COMPAT_PASTE_START = "A1"  # 붙여넣기 시작 셀

# ── MA Reporting 시트 설정 ───────────────────────────────
MA_COL_IDENTIFIER = 1   # A열 = 1 (식별자, 고정값)
MA_COL_VALUE      = 15  # O열 = 15 (KRW 값)
MA_DATA_START_ROW = 2   # 데이터 시작 행

# ── input 파일 GM1 시트 설정 ─────────────────────────────
GM1_COL_KEY    = 1  # A열 = 1 (식별자, MA Reporting A열과 매칭)
GM1_COL_TARGET = 8  # H열 = 8 (업데이트 대상)
GM1_DATA_START_ROW = 2  # 데이터 시작 행
