"""
Integration tests for API endpoints and pipeline components.
"""

import unittest
import json
from pathlib import Path
import sys
import tempfile
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validation.schemas import RecommendationRequest, RecommendationResponse
from resume_processing.parser import ResumeParser, JobDescriptionParser
from validation.data_validator import DataValidator


class TestPipelineIntegration(unittest.TestCase):
    """Test full pipeline integration."""
    
    def setUp(self):
        """Setup test data."""
        self.resume_parser = ResumeParser()
        self.job_parser = JobDescriptionParser()
        
        self.sample_resume = """
        John Doe
        Email: john@example.com
        Phone: (555) 123-4567
        
        PROFESSIONAL SUMMARY
        Experienced software engineer with 6 years of experience in Python, AWS, and microservices.
        
        TECHNICAL SKILLS
        Languages: Python, Java, JavaScript
        Cloud: AWS, GCP
        Databases: PostgreSQL, MongoDB
        Tools: Docker, Kubernetes, Jenkins
        
        PROFESSIONAL EXPERIENCE
        Senior Software Engineer at TechCorp (2021-Present)
        - Led development of microservices architecture
        - Improved performance by 40%
        
        Software Engineer at StartupXYZ (2018-2021)
        - Built REST APIs using Python/Flask
        - Managed AWS infrastructure
        
        EDUCATION
        B.S. Computer Science - State University (2018)
        """
        
        self.sample_job = """
        Senior Python Developer
        TechCorp Inc.
        
        We are seeking an experienced Senior Python Developer to join our engineering team.
        
        Position Details:
        Location: San Francisco, CA (Remote available)
        Salary: $130,000 - $160,000
        Job Type: Full-time
        
        Required Skills:
        - 5+ years of Python development
        - AWS/Cloud experience
        - Microservices architecture knowledge
        - PostgreSQL expertise
        
        Responsibilities:
        - Design and develop scalable Python applications
        - Lead technical discussions with the team
        - Mentor junior developers
        
        Nice to Have:
        - Kubernetes experience
        - CI/CD pipeline expertise
        """
    
    def test_resume_parsing_integration(self):
        """Test resume parsing returns structured data."""
        result = self.resume_parser.parse(self.sample_resume)
        
        # Check all expected keys exist
        self.assertIn('skills', result)
        self.assertIn('contact_info', result)
        self.assertIn('education', result)
        self.assertIn('work_experience', result)
        self.assertIn('years_of_experience', result)
        
        # Check extracted skills
        self.assertGreater(len(result['skills']), 0)
        self.assertIn('Python', result['skills'])
        
        # Check contact info
        self.assertEqual(result['contact_info'].get('email'), 'john@example.com')
        
        # Check experience years
        self.assertEqual(result['years_of_experience'], 6)
    
    def test_job_parsing_integration(self):
        """Test job description parsing returns structured data."""
        result = self.job_parser.parse(self.sample_job)
        
        # Check all expected keys exist
        self.assertIn('seniority_level', result)
        self.assertIn('salary_range', result)
        self.assertIn('experience_required', result)
        self.assertIn('remote', result)
        
        # Check parsed values
        self.assertEqual(result['seniority_level'], 'Senior')
        self.assertEqual(result['experience_required'], 5)
        self.assertTrue(result['remote'])
        self.assertGreater(result['salary_range']['min'], 0)
    
    def test_resume_job_matching_compatibility(self):
        """Test if parsed resume and job are compatible."""
        resume_data = self.resume_parser.parse(self.sample_resume)
        job_data = self.job_parser.parse(self.sample_job)
        
        # Check experience match
        self.assertGreaterEqual(
            resume_data['years_of_experience'],
            job_data['experience_required']
        )
        
        # Check skill overlap
        resume_skills = set(resume_data['skills'])
        job_skills = set(job_data['required_skills'])
        overlap = resume_skills & job_skills
        
        self.assertGreater(len(overlap), 0)
    
    def test_validation_flow(self):
        """Test complete validation flow."""
        # Validate resume
        is_valid, errors = DataValidator.validate_resume_text(self.sample_resume)
        self.assertTrue(is_valid)
        
        # Validate job
        is_valid, errors = DataValidator.validate_job_description(self.sample_job)
        self.assertTrue(is_valid)
        
        # Parse both
        resume_data = self.resume_parser.parse(self.sample_resume)
        job_data = self.job_parser.parse(self.sample_job)
        
        # Both should be valid dictionaries
        self.assertIsInstance(resume_data, dict)
        self.assertIsInstance(job_data, dict)


class TestRecommendationFlow(unittest.TestCase):
    """Test recommendation generation flow."""
    
    def test_recommendation_request_validation(self):
        """Test recommendation request is properly validated."""
        valid_request = {
            "resume_index": 0,
            "top_n": 10,
            "min_score": 0.5
        }
        
        request = RecommendationRequest(**valid_request)
        self.assertEqual(request.resume_index, 0)
        self.assertEqual(request.top_n, 10)
    
    def test_recommendation_request_validation_invalid_top_n(self):
        """Test recommendation request validation fails for invalid top_n."""
        invalid_request = {
            "resume_index": 0,
            "top_n": 200  # Exceeds max of 100
        }
        
        with self.assertRaises(Exception):
            RecommendationRequest(**invalid_request)
    
    def test_recommendation_response_generation(self):
        """Test recommendation response structure."""
        from datetime import datetime
        
        response = RecommendationResponse(
            resume_id="RES_001",
            job_id="JOB_001",
            match_score=0.85,
            match_probability=0.82,
            reasoning={"skills_match": 0.9, "experience_match": 0.8},
            confidence_level="high"
        )
        
        self.assertEqual(response.resume_id, "RES_001")
        self.assertEqual(response.job_id, "JOB_001")
        self.assertAlmostEqual(response.match_score, 0.85)
        self.assertEqual(response.confidence_level, "high")


if __name__ == '__main__':
    unittest.main()
