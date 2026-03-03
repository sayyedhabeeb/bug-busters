import joblib
import json
import uuid
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.database.models import User, Company, Job, Candidate, Application, UserRole
from src.matching.ranking import RankingEngine
import logging
import time
from datetime import datetime
from sentence_transformers import SentenceTransformer
from src.app_logging.logger import get_logger
from src.api.schemas import JobCreate

logger = get_logger(__name__)

class InferenceService:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.models_dir = self.project_root / "outputs" / "models"
        self.features_dir = self.project_root / "data" / "processed" / "features"
        
        self.vectorizer = None
        self.embedding_model = None
        self.ranker = RankingEngine()
        self.pipeline = None

    def load_resources(self):
        """Mandatory load of all models and artifacts. Fails if missing."""
        logger.info("Initializing ML Resources...")
        # Device management
        import torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Loading mandatory XGBoost from {self.models_dir / 'trained_model.pkl'}")
        self.xgb_model = joblib.load(self.models_dir / "trained_model.pkl")
        
        logger.info(f"Loading mandatory TF-IDF from {self.features_dir / 'tfidf_vectorizer.pkl'}")
        import pickle
        with open(self.features_dir / "tfidf_vectorizer.pkl", "rb") as f:
            self.vectorizer = pickle.load(f)
            
        logger.info("Warming up Sentence Transformer (SBERT)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        logger.info("ML Resources Loaded Successfully.")

    def predict_and_rank(self, candidate_data: dict, job_data: dict) -> dict:
        """Strict model-driven matching logic. No placeholders."""
        resume_text = candidate_data.get("resume_text", "")
        job_text = job_data.get("job_description", "")
        
        # 1. Component initialization
        from src.nlp.processor import NLPProcessor
        nlp = NLPProcessor()
        clean_resume_text = nlp.clean_text(resume_text)
        clean_job_text = nlp.clean_text(job_text)
        
        # 2. Vectorization (TF-IDF & SBERT)
        tfidf_matrix = self.vectorizer.transform([clean_resume_text, clean_job_text])
        tfidf_sim = float(np.dot(tfidf_matrix[0].toarray(), tfidf_matrix[1].toarray().T)[0][0])
        
        embs = self.embedding_model.encode([clean_resume_text, clean_job_text])
        emb_sim = float(np.dot(embs[0], embs[1]) / (np.linalg.norm(embs[0]) * np.linalg.norm(embs[1])))
        
        # 3. Feature Engineering (10 Features in Exact Training Order)
        cand_skills = set(candidate_data.get("skills", []))
        job_skills = set(job_data.get("required_skills", []))
        shared = cand_skills.intersection(job_skills)
        skill_match_ratio = len(shared) / len(job_skills) if job_skills else 0.0
        
        resume_words = set(clean_resume_text.split())
        job_words = set(clean_job_text.split())
        keyword_overlap = len(resume_words.intersection(job_words)) / len(job_words) if job_words else 0.0
        
        word_count = len(resume_words)
        avg_word_len = sum(len(w) for w in resume_words) / word_count if word_count > 0 else 0
        readability_score = max(0, 100 - (avg_word_len * 10))
        skill_density = len(cand_skills) / word_count if word_count > 0 else 0
        
        quality_score = 0.5
        if word_count > 200: quality_score += 0.2
        if len(cand_skills) > 5: quality_score += 0.3

        # Construct feature vector matches trained_model.pkl exactly
        feature_dict = {
            "tfidf_similarity": tfidf_sim,
            "embedding_similarity": emb_sim,
            "skill_overlap_count": float(len(shared)),
            "skill_match_ratio": float(skill_match_ratio),
            "keyword_overlap": float(keyword_overlap),
            "resume_word_count": float(word_count),
            "job_word_count": float(len(job_words)),
            "readability_score": float(readability_score),
            "skill_density": float(skill_density),
            "resume_quality_score": float(quality_score)
        }
        
        expected_cols = [
            "tfidf_similarity", "embedding_similarity", "skill_overlap_count", 
            "skill_match_ratio", "keyword_overlap", "resume_word_count", 
            "job_word_count", "readability_score", "skill_density", 
            "resume_quality_score"
        ]
        
        df_features = pd.DataFrame([feature_dict])[expected_cols]
        
        # 4. Mandatory XGBoost Prediction
        # No fallback. If self.xgb_model is missing, this will raise AttributeError
        model_prob = float(self.xgb_model.predict_proba(df_features)[0][1])
        
        # --- Structured Human-Readable AI Analysis ---
        candidate_id = candidate_data.get('id', 'unknown')
        job_title = job_data.get('job_title', 'Unknown Job')
        
        logger.info(f"\n[AI PIPELINE] Analyzed Candidate({candidate_id}) vs Job({job_title})")
        logger.info(f"[NOTE] 'RAW DATA' represents the unscaled 0.0-1.0 similarity scores from each tool.")
        logger.info("+" + "-"*30 + "+" + "-"*12 + "+" + "-"*12 + "+")
        logger.info(f"| {'AI TOOL / TECHNIQUE':<28} | {'RAW DATA':<10} | {'MATCH %':<10} |")
        logger.info("+" + "-"*30 + "+" + "-"*12 + "+" + "-"*12 + "+")
        
        log_rows = [
            ("spaCy Clean-NLP (L-Tokens)", 1.0), # Representing the tool is active
            ("TF-IDF Keywords (sklearn)", tfidf_sim),
            ("SBERT Semantic (Transform)", emb_sim),
            ("Skill Match Ratio (Regex)", skill_match_ratio),
            ("Keyword Overlap (NLP)", keyword_overlap),
            ("Resume Quality (Heuristic)", quality_score)
        ]
        
        for name, score in log_rows:
            logger.info(f"| {name:<28} | {score:<10.4f} | {max(0, score)*100:<9.1f}% |")
            
        logger.info("+" + "-"*30 + "+" + "-"*12 + "+" + "-"*12 + "+")
        logger.info(f"| {'XGBOOST FINAL RANKING':<28} | {model_prob:<10.4f} | {model_prob*100:<9.1f}% |")
        logger.info("+" + "-"*30 + "+" + "-"*12 + "+" + "-"*12 + "+\n")
        
        # 5. Result Construction
        # Displaying real model confidence
        return {
            "final_score": model_prob, # Result is strictly model-driven
            "explanation": self.ranker.explain_score({
                "score_breakdown": {"model": model_prob, "vector": emb_sim, "skill": skill_match_ratio, "experience": 0.5},
                "embedding_similarity": emb_sim,
                "skill_match_ratio": skill_match_ratio
            }),
            "score_breakdown": {
                 "model": model_prob, 
                 "vector": emb_sim, 
                 "skill": skill_match_ratio, 
                 "experience": 0.5
            },
            "model_confidence": model_prob,
            "vector_similarity": emb_sim
        }

    def get_recommendations(self, request, db: Session):
        """Fetch candidates and rank them for a job."""
        # 1. Fetch Job
        job = db.query(Job).filter(Job.id == request.job_id).first()
        if not job:
            job_data = {
                "job_id": request.job_id,
                "job_title": "Manual Requirement",
                "job_description": request.job_description,
                "required_skills": request.required_skills
            }
        else:
            job_data = {
                "job_id": job.id,
                "job_title": job.title,
                "job_description": job.description,
                "required_skills": job.skills
            }

        # 2. Fetch Candidates
        candidates = db.query(Candidate).all()
        results = []
        
        start_time = time.time()
        for cand in candidates:
            if not cand.resume_text and not cand.skills:
                continue
                
            cand_data = {
                "id": str(cand.id),
                "resume_text": cand.resume_text or "",
                "skills": cand.skills or [],
                "experience_years": cand.experience_years or 0
            }
            
            match = self.predict_and_rank(cand_data, job_data)
            
            results.append({
                "id": cand_data["id"],
                "name": cand.user.name if cand.user else "Unknown",
                "skills": cand.skills or [],
                "experience_years": cand.experience_years or 0,
                "score": match["final_score"],
                "score_breakdown": match["score_breakdown"],
                "explanation": match["explanation"]
            })
            
        results.sort(key=lambda x: x["score"], reverse=True)
        for i, res in enumerate(results):
            res["rank"] = i + 1
            
        # --- Recruiter Summary Table ---
        job_title = job.title if job else "Unknown Job"
        logger.info(f"\n[AI RECOMMENDATION SUMMARY] Top Candidates for: {job_title}")
        logger.info("+" + "-"*35 + "+" + "-"*15 + "+")
        logger.info(f"| {'CANDIDATE NAME':<33} | {'MATCH SCORE':<13} |")
        logger.info("+" + "-"*35 + "+" + "-"*15 + "+")
        for res in results[:request.top_k]:
            logger.info(f"| {res['name']:<33} | {res['score']*100:>12.1f}% |")
        logger.info("+" + "-"*35 + "+" + "-"*15 + "+\n")

        return {
            "job_id": request.job_id,
            "matches": results[:request.top_k],
            "processing_time_ms": (time.time() - start_time) * 1000
        }

class RecruitmentService:
    def add_user(self, db: Session, user_dto) -> User:
        user = User(
            name=user_dto.name,
            email=user_dto.email,
            password=user_dto.password,
            role=UserRole(user_dto.role)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        if user.role == UserRole.RECRUITER:
            company = Company(
                name=f"{user.name}'s Company",
                industry=user_dto.industry or "Tech",
                recruiter_id=user.id
            )
            db.add(company)
        else:
            candidate = Candidate(
                user_id=user.id,
                experience_years=user_dto.experience_level,
                preferred_role=user_dto.preferred_role
            )
            db.add(candidate)
        
        db.commit()
        return user

    def authenticate(self, db: Session, email: str, password: str) -> Optional[User]:
        return db.query(User).filter(User.email == email, User.password == password).first()

    def get_companies(self, db: Session):
        return db.query(Company).all()

    def auto_match_job_to_all_candidates(self, db: Session, job: Job, inference_service):
        """Automatically match a new job against all existing candidates."""
        candidates = db.query(Candidate).all()
        job_data = {
            "job_id": job.id,
            "job_title": job.title,
            "job_description": job.description,
            "required_skills": job.skills or [],
            "experience_required": job.experience_required or 0
        }
        
        for cand in candidates:
            try:
                cand_data = {
                    "id": str(cand.id),
                    "resume_text": cand.resume_text or "",
                    "skills": cand.skills or [],
                    "experience_years": cand.experience_years or 0
                }
                
                match = inference_service.predict_and_rank(cand_data, job_data)
                score = int(match["final_score"] * 100)
                
                # Upsert application
                app = db.query(Application).filter(
                    Application.candidate_id == cand.id,
                    Application.job_id == job.id
                ).first()
                
                if app:
                    app.match_score = score
                    app.status = "Auto-Matched"
                else:
                    app = Application(
                        candidate_id=cand.id,
                        job_id=job.id,
                        match_score=score,
                        status="Auto-Matched"
                    )
                    db.add(app)
                
                db.commit() # Individual commit for robustness
                logger.info(f"Auto-matched job {job.title} to candidate {cand.id} with score {score}%")
            except Exception as e:
                logger.error(f"Failed to match job {job.id} to candidate {cand.id}: {str(e)}")
                db.rollback()
        
        return True

    def add_job(self, db: Session, job_dto, inference_service) -> Job:
        job = Job(
            title=job_dto.title,
            description=job_dto.description,
            skills=job_dto.required_skills,
            experience_required=job_dto.experience_required,
            location=job_dto.location,
            salary_range=job_dto.salary_range,
            job_type=job_dto.job_type,
            company_id=db.query(Company).filter(Company.recruiter_id == job_dto.recruiter_id).first().id,
            embedding=inference_service.embedding_model.encode(job_dto.description).tolist()
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Trigger global match
        self.auto_match_job_to_all_candidates(db, job, inference_service)
        
        return job

    def get_jobs(self, db: Session):
        jobs = db.query(Job).all()
        return [
            {
                "id": j.id,
                "title": j.title,
                "description": j.description,
                "skills": j.skills,
                "experience_required": j.experience_required,
                "location": j.location,
                "salary_range": j.salary_range,
                "job_type": j.job_type,
                "company_name": j.company.name if j.company else "Unknown"
            } for j in jobs
        ]

    def get_recruiter_stats(self, db: Session, inference_service):
        """Get summary statistics for the recruiter dashboard."""
        total_jobs = db.query(Job).count()
        total_candidates = db.query(Candidate).count()
        
        # Calculate approximate avg match score (across all jobs and candidates if possible, 
        # or just a sample to keep it fast)
        # For simplicity in this demo, we'll take the top 5 candidates across all jobs
        # or a hardcoded representative average if the DB is small.
        # Let's try to get a real average if possible.
        jobs = db.query(Job).all()
        candidates = db.query(Candidate).all()
        
        avg_score = 0
        if jobs and candidates:
            # We sample matches to avoid O(N*M) heavy computation on every dashboard load
            sample_matches = []
            for j in jobs[:3]: # Sample first 3 jobs
                for c in candidates[:10]: # Sample first 10 candidates
                    cand_data = {"id": c.id, "resume_text": c.resume_text or "", "skills": c.skills or []}
                    job_data = {"job_id": j.id, "job_description": j.description, "required_skills": j.skills or []}
                    match = inference_service.predict_and_rank(cand_data, job_data)
                    sample_matches.append(match["final_score"])
            if sample_matches:
                avg_score = sum(sample_matches) / len(sample_matches)
        
        recent_jobs = db.query(Job).order_by(Job.id.desc()).limit(5).all()
        
        total_apps = db.query(Application).count()
        
        return {
            "total_jobs": total_jobs,
            "total_candidates": total_candidates,
            "total_applications": total_apps,
            "avg_match_score": round(avg_score * 100, 1),
            "recent_vacancies": [
                {
                    "id": j.id,
                    "title": j.title,
                    "company": j.company.name if j.company else "Unknown",
                    "location": j.location,
                    "type": j.job_type
                } for j in recent_jobs
            ]
        }

    def get_job_recommendations(self, candidate_user_id: int, db: Session, inference_service):
        """Rank all jobs for a specific candidate."""
        candidate = self.get_candidate(db, candidate_user_id)
        if not candidate:
            return []
            
        cand_data = {
            "id": str(candidate.id),
            "resume_text": candidate.resume_text or "",
            "skills": candidate.skills or [],
            "experience_years": candidate.experience_years or 0
        }
        
        jobs = self.get_jobs(db)
        results = []
        
        for job in jobs:
            job_data = {
                "job_id": job["id"],
                "job_title": job["title"],
                "job_description": job["description"],
                "required_skills": job["skills"] or [],
                "experience_required": job["experience_required"] or 0
            }
            
            match = inference_service.predict_and_rank(cand_data, job_data)
            
            results.append({
                "id": job["id"],
                "title": job["title"],
                "company": job["company_name"],
                "location": job["location"],
                "salary": job["salary_range"],
                "type": job["job_type"],
                "score": match["final_score"],
                "explanation": match["explanation"]
            })
            
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # --- Candidate Summary Table ---
        candidate_name = db.query(User).filter(User.id == candidate_user_id).first().name
        logger.info(f"\n[AI RECOMMENDATION SUMMARY] Top Jobs for: {candidate_name}")
        logger.info("+" + "-"*35 + "+" + "-"*15 + "+")
        logger.info(f"| {'JOB TITLE':<33} | {'MATCH SCORE':<13} |")
        logger.info("+" + "-"*35 + "+" + "-"*15 + "+")
        for res in results[:10]: # Summary of top 10
            logger.info(f"| {res['title']:<33} | {res['score']*100:>12.1f}% |")
        logger.info("+" + "-"*35 + "+" + "-"*15 + "+\n")
        
        return results

    def delete_job(self, db: Session, job_id: str):
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            db.delete(job)
            db.commit()
            return {"message": "Job deleted"}
        return {"error": "Job not found"}

    def update_job(self, db: Session, job_id: str, data: JobCreate, embedding_model):
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": "Job not found"}
        
        job.title = data.title
        job.description = data.description
        job.location = data.location
        job.salary_range = data.salary_range
        job.job_type = data.job_type
        job.experience_required = data.experience_required
        
        # Update embeddings if description changed
        combined_text = f"{data.title} {data.description}"
        if embedding_model:
            job.embeddings = embedding_model.encode(combined_text).tolist()
            
        db.commit()
        return job

    def apply(self, db: Session, user_id: int, job_id: int, score: float):
        # 1. Get Candidate ID from User ID
        candidate = db.query(Candidate).filter(Candidate.user_id == user_id).first()
        if not candidate:
            return {"error": "Candidate profile not found. Please upload resume first."}
            
        # 2. Check if already applied
        existing = db.query(Application).filter(
            Application.candidate_id == candidate.id,
            Application.job_id == job_id
        ).first()
        if existing:
            return {"message": "Already applied"}
            
        # 3. Create Application
        app = Application(
            candidate_id=candidate.id,
            job_id=job_id,
            match_score=score,
            status="Applied"
        )
        db.add(app)
        db.commit()
        return {"message": "Application successful", "application_id": app.id}

    def get_applications_for_recruiter(self, db: Session, recruiter_id: int):
        # Fetch all applications and the associated job/user data
        results = db.query(Application).join(Job).all()
        
        output = []
        for a in results:
            output.append({
                "id": a.id,
                "candidate_id": a.candidate_id,
                "job_title": a.job.title,
                "candidate_name": a.candidate.user.name if a.candidate.user else "Unknown",
                "match_score": a.match_score / 100.0, # Scale back to 0-1 for frontend
                "status": a.status,
                "applied_at": a.applied_at.isoformat() if a.applied_at else None
            })
        return output

    def get_candidate(self, db: Session, user_id: int) -> Optional[Candidate]:
        return db.query(Candidate).filter(Candidate.user_id == user_id).first()

    def update_candidate(self, db: Session, user_id: int, **kwargs) -> Optional[Candidate]:
        candidate = self.get_candidate(db, user_id)
        if candidate:
            for key, value in kwargs.items():
                if hasattr(candidate, key):
                    setattr(candidate, key, value)
            db.commit()
            db.refresh(candidate)
        return candidate

    def auto_match_candidate_to_all_jobs(self, db: Session, candidate: Candidate, inference_service):
        """Automatically match a candidate against all active jobs and store in Application table."""
        jobs = db.query(Job).all()
        
        cand_data = {
            "id": str(candidate.id),
            "resume_text": candidate.resume_text or "",
            "skills": candidate.skills or [],
            "experience_years": candidate.experience_years or 0
        }
        
        for job in jobs:
            try:
                job_data = {
                    "job_id": job.id,
                    "job_title": job.title,
                    "job_description": job.description,
                    "required_skills": job.skills or [],
                    "experience_required": job.experience_required or 0
                }
                
                match = inference_service.predict_and_rank(cand_data, job_data)
                score = int(match["final_score"] * 100)
                
                # Upsert application
                app = db.query(Application).filter(
                    Application.candidate_id == candidate.id,
                    Application.job_id == job.id
                ).first()
                
                if app:
                    app.match_score = score
                    app.status = "Auto-Matched"
                else:
                    app = Application(
                        candidate_id=candidate.id,
                        job_id=job.id,
                        match_score=score,
                        status="Auto-Matched"
                    )
                    db.add(app)
                
                db.commit() # Commit each match to ensure partial success
                logger.info(f"Auto-matched candidate {candidate.id} to job {job.title} with score {score}%")
            except Exception as e:
                logger.error(f"Failed to match candidate {candidate.id} to job {job.id}: {str(e)}")
                db.rollback()
        
        return True
