from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import sys
from typing import Iterator
import psycopg2
import psycopg2.extras

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import get_database_config

def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(**get_database_config())

@contextmanager
def db_connection(autocommit: bool = False) -> Iterator[psycopg2.extensions.connection]:
    conn = get_connection()
    conn.autocommit = autocommit
    try:
        yield conn
        if not autocommit:
            conn.commit()
    except Exception:
        if not autocommit:
            conn.rollback()
        raise
    finally:
        conn.close()

@contextmanager
def db_cursor(autocommit: bool = False, dict_cursor: bool = False):
    with db_connection(autocommit=autocommit) as conn:
        cursor_factory = psycopg2.extras.RealDictCursor if dict_cursor else None
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            yield cur

def test_connection() -> bool:
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return True
    except Exception as e:
        print(f"Koneksi database GAGAL: {e}")
        return False

if __name__ == "__main__":
    ok = test_connection()
    if ok:
        db_config = get_database_config()
        print(f"Koneksi ke database '{db_config['dbname']}' di {db_config['host']}:{db_config['port']} berhasil.")
    else:
        print("Cek kembali environment variable DB_* atau PG* di .env.")