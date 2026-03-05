
import sys
import os
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
project_root = Path(__file__).resolve().parents[0]
sys.path.append(str(project_root))

from src.api.services import InferenceService
from src.database.models import User, Job, Candidate

# Mock candidate and job
cand_data = {
    "skills": ["Git", "Machine Learning", "MySQL", "Python", "SQL"],
    "resume_text": "I am a software engineer with experience in Python, Machine Learning, and SQL databases like MySQL. I use Git for version control.",
    "experience_years": 5
}

job_data = {
    "job_title": "Data Scientist",
    "job_description": "We are looking for a Data Scientist with skills in Python, Machine Learning, Pandas, TensorFlow, and NumPy.",
    "required_skills": ["Python", "Machine Learning", "Pandas", "TensorFlow", "NumPy"],
    "experience_required": 3
}

service = InferenceService()
service.load_resources()

print("--- DIAGNOSTIC START ---")
result = service.predict_and_rank(cand_data, job_data)

print(f"Final Score: {result['final_score']}")
print(f"XGBoost Score: {result['xgboost_score']}")
print(f"Score Breakdown: {result['score_breakdown']}")
print(f"Skill Gap: {result['skill_gap']}")
print("--- DIAGNOSTIC END ---")
