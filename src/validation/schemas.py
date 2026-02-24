"""
Data validation schemas using Pydantic for type safety and validation.
Ensures all inputs/outputs meet expected formats and constraints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime


class ResumeData(BaseModel):
    """Validated resume data structure."""
    resume_id: str = Field(..., description="Unique resume identifier")
    candidate_name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    raw_text: str = Field(..., min_length=50, description="Full resume text")
    skills: List[str] = Field(default_factory=list)
    experience_years: float = Field(ge=0, le=70, default=0.0)
    education_level: Optional[str] = None
    location: Optional[str] = None
    remote_willing: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "resume_id": "RES_001",
                "candidate_name": "John Doe",
                "email": "john@example.com",
                "raw_text": "Experienced software engineer with 5 years...",
                "skills": ["Python", "SQL", "AWS"],
                "experience_years": 5.0,
                "education_level": "Bachelor's",
                "location": "San Francisco",
                "remote_willing": True
            }
        }


class JobDescription(BaseModel):
    """Validated job description structure."""
    job_id: str = Field(..., description="Unique job identifier")
    job_title: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    raw_text: str = Field(..., min_length=50)
    required_skills: List[str] = Field(default_factory=list)
    experience_required: float = Field(ge=0, le=50, default=0.0)
    salary_min: Optional[float] = Field(ge=0)
    salary_max: Optional[float] = Field(ge=0)
    location: Optional[str] = None
    remote_available: bool = False
    seniority_level: Optional[str] = None  # Junior, Mid, Senior
    job_type: str = Field(default="Full-time")  # Full-time, Contract, Part-time
    
    @validator('salary_max')
    def salary_range_valid(cls, v, values):
        if v and 'salary_min' in values and values['salary_min']:
            if v < values['salary_min']:
                raise ValueError('salary_max must be >= salary_min')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "JOB_001",
                "job_title": "Senior Python Developer",
                "company": "Tech Corp",
                "raw_text": "We are looking for a senior Python developer...",
                "required_skills": ["Python", "AWS", "Docker"],
                "experience_required": 5.0,
                "salary_min": 100000,
                "salary_max": 150000,
                "location": "San Francisco",
                "remote_available": True,
                "seniority_level": "Senior",
                "job_type": "Full-time"
            }
        }


class RecommendationRequest(BaseModel):
    """Validated recommendation request."""
    resume_index: int = Field(..., ge=0)
    top_n: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(default=0.0, ge=0, le=1.0)
    filters: Optional[Dict[str, Any]] = None


class RecommendationResponse(BaseModel):
    """Validated recommendation response."""
    resume_id: str
    job_id: str
    match_score: float = Field(ge=0, le=1.0)
    match_probability: float = Field(ge=0, le=1.0)
    reasoning: Dict[str, Any]  # Explain why this match
    confidence_level: str  # high, medium, low
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchPredictionRequest(BaseModel):
    """Batch prediction request."""
    resume_ids: List[str]
    top_n: int = Field(default=5, ge=1, le=50)


class HealthCheckResponse(BaseModel):
    """API health check response."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_version: Optional[str] = None
    database_connected: bool = False


class ErrorResponse(BaseModel):
    """Standard error response."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
