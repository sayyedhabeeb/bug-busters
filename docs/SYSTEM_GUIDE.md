# Master System Guide: Bug-Busters AI

This document is the definitive technical reference for the **Automatic Resume Screening & AI Job Recommendation System**.

## 1. System Architecture

### Core Engines
- **Data EDA Engine**: `src/data_processing/eda_engine.py` - Statistical analysis of input datasets.
- **Feature Engineering Engine**: `src/feature_engineering/engine.py` - TF-IDF and SBERT vectorization.
- **Model Training Engine**: `src/modeling/engine.py` - XGBoost classification with stratified K-fold.
- **Evaluation Engine**: `src/evaluation/engine.py` - Precision, Recall, ROC-AUC, and SHAP explainability.

### Supporting Modules
- **API Server**: `src/api/server.py` - FastAPI implementation.
- **Service Layer**: `src/api/services.py` - Business logic and model inference.
- **NLP Processing**: `src/nlp/processor.py` - Text cleaning and entity surgery (spaCy/NLTK).
- **Database Layer**: `src/database/models.py` - SQLAlchemy models (SQLite/MySQL).
- **Async Processing**: `src/async_processor.py` - Task management and retries.
- **Caching**: `src/cache.py` - Performance optimization.

---

## 2. The AI Pipeline (End-to-End)

The pipeline is orchestrated via `main.py` and follows these stages:

1. **Ingestion**: Raw conversion from data sources.
2. **Parsing**: `ResumeParser` converts files to structured text.
3. **Cleaning**: `NLPProcessor` resolves word roots and removes noise.
4. **Encoding**: `FeatureEngine` creates the semantic "Fingerprint" using **SBERT** and **TF-IDF**.
5. **Training**: `ModelTrainingEngine` learns matching patterns using **XGBoost**.
6. **Inference**: Real-time probability scoring delivered via `/api/recommend`.

---

## 3. Tool Participation

| Tool | Role | Implementation |
| :--- | :--- | :--- |
| **spaCy** | Entity Surgery | Extracting Professional Entities (NER) |
| **SBERT** | Semantic Encoding | 384-dimensional latent space representations |
| **XGBoost** | Master Brain | Final decision classification |
| **TF-IDF** | Keyword Navigator | Statistical frequency weighting |
| **NLTK** | Linguistic Janitor | Lemmatization and text normalization |

---

## 4. Operational Commands

| Action | Command |
| :--- | :--- |
| **Full Pipeline** | `python main.py --all` |
| **EDA Only** | `python main.py --eda` |
| **Feature Engineering**| `python main.py --features` |
| **Train Only** | `python main.py --train` |
| **Evaluate** | `python main.py --evaluate` |
| **API Server** | `python main.py --api` |
| **Dashboard** | `npm run dev` (in `frontend/`) |

---

## 5. Deployment & Production

### Environment Setup
- **Venv**: Always activate `.\venv\Scripts\Activate.ps1`.
- **Config**: Settings managed in `src/api/server.py` and `.env`.

### Monitoring
- **SHAP Summary**: Located in `outputs/reports/shap_summary.png`.
- **Drift Detection**: Integrated into the training workflow.
- **Audit Logs**: Stored in the database `prediction_logs` table.
