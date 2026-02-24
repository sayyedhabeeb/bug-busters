import joblib
import pickle
import os
from pathlib import Path
import pandas as pd

models_dir = Path("outputs/models")
models = [
    "xgboost_ranking_model.pkl",
    "trained_model.pkl",
    "xgb_model.joblib",
    "lr_baseline.joblib"
]

for model_name in models:
    path = models_dir / model_name
    if not path.exists():
        print(f"{model_name} does not exist.")
        continue
    
    print(f"\n--- Inspecting {model_name} ---")
    try:
        if path.suffix == ".pkl":
            with open(path, "rb") as f:
                model = pickle.load(f)
        else:
            model = joblib.load(path)
        
        print(f"Model type: {type(model)}")
        
        if hasattr(model, "feature_names_in_"):
            print(f"Features ({len(model.feature_names_in_)}): {model.feature_names_in_}")
        elif hasattr(model, "get_booster"):
            booster = model.get_booster()
            if booster.feature_names:
                print(f"Features ({len(booster.feature_names)}): {booster.feature_names}")
            else:
                print("Booster has no feature names.")
        else:
            print("Model has no feature names attribute.")
            
    except Exception as e:
        print(f"Failed to load {model_name}: {e}")
