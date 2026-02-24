# DOCUMENTATION INDEX

This index now covers the complete implemented frontend and backend work in this repository.

Last Updated: February 17, 2026  
Scope: Frontend + Backend + Integration + Verification

## 1. Start Here

1. [README.md](../../README.md)
2. [SETUP.md](../guides/SETUP.md)
3. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
4. [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)
5. [PROJECT_REPORT.md](../reports/PROJECT_REPORT.md)

## 2. Documentation Map

### Guides

- [COMPLETE_SETUP_GUIDE.md](../guides/COMPLETE_SETUP_GUIDE.md)
- [IMPLEMENTATION_CHECKLIST.md](../guides/IMPLEMENTATION_CHECKLIST.md)
- [INTEGRATION_GUIDE.md](../guides/INTEGRATION_GUIDE.md)
- [PRODUCTION_UPGRADE_GUIDE.md](../guides/PRODUCTION_UPGRADE_GUIDE.md)
- [SETUP.md](../guides/SETUP.md)

### Reports

- [PROJECT_REPORT.md](../reports/PROJECT_REPORT.md)
- [PROJECT_COMPLETION_SUMMARY.md](../reports/PROJECT_COMPLETION_SUMMARY.md)
- [FINAL_UPDATE_SUMMARY.md](../reports/FINAL_UPDATE_SUMMARY.md)
- [ENHANCEMENT_REPORT.md](../reports/ENHANCEMENT_REPORT.md)
- [ENHANCEMENT_COMPLETE.md](../reports/ENHANCEMENT_COMPLETE.md)

### Reference

- [INDEX.md](INDEX.md)
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

## 3. Completed Backend Development Work

### API Layer

| Area | Key Files | Status |
|---|---|---|
| FastAPI service (primary API flow) | [src/api/main.py](../../src/api/main.py) | Complete |
| FastAPI service (extended DB + ranking flow) | [src/api/server.py](../../src/api/server.py) | Complete |
| CLI orchestration entrypoint | [main.py](../../main.py) | Complete |

Implemented endpoint coverage:

- `GET /health` in both API variants
- `GET /model-info` in `src/api/main.py`
- `POST /recommend` in both API variants

### Core ML and Recommendation Pipeline

| Domain | Key Files | Status |
|---|---|---|
| Data processing and EDA | [src/data_processing/engine.py](../../src/data_processing/engine.py), [src/data_processing/data_preprocessing.py](../../src/data_processing/data_preprocessing.py) | Complete |
| Feature engineering | [src/feature_engineering/engine.py](../../src/feature_engineering/engine.py), [src/feature_engineering/feature_builder.py](../../src/feature_engineering/feature_builder.py) | Complete |
| Model training | [src/modeling/engine.py](../../src/modeling/engine.py), [src/modeling/model_training.py](../../src/modeling/model_training.py) | Complete |
| Evaluation | [src/evaluation/engine.py](../../src/evaluation/engine.py) | Complete |
| Inference | [src/inference/pipeline.py](../../src/inference/pipeline.py), [src/inference/engine.py](../../src/inference/engine.py) | Complete |
| Matching and ranking | [src/matching/engine.py](../../src/matching/engine.py), [src/matching/vector_search.py](../../src/matching/vector_search.py), [src/matching/ranking.py](../../src/matching/ranking.py) | Complete |
| Resume parsing and quality scoring | [src/resume_processing/parser.py](../../src/resume_processing/parser.py), [src/resume_processing/quality_assessment.py](../../src/resume_processing/quality_assessment.py), [src/resume_processing/engine.py](../../src/resume_processing/engine.py) | Complete |
| Batch processing | [src/batch_processing/engine.py](../../src/batch_processing/engine.py), [src/batch_processing/processor.py](../../src/batch_processing/processor.py) | Complete |

### Data, Validation, Monitoring, and Persistence

| Domain | Key Files | Status |
|---|---|---|
| Database models and connectors | [src/database/models.py](../../src/database/models.py), [src/database/connection.py](../../src/database/connection.py), [src/database/postgres_connector.py](../../src/database/postgres_connector.py) | Complete |
| Input validation and schemas | [src/validation/data_validator.py](../../src/validation/data_validator.py), [src/validation/schemas.py](../../src/validation/schemas.py), [src/schemas/resume.py](../../src/schemas/resume.py), [src/schemas/job.py](../../src/schemas/job.py) | Complete |
| Monitoring and fairness | [src/monitoring/model_monitoring.py](../../src/monitoring/model_monitoring.py), [src/monitoring/drift.py](../../src/monitoring/drift.py), [src/monitoring/fairness.py](../../src/monitoring/fairness.py) | Complete |
| Explainability | [src/explainability/engine.py](../../src/explainability/engine.py), [src/explainability/explainer.py](../../src/explainability/explainer.py), [src/explainability/shap_engine.py](../../src/explainability/shap_engine.py) | Complete |
| Logging and utilities | [src/app_logging/logger.py](../../src/app_logging/logger.py), [src/utils/security.py](../../src/utils/security.py), [src/utils/versioning.py](../../src/utils/versioning.py) | Complete |

### Cross-Cutting Enhancement Modules (v2.1)

These modules are implemented and documented in the enhancement report set:

- [src/exceptions.py](../../src/exceptions.py)
- [src/cache.py](../../src/cache.py)
- [src/async_processor.py](../../src/async_processor.py)
- [src/utils/](../../src/utils)
- [src/middleware.py](../../src/middleware.py)
- [src/orchestration.py](../../src/orchestration.py)
- [src/profiling.py](../../src/profiling.py)

Detailed docs:

- [FINAL_UPDATE_SUMMARY.md](../reports/FINAL_UPDATE_SUMMARY.md)
- [ENHANCEMENT_REPORT.md](../reports/ENHANCEMENT_REPORT.md)
- [INTEGRATION_GUIDE.md](../guides/INTEGRATION_GUIDE.md)

## 4. Completed Frontend Development Work

| Area | Key Files | Status |
|---|---|---|
| Streamlit dashboard shell and navigation | [src/ui/app.py](../../src/ui/app.py) | Complete |
| Resume matching UI flow (upload + JD + result visualization) | [src/ui/app.py](../../src/ui/app.py) | Complete |
| Model monitoring UI metrics view | [src/ui/app.py](../../src/ui/app.py) | Complete |
| Frontend module package | [src/ui/__init__.py](../../src/ui/__init__.py) | Complete |

Notes:

- Frontend stack is Streamlit-based (no React/Vue frontend in this repository).
- Dashboard run path is integrated via `python main.py --dashboard`.

## 5. Testing and Verification Coverage

| Area | Key Files | Status |
|---|---|---|
| Unit tests | [tests/unit/test_core.py](../../tests/unit/test_core.py) | Complete |
| Integration tests | [tests/integration/test_pipeline.py](../../tests/integration/test_pipeline.py) | Complete |
| Test configuration | [tests/conftest.py](../../tests/conftest.py) | Complete |
| Pipeline verification scripts | [verify_week10.py](../../verify_week10.py), [verify_week11.py](../../verify_week11.py) | Complete |

## 6. Execution Shortcuts

```bash
python main.py --eda
python main.py --features
python main.py --train
python main.py --evaluate
python main.py --api
python main.py --dashboard
python main.py --tests
python main.py --all
```

One-command project launcher (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_project.ps1
```

Pipeline stage scripts:

- [scripts/run_preprocessing.py](../../scripts/run_preprocessing.py)
- [scripts/run_feature_engineering.py](../../scripts/run_feature_engineering.py)
- [scripts/run_training.py](../../scripts/run_training.py)
- [scripts/run_pipeline.ps1](../../scripts/run_pipeline.ps1)

## 7. Related Output Reports

- [outputs/reports/EDA_SUMMARY.md](../../outputs/reports/EDA_SUMMARY.md)
- [outputs/reports/DATA_INTEGRATION_REPORT.md](../../outputs/reports/DATA_INTEGRATION_REPORT.md)
- [outputs/reports/DATA_IMPORT_SUMMARY.md](../../outputs/reports/DATA_IMPORT_SUMMARY.md)
- [outputs/reports/NEW_DATASETS_EDA_REPORT.md](../../outputs/reports/NEW_DATASETS_EDA_REPORT.md)
- [outputs/reports/FEATURE_ENGINEERING_WEEKLY_REVIEW.md](../../outputs/reports/FEATURE_ENGINEERING_WEEKLY_REVIEW.md)

## 8. Scope Statement

This file is now a consolidated index for:

- Completed backend engineering work across all implemented `src/` backend domains.
- Completed frontend engineering work in the Streamlit UI module.
- Supporting guides, reports, tests, and execution paths.

If a new module is added under `src/`, this index should be updated in the same pull request.
