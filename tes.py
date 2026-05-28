import pandas as pd

# ==========================================
# 1. MEMBACA DATA ASLI DARI EXCEL
# ==========================================
# Membaca file excel. Pastikan Anda sudah install pandas & openpyxl 
# dengan perintah: pip install pandas openpyxl

df = pd.read_excel('private/REAL_RKAP.xlsx', sheet_name='GNI')


# # Memfilter baris di mana kolom 'proyek_nomor' mengandung nama proyek target
target_proyek = "Advance NDT ( ECT & IRIS & PAUT) 340"
df_filtered = df[df['proyek_nomor'].astype(str).str.contains(target_proyek, case=False, na=False, regex=False)]

# # Mengonversi data Excel menjadi struktur list dictionary yang siap dibaca oleh loop
dataset = []
for index, row in df_filtered.iterrows():
    dataset.append({
        "bulan": str(row["bulan"]).strip()[:3].capitalize(),
        "b_pendapatan": str(int(round(float(row["Pendapatan"])))),
        "b_personil": str(int(round(float(row["Personil"])))),
        "b_dinas": str(int(round(float(row["Perjalanan Dinas"])))),
        "b_perlengkapan": str(int(round(float(row["Perlengkapan Kerja"])))),
        "b_kerjasama": str(int(round(float(row["Kerjasama"])))),
        "b_fasilitas": str(int(round(float(row["Fasilitas Kerja"])))),
        "b_studi": str(int(round(float(row["Studi Kelayakan"])))),
        "b_jasa": str(int(0))
    })

# print(dataset)
# print(df.columns)

df_exclude_skip = df[df['link'] != 'skip']
unique_projects = df_exclude_skip['proyek_nomor'].dropna().unique()
unique_link = df_exclude_skip['link'].dropna().unique()
print(len(unique_projects))
print(len(unique_link))