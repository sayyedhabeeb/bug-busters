"""
Model Monitoring Engine
-----------------------
Engine for monitoring model fairness and bias.
Calculates key metrics: Demographic Parity, Equal Opportunity, Disparate Impact.
"""

import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class BiasMonitor:
    """
    Monitor for detecting bias in model predictions.
    """
    
    def __init__(self, output_dir: Path = Path("outputs/reports/monitoring")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_bias(self, df: pd.DataFrame, protected_col: str, target_col: str = "label", pred_col: str = "prediction") -> Dict[str, Any]:
        """
        Analyze bias metrics for a protected attribute.
        
        Args:
            df: DataFrame containing features, true labels, and predictions.
            protected_col: Name of the column representing the protected group (e.g., 'gender', 'age_group').
            target_col: Name of the column with ground truth labels.
            pred_col: Name of the column with model predictions (binary).
            
        Returns:
            Dictionary containing bias metrics.
        """
        logger.info(f"Analyzing bias for protected attribute: {protected_col}")
        
        if protected_col not in df.columns:
            logger.warning(f"Protected attribute '{protected_col}' not found in data.")
            return {"error": f"Column {protected_col} not found"}
            
        # Define groups
        # Assume 1 is privileged, 0 is unprivileged for binary
        # Or if categorical, take majority as privileged
        unique_vals = df[protected_col].unique()
        if len(unique_vals) != 2:
             # Heuristic: If more than 2, take the most frequent as privileged vs rest
             privileged_val = df[protected_col].mode()[0]
             df['derived_protected'] = (df[protected_col] == privileged_val).astype(int)
             protected_col = 'derived_protected'
             logger.info(f"Multi-class protected attribute. Treating '{privileged_val}' as privileged (1) vs others (0).")
        else:
             # Assume 1 is privileged if numeric 0/1, else take first
             privileged_val = 1 if 1 in unique_vals else unique_vals[0]
        
        privileged_group = df[df[protected_col] == privileged_val]
        unprivileged_group = df[df[protected_col] != privileged_val]
        
        if unprivileged_group.empty:
            logger.warning("Unprivileged group is empty. Cannot calculate bias.")
            return {"error": "Unprivileged group empty"}

        # Metrics Calculation
        metrics = {}
        
        # 1. Demographic Parity (Statistical Parity)
        # P(pred=1 | privileged)
        positive_rate_priv = privileged_group[pred_col].mean()
        positive_rate_unpriv = unprivileged_group[pred_col].mean()
        
        metrics["demographic_parity_diff"] = positive_rate_unpriv - positive_rate_priv
        metrics["disparate_impact"] = positive_rate_unpriv / positive_rate_priv if positive_rate_priv > 0 else 0.0
        
        # 2. Equal Opportunity (True Positive Rate Parity)
        # P(pred=1 | y=1, privileged)
        tpr_priv = privileged_group[privileged_group[target_col] == 1][pred_col].mean()
        tpr_unpriv = unprivileged_group[unprivileged_group[target_col] == 1][pred_col].mean()
        
        metrics["equal_opportunity_diff"] = tpr_unpriv - tpr_priv
        
        # 3. Average Odds Difference
        # Average of TPR difference and FPR difference
        fpr_priv = privileged_group[privileged_group[target_col] == 0][pred_col].mean()
        fpr_unpriv = unprivileged_group[unprivileged_group[target_col] == 0][pred_col].mean()
        
        metrics["average_odds_diff"] = 0.5 * ((tpr_unpriv - tpr_priv) + (fpr_unpriv - fpr_priv))
        
        # Save Report
        self._save_report(metrics, protected_col)
        
        return metrics

    def _save_report(self, metrics: Dict[str, Any], attribute: str):
        """Save bias report."""
        report_path = self.output_dir / f"bias_report_{attribute}.json"
        
        with open(report_path, "w") as f:
            json.dump(metrics, f, indent=2)
            
        logger.info(f"Bias report saved to {report_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example usage (simulated)
    # df = pd.DataFrame({'gender': [1, 0, 1, 0], 'label': [1, 1, 0, 0], 'prediction': [1, 0, 0, 0]})
    # monitor = BiasMonitor()
    # monitor.analyze_bias(df, 'gender')
    pass
