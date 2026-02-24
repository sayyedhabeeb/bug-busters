import joblib
import pickle
from pathlib import Path

path = Path("outputs/models/xgboost_ranking_model.pkl")
with open(path, "rb") as f:
    model = pickle.load(f)

print(f"Model: {path.name}")
if hasattr(model, "feature_names_in_"):
    print(f"Features ({len(model.feature_names_in_)}): {list(model.feature_names_in_)}")
elif hasattr(model, "get_booster"):
    booster = model.get_booster()
    if booster.feature_names:
        print(f"Features ({len(booster.feature_names)}): {booster.feature_names}")
    else:
        print("Booster has no feature names.")
else:
    print("No feature names found.")
