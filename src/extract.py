import time
from selenium.webdriver.common.by import By

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

def formated_number(number):
    return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def extract_kode_proyek(input_link):
    if "view/" in input_link:
        kode_proyek = input_link.split("view/")[-1].strip()
        # Membersihkan jika bagian anchor misal #rab atau #rkap terbawa
        if "#" in kode_proyek:
            kode_proyek = kode_proyek.split("#")[0]
    else:
        kode_proyek = input_link.strip()  # Fallback jika Excel hanya berisi kode angka
    return kode_proyek


def extract_proyek_rkap_crm(driver):    
    proyek_CRM = "-"
    rkap_proyek_CRM = "-"
    try:
        # Membaca teks meskipun elemen tersebut memiliki atribut display:none di HTML (get_attribute("textContent"))
        crm_project_element = driver.find_element(By.XPATH, "//label[@for='nama_potensial']/following-sibling::div/p[@class='value']")
        proyek_CRM = crm_project_element.get_attribute("textContent").strip()
        
        # Jika isinya hanya '-' atau tersembunyi, fallback/gunakan Nama id proyek
        if proyek_CRM == "-" or not proyek_CRM:
            crm_project_element_alt = driver.find_element(By.XPATH, "//label[@for='potential_id']/following-sibling::div/p[@class='value']")
            proyek_CRM = crm_project_element_alt.get_attribute("textContent").strip()
        
        crm_rkap_element = driver.find_element(By.XPATH, "//label[@for='estimasi_nilai_kontrak']/following-sibling::div/p[@class='value']")
        rkap_proyek_CRM = crm_rkap_element.get_attribute("textContent").strip()

    except Exception as e:
        proyek_CRM = "Tidak ditemukan"
        rkap_proyek_CRM = "Tidak ditemukan"
    
    return proyek_CRM, rkap_proyek_CRM



