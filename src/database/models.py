from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum, LargeBinary
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(Enum(UserRole), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False) # Simple plain-text as per request
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="recruiter", uselist=False)
    candidate_profile = relationship("Candidate", back_populates="user", uselist=False)

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(255))
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Relationships
    recruiter = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    description = Column(LONGTEXT, nullable=False)
    skills = Column(JSON) 
    experience_required = Column(Integer, default=0)
    location = Column(String(255), default="Remote")
    salary_range = Column(String(255), default="N/A")
    job_type = Column(String(255), default="Full-time")
    embedding = Column(JSON) 
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    resume_text = Column(LONGTEXT, nullable=True) 
    resume_path = Column(String(255), nullable=True)
    cv_content = Column(LargeBinary, nullable=True)
    cv_filename = Column(String(255), nullable=True)
    skills = Column(JSON, nullable=True)
    experience_years = Column(Integer)
    preferred_role = Column(String(255))
    embedding = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="candidate_profile")
    applications = relationship("Application", back_populates="candidate")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"))
    match_score = Column(Integer)
    xgboost_score = Column(Float, nullable=True) # Persist raw model prediction
    match_drivers = Column(JSON, nullable=True) # Persist SHAP-based insights
    status = Column(String(50), default="Applied")
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
