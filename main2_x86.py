import sys
from wakepy import keep
import subprocess
import time
from datetime import datetime
import traceback
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

def bersihkan_teks(teks):
    if not teks or str(teks).lower() == "nan":
        return ""
    # 1. Kapital semua & hapus spasi ujung
    t = str(teks).upper().strip()
    # 2. Seragamkan 'AND' menjadi '&'
    t = t.replace('AND', '&')
    # 3. Hapus tanda koma dan spasi ganda di tengah kalimat
    t = t.replace(',', '')
    t = " ".join(t.split())
    return t

# ==========================================
# 0. FORM KONTROL
# ==========================================
print("\nMembaca dan memproses file Excel...")
excel_file = 'private/REAL_RKAP.xlsx'
excel_sheet = input("\nMasukkan nama sheet Excel yang akan diproses (misal: SIBPP): ")
df = pd.read_excel(excel_file, sheet_name=excel_sheet.upper())

# Mendapatkan daftar proyek unik dari kolom 'proyek_nomor'
unique_projects = df['proyek_nomor'].dropna().unique()
print(f"Ditemukan {len(unique_projects)} proyek unik.")

# Menjalankan perintah CMD di latar belakang tanpa memblokir jalannya Python (menggunakan Popen)
# "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-debug"
# pyinstaller --onefile --hidden-import="selenium" --hidden-import="selenium.webdriver" --hidden-import="selenium.webdriver.chrome.webdriver" main2_x86.py
print("\n[System] Mencoba membuka Google Chrome dalam Mode Debugging...")
chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
port = "9222"
user_data = r"C:\chrome-debug"
try:
    subprocess.Popen([
        chrome_path, 
        f"--remote-debugging-port={port}", 
        f"--user-data-dir={user_data}"
    ])
    time.sleep(2) 
    print("[System] Google Chrome berhasil dibuka.")

except Exception as e:
    print(f"[⚠️ ERROR] Gagal membuka Chrome secara otomatis. Pastikan jalur path benar: {e}")
    print("Mencoba melanjutkan koneksi port jika Chrome sudah terbuka manual...")
    sys.exit()

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

driver = webdriver.Chrome(options=chrome_options)

# Beri jeda agar user bisa memastikan sudah login di browser yang terbuka sebelum script berjalan otomatis
address = f"https://crm.ptsi.co.id/index.php"
driver.get(address)
input("\nPastikan Anda sudah login di browser, lalu tekan Enter di sini untuk mulai otomatisasi...")
start_time = datetime.now()

log_file = "automation_log.txt"

list_skipped = []
list_mismatch = []
list_error = []

# Mengaktifkan wakepy agar layar tetap menyala (presenting mode)
screen_awake = keep.presenting()
screen_awake.__enter__()

# ==========================================
# 1. PERULANGAN UNTUK SETIAP PROYEK UNIK
# ==========================================
total_projects = len(unique_projects)
updated_count = 0
skipped_count = 0
mismatch_count = 0

for target_proyek in unique_projects:
    try:
        # Memfilter baris dan mengambil link data untuk setipa proyek
        df_filtered = df[df['proyek_nomor'].astype(str) == str(target_proyek)]
        input_link = str(df_filtered['link'].iloc[0]).strip() if 'link' in df_filtered.columns else ""
        
        # Mengekstrak kode proyek dari link setelah "view/"
        if "view/" in input_link:
            kode_proyek = input_link.split("view/")[-1].strip()
            # Membersihkan jika bagian anchor misal #rab terbawa
            if "#" in kode_proyek:
                kode_proyek = kode_proyek.split("#")[0]
        else:
            kode_proyek = input_link.strip()  # Fallback jika Excel hanya berisi kode angka

        # Membuka web untuk mendapatkan nama project CRM
        address_rkap = f"https://crm.ptsi.co.id/index.php/project/rkap/view/{kode_proyek}#rkap"
        driver.get(address_rkap)
        time.sleep(2) # Beri jeda agar halaman sepenuhnya dimuat
        
        target_proyek_CRM = "-"
        try:
            # Membaca teks meskipun elemen tersebut memiliki atribut display:none di HTML (get_attribute("textContent"))
            crm_project_element = driver.find_element(By.XPATH, "//label[@for='potential_id']/following-sibling::div/p[@class='value']")
            target_proyek_CRM = crm_project_element.get_attribute("textContent").strip()
            
            # Jika isinya hanya '-' atau tersembunyi, fallback/gunakan Nama RKAP
            if target_proyek_CRM == "-" or not target_proyek_CRM:
                crm_project_element_alt = driver.find_element(By.XPATH, "//label[@for='nama_potensial']/following-sibling::div/p[@class='value']")
                target_proyek_CRM = crm_project_element_alt.get_attribute("textContent").strip()
        except Exception as e:
            target_proyek_CRM = "Tidak ditemukan"

        pend_1 = df_filtered['pend_1'].iloc[0] if 'pend_1' in df_filtered.columns else "Tidak ada"
        pers_1 = df_filtered['pers_1'].iloc[0] if 'pers_1' in df_filtered.columns else "Tidak ada"
        pend_1_formatted = f"{pend_1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pers_1_formatted = f"{pers_1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        print(f"\n\n==========================================")
        print(f"PROGRESS SAAT INI     : {updated_count} Sukses | {skipped_count} Dilewati | {mismatch_count} Mismatch")
        print(f"NAMA PROYEK CRM       : {target_proyek_CRM}")
        print(f"NAMA PROYEK RKAP REAL : {target_proyek}")
        print(f"KODE PROYEK RKAP REAL : {kode_proyek}")
        print(f"PENDAPATAN RKAP REAL  : {pend_1_formatted}")
        print(f"PERSONIL RKAP REAL    : {pers_1_formatted}")
        print(f"==========================================")
            
        if not input_link or input_link.lower() == "nan":
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
            
        # ==========================================
        # MEMBUKA HALAMAN RKAP UNTUK CEK PORTOFOLIO
        # ==========================================    
        print(f"\nSedang berada di laman {address_rkap} untuk cek Portofolio...")

        portofolio_excel = str(df_filtered['portofolio'].iloc[0]).strip() if 'portofolio' in df_filtered.columns else ""
        if portofolio_excel and portofolio_excel.lower() != "nan":
            try:
                portofolio_web_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//label[@for='unit_portofolio_id']/following-sibling::div/p[@class='value']"))
                )
                portofolio_web = portofolio_web_element.text.strip()
                
                portofolio_web_bersih = bersihkan_teks(portofolio_web)
                portofolio_excel_bersih = bersihkan_teks(portofolio_excel)
                
                # Bandingkan hasil teks yang sudah dibersihkan
                if portofolio_web_bersih != portofolio_excel_bersih:
                    print(f"⚠️ Mismatch Portofolio - Proyek: {target_proyek}, Kode: {kode_proyek}, Web: '{portofolio_web}', Excel: '{portofolio_excel}'")
                    list_mismatch.append(f"Proyek: {target_proyek} | Kode: {kode_proyek} | Web: '{portofolio_web}' | Excel: '{portofolio_excel}'")
                    mismatch_count += 1
                else:
                    print(f"✅ Cocok - Portofolio Proyek {kode_proyek} sesuai antara Web dan Excel.")
            except Exception as e:
                print("⚠️ Peringatan: Elemen Unit Pengelola Portofolio tidak ditemukan di web atau tidak dapat diakses.")
                
        # ==========================================
        # MEMBUKA HALAMAN RAB UNTUK INPUT DATA
        # ==========================================
        address_rab = f"https://crm.ptsi.co.id/index.php/project/rkap/view/{kode_proyek}#rab"
        driver.get(address_rab)
        print(f"Beralih ke laman {address_rab} untuk mulai input data RAB...")
        time.sleep(2) # Beri jeda sebelum mulai klik bulan
        
        dataset = []
        for index, row in df_filtered.iterrows():
            dataset.append({
                "bulan": str(row["bulan"]).strip(),
                "b_pendapatan": str(int(round(float(row["Pendapatan"])))),
                "b_personil": str(int(round(float(row["Personil"])))),
                "b_dinas": str(int(round(float(row["Perjalanan Dinas"])))),
                "b_perlengkapan": str(int(round(float(row["Perlengkapan Kerja"])))),
                "b_kerjasama": str(int(round(float(row["Kerjasama"])))),
                "b_fasilitas": str(int(round(float(row["Fasilitas Kerja"])))),
                "b_studi": str(int(round(float(row["Studi Kelayakan"])))),
                "b_jasa": "0"
            })

        print(f"✅ Berhasil memuat {len(dataset)-1} baris data untuk proyek tersebut.")
        print(f"Mulai input data untuk seluruh bulan...")

        # ==========================================
        # 2. PERULANGAN OTOMATISASI UNTUK SETIAP BULAN
        # ==========================================
        dataset = dataset[1:]
        for data in dataset:
            target_bulan = data["bulan"][:3].capitalize()
            
            while True:
                # print(f"\n------------------------------------------")
                # print(f"MULAI MEMPROSES BULAN: {data["bulan"].upper()}")
                # print(f"PROYEK : {target_proyek}")
                # print(f"KODE   : {kode_proyek}")
                # print(f"------------------------------------------")
                
                try:
                    # print(f"[{target_bulan}] Mencari dan mengklik link...")
                    link_bulan = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//div[@id='rab-bulanan']//a[text()='{target_bulan}']"))
                    )
                    driver.execute_script("arguments[0].click();", link_bulan)

                    # print(f"[{target_bulan}] Menunggu pop-up modal RAB muncul...")
                    WebDriverWait(driver, 15).until(
                        EC.visibility_of_element_located((By.ID, "rabModal"))
                    )

                    for id_elemen, nilai_input in data.items():
                        if id_elemen == "bulan":
                            continue
                            
                        # print(f"[{target_bulan}] Mengisi {id_elemen} -> {nilai_input}")
                        
                        input_field = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, id_elemen))
                        )
                        
                        input_field.click()
                        input_field.send_keys(Keys.CONTROL + "a")
                        input_field.send_keys(Keys.BACKSPACE)
                        input_field.send_keys(str(nilai_input))
                        
                        time.sleep(0.2)

                    # print(f"[{target_bulan}] Memicu kalkulasi rumus web...")
                    input_field.send_keys(Keys.TAB) 
                    time.sleep(1) 

                    # print(f"[{target_bulan}] Memastikan tombol Simpan aktif...")
                    tombol_simpan = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "rab-confirmation"))
                    )
                    
                    # print(f"[{target_bulan}] Mengklik tombol Simpan...")
                    driver.execute_script("arguments[0].click();", tombol_simpan)

                    # print(f"[{target_bulan}] Menunggu sinkronisasi server...")
                    WebDriverWait(driver, 60).until(
                        EC.invisibility_of_element_located((By.ID, "rabModal"))
                    )
                    
                    print(f"✅ DATA [{data["bulan"].capitalize()}] BERHASIL DIINPUT DAN DISIMPAN!")
                    time.sleep(1)
                    break  # Berhasil, memecah (keluar) dari loop `while` untuk lanjut ke iterasi `for` berikutnya

                except Exception as e:
                    print(f"\n[⚠️ ERROR] Gagal memproses bulan {target_bulan}.")
                    # print(traceback.format_exc())
                    
                    list_error.append(f"Proyek: {target_proyek} | Kode: {kode_proyek} | Bulan: {target_bulan}")

                    print("Merefresh halaman dan mencoba input ulang...")
                    driver.refresh()
                    time.sleep(2) # Tunggu sejenak setelah refresh agar script siap membaca ulang web

        # Menambah hitungan proyek yang sukses diproses setelah semua perulangan bulan untuk proyek ini selesai
        updated_count += 1

    except Exception as e:
        print(f"\n[⚠️ ERROR Sistem] Gagal memproses keseluruhan proyek {target_proyek}: {e}")
        list_error.append(f"Proyek: {target_proyek} | Error Sistem: Gagal diproses")
        skipped_count += 1
        continue

# Mematikan wakepy (mengembalikan pengaturan layar ke normal)
screen_awake.__exit__(None, None, None)

end_time = datetime.now()
total_duration = end_time - start_time
total_duration_str = str(total_duration).split('.')[0] # Menghilangkan milidetik agar tampilan lebih rapi

summary_text = (
    "==========================================\n"
    "PROSES SELESAI! Seluruh data proyek telah diinput.\n"
    f"Sumber File Excel  : {excel_file}\n"
    f"Sumber Sheet       : {excel_sheet}\n"
    f"Waktu Mulai        : {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"Waktu Selesai      : {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"Total Durasi       : {total_duration_str}\n"
    f"Total Proyek       : {total_projects}\n"
    f"Berhasil Diupdate  : {updated_count}\n"
    f"Proyek Dilewati    : {skipped_count}\n"
    f"Portofolio Mismatch: {mismatch_count}\n"
)

if list_skipped:
    summary_text += "\nDetail Proyek Dilewati (Skipped):\n"
    for item in list_skipped:
        summary_text += f"- {item}\n"

if list_mismatch:
    summary_text += "\nDetail Portofolio Mismatch:\n"
    for item in list_mismatch:
        summary_text += f"- {item}\n"

list_error = list(set(list_error))
if list_error:
    summary_text += "\nDetail Error Input Data:\n"
    for item in list_error:
        summary_text += f"- {item}\n"

summary_text += "=========================================="

print("\n" + summary_text)

# Menyimpan log ringkasan akhir ke automation_log.txt
with open(log_file, "a", encoding="utf-8") as f:
    f.write(summary_text + "\n\n")

driver.quit()