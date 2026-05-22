import pandas as pd

# ==========================================
# 1. MEMBACA DATA ASLI DARI EXCEL
# ==========================================
# Membaca file excel. Pastikan Anda sudah install pandas & openpyxl 
# dengan perintah: pip install pandas openpyxl
df = pd.read_excel('SIBPP_RKAP.xlsx')

df_filtered = df[df['nomor'].astype(str).str.contains('12', na=False)]

print(df_filtered["proyek_1"])
# proyek_ke_12_asli = df['proyek_2'].iloc[12]
# print(f"Nama proyek ke-12 di data asli: {proyek_ke_12_asli}")
# print(df.columns)

# # Memfilter baris di mana kolom 'proyek_2' mengandung nama proyek target
# target_proyek = "Advance NDT ( ECT & IRIS & PAUT) 340"
# df_filtered = df[df['proyek_2'].astype(str).str.contains(target_proyek, case=False, na=False)]

# # Mengonversi data Excel menjadi struktur list dictionary yang siap dibaca oleh loop
# dataset = []
# for index, row in df_filtered.iterrows():
#     dataset.append({
#         "bulan": str(row["bulanan"]).strip()[:3].capitalize(),
#         "b_pendapatan": str(int(round(float(row["Pendapatan"])))),
#         "b_personil": str(int(round(float(row["Personil"])))),
#         "b_dinas": str(int(round(float(row["Perjalanan Dinas"])))),
#         "b_perlengkapan": str(int(round(float(row["Perlengkapan Kerja"])))),
#         "b_kerjasama": str(int(round(float(row["Kerjasama"])))),
#         "b_fasilitas": str(int(round(float(row["Fasilitas Kerja"])))),
#         "b_studi": str(int(round(float(row["Studi Kelayakan"])))),
#         "b_jasa": str(int(0))
#     })

# print(dataset)