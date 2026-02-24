"""
Feature Engineering Engine
--------------------------
Standardized module for building feature matrices (TF-IDF, Embeddings, Custom Logic).
Focuses on vectorization, similarity computation, and quality validation.
"""

from __future__ import annotations

import logging
import pickle
import numpy as np
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Set

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class FeatureEngineConfig:
    """Configuration for the Feature Engineering Engine."""
    project_root: Path = Path(__file__).resolve().parents[2]
    
    @property
    def interim_data_dir(self) -> Path:
        return self.project_root / "data" / "interim"
    
    @property
    def processed_feature_dir(self) -> Path:
        return self.project_root / "data" / "processed" / "features"
    
    @property
    def reports_dir(self) -> Path:
        return self.project_root / "outputs" / "reports"

    # Hyperparameters
    MAX_FEATURES: int = 5000
    NGRAM_RANGE: tuple = (1, 2)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"


class FeatureEngine:
    """
    Main engine for feature engineering and analysis.
    Combines logic for feature creation, EDA, and validation.
    """

    def __init__(self, config: Optional[FeatureEngineConfig] = None) -> None:
        self.config = config or FeatureEngineConfig()
        
        # Models
        self.vectorizer = TfidfVectorizer(
            max_features=self.config.MAX_FEATURES,
            ngram_range=self.config.NGRAM_RANGE,
            stop_words="english"
        )
        self.embedding_model = None  # Lazy load
        
        # Data
        self.resumes = pd.DataFrame()
        self.jobs = pd.DataFrame()
        self.skills: Set[str] = set()
        
        # State
        self.feature_matrix = pd.DataFrame()

    def load_data(self) -> None:
        """Load cleaned datasets from interim storage."""
        try:
            self.resumes = pd.read_csv(self.config.interim_data_dir / "resumes_clean.csv")
            self.jobs = pd.read_csv(self.config.interim_data_dir / "jobs_clean.csv")
            
            skill_path = self.config.interim_data_dir / "skills_clean.csv"
            if skill_path.exists():
                skills_df = pd.read_csv(skill_path)
                col = "skill" if "skill" in skills_df.columns else skills_df.columns[0]
                self.skills = set(skills_df[col].astype(str).str.lower().tolist())
            else:
                self.skills = set()
                
            logger.info(f"Loaded {len(self.resumes)} resumes, {len(self.jobs)} jobs, {len(self.skills)} skills.")
            
        except FileNotFoundError as e:
            logger.error(f"Failed to load data: {e}")
            raise


    def build_features(self) -> pd.DataFrame:
        """Generate comprehensive features (TF-IDF + Embeddings + Custom)."""
        if self.resumes.empty or self.jobs.empty:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Prepare corpus for TF-IDF
        corpus = pd.concat([self.resumes["resume_text"], self.jobs["job_text"]], ignore_index=True)
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        
        n_resumes = len(self.resumes)
        resume_tfidf = tfidf_matrix[:n_resumes]
        job_tfidf = tfidf_matrix[n_resumes:]
        
        # Prepare Embeddings
        self._load_embedding_model()
        resume_emb = self.embedding_model.encode(self.resumes["resume_text"].tolist(), show_progress_bar=True)
        job_emb = self.embedding_model.encode(self.jobs["job_text"].tolist(), show_progress_bar=True)
        
        # Calculate Similarities
        tfidf_sim = cosine_similarity(resume_tfidf, job_tfidf)
        emb_sim = cosine_similarity(resume_emb, job_emb)

        rows = []
        logger.info("Building feature rows...")
        
        for i, resume_row in self.resumes.iterrows():
            resume_text = str(resume_row["resume_text"])
            resume_words = set(resume_text.split())
            resume_skills = self._extract_skills(resume_text)

            for j, job_row in self.jobs.iterrows():
                job_text = str(job_row["job_text"])
                job_words = set(job_text.split())
                job_skills = self._extract_skills(job_text)
                
                # Custom Features
                shared_skills = resume_skills.intersection(job_skills)
                skill_match_ratio = len(shared_skills) / len(job_skills) if job_skills else 0.0
                keyword_overlap = len(resume_words.intersection(job_words)) / len(job_words) if job_words else 0.0
                
                # Composite Label (Pseudo-label if not provided)
                # Weighted: 50% TF-IDF, 30% Embeddings, 20% Skills
                score = (0.5 * tfidf_sim[i, j]) + (0.3 * emb_sim[i, j]) + (0.2 * skill_match_ratio)
                
                # Advanced Features
                # 1. Readability Score (Flesch Reading Ease approximation)
                # 206.835 - 1.015(total_words/total_sentences) - 84.6(total_syllables/total_words)
                # Simplified: longer words/sentences -> lower readability (more complex)
                word_count = len(resume_words)
                avg_word_len = sum(len(w) for w in resume_words) / word_count if word_count > 0 else 0
                readability_score = max(0, 100 - (avg_word_len * 10)) # Mock calculation
                
                # 2. Skill Density
                skill_density = len(resume_skills) / word_count if word_count > 0 else 0
                
                # 3. Resume Quality Score (Heuristic)
                # Based on length, skills, and structure
                quality_score = 0.5
                if word_count > 200: quality_score += 0.2
                if len(resume_skills) > 5: quality_score += 0.3
                
                rows.append({
                    "resume_index": i,
                    "job_index": j,
                    "tfidf_similarity": float(tfidf_sim[i, j]),
                    "embedding_similarity": float(emb_sim[i, j]),
                    "skill_overlap_count": len(shared_skills),
                    "skill_match_ratio": float(skill_match_ratio),
                    "keyword_overlap": float(keyword_overlap),
                    "resume_word_count": word_count,
                    "job_word_count": len(job_words),
                    "readability_score": readability_score,
                    "skill_density": skill_density,
                    "resume_quality_score": quality_score,
                    "score": score # Store raw score for dynamic labeling
                })

        self.feature_matrix = pd.DataFrame(rows)
        
        # Dynamic Labeling: Top 25% matches are labeled as 1 (Positive)
        # This ensures we always have positive samples for training
        threshold = self.feature_matrix["score"].quantile(0.75)
        logger.info(f"Dynamic labeling threshold (75th percentile): {threshold:.4f}")
        
        self.feature_matrix["label"] = (self.feature_matrix["score"] >= threshold).astype(int)
        
        # Clean up score column if not needed, but keep for debug
        # self.feature_matrix.drop(columns=["score"], inplace=True)
        
        return self.feature_matrix

    def validate_features(self) -> bool:
        """Validate the generated feature matrix quality."""
        df = self.feature_matrix
        if df.empty:
            logger.error("Feature matrix is empty.")
            return False
            
        # Check nulls
        null_counts = df.isnull().sum().sum()
        if null_counts > 0:
            logger.warning(f"Found {null_counts} null values in feature matrix.")
            
        # Check finiteness
        numeric_cols = df.select_dtypes(include=[np.number])
        if not np.isfinite(numeric_cols).all().all():
            logger.warning("Found infinite values in feature matrix.")
            
        logger.info("Feature validation completed.")
        return True

    def save_artifacts(self) -> None:
        """Persist feature matrix and vectorizer."""
        self.config.processed_feature_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Matrix
        out_path = self.config.processed_feature_dir / "feature_matrix.csv"
        self.feature_matrix.to_csv(out_path, index=False)
        
        # Save Vectorizer
        with open(self.config.processed_feature_dir / "tfidf_vectorizer.pkl", "wb") as f:
            pickle.dump(self.vectorizer, f)
            
        logger.info(f"Saved artifacts to {self.config.processed_feature_dir}")

    def run(self) -> None:
        """Execute the full engine pipeline."""
        logger.info("Starting Feature Engineering Engine...")
        self.load_data()
        self.build_features()
        if self.validate_features():
            self.save_artifacts()
        logger.info("Feature Engineering completed successfully.")

    def _extract_skills(self, text: str) -> Set[str]:
        """Extract skills using exact matching against knowledge base."""
        if not self.skills:
            return set()
        
        # Remove punctuation for better matching
        import re
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        text_padded = f" {text_clean} "
        
        # Simple token matching - optimized for speed
        return {skill for skill in self.skills if f" {skill} " in text_padded}

    def _load_embedding_model(self) -> None:
        """Lazy load the sentence transformer model."""
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {self.config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    engine = FeatureEngine()
    engine.run()
