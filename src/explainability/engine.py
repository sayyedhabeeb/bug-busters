"""
Explainability Engine
---------------------
Engine for generating model explanations using SHAP (SHapley Additive exPlanations).
Provides global feature importance and local prediction justifications.
"""

import logging
import pickle
import json
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd
import numpy as np
import shap

logger = logging.getLogger(__name__)

class ExplainabilityEngine:
    """
    Engine for Explainable AI (XAI) using SHAP.
    """
    
    def __init__(self, model_path: Path = Path("outputs/models/trained_model.pkl"),
                 feature_path: Path = Path("data/processed/features/feature_matrix.csv"),
                 output_dir: Path = Path("outputs/reports/explainability")):
        self.model_path = model_path
        self.feature_path = feature_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.explainer = None
        self.shap_values = None
        
    def load_resources(self) -> None:
        """Load model and data for explanation."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
            
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
            
        logger.info("Model loaded for explainability.")

    def explain_global(self) -> Dict[str, Any]:
        """
        Generate global explanations (Feature Importance, Summary Plot).
        """
        logger.info("Generating Global Explanations...")
        if self.model is None:
            self.load_resources()
            
        # Load Data Sample for SHAP (using random sample to speed up)
        df = pd.read_csv(self.feature_path)
        
        # Filter features
        ignore_cols = {"label", "resume_index", "job_index", "resume_id", "job_id", "score"}
        feature_cols = [col for col in df.columns if col not in ignore_cols]
        X = df[feature_cols]
        
        # Subsample for performance if dataset is large
        if len(X) > 1000:
            X_sample = X.sample(1000, random_state=42)
        else:
            X_sample = X
            
        # Initialize Explainer
        # TreeExplainer is best for XGBoost/RandomForest
        self.explainer = shap.TreeExplainer(self.model)
        self.shap_values = self.explainer.shap_values(X_sample)
        
        # Save Summary Plot
        plt.figure(figsize=(10, 6))
        shap.summary_plot(self.shap_values, X_sample, show=False)
        plot_path = self.output_dir / "shap_summary_plot.png"
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        logger.info(f"SHAP summary plot saved to {plot_path}")
        
        # Calculate Mean Absolute SHAP values (Feature Importance)
        feature_importance = pd.DataFrame(list(zip(feature_cols, np.abs(self.shap_values).mean(0))), 
                                          columns=['feature', 'importance'])
        feature_importance = feature_importance.sort_values(by='importance', ascending=False)
        
        importance_path = self.output_dir / "feature_importance.csv"
        feature_importance.to_csv(importance_path, index=False)
        logger.info(f"Feature importance saved to {importance_path}")
        
        return {
            "summary_plot": str(plot_path),
            "feature_importance": str(importance_path),
            "top_features": feature_importance.head(5).to_dict(orient='records')
        }

    def explain_local(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate explanation for a single prediction.
        Args:
            features: Dictionary of feature values.
        """
        if self.model is None:
            self.load_resources()
            
        if self.explainer is None:
             # Re-initialize explainer with dummy background if needed, 
             # but TreeExplainer usually stores info. 
             # For robustness, we might need a background dataset, but TreeExplainer is self-contained for XGBoost.
             self.explainer = shap.TreeExplainer(self.model)

        # Convert input to DataFrame
        df_input = pd.DataFrame([features])
        
        # Calculate SHAP values for this instance
        shap_values_local = self.explainer.shap_values(df_input)
        
        # Format explanation
        explanation = []
        for feat, val in zip(df_input.columns, shap_values_local[0]):
            explanation.append({
                "feature": feat,
                "shap_value": float(val),
                "impact": "positive" if val > 0 else "negative"
            })
            
        # Sort by absolute impact
        explanation.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        
        return {
            "prediction": float(self.model.predict_proba(df_input)[:, 1][0]),
            "explanation": explanation[:5] # Top 5 contributing factors
        }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = ExplainabilityEngine()
    try:
        engine.load_resources()
        engine.explain_global()
    except Exception as e:
        logger.error(f"Explainability failed: {e}")
