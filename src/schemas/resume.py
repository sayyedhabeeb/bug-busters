from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict
from datetime import datetime

class Education(BaseModel):
    degree: str
    institution: Optional[str] = None
    year: Optional[int] = None

class WorkExperience(BaseModel):
    title: str
    company: Optional[str] = None
    duration_months: Optional[int] = None
    description: Optional[str] = None

class ResumeSchema(BaseModel):
    """
    Strict validation schema for Resume data.
    """
    resume_id: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[WorkExperience] = Field(default_factory=list)
    clean_text: str = Field(..., min_length=50, description="Cleaned resume text content")
    
    # Metadata
    parsed_at: datetime = Field(default_factory=datetime.utcnow)
    file_source: str
    
    @validator('skills')
    def validate_skills(cls, v):
        return [s.lower().strip() for s in v if s and len(s) > 1]

class ResumeFeatureVector(BaseModel):
    """
    Schema for the engineered feature vector used in inference.
    """
    resume_id: str
    tfidf_vector: List[float]
    embedding: List[float] # 384-dim
    years_experience: float
    skill_count: int
    education_level: int # Ordinal encoded
