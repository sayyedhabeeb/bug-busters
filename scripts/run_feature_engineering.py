"""CLI script to run feature engineering."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.feature_engineering.engine import FeatureEngine


if __name__ == "__main__":
    FeatureEngine().run()
