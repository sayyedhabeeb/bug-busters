"""
Model Training Engine
---------------------
Advanced engine for Enterprise-Grade model training.
Implements XGBoost with Hyperparameter Tuning and Cross-Validation.
"""

import logging
import pickle
import json
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score, 
    classification_report, 
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score
)

logger = logging.getLogger(__name__)

try:
    import shap
    HAS_SHAP = True
except Exception as e:
    # Use a basic print if logger is not ready, though it should be here
    logging.warning(f"SHAP could not be imported: {e}. Explainability features will be disabled.")
    HAS_SHAP = False

class ModelTrainingEngine:
    """
    Engine for training and saving XGBoost models with advanced tuning.
    """
    
    def __init__(self, output_dir: Path = Path("outputs/models"), feature_path: Path = Path("data/processed/features/feature_matrix.csv")):
        self.output_dir = output_dir
        self.feature_path = feature_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.feature_columns = []
        
    def train(self, test_size: float = 0.2, random_state: int = 42, tune: bool = True) -> Dict[str, Any]:
        """
        Train the model using the feature matrix.
        
        Args:
            test_size: Proportion of dataset to include in the test split.
            random_state: Random seed.
            tune: Whether to perform hyperparameter tuning.
            
        Returns:
            Dictionary containing training metadata and metrics.
        """
        logger.info("Starting Enterprise Model Training...")
        
        # 1. Load Data
        if not self.feature_path.exists():
            raise FileNotFoundError(f"Feature matrix not found at {self.feature_path}")
            
        df = pd.read_csv(self.feature_path)
        logger.info(f"Loaded feature matrix with shape {df.shape}")
        
        if "label" not in df.columns:
            raise ValueError("Feature matrix must contain a 'label' column.")
            
        # 2. Prepare Feature Matrix
        ignore_cols = {"label", "resume_index", "job_index", "resume_id", "job_id", "score"} # Ignore 'score' used for labeling
        self.feature_columns = [col for col in df.columns if col not in ignore_cols]
        
        X = df[self.feature_columns]
        y = df["label"]

        # SAFETY CHECK: Ensure we have both classes before training!
        if y.nunique() < 2:
            raise ValueError(
                f"❌ Cannot train: Only one class in labels! "
                f"0: {(y == 0).sum()}, 1: {(y == 1).sum()}. "
                f"Check feature engineering labeling logic and score distribution."
            )

        # Calculate class weight for XGBoost
        # scale_pos_weight = sum(negative) / sum(positive)
        n_pos = sum(y == 1)
        n_neg = sum(y == 0)
        self.scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1.0
        logger.info(f"Class Imbalance: Neg={n_neg}, Pos={n_pos}. Using scale_pos_weight={self.scale_pos_weight:.2f}")
        
        # 3. Split Data
        stratify = y if y.nunique() > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=stratify
        )
        
        # 4. Stage 1: Baseline XGBoost (Default Parameters)
        logger.info("--- STAGE 1: Training Baseline XGBoost (Default Parameters) ---")
        baseline_model = xgb.XGBClassifier(
            random_state=random_state,
            scale_pos_weight=self.scale_pos_weight,
            eval_metric='logloss',
            n_jobs=-1
        )
        baseline_model.fit(X_train, y_train)
        
        y_pred_base = baseline_model.predict(X_test)
        y_prob_base = baseline_model.predict_proba(X_test)[:, 1]
        baseline_metrics = self._get_metrics(y_test, y_pred_base, y_prob_base)
        
        # 5. Stage 2: Cross-Validation Score
        logger.info("--- STAGE 2: 5-Fold Cross-Validation ---")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
        cv_scores = cross_val_score(baseline_model, X_train, y_train, cv=cv, scoring='roc_auc', n_jobs=-1)
        mean_cv_roc_auc = cv_scores.mean()
        logger.info(f"Mean CV ROC-AUC: {mean_cv_roc_auc:.4f}")

        # 6. Stage 3: Hyperparameter Tuning and Best Model
        results = {
            "Baseline (Default)": baseline_metrics,
            "CV Score (Mean ROC-AUC)": mean_cv_roc_auc
        }

        if tune:
            logger.info("--- STAGE 3: Hyperparameter Tuning (RandomizedSearchCV) ---")
            self.model, best_cv_score = self._tune_xgboost(X_train, y_train, random_state)
            
            y_pred_tuned = self.model.predict(X_test)
            y_prob_tuned = self.model.predict_proba(X_test)[:, 1]
            tuned_metrics = self._get_metrics(y_test, y_pred_tuned, y_prob_tuned)
            results["Tuned Best Model"] = tuned_metrics
            results["Best CV Score (Tuning)"] = best_cv_score
        else:
            self.model = baseline_model
            results["Tuned Best Model"] = baseline_metrics # Same as baseline if no tuning

        # 7. Final Comparison and Results
        self._print_comparison(results)
        
        # 8. Explain Model (SHAP)
        self.explain_model(X_test)
        
        # 9. Save Artifacts
        self._save_artifacts()
        
        return {
            "model_type": "XGBClassifier",
            "feature_columns": self.feature_columns,
            "baseline_metrics": baseline_metrics,
            "cv_mean_roc_auc": mean_cv_roc_auc,
            "tuned_metrics": results.get("Tuned Best Model"),
            "samples": len(df),
            "test_size": test_size,
            "tuned": tune
        }

    def _get_metrics(self, y_true, y_pred, y_prob) -> Dict[str, float]:
        """Calculate standard evaluation metrics."""
        return {
            "Accuracy": accuracy_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred, zero_division=0),
            "Recall": recall_score(y_true, y_pred, zero_division=0),
            "F1-score": f1_score(y_true, y_pred, zero_division=0),
            "ROC-AUC": roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else 0.0
        }

    def _print_comparison(self, results: Dict[str, Any]):
        """Print a clear comparison of results in the terminal."""
        print("\n" + "="*80)
        print(f"{'STAGE COMPARISON REPORT':^80}")
        print("="*80)
        
        metrics_to_show = ["Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC"]
        
        header = f"{'Metric':<20} | {'Baseline':<15} | {'Tuned Best':<15}"
        print(header)
        print("-" * len(header))
        
        base = results["Baseline (Default)"]
        tuned = results.get("Tuned Best Model", {})
        
        for metric in metrics_to_show:
            b_val = base.get(metric, 0)
            t_val = tuned.get(metric, 0)
            print(f"{metric:<20} | {b_val:<15.4f} | {t_val:<15.4f}")
            
        print("-" * len(header))
        print(f"{'Mean CV ROC-AUC':<20} | {results['CV Score (Mean ROC-AUC)']:<15.4f} | {'N/A':<15}")
        if "Best CV Score (Tuning)" in results:
            print(f"{'Best Tuning CV Score':<20} | {'N/A':<15} | {results['Best CV Score (Tuning)']:<15.4f}")
        print("="*80 + "\n")

    def _tune_xgboost(self, X, y, random_state):
        """Perform RandomizedSearchCV for XGBoost."""
        param_dist = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'max_depth': [3, 5, 7, 9],
            'min_child_weight': [1, 3, 5],
            'gamma': [0, 0.1, 0.2, 0.3],
            'subsample': [0.6, 0.7, 0.8, 0.9, 1.0],
            'colsample_bytree': [0.6, 0.7, 0.8, 0.9, 1.0]
        }
        
        xgb_model = xgb.XGBClassifier(
            scale_pos_weight=self.scale_pos_weight,
            eval_metric='logloss', 
            random_state=random_state,
            n_jobs=-1
        )
        
        # 2. Dynamic Stratified K-Fold based on minority class size
        class_counts = y.value_counts()
        min_samples = class_counts.min()
        n_splits = min(5, min_samples)
        
        if n_splits < 2:
            logger.warning(f"Minority class has only {min_samples} samples. Skipping CV and using default parameters.")
            return xgb_model.fit(X, y)

        logger.info(f"Using {n_splits}-fold cross-validation (limited by minority class size: {min_samples})")
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        
        random_search = RandomizedSearchCV(
            estimator=xgb_model,
            param_distributions=param_dist,
            n_iter=20,  # 20 iterations
            scoring='roc_auc',
            cv=cv,
            verbose=1,
            random_state=random_state,
            n_jobs=-1
        )
        
        random_search.fit(X, y)
        
        logger.info(f"Best Parameters: {random_search.best_params_}")
        logger.info(f"Best CV Score (ROC-AUC): {random_search.best_score_:.4f}")
        
        return random_search.best_estimator_, random_search.best_score_

    def explain_model(self, X_test: pd.DataFrame):
        """Generate SHAP values for explainability."""
        if not HAS_SHAP:
            logger.warning("Skipping SHAP explanation: SHAP is not available.")
            return

        logger.info("Generating SHAP explanations...")
        
        # TreeExplainer for XGBoost
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(X_test)
        
        report_dir = self.output_dir.parent / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save summary plot
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test, show=False)
        plot_path = report_dir / "shap_summary.png"
        plt.savefig(plot_path, bbox_inches="tight")
        plt.close()
        logger.info(f"SHAP summary plot saved to {plot_path}")

    def _save_artifacts(self) -> None:
        """Save trained model and metadata."""
        model_path = self.output_dir / "trained_model.pkl"
        meta_path = self.output_dir / "model_metadata.json"
        
        # Save Model
        with open(model_path, "wb") as f:
            pickle.dump(self.model, f)
            
        # Save Metadata (Features, Etc.)
        metadata = {
            "feature_columns": self.feature_columns,
            "model_type": type(self.model).__name__,
            "timestamp": pd.Timestamp.now().isoformat(),
            "library": "xgboost"
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Model saved to {model_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = ModelTrainingEngine()
    try:
        engine.train(tune=True)
    except Exception as e:
        logger.error(f"Training failed: {e}")
