# Automatic Resume Screening & AI Job Recommendation System

## 1. Abstract
IT companies receive a large volume of resumes for multiple technical roles. Manual screening is inefficient, error-prone, and susceptible to bias. This project presents an AI-powered automatic resume screening and job recommendation system designed for IT company recruitment management. The system leverages Natural Language Processing (NLP), semantic matching, and fairness-aware machine learning to parse resumes, match candidates to job descriptions, recommend suitable roles, and provide explainable, unbiased hiring decisions.

## 2. Problem Statement
Recruitment teams face challenges such as high resume volume, time-consuming manual screening, keyword-based ATS limitations, human bias, inconsistent resume formats, and lack of feedback to candidates. These issues lead to missed qualified applicants and inefficient hiring processes.

## 3. Objectives
- Automate resume screening for IT roles
- Perform semantic candidate–job matching beyond keywords
- Rank and recommend candidates fairly
- Suggest alternate job roles when fit is low
- Provide explainable skill-gap feedback
- Ensure ethical and bias-aware recruitment decisions

## 4. System Overview
The proposed system parses resumes and job descriptions, extracts structured information, generates semantic embeddings, computes fit scores, and recommends suitable candidates or job roles. A bias mitigation layer ensures fairness, while rule-based explanations provide transparency for recruiters and candidates.

## 5. System Modules
1. **Resume Parsing Module** (spaCy-based NLP pipeline)
2. **Job Description Analyzer**
3. **Skill Extraction & Normalization Module**
4. **Semantic Matching Engine** (MiniLM / Sentence-BERT)
5. **Fit Scoring Model** (Weighted Ensemble)
6. **Recommendation Engine** (Cosine Similarity)
7. **Bias & Fairness Module** (AIF360)
8. **Rule-Based Skill Gap & Feedback Module**

## 6. Data Pipeline & Workflow
Resume Upload → Text Preprocessing → Resume Parsing → Skill Normalization → Embedding Generation → Similarity Computation → Fit Scoring → Bias Analysis → Candidate Ranking & Job Recommendation

## 7. Matching & Scoring Methodology
Final Match Score is computed as:

$$
Final Score = 0.40 \times Skill Match + 0.25 \times Experience Match + 0.10 \times Education Match + 0.25 \times Semantic Similarity
$$

This weighted approach ensures balanced and interpretable candidate evaluation.

## 8. Technical Implementation

### 8.1 Resume Parsing (NLP)
The system uses regex and NLP to extract structured data from resumes.
*Source: `src/resume_processing/parser.py`*

```python
class ResumeParser:
    """Extract structured information from resume text."""
    
    SKILL_KEYWORDS = {
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', ...
    }
    
    def parse(self, resume_text: str) -> Dict[str, any]:
        """Parse resume and extract structured information."""
        self.extracted_data = {
            'raw_text': resume_text,
            'skills': [],
            'education': [],
            'work_experience': [],
            'years_of_experience': 0,
            # ...
        }
        
        self._extract_skills(resume_text)
        self._extract_experience_years(resume_text)
        # ...
        return self.extracted_data

    def _extract_skills(self, text: str) -> None:
        """Extract technical skills."""
        text_lower = text.lower()
        found_skills = []
        for skill in self.SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        self.extracted_data['skills'] = sorted(list(set(found_skills)))
```

### 8.2 Feature Engineering & Embeddings
We generate TF-IDF vectors and Semantic Embeddings (Sentence-BERT) for robust matching.
*Source: `src/feature_engineering/pipeline.py`*

```python
def build_pairwise_features(self) -> Tuple[pd.DataFrame, Any, Tuple]:
    """Generate the main feature matrix (Resumes x Jobs)."""
    
    # TF-IDF Setup
    corpus = pd.concat([self.resumes['_cleaned_text'], self.jobs['_cleaned_text']], ignore_index=True)
    self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    tfidf_matrix = self.vectorizer.fit_transform(corpus)
    
    # Semantic Embeddings (Sentence-BERT)
    if EMBEDDING_AVAILABLE:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        r_emb = model.encode(self.resumes['_cleaned_text'].tolist())
        j_emb = model.encode(self.jobs['_cleaned_text'].tolist())
        embedding_sim = cosine_similarity(r_emb, j_emb)

    # Feature Construction
    for i, r_row in self.resumes.iterrows():
        for j, j_row in self.jobs.iterrows():
             feat = {
                'tfidf_similarity': float(cosine_sim[i, j]),
                'embedding_similarity': float(embedding_sim[i, j]),
                'skill_match_ratio': ratio_shared,
                # ...
            }
            rows.append(feat)
```

### 8.3 Smart Matching Engine
The matching engine applies the weighted scoring formula and hard filters.
*Source: `src/matching/smart_matcher.py`*

```python
def match_candidate_to_job(self, candidate_data, job_data, features) -> MatchResult:
    # 1. Check hard requirements (pass/fail)
    hard_filter_result = self._check_hard_requirements(candidate_data, job_data)
    
    # 2. Calculate component scores
    component_scores = {
        'skills_match': self._score_skills_match(candidate_data, job_data, features),
        'experience_match': self._score_experience_match(candidate_data, job_data),
        'education_match': self._score_education_match(candidate_data, job_data),
        'semantic_match': features.get('embedding_similarity', 0.0),
    }
    
    # 3. Calculate weighted overall score
    # Formula: 0.35*Skills + 0.25*Exp + 0.15*Edu + 0.07*Semantic ...
    overall_score = self._calculate_overall_score(component_scores, passes_filters)
    
    return MatchResult(overall_score=overall_score, ...)
```

## 9. Bias Mitigation Strategy
To reduce bias, sensitive attributes such as name, gender pronouns, age, date of birth, and photographs are removed during preprocessing. The AIF360 toolkit is used to monitor fairness metrics and mitigate unintended discrimination in screening outcomes.

## 10. Job Recommendation & Skill-Gap Analysis
If a candidate is not suitable for the applied role, the system recommends alternate IT job roles based on semantic similarity. Skill-gap analysis identifies missing competencies and provides improvement suggestions, ensuring transparency and candidate guidance.

## 11. Technology Stack
- **Python**: Core logic
- **spaCy**: Resume Parsing & NLP
- **Sentence-BERT / MiniLM**: Semantic Embeddings
- **Logistic Regression / XGBoost**: Fit Scoring & Ranking
- **Cosine Similarity**: Recommendation Engine
- **AIF360**: Bias & Fairness Monitoring
- **FastAPI**: Backend API
- **FAISS**: Scalable Similarity Search

## 12. Challenges
- Highly varied resume formats
- Inconsistent skill naming
- Limited labeled datasets
- Fairness and ethical concerns in AI-based hiring

## 13. Expected Outcomes
The system improves recruitment efficiency, enhances candidate–job matching accuracy, reduces bias, and provides explainable AI-driven decision support for IT recruiters.

## 14. Future Enhancements
- Multilingual resume processing
- Deep learning-based ranking models
- Fairness audit dashboard
- Continuous learning from recruiter feedback
- Full ATS integration for enterprise deployment

## 15. References 
1. spaCy Documentation – Industrial-strength NLP in Python, 2024.
2. FAISS: Facebook AI Similarity Search, Meta AI Research, 2023.
