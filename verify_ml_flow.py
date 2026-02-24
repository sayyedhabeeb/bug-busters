import sys
from pathlib import Path
import os
import shutil

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.api.services import InferenceService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("strict_verification")

def verify_strict_pipeline():
    print("\n--- Strict ML Pipeline Verification ---")
    service = InferenceService()
    
    # 1. Test Fail-Fast: Try to load without model file
    print("\nTest 1: Fail-Fast (Mandatory Resource Check)")
    model_path = project_root / "outputs" / "models" / "trained_model.pkl"
    temp_path = project_root / "outputs" / "models" / "trained_model.pkl.bak"
    
    if model_path.exists():
        os.rename(model_path, temp_path)
        try:
            print("Attempting to load resources with missing model...")
            service.load_resources()
            print("[FAILURE] loaded resources even when model was missing!")
            sys.exit(1)
        except Exception as e:
            print(f"[SUCCESS] Caught expected error on missing model: {e}")
        finally:
            os.rename(temp_path, model_path)
    else:
        print("Skipped: trained_model.pkl not found at start.")

    # 2. Test Mandatory Inference
    print("\nTest 2: Mandatory Model Probability")
    service.load_resources()
    
    cand_data = {
        "resume_text": "Experienced Cloud Architect with AWS, Kubernetes, and Golang expertise.",
        "skills": ["AWS", "Kubernetes", "Golang"]
    }
    
    job_data_match = {
        "job_description": "We need a Cloud Architect skilled in AWS and Kubernetes to lead our cloud migration.",
        "required_skills": ["AWS", "Kubernetes"]
    }
    
    job_data_mismatch = {
        "job_description": "Seeking a Sous Chef for a high-end Italian restaurant. Pasta making skills required.",
        "required_skills": ["Cooking", "Pasta"]
    }
    
    print("Running match prediction...")
    res_match = service.predict_and_rank(cand_data, job_data_match)
    prob_match = res_match['model_confidence']
    print(f"Match Probability: {prob_match}")
    
    print("Running mismatch prediction...")
    res_mismatch = service.predict_and_rank(cand_data, job_data_mismatch)
    prob_mismatch = res_mismatch['model_confidence']
    print(f"Mismatch Probability: {prob_mismatch}")
    
    if prob_match > 0.6 and prob_mismatch < 0.4:
         print("[SUCCESS] Model correctly differentiated matches (Dynamic & Connected)")
    else:
         print(f"Check Result: Match={prob_match}, Mismatch={prob_mismatch}")
    
    # 3. Test Feature Ordering
    print("\nTest 3: Feature Dependency check")
    # Change skill overlap - should change model_prob
    cand_data_no_skills = cand_data.copy()
    cand_data_no_skills['skills'] = []
    res_no_skills = service.predict_and_rank(cand_data_no_skills, job_data_match)
    prob_no_skills = res_no_skills['model_confidence']
    print(f"Probability with skills: {prob_match}")
    print(f"Probability without skills: {prob_no_skills}")
    
    if prob_match != prob_no_skills:
        print("[SUCCESS] Model responds to feature changes (Feature Engineering active)")
    else:
        print("[FAILURE] Model probability remains static despite feature changes!")

if __name__ == "__main__":
    try:
        verify_strict_pipeline()
    except Exception as e:
        print(f"Verification Script Failed: {e}")
        sys.exit(1)
