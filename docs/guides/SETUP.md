# Job Recommendation System - Setup & Installation Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Organize Your Data
Place your CSV files in the appropriate locations:
```
data/
├── raw/
│   ├── resume_dataset.csv
│   ├── job_description_dataset.csv
│   └── skill_dataset.csv
└── processed/
    └── (auto-generated processed files)
```

### 3. Run the Pipeline
```bash
python main.py --features    # Extract features
python main.py --train       # Train model
python main.py --evaluate    # Evaluate results
```

## Project Structure

This project follows a professional ML pipeline structure:

- **`config/`** - Configuration and settings
- **`src/`** - Source code organized by functionality
  - `data_processing/` - EDA and data augmentation
  - `feature_engineering/` - Feature extraction
  - `modeling/` - Model training
  - `evaluation/` - Metrics and evaluation
  - `api/` - REST API
  - `ui/` - Streamlit dashboard
  - `utils/` - Utilities
- **`data/`** - Raw and processed data
- **`outputs/`** - Models, features, and reports
- **`notebooks/`** - Jupyter notebooks
- **`tests/`** - Unit tests

See `PROJECT_STRUCTURE.md` for detailed information.

## Key Features

✅ **Modular Architecture** - Clean separation of concerns  
✅ **Reproducible** - Configuration-driven setup  
✅ **Scalable** - Easy to add new features  
✅ **Well-documented** - Clear code and docstrings  
✅ **Version Control Ready** - Proper .gitignore setup  

## API Usage

Start the API server:
```bash
python main.py --api
```

Make recommendations:
```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{"resume_index": 0}'
```

## Dashboard

Start the Streamlit dashboard:
```bash
python main.py --dashboard
```

## Troubleshooting

**Missing dependencies?**
```bash
pip install -r requirements.txt --upgrade
```

**Data path issues?**
Check `config/config.py` and update paths if needed.

**Port already in use?**
Change `API_PORT` in `config/config.py`

## Development

Adding new features:
1. Create module in appropriate `src/` subdirectory
2. Update imports in `__init__.py`
3. Add tests in `tests/`
4. Update configuration if needed
5. Document in this README

## License

See LICENSE file for details.
