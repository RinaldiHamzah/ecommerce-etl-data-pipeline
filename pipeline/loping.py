import re
import pandas as pd

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    new_cols = []
    for col in df.columns:
        c = str(col).strip().lower()
        c = re.sub(r"\s+", "_", c)
        c = re.sub(r"[^0-9a-z_]", "", c)
        new_cols.append(c)
    df.columns = new_cols
    return df

def parse_date(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", dayfirst=True, format="mixed")
    return parsed.dt.strftime("%Y-%m-%d")

def parse_date_iso(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", format="mixed")
    return parsed.dt.strftime("%Y-%m-%d")
