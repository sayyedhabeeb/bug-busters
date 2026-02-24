import joblib
from pathlib import Path
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

models_dir = Path("outputs/models")
print(f"Checking models in: {models_dir.absolute()}")

for f in models_dir.glob("*"):
    if f.suffix in [".pkl", ".joblib"]:
        print(f"\nModel: {f.name}")
        try:
            m = joblib.load(f)
            print(f"Type: {type(m)}")
            
            # Try different attributes to find feature names
            if hasattr(m, "feature_names_in_"):
                print(f"Features ({len(m.feature_names_in_)}): {list(m.feature_names_in_)}")
            elif hasattr(m, "get_booster"):
                booster = m.get_booster()
                if booster.feature_names:
                    print(f"Features ({len(booster.feature_names)}): {booster.feature_names}")
                else:
                    print("Booster has no feature names.")
            elif hasattr(m, "feature_names"):
                print(f"Features ({len(m.feature_names)}): {m.feature_names}")
            else:
                print("No obvious feature names found.")
        except Exception as e:
            print(f"Error loading {f.name}: {e}")
