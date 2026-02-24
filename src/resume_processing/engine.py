"""
Resume Processing Engine
------------------------
Unified module for:
1. Parsing resumes and job descriptions (Information Extraction)
2. Assessing resume quality (Scoring & Feedback)
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ResumeProcessingEngine:
    """
    Main engine for resume processing.
    Combines parsing and quality assessment capabilities.
    """

    def __init__(self) -> None:
        self.parser = ResumeParser()
        self.job_parser = JobDescriptionParser()
        self.scorer = ResumeQualityScorer()

    def process_resume(self, text: str) -> Dict[str, any]:
        """Parse and score a resume in one go."""
        parsed_data = self.parser.parse(text)
        quality_score = self.scorer.score_resume(text)
        
        return {
            "parsed": parsed_data,
            "quality": quality_score
        }

    def parse_job(self, text: str) -> Dict[str, any]:
        """Parse a job description."""
        return self.job_parser.parse(text)


class ResumeParser:
    """Extract structured information from resume text."""
    
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
        self.extracted_data: Dict[str, any] = {}
    
    def parse(self, resume_text: str) -> Dict[str, any]:
        """Parse resume and extract structured information."""
        self.extracted_data = {
            'raw_text': resume_text,
            'sections': {},
            'skills': [],
            'education': [],
            'work_experience': [],
            'contact_info': {},
            'years_of_experience': 0,
        }
        
        self._extract_contact_info(resume_text)
        self._extract_sections(resume_text)
        self._extract_skills(resume_text)
        self._extract_education(resume_text)
        self._extract_work_experience(resume_text)
        self._calculate_experience_years(resume_text)
        
        return self.extracted_data
    
    def _extract_contact_info(self, text: str) -> None:
        """Extract email, phone, and location."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            self.extracted_data['contact_info']['email'] = emails[0]
        
        phone_pattern = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            self.extracted_data['contact_info']['phone'] = phones[0]
        
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
            for header in section_headers:
                if header in line_lower and len(line) < 50:
                    current_section = header
                    sections[current_section] = []
                    break
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
        self.extracted_data['skills'] = sorted(list(set(found_skills)))
    
    def _extract_education(self, text: str) -> None:
        """Extract education information."""
        lines = text.split('\n')
        education_entries = []
        for i, line in enumerate(lines):
            for edu_keyword in self.EDUCATION_KEYWORDS:
                if edu_keyword.lower() in line.lower():
                    education_entries.append({'degree': line.strip(), 'line': i})
                    break
        self.extracted_data['education'] = education_entries
    
    def _extract_work_experience(self, text: str) -> None:
        """Extract work experience entries."""
        date_pattern = r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{1,2}|\d{1,2}/\d{4}|20\d{2}'
        lines = text.split('\n')
        experiences = []
        for i, line in enumerate(lines):
            if re.search(date_pattern, line) and line.strip():
                experiences.append({'text': line.strip(), 'line': i})
        self.extracted_data['work_experience'] = experiences
    
    def _calculate_experience_years(self, text: str) -> None:
        """Estimate years of experience from resume content."""
        years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
        matches = re.findall(years_pattern, text, re.IGNORECASE)
        if matches:
            years = [int(m) for m in matches]
            self.extracted_data['years_of_experience'] = max(years)
        else:
            exp_entries = len(self.extracted_data['work_experience'])
            self.extracted_data['years_of_experience'] = max(0, exp_entries - 1)


class JobDescriptionParser:
    """Extract structured information from job descriptions."""
    
    SENIORITY_LEVELS = ["principal", "lead", "senior", "mid", "junior", "entry"]
    JOB_TYPES = ['full-time', 'part-time', 'contract', 'temporary', 'internship']
    SKILL_KEYWORDS = ResumeParser.SKILL_KEYWORDS
    
    def __init__(self):
        self.extracted_data: Dict[str, any] = {}
    
    def parse(self, job_text: str) -> Dict[str, any]:
        """Parse job description and extract structured information."""
        self.extracted_data = {
            'raw_text': job_text,
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
        salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?|\$\d+k?'
        matches = re.findall(salary_pattern, text, re.IGNORECASE)
        if matches:
            salaries = []
            for match in matches:
                nums = re.findall(r'\d+', match.replace(',', ''))
                if nums:
                    salaries.extend([int(n) for n in nums])
            if salaries:
                self.extracted_data['salary_range'] = {'min': min(salaries), 'max': max(salaries)}
    
    def _extract_experience_requirement(self, text: str) -> None:
        """Extract years of experience required."""
        patterns = [r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience", r"(\d+)\+?\s*(?:years?|yrs?)"]
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
            found_levels.sort(key=lambda item: item[0])
            self.extracted_data["seniority_level"] = found_levels[0][1].capitalize()
    
    def _extract_job_type(self, text: str) -> None:
        """Extract job type."""
        text_lower = text.lower()
        for job_type in self.JOB_TYPES:
            if job_type in text_lower:
                self.extracted_data['job_type'] = job_type.capitalize()
                break

    def _extract_required_skills(self, text: str) -> None:
        """Extract required skills."""
        text_lower = text.lower()
        found_skills = []
        for skill in self.SKILL_KEYWORDS:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        self.extracted_data["required_skills"] = sorted(set(found_skills))
    
    def _extract_remote_option(self, text: str) -> None:
        """Check if remote work is available."""
        remote_keywords = ['remote', 'work from home', 'virtual', 'distributed']
        text_lower = text.lower()
        self.extracted_data['remote'] = any(keyword in text_lower for keyword in remote_keywords)


class ResumeQualityScorer:
    """Score and assess resume quality."""
    
    def __init__(self):
        self.red_flags = []
        self.warnings = []
    
    def score_resume(self, resume_text: str) -> Dict[str, any]:
        """Comprehensive resume quality scoring."""
        self.red_flags = []
        self.warnings = []
        
        scores = {
            'completeness': self._score_completeness(resume_text),
            'professionalism': self._score_professionalism(resume_text),
            'clarity': self._score_clarity(resume_text),
            'keyword_richness': self._score_keywords(resume_text),
            'structure': self._score_structure(resume_text),
        }
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            'overall_score': round(overall_score, 2),
            'component_scores': scores,
            'red_flags': self.red_flags,
            'warnings': self.warnings,
            'recommendations': self._generate_recommendations(scores),
        }
    
    def _score_completeness(self, text: str) -> float:
        """Score resume completeness (0-100)."""
        score = 0
        sections_found = 0
        if re.search(r'(contact|email|phone)', text, re.IGNORECASE): sections_found += 1
        if re.search(r'(professional summary|objective)', text, re.IGNORECASE): sections_found += 1
        if re.search(r'(experience|employment|work)', text, re.IGNORECASE): sections_found += 1
        if re.search(r'(education|degree)', text, re.IGNORECASE): sections_found += 1
        if re.search(r'(skills|competencies)', text, re.IGNORECASE): sections_found += 1
        
        score += (sections_found / 5) * 50
        lines = text.split('\n')
        if len(lines) > 20: score += 20
        elif len(lines) > 10: score += 10
        if re.search(r'\d+\s*(?:years?|yrs?)', text): score += 15
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text): score += 15
        
        if sections_found < 3: self.red_flags.append("Missing essential resume sections")
        return min(score, 100)
    
    def _score_professionalism(self, text: str) -> float:
        """Score professionalism and tone (0-100)."""
        score = 100
        text_lower = text.lower()
        unprofessional_words = ['awesome', 'cool', 'crazy', 'god', 'hell', 'damn', 'lol', 'haha', 'omg', 'btw', 'imho']
        
        for word in unprofessional_words:
            if word in text_lower:
                score -= 5
                self.warnings.append(f"Unprofessional language detected: '{word}'")
        
        casual_contractions = ["don't", "can't", "won't", "isn't", "it's"]
        contraction_count = sum(1 for word in casual_contractions if word in text_lower)
        score -= contraction_count * 2
        
        if text.count('!!!') > 0 or text.count('???') > 0:
            score -= 10
            self.warnings.append("Excessive punctuation detected")
        
        uppercase_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if uppercase_ratio < 0.02:
            self.warnings.append("Very low capitalization - check for proper formatting")
            score -= 5
        elif uppercase_ratio > 0.3:
            self.warnings.append("Excessive capitalization detected")
            score -= 5
        
        return max(score, 0)
    
    def _score_clarity(self, text: str) -> float:
        """Score clarity and readability (0-100)."""
        score = 50
        action_verbs = ['managed', 'developed', 'led', 'designed', 'implemented', 'coordinated', 'improved', 'enhanced', 'established', 'oversaw']
        verb_count = sum(1 for verb in action_verbs if verb in text.lower())
        score += min(verb_count * 5, 30)
        
        achievement_patterns = [r'(?:increased|decreased|improved|reduced|saved).+?(?:\d+%|\$\d+)', r'\d+(?:\s*(?:%|million|thousand|k|\$))', r'(?:top|leading|award|recognition|certified)']
        achievement_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in achievement_patterns)
        score += min(achievement_count * 3, 20)
        return min(score, 100)
    
    def _score_keywords(self, text: str) -> float:
        """Score keyword richness (0-100)."""
        score = 0
        text_lower = text.lower()
        tech_keywords = ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'machine learning', 'analytics', 'api', 'database']
        keyword_count = sum(1 for kw in tech_keywords if kw in text_lower)
        score += min(keyword_count * 10, 50)
        
        soft_skills = ['leadership', 'communication', 'teamwork', 'problem solving', 'project management', 'strategic']
        soft_skill_count = sum(1 for skill in soft_skills if skill in text_lower)
        score += min(soft_skill_count * 8, 30)
        
        if re.search(r'agile|scrum|sprint', text_lower): score += 10
        if re.search(r'ci/cd|devops|kubernetes', text_lower): score += 10
        return min(score, 100)
    
    def _score_structure(self, text: str) -> float:
        """Score structure (0-100)."""
        score = 50
        lines = text.split('\n')
        lines_with_bullets = sum(1 for line in lines if line.strip().startswith(('-', '•', '*')))
        if lines_with_bullets > 5: score += 15
        
        avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
        if 30 <= avg_line_length <= 100: score += 20
        
        empty_lines = sum(1 for line in lines if not line.strip())
        if 0 < empty_lines < len(lines) * 0.3: score += 15
        return min(score, 100)
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        if scores['completeness'] < 70: recommendations.append("Add missing resume sections (summary, skills, certifications)")
        if scores['professionalism'] < 80: recommendations.append("Review and remove unprofessional language")
        if scores['clarity'] < 70: recommendations.append("Use more action verbs and quantifiable achievements")
        if scores['keyword_richness'] < 60: recommendations.append("Include relevant technical and industry keywords")
        if scores['structure'] < 70: recommendations.append("Improve formatting and organization with consistent structure")
        return recommendations


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    engine = ResumeProcessingEngine()
    print("Resume Processing Engine Ready")
