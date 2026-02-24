import joblib
import os
from pathlib import Path

models_dir = Path("outputs/models")
files = [
    "xgboost_ranking_model.pkl",
    "trained_model.pkl",
    "xgb_model.joblib",
    "lr_baseline.joblib"
]

for filename in files:
    path = models_dir / filename
    if not path.exists():
        continue
    
    print(f"\n--- {filename} ---")
    try:
        model = joblib.load(path)
        print(f"Type: {type(model)}")
        if hasattr(model, "feature_names_in_"):
            print(f"Features: {list(model.feature_names_in_)}")
        elif hasattr(model, "get_booster"):
            booster = model.get_booster()
            print(f"Features: {booster.feature_names}")
    except Exception as e:
        print(f"Failed: {e}")
