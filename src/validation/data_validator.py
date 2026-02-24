"""
Data validation and quality checks for inputs and outputs.
"""

from typing import Dict, Any, Tuple, List
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates data quality and schema compliance."""
    
    @staticmethod
    def validate_resume_text(text: str) -> Tuple[bool, List[str]]:
        """
        Validate resume text format and content.
        Returns (is_valid, error_messages)
        """
        errors = []
        
        if not text or len(text.strip()) < 50:
            errors.append("Resume text too short (minimum 50 characters)")
        
        if len(text) > 1000000:  # 1MB
            errors.append("Resume text too large (maximum 1MB)")
        
        # Check for required sections (heuristic)
        text_lower = text.lower()
        required_keywords = ['email', 'phone', 'experience', 'education']
        missing = [kw for kw in required_keywords if kw not in text_lower]
        
        if missing:
            logger.warning(f"Resume missing keywords: {missing}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_job_description(text: str) -> Tuple[bool, List[str]]:
        """Validate job description."""
        errors = []
        
        if not text or len(text.strip()) < 50:
            errors.append("Job description too short")
        
        if len(text) > 500000:  # 500KB
            errors.append("Job description too large")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, expected_columns: List[str]) -> Tuple[bool, List[str]]:
        """Validate dataframe structure."""
        errors = []
        
        if df is None or df.empty:
            errors.append("DataFrame is empty")
            return False, errors
        
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check for excessive missing values
        missing_pct = df.isnull().sum() / len(df)
        problematic_cols = missing_pct[missing_pct > 0.5]
        if not problematic_cols.empty:
            logger.warning(f"Columns with >50% missing values: {problematic_cols.to_dict()}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_feature_matrix(X: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate feature matrix."""
        errors = []
        
        if X.isnull().any().any():
            null_cols = X.columns[X.isnull().any()].tolist()
            errors.append(f"Null values in columns: {null_cols}")
        
        # Check for infinite values
        inf_cols = X.columns[~(X != X) & ((X == 1) | (X == -1) & (X > 1e10))]
        if len(inf_cols) > 0:
            errors.append(f"Infinite values in columns: {inf_cols.tolist()}")
        
        # Check for NaN values
        if X.isna().any().any():
            errors.append("NaN values present in feature matrix")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_predictions(predictions: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate model predictions."""
        errors = []
        
        if not predictions or 'recommendations' not in predictions:
            errors.append("Missing 'recommendations' key in predictions")
            return False, errors
        
        for rec in predictions.get('recommendations', []):
            if 'match_score' in rec:
                score = rec['match_score']
                if not (0 <= score <= 1):
                    errors.append(f"Invalid match_score: {score} (must be 0-1)")
        
        return len(errors) == 0, errors


class DataSanitizer:
    """Sanitizes and cleans input data."""
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input."""
        if not text:
            return ""

        # Remove special characters while keeping basic punctuation.
        import re
        text = re.sub(r"[^\w\s\-\.,]", "", text)
        text = " ".join(text.split())

        return text.strip()
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email input."""
        if not email:
            return ""
        return email.strip().lower()
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary values."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = DataSanitizer.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized[key] = DataSanitizer.sanitize_dict(value)
            else:
                sanitized[key] = value
        return sanitized


class InputValidator:
    """Validates API inputs."""
    
    @staticmethod
    def validate_resume_input(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate resume input."""
        errors = []
        
        required_fields = ['resume_id', 'raw_text']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        if 'raw_text' in data:
            is_valid, text_errors = DataValidator.validate_resume_text(data['raw_text'])
            errors.extend(text_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_job_input(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate job description input."""
        errors = []
        
        required_fields = ['job_id', 'raw_text']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        if 'raw_text' in data:
            is_valid, text_errors = DataValidator.validate_job_description(data['raw_text'])
            errors.extend(text_errors)
        
        return len(errors) == 0, errors
