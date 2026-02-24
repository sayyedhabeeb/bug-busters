from aif360.datasets import BinaryLabelDataset
from aif360.metrics import ClassificationMetric
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class FairnessMonitor:
    """
    Monitors AI Fairness metrics using AIF360.
    Calculates Disparate Impact, Statistical Parity, etc.
    """
    
    def __init__(self):
        pass

    def check_bias(self, 
                   predictions_df: pd.DataFrame, 
                   sensitive_attribute: str = "gender",
                   privileged_group: Any = "Male",
                   unprivileged_group: Any = "Female",
                   outcome_col: str = "prediction") -> Dict[str, Any]:
        """
        Calculate fairness metrics for a batch of predictions using AIF360.
        """
        if sensitive_attribute not in predictions_df.columns:
            return {"error": f"Attribute {sensitive_attribute} not found in data."}

        try:
            # Prepare AIF360 BinaryLabelDataset
            df_aif = predictions_df[[sensitive_attribute, outcome_col]].copy()
            
            # Binary encoding for AIF360 (assuming string inputs)
            # Find unique values to map to 1/0 if needed, but let's assume valid binary or categorical
            # To be safe, we'll map them based on privileged/unprivileged
            df_aif[sensitive_attribute] = df_aif[sensitive_attribute].map({
                privileged_group: 1, 
                unprivileged_group: 0
            })
            
            dataset = BinaryLabelDataset(
                df=df_aif,
                label_names=[outcome_col],
                protected_attribute_names=[sensitive_attribute]
            )

            # Calculation using AIF360 ClassificationMetric (or simple DatasetMetric)
            # For DIR and SPD, DatasetMetric is enough, but ClassificationMetric covers more.
            # Here we use ClassificationMetric by comparing dataset with itself as 'prediction'
            metric = ClassificationMetric(
                dataset, dataset, 
                unprivileged_groups=[{sensitive_attribute: 0}],
                privileged_groups=[{sensitive_attribute: 1}]
            )

            dir_val = metric.disparate_impact()
            spd_val = metric.statistical_parity_difference()
            eod_val = metric.equal_opportunity_difference()

            metrics = {
                "privileged_group": privileged_group,
                "unprivileged_group": unprivileged_group,
                "disparate_impact_ratio": float(dir_val),
                "statistical_parity_difference": float(spd_val),
                "equal_opportunity_difference": float(eod_val),
                "bias_detected": not (0.8 <= dir_val <= 1.25)
            }
            
            if metrics["bias_detected"]:
                logger.warning(f"AIF360 Analysis: Potential bias detected for {sensitive_attribute}: DIR={dir_val:.2f}")
                
            return metrics
            
        except Exception as e:
            logger.error(f"Fairness check failed: {e}")
            # Fallback to simple calculation if AIF360 fails
            return self._fallback_check_bias(predictions_df, sensitive_attribute, privileged_group, unprivileged_group, outcome_col)

    def _fallback_check_bias(self, df, attr, priv, unpriv, outcome) -> Dict[str, Any]:
        """Simple fallback if AIF360 integration fails."""
        p_df = df[df[attr] == priv]
        u_df = df[df[attr] == unpriv]
        if p_df.empty or u_df.empty: return {"warning": "Insufficient data"}
        
        rate_p = p_df[outcome].mean()
        rate_u = u_df[outcome].mean()
        dir_val = rate_u / rate_p if rate_p > 0 else 0
        
        return {
            "disparate_impact_ratio": float(dir_val),
            "bias_detected": not (0.8 <= dir_val <= 1.25),
            "method": "fallback"
        }

    def generate_report(self, history_df: pd.DataFrame) -> str:
        """Generate a textual summary of fairness over time."""
        # TODO: Implement trend analysis
        return "Fairness analysis reporting not fully implemented yet."
