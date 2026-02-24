import logging
import json
from pathlib import Path
from typing import Optional, Any, List
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from src.api.schemas import (
    JobRequest, RecommendationResponse, MatchResult, 
    JobCreate, CandidateCreate, UserCreate, UserLogin, UserResponse
)
from src.api.services import InferenceService, RecruitmentService
from src.resume_processing.parser import ResumeParser
from src.database.connection import get_db, DatabaseManager
from src.database.models import User, Company, Job, Candidate, Application, UserRole

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bug_busters_api")

# Singleton Services
service = InferenceService()
recruitment_service = RecruitmentService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: Database setup and model loading."""
    logger.info("Startup: Initializing systems...")
    try:
        DatabaseManager.create_tables()
        # Use standardized paths for resources
        service.load_resources()
        logger.info("Startup: Systems ready.")
    except Exception as e:
        logger.error(f"Startup Failed: {e}")
        raise e
    yield

app = FastAPI(title="Bug-Busters API", version="3.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return recruitment_service.add_user(db, user)

@app.post("/api/auth/login", response_model=UserResponse)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = recruitment_service.authenticate(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return db_user

@app.get("/api/companies")
async def get_companies(db: Session = Depends(get_db)):
    return recruitment_service.get_companies(db)

@app.post("/api/jobs")
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    return recruitment_service.add_job(db, job, service)

@app.get("/api/jobs")
async def get_jobs(db: Session = Depends(get_db)):
    return recruitment_service.get_jobs(db)

@app.put("/api/jobs/{job_id}")
async def update_job(job_id: int, job_data: JobCreate, db: Session = Depends(get_db)):
    return recruitment_service.update_job(db, job_id, job_data, service.embedding_model)

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    return recruitment_service.delete_job(db, job_id)

@app.get("/api/recruiter/stats")
async def get_recruiter_stats(db: Session = Depends(get_db)):
    return recruitment_service.get_recruiter_stats(db, service)

@app.post("/api/recommend", response_model=RecommendationResponse)
async def recommend(request: JobRequest, db: Session = Depends(get_db)):
    # Custom recommendation logic using standardized InferenceService
    return service.get_recommendations(request, db)

@app.get("/api/recommend/jobs/{user_id}")
async def get_job_recommendations(user_id: int, db: Session = Depends(get_db)):
    return recruitment_service.get_job_recommendations(user_id, db, service)

@app.get("/api/candidates/{candidate_id}/cv")
async def get_candidate_cv(candidate_id: str, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate or not candidate.cv_content:
        raise HTTPException(status_code=404, detail="CV not found")
    
    return Response(
        content=candidate.cv_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={candidate.cv_filename or 'cv.pdf'}"
        }
    )

@app.get("/api/candidates/me/{user_id}")
async def get_candidate_profile(user_id: int, db: Session = Depends(get_db)):
    candidate = recruitment_service.get_candidate(db, user_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    return {
        "id": candidate.id,
        "name": user.name,
        "email": user.email,
        "preferred_role": candidate.preferred_role,
        "experience_years": candidate.experience_years,
        "skills": candidate.skills or [],
        "resume_path": candidate.resume_path
    }

@app.post("/api/applications")
async def apply_to_job(request: dict, db: Session = Depends(get_db)):
    user_id = request.get("user_id")
    job_id = request.get("job_id")
    score = request.get("score", 0.0)
    
    if not user_id or not job_id:
        raise HTTPException(status_code=400, detail="User ID and Job ID required")
        
    return recruitment_service.apply(db, user_id, job_id, score)

@app.get("/api/applications/recruiter/{recruiter_id}")
async def get_recruiter_applications(recruiter_id: int, db: Session = Depends(get_db)):
    return recruitment_service.get_applications_for_recruiter(db, recruiter_id)

@app.post("/api/candidates/upload")
async def upload_resume(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # 1. Save File
        upload_dir = Path("uploads") / str(user_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename
        
        logger.info(f"Uploading file for user {user_id}: {file.filename}")
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
            
        # 2. Extract Text & Skills using ResumeParser
        logger.info("Initializing ResumeParser...")
        parser = ResumeParser()
        resume_data = parser.parse(str(file_path))
        
        resume_text = resume_data.get('raw_text', '')
        skills = resume_data.get('skills', [])
        years = resume_data.get('years_of_experience', 0)
        
        # 3. If skills extraction was empty, fallback to pipeline's feature engine
        if not skills:
            logger.info("No skills found by ResumeParser, falling back to FeatureEngine...")
            skills = list(service.pipeline.feature_engine._extract_skills(resume_text))
        
        # 4. Update Database
        logger.info(f"Updating candidate profile for user {user_id}...")
        candidate = recruitment_service.update_candidate(
            db, user_id, 
            resume_text=resume_text, 
            resume_path=str(file_path),
            cv_content=content,
            cv_filename=file.filename,
            skills=skills,
            experience_years=years
        )
        
        # 5. Automatic Matching
        if candidate:
            logger.info(f"Triggering automatic matching for candidate {candidate.id}...")
            recruitment_service.auto_match_candidate_to_all_jobs(db, candidate, service)
        
        logger.info(f"--- Resume Analysis Complete [User: {user_id}] ---")
        logger.info(f"Skills Extracted: {skills}")
        logger.info(f"Experience: {years} years")
        
        return {
            "message": "Resume uploaded, stored in DB, and auto-matched against all jobs!",
            "skills_extracted": skills,
            "years_of_experience": years
        }
    except Exception as e:
        logger.error(f"Upload failed for user {user_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
