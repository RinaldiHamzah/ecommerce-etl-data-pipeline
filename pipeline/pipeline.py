from pathlib import Path
import sys

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.runner import run_pipeline

if __name__ == "__main__":
    run_pipeline()
