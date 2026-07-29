import re
import pandas as pd
from pipeline.path import WAREHOUSE_DIR
from logger import logger

def check_zero_columns(cleaned_tables: dict[str, pd.DataFrame] | None = None) -> None:
    logger.info("Memulai pengecekan nilai dengan akhiran '.0'.")
    dot_zero_pattern = re.compile(r"^-?\d+\.0$")
    any_found = False
    if cleaned_tables is not None:
        table_names = list(cleaned_tables.keys())
    else:
        table_names = [
            p.stem.replace("_clean", "")
            for p in WAREHOUSE_DIR.glob("*_clean.csv")]
    for name in table_names:
        file_path = WAREHOUSE_DIR / f"{name}_clean.csv"
        if not file_path.exists():
            logger.warning(f"{file_path.name} tidak ditemukan.")
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
            logger.warning(f"{name}_clean.csv masih memiliki nilai '.0'.")
            for col, jumlah, contoh in bermasalah:
                logger.warning(
                    f"{name}.{col} -> {jumlah} baris | contoh: {contoh}")
        else:
            logger.info(f"{name}_clean.csv bersih.")

    if not any_found:
        logger.info("Semua file bersih dari nilai '.0'.")
    else:
        logger.warning("Masih ditemukan nilai '.0' pada beberapa file.")
