"""CLI script to run model training."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.modeling.engine import ModelTrainingEngine


if __name__ == "__main__":
    ModelTrainingEngine().train()
