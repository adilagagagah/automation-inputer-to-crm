import time
import traceback
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


# ==========================================
# 0. FORM KONTROL
# ==========================================
# kode_proyek = 
target_proyek = input("\nMasukkan nama proyek : ")
kode_proyek   = input("Masukkan kode link   : ")
address = f"https://crm.ptsi.co.id/index.php/project/rkap/view/{kode_proyek}#rab"


# ==========================================
# 1. MEMBACA & FILTER DATA DARI EXCEL ASLI
# ==========================================
print("\nMembaca dan memproses file Excel...")
df = pd.read_excel('SIBPP_PROYEK.xlsm')

# Memfilter baris di mana kolom 'proyek_2' mengandung nama proyek target
df_filtered = df[df['proyek_2'].astype(str).str.contains(target_proyek, case=False, na=False)]

# Mengonversi data Excel menjadi struktur list dictionary yang siap dibaca oleh loop
dataset = []
for index, row in df_filtered.iterrows():
    dataset.append({
        "bulan": str(row["bulanan"]).strip()[:3].capitalize(),
        "b_pendapatan": str(int(round(float(row["Pendapatan"])))),
        "b_personil": str(int(round(float(row["Personil"])))),
        "b_dinas": str(int(round(float(row["Perjalanan Dinas"])))),
        "b_perlengkapan": str(int(round(float(row["Perlengkapan Kerja"])))),
        "b_kerjasama": str(int(round(float(row["Kerjasama"])))),
        "b_fasilitas": str(int(round(float(row["Fasilitas Kerja"])))),
        "b_studi": str(int(round(float(row["Studi Kelayakan"])))),
        "b_jasa": "0"  # Set langsung ke string "0" agar seragam dengan data lainnya
    })

print(f"Berhasil memuat {len(dataset)} baris data untuk proyek tersebut.")

# ==========================================
# 2. INISIALISASI BROWSER
# ==========================================
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(options=chrome_options)
driver.get(address)

print("\nSilakan login dahulu di browser, lalu pastikan berada di halaman RAB.\nMelanjutkan untuk MULAI INPUT DATA OTOMATIS...")

# ==========================================
# 3. PERULANGAN OTOMATISASI UNTUK SETIAP BULAN
# ==========================================
for data in dataset:
    target_bulan = data["bulan"]
    if target_bulan == "Kum":
        continue
    
    print(f"\n==========================================")
    print(f"MULAI MEMPROSES BULAN: {target_bulan.upper()}")
    print(f"==========================================")
    
    try:
        # ---- LANGKAH A: KLIK LINK BULAN ----
        print(f"[{target_bulan}] Mencari dan mengklik link...")
        link_bulan = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='rab-bulanan']//a[text()='{target_bulan}']"))
        )
        driver.execute_script("arguments[0].click();", link_bulan)

        # ---- LANGKAH B: MENUNGGU POP-UP / MODAL ----
        print(f"[{target_bulan}] Menunggu pop-up modal RAB muncul...")
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "rabModal"))
        )

        # ---- LANGKAH C: INPUT SEMUA DATA SECARA DINAMIS ----
        # ---- LANGKAH C: INPUT SEMUA DATA SECARA DINAMIS ----
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

        # === TAMBAHAN REALISTIS 1: TRIGGER KALKULASI WEB ===
        # Tekan TAB pada kolom terakhir agar sistem web mendeteksi "pindah fokus" 
        # dan menyelesaikan kalkulasi rumusnya secara sempurna.
        print(f"[{target_bulan}] Memicu kalkulasi rumus web...")
        input_field.send_keys(Keys.TAB) 
        
        # Berikan jeda eksplisit 1.5 - 2 detik agar skrip internal web selesai bekerja
        time.sleep(1.5) 

        # ---- LANGKAH D: KLIK TOMBOL SIMPAN (VERSI AMAN) ----
        print(f"[{target_bulan}] Memastikan tombol Simpan aktif...")
        
        # Tunggu sampai tombol simpan benar-benar bisa diklik secara native (tidak tertutup/terkunci)
        tombol_simpan = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "rab-confirmation"))
        )
        
        print(f"[{target_bulan}] Mengklik tombol Simpan...")
        driver.execute_script("arguments[0].click();", tombol_simpan)

        # ---- LANGKAH E: MENUNGGU MODAL TERTUTUP ----
        print(f"[{target_bulan}] Menunggu sinkronisasi server (bisa memakan waktu)...")
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.ID, "rabModal"))
        )
        
        print(f"[{target_bulan}] DATA BERHASIL DIINPUT DAN DISIMPAN!")
        time.sleep(2) # Istirahat sejenak sebelum menembak bulan berikutnya

    except Exception as e:
        print(f"\n[⚠️ ERROR] Gagal memproses bulan {target_bulan}.")
        print(traceback.format_exc())
        
        # JIKA ERROR: Paksa tutup modal (klik Batal) agar perulangan bulan selanjutnya tidak ikut macet
        try:
            tombol_batal = driver.find_element(By.ID, "rab-cancel")
            if tombol_batal.is_displayed():
                tombol_batal.click()
                time.sleep(2)
        except:
            pass
            
        print("Melanjutkan ke data bulan berikutnya...\n")
        continue

print("\n==========================================")
print("PROSES SELESAI! Seluruh data proyek telah diinput.")
print(f"{target_proyek} & {kode_proyek}")
print("==========================================")
driver.quit()