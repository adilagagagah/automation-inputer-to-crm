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
# 1. SIMULASI DATA EXCEL (Bisa diganti pandas)
# ==========================================
# Kita buat struktur data yang mencocokkan "Bulan" dengan "Data Input"
target_bulan = "Apr"  # Variabel Utama 1: Link yang mau diklik
data_personil = "382474338".strip()  # Variabel Utama 2: Data dari Excel


# ==========================================
# 2. INISIALISASI BROWSER
# ==========================================
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://crm.ptsi.co.id/index.php/project/rkap/view/22170#rab")

input("Silakan login dahulu di browser, lalu tekan Enter di sini untuk mulai otomatisasi...")

try:
    # ==========================================
    # 3. PROSES KLIK LINK BULAN
    # ==========================================
    # Menemukan link <a> berdasarkan teks bulannya (misal: "Mar")
    # Dipersempit hanya mencari di dalam tabel id="rab-bulanan" berdasarkan HTML
    print(f"Mencari dan mengklik link bulan: {target_bulan}...")
    link_bulan = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//div[@id='rab-bulanan']//a[text()='{target_bulan}']"))
    )
    # Gunakan Javascript Click agar tidak gagal jika elemen tertutup elemen UI lain
    driver.execute_script("arguments[0].click();", link_bulan)

    # ==========================================
    # 4. MENUNGGU POP-UP / MODAL MUNCUL (KRUSIAL!)
    # ==========================================
    # Program akan menunggu sampai elemen modal dengan ID 'rabModal' benar-benar terlihat di layar (style="display: block;")
    print("Menunggu pop-up modal RAB muncul...")
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "rabModal"))
    )

    # ==========================================
    # 5. INPUT DATA KE DALAM FORM POP-UP
    # ==========================================
    # Cari input personil berdasarkan ID-nya yang unik: 'b_personil'
    input_personil = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "b_personil"))
    )
    
    print(f"Menginput data personil: {data_personil}")
    
    # Gunakan trik Ctrl+A lalu hapus (lebih efektif dari .clear() untuk form uang)
    input_personil.click()
    input_personil.send_keys(Keys.CONTROL + "a")
    input_personil.send_keys(Keys.BACKSPACE)
    input_personil.send_keys(data_personil)
    
    # --- Opsional: Input field lain jika dibutuhkan ---
    # driver.find_element(By.ID, "b_personil").send_keys("5000000")
    # driver.find_element(By.ID, "b_dinas").send_keys("2000000")

    time.sleep(1) # Jeda aman setengah detik sebelum klik simpan

    # ==========================================
    # 6. KLIK TOMBOL SIMPAN
    # ==========================================
    # Berdasarkan HTML Anda, tombol simpan memiliki ID 'rab-confirmation'
    tombol_simpan = driver.find_element(By.ID, "rab-confirmation")
    print("Mengklik tombol Simpan...")
    tombol_simpan.click()

    # Tunggu beberapa detik untuk memastikan data terkirim ke server sebelum lanjut ke data berikutnya
    time.sleep(3)
    print("Proses berhasil!")

except Exception as e:
    print("\n--- TERJADI KESALAHAN ---")
    print(traceback.format_exc())

finally:
    driver.quit()