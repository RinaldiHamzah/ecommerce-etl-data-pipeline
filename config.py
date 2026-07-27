import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

ROOT = Path(__file__).resolve().parent
DB_HOST = os.getenv("DB_HOST", os.getenv("PGHOST", "localhost"))
DB_PORT = os.getenv("DB_PORT", os.getenv("PGPORT", "5432"))
DB_NAME = os.getenv("DB_NAME", os.getenv("PGDATABASE", "ecommerce_order"))
DB_USER = os.getenv("DB_USER", os.getenv("PGUSER", "postgres"))
DB_PASSWORD = os.getenv("DB_PASSWORD", os.getenv("PGPASSWORD"))

def get_database_config() -> dict[str, str]:
    missing = [
        name
        for name, value in {
            "DB_HOST/PGHOST": DB_HOST,
            "DB_PORT/PGPORT": DB_PORT,
            "DB_NAME/PGDATABASE": DB_NAME,
            "DB_USER/PGUSER": DB_USER,
            "DB_PASSWORD/PGPASSWORD": DB_PASSWORD,
        }.items()
        if value in (None, "")]
    if missing:
        raise RuntimeError(
            "Environment database belum lengkap. Isi: " + ", ".join(missing))
    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,}
