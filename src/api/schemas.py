from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional, Any
from enum import Enum

class UserRole(str, Enum):
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str
    industry: Optional[str] = None # For recruiters
    experience_level: Optional[int] = 0 # For candidates
    preferred_role: Optional[str] = None # For candidates

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: Any

    class Config:
        from_attributes = True

class Candidate(BaseModel):
    id: str
    resume_text: Optional[str] = None
    skills: List[str] = []
    experience_years: int = 0
    
class JobRequest(BaseModel):
    job_id: str
    job_description: Optional[str] = None
    required_skills: Optional[List[str]] = []
    top_k: int = 10

class MatchResult(BaseModel):
    id: str
    name: str = "Unknown"
    skills: List[str] = []
    experience_years: int = 0
    rank: int
    score: float
    score_breakdown: Dict[str, float]
    explanation: Optional[str] = None

class RecommendationResponse(BaseModel):
    job_id: str
    matches: List[MatchResult]
    processing_time_ms: float

class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    experience_required: int = 0
    location: Optional[str] = "Remote"
    salary_range: Optional[str] = "N/A"
    job_type: Optional[str] = "Full-time"
    recruiter_id: int
    
class CandidateCreate(BaseModel):
    resume_text: str
    skills: List[Optional[str]] = []
    experience_years: Optional[int] = 0
