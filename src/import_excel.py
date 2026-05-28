import pandas as pd
import sys

def import_excel(excel_file = 'private/REAL_RKAP.xlsx', excel_sheet=""):
    try:
        df = pd.read_excel(excel_file, sheet_name=excel_sheet.upper())
        return df

    except Exception as e:
        message = "[⚠️ ERROR] Tidak dapat membuka excel. Silakan Save dan tutup Excel terlebih dahulu. \n"
        message += "Tekan Enter untuk keluar program..."
        input(message)
        sys.exit(1)