# Automatic Resume Screening and AI Job Recommendation

Clean, modular machine learning project structure for resume-job matching with separated stages for preprocessing, feature engineering, and model training.

## Project Structure

```text
Bug busters-project/
|-- data/
|   |-- raw/                    # Original input datasets
|   |-- interim/                # Cleaned datasets from preprocessing (Git Ignored)
|   `-- processed/
|       `-- features/           # Final feature artifacts (Git Ignored)
|-- docs/                       # Project documentation
|-- outputs/
|   |-- models/                 # Serialized trained models
|   |-- reports/                # Analysis and evaluation reports
|   `-- features/               # Mirrored feature artifacts for API
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
|-- main.py                     # CLI Orchestration (Unified Entrypoint)
|-- pyproject.toml
`-- requirements.txt
```

## What Was Refactored

- **Standardized Engines**: Consolidated logic into single "Engine" classes for EDA, Feature Engineering, Training, and Evaluation.
- **Unified CLI**: Primary pipeline orchestration via `main.py` with multi-stage flags (`--eda`, `--features`, etc.).
- **Redundancy Cleanup**: Removed 10+ duplicate and legacy scripts while preserving all technical logic.
- **Explainability**: Integrated SHAP values directly into the training workflow.
- **API Consolidation**: Merged multiple server implementations into a unified `api/server.py`.
- **Dynamic Labeling**: Improved labeling strategy with similarity-based and quantile fallbacks.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Pipeline

The system is controlled via `main.py`. You can run components individually or the full pipeline at once.

### Full Pipeline Run
```bash
python main.py --all
```

### Individual Stages
- **Data Preprocessing & EDA**: `python main.py --eda`
- **Feature Engineering**: `python main.py --features`
- **Model Training**: `python main.py --train`
- **Evaluation**: `python main.py --evaluate`

## Documentation

- **Technical Reference**: [`docs/SYSTEM_GUIDE.md`](docs/SYSTEM_GUIDE.md) - Full architecture and AI details.
- **Progress Tracker**: [`docs/guides/IMPLEMENTATION_CHECKLIST.md`](docs/guides/IMPLEMENTATION_CHECKLIST.md) - Feature status.
- **Usage Guide**: [`docs/MODEL_PIPELINE_GUIDE.md`](docs/MODEL_PIPELINE_GUIDE.md) - Command reference and examples.

## Start Services

### API Server
```bash
python main.py --api
```

### TalentMatch AI UI
```bash
python main.py --ui
```

---

## Master Architecture
The system uses a consolidated engine architecture:
- `eda_engine.py` -> `engine.py` (FE) -> `engine.py` (Train) -> `engine.py` (Eval)

*For detailed component breakdowns, see the [Master System Guide](docs/SYSTEM_GUIDE.md).*
