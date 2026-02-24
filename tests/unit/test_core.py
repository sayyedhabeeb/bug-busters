"""
Unit tests for core functionality.
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validation.schemas import ResumeData, JobDescription, RecommendationRequest
from validation.data_validator import DataValidator, DataSanitizer, InputValidator
from resume_processing.parser import ResumeParser, JobDescriptionParser


class TestDataValidation(unittest.TestCase):
    """Test data validation functions."""
    
    def test_resume_text_validation_valid(self):
        """Test valid resume text."""
        valid_text = "John Doe | john@example.com | (123) 456-7890 | Software Engineer with 5 years experience in Python and AWS."
        is_valid, errors = DataValidator.validate_resume_text(valid_text)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_resume_text_validation_too_short(self):
        """Test resume text too short."""
        short_text = "Hello"
        is_valid, errors = DataValidator.validate_resume_text(short_text)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_job_description_validation_valid(self):
        """Test valid job description."""
        valid_text = "We are looking for a Senior Python Developer with 5+ years of experience in AWS and Docker."
        is_valid, errors = DataValidator.validate_job_description(valid_text)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_data_sanitizer_text(self):
        """Test text sanitizer."""
        dirty_text = "  Hello   World   @#$%   Test  "
        clean_text = DataSanitizer.sanitize_text(dirty_text)
        self.assertEqual(clean_text, "Hello World Test")
    
    def test_data_sanitizer_email(self):
        """Test email sanitizer."""
        email = "  JOHN@EXAMPLE.COM  "
        clean_email = DataSanitizer.sanitize_email(email)
        self.assertEqual(clean_email, "john@example.com")


class TestPydanticSchemas(unittest.TestCase):
    """Test Pydantic schema validation."""
    
    def test_resume_schema_valid(self):
        """Test valid resume schema."""
        data = {
            "resume_id": "RES_001",
            "candidate_name": "John Doe",
            "raw_text": "Experienced software engineer with 5 years of Python experience"
        }
        resume = ResumeData(**data)
        self.assertEqual(resume.resume_id, "RES_001")
        self.assertEqual(resume.experience_years, 0.0)  # default
    
    def test_resume_schema_missing_field(self):
        """Test schema with missing required field."""
        data = {
            "resume_id": "RES_001",
            # missing candidate_name and raw_text
        }
        with self.assertRaises(Exception):
            ResumeData(**data)
    
    def test_job_schema_salary_validation(self):
        """Test job schema salary validation."""
        data = {
            "job_id": "JOB_001",
            "job_title": "Senior Developer",
            "company": "Tech Corp",
            "raw_text": "Join our team as a senior developer",
            "salary_min": 100000,
            "salary_max": 50000,  # Invalid: max < min
        }
        with self.assertRaises(Exception):
            JobDescription(**data)
    
    def test_recommendation_request_schema(self):
        """Test recommendation request schema."""
        data = {
            "resume_index": 5,
            "top_n": 10,
            "min_score": 0.5
        }
        request = RecommendationRequest(**data)
        self.assertEqual(request.resume_index, 5)
        self.assertEqual(request.top_n, 10)


class TestResumeParser(unittest.TestCase):
    """Test resume parsing."""
    
    def setUp(self):
        self.parser = ResumeParser()
    
    def test_parse_basic_resume(self):
        """Test basic resume parsing."""
        resume_text = """
        John Doe
        Email: john@example.com
        Phone: (123) 456-7890
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 7 years of experience
        
        SKILLS
        Python, Java, AWS, Docker, SQL
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2016
        
        EXPERIENCE
        Senior Software Engineer at Tech Corp (2020-Present)
        Software Engineer at StartUp Inc (2018-2020)
        """
        
        result = self.parser.parse(resume_text)
        
        self.assertIn('skills', result)
        self.assertGreater(len(result['skills']), 0)
        self.assertEqual(result['years_of_experience'], 7)
    
    def test_parse_contact_extraction(self):
        """Test contact information extraction."""
        resume_text = "Contact: john.doe@example.com | Phone: (555) 123-4567 | Located in San Francisco"
        result = self.parser.parse(resume_text)
        
        self.assertIn('contact_info', result)
        self.assertIn('email', result['contact_info'])
        self.assertIn('phone', result['contact_info'])


class TestJobDescriptionParser(unittest.TestCase):
    """Test job description parsing."""
    
    def setUp(self):
        self.parser = JobDescriptionParser()
    
    def test_parse_job_description(self):
        """Test job description parsing."""
        job_text = """
        Senior Python Developer
        
        We are looking for a Senior Python Developer with 5+ years of experience.
        
        Salary: $120,000 - $150,000
        
        Location: San Francisco (Remote available)
        
        Required Skills:
        - Python
        - AWS
        - Docker
        - Kubernetes
        
        Job Type: Full-time
        """
        
        result = self.parser.parse(job_text)
        
        self.assertEqual(result['experience_required'], 5)
        self.assertEqual(result['seniority_level'], 'Senior')
        self.assertEqual(result['job_type'], 'Full-time')
        self.assertTrue(result['remote'])
        self.assertIn('salary_range', result)
        self.assertGreater(result['salary_range']['min'], 0)


class TestDataFrameValidation(unittest.TestCase):
    """Test DataFrame validation."""
    
    def test_dataframe_validation_valid(self):
        """Test valid dataframe."""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        is_valid, errors = DataValidator.validate_dataframe(df, ['col1', 'col2'])
        self.assertTrue(is_valid)
    
    def test_dataframe_validation_missing_column(self):
        """Test dataframe with missing column."""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        is_valid, errors = DataValidator.validate_dataframe(df, ['col1', 'col2'])
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


if __name__ == '__main__':
    unittest.main()
