import shap
import pandas as pd
import numpy as np
import logging
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ShapEngine:
    """
    Explainable AI Engine using SHAP (SHapley Additive exPlanations).
    Interprets XGBoost/sklearn models.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        self.model = None
        self.explainer = None
        self.is_ready = False
        
        if model_path and model_path.exists():
            self.load_model(model_path)

    def load_model(self, model_path: Path):
        """Load model and initialize explainer."""
        try:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            
            # Identify model type
            if hasattr(self.model, "predict_proba"):
                # TreeExplainer for XGBoost/RandomForest
                try:
                    self.explainer = shap.TreeExplainer(self.model)
                except Exception:
                    # Fallback for generic sklearn models
                    # KernelExplainer requires background data, might be slow
                    # self.explainer = shap.KernelExplainer(self.model.predict_proba, X_background)
                    # For now, simplistic linear approximation or skip
                    logger.warning("Could not initialize TreeExplainer. Partial explanation mode.")
                    self.explainer = None
            
            self.is_ready = True
            logger.info("SHAP Engine initialized.")
            
        except Exception as e:
            logger.error(f"Failed to load explanation model: {e}")

    def explain_local(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Explain a single prediction.
        expected_features: Dict of feature_name -> value
        """
        if not self.is_ready or not self.explainer:
            return {"explanation": "Model explanation not available."}

        try:
            # Convert dict to DataFrame
            # Ensure column order matches model
            # This is tricky without metadata. Assuming feature keys match model inputs.
            df = pd.DataFrame([features])
            
            # Align columns if possible (requires model.feature_names_in_)
            if hasattr(self.model, "feature_names_in_"):
                df = df[self.model.feature_names_in_]
                
            shap_values = self.explainer.shap_values(df)
            
            # For classification, shap_values might be list [class0, class1]
            if isinstance(shap_values, list):
                shap_values = shap_values[1] # Positive class
            
            # Create contribution dictionary
            contributions = dict(zip(df.columns, shap_values[0]))
            
            # Sort by absolute impact
            sorted_contribs = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
            
            # Generate Text Explanation
            top_3 = sorted_contribs[:3]
            explanation_parts = []
            for feat, val in top_3:
                direction = "increased" if val > 0 else "decreased"
                explanation_parts.append(f"{feat} {direction} score")
            
            return {
                "shap_values": contributions,
                "top_features": top_3,
                "explanation": ", ".join(explanation_parts)
            }
            
        except Exception as e:
            logger.error(f"Explanation failed: {e}")
            return {"explanation": "Explanation failed due to internal error."}

    def explain_global(self, X_sample: pd.DataFrame) -> Dict[str, Any]:
        """Generate global feature importance."""
        if not self.is_ready or not self.explainer:
            return {}
            
        shap_values = self.explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
             shap_values = shap_values[1]
             
        # Mean absolute SHAP value
        global_importance = np.abs(shap_values).mean(0)
        feature_names = X_sample.columns.tolist()
        
        return dict(zip(feature_names, global_importance))
