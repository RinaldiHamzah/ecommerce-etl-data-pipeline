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

Command = Callable[[], int]

def run_pipeline_command() -> int:
    run_pipeline()
    return 0

def run_validation_command() -> int:
    issues = run_validation()
    return 1 if issues else 0

def run_init_db_command() -> int:
    init_database()
    return 0

def run_load_db_command() -> int:
    run_loader()
    return 0

def run_test_command() -> int:
    suite = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


def run_dashboard_command() -> int:
    command = [sys.executable, "app.py"]
    print("Dashboard Flask berjalan di http://127.0.0.1:5001")
    return subprocess.call(command)


def run_all_command() -> int:
    run_pipeline()

    issues = run_validation()
    if issues:
        print("\nWorkflow dihentikan karena validasi masih menemukan issue.")
        return 1
    init_database()
    run_loader()
    return 0


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
    return COMMANDS[args.command]()

if __name__ == "__main__":
    raise SystemExit(main())
