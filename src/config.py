# config.py
import os
import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH_X86 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = "9222"
USER_DATA = r"C:\chrome-debug"
BASE_URL = "https://crm.ptsi.co.id/index.php"

def inisialisasi_chrome():
    """Membuka Chrome dalam mode debugging dan mengembalikan objek WebDriver."""
    print("\n[System] Mencoba membuka Google Chrome dalam Mode Debugging...")
    
    chrome_executable = CHROME_PATH
    if not os.path.exists(chrome_executable) and os.path.exists(CHROME_PATH_X86):
        chrome_executable = CHROME_PATH_X86
        
    try:
        subprocess.Popen([
            chrome_executable, 
            f"--remote-debugging-port={PORT}", 
            f"--user-data-dir={USER_DATA}"
        ])
        time.sleep(2) 
        print("[System] Google Chrome berhasil dibuka.")
    except Exception as e:
        print(f"[⚠️ ERROR] Gagal membuka Chrome secara otomatis. Pastikan jalur path benar: {e}")
        print("Mencoba melanjutkan koneksi port jika Chrome sudah terbuka manual...")
        sys.exit()

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{PORT}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(BASE_URL)
    return driver