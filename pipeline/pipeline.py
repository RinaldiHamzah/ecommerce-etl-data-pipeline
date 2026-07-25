from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = ROOT / "database" / "ecommerce.db"
RAW_FILES = {
    "customers": RAW_DIR / "raw_customers.csv",
    "inventory": RAW_DIR / "raw_inventory.csv",
    "order_promo": RAW_DIR / "raw_order_promo.csv",
    "orders": RAW_DIR / "raw_orders.csv",
    "payments": RAW_DIR / "raw_payments.csv",
    "products": RAW_DIR / "raw_products.csv",
    "promo": RAW_DIR / "raw_promo.csv",
    "returns": RAW_DIR / "raw_returns.csv",
    "suppliers": RAW_DIR / "raw_suppliers.csv",}

def load_raw_data(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    
    if "customer_name" in df.columns:
        df["customer_name"] = df["customer_name"].astype(str).str.strip().str.title()
        
    if "phone_number" in df.columns:
        df["phone_number"] = df["phone_number"].astype(str).str.replace(r'\.0$', '', regex=True)
        df["phone_number"] = df["phone_number"].apply(lambda x: '0' + x if pd.notna(x) and x != 'nan' and x.startswith('8') else x)
        df["phone_number"] = df["phone_number"].replace('nan', np.nan)
        
    if "join_date" in df.columns:
        df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce", format="mixed")
        
    if "kota" in df.columns:
        df["kota"] = df["kota"].astype(str).str.strip().str.title()
        df["kota"] = df["kota"].replace('Nan', np.nan)
        
    if "segment" in df.columns:
        df["segment"] = df["segment"].astype(str).str.strip().str.title()
        df["segment"] = df["segment"].replace('Nan', np.nan)
        
    if "gender" in df.columns:
        gender_map = {'Laki-Laki': 'L', 'Laki-laki': 'L', 'M': 'L', 'L': 'L', 'Perempuan': 'P', 'F': 'P', 'P': 'P', 'nan': np.nan, 'None': np.nan, '': np.nan}
        df["gender"] = df["gender"].astype(str).str.strip().str.title().replace(gender_map)
        df["gender"] = df["gender"].replace('Nan', np.nan)
        
    if "customer_id" in df.columns:
        df = df.dropna(subset=["customer_id"])
        df = df[df["customer_id"].astype(str).str.strip() != ""]
        df = df.drop_duplicates(subset=["customer_id"], keep="last")
        
    return df
def clean_inventory(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    
    if "stok_tersedia" in df.columns:
        df["stok_tersedia"] = pd.to_numeric(df["stok_tersedia"], errors="coerce")
        df.loc[df["stok_tersedia"] < 0, "stok_tersedia"] = 0
        df["stok_tersedia"] = df["stok_tersedia"].fillna(0).astype(int)
        
    if "last_update" in df.columns:
        df["last_update"] = pd.to_datetime(df["last_update"], errors="coerce", format="mixed")
        
    if "gudang" in df.columns:
        df["gudang"] = df["gudang"].astype(str).str.strip().str.title()
        
    if "product_id" in df.columns:
        df = df.dropna(subset=["product_id"])
        df = df.drop_duplicates(subset=["product_id", "gudang"], keep="last")
        
    return df
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df.loc[df["quantity"] < 0, "quantity"] = np.nan
        df["quantity"] = df["quantity"].fillna(1).astype(int)
        
    if "total_harga" in df.columns:
        df["total_harga"] = pd.to_numeric(df["total_harga"], errors="coerce")
        df.loc[df["total_harga"] < 0, "total_harga"] = np.nan
        df["total_harga"] = df["total_harga"].fillna(df["total_harga"].median() if not df["total_harga"].isna().all() else 0)
        
    if "tanggal_order" in df.columns:
        df["tanggal_order"] = pd.to_datetime(df["tanggal_order"], errors="coerce", format="mixed")
        
    if "kota" in df.columns:
        df["kota"] = df["kota"].astype(str).str.strip().str.title()
        df["kota"] = df["kota"].replace('Nan', np.nan)
        
    if "channel" in df.columns:
        df["channel"] = df["channel"].astype(str).str.strip().str.upper()
        
    if "status" in df.columns:
        df["status"] = df["status"].astype(str).str.strip().str.title()
        
    if "order_id" in df.columns:
        df = df.dropna(subset=["order_id"])
        df = df.drop_duplicates(subset=["order_id"], keep="last")
        
    return df
def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    
    if "jumlah_bayar" in df.columns:
        df["jumlah_bayar"] = pd.to_numeric(df["jumlah_bayar"], errors="coerce")
        df.loc[df["jumlah_bayar"] < 0, "jumlah_bayar"] = np.nan
        df["jumlah_bayar"] = df["jumlah_bayar"].fillna(df["jumlah_bayar"].median() if not df["jumlah_bayar"].isna().all() else 0)
        
    if "biaya_admin" in df.columns:
        df["biaya_admin"] = pd.to_numeric(df["biaya_admin"], errors="coerce")
        df.loc[df["biaya_admin"] < 0, "biaya_admin"] = np.nan
        df["biaya_admin"] = df["biaya_admin"].fillna(0)
        
    if "tanggal_bayar" in df.columns:
        df["tanggal_bayar"] = pd.to_datetime(df["tanggal_bayar"], errors="coerce", format="mixed")
        
    if "metode_pembayaran" in df.columns:
        df["metode_pembayaran"] = df["metode_pembayaran"].astype(str).str.strip().str.title()
        
    if "status_pembayaran" in df.columns:
        df["status_pembayaran"] = df["status_pembayaran"].astype(str).str.strip().str.title()
        
    if "payment_id" in df.columns:
        df = df.dropna(subset=["payment_id"])
        df = df.drop_duplicates(subset=["payment_id"], keep="last")
        
    return df
def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    
    if "harga_satuan" in df.columns:
        df["harga_satuan"] = pd.to_numeric(df["harga_satuan"], errors="coerce")
        df.loc[df["harga_satuan"] < 0, "harga_satuan"] = np.nan
        df["harga_satuan"] = df["harga_satuan"].fillna(df["harga_satuan"].median() if not df["harga_satuan"].isna().all() else 0)
        
    if "kategori" in df.columns:
        df["kategori"] = df["kategori"].astype(str).str.strip().str.title()
        
    if "product_id" in df.columns:
        df = df.dropna(subset=["product_id"])
        df = df.drop_duplicates(subset=["product_id"], keep="last")
        
    return df
def clean_promo(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    
    if "nilai_diskon" in df.columns:
        df["nilai_diskon"] = pd.to_numeric(df["nilai_diskon"], errors="coerce")
        df.loc[df["nilai_diskon"] < 0, "nilai_diskon"] = 0
        df["nilai_diskon"] = df["nilai_diskon"].fillna(0)
        
    if "tanggal_mulai" in df.columns:
        df["tanggal_mulai"] = pd.to_datetime(df["tanggal_mulai"], errors="coerce", format="mixed")
        
    if "tanggal_selesai" in df.columns:
        df["tanggal_selesai"] = pd.to_datetime(df["tanggal_selesai"], errors="coerce", format="mixed")
        
    if "nama_promo" in df.columns:
        df["nama_promo"] = df["nama_promo"].astype(str).str.strip().str.title()
        
    if "status" in df.columns:
        df["status"] = df["status"].astype(str).str.strip().str.lower()
        
    if "promo_code" in df.columns:
        df = df.dropna(subset=["promo_code"])
        df = df.drop_duplicates(subset=["promo_code"], keep="last")
        
    return df
def clean_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    
    if "quantity_return" in df.columns:
        df["quantity_return"] = pd.to_numeric(df["quantity_return"], errors="coerce")
        df.loc[df["quantity_return"] < 0, "quantity_return"] = 0
        df["quantity_return"] = df["quantity_return"].fillna(0).astype(int)
        
    if "refund_amount" in df.columns:
        df["refund_amount"] = pd.to_numeric(df["refund_amount"], errors="coerce")
        df.loc[df["refund_amount"] < 0, "refund_amount"] = 0
        df["refund_amount"] = df["refund_amount"].fillna(0)
        
    if "tanggal_return" in df.columns:
        df["tanggal_return"] = pd.to_datetime(df["tanggal_return"], errors="coerce", format="mixed")
        
    if "alasan_return" in df.columns:
        df["alasan_return"] = df["alasan_return"].astype(str).str.strip().str.title()
        
    if "status_return" in df.columns:
        df["status_return"] = df["status_return"].astype(str).str.strip().str.title()
        
    if "return_id" in df.columns:
        df = df.dropna(subset=["return_id"])
        df = df.drop_duplicates(subset=["return_id"], keep="last")
        
    return df
def clean_suppliers(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    
    if "kontak" in df.columns:
        df["kontak"] = df["kontak"].fillna("021-2455342")
        
    if "kota" in df.columns:
        df["kota"] = df["kota"].fillna("").astype(str).str.strip().str.title()
        df["kota"] = df["kota"].replace("Nan", np.nan)
        df["kota"] = df["kota"].replace("", np.nan)
        
    if "lead_time_hari" in df.columns:
        df["lead_time_hari"] = pd.to_numeric(df["lead_time_hari"], errors="coerce")
        df.loc[df["lead_time_hari"] < 0, "lead_time_hari"] = np.nan
        
        # Fill based on mean of kota
        if "kota" in df.columns:
            mean_per_kota = df.groupby("kota")["lead_time_hari"].transform("mean")
            df["lead_time_hari"] = df["lead_time_hari"].fillna(mean_per_kota)
            
        df["lead_time_hari"] = df["lead_time_hari"].fillna(0).astype(int)
        
    if "nama_supplier" in df.columns:
        df["nama_supplier"] = df["nama_supplier"].astype(str).str.strip().str.title()
        
    if "supplier_id" in df.columns:
        df = df.dropna(subset=["supplier_id"])
        df = df.drop_duplicates(subset=["supplier_id"], keep="last")
        
    return df
def clean_order_promo(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    if "order_id" in df.columns and "promo_code" in df.columns:
        df = df.dropna(subset=["order_id", "promo_code"])
        df = df.drop_duplicates(subset=["order_id", "promo_code"], keep="last")
    return df
def write_processed_files(cleaned_tables: dict[str, pd.DataFrame]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in cleaned_tables.items():
        output_path = PROCESSED_DIR / f"{name}_clean.csv"
        df.to_csv(output_path, index=False)
def load_to_sqlite(cleaned_tables: dict[str, pd.DataFrame]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}")
    for name, df in cleaned_tables.items():
        df.to_sql(name, engine, if_exists="replace", index=False)
def run_pipeline() -> None:
    cleaned_tables = {}
    cleaned_tables["customers"] = clean_customers(load_raw_data(RAW_FILES["customers"]))
    cleaned_tables["inventory"] = clean_inventory(load_raw_data(RAW_FILES["inventory"]))
    cleaned_tables["order_promo"] = clean_order_promo(load_raw_data(RAW_FILES["order_promo"]))
    cleaned_tables["orders"] = clean_orders(load_raw_data(RAW_FILES["orders"]))
    cleaned_tables["payments"] = clean_payments(load_raw_data(RAW_FILES["payments"]))
    cleaned_tables["products"] = clean_products(load_raw_data(RAW_FILES["products"]))
    cleaned_tables["promo"] = clean_promo(load_raw_data(RAW_FILES["promo"]))
    cleaned_tables["returns"] = clean_returns(load_raw_data(RAW_FILES["returns"]))
    cleaned_tables["suppliers"] = clean_suppliers(load_raw_data(RAW_FILES["suppliers"]))
    write_processed_files(cleaned_tables)
    load_to_sqlite(cleaned_tables)
    print(f"Pipeline selesai. Data disimpan di {PROCESSED_DIR} dan {DB_PATH}")
if __name__ == "__main__":
    run_pipeline()
