import os
from wakepy import keep
import time
from datetime import datetime
import pandas as pd
from selenium.webdriver.common.by import By

from src.config import inisialisasi_chrome
from src.log import get_menu, catat_proyek_done, create_summary_log
from src.validation import duplicate_link_validation, address_link_validation, portofolio_validation, is_already_done
from src.extract import formated_number, clear_formated, extract_kode_proyek, extract_proyek_rkap_crm
from src.import_excel import import_excel
from src.input import create_dataset_per_proyek, input_data_proyek

def main():
    # pyinstaller --onefile --hidden-import="selenium" --hidden-import="selenium.webdriver" --hidden-import="selenium.webdriver.chrome.webdriver" main.py

    # membaca data dari excel
    print("\nMembaca dan memproses file Excel...")
    excel_file = 'private/REAL_RKAP.xlsx'
    excel_sheet = input("\nMasukkan nama sheet Excel yang akan diproses (misal: SIBPP): ").upper()
    df = import_excel(excel_file, excel_sheet=excel_sheet)
    df['proyek_nomor'] = df['proyek_nomor'].apply(lambda x: " ".join(str(x).split()) if pd.notnull(x) else x)

    unique_projects = df['proyek_nomor'].dropna().unique()
    total_projects = len(unique_projects)
    print(f"Ditemukan {total_projects} proyek unik.")
    
    log_file = "automation_log.txt"
    proyek_done_file = "proyek_done.txt"
    processed_projects = {}

    if os.path.exists(proyek_done_file):
        get_menu(proyek_done_file, processed_projects)

    # buka chrome
    driver = inisialisasi_chrome()
    input("\nPastikan Anda sudah login di browser, lalu tekan Enter di sini untuk mulai otomatisasi...")

    # validasi data exclude skip, apakah link sudah unique semua
    print(duplicate_link_validation(df))
    print(address_link_validation(df))

    # Mengaktifkan wakepy agar layar tetap menyala (presenting mode)
    screen_awake = keep.presenting()
    screen_awake.__enter__()
    start_time = datetime.now()

    # input setiap project
    list_skipped = []
    list_mismatch = []
    list_error = []

    updated_count = 0
    skipped_count = 0
    mismatch_count = 0
    error_count = 0

    for target_proyek in unique_projects:
        if is_already_done(target_proyek, processed_projects, list_mismatch, updated_count, mismatch_count):
            continue

        try:
            # Memfilter baris dan mengambil link data untuk setiap proyek
            df_filtered = df[df['proyek_nomor'].astype(str) == str(target_proyek)]
            input_link = str(df_filtered['link'].iloc[0]).strip() if 'link' in df_filtered.columns else ""
            kode_proyek = extract_kode_proyek(input_link)

            # ambil nama proyek crm, ambil nominal rkap, cek portofolio
            address_rkap = f"https://crm.ptsi.co.id/index.php/project/rkap/view/{kode_proyek}#rkap"
            driver.get(address_rkap)
            time.sleep(2)
            nama_crm, rkap_crm = extract_proyek_rkap_crm(driver)

            pend_1 = df_filtered['pend_1'].iloc[0] if 'pend_1' in df_filtered.columns else 0
            pend_1_formatted = formated_number(pend_1)
            pend_crm_formatted = formated_number(rkap_crm)

            print(f"\n\n==========================================")
            print(f"PROGRESS SAAT INI     : {updated_count} Sukses | {skipped_count} Dilewati | {mismatch_count} Mismatch | {error_count} Error")
            print(f"NAMA PROYEK CRM       : {nama_crm}")
            print(f"NAMA PROYEK RKAP REAL : {target_proyek}")
            print(f"KODE PROYEK RKAP REAL : {kode_proyek}")
            print(f"PENDAPATAN RKAP CRM   : {pend_crm_formatted}")
            print(f"PENDAPATAN RKAP REAL  : {pend_1_formatted}")
            print(f"==========================================")
        
            if not input_link or input_link.lower() == "nan" or str(input_link) == "Tidak ada":
                print("⚠️ Link tidak ditemukan di data Excel. Melewati proyek ini...")
                list_skipped.append(f"Proyek: {target_proyek}")
                skipped_count += 1
                continue
                
            if input_link.lower() == "skip":
                print(f"⏩ Terdeteksi instruksi 'skip' pada kolom link. Melewati proyek ini...")
                list_skipped.append(f"Proyek: {target_proyek}")
                skipped_count += 1
                continue
                
            # Validasi apakah kode_proyek valid (berisi angka)
            if not kode_proyek.isdigit():
                print(f"⚠️ Link tidak valid ({input_link}). Melewati proyek ini...")
                list_skipped.append(f"Proyek: {target_proyek}")
                skipped_count += 1
                continue

            print(f"\nSedang berada di laman {address_rkap} untuk cek Portofolio...")
            pesan_mismatch = portofolio_validation(driver, kode_proyek, df_filtered)
            if pesan_mismatch:
                list_mismatch.append(f"Proyek: {target_proyek} | Kode: {kode_proyek} | {pesan_mismatch}")
                mismatch_count += 1

            # ==========================================
            # MEMBUKA HALAMAN RAB UNTUK INPUT DATA
            # ==========================================
            address_rab = f"https://crm.ptsi.co.id/index.php/project/rkap/view/{kode_proyek}#rab"
            print(f"Beralih ke laman {address_rab} untuk mulai input data RAB...")
            driver.get(address_rab)
            time.sleep(2)
            dataset_per_proyek = create_dataset_per_proyek(df_filtered)
            
            # cek apakah proyek desentralisasi (tidak bisa input bulanan)
            a_tags = driver.find_elements(By.XPATH, "//div[@id='rab-bulanan']//a")
            if not a_tags:
                print(f"⚠️ Tidak ada link bulan (tag a). Terdeteksi proyek desentralisasi. Lanjut ke proyek selanjutnya...")
                list_skipped.append(f"Proyek: {target_proyek} | Keterangan: Proyek desentralisasi")
                skipped_count += 1
                continue

            print(f"✅ Berhasil memuat {len(dataset_per_proyek)-1} baris data untuk proyek tersebut.")
            print(f"Mulai input data untuk seluruh bulan...")

            # Input data setiap bulan
            pesan_input = input_data_proyek(driver, dataset_per_proyek)
            if pesan_input:
                pesan_mismatch = (pesan_mismatch + " | " + pesan_input) if pesan_mismatch else pesan_input
            catat_proyek_done(proyek_done_file, target_proyek, pesan_mismatch)
            updated_count += 1
        
        except Exception as e:
            print(f"\n[⚠️ ERROR Sistem] Gagal memproses keseluruhan proyek {target_proyek}: {e}")
            list_error.append(f"Proyek: {target_proyek} | Error Sistem: Gagal diproses")
            error_count += 1
            continue

    screen_awake.__exit__(None, None, None)

    end_time = datetime.now()
    total_duration = end_time - start_time
    total_duration_str = str(total_duration).split('.')[0] # Menghilangkan milidetik agar tampilan lebih rapi

    summary_text = create_summary_log(excel_file, excel_sheet, start_time, end_time, 
                                    total_duration_str, total_projects, 
                                    updated_count, skipped_count, mismatch_count, 
                                    list_skipped, list_mismatch, list_error)

    print("\n" + summary_text)

    # Menyimpan log ringkasan akhir ke automation_log.txt
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(summary_text + "\n\n")

    input("\nProgram telah selesai, silakan cek automation_log.txt \nTekan Enter untuk keluar..")

    driver.quit()


if __name__ == "__main__":
    main()