"""
Data Processing Engine
----------------------
Handles raw data ingestion, cleaning, and basic EDA.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DataProcessingConfig:
    """Configuration for data processing."""
    project_root: Path = Path(__file__).resolve().parents[2]
    
    @property
    def raw_data_dir(self) -> Path:
        return self.project_root / "data" / "raw"

    @property
    def interim_data_dir(self) -> Path:
        return self.project_root / "data" / "interim"


class DataProcessingEngine:
    """
    Main engine for data processing.
    Handles loading, cleaning, and persisting datasets.
    """

    def __init__(self, config: Optional[DataProcessingConfig] = None) -> None:
        self.config = config or DataProcessingConfig()

    def clean_text(self, text: str) -> str:
        """Normalize text while keeping key technical symbols."""
        if pd.isna(text):
            return ""

        cleaned = str(text).lower()
        cleaned = re.sub(r"[\r\n]+", " ", cleaned)
        # Preserve +, #, . for C++, C#, .NET, Node.js
        cleaned = re.sub(r"[^a-z0-9\s\.\+\#-]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def _load_csv(self, path: Path, **kwargs) -> pd.DataFrame:
        """Load a CSV if present, otherwise return an empty DataFrame."""
        if not path.exists():
            logger.warning("Missing dataset: %s", path)
            return pd.DataFrame()
        return pd.read_csv(path, **kwargs)

    def load_raw_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load raw resume, job, and skill datasets."""
        resumes = self._load_csv(self.config.raw_data_dir / "resume_datasets_full.csv", on_bad_lines="skip")
        if resumes.empty:
            resumes = self._load_csv(self.config.raw_data_dir / "resume_dataset.csv")

        jobs = self._load_csv(self.config.raw_data_dir / "job_description_dataset.csv")
        skills = self._load_csv(self.config.raw_data_dir / "skill_dataset.csv")
        
        return resumes, jobs, skills

    def preprocess_resumes(self, resumes: pd.DataFrame) -> pd.DataFrame:
        """Standardize resume dataset."""
        if resumes.empty:
            return pd.DataFrame(columns=["resume_id", "resume_text", "category"])

        text_col = next((c for c in ["Resume_str", "Resume_html", "Resume", "resume_text"] if c in resumes.columns), None)
        if text_col is None:
            resumes["resume_text"] = ""
        else:
            resumes["resume_text"] = resumes[text_col].fillna("").astype(str)

        if "resume_id" not in resumes.columns:
            resumes["resume_id"] = range(1, len(resumes) + 1)

        resumes["resume_text"] = resumes["resume_text"].apply(self.clean_text)
        resumes = resumes[resumes["resume_text"].str.len() > 50].copy()

        category_col = "Category" if "Category" in resumes.columns else None
        resumes["category"] = resumes[category_col].fillna("unknown").astype(str) if category_col else "unknown"
        
        return resumes[["resume_id", "resume_text", "category"]].drop_duplicates(subset=["resume_text"]).reset_index(drop=True)

    def preprocess_jobs(self, jobs: pd.DataFrame) -> pd.DataFrame:
        """Standardize job dataset."""
        if jobs.empty:
            return pd.DataFrame(columns=["job_id", "job_text"])

        text_col = next((c for c in ["Job Description", "description", "job_text"] if c in jobs.columns), None)
        if text_col is None:
            jobs["job_text"] = ""
        else:
            jobs["job_text"] = jobs[text_col].fillna("").astype(str)

        if "job_id" not in jobs.columns:
            jobs["job_id"] = range(1, len(jobs) + 1)

        jobs["job_text"] = jobs["job_text"].apply(self.clean_text)
        jobs = jobs[jobs["job_text"].str.len() > 50].copy()
        
        return jobs[["job_id", "job_text"]].drop_duplicates(subset=["job_text"]).reset_index(drop=True)

    def preprocess_skills(self, skills: pd.DataFrame) -> pd.DataFrame:
        """Standardize skill list."""
        if skills.empty:
            return pd.DataFrame(columns=["skill"])

        col = "skill" if "skill" in skills.columns else ("Skill" if "Skill" in skills.columns else skills.columns[0])
        skills = skills[[col]].rename(columns={col: "skill"})
        skills["skill"] = skills["skill"].astype(str).str.lower().str.strip()
        skills = skills[skills["skill"].str.len() > 1]
        
        return skills.drop_duplicates(subset=["skill"]).reset_index(drop=True)

    def run(self) -> None:
        """Execute preprocessing pipeline."""
        logger.info("Starting Data Processing Engine...")
        self.config.interim_data_dir.mkdir(parents=True, exist_ok=True)

        resumes_raw, jobs_raw, skills_raw = self.load_raw_data()
        
        resumes = self.preprocess_resumes(resumes_raw)
        jobs = self.preprocess_jobs(jobs_raw)
        skills = self.preprocess_skills(skills_raw)

        resumes.to_csv(self.config.interim_data_dir / "resumes_clean.csv", index=False)
        jobs.to_csv(self.config.interim_data_dir / "jobs_clean.csv", index=False)
        skills.to_csv(self.config.interim_data_dir / "skills_clean.csv", index=False)

        logger.info(f"Saved cleaned datasets to {self.config.interim_data_dir}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    engine = DataProcessingEngine()
    engine.run()
