import re
import pandas as pd
from pipeline.path import WAREHOUSE_DIR

def check_zero_columns(cleaned_tables: dict[str, pd.DataFrame] | None = None) -> None:
    dot_zero_pattern = re.compile(r"^-?\d+\.0$")
    any_found = False

    if cleaned_tables is not None:
        table_names = list(cleaned_tables.keys())
    else:
        table_names = [p.stem.replace("_clean", "") for p in WAREHOUSE_DIR.glob("*_clean.csv")]

    for name in table_names:
        file_path = WAREHOUSE_DIR / f"{name}_clean.csv"
        if not file_path.exists():
            continue

        df_check = pd.read_csv(file_path, dtype=str)
        bermasalah = []
        for col in df_check.columns:
            nilai_non_null = df_check[col].dropna()
            if len(nilai_non_null) == 0:
                continue
            cocok = nilai_non_null.astype(str).str.match(dot_zero_pattern)
            if cocok.any():
                jumlah = cocok.sum()
                contoh = nilai_non_null[cocok].iloc[0]
                bermasalah.append((col, jumlah, contoh))

        if bermasalah:
            any_found = True
            print(f"{name}_clean.csv -- ditemukan kolom dengan '.0':")
            for col, jumlah, contoh in bermasalah:
                print(f"     - {col}: {jumlah} baris (contoh nilai: '{contoh}')")
        else:
            print(f"{name}_clean.csv -- aman, tidak ada '.0'")

    if not any_found:
        print("\nSemua file bersih dari sisa '.0'.")
    else:
        print("\nAda file yang masih bermasalah -- cek fungsi clean_<nama_tabel> untuk kolom di atas,")
        print("pastikan ada .astype(int) SETELAH semua nilai NaN ditangani (dropna/fillna).")
