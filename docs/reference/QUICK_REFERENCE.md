# 🚀 Quick Reference Card - UPDATED v2.1

## ⚡ NEW: Enhanced Components (v2.1)

### 7 New Modules Added
- ✅ **src/exceptions.py** - 18 exception types
- ✅ **src/cache.py** - 4 cache backends  
- ✅ **src/async_processor.py** - Async + retry + circuit breaker
- ✅ **src/utils.py** - 50+ utility functions
- ✅ **src/middleware.py** - API middleware stack
- ✅ **src/orchestration.py** - Pipeline framework
- ✅ **src/profiling.py** - Performance tools

### Quick Imports

```python
# Error handling
from src.exceptions import ValidationError, MatchingError

# Caching  
from src.cache import get_cache, cached

# Async processing
from src.async_processor import get_task_manager

# Utilities
from src.utils import extract_emails, chunk_list, generate_hash

# Middleware
from src.middleware import rate_limit, request_logger_middleware

# Orchestration
from src.orchestration import WorkflowBuilder

# Profiling
from src.profiling import get_profiler
```

### Common Patterns

```python
# Cached function
@cached(ttl=3600)
def compute(data):
    return expensive_op(data)

# Protected endpoint
@app.route('/api/endpoint')
@rate_limit(100, 60)
def endpoint():
    pass

# Async task
task_mgr = get_task_manager()
task_id = task_mgr.submit_task(func, arg1, arg2)

# Pipeline
builder = WorkflowBuilder("my_flow")
builder.add_stage("step1", func1, [])
builder.add_stage("step2", func2, ["step1"])
result = builder.build().execute()

# Error handling
try:
    if not validate(data):
        raise ValidationError("Invalid data")
except ValidationError as e:
    return jsonify(e.to_dict()), e.status_code

# Profiling
@get_profiler().profile_function
def critical_func():
    pass
```

---

## Project Structure (Updated)

```
job-recommendation-system/
├── config/              ← Configuration
├── src/
│   ├── exceptions.py    ← ✨ NEW Error handling
│   ├── cache.py         ← ✨ NEW Caching layer
│   ├── async_processor.py ← ✨ NEW Async/retry/CB
│   ├── utils.py         ← ✨ NEW 50+ utilities
│   ├── middleware.py    ← ✨ NEW API middleware
│   ├── orchestration.py ← ✨ NEW Pipelines
│   ├── profiling.py     ← ✨ NEW Performance
│   ├── api/             ← API server
│   ├── matching/        ← Smart matching
│   ├── database/        ← Database layer
│   └── [other modules]
├── data/                ← Data files
├── outputs/             ← Results
├── notebooks/           ← Notebooks
├── tests/               ← Tests
└── docs/
    ├── ENHANCEMENT_REPORT.md ← ✨ NEW
    ├── INTEGRATION_GUIDE.md  ← ✨ NEW  
    ├── FINAL_UPDATE_SUMMARY.md ← ✨ NEW
    └── [other docs]
```

## Common Commands

```bash
# Setup
pip install -r requirements.txt

# Run pipeline
python main.py --features   # Extract features
python main.py --train      # Train model
python main.py --evaluate   # Evaluate

# Services
python main.py --api        # Start API
python main.py --dashboard  # Start dashboard
```

## SRC Modules Explained

| Module | Purpose |
|--------|---------|
| `api/` | Flask REST API server |
| `data_processing/` | EDA, cleaning, augmentation |
| `feature_engineering/` | Feature extraction |
| `modeling/` | Model training |
| `evaluation/` | Metrics, evaluation |
| `ui/` | Streamlit dashboard |
| `utils/` | Helper functions |

## Documentation Map

1. **Start Here:** `INDEX.md` - Navigation guide
2. **Setup:** `SETUP.md` - Installation & quick start
3. **Details:** `PROJECT_STRUCTURE.md` - Full architecture
4. **Summary:** `REORGANIZATION_SUMMARY.md` - What changed
5. **Verify:** `CLEANUP_CHECKLIST.md` - Verification list

## Key Rules

✅ Data: Always in `data/raw/` or `data/processed/`  
✅ Code: Always in `src/` with proper module  
✅ Models: Always in `outputs/models/`  
✅ Features: Always in `outputs/features/`  
✅ Reports: Always in `outputs/reports/`  
✅ Config: Always via `config/config.py`  
✅ Tests: Always in `tests/`  
✅ Notes: Always in `notebooks/`  

## Removed

❌ Old numbered directories (1_EDA, 2_FEATURE_ENGINEERING, etc.)  
❌ Scattered feature_store folders  
❌ Duplicate model_outputs  
❌ Unnecessary root files  
❌ __pycache__ directories  

## Added

✨ Professional structure  
✨ Centralized configuration  
✨ Comprehensive documentation  
✨ Proper .gitignore  
✨ Entry point (main.py)  
✨ Module initialization files  

---

**Questions?** See INDEX.md or SETUP.md!
