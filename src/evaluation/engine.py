"""
Evaluation Engine
-----------------
Standardized engine for comprehensive model evaluation.
Includes Classification Metrics (Accuracy, F1) and Ranking Metrics (NDCG, MRR, Precision@K).
"""

import logging
import json
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, roc_auc_score, confusion_matrix, roc_curve, auc
)

logger = logging.getLogger(__name__)

class EvaluationEngine:
    """
    Engine for evaluating model performance.
    """
    
    def __init__(self, model_path: Path = Path("outputs/models/trained_model.pkl"), 
                 feature_path: Path = Path("data/processed/features/feature_matrix.csv"),
                 output_dir: Path = Path("outputs/reports")):
        self.model_path = model_path
        self.feature_path = feature_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model = None

    def evaluate(self) -> Dict[str, Any]:
        """
        Load model and data, then perform evaluation.
        """
        logger.info("Starting model evaluation...")
        
        # 1. Load Resources
        self._load_model()
        
        if not self.feature_path.exists():
            raise FileNotFoundError(f"Feature matrix not found at {self.feature_path}")
        
        df = pd.read_csv(self.feature_path)
        
        if "label" not in df.columns:
            raise ValueError("Feature matrix missing 'label' column.")
            
        # Filter features based on model expectation (load metadata if possible, else infer)
        ignore_cols = {"label", "resume_index", "job_index", "resume_id", "job_id", "score"}
        feature_cols = [col for col in df.columns if col not in ignore_cols]
        
        X = df[feature_cols]
        y = df["label"]
        
        # 2. Predictions
        y_pred = self.model.predict(X)
        y_prob = self.model.predict_proba(X)[:, 1]
        
        # 3. Calculate Metrics
        metrics = {
            "accuracy": float(accuracy_score(y, y_pred)),
            "precision": float(precision_score(y, y_pred, zero_division=0)),
            "recall": float(recall_score(y, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y, y_prob)) if len(np.unique(y)) > 1 else 0.0,
            "classification_report": classification_report(y, y_pred, output_dict=True, zero_division=0)
        }
        
        # 4. Ranking Metrics (NDCG, MRR, P@K, R@K)
        # Try both resume_index and job_index for grouping context
        group_col = "job_index" if "job_index" in df.columns else "resume_index"
        if group_col in df.columns:
            logger.info(f"Calculating ranking metrics grouped by {group_col}...")
            ranking_metrics = self._calculate_ranking_metrics(df, y_prob, group_col=group_col)
            metrics.update(ranking_metrics)
            
        # 5. Visualizations
        self._plot_visualizations(y, y_pred, y_prob)
            
        # 6. Save Report
        self._save_report(metrics)
        
        logger.info("Evaluation complete.")
        return metrics

    def _load_model(self):
        """Load the trained model."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
            
        self.model = joblib.load(self.model_path)
            
    def _calculate_ranking_metrics(self, df: pd.DataFrame, y_prob: np.ndarray, group_col: str = "resume_index", k: int = 10) -> Dict[str, float]:
        """
        Calculate ranking metrics (NDCG@K, MRR, Precision@K, Recall@K) grouping by query.
        """
        df_rank = df.copy()
        df_rank['score'] = y_prob
        
        ndcg_scores = []
        mrr_scores = []
        precision_at_k_scores = []
        recall_at_k_scores = []
        
        # Group by query
        grouped = df_rank.groupby(group_col)
        
        for name, group in grouped:
            # Sort by predicted score descending
            group_sorted = group.sort_values('score', ascending=False)
            
            # Ground truth relevance (binary)
            relevance = group_sorted['label'].values
            
            # Skip if no relevant items for this query
            total_relevant = sum(relevance)
            if total_relevant == 0:
                continue
                
            # Top K predictions
            top_k_relevance = relevance[:k]
            
            # NDCG@K
            ndcg = self._ndcg_at_k(relevance, k)
            ndcg_scores.append(ndcg)
            
            # MRR (Mean Reciprocal Rank)
            try:
                first_relevant_rank = np.where(relevance == 1)[0][0] + 1
                mrr_scores.append(1.0 / first_relevant_rank)
            except IndexError:
                mrr_scores.append(0.0)
                
            # Precision@K
            tp_at_k = sum(top_k_relevance)
            precision_at_k = tp_at_k / k
            precision_at_k_scores.append(precision_at_k)
            
            # Recall@K
            recall_at_k = tp_at_k / total_relevant
            recall_at_k_scores.append(recall_at_k)
                
        return {
            f"mean_ndcg_at_{k}": float(np.mean(ndcg_scores)) if ndcg_scores else 0.0,
            "mrr": float(np.mean(mrr_scores)) if mrr_scores else 0.0,
            f"mean_precision_at_{k}": float(np.mean(precision_at_k_scores)) if precision_at_k_scores else 0.0,
            f"mean_recall_at_{k}": float(np.mean(recall_at_k_scores)) if recall_at_k_scores else 0.0
        }

    def _ndcg_at_k(self, r: np.ndarray, k: int) -> float:
        """Compute NDCG at k."""
        r = np.asarray(r, dtype=float)[:k]
        dcg = np.sum(r / np.log2(np.arange(2, r.size + 2)))
        idcg = np.sum(np.ones_like(r) / np.log2(np.arange(2, r.size + 2))) # Ideal: all 1s
        if idcg == 0:
            return 0.0
        return dcg / idcg

    def _plot_visualizations(self, y_true, y_pred, y_prob):
        """Generate and save evaluation plots."""
        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
        plt.title("Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.savefig(self.output_dir / "confusion_matrix.png")
        plt.close()

        # ROC Curve
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")
        plt.savefig(self.output_dir / "roc_curve.png")
        plt.close()
        
        logger.info(f"Visualizations saved to {self.output_dir}")

    def _save_report(self, metrics: Dict[str, Any]):
        """Save evaluation report."""
        report_path = self.output_dir / "evaluation_report.json"
        
        with open(report_path, "w") as f:
            json.dump(metrics, f, indent=2)
            
        logger.info(f"Evaluation report saved to {report_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = EvaluationEngine()
    try:
        engine.evaluate()
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
