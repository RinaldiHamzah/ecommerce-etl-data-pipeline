from pathlib import Path
import sys

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.connector import db_connection

DATABASE_DIR = Path(__file__).resolve().parent
SQL_FILES = [
    DATABASE_DIR / "schema.sql",
    DATABASE_DIR / "index.sql",
    DATABASE_DIR / "view.sql",]

def log(message: str) -> None:
    print(message)

def init_database():
    with db_connection() as conn:
        with conn.cursor() as cursor:
            for sql_file in SQL_FILES:
                if not sql_file.exists():
                    log(f"File {sql_file} tidak ditemukan, dilewati.")
                    continue
                
                log(f"Menjalankan script: {sql_file}...")
                sql_content = sql_file.read_text(encoding="utf-8").strip()
                if not sql_content:
                    log(f"File {sql_file} kosong, dilewati.")
                    continue
                cursor.execute(sql_content)
                log(f"Berhasil mengeksekusi {sql_file.name}")

    log("Database berhasil di-inisialisasi (schema, index, view).")

if __name__ == "__main__":
    init_database()
