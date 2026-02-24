"""
Resume quality assessment and scoring.
Evaluates completeness, professionalism, and effectiveness of resumes.
"""

import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ResumeQualityScorer:
    """Score and assess resume quality."""
    
    def __init__(self):
        self.sections_expected = [
            'contact', 'summary', 'experience', 'education', 'skills', 'certification'
        ]
        self.red_flags = []
        self.warnings = []
    
    def score_resume(self, resume_text: str) -> Dict[str, any]:
        """
        Comprehensive resume quality scoring.
        Returns score 0-100 and detailed feedback.
        """
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
        max_score = 100
        section_weight = 15
        
        # Check for essential sections
        sections_found = 0
        if re.search(r'(contact|email|phone)', text, re.IGNORECASE):
            sections_found += 1
        if re.search(r'(professional summary|objective)', text, re.IGNORECASE):
            sections_found += 1
        if re.search(r'(experience|employment|work)', text, re.IGNORECASE):
            sections_found += 1
        if re.search(r'(education|degree)', text, re.IGNORECASE):
            sections_found += 1
        if re.search(r'(skills|competencies)', text, re.IGNORECASE):
            sections_found += 1
        
        score += (sections_found / 5) * 50
        
        # Check content depth
        lines = text.split('\n')
        if len(lines) > 20:
            score += 20
        elif len(lines) > 10:
            score += 10
        
        # Check for specific details
        if re.search(r'\d+\s*(?:years?|yrs?)', text):
            score += 15
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
            score += 15
        
        if sections_found < 3:
            self.red_flags.append("Missing essential resume sections")
        
        return min(score, max_score)
    
    def _score_professionalism(self, text: str) -> float:
        """Score professionalism and tone (0-100)."""
        score = 100
        text_lower = text.lower()
        
        # Deduct for unprofessional language
        unprofessional_words = [
            'awesome', 'cool', 'crazy', 'god', 'hell', 'damn',
            'lol', 'haha', 'omg', 'btw', 'imho'
        ]
        
        for word in unprofessional_words:
            if word in text_lower:
                score -= 5
                self.warnings.append(f"Unprofessional language detected: '{word}'")
        
        # Check for casual contractions
        casual_contractions = ["don't", "can't", "won't", "isn't", "it's"]
        contraction_count = sum(1 for word in casual_contractions if word in text_lower)
        score -= contraction_count * 2
        
        # Check for excessive punctuation
        if text.count('!!!') > 0 or text.count('???') > 0:
            score -= 10
            self.warnings.append("Excessive punctuation detected")
        
        # Check for proper capitalization
        uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
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
        
        # Check for action verbs
        action_verbs = [
            'managed', 'developed', 'led', 'designed', 'implemented',
            'coordinated', 'improved', 'enhanced', 'established', 'oversaw'
        ]
        
        verb_count = sum(1 for verb in action_verbs if verb in text.lower())
        score += min(verb_count * 5, 30)
        
        # Check for quantifiable achievements
        achievement_patterns = [
            r'(?:increased|decreased|improved|reduced|saved).+?(?:\d+%|\$\d+)',
            r'\d+(?:\s*(?:%|million|thousand|k|\$))',
            r'(?:top|leading|award|recognition|certified)'
        ]
        
        achievement_count = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in achievement_patterns
        )
        score += min(achievement_count * 3, 20)
        
        return min(score, 100)
    
    def _score_keywords(self, text: str) -> float:
        """Score keyword richness and technical content (0-100)."""
        score = 0
        text_lower = text.lower()
        
        # Technical keywords
        tech_keywords = [
            'python', 'java', 'javascript', 'sql', 'aws', 'docker',
            'machine learning', 'analytics', 'api', 'database'
        ]
        
        keyword_count = sum(1 for kw in tech_keywords if kw in text_lower)
        score += min(keyword_count * 10, 50)
        
        # Soft skills
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'project management', 'strategic'
        ]
        
        soft_skill_count = sum(1 for skill in soft_skills if skill in text_lower)
        score += min(soft_skill_count * 8, 30)
        
        # Industry-specific terms
        if re.search(r'agile|scrum|sprint', text_lower):
            score += 10
        if re.search(r'ci/cd|devops|kubernetes', text_lower):
            score += 10
        
        return min(score, 100)
    
    def _score_structure(self, text: str) -> float:
        """Score overall structure and organization (0-100)."""
        score = 50
        lines = text.split('\n')
        
        # Consistent formatting
        lines_with_bullets = sum(1 for line in lines if line.strip().startswith(('-', '•', '*')))
        if lines_with_bullets > 5:
            score += 15
        
        # Reasonable line length (not too long, not too short)
        avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
        if 30 <= avg_line_length <= 100:
            score += 20
        
        # Proper spacing
        empty_lines = sum(1 for line in lines if not line.strip())
        if 0 < empty_lines < len(lines) * 0.3:
            score += 15
        
        return min(score, 100)
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if scores['completeness'] < 70:
            recommendations.append("Add missing resume sections (summary, skills, certifications)")
        
        if scores['professionalism'] < 80:
            recommendations.append("Review and remove unprofessional language")
        
        if scores['clarity'] < 70:
            recommendations.append("Use more action verbs and quantifiable achievements")
        
        if scores['keyword_richness'] < 60:
            recommendations.append("Include relevant technical and industry keywords")
        
        if scores['structure'] < 70:
            recommendations.append("Improve formatting and organization with consistent structure")
        
        return recommendations


class EmploymentGapDetector:
    """Detect and analyze employment gaps in resume."""
    
    def detect_gaps(self, experience_entries: List[Dict]) -> Dict[str, any]:
        """
        Detect employment gaps from work experience.
        
        Args:
            experience_entries: List of work experience with dates
        
        Returns:
            Gap analysis results
        """
        gaps = []
        total_gap_months = 0
        
        # Sort by end date
        sorted_entries = sorted(
            experience_entries,
            key=lambda x: x.get('end_date', ''),
            reverse=True
        )
        
        for i in range(len(sorted_entries) - 1):
            current = sorted_entries[i]
            next_entry = sorted_entries[i + 1]
            
            # Calculate gap between end_date and next start_date
            gap_months = self._calculate_gap(
                current.get('end_date'),
                next_entry.get('start_date')
            )
            
            if gap_months > 1:  # Flag gaps > 1 month
                gaps.append({
                    'duration_months': gap_months,
                    'between': f"{next_entry.get('company')} to {current.get('company')}",
                    'severity': self._classify_gap(gap_months)
                })
                total_gap_months += gap_months
        
        return {
            'has_gaps': len(gaps) > 0,
            'gaps': gaps,
            'total_gap_months': total_gap_months,
            'concern_level': self._assess_concern(total_gap_months)
        }
    
    @staticmethod
    def _calculate_gap(end_date: str, start_date: str) -> int:
        """Calculate months between dates."""
        # Simplified - in production use dateutil.parser
        return 0
    
    @staticmethod
    def _classify_gap(months: int) -> str:
        """Classify gap severity."""
        if months < 3:
            return 'minor'
        elif months < 6:
            return 'moderate'
        elif months < 12:
            return 'significant'
        else:
            return 'critical'
    
    @staticmethod
    def _assess_concern(total_months: int) -> str:
        """Assess overall concern level."""
        if total_months == 0:
            return 'no_concern'
        elif total_months < 6:
            return 'low'
        elif total_months < 12:
            return 'medium'
        else:
            return 'high'


class SkillLevelDetector:
    """Detect skill proficiency levels from resume context."""
    
    PROFICIENCY_KEYWORDS = {
        'expert': ['expert', 'mastered', 'proficient', 'highly skilled', 'advanced'],
        'advanced': ['advanced', 'deep knowledge', 'extensive'],
        'intermediate': ['intermediate', 'solid', 'good'],
        'beginner': ['basic', 'familiar with', 'introduction to', 'learning'],
    }
    
    def detect_skill_levels(self, resume_text: str, skills: List[str]) -> Dict[str, str]:
        """
        Detect proficiency level for each skill.
        
        Args:
            resume_text: Full resume text
            skills: List of identified skills
        
        Returns:
            Mapping of skill to proficiency level
        """
        skill_levels = {}
        text_lower = resume_text.lower()
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Find context around skill mention
            pattern = f'.{{0,100}}{re.escape(skill_lower)}.{{0,100}}'
            matches = re.findall(pattern, text_lower)
            
            if matches:
                # Check context for proficiency indicators
                context = ' '.join(matches)
                level = self._determine_level(context)
                skill_levels[skill] = level
            else:
                skill_levels[skill] = 'unknown'
        
        return skill_levels
    
    def _determine_level(self, context: str) -> str:
        """Determine proficiency level from context."""
        for level, keywords in self.PROFICIENCY_KEYWORDS.items():
            if any(kw in context for kw in keywords):
                return level
        
        return 'intermediate'  # Default level
