from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any
import pandas as pd

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.path import WAREHOUSE_DIR

@dataclass
class ValidationIssue:
    severity: str
    table: str
    rule: str
    message: str
    count: int
    examples: list[dict[str, Any]]


PRIMARY_KEYS = {
    "products": ["product_id"],
    "customers": ["customer_id"],
    "promo": ["promo_code"],
    "suppliers": ["supplier_id"],
    "orders": ["order_id"],
    "payments": ["payment_id"],
    "returns": ["return_id"],
    "order_promo": ["order_id", "promo_code"],}

REQUIRED_COLUMNS = {
    "products": ["product_id", "product_name", "kategori", "harga_satuan"],
    "customers": ["customer_id", "customer_name"],
    "promo": ["promo_code", "tipe_diskon", "nilai_diskon"],
    "suppliers": ["supplier_id"],
    "inventory": ["product_id", "stok_tersedia"],
    "orders": ["order_id", "product_id", "quantity", "harga_satuan", "total_harga"],
    "payments": ["payment_id", "order_id", "jumlah_bayar"],
    "returns": ["return_id", "order_id", "quantity_return", "refund_amount"],
    "order_promo": ["order_id", "promo_code"],}

DATE_COLUMNS = {
    "customers": ["join_date"],
    "promo": ["tanggal_mulai", "tanggal_selesai"],
    "inventory": ["last_update"],
    "orders": ["tanggal_order"],
    "payments": ["tanggal_bayar"],
    "returns": ["tanggal_return"],}

NON_NEGATIVE_COLUMNS = {
    "products": ["harga_satuan"],
    "promo": ["nilai_diskon"],
    "inventory": ["stok_tersedia"],
    "orders": ["harga_satuan", "total_harga"],
    "payments": ["jumlah_bayar", "biaya_admin"],
    "returns": ["refund_amount"],}

POSITIVE_COLUMNS = {
    "orders": ["quantity"],
    "returns": ["quantity_return"],
    "suppliers": ["lead_time_hari"],}

FOREIGN_KEYS = [
    ("orders", "product_id", "products", "product_id"),
    ("suppliers", "product_id", "products", "product_id"),
    ("inventory", "product_id", "products", "product_id"),
    ("payments", "order_id", "orders", "order_id"),
    ("returns", "order_id", "orders", "order_id"),
    ("order_promo", "order_id", "orders", "order_id"),
    ("order_promo", "promo_code", "promo", "promo_code"),]


def blank_data(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().isin(["", "nan", "None", "NaT"])


def examples(df: pd.DataFrame, mask: pd.Series, columns: list[str], limit: int = 3) -> list[dict[str, Any]]:
    available_columns = [col for col in columns if col in df.columns]
    if not available_columns:
        available_columns = list(df.columns[:5])
    sample = df.loc[mask, available_columns].head(limit)
    return sample.where(pd.notna(sample), None).to_dict("records")


def add_issue(
    issues: list[ValidationIssue],
    table: str,
    rule: str,
    message: str,
    count: int,
    examples: list[dict[str, Any]],
    severity: str = "ERROR",) -> None:
    if count > 0:
        issues.append(
            ValidationIssue(
                severity=severity,
                table=table,
                rule=rule,
                message=message,
                count=count,
                examples=examples,))

def validate_primary_keys(tables: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for table, pk_columns in PRIMARY_KEYS.items():
        df = tables.get(table)
        if df is None:
            continue
        missing_pk_columns = [col for col in pk_columns if col not in df.columns]
        if missing_pk_columns:
            add_issue(
                issues,
                table,
                "primary_key_columns",
                "Kolom primary key tidak ditemukan: " + ", ".join(missing_pk_columns),
                len(missing_pk_columns),
                [],)
            continue

        blank_mask = pd.Series(False, index=df.index)
        for col in pk_columns:
            blank_mask = blank_mask | blank_data(df[col])
        add_issue(
            issues,
            table,
            "primary_key_not_null",
            "Primary key kosong/null.",
            int(blank_mask.sum()),
            examples(df, blank_mask, pk_columns),)

        duplicate_mask = df.duplicated(subset=pk_columns, keep=False)
        add_issue(
            issues,
            table,
            "primary_key_unique",
            "Primary key duplikat.",
            int(duplicate_mask.sum()),
            examples(df, duplicate_mask, pk_columns),)

    return issues


def validate_required_columns(tables: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for table, required_columns in REQUIRED_COLUMNS.items():
        df = tables.get(table)
        if df is None:
            continue

        missing_columns = [col for col in required_columns if col not in df.columns]
        add_issue(
            issues,
            table,
            "required_columns_exist",
            "Kolom wajib tidak ditemukan: " + ", ".join(missing_columns),
            len(missing_columns),[],)

        for col in required_columns:
            if col not in df.columns:
                continue
            blank_mask = blank_data(df[col])
            add_issue(
                issues,
                table,
                "required_columns_not_null",
                f"Kolom wajib '{col}' kosong/null.",
                int(blank_mask.sum()),
                examples(df, blank_mask, [col]),)
    return issues


def validate_dates(tables: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for table, date_columns in DATE_COLUMNS.items():
        df = tables.get(table)
        if df is None:
            continue

        for col in date_columns:
            if col not in df.columns:
                continue
            blank_mask = blank_data(df[col])
            parsed = pd.to_datetime(df[col], errors="coerce")
            invalid_mask = parsed.isna() & ~blank_mask
            add_issue(
                issues,
                table,
                "valid_date",
                f"Kolom tanggal '{col}' berisi format tidak valid.",
                int(invalid_mask.sum()),
                examples(df, invalid_mask, [col]),)

        if table == "promo" and {"tanggal_mulai", "tanggal_selesai"}.issubset(df.columns):
            start_date = pd.to_datetime(df["tanggal_mulai"], errors="coerce")
            end_date = pd.to_datetime(df["tanggal_selesai"], errors="coerce")
            invalid_range = start_date.notna() & end_date.notna() & (end_date < start_date)
            add_issue(
                issues,
                table,
                "valid_date_range",
                "tanggal_selesai lebih awal dari tanggal_mulai.",
                int(invalid_range.sum()),
                (df, invalid_range, ["promo_code", "tanggal_mulai", "tanggal_selesai"]),)

    return issues


def validate_numeric_values(tables: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for table, columns in NON_NEGATIVE_COLUMNS.items():
        df = tables.get(table)
        if df is None:
            continue
        for col in columns:
            if col not in df.columns:
                continue
            numeric = pd.to_numeric(df[col], errors="coerce")
            invalid_mask = numeric < 0
            add_issue(
                issues,
                table,
                "non_negative_value",
                f"Kolom '{col}' bernilai negatif.",
                int(invalid_mask.sum()),
                examples(df, invalid_mask, [col]),)

    for table, columns in POSITIVE_COLUMNS.items():
        df = tables.get(table)
        if df is None:
            continue
        for col in columns:
            if col not in df.columns:
                continue
            numeric = pd.to_numeric(df[col], errors="coerce")
            invalid_mask = numeric <= 0
            add_issue(
                issues,
                table,
                "positive_value",
                f"Kolom '{col}' harus lebih besar dari 0.",
                int(invalid_mask.sum()),
                examples(df, invalid_mask, [col]),)

    return issues


def validate_foreign_keys(tables: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for table, column, ref_table, ref_column in FOREIGN_KEYS:
        df = tables.get(table)
        ref_df = tables.get(ref_table)
        if df is None or ref_df is None or column not in df.columns or ref_column not in ref_df.columns:
            continue

        values = df[column]
        ref_values = set(ref_df[ref_column].dropna().astype(str))
        invalid_mask = ~blank_data(values) & ~values.astype(str).isin(ref_values)
        add_issue(
            issues,
            table,
            "foreign_key_valid",
            f"FK {table}.{column} tidak ditemukan di {ref_table}.{ref_column}.",
            int(invalid_mask.sum()),
            examples(df, invalid_mask, [column]),)

    return issues


def validate_tables(tables: dict[str, pd.DataFrame]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(validate_primary_keys(tables))
    issues.extend(validate_required_columns(tables))
    issues.extend(validate_dates(tables))
    issues.extend(validate_numeric_values(tables))
    issues.extend(validate_foreign_keys(tables))
    return issues


def load_warehouse_tables() -> dict[str, pd.DataFrame]:
    tables = {}
    table_names = set(REQUIRED_COLUMNS) | set(PRIMARY_KEYS)
    for table in sorted(table_names):
        path = WAREHOUSE_DIR / f"{table}_clean.csv"
        if path.exists():
            tables[table] = pd.read_csv(path)
    return tables


def print_validation_report(issues: list[ValidationIssue]) -> None:
    print("\nValidasi:")
    if not issues:
        print("✓ Semua Validasi Data Successfully")
        return

    total_rows = sum(issue.count for issue in issues)
    print(f"Ditemukan {len(issues)} jenis issue ({total_rows} baris terdampak).")
    for issue in issues:
        print(f"- [{issue.severity}] {issue.table} / {issue.rule}: {issue.message} ({issue.count})")
        if issue.examples:
            print(f"  contoh: {issue.examples}")


def run_validation() -> list[ValidationIssue]:
    tables = load_warehouse_tables()
    issues = validate_tables(tables)
    print_validation_report(issues)
    return issues

if __name__ == "__main__":
    run_validation()
