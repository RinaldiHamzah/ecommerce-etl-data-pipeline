from __future__ import annotations

import argparse
from collections.abc import Callable
import subprocess
import sys
import unittest

from database.init import init_database
from database.loader import run_loader
from pipeline.runner import run_pipeline
from pipeline.validation import run_validation
from logger import logger

Command = Callable[[], int]

def run_pipeline_command() -> int:
    logger.info("Pipeline dimulai.")
    try:
        run_pipeline()
        logger.info("Pipeline selesai.")
        return 0
    except Exception:
        logger.exception("Pipeline gagal dijalankan.")
        return 1

def run_validation_command() -> int:
    logger.info("Validasi data dimulai.")
    try:
        issues = run_validation()
        if issues:
            logger.warning(f"Validasi selesai dengan {issues} issue.")
            return 1
        logger.info("Validasi berhasil tanpa issue.")
        return 0
    except Exception:
        logger.exception("Validasi gagal.")
        return 1

def run_init_db_command() -> int:
    logger.info("Inisialisasi database dimulai.")
    try:
        init_database()
        logger.info("Inisialisasi database berhasil.")
        return 0
    except Exception:
        logger.exception("Inisialisasi database gagal.")
        return 1

def run_load_db_command() -> int:
    logger.info("Loading data ke PostgreSQL dimulai.")
    try:
        run_loader()
        logger.info("Loading data ke PostgreSQL selesai.")
        return 0
    except Exception:
        logger.exception("Loading database gagal.")
        return 1

def run_test_command() -> int:
    logger.info("Menjalankan automated testing.")
    suite = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        logger.info("Semua unit test berhasil.")
        return 0
    logger.warning("Terdapat unit test yang gagal.")
    return 1

def run_dashboard_command() -> int:
    logger.info("Dashboard Flask dijalankan.")
    command = [sys.executable, "app.py"]
    print("Dashboard Flask berjalan di http://127.0.0.1:5001")
    try:
        return subprocess.call(command)
    except Exception:
        logger.info("Dashboard dihentikan oleh pengguna.")
        return 0
    except Exception:
        logger.exception("Dashboard gagal dijalankan.")
        return 1

def run_all_command() -> int:
    logger.info("=" * 50)
    logger.info("Workflow Ekstrak, Transform, dan Loading data dimulai.")
    try:
        logger.info("Tahap 1 : Pipeline")
        run_pipeline()
        logger.info("Tahap 2 : Validation")
        issues = run_validation()
        if issues:
            logger.warning(
                f"Workflow dihentikan karena ditemukan {issues} issue validasi.")
            print("\nWorkflow dihentikan karena validasi masih menemukan issue.")
            return 1
        logger.info("Tahap 3 : Init Database")
        init_database()
        logger.info("Tahap 4 : Load PostgreSQL")
        run_loader()
        logger.info("Workflow ETL selesai dengan sukses.")
        logger.info("=" * 50)
        return 0
    except Exception:
        logger.exception("Workflow ETL gagal.")
        return 1

COMMANDS: dict[str, Command] = {
    "pipeline": run_pipeline_command,
    "validate": run_validation_command,
    "test": run_test_command,
    "dashboard": run_dashboard_command,
    "init-db": run_init_db_command,
    "load-db": run_load_db_command,
    "all": run_all_command,}

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Command runner untuk workflow ETL Ecommerce Order.",)
    parser.add_argument(
        "command",
        choices=COMMANDS.keys(),
        help=(
            "pipeline=bersihkan raw CSV, validate=cek kualitas data, "
            "test=jalankan automated test ringan, "
            "dashboard=jalankan dashboard Flask, "
            "init-db=buat ulang schema PostgreSQL, load-db=load CSV clean, "
            "all=jalankan semua workflow"),)
    return parser

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    logger.info(f"Command diterima : {args.command}")
    return COMMANDS[args.command]()

if __name__ == "__main__":
    raise SystemExit(main())
