from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src.extract import bersihkan_teks

def get_unique_exclude_skip(df):
    df_exclude_skip = df[df['link'] != 'skip']
    unique_projects = df_exclude_skip['proyek_nomor'].dropna().unique()
    unique_link = df_exclude_skip['link'].dropna().unique()
    return unique_projects, unique_link

def duplicate_link_validation(df):
    unique_projects, unique_link = get_unique_exclude_skip(df)
    message = "✅ Semua link project unik dan sesuai"
    if len(unique_projects) != len(unique_link):
        message = f"⚠️ Terdapat {len(unique_projects) - len(unique_link)} link project duplikat. Perbaiki data terlebih dahulu"
    return message

def address_link_validation(df):
    _, unique_link = get_unique_exclude_skip(df)
    message = "✅ Semua link project diawali dengan 'https://crm.ptsi.co.id/"
    invalid_links = [link for link in unique_link if not str(link).startswith('https://crm.ptsi.co.id/')]
    if invalid_links:
        message = f"⚠️ Terdapat {len(invalid_links)} link yang tidak diawali dengan 'https://crm.ptsi.co.id/'. Perbaiki data terlebih dahulu."
    return message

def portofolio_validation(driver, kode_proyek, df_filtered):
    pesan_mismatch = ""
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
                pesan_mismatch = f"⚠️ Mismatch Portofolio - Web: '{portofolio_web}', Excel: '{portofolio_excel}'"
                print(pesan_mismatch)
            else:
                print(f"✅ Cocok - Portofolio Proyek {kode_proyek} sesuai antara Web dan Excel.")
        except Exception as e:
            print("⚠️ Peringatan: Elemen Unit Pengelola Portofolio tidak ditemukan di web atau tidak dapat diakses.")
            
    return pesan_mismatch

def is_already_done(target_proyek, processed_projects, list_mismatch, updated_count, mismatch_count):
    target_proyek_str = " ".join(str(target_proyek).split())
    if target_proyek_str in processed_projects:
        info_done = processed_projects[target_proyek_str]
        print(f"\n[proyek_done] ⏩ Melewati proyek {target_proyek} (Sudah diproses di proyek_done)")
        if info_done and "Mismatch Portofolio" in info_done:
            print(f"   {info_done}")
            list_mismatch.append(f"Proyek: {target_proyek} | {info_done}")
            mismatch_count += 1
            
        updated_count += 1
        return True
    return False