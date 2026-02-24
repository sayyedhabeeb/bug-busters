"""
EDA Engine
----------
Enterprise-grade engine for Exploratory Data Analysis.
Provides automated data profiling, quality checks, and reporting.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class EDAEngine:
    """
    Engine for automated EDA and data quality assessment.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.interim_dir = self.project_root / "data" / "interim"
        self.reports_dir = self.project_root / "outputs" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def run_full_eda(self) -> Dict[str, Any]:
        """Execute full EDA pipeline on interim data."""
        logger.info("Starting Project-Wide EDA...")
        
        results = {}
        
        # Load Data
        try:
            resumes = pd.read_csv(self.interim_dir / "resumes_clean.csv")
            jobs = pd.read_csv(self.interim_dir / "jobs_clean.csv")
            logger.info(f"Loaded {len(resumes)} resumes and {len(jobs)} jobs.")
        except FileNotFoundError as e:
            logger.error(f"Interim data not found: {e}")
            return {"status": "error", "message": str(e)}

        # 1. Resume Analysis
        resume_stats = self._analyze_dataframe(resumes, "Resume", "resume_text")
        results["resumes"] = resume_stats
        
        # 2. Job Analysis
        job_stats = self._analyze_dataframe(jobs, "Job", "job_text")
        results["jobs"] = job_stats
        
        # 3. Save Summary Report
        self._save_markdown_report(results)
        
        logger.info("EDA Pipeline completed successfully.")
        return results

    def _analyze_dataframe(self, df: pd.DataFrame, name: str, text_col: str) -> Dict[str, Any]:
        """Analyze a specific dataframe for quality and distribution."""
        stats = {
            "total_count": len(df),
            "missing_values": df.isnull().sum().to_dict(),
        }
        
        if text_col in df.columns:
            lengths = df[text_col].astype(str).str.len()
            stats["text_stats"] = {
                "avg_length": float(lengths.mean()),
                "min_length": int(lengths.min()),
                "max_length": int(lengths.max()),
                "std_dev": float(lengths.std())
            }
            
        if "category" in df.columns:
            stats["categories"] = df["category"].value_counts().to_dict()
            
        return stats

    def _save_markdown_report(self, results: Dict[str, Any]):
        """Generate a markdown report from the results dictionary."""
        report = ["# 📊 Project EDA Summary Report\n"]
        
        for name, stats in results.items():
            report.append(f"## {name.capitalize()} Dataset")
            report.append(f"- **Total Records**: {stats['total_count']}")
            
            if "text_stats" in stats:
                ts = stats["text_stats"]
                report.append(f"- **Avg Text Length**: {ts['avg_length']:.2f} chars")
                report.append(f"- **Length Range**: {ts['min_length']} - {ts['max_length']} chars")
            
            if "categories" in stats:
                report.append("\n### Distribution by Category")
                for cat, count in stats["categories"].items():
                    report.append(f"- {cat}: {count}")
            
            report.append("\n---\n")
            
        report_path = self.reports_dir / "EDA_PROJECT_SUMMARY.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        logger.info(f"Markdown report saved to {report_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    EDAEngine().run_full_eda()
