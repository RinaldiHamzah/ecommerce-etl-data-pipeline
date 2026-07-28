import pandas as pd
import numpy as np
import random
import re

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Seragamkan nama kolom: lowercase, strip, spasi -> underscore."""
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
    """
    Parsing tanggal campuran (dd/mm/yyyy, ISO, 'Mon dd, yyyy', dst) dengan
    dayfirst=True, lalu dikembalikan sebagai string tanggal 'YYYY-MM-DD'
    tanpa komponen jam.
    """
    parsed = pd.to_datetime(series, errors="coerce", dayfirst=True, format="mixed")
    return parsed.dt.strftime("%Y-%m-%d")

def parse_date_iso(series: pd.Series) -> pd.Series:
    """
    Parsing tanggal yang sudah konsisten format ISO (YYYY-MM-DD), TANPA
    dayfirst, supaya tidak salah tafsir tanggal yang day & month-nya
    sama-sama <=12 (mis. '2024-03-10' jangan sampai jadi 10 Maret -> 3 Okt).
    """
    parsed = pd.to_datetime(series, errors="coerce", format="mixed")
    return parsed.dt.strftime("%Y-%m-%d")


def filter_existing_references(
    df: pd.DataFrame,
    column: str,
    reference_df: pd.DataFrame,
    reference_column: str,
) -> pd.DataFrame:
    if column not in df.columns or reference_column not in reference_df.columns:
        return df

    valid_values = set(reference_df[reference_column].dropna().astype(str).str.strip().str.upper())
    return df[df[column].astype(str).str.strip().str.upper().isin(valid_values)]

# ---------------------------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------------------------
def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    if "product_id" in df.columns:
        df["product_id"] = df["product_id"].astype(str).str.strip().str.upper()
        df = df.dropna(subset=["product_id"])
        df = df[~df["product_id"].isin(["", "NAN"])]

    if "product_name" in df.columns:
        # Tidak di-title-case supaya akronim seperti "SPF50" / "EDT" tidak
        # ikut berubah jadi "Spf50" / "Edt".
        df["product_name"] = df["product_name"].astype(str).str.strip()
        df["product_name"] = df["product_name"].str.replace(r"\s+", " ", regex=True)

    if "kategori" in df.columns:
        df["kategori"] = df["kategori"].astype(str).str.strip().str.title()

    if "harga_satuan" in df.columns:
        df["harga_satuan"] = pd.to_numeric(df["harga_satuan"], errors="coerce")
        df.loc[df["harga_satuan"] <= 0, "harga_satuan"] = np.nan
        df["harga_satuan"] = df["harga_satuan"].fillna(df["harga_satuan"].median()).astype(int)

    df = df.drop_duplicates(subset=["product_id"], keep="last")
    df = df.sort_values(by="product_id").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# PROMO
# ---------------------------------------------------------------------------
def clean_promo(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    if "promo_code" in df.columns:
        df["promo_code"] = df["promo_code"].astype(str).str.strip().str.upper()
        df = df.dropna(subset=["promo_code"])
        df = df[df["promo_code"] != ""]

    if "nama_promo" in df.columns:
        df["nama_promo"] = df["nama_promo"].astype(str).str.strip().str.title()

    if "tipe_diskon" in df.columns:
        df["tipe_diskon"] = df["tipe_diskon"].astype(str).str.strip().str.title()
        valid_type = ["Fixed", "Percentage"]
        df.loc[~df["tipe_diskon"].isin(valid_type), "tipe_diskon"] = np.nan

    if "nilai_diskon" in df.columns:
        df["nilai_diskon"] = pd.to_numeric(df["nilai_diskon"], errors="coerce")
        fixed = df["tipe_diskon"] == "Fixed"
        df.loc[fixed & (df["nilai_diskon"] <= 0), "nilai_diskon"] = np.nan
        percentage = df["tipe_diskon"] == "Percentage"
        df.loc[percentage & ((df["nilai_diskon"] <= 0) | (df["nilai_diskon"] > 100)), "nilai_diskon"] = np.nan
        df["nilai_diskon"] = df.groupby("tipe_diskon")["nilai_diskon"].transform(lambda x: x.fillna(round(x.mean())))
        df["nilai_diskon"] = df["nilai_diskon"].astype(int)

    if "tanggal_mulai" in df.columns:
        df["tanggal_mulai"] = parse_date_iso(df["tanggal_mulai"])
    if "tanggal_selesai" in df.columns:
        df["tanggal_selesai"] = parse_date_iso(df["tanggal_selesai"])
    if {"tanggal_mulai", "tanggal_selesai"}.issubset(df.columns):
        mask = pd.to_datetime(df["tanggal_selesai"]) < pd.to_datetime(df["tanggal_mulai"])
        df.loc[mask, "tanggal_selesai"] = np.nan

    if "status" in df.columns:
        df["status"] = df["status"].astype(str).str.strip().str.title()
        valid_status = ["Active", "Expired"]
        df.loc[~df["status"].isin(valid_status), "status"] = np.nan

    df = df.drop_duplicates(subset="promo_code", keep="last")
    if "tanggal_mulai" in df.columns:
        df = df.sort_values(by="tanggal_mulai")
    df = df.reset_index(drop=True)
    return df
# Kode ini masih kurang pada kolom nilai_diskon yang masih ada .0 nilainya 

# ---------------------------------------------------------------------------
# SUPPLIERS
# ---------------------------------------------------------------------------
def clean_suppliers(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    if "supplier_id" in df.columns:
        df["supplier_id"] = df["supplier_id"].astype(str).str.strip().str.upper()
        df = df.dropna(subset=["supplier_id"])
        df = df[df["supplier_id"] != ""]

    if "product_id" in df.columns:
        df["product_id"] = df["product_id"].astype(str).str.strip().str.upper()

    if "nama_supplier" in df.columns:
        df["nama_supplier"] = df["nama_supplier"].astype(str).str.strip()

    if "kontak" in df.columns:
        df["kontak"] = df["kontak"].astype(str).str.strip()
        df["kontak"] = df["kontak"].replace(["", "nan", "None"], np.nan)
        df["kontak"] = df["kontak"].fillna("021-2455342")

    if "kota" in df.columns:
        df["kota"] = df["kota"].astype(str).str.strip().str.title()
        df["kota"] = df["kota"].replace(["", "Nan"], np.nan)

    if "lead_time_hari" in df.columns:
        df["lead_time_hari"] = pd.to_numeric(df["lead_time_hari"], errors="coerce")
        df.loc[df["lead_time_hari"] <= 0, "lead_time_hari"] = np.nan
        if "kota" in df.columns:
            mean_kota = df.groupby("kota")["lead_time_hari"].transform("mean")
            df["lead_time_hari"] = df["lead_time_hari"].fillna(mean_kota)
        df["lead_time_hari"] = df["lead_time_hari"].fillna(df["lead_time_hari"].median()).round().astype(int)

    df = df.drop_duplicates(subset="supplier_id", keep="last")
    df = df.sort_values(by="supplier_id").reset_index(drop=True)
    return df

# ---------------------------------------------------------------------------
# CUSTOMERS
# ---------------------------------------------------------------------------
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    if "customer_name" in df.columns:
        df["customer_name"] = df["customer_name"].astype(str).str.strip().str.title().replace("Nan", np.nan)

        # Nama kosong diisi dengan nama acak (beda-beda tiap baris), bukan
        # satu nama default yang sama untuk semua baris kosong.
        first_names = ["Budi", "Andi", "Siti", "Rina", "Dimas", "Fajar", "Nadia", "Putri", "Agus", "Indah"]
        last_names = ["Santoso", "Pratama", "Saputra", "Wijaya", "Hidayat", "Lestari", "Permata", "Kusuma", "Nugroho", "Rahman"]

        mask_name = df["customer_name"].isna()
        if mask_name.any():
            rng_name = random.Random(42)  # seeded supaya hasil konsisten tiap dijalankan ulang
            df.loc[mask_name, "customer_name"] = [
                f"{rng_name.choice(first_names)} {rng_name.choice(last_names)}" for _ in range(mask_name.sum())]

    if "customer_email" in df.columns:
        df["customer_email"] = df["customer_email"].astype(str).str.strip().str.lower().replace("nan", np.nan)
        df["customer_email"] = df["customer_email"].fillna("dummy123@email.com")

    if "phone_number" in df.columns:
        df["phone_number"] = (
            df["phone_number"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .replace(["nan", ""], np.nan))

        def format_phone(phone):
            if pd.isna(phone):
                return np.nan
            if phone.startswith("62"):
                return "+" + phone
            if phone.startswith("0"):
                return "+62" + phone[1:]
            if phone.startswith("8"):
                return "+62" + phone
            return np.nan

        df["phone_number"] = df["phone_number"].apply(format_phone)

        missing_mask = df["phone_number"].isna()
        counter = missing_mask.cumsum().astype(str).str.zfill(8)
        df.loc[missing_mask, "phone_number"] = "+62812" + counter[missing_mask]

    if "join_date" in df.columns:
        df["join_date"] = parse_date(df["join_date"])

    if "gender" in df.columns:
        gender_map = {
            "L": "Laki-Laki", "M": "Laki-Laki", "Male": "Laki-Laki",
            "Laki": "Laki-Laki", "Laki-Laki": "Laki-Laki",
            "P": "Perempuan", "F": "Perempuan", "Female": "Perempuan", "Perempuan": "Perempuan",}
        df["gender"] = df["gender"].astype(str).str.strip().str.title().replace(gender_map).replace("Nan", np.nan)
        missing_gender = df["gender"].isna()
        if missing_gender.any():
            rng = np.random.default_rng(42)
            df.loc[missing_gender, "gender"] = rng.choice(
                ["Laki-Laki", "Perempuan"], size=missing_gender.sum())

    if "kota" in df.columns:
        df["kota"] = df["kota"].astype(str).str.strip().str.title().replace("Nan", np.nan)

    if "segment" in df.columns:
        df["segment"] = df["segment"].astype(str).str.strip().str.title().replace("Nan", np.nan)

    if "customer_id" in df.columns:
        # Hanya buang baris tanpa primary key (kosong / NaN).
        df = df.dropna(subset=["customer_id"])
        df = df[df["customer_id"].astype(str).str.strip() != ""]
        df["customer_id"] = df["customer_id"].astype(str).str.strip().str.upper()
        df = df.drop_duplicates(subset=["customer_id"], keep="last")
 
    return df.reset_index(drop=True)

# ---------------------------------------------------------------------------
# INVENTORY
# ---------------------------------------------------------------------------
def clean_inventory(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    if "product_id" in df.columns:
        df = df.dropna(subset=["product_id"])
        df = df[df["product_id"].astype(str).str.strip() != ""]
        df["product_id"] = df["product_id"].astype(str).str.strip().str.upper()

    if "gudang" in df.columns:
        df["gudang"] = (
            df["gudang"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True).str.title().replace("Nan", np.nan))

    if "stok_tersedia" in df.columns:
        df["stok_tersedia"] = pd.to_numeric(df["stok_tersedia"], errors="coerce")
        df["stok_tersedia"] = df["stok_tersedia"].replace([np.inf, -np.inf], np.nan).fillna(0)
        df["stok_tersedia"] = df["stok_tersedia"].abs()
        df["stok_tersedia"] = df["stok_tersedia"].astype(int)

    if "last_update" in df.columns:
        df["last_update"] = parse_date(df["last_update"])

    if {"product_id", "gudang"}.issubset(df.columns):
        df = df.drop_duplicates(subset=["product_id", "gudang"], keep="last")

    return df.reset_index(drop=True)

# ---------------------------------------------------------------------------
# ORDERS
# ---------------------------------------------------------------------------
def clean_orders(
    df: pd.DataFrame,
    products_df: pd.DataFrame,
    customers_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    df = normalize_columns(df)
    products_df = normalize_columns(products_df)
    if customers_df is not None:
        customers_df = normalize_columns(customers_df)

    if "product_id" in df.columns:
        df["product_id"] = df["product_id"].astype(str).str.strip().str.upper()

    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df.loc[df["quantity"] < 0, "quantity"] = np.nan
        df["quantity"] = df["quantity"].fillna(1).astype(int)

    # Ambil ulang product_name, kategori, harga_satuan dari master produk
    # (bukan dari raw orders) supaya konsisten & bebas typo/harga usang.
    kolom_produk = ["product_id", "product_name", "kategori", "harga_satuan"]
    products_lookup = products_df[kolom_produk].drop_duplicates("product_id")
    df = df.merge(products_lookup, on="product_id", how="left", suffixes=("", "_master"))

    if "product_name_master" in df.columns:
        df["product_name"] = df["product_name_master"].astype(str).str.title()
        df.drop(columns="product_name_master", inplace=True)
    if "kategori_master" in df.columns:
        df["kategori"] = df["kategori_master"]
        df.drop(columns="kategori_master", inplace=True)
    if "harga_satuan_master" in df.columns:
        df["harga_satuan"] = pd.to_numeric(df["harga_satuan_master"], errors="coerce")
        df.drop(columns="harga_satuan_master", inplace=True)

    if "quantity" in df.columns and "harga_satuan" in df.columns:
        df["total_harga"] = (df["quantity"] * df["harga_satuan"]).astype(int)

    if "tanggal_order" in df.columns:
        df["tanggal_order"] = parse_date(df["tanggal_order"])

    if "kota" in df.columns:
        df["kota"] = df["kota"].astype(str).str.strip().str.title().replace("Nan", np.nan)

    if "channel" in df.columns:
        df["channel"] = df["channel"].astype(str).str.strip().str.replace("_", " ", regex=False).str.title()

    status_valid = ["Pending", "Completed", "Cancelled", "Shipped"]
    if "status" in df.columns:
        df["status"] = df["status"].astype(str).str.strip().str.title()
        df.loc[~df["status"].isin(status_valid), "status"] = "Pending"

    if "customer_email" in df.columns:
        df["customer_email"] = df["customer_email"].astype(str).str.strip().str.lower()
        df.loc[~df["customer_email"].str.contains("@", na=False), "customer_email"] = np.nan
        df["customer_email"] = df["customer_email"].fillna("dummy123@gmail.com")

    if (
        customers_df is not None
        and "customer_email" in df.columns
        and {"customer_id", "customer_email"}.issubset(customers_df.columns)
    ):
        customer_lookup = customers_df[["customer_id", "customer_email"]].copy()
        customer_lookup["customer_email"] = customer_lookup["customer_email"].astype(str).str.strip().str.lower()
        customer_lookup["customer_id"] = customer_lookup["customer_id"].astype(str).str.strip().str.upper()
        customer_lookup = customer_lookup.drop_duplicates(subset=["customer_email"], keep="last")
        df = df.merge(customer_lookup, on="customer_email", how="left")

    if "order_id" in df.columns:
        df["order_id"] = df["order_id"].astype(str).str.strip().str.upper()
        df = df.dropna(subset=["order_id"])
        df = df.drop_duplicates(subset="order_id", keep="last")

    return df.reset_index(drop=True)

# ---------------------------------------------------------------------------
# PAYMENTS
# ---------------------------------------------------------------------------
def clean_payments(df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    orders_df = normalize_columns(orders_df)

    if "metode_pembayaran" in df.columns:
        mapping = {
            "cod": "COD",
            "qris": "QRIS",
            "e-wallet": "E-Wallet",
            "e wallet": "E-Wallet",
            "ewallet": "E-Wallet",
            "bank transfer": "Bank Transfer",
            "bank_transfer": "Bank Transfer",
            "bank-transfer": "Bank Transfer",
            "virtual account": "Virtual Account",
            "virtual_account": "Virtual Account",
            "virtual-account": "Virtual Account",
            "credit card": "Credit Card",
            "credit_card": "Credit Card",
            "creadit_card": "Credit Card",
            "credit-card": "Credit Card",
            "creadit card": "Credit Card"}
        df["metode_pembayaran"] = (
            df["metode_pembayaran"]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r"[\s_-]+", " ", regex=True)
            .replace(mapping)
        )

    if "status_pembayaran" in df.columns:
        df["status_pembayaran"] = df["status_pembayaran"].astype(str).str.strip().str.title()

    if "jumlah_bayar" in df.columns:
        df["jumlah_bayar"] = pd.to_numeric(df["jumlah_bayar"], errors="coerce")
        df.loc[df["jumlah_bayar"] < 0, "jumlah_bayar"] = np.nan

    if "biaya_admin" in df.columns:
        df["biaya_admin"] = pd.to_numeric(df["biaya_admin"], errors="coerce")
        df["biaya_admin"] = df["biaya_admin"].clip(lower=0).fillna(0).astype(int)

    if "tanggal_bayar" in df.columns:
        df["tanggal_bayar"] = parse_date(df["tanggal_bayar"])

    if "payment_id" in df.columns:
        df = df.dropna(subset=["payment_id"])
        df = df.drop_duplicates(subset=["payment_id"], keep="last")

    if "order_id" in df.columns:
        df["order_id"] = df["order_id"].astype(str).str.strip().str.upper()
        df = filter_existing_references(df, "order_id", orders_df, "order_id")
        df = df.drop_duplicates(subset=["order_id"], keep="last")

    # Baris tanpa jumlah_bayar (kosong / negatif -> NaN) dibuang karena
    # transaksi tanpa nominal tidak bisa direkonsiliasi.
    if "jumlah_bayar" in df.columns:
        df = df.dropna(subset=["jumlah_bayar"])
        df["jumlah_bayar"] = df["jumlah_bayar"].astype(int)

    return df.reset_index(drop=True)

# ---------------------------------------------------------------------------
# RETURNS
# ---------------------------------------------------------------------------
def clean_returns(df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    orders_df = normalize_columns(orders_df)

    if "quantity_return" in df.columns:
        df["quantity_return"] = pd.to_numeric(df["quantity_return"], errors="coerce")
        df.loc[df["quantity_return"] < 0, "quantity_return"] = np.nan

    if "refund_amount" in df.columns:
        df["refund_amount"] = pd.to_numeric(df["refund_amount"], errors="coerce")
        df["refund_amount"] = df["refund_amount"].abs()

    if "tanggal_return" in df.columns:
        df["tanggal_return"] = parse_date(df["tanggal_return"])

    if "alasan_return" in df.columns:
        df["alasan_return"] = df["alasan_return"].astype(str).str.strip().str.lower().replace("nan", np.nan)

    if "status_return" in df.columns:
        df["status_return"] = df["status_return"].astype(str).str.strip().str.title()

    if "return_id" in df.columns:
        df["return_id"] = df["return_id"].astype(str).str.strip().str.upper()
        df = df.dropna(subset=["return_id"])
        df = df.drop_duplicates(subset=["return_id"], keep="last")

    if "order_id" in df.columns:
        df["order_id"] = df["order_id"].astype(str).str.strip().str.upper()
        df = filter_existing_references(df, "order_id", orders_df, "order_id")

    # Baris tanpa alasan / jumlah / nominal refund dibuang karena data
    # retur tidak lengkap untuk diproses lebih lanjut.
    df = df.dropna(subset=["alasan_return", "quantity_return", "refund_amount"])
    df["quantity_return"] = df["quantity_return"].astype(int)
    df["refund_amount"] = df["refund_amount"].astype(int)

    return df.reset_index(drop=True)

# ---------------------------------------------------------------------------
# ORDER_PROMO (bridge table)
# ---------------------------------------------------------------------------
def clean_order_promo(df: pd.DataFrame, orders_df: pd.DataFrame, promo_df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    orders_df = normalize_columns(orders_df)
    promo_df = normalize_columns(promo_df)

    df["order_id"] = df["order_id"].astype(str).str.strip().str.upper()
    df["promo_code"] = df["promo_code"].astype(str).str.strip().str.upper()

    df = df.dropna(subset=["order_id", "promo_code"])
    df = df[(df["order_id"] != "") & (df["promo_code"] != "")]
    df = filter_existing_references(df, "order_id", orders_df, "order_id")
    df = filter_existing_references(df, "promo_code", promo_df, "promo_code")
    df = df.drop_duplicates(subset=["order_id", "promo_code"], keep="last")

    df = df.sort_values("order_id").reset_index(drop=True)
    return df


