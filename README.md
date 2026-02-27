# Automatic Resume Screening and AI Job Recommendation

Clean, modular machine learning project structure for resume-job matching with separated stages for preprocessing, feature engineering, and model training.

## Project Structure

```text
Bug busters-project/
|-- data/
|   |-- raw/                    # Original input datasets
|   |-- interim/                # Cleaned datasets from preprocessing
|   `-- processed/
|       `-- features/           # Final feature matrix and vectorizer artifacts
|-- models/                     # Serialized trained models
|-- notebooks/
|   `-- 01_feature_engineering_analysis.ipynb
|-- docs/                       # Project documentation
|-- scripts/                    # Automation scripts
|-- src/
|   |-- data_processing/
|   |   |-- data_preprocessing.py
|   |   `-- eda_engine.py       # Consolidated EDA
|   |-- feature_engineering/
|   |   `-- engine.py           # Consolidated Feature Engineering
|   |-- modeling/
|   |   `-- engine.py           # Consolidated Training
|   |-- evaluation/
|   |   `-- engine.py           # Consolidated Evaluation
|   `-- api/
|       `-- server.py           # Standardized API server
|-- main.py                     # CLI Orchestration
|-- pyproject.toml
`-- requirements.txt
```

## What Was Refactored

- **Standardized Engines**: Consolidated logic into single "Engine" classes for EDA, Feature Engineering, Training, and Evaluation.
- **Workflow Roadmap**: Clearly defined pipeline stages (EDA -> FE -> Training -> Evaluation -> API).
- **Redundancy Cleanup**: Removed 10+ duplicate and legacy files while preserved technical logic.
- **Explainability**: Integrated SHAP values directly into the training workflow.
- **API Consolidation**: Merged multiple server implementations into a unified `api/server.py`.
- **Class Imbalance Fix**: Implemented `scale_pos_weight` and pre-training data validation to handle minority class learning.
- **Dynamic Labeling Strategy**: Improved `src/feature_engineering/engine.py` with multi-tier fallback (Similarity Threshold -> Quantile Fallback) to ensure balanced training data.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Documentation

- Guides: `docs/guides`
- Reports: `docs/reports`
- Reference docs: `docs/reference`

## Run the Pipeline

### 1. Data Preprocessing

```bash
python scripts/run_preprocessing.py
```

Output:
- `data/interim/resumes_clean.csv`
- `data/interim/jobs_clean.csv`
- `data/interim/skills_clean.csv`

### 2. Feature Engineering

```bash
python scripts/run_feature_engineering.py
```

Output:
- `data/processed/features/feature_matrix.csv`
- `data/processed/features/tfidf_vectorizer.pkl`

### 3. Model Training

```bash
python scripts/run_training.py
```

Output:
- `models/trained/resume_job_matcher.pkl`
- `models/trained/metrics.json`

### 4. One-command Pipeline (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_pipeline.ps1
```

Optional flags:
- `-SkipPreprocessing`
- `-SkipFeatureEngineering`
- `-SkipTraining`

## Run Full Project (Pipeline + API + Dashboard)

Use this command from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_project.ps1
```

What it does:
- Runs preprocessing, feature engineering, and training
- Runs model evaluation
- Opens API and dashboard in separate PowerShell windows

Quick variants:

```powershell
# Run pipeline/evaluation only (do not start services)
powershell -ExecutionPolicy Bypass -File scripts/run_project.ps1 -NoStartServices

# Start only services (skip pipeline/evaluation)
powershell -ExecutionPolicy Bypass -File scripts/run_project.ps1 -SkipPipeline -SkipEvaluation
```

## Main CLI

You can still run the project via:

```bash
- **Technical Reference**: [`docs/SYSTEM_GUIDE.md`](docs/SYSTEM_GUIDE.md) - Full architecture and AI details.
- **Progress Tracker**: [`docs/guides/IMPLEMENTATION_CHECKLIST.md`](docs/guides/IMPLEMENTATION_CHECKLIST.md) - Feature status.
- **Usage Guide**: [`docs/MODEL_PIPELINE_GUIDE.md`](docs/MODEL_PIPELINE_GUIDE.md) - Command reference and examples.

---

## Master Architecture
The system uses a consolidated engine architecture:
- `eda_engine.py` -> `engine.py` (FE) -> `engine.py` (Train) -> `engine.py` (Eval)

*For detailed component breakdowns, see the [Master System Guide](docs/SYSTEM_GUIDE.md).*
