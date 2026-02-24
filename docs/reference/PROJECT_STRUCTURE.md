# Project Structure Documentation

## Directory Layout

```
job-recommendation-system/
├── config/                      # Configuration files
│   └── config.py               # Main configuration settings
├── src/                        # Source code
│   ├── __init__.py
│   ├── data_processing/        # EDA, data augmentation, merging
│   │   ├── eda.py
│   │   ├── augmentation.py
│   │   ├── merge.py
│   │   ├── explorer.py
│   │   └── __init__.py
│   ├── feature_engineering/    # Feature extraction and validation
│   │   ├── pipeline.py
│   │   ├── validate.py
│   │   └── __init__.py
│   ├── modeling/               # Model training
│   │   ├── train.py
│   │   └── __init__.py
│   ├── evaluation/             # Model evaluation and metrics
│   │   ├── metrics.py
│   │   └── __init__.py
│   ├── api/                    # Flask API server
│   │   ├── server.py
│   │   └── __init__.py
│   ├── ui/                     # Streamlit dashboard
│   │   ├── app.py
│   │   └── __init__.py
│   └── utils/                  # Utility functions and helpers
│       └── __init__.py
├── data/                       # Data directory
│   ├── raw/                    # Original data files
│   ├── processed/              # Cleaned and processed data
│   └── external/               # External data sources
├── outputs/                    # Generated outputs
│   ├── models/                 # Trained model files
│   ├── features/               # Feature matrices and embeddings
│   └── reports/                # Reports, analysis, and visualizations
├── notebooks/                  # Jupyter notebooks for exploration
├── tests/                      # Unit tests
├── logs/                       # Application logs
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore rules
```

## Key Directories

### `/config`
Configuration files for the entire project including paths, model parameters, and environment settings.

### `/src`
All source code organized by functionality:
- **data_processing**: Data loading, cleaning, and augmentation
- **feature_engineering**: Feature extraction and engineering
- **modeling**: Model training and tuning
- **evaluation**: Metrics and performance evaluation
- **api**: REST API server
- **ui**: Streamlit web dashboard
- **utils**: Shared utility functions

### `/data`
- **raw**: Original, unmodified data files
- **processed**: Cleaned and preprocessed data
- **external**: Additional external data sources

### `/outputs`
- **models**: Serialized trained models (.pkl, .joblib)
- **features**: Feature matrices, embeddings, and vectors
- **reports**: Analysis reports, visualizations, and metrics

### `/notebooks`
Jupyter notebooks for exploratory analysis and experimentation.

### `/tests`
Unit tests for core functionality.

## Usage

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the main pipeline**:
   ```bash
   python main.py
   ```

3. **Run individual components**:
   ```bash
   python main.py --eda       # Run EDA
   python main.py --features  # Extract features
   python main.py --train     # Train model
   python main.py --evaluate  # Evaluate model
   python main.py --api       # Start API
   python main.py --dashboard # Start dashboard
   ```

## File Organization Rules

- **Data files**: Always stored in `/data` (raw or processed)
- **Model outputs**: Always stored in `/outputs/models`
- **Feature matrices**: Always stored in `/outputs/features`
- **Reports**: Always stored in `/outputs/reports`
- **Logs**: Always written to `/logs`
