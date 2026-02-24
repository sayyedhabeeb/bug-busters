"""CLI script to run data preprocessing."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_processing.data_preprocessing import run_preprocessing


if __name__ == "__main__":
    run_preprocessing()
