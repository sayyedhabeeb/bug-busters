# 📚 Project Documentation Index

Welcome to the reorganized Job Recommendation System! Here's a guide to all the documentation files:

## 📖 Start Here

### 1. **[SETUP.md](SETUP.md)** - Installation & Quick Start
   - How to install dependencies
   - Quick start guide
   - Running the pipeline
   - API and dashboard usage
   - Troubleshooting

### 2. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Architecture Overview
   - Complete directory layout with descriptions
   - Module organization
   - File organization rules
   - Usage examples

### 3. **[README.md](README.md)** - Project Overview
   - AI Job Recommendation System description
   - Features overview
   - Installation steps
   - Usage instructions

## 📋 Reference Documents

### **[REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)**
   - Summary of changes made
   - Files reorganized
   - Cleanup performed
   - Benefits of new structure

### **[CLEANUP_CHECKLIST.md](CLEANUP_CHECKLIST.md)**
   - Detailed checklist of all changes
   - Directory structure verification
   - File consolidation details
   - Next steps for users

## 🗂️ Project Structure

```
job-recommendation-system/
├── 📂 config/              Configuration files (config.py)
├── 📂 src/                 Source code (7 modules)
│   ├── api/               Flask REST API
│   ├── data_processing/   EDA & data augmentation
│   ├── evaluation/        Model evaluation
│   ├── feature_engineering/  Feature extraction
│   ├── modeling/          Model training
│   ├── ui/                Streamlit dashboard
│   └── utils/             Utility functions
├── 📂 data/                Data directory
│   ├── raw/               Original datasets
│   ├── processed/         Processed data
│   └── external/          External data
├── 📂 outputs/             Generated outputs
│   ├── models/            Trained models
│   ├── features/          Feature matrices
│   └── reports/           Analysis & reports
├── 📂 notebooks/           Jupyter notebooks
├── 📂 tests/               Unit tests
├── 📂 logs/                Application logs
├── main.py                Entry point
├── requirements.txt       Dependencies
└── [Documentation files]  This index + guides
```

## 🚀 Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run feature extraction
python main.py --features

# Train the model
python main.py --train

# Start API server
python main.py --api

# Start dashboard
python main.py --dashboard
```

## 📖 By Use Case

### "I'm new to this project"
1. Read: [SETUP.md](SETUP.md)
2. Read: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. Install: Follow SETUP.md instructions
4. Explore: Check the `notebooks/` directory

### "I want to understand the structure"
1. Read: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. Check: Directory layout in this file
3. Review: `config/config.py` for settings

### "I want to modify the code"
1. Read: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. Find: Your module in `src/`
3. Check: Related `__init__.py` files
4. Add tests: In `tests/` directory

### "I want to understand what changed"
1. Read: [REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)
2. Check: [CLEANUP_CHECKLIST.md](CLEANUP_CHECKLIST.md) for details

## ✨ Key Features of New Structure

✅ **Modular Design** - Each component is independent  
✅ **Clear Organization** - Easy to find what you need  
✅ **Scalable** - Easy to add new features  
✅ **Professional** - Follows industry standards  
✅ **Maintainable** - Well-documented and organized  
✅ **Version Control Ready** - Proper .gitignore  
✅ **Configuration-Driven** - Centralized settings  

## 🔗 File Locations

| What? | Where? |
|-------|--------|
| Configuration | `config/config.py` |
| API Server | `src/api/server.py` |
| Dashboard | `src/ui/app.py` |
| Data Processing | `src/data_processing/` |
| Features | `src/feature_engineering/` |
| Models | `src/modeling/` + `outputs/models/` |
| Data Files | `data/raw/` and `data/processed/` |
| Results | `outputs/` |
| Notebooks | `notebooks/` |
| Tests | `tests/` |

## 💡 Tips

- Always put raw data in `data/raw/`
- Always save processed data to `data/processed/`
- Always save models to `outputs/models/`
- Always save feature matrices to `outputs/features/`
- Always save reports to `outputs/reports/`
- Use `config/config.py` for all settings
- Add unit tests to `tests/`

---

**Need help?** Check the relevant documentation file above!
