from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class JobSchema(BaseModel):
    """
    Strict validation schema for Job Description data.
    """
    job_id: str
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=20)
    required_skills: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    experience_level: Optional[str] = None
    
    # Metadata
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    @validator('required_skills')
    def validate_skills(cls, v):
        return [s.lower().strip() for s in v if s.strip()]

class JobSearchQuery(BaseModel):
    """
    Schema for job search parameters.
    """
    query_text: Optional[str] = None
    skills_filter: Optional[List[str]] = None
    location_filter: Optional[str] = None
    min_experience: Optional[int] = None
    top_k: int = Field(10, ge=1, le=50)
