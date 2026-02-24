from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import pandas as pd
import numpy as np
import logging
import time

from src.feature_engineering.engine import FeatureEngine
from src.matching.engine import MatchingEngine
from src.matching.ranking import RankingEngine
from src.utils.caching import ModelCache
from src.app_logging.logger import pred_logger, perf_logger
from src.utils.security import SecurityUtils

logger = logging.getLogger(__name__)

class InferencePipeline:
    """
    Production Inference Pipeline.
    Orchestrates the flow from raw data to ranked recommendations.
    """
    
    def __init__(self):
        self.feature_engine = FeatureEngine()
        self.matching_engine = MatchingEngine()
        self.ranking_engine = RankingEngine()
        self.cache = ModelCache()
        
        # Initialize resources
        self._warmup()

    def _warmup(self):
        """Preload heavy models."""
        logger.info("Warming up Inference Pipeline...")
        # FeatureEngine lazily loads the embedding model
        self.feature_engine._load_embedding_model()

    def recommend(self, resume_input: str, job_description: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Generate recommendations for a resume against a job description.
        
        Args:
            resume_input: Path to resume file OR raw text
            job_description: Job description text
            
        Returns:
            Dict containing ranked results and metadata
        """
        start_time = time.time()
        
        try:
            # 1. Validation & Security
            if Path(resume_input).exists():
                if not SecurityUtils.is_safe_path(resume_input):
                     raise ValueError("Invalid resume path")
                 
            # 2. Extract & Parse Resume
            # Using the enhanced ResumeParser which handles Files (PDF/DOCX) + NLP
            from src.resume_processing.parser import ResumeParser
            parser = ResumeParser()
            resume_data = parser.parse(resume_input)
            
            resume_text = resume_data['raw_text']
            clean_resume = resume_data['clean_text']
            
            # 3. Process Job Description
            from src.resume_processing.parser import JobDescriptionParser
            jd_parser = JobDescriptionParser()
            job_data_extracted = jd_parser.parse(job_description)
            clean_job = job_data_extracted['clean_text']
            
            # 4. Feature Extraction
            emb_model = self.feature_engine.embedding_model
            if not emb_model:
                self.feature_engine._load_embedding_model()
                emb_model = self.feature_engine.embedding_model
            
            # Embeddings (Using clean text from NLP processor)
            resume_emb = emb_model.encode([clean_resume])[0]
            job_emb = emb_model.encode([clean_job])[0]
            
            # Similarity
            from sklearn.metrics.pairwise import cosine_similarity
            semantic_score = float(cosine_similarity(resume_emb.reshape(1, -1), job_emb.reshape(1, -1))[0][0])
            
            # Skills
            resume_skills = set(resume_data['skills'])
            job_skills = set(job_data_extracted['required_skills'])
            
            # Feature Dict
            features = {
                "embedding_similarity": semantic_score,
                "skill_overlap_count": len(resume_skills.intersection(job_skills)),
                "skill_match_ratio": len(resume_skills.intersection(job_skills)) / len(job_skills) if job_skills else 0,
                "experience_match": 1.0 if resume_data['years_of_experience'] >= job_data_extracted['experience_required'] else 0.5
            }
            
            # 5. Matching & Scoring
            candidate_info = {
                "id": resume_data.get('contact_info', {}).get('email', 'anonymous_candidate'),
                "skills": list(resume_skills),
                "years_of_experience": resume_data['years_of_experience'],
                "education_level": resume_data['education'][0]['degree'] if resume_data['education'] else "Unknown"
            }
            job_info = {
                "id": "target_job",
                "required_skills": list(job_skills),
                "experience_required": job_data_extracted['experience_required'],
                "education_level": "Bachelor" 
            }
            
            match_result = self.matching_engine.match_candidate_to_job(
                candidate_info, job_info, features
            )
            
            # 6. Advanced Ranking
            ranked = self.ranking_engine.rank_candidates(
                [{
                    "id": candidate_info["id"],
                    "model_probability": match_result.overall_score / 100.0, 
                    "embedding_similarity": semantic_score,
                    "skill_match_ratio": features["skill_match_ratio"],
                    "experience_score": features["experience_match"],
                    "explanation": match_result.reasoning
                }]
            )
            
            result = ranked[0]
            
            # 7. Logging & Return
            latency = time.time() - start_time
            perf_logger.info(json.dumps({"endpoint": "recommend", "latency": latency}))
            
            return {
                "status": "success",
                "latency_ms": round(latency * 1000, 2),
                "match": {
                    "score": result["hybrid_score"],
                    "breakdown": result["score_breakdown"],
                    "entities": resume_data['entities'],
                    "reason": result["explanation"],
                    "missing_skills": list(job_skills - resume_skills)
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    from src.app_logging.logger import LoggerSetup
    LoggerSetup.setup()
    pipeline = InferencePipeline()
    # Test
    print(pipeline.recommend("Python Developer with 5 years experience", "Need Python Expert"))
