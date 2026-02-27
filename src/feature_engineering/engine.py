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
        logger.info("Computing TF-IDF matrix...")
        corpus = pd.concat([self.resumes["resume_text"], self.jobs["job_text"]], ignore_index=True)
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        
        n_resumes = len(self.resumes)
        resume_tfidf = tfidf_matrix[:n_resumes]
        job_tfidf = tfidf_matrix[n_resumes:]
        
        # Prepare Embeddings
        logger.info("Computing embeddings (Sentence Transformer)...")
        self._load_embedding_model()
        resume_emb = self.embedding_model.encode(self.resumes["resume_text"].tolist(), show_progress_bar=True)
        job_emb = self.embedding_model.encode(self.jobs["job_text"].tolist(), show_progress_bar=True)
        
        # Calculate Similarities
        logger.info("Computing cosine similarities...")
        tfidf_sim = cosine_similarity(resume_tfidf, job_tfidf)
        emb_sim = cosine_similarity(resume_emb, job_emb)

        rows = []
        logger.info("Building feature rows...")
        
        # Pre-build category lookup for jobs (if 'category' column exists)
        job_has_category = "category" in self.jobs.columns
        resume_has_category = "category" in self.resumes.columns
        use_category_labels = job_has_category and resume_has_category
        
        if use_category_labels:
            logger.info("Using category-based labeling (honest labels).")
        else:
            logger.info("Category columns not found; falling back to score-based dynamic labeling.")

        # --- OPTIMIZATION: Pre-extract things that don't change in loops ---
        logger.info("Pre-calculating resume/job components...")
        res_data = []
        for _, r in self.resumes.iterrows():
            txt = str(r["resume_text"])
            res_data.append({
                "words": set(txt.split()),
                "skills": self._extract_skills(txt),
                "category": str(r.get("category", "")).strip().upper() if use_category_labels else ""
            })

        job_data = []
        for _, j in self.jobs.iterrows():
            txt = str(j["job_text"])
            job_data.append({
                "words": set(txt.split()),
                "skills": self._extract_skills(txt),
                "category": str(j.get("category", "")).strip().upper() if use_category_labels else ""
            })

        for i in range(len(self.resumes)):
            r_item = res_data[i]
            res_words = r_item["words"]
            res_skills = r_item["skills"]
            res_cat = r_item["category"]
            
            for j in range(len(self.jobs)):
                j_item = job_data[j]
                job_words = j_item["words"]
                job_skills = j_item["skills"]
                job_cat = j_item["category"]
                
                # Custom Features
                shared_skills = res_skills.intersection(job_skills)
                skill_match_ratio = len(shared_skills) / len(job_skills) if job_skills else 0.0
                keyword_overlap = len(res_words.intersection(job_words)) / len(job_words) if job_words else 0.0
                
                # Composite score
                score = (0.5 * tfidf_sim[i, j]) + (0.3 * emb_sim[i, j]) + (0.2 * skill_match_ratio)
                
                # Quality Features
                word_count = len(res_words)
                avg_word_len = sum(len(w) for w in res_words) / word_count if word_count > 0 else 0
                readability_score = max(0, 100 - (avg_word_len * 10))
                skill_density = len(res_skills) / word_count if word_count > 0 else 0
                
                quality_score = 0.5
                if word_count > 200: quality_score += 0.2
                if len(res_skills) > 5: quality_score += 0.3

                # Label
                if use_category_labels:
                    label = 1 if (res_cat == job_cat and res_cat != "") else 0
                else:
                    label = None

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
                    "score": score,
                    "label": label,
                })

        self.feature_matrix = pd.DataFrame(rows)

        if not use_category_labels:
            # ╔══════════════════════════════════════════════════════════════╗
            # ║ FIXED: Dynamic Labeling with Better Strategy                ║
            # ╚══════════════════════════════════════════════════════════════╝

            logger.info(f"Score statistics before labeling:")
            logger.info(f"  Min: {self.feature_matrix['score'].min():.4f}")
            logger.info(f"  Max: {self.feature_matrix['score'].max():.4f}")
            logger.info(f"  Mean: {self.feature_matrix['score'].mean():.4f}")
            logger.info(f"  Median: {self.feature_matrix['score'].median():.4f}")

            # Strategy 1: Use fixed similarity threshold
            # Scores > 0.6 are considered matches (reasonable for cosine similarity)
            threshold_similarity = 0.6
            labels_similarity = (self.feature_matrix["score"] > threshold_similarity).astype(int)

            # Strategy 2: Use quantile-based (top 25%)
            threshold_quantile = self.feature_matrix["score"].quantile(0.75)
            labels_quantile = (self.feature_matrix["score"] >= threshold_quantile).astype(int)

            # Choose strategy based on positive sample count
            n_positive_sim = (labels_similarity == 1).sum()
            n_positive_quant = (labels_quantile == 1).sum()

            logger.info(f"\nLabeling strategy comparison:")
            logger.info(f"  Similarity-based (> 0.6): {n_positive_sim} positive ({n_positive_sim/len(self.feature_matrix)*100:.2f}%)")
            logger.info(f"  Quantile-based (top 25%): {n_positive_quant} positive ({n_positive_quant/len(self.feature_matrix)*100:.2f}%)")

            # Use strategy that produces BOTH positive and negative samples
            if n_positive_sim > 0 and n_positive_sim < len(self.feature_matrix):
                # Use similarity-based (good balance)
                self.feature_matrix["label"] = labels_similarity
                logger.info(f"✓ Using similarity-based labeling (threshold={threshold_similarity})")
            elif n_positive_quant > 0 and n_positive_quant < len(self.feature_matrix):
                # Fallback to quantile-based
                self.feature_matrix["label"] = labels_quantile
                logger.info(f"✓ Using quantile-based labeling (threshold={threshold_quantile:.4f})")
            else:
                # Emergency fallback: just use top 25% regardless
                logger.warning(f"⚠️  WARNING: Using emergency fallback labeling!")
                self.feature_matrix["label"] = (self.feature_matrix["score"] >= self.feature_matrix["score"].quantile(0.75)).astype(int)

        # Verify labeling worked
        n_pos = (self.feature_matrix["label"] == 1).sum()
        n_neg = (self.feature_matrix["label"] == 0).sum()
        logger.info(f"\nFinal label distribution:")
        logger.info(f"  Negative (0): {n_neg:,} ({n_neg/(n_pos+n_neg)*100:.2f}%)")
        logger.info(f"  Positive (1): {n_pos:,} ({n_pos/(n_pos+n_neg)*100:.2f}%)")

        # SAFETY CHECK: Ensure we have both classes!
        if n_pos == 0 or n_neg == 0:
            raise ValueError(
                f"❌ CRITICAL: Labeling failed! Only one class present. "
                f"Positive={n_pos}, Negative={n_neg}. "
                f"Check score distribution and threshold settings."
            )
        
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
        
        import re
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        text_padded = f" {text_clean} "
        
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
