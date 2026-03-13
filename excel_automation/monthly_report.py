"""
월 마감 보고 자동화 스크립트
===============================
실행 전 체크리스트:
  1. SAP download 시트에 SAP 데이터 붙여넣기 완료
  2. config.py에서 MONTH 및 파일 경로 확인
  3. Excel 파일이 닫혀 있는지 확인

실행 방법:
  python monthly_report.py
"""

import glob
import os
import sys
import xlwings as xw
from config import *


# ─────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────

def find_input_file() -> str:
    """월별 input 파일 경로 반환"""
    files = glob.glob(os.path.join(INPUT_FOLDER, INPUT_PATTERN))
    if not files:
        raise FileNotFoundError(
            f"Input 파일을 찾을 수 없습니다.\n"
            f"  폴더: {INPUT_FOLDER}\n"
            f"  패턴: {INPUT_PATTERN}"
        )
    if len(files) > 1:
        print(f"  ⚠️  Input 파일 {len(files)}개 발견 → 첫 번째 파일 사용: {files[0]}")
    return files[0]


def col_letter_to_index(letter: str) -> int:
    """컬럼 알파벳 → 1-based 숫자 변환 (e.g., 'A'→1, 'O'→15)"""
    result = 0
    for ch in letter.upper():
        result = result * 26 + (ord(ch) - ord('A') + 1)
    return result


# ─────────────────────────────────────────────
# Step 2: PVOT 피벗테이블 새로고침
# ─────────────────────────────────────────────

def refresh_pivot(wb: xw.Book):
    """PVOT 시트의 모든 피벗테이블 새로고침"""
    print("  📊 PVOT 피벗 새로고침 중...")
    pvot_sheet = wb.sheets[SHEET_PVOT]

    pivot_count = pvot_sheet.api.PivotTables().Count
    if pivot_count == 0:
        print("  ⚠️  피벗테이블이 없습니다. PVOT 시트 이름을 확인하세요.")
        return

    for i in range(1, pivot_count + 1):
        pvot_sheet.api.PivotTables(i).RefreshTable()

    print(f"  ✅ PVOT 피벗 새로고침 완료 (피벗 {pivot_count}개)")


# ─────────────────────────────────────────────
# Step 3: Summary 시트 업데이트
# (PVOT 피벗 새로고침 후 Summary 수식 자동 반영 가정)
# ─────────────────────────────────────────────

def update_summary(wb: xw.Book):
    """
    Summary 시트는 PVOT를 참조하는 수식으로 구성되어 있다고 가정.
    피벗 새로고침 후 자동 업데이트됨.

    만약 Summary가 수식이 아닌 경우:
    → 아래 TODO 부분을 실제 로직으로 교체하세요.
    """
    print("  📋 Summary 시트 확인 중...")
    summary_sheet = wb.sheets[SHEET_SUMMARY]

    # TODO: Summary가 PVOT 수식 참조가 아닌 경우 아래 로직 구현
    # 예시: PVOT 데이터를 읽어 고객사별 월별 합계를 Summary에 기록
    #
    # pvot_sheet = wb.sheets[SHEET_PVOT]
    # pvot_df = pvot_sheet.used_range.options(pd.DataFrame, header=1).value
    # ...

    # 현재는 수식 자동 반영 가정 → 강제 재계산
    wb.app.api.CalculateFull()
    print("  ✅ Summary 업데이트 완료 (수식 재계산)")


# ─────────────────────────────────────────────
# Step 4: Compability 시트 — Summary 값 복사 붙여넣기
# ─────────────────────────────────────────────

def update_compability(wb: xw.Book):
    """Summary 데이터를 Compability에 값만 붙여넣기"""
    print("  📋 Compability 시트 업데이트 중...")

    summary_sheet = wb.sheets[SHEET_SUMMARY]
    compat_sheet  = wb.sheets[SHEET_COMPAT]

    # Summary 데이터 범위 (구분+고객사+월별데이터, 17행)
    end_row = SUMMARY_START_ROW + SUMMARY_DATA_ROWS - 1
    src_range = summary_sheet.range(
        f"{SUMMARY_COL_GUBUN}{SUMMARY_START_ROW}:"
        f"{SUMMARY_COL_DATA_END}{end_row}"
    )

    # 값 읽기 → Compability에 값만 붙여넣기
    values = src_range.value
    compat_sheet.range(COMPAT_PASTE_START).value = values

    print(f"  ✅ Compability 업데이트 완료 ({len(values)}행 복사)")


# ─────────────────────────────────────────────
# Step 5: MA Reporting 시트 — Compability 값 연결
# (MA Reporting이 Compability 수식 참조라면 재계산으로 충분)
# ─────────────────────────────────────────────

def update_ma_reporting(wb: xw.Book):
    """
    MA Reporting은 Compability를 수식으로 참조한다고 가정.
    A열 식별자는 고정값이므로 건드리지 않음.

    만약 수식 참조가 아닌 경우:
    → Compability 값을 읽어 MA Reporting B열 이후에 붙여넣기
    """
    print("  📄 MA Reporting 시트 확인 중...")
    wb.app.api.CalculateFull()

    # TODO: 수식 참조가 아닌 경우 아래 주석 해제 후 수정
    #
    # compat_sheet = wb.sheets[SHEET_COMPAT]
    # ma_sheet     = wb.sheets[SHEET_MA]
    # values = compat_sheet.used_range.value
    # ma_sheet.range("B2").value = values  # A열(식별자) 제외하고 B열부터 붙여넣기

    print("  ✅ MA Reporting 업데이트 완료")


# ─────────────────────────────────────────────
# Step 6: input 파일 GM1 시트 H열 업데이트
# ─────────────────────────────────────────────

def update_input_gm1(wb: xw.Book, input_path: str):
    """
    MA Reporting A열(식별자) + O열(KRW값) 읽기
    → input 파일 GM1 시트 A열과 매칭
    → 일치하는 행의 H열에 값 입력
    """
    print(f"  📂 Input 파일 업데이트 중: {os.path.basename(input_path)}")

    ma_sheet = wb.sheets[SHEET_MA]

    # MA Reporting 데이터 읽기 (A열 ~ O열)
    last_row = ma_sheet.cells(ma_sheet.cells.last_cell.row, MA_COL_IDENTIFIER).end("up").row
    ma_values = ma_sheet.range(
        ma_sheet.cells(MA_DATA_START_ROW, MA_COL_IDENTIFIER),
        ma_sheet.cells(last_row, MA_COL_VALUE)
    ).value

    # 식별자 → 값 딕셔너리 생성
    ma_dict = {}
    for row in ma_values:
        if row and row[0] is not None:
            identifier = str(row[0]).strip()
            value      = row[MA_COL_VALUE - MA_COL_IDENTIFIER]  # O열 상대 인덱스
            ma_dict[identifier] = value

    if not ma_dict:
        print("  ⚠️  MA Reporting에서 읽을 데이터가 없습니다.")
        return

    print(f"  → MA Reporting 식별자 {len(ma_dict)}개 로드")

    # input 파일 열기 (별도 Excel 인스턴스)
    input_app = xw.App(visible=False)
    try:
        input_wb  = input_app.books.open(input_path)
        gm1_sheet = input_wb.sheets[SHEET_INPUT_GM1]

        # GM1 A열 마지막 행 찾기
        gm1_last_row = gm1_sheet.cells(
            gm1_sheet.cells.last_cell.row, GM1_COL_KEY
        ).end("up").row

        updated = 0
        not_found = []

        for i in range(GM1_DATA_START_ROW, gm1_last_row + 1):
            key = gm1_sheet.cells(i, GM1_COL_KEY).value
            if key is None:
                continue
            key = str(key).strip()
            if key in ma_dict:
                gm1_sheet.cells(i, GM1_COL_TARGET).value = ma_dict[key]
                updated += 1
            else:
                not_found.append(key)

        input_wb.save()
        print(f"  ✅ GM1 H열 업데이트 완료: {updated}행 업데이트")

        if not_found:
            print(f"  ⚠️  매칭 안된 식별자 ({len(not_found)}개): {not_found[:5]}{'...' if len(not_found) > 5 else ''}")

    finally:
        input_app.quit()


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────

def main():
    print("=" * 55)
    print(f"  월 마감 보고 자동화 시작 ({YEAR}년 {MONTH}월)")
    print("=" * 55)

    # Input 파일 확인
    try:
        input_path = find_input_file()
        print(f"  ✅ Input 파일 확인: {os.path.basename(input_path)}\n")
    except FileNotFoundError as e:
        print(f"\n❌ 오류: {e}")
        sys.exit(1)

    # 템플릿 파일 열기
    app = xw.App(visible=True)
    app.display_alerts = False  # 팝업 메시지 억제

    try:
        wb = app.books.open(TEMPLATE_PATH)

        # Step 2
        refresh_pivot(wb)

        # Step 3
        update_summary(wb)

        # Step 4
        update_compability(wb)

        # Step 5
        update_ma_reporting(wb)

        # 템플릿 저장
        wb.save()
        print("\n  💾 템플릿 저장 완료")

        # Step 6
        update_input_gm1(wb, input_path)

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        raise

    finally:
        wb.close()
        app.quit()

    print("\n" + "=" * 55)
    print("  🎉 월 마감 보고 자동화 완료!")
    print("=" * 55)


if __name__ == "__main__":
    main()
