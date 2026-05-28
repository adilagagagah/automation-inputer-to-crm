import sys

def get_menu(proyek_done_file, processed_projects):
    with open(proyek_done_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                if " | " in line:
                    parts = line.split(" | ", 1)
                    processed_projects[parts[0]] = parts[1]
                else:
                    processed_projects[line] = ""
    
    if processed_projects:
        print(f"\n[proyek_done] Ditemukan {len(processed_projects)} proyek yang sudah selesai diproses sebelumnya.")
        print("0. Keluar dari program.")
        print("1. Lanjutkan dari proyek yang belum di input (skip/blank).")
        print("2. Mulai dari awal (Hapus proyek_done).")
        while True:
            pilihan = input("Masukkan pilihan (0/1/2): ")
            if pilihan == '1':
                print("⏩ Melanjutkan dari proyek yang belum di input...")
                break
            elif pilihan == '2':
                print("🔄 Mulai dari awal. proyek_done dibersihkan...")
                processed_projects = {}
                open(proyek_done_file, "w").close() # Kosongkan file proyek_done
                break
            elif pilihan == '0':
                sys.exit(1)
            else:
                print("⚠️ Pilihan tidak valid. Silakan masukkan 0, 1, atau 2")

def catat_proyek_done(proyek_done_file, proyek, info=""):
    with open(proyek_done_file, "a", encoding="utf-8") as f:
        if info:
            f.write(f"{proyek} | {info}\n")
        else:
            f.write(str(proyek) + "\n")

def create_summary_log(excel_file, excel_sheet, start_time, end_time, 
                       total_duration_str, total_projects, 
                       updated_count, skipped_count, mismatch_count, 
                       list_skipped, list_mismatch, list_error):
    
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
    return summary_text