"""
Inference Engine
----------------
Orchestrates the end-to-end prediction pipeline for production.
Handles Resume -> Features -> Prediction -> Ranking -> Explanation.
"""

import logging
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

# Import Engines
from src.resume_processing.engine import ResumeProcessingEngine
from src.feature_engineering.engine import FeatureEngine
from src.explainability.engine import ExplainabilityEngine

logger = logging.getLogger(__name__)

class InferenceEngine:
    """
    Production-ready Inference Pipeline.
    """
    
    def __init__(self, model_path: Path = Path("outputs/models/trained_model.pkl"),
                 vectorizer_path: Path = Path("data/processed/features/tfidf_vectorizer.pkl")):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        
        self.resume_processor = ResumeProcessingEngine()
        self.feature_engine = FeatureEngine() # Needs to load vectorizer/embeddings
        self.explainer = ExplainabilityEngine(model_path=model_path)
        
        self.model = None
        self.vectorizer = None
        
        self.load_resources()

    def load_resources(self):
        """Preload heavy resources (Model, Vectorizer, Embeddings)."""
        logger.info("Loading Inference Resources...")
        
        # Load Model
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
            
        # Load Vectorizer
        if not self.vectorizer_path.exists():
             # Fallback or error - usually required for feature engineering
             logger.warning(f"Vectorizer not found at {self.vectorizer_path}. Feature Engineering might fail if not re-initialized.")
        else:
            with open(self.vectorizer_path, "rb") as f:
                self.vectorizer = pickle.load(f)
                # Inject into FeatureEngine
                self.feature_engine.vectorizer = self.vectorizer
        
        # Preload Embeddings Model
        self.feature_engine._load_embedding_model()
        
        logger.info("Inference Resources Loaded.")

    def predict(self, resume_text: str, job_texts: List[str], top_k: int = 5) -> Dict[str, Any]:
        """
        End-to-end prediction pipeline.
        
        Args:
            resume_text: Raw text of the candidate's resume.
            job_texts: List of raw job descriptions to match against.
            top_k: Number of recommendations to return.
            
        Returns:
            Dictionary with ranked jobs and explanations.
        """
        # 1. Preprocessing
        clean_resume = self._clean_text(resume_text)
        clean_jobs = [self._clean_text(job) for job in job_texts]
        
        # 2. Feature Engineering (On-the-fly)
        # We need a way to generate features for single instance without loading entire dataset
        # Creating a temporary DataFrame structure expected by FeatureEngine logic
        
        # Extract Skills (using existing logic)
        resume_skills = self.feature_engine._extract_skills(clean_resume)
        
        features_list = []
        
        # Pre-compute Resume Embedding/TF-IDF
        resume_emb = self.feature_engine.embedding_model.encode([clean_resume])[0]
        resume_tfidf = self.vectorizer.transform([clean_resume])
        
        # Batch Process Jobs
        job_embs = self.feature_engine.embedding_model.encode(clean_jobs)
        job_tfidfs = self.vectorizer.transform(clean_jobs)
        
        from sklearn.metrics.pairwise import cosine_similarity
        
        for idx, job_text in enumerate(clean_jobs):
            job_skills = self.feature_engine._extract_skills(job_text)
            
            # Calculate metrics
            tfidf_sim = float(cosine_similarity(resume_tfidf, job_tfidfs[idx])[0][0])
            emb_sim = float(cosine_similarity(resume_emb.reshape(1, -1), job_embs[idx].reshape(1, -1))[0][0])
            
            shared_skills = resume_skills.intersection(job_skills)
            skill_match_ratio = len(shared_skills) / len(job_skills) if job_skills else 0.0
            
            resume_words = set(clean_resume.split())
            job_words = set(job_text.split())
            keyword_overlap = len(resume_words.intersection(job_words)) / len(job_words) if job_words else 0.0
            
            features_list.append({
                "tfidf_similarity": tfidf_sim,
                "embedding_similarity": emb_sim,
                "skill_overlap_count": len(shared_skills),
                "skill_match_ratio": skill_match_ratio,
                "keyword_overlap": keyword_overlap,
                "resume_word_count": len(resume_words),
                "job_word_count": len(job_words)
            })
            
        df_features = pd.DataFrame(features_list)
        
        # 3. Prediction
        # Ensure columns match model expectation
        # We might need to filter columns if model has feature_names_in_
        if hasattr(self.model, "feature_names_in_"):
            # Ensure order and existence
            missing_cols = set(self.model.feature_names_in_) - set(df_features.columns)
            for col in missing_cols:
                df_features[col] = 0.0 # Default for missing features
            
            # Reorder columns
            df_features = df_features[self.model.feature_names_in_]
            
        probs = self.model.predict_proba(df_features)[:, 1]
        
        # 4. Ranking
        rank_results = []
        for idx, prob in enumerate(probs):
            rank_results.append({
                "job_index": idx,
                "score": float(prob),
                "features": df_features.iloc[idx].to_dict()
            })
            
        # Sort by Score
        rank_results.sort(key=lambda x: x["score"], reverse=True)
        top_results = rank_results[:top_k]
        
        # 5. Explainability
        final_output = []
        for res in top_results:
            explanation_res = self.explainer.explain_local(res["features"])
            final_output.append({
                "job_index": res["job_index"],
                "score": res["score"],
                "explanation": explanation_res["explanation"]
            })
            
        return {
            "resume_processed": True,
            "jobs_evaluated": len(job_texts),
            "recommendations": final_output
        }

    def _clean_text(self, text: str) -> str:
        """Clean text for vectorization."""
        import re
        text = str(text).lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Dummy Test
    # engine = InferenceEngine()
    # print(engine.predict("Python Data Scientist", ["Looking for Python Data Scientist", "Nurse"]))
    pass
