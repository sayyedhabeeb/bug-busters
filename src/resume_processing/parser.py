import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set

from .parsers.pdf_parser import PDFParser
from .parsers.docx_parser import DOCXParser
from src.nlp.processor import NLPProcessor

logger = logging.getLogger(__name__)

class ResumeParser:
    """Extract structured information from resume text and files."""
    
    SKILL_KEYWORDS = {
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Go', 'Rust', 'Ruby',
        'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
        'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask',
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
        'Git', 'CI/CD', 'Jenkins', 'GitLab', 'GitHub',
        'Agile', 'Scrum', 'Jira', 'Linux', 'Windows'
    }
    
    EDUCATION_KEYWORDS = {
        'Bachelor', 'Master', 'PhD', 'B.S.', 'M.S.', 'B.A.', 'M.A.',
        'Associate', 'Diploma', 'Certificate'
    }
    
    def __init__(self):
        self.extracted_data: Dict[str, Any] = {}
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.nlp_processor = NLPProcessor()
    
    def parse(self, resume_input: str) -> Dict[str, Any]:
        """
        Parse resume and extract structured information.
        Accepts raw text or file path.
        """
        resume_text = ""
        # Check if input is a valid file path
        try:
            file_path = Path(resume_input)
            if file_path.exists() and file_path.is_file():
                if self.pdf_parser.supports(file_path):
                    resume_text = self.pdf_parser.extract_text(file_path)
                elif self.docx_parser.supports(file_path):
                    resume_text = self.docx_parser.extract_text(file_path)
                elif file_path.suffix.lower() in ['.txt', '.md', '.rtf']:
                    # Safe text reading
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        resume_text = f.read()
                else:
                    logger.warning(f"Unsupported file format for parsing: {file_path.suffix}")
                    resume_text = ""
            else:
                resume_text = resume_input
        except Exception:
            resume_text = resume_input

        self.extracted_data = {
            'raw_text': resume_text,
            'clean_text': self.nlp_processor.clean_text(resume_text),
            'sections': {},
            'skills': [],
            'education': [],
            'work_experience': [],
            'contact_info': {},
            'entities': {},
            'years_of_experience': 0,
        }
        
        self._extract_contact_info(resume_text)
        self._extract_entities(resume_text)
        self._extract_sections(resume_text)
        self._extract_skills(resume_text)
        self._extract_education(resume_text)
        self._extract_work_experience(resume_text)
        self._calculate_experience_years(resume_text)
        
        return self.extracted_data

    def _extract_entities(self, text: str) -> None:
        """Use NLPProcessor to extract named entities."""
        self.extracted_data['entities'] = self.nlp_processor.extract_entities(text)

    def _extract_contact_info(self, text: str) -> None:
        """Extract email, phone, and location."""
        # Email pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            self.extracted_data['contact_info']['email'] = emails[0]
        
        # Phone pattern (US format)
        phone_pattern = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            self.extracted_data['contact_info']['phone'] = phones[0]
        
        # Location patterns (simple heuristic)
        location_keywords = ['located in', 'based in', 'city:', 'address:']
        for keyword in location_keywords:
            match = re.search(f'{keyword}\\s+([^\\n.,]+)', text, re.IGNORECASE)
            if match:
                self.extracted_data['contact_info']['location'] = match.group(1).strip()
                break
    
    def _extract_sections(self, text: str) -> None:
        """Extract resume sections."""
        section_headers = [
            'experience', 'employment', 'work history',
            'education', 'skills', 'certification',
            'projects', 'summary', 'objective', 'about'
        ]
        
        sections = {}
        current_section = None
        
        for line in text.split('\n'):
            line_lower = line.lower().strip()
            
            # Check if this is a section header
            for header in section_headers:
                if header in line_lower and len(line) < 50:
                    current_section = header
                    sections[current_section] = []
                    break
            
            # Add content to current section
            if current_section and line.strip():
                sections[current_section].append(line.strip())
        
        self.extracted_data['sections'] = sections
    
    def _extract_skills(self, text: str) -> None:
        """Extract technical skills."""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Remove duplicates and sort
        self.extracted_data['skills'] = sorted(list(set(found_skills)))
    
    def _extract_education(self, text: str) -> None:
        """Extract education information."""
        lines = text.split('\n')
        education_entries = []
        
        for i, line in enumerate(lines):
            for edu_keyword in self.EDUCATION_KEYWORDS:
                if edu_keyword.lower() in line.lower():
                    # Extract degree and potentially the institution
                    entry = {
                        'degree': line.strip(),
                        'line': i
                    }
                    education_entries.append(entry)
                    break
        
        self.extracted_data['education'] = education_entries
    
    def _extract_work_experience(self, text: str) -> None:
        """Extract work experience entries."""
        # Look for date patterns (simplified)
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{1,2}|\d{1,2}/\d{4}|20\d{2}'
        
        lines = text.split('\n')
        experiences = []
        
        for i, line in enumerate(lines):
            if re.search(date_pattern, line) and line.strip():
                experience = {
                    'text': line.strip(),
                    'line': i
                }
                experiences.append(experience)
        
        self.extracted_data['work_experience'] = experiences
    
    def _calculate_experience_years(self, text: str) -> None:
        """Estimate years of experience from resume content."""
        # Look for year mentions
        years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
        matches = re.findall(years_pattern, text, re.IGNORECASE)
        
        if matches:
            # Take the highest mentioned year (likely total experience)
            years = [int(m) for m in matches]
            self.extracted_data['years_of_experience'] = max(years)
        else:
            # Heuristic: count education entries to estimate experience
            exp_entries = len(self.extracted_data['work_experience'])
            self.extracted_data['years_of_experience'] = max(0, exp_entries - 1)


class JobDescriptionParser:
    """Extract structured information from job descriptions."""
    
    SENIORITY_LEVELS = ["principal", "lead", "senior", "mid", "junior", "entry"]
    JOB_TYPES = ['full-time', 'part-time', 'contract', 'temporary', 'internship']
    
    def __init__(self):
        self.extracted_data: Dict[str, Any] = {}
        self.nlp_processor = NLPProcessor()
    
    def parse(self, job_text: str) -> Dict[str, Any]:
        """Parse job description and extract structured information."""
        self.extracted_data = {
            'raw_text': job_text,
            'clean_text': self.nlp_processor.clean_text(job_text),
            'required_skills': [],
            'nice_to_have_skills': [],
            'salary_range': {},
            'experience_required': 0,
            'seniority_level': None,
            'job_type': None,
            'remote': False,
        }
        
        self._extract_salary(job_text)
        self._extract_experience_requirement(job_text)
        self._extract_seniority_level(job_text)
        self._extract_job_type(job_text)
        self._extract_required_skills(job_text)
        self._extract_remote_option(job_text)
        
        return self.extracted_data
    
    def _extract_salary(self, text: str) -> None:
        """Extract salary information."""
        # Pattern for salary ranges
        salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?|\$\d+k?'
        matches = re.findall(salary_pattern, text, re.IGNORECASE)
        
        if matches:
            salaries = []
            for match in matches:
                # Extract numeric values
                nums = re.findall(r'\d+', match.replace(',', ''))
                if nums:
                    salaries.extend([int(n) for n in nums])
            
            if salaries:
                self.extracted_data['salary_range'] = {
                    'min': min(salaries),
                    'max': max(salaries)
                }
    
    def _extract_experience_requirement(self, text: str) -> None:
        """Extract years of experience required."""
        patterns = [
            r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
            r"(\d+)\+?\s*(?:years?|yrs?)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                self.extracted_data["experience_required"] = int(matches[0])
                return
    
    def _extract_seniority_level(self, text: str) -> None:
        """Determine seniority level."""
        text_lower = text.lower()
        found_levels = []
        for level in self.SENIORITY_LEVELS:
            match = re.search(rf"\b{re.escape(level)}\b", text_lower)
            if match:
                found_levels.append((match.start(), level))

        if found_levels:
            # Use earliest mention to avoid later context (e.g. "mentor junior developers")
            found_levels.sort(key=lambda item: item[0])
            self.extracted_data["seniority_level"] = found_levels[0][1].capitalize()
    
    def _extract_job_type(self, text: str) -> None:
        """Extract job type."""
        text_lower = text.lower()
        for job_type in self.JOB_TYPES:
            if job_type in text_lower:
                # Keep exact expected style, e.g. Full-time.
                self.extracted_data['job_type'] = job_type.capitalize()
                break

    def _extract_required_skills(self, text: str) -> None:
        """Extract required skills using the shared skill vocabulary."""
        text_lower = text.lower()
        found_skills = []

        for skill in ResumeParser.SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        self.extracted_data["required_skills"] = sorted(set(found_skills))
    
    def _extract_remote_option(self, text: str) -> None:
        """Check if remote work is available."""
        remote_keywords = ['remote', 'work from home', 'virtual', 'distributed']
        text_lower = text.lower()
        
        self.extracted_data['remote'] = any(keyword in text_lower for keyword in remote_keywords)
