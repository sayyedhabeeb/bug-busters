# Feature Engineering Weekly Review Notes

## Overview
Feature engineering transforms cleaned resume and job data into machine learning-ready features by extracting patterns, similarities, and domain-specific matching metrics.

---

## 📁 File Locations

### Input Files (From EDA Pipeline)
- **Source Directory**: `1_EDA/eda_outputs/`
  - `resumes_cleaned.csv` - Cleaned resume data
  - `job_descriptions_cleaned.csv` - Cleaned job descriptions
  - `skills_cleaned.csv` - List of all skills

### Main Feature Engineering File
### Main Feature Engineering File
- **Primary Script**: `2_FEATURE_ENGINEERING/feature_engineering_merged.py` (merged - legacy + enhanced)
  - **Size**: 800+ lines (merged file)
  - **Output Directory**: `2_FEATURE_ENGINEERING/feature_store/`

- **Job Embeddings**: `feature_store/job_embeddings.npy` (semantic vectors)

---

## 🔧 Feature Engineering Pipeline

### Stage 1: Data Loading & Cleaning
```
feature_engineering_merged.py (Main Pipeline — legacy + enhanced)
    ↓
clean_text() → Normalize text (lowercase, remove special chars, trim whitespace)
```

### Stage 2: Structured Feature Extraction
```
extract_structured_features() → Extract from cleaned text:
  • word_count - Number of words
  • char_count - Number of characters
  • sentence_count - Number of sentences
  • years_experience - Extracted from regex pattern
  • education_level - Bachelor/Master/PhD/Associate/Diploma
  • level - Entry/Junior/Mid/Senior/Expert
  • experienced_flag - Boolean flag for "experienced" keyword
  • remote_flag - Boolean flag for "remote" keyword
  • mentor_req_flag - Boolean flag for "mentor" requirement
```

### Stage 3: Skill Matching
```
load_skill_list() → Create sorted list of skills
    ↓
extract_skills_from_text() → Find skills in resume/job text using regex word boundaries
    ↓
Calculate:
  • resume_num_skills - Count of skills in resume
  • job_num_skills - Count of skills in job
  • shared_skills_count - Common skills between resume & job
  • shared_skills_ratio - (shared / job_skills) normalized
  • fuzzy_skill_score - Token-based similarity (0-1) if rapidfuzz available
```

### Stage 4: Text Similarity Features
```
build_tfidf() → TF-IDF Vectorization:
  • Max 5000 features
  • N-grams: 1-2
  • Output: TF-IDF matrix for all texts
    ↓
cosine_similarity(resume_tfidf, job_tfidf) → tfidf_cosine (0-1 score)

build_embeddings() → Semantic Embeddings (if sentence-transformers available):
  • Model: all-MiniLM-L6-v2
  • Creates dense vectors capturing semantic meaning
    ↓
cosine_similarity(resume_embeddings, job_embeddings) → embedding_cosine (0-1 score)
```

### Stage 5: Domain-Specific Matching (NEW)
```
education_level_compatibility() → Matches education requirements:
  • Scale: Diploma(1) → Associate(2) → Bachelor(3) → Master(4) → PhD(5)
  • Returns: 0-1 score (1.0 if resume >= job requirement)

experience_level_compatibility() → Matches career levels:
  • Scale: Entry(1) → Junior(2) → Mid(3) → Senior(4) → Expert(5)
  • Returns: 0-1 score (1.0 if resume >= job requirement)

years_experience_match() → Matches years of experience:
  • Returns: 1.0 if resume_years >= job_years
  • Partial credit: 1.0 - (gap × 0.1)
```

### Stage 6: Text Overlap Features (NEW)
```
extract_keywords() → Extract meaningful words:
  • Remove common words (the, a, and, etc.)
  • Filter words with length > 2
  • Return set of keywords

keyword_overlap_score() → Calculate overlap:
  • Returns: (shared_keywords / job_keywords) ratio
```

### Stage 7: Pairwise Feature Matrix
```
For each (resume, job) pair:
  Create row with ALL features from above stages
  Total combinations: 11 resumes × 70 jobs = 770 pairs
```

### Stage 8: Feature Interactions (NEW)
```
create_feature_interactions() → Combine features:
  • skill_experience_interaction = shared_skills_ratio × (1 - exp(-years/5))
  • similarity_skill_interaction = tfidf_cosine × (1 + shared_skills/job_skills)
  • remote_compatibility = (resume_remote == job_remote) × 0.8 + 0.2
```

### Stage 9: Label Creation & Quality Checks
```
Label Engineering:
  label = 1 if (tfidf_cosine > 0.1) OR (embedding_cosine > 0.2) else 0

Quality Checks:
  • Missing values scan
  • Infinite values detection
  • Feature range statistics
  • Handle NaN in fuzzy_skill_score
```

---

## 📊 Features Generated (38 Total)

### Indices (2)
- `resume_index`, `job_index`
- `resume_id`, `job_id`

### Text Similarity (2)
- `tfidf_cosine` - TF-IDF based similarity (0-1)
- `embedding_cosine` - Semantic similarity (0-1)

### Text Statistics (6)
- `resume_len`, `job_len` - Word counts
- `resume_word_count`, `job_word_count`
- `resume_char_count`, `job_char_count`
- `resume_sentence_count`, `job_sentence_count`

### Skill Features (4)
- `resume_num_skills`, `job_num_skills`
- `shared_skills_count`, `shared_skills_ratio`
- `fuzzy_skill_score` - Fuzzy matching score (0-1)

### Domain Features - Resume (8)
- `resume_years_experience` - Extracted years
- `resume_education_level` - Education extracted
- `resume_level` - Career level extracted
- `resume_experienced_flag` - Has "experienced" keyword
- `resume_remote_flag` - Has "remote" keyword
- `resume_experienced_flag`, `resume_remote_flag` (from flags)

### Domain Features - Job (8)
- `job_years_experience`
- `job_education_level`
- `job_level`
- `job_experienced_flag`
- `job_remote_flag`
- `job_mentor_req_flag` - Has "mentor" requirement

### Domain Matching Features (3) - NEW
- `education_level_match` - Education compatibility (0-1)
- `experience_level_match` - Level compatibility (0-1)
- `years_experience_match` - Years compatibility (0-1)

### Text Overlap (1) - NEW
- `keyword_overlap_score` - Keyword overlap (0-1)

### Interaction Features (3) - NEW
- `skill_experience_interaction`
- `similarity_skill_interaction`
- `remote_compatibility`

### Target Label (1)
- `label` - Match/no-match binary label

---

## 🔑 Key Functions Summary

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `load_data()` | Load cleaned data | File paths | DataFrames (resumes, jobs, skills) |
| `clean_text()` | Normalize text | Raw text | Cleaned text string |
| `extract_structured_features()` | Extract basic features | DataFrame, text column | DataFrame with features |
| `extract_skills_from_text()` | Find skills in text | Text, skills list | List of found skills |
| `build_tfidf()` | Create TF-IDF vectors | Text corpus | Vectorizer, matrix |
| `build_embeddings()` | Create semantic vectors | Text corpus | Model, embedding matrix |
| `pairwise_feature_matrix()` | Create all features per pair | DataFrames, skills | Feature matrix (770×38) |
| `education_level_compatibility()` | Match education | Resume edu, job edu | Score (0-1) |
| `experience_level_compatibility()` | Match career level | Resume level, job level | Score (0-1) |
| `years_experience_match()` | Match experience years | Years values | Score (0-1) |
| `extract_keywords()` | Extract meaningful words | Text | Set of keywords |
| `keyword_overlap_score()` | Calculate keyword overlap | Resume text, job text | Score (0-1) |
| `create_feature_interactions()` | Combine features | Feature DataFrame | DataFrame with interactions |
| `check_feature_quality()` | Validate features | Feature DataFrame | Quality report dict |
| `save_features()` | Save to CSV | DataFrame, name | File path |
| `main()` | Execute pipeline | None | Prints report, saves files |

---

## ⚙️ Configuration & Dependencies

### Required Libraries
```python
pandas, numpy - Data manipulation
sklearn.feature_extraction.text - TF-IDF
sklearn.metrics.pairwise - Cosine similarity
sentence_transformers - Embeddings (optional)
rapidfuzz - Fuzzy matching (optional)
re, pickle, pathlib - Standard utilities
```

### Optional Features
- **Embeddings**: Requires `sentence-transformers` package
  - Uses `all-MiniLM-L6-v2` model (438MB)
  - Provides semantic similarity beyond TF-IDF
- **Fuzzy Matching**: Requires `rapidfuzz` package
  - Token-set similarity for skills
  - More robust to word order differences

### Output Directory
- Automatically created: `feature_store/`
- Contains: feature_matrix.csv, embeddings, vectorizer

---

## 📈 Data Flow Summary

```
1_EDA (Cleaned Data)
    ↓
resumes_cleaned.csv
job_descriptions_cleaned.csv
skills_cleaned.csv
    ↓
feature_engineering.py (Main Pipeline)
    ├─ Text Cleaning
    ├─ Structured Features
    ├─ TF-IDF Vectorization
    ├─ Semantic Embeddings
    ├─ Skill Matching
    ├─ Domain Matching ← NEW
    ├─ Keyword Overlap ← NEW
    ├─ Pairwise Matrix (770 pairs)
    ├─ Interactions ← NEW
    ├─ Quality Checks ← NEW
    └─ Label Creation
    ↓
feature_store/
    ├─ feature_matrix.csv (770×38) ← INPUT FOR MODELING
    ├─ tfidf_vectorizer.pkl (for inference)
    ├─ resume_embeddings.npy
    └─ job_embeddings.npy
```

---

## 🎯 Last Run Statistics

- **Input Data**: 11 resumes, 70 jobs, 50+ skills
- **Output Pairs**: 770 resume-job combinations
- **Total Features**: 38 (including 7 new features)
- **Quality Status**: ✅ No missing values, no infinite values
- **Feature Ranges**: All normalized 0-1 scores working properly
- **Execution Status**: ✅ Successful

---

## 🔍 Weekly Review Checklist

- [ ] Verify input data freshness (resumes_cleaned.csv, jobs_cleaned.csv)
- [ ] Check feature matrix output (770×38 expected)
- [ ] Validate feature ranges (all should be 0-1 or reasonable numeric)
- [ ] Confirm no missing or infinite values
- [ ] Review label distribution (match vs non-match ratio)
- [ ] Check embedding generation (if using sentence-transformers)
- [ ] Verify TF-IDF vectorizer saved properly
- [ ] Test pairwise_feature_matrix() with sample data
- [ ] Monitor execution time for large datasets
- [ ] Validate domain matching functions (education, level, experience)

---

## 🚀 Next Steps (Modeling Phase)

The feature_matrix.csv will be used in:
- **3_MODELING/train_model.py** - Model training pipeline
- Feature selection/dimensionality reduction
- Model building and hyperparameter tuning
- Evaluation metrics calculation

---

## 📝 Notes
- Feature engineering is computationally intensive for large datasets (embeddings take time)
- All features are normalized to 0-1 scale for model compatibility
- Domain matching features provide business-meaningful scoring
- Interaction features help capture complex relationships
- Quality checks ensure data integrity before modeling
