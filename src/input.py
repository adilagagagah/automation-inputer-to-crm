import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def create_dataset_per_proyek(df_filtered):
    dataset_per_proyek = []
    for index, row in df_filtered.iterrows():
        dataset_per_proyek.append({
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
    return dataset_per_proyek

def input_data_proyek(driver, dataset_per_proyek):
    dataset_per_proyek = dataset_per_proyek[1:]
    for bulan in dataset_per_proyek:
        target_bulan = bulan["bulan"][:3].capitalize()    
        while True:
            try:
                # print(f"[{target_bulan}] Mencari dan mengklik link...")
                elemen_bulan = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@id='rab-bulanan']//a[contains(text(), '{target_bulan}')]"))
                )

                driver.execute_script("arguments[0].click();", elemen_bulan)

                # print(f"[{target_bulan}] Menunggu pop-up modal RAB muncul...")
                WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.ID, "rabModal"))
                )

                for id_elemen, nilai_input in bulan.items():
                    if id_elemen == "bulan":
                        continue
                        
                    # print(f"[{target_bulan}] Mengisi {id_elemen} -> {nilai_input}")
                    
                    input_field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, id_elemen))
                    )
                    
                    # Dapatkan nilai saat ini pada form dan hilangkan format angka (titik/koma) jika ada
                    current_value = input_field.get_attribute("value")
                    cleaned_current_value = current_value.replace(".", "").replace(",", "").strip() if current_value else ""
                    
                    # Cek apakah form kosong & nilai yang diinput "0", ATAU nilai di form sudah sama dengan nilai_input
                    if (cleaned_current_value == "" and str(nilai_input) == "0") or (cleaned_current_value == str(nilai_input)):
                        continue
                    
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
                
                print(f"✅ DATA [{bulan["bulan"].capitalize()}] BERHASIL DIINPUT DAN DISIMPAN!")
                time.sleep(1)
                break  # Berhasil, memecah (keluar) dari loop `while` untuk lanjut ke iterasi `for` berikutnya

            except Exception as e:
                # JIKA ERROR (misal elemen tidak ditemukan / timeout):
                print(f"\n[⚠️ ERROR] Gagal memproses bulan {target_bulan}.")
                print("Merefresh halaman dan mencoba input ulang...")
                driver.refresh()
                time.sleep(1) # Tunggu sejenak setelah refresh agar script siap membaca ulang web

def input_rab_kumulatif(driver, address, dataset_per_proyek):
    data_kumulatif = dataset_per_proyek[0]
    while True:
        try:
            address_rkap = f"{address}#rkap"
            driver.get(address_rkap)
            time.sleep(2)
            
            is_changed = False
            
            estimasi_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "estimasi_nilai_kontrak"))
            )
            
            current_value = estimasi_input.get_attribute("value")
            cleaned_current_value = current_value.replace(".", "").replace(",", "").strip() if current_value else ""
            target_value = str(data_kumulatif["b_pendapatan"])
            
            if cleaned_current_value != target_value:
                estimasi_input.click()
                estimasi_input.send_keys(Keys.CONTROL + "a")
                estimasi_input.send_keys(Keys.BACKSPACE)
                estimasi_input.send_keys(target_value)
                time.sleep(0.2)
                is_changed = True

            address_rab = f"{address}#rab"
            driver.get(address_rab)
            time.sleep(2)
            for id_elemen, nilai_input in data_kumulatif.items():
                if id_elemen == "bulan" or id_elemen == "b_pendapatan":
                    continue

                input_field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, id_elemen))
                    )
                    
                # Dapatkan nilai saat ini pada form dan hilangkan format angka (titik/koma) jika ada
                current_value = input_field.get_attribute("value")
                cleaned_current_value = current_value.replace(".", "").replace(",", "").strip() if current_value else ""
                
                # Cek apakah form kosong & nilai yang diinput "0", ATAU nilai di form sudah sama dengan nilai_input
                if (cleaned_current_value == "" and str(nilai_input) == "0") or (cleaned_current_value == str(nilai_input)):
                    continue
                
                input_field.click()
                input_field.send_keys(Keys.CONTROL + "a")
                input_field.send_keys(Keys.BACKSPACE)
                input_field.send_keys(str(nilai_input))
                time.sleep(0.2)
                is_changed = True

            if is_changed:
                estimasi_input.send_keys(Keys.TAB) 
                time.sleep(1) 
                tombol_simpan = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "btn-save"))
                )
                driver.execute_script("arguments[0].click();", tombol_simpan)
                print(f"✅ DATA [KUMULATIF] BERHASIL DIUPDATE DAN DISIMPAN!")
                time.sleep(2)
            else:
                print(f"✅ DATA [KUMULATIF] SUDAH SESUAI, TIDAK ADA PERUBAHAN.")
        
        except Exception as e:
            # JIKA ERROR (misal elemen tidak ditemukan / timeout):
            print(f"\n[⚠️ ERROR] Gagal memproses nilai kumulatif.")
            print("Merefresh halaman dan mencoba input ulang...")
            driver.refresh()
            time.sleep(1) # Tunggu sejenak setelah refresh agar script siap membaca ulang web
