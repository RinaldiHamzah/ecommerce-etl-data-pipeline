#input_ouput.py
from pathlib import Path
import pandas as pd
from pipeline.path import WAREHOUSE_DIR

def load_raw_data(file_path: Path) -> pd.DataFrame:
    return pd.read_csv(file_path)

def write_processed_files(cleaned_tables: dict[str, pd.DataFrame]) -> None:
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in cleaned_tables.items():
        output_path = WAREHOUSE_DIR / f"{name}_clean.csv"
        df.to_csv(output_path, index=False)
