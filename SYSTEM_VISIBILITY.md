# System Connectivity & Visibility Guide

This document explains exactly how your trained model is connected to the UI and how you can verify its "work" through logs.

## 1. Where the Connection Happens

### A. Backend → Model ([services.py](file:///c:/Users/SAYYED%20HABEEB/Desktop/Bug%20busters-project/src/api/services.py))
- **Loading**: Inside `load_resources()`, the system strictly loads `trained_model.pkl`. 
- **Inference**: Inside `predict_and_rank()`, the system extracts 10 features from your resume/job text and calls `self.xgb_model.predict_proba(df_features)`.

### B. API → UI ([Candidates.jsx](file:///c:/Users/SAYYED%20HABEEB/Desktop/Bug%20busters-project/frontend/src/pages/RecruiterPortal/Candidates.jsx))
- **Request**: The UI sends the `job_id` to `http://localhost:8000/api/recommend`.
- **Recognition**: The UI specifically looks for the `score` field in the JSON response. This score is values between `0.0` and `1.0` (e.g., `0.85` becomes `85% Match`).

---

## 2. How to See the Logs

To see the system "thinking" and analyzing code, watch your **Backend Terminal** (where the API is running).

### A. Recommendation Logs (Detailed & Summary)
Whenever a comparison is made, you will see a detailed breakdown:
```text
[AI XGBOOST ENGINE] Comparison: Candidate(26) vs Job(Backend Engineer)
+-------------------------+------------+------------+
| ML COMPONENT            | RAW DATA   | MATCH %    |
+-------------------------+------------+------------+
| TF-IDF Keywords         | 0.2597     | 26.0%      |
| SBERT Semantic          | 0.3089     | 30.9%      |
| ...                     | ...        | ...        |
+-------------------------+------------+------------+
| XGBOOST FINAL RANK      | 0.9750     | 97.5%      |
+-------------------------+------------+------------+
```

After all comparisons are done, you get a clean **Summary Table**:
```text
[AI RECOMMENDATION SUMMARY] Top Jobs for: Habeeb
+-----------------------------------+---------------+
| JOB TITLE                         | MATCH SCORE   |
+-----------------------------------+---------------+
| Backend Engineer                  |         97.5% |
| Senior Python Developer           |         97.5% |
+-----------------------------------+---------------+
```

### B. Resume Analysis Logs
When a candidate uploads a resume, you will see the extraction results:
```text
INFO:bug_busters_api:--- Resume Analysis Complete [User: 5] ---
INFO:bug_busters_api:Skills Extracted: ['Python', 'SQL', 'FastAPI']
INFO:bug_busters_api:Experience: 4 years
```

---

## 3. How the UI "Recognizes" the Model
The UI doesn't just show numbers; it uses the model's **Confidence Logic**:
1. It displays **"Ranked by trained XGBoost model"** in the header.
2. It uses a color-coded system based on the model score:
   - **Green**: Score > 80% (High Confidence)
   - **Blue/Primary**: Score > 50% (Medium Confidence)
   - **Amber**: Score < 50% (Low Confidence)
3. It displays the `explanation` field (Logic) which is generated from the model's feature weights.
