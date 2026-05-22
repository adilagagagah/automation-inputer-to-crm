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
df = pd.read_excel('private/SIBPP_RKAP.xlsx')

# Mendapatkan daftar proyek unik dari kolom 'proyek_2'
unique_projects = df['proyek_2'].dropna().unique()
print(f"Ditemukan {len(unique_projects)} proyek unik.")

# "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\chrome-debug"
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(options=chrome_options)

# Beri jeda agar user bisa memastikan sudah login di browser yang terbuka sebelum script berjalan otomatis
input("\nPastikan Anda sudah login di browser, lalu tekan Enter di sini untuk mulai otomatisasi...")
start_time = datetime.now()

# ==========================================
# 1. PERULANGAN UNTUK SETIAP PROYEK UNIK
# ==========================================
total_projects = len(unique_projects)
updated_count = 0
skipped_count = 0
mismatch_count = 0

for target_proyek in unique_projects:
    # Memfilter baris data hanya untuk proyek ini
    df_filtered = df[df['proyek_2'].astype(str) == str(target_proyek)]
    
    pend_1 = df_filtered['pend_1'].iloc[0] if 'pend_1' in df_filtered.columns else "Tidak ada"
    pers_1 = df_filtered['pers_1'].iloc[0] if 'pers_1' in df_filtered.columns else "Tidak ada"
    pend_1_formatted = f"{pend_1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    pers_1_formatted = f"{pers_1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    print(f"\n==========================================")
    print(f"PROYEK: {target_proyek}")
    print(f"PENDAPATAN RKAP REAL: {pend_1_formatted}")
    print(f"PERSONIL RKAP REAL  : {pers_1_formatted}")
    print(f"==========================================")
    
    # Mengambil link dari dataframe kolom 'link'
    input_link = str(df_filtered['link'].iloc[0]).strip() if 'link' in df_filtered.columns else ""
    
    if not input_link or input_link.lower() == "nan":
        print("⚠️ Link tidak ditemukan di data Excel. Melewati proyek ini...")
        skipped_count += 1
        continue
        
    if input_link.lower() == "skip":
        pesan_skip = f"Skipped - Proyek: {target_proyek}"
        print(f"⏩ Terdeteksi instruksi 'skip' pada kolom link. Melewati proyek ini...")
        with open("skipped_projects_log.txt", "a", encoding="utf-8") as f:
            f.write(pesan_skip + "\n")
        skipped_count += 1
        continue
        
    # Mengekstrak kode proyek dari link setelah "view/"
    if "view/" in input_link:
        kode_proyek = input_link.split("view/")[-1].strip()
        # Membersihkan jika bagian anchor misal #rab terbawa
        if "#" in kode_proyek:
            kode_proyek = kode_proyek.split("#")[0]
    else:
        kode_proyek = input_link.strip()  # Fallback jika Excel hanya berisi kode angka

    # Validasi apakah kode_proyek valid (berisi angka)
    if not kode_proyek.isdigit():
        print(f"⚠️ Link tidak valid ({input_link}). Melewati proyek ini...")
        skipped_count += 1
        continue
        
    # ==========================================
    # CEK KESESUAIAN PORTOFOLIO DI HALAMAN #RKAP
    # ==========================================
    address_rkap = f"https://crm.ptsi.co.id/index.php/project/rkap/view/{kode_proyek}#rkap"
    driver.get(address_rkap)
    print(f"\nSedang berada di laman {address_rkap} untuk cek Portofolio...")
    time.sleep(3) # Beri jeda agar halaman sepenuhnya dimuat
    
    portofolio_excel = str(df_filtered['Portofolio'].iloc[0]).strip() if 'Portofolio' in df_filtered.columns else ""
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
                pesan_mismatch = f"Mismatch Portofolio - Proyek: {target_proyek}, Kode: {kode_proyek}, Web: '{portofolio_web}', Excel: '{portofolio_excel}'"
                print(f"⚠️ {pesan_mismatch}")
                with open("portofolio_mismatch_log.txt", "a", encoding="utf-8") as f:
                    f.write(pesan_mismatch + "\n")
                mismatch_count += 1
            else:
                print(f"✅ Cocok - Portofolio Proyek {kode_proyek} sesuai antara Web dan Excel.")
        except Exception as e:
            print("⚠️ Peringatan: Elemen Unit Pengelola Portofolio tidak ditemukan di web atau tidak dapat diakses.")
            
    # ==========================================
    # BERALIH KE HALAMAN #RAB UNTUK INPUT DATA
    # ==========================================
    address_rab = f"https://crm.ptsi.co.id/index.php/project/rkap/view/{kode_proyek}#rab"
    driver.get(address_rab)
    print(f"Beralih ke laman {address_rab} untuk mulai input data RAB...")
    time.sleep(3) # Beri jeda sebelum mulai klik bulan
    
    dataset = []
    for index, row in df_filtered.iterrows():
        dataset.append({
            "bulan": str(row["bulanan"]).strip(),
            "b_pendapatan": str(int(round(float(row["Pendapatan"])))),
            "b_personil": str(int(round(float(row["Personil"])))),
            "b_dinas": str(int(round(float(row["Perjalanan Dinas"])))),
            "b_perlengkapan": str(int(round(float(row["Perlengkapan Kerja"])))),
            "b_kerjasama": str(int(round(float(row["Kerjasama"])))),
            "b_fasilitas": str(int(round(float(row["Fasilitas Kerja"])))),
            "b_studi": str(int(round(float(row["Studi Kelayakan"])))),
            "b_jasa": "0"
        })

    print(f"Berhasil memuat {len(dataset)} baris data untuk proyek tersebut.")

    # ==========================================
    # 2. PERULANGAN OTOMATISASI UNTUK SETIAP BULAN
    # ==========================================
    for data in dataset:
        target_bulan = data["bulan"][:3].capitalize()
        if target_bulan == "Kum":
            continue
        
        while True:
            print(f"\n------------------------------------------")
            print(f"MULAI MEMPROSES BULAN: {data["bulan"].upper()}")
            print(f"PROYEK : {target_proyek}")
            print(f"KODE   : {kode_proyek}")
            print(f"------------------------------------------")
            
            try:
                print(f"[{target_bulan}] Mencari dan mengklik link...")
                link_bulan = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@id='rab-bulanan']//a[text()='{target_bulan}']"))
                )
                driver.execute_script("arguments[0].click();", link_bulan)

                print(f"[{target_bulan}] Menunggu pop-up modal RAB muncul...")
                WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.ID, "rabModal"))
                )

                for id_elemen, nilai_input in data.items():
                    if id_elemen == "bulan":
                        continue
                        
                    print(f"[{target_bulan}] Mengisi {id_elemen} -> {nilai_input}")
                    
                    input_field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, id_elemen))
                    )
                    
                    input_field.click()
                    input_field.send_keys(Keys.CONTROL + "a")
                    input_field.send_keys(Keys.BACKSPACE)
                    input_field.send_keys(str(nilai_input))
                    
                    time.sleep(0.2)

                print(f"[{target_bulan}] Memicu kalkulasi rumus web...")
                input_field.send_keys(Keys.TAB) 
                time.sleep(1.5) 

                print(f"[{target_bulan}] Memastikan tombol Simpan aktif...")
                tombol_simpan = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "rab-confirmation"))
                )
                
                print(f"[{target_bulan}] Mengklik tombol Simpan...")
                driver.execute_script("arguments[0].click();", tombol_simpan)

                print(f"[{target_bulan}] Menunggu sinkronisasi server...")
                WebDriverWait(driver, 60).until(
                    EC.invisibility_of_element_located((By.ID, "rabModal"))
                )
                
                print(f"[{target_bulan}] DATA BERHASIL DIINPUT DAN DISIMPAN!")
                time.sleep(2)
                break  # Berhasil, memecah (keluar) dari loop `while` untuk lanjut ke iterasi `for` berikutnya

            except Exception as e:
                print(f"\n[⚠️ ERROR] Gagal memproses bulan {target_bulan}.")
                # print(traceback.format_exc())
                
                # Menambahkan log ke dalam file teks setiap kali terjadi error
                with open("error_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"Gagal memproses - Proyek: {target_proyek}, Kode: {kode_proyek}, Bulan: {target_bulan}\n")

                print("Merefresh halaman dan mencoba kembali untuk bulan yang sama...\n")
                driver.refresh()
                time.sleep(3) # Tunggu sejenak setelah refresh agar script siap membaca ulang web

    # Menambah hitungan proyek yang sukses diproses setelah semua perulangan bulan untuk proyek ini selesai
    updated_count += 1

end_time = datetime.now()
total_duration = end_time - start_time
total_duration_str = str(total_duration).split('.')[0] # Menghilangkan milidetik agar tampilan lebih rapi

print("\n==========================================")
print("PROSES SELESAI! Seluruh data proyek telah diinput.")
print(f"Waktu Mulai        : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Waktu Selesai      : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total Durasi       : {total_duration_str}")
print(f"Total Proyek       : {total_projects}")
print(f"Berhasil Diupdate  : {updated_count}")
print(f"Proyek Dilewati    : {skipped_count}")
print(f"Portofolio Mismatch: {mismatch_count}")
print("==========================================")
driver.quit()