"""
Matching Engine
---------------
Advanced job matching with smart filtering and compatibility scoring.
Handles hard requirements, soft preferences, and candidate-job fit.
"""

from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Container for match results."""
    candidate_id: str
    job_id: str
    overall_score: float
    component_scores: Dict[str, float]
    passes_hard_filters: bool
    filter_failures: List[str]
    match_type: str  # 'perfect', 'strong', 'moderate', 'weak'
    reasoning: Dict[str, str]


class MatchingEngine:
    """Advanced job matching with filtering and reasoning-based logic."""
    
    def __init__(self):
        self.hard_requirement_weight = 0.5
        self.soft_preference_weight = 0.5
    
    def match_candidate_to_job(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        features: Dict[str, float]
    ) -> MatchResult:
        """
        Comprehensive candidate-to-job matching.
        """
        
        # 1. Check hard requirements (pass/fail)
        hard_filter_result = self._check_hard_requirements(candidate_data, job_data)
        passes_filters = hard_filter_result['passes']
        
        # 2. Calculate component scores
        component_scores = {
            'skills_match': self._score_skills_match(candidate_data, job_data, features),
            'experience_match': self._score_experience_match(candidate_data, job_data),
            'education_match': self._score_education_match(candidate_data, job_data),
            'location_match': self._score_location_match(candidate_data, job_data),
            'salary_match': self._score_salary_match(candidate_data, job_data),
            'semantic_match': features.get('embedding_similarity', 0.0), # Uses new feature
        }
        
        # 3. Calculate weighted overall score
        overall_score = self._calculate_overall_score(component_scores, passes_filters)
        
        # 4. Determine match type
        match_type = self._classify_match(overall_score, passes_filters)
        
        # 5. Generate reasoning
        reasoning = self._generate_reasoning(
            candidate_data, job_data, component_scores, hard_filter_result
        )
        
        return MatchResult(
            candidate_id=candidate_data.get('id', 'unknown'),
            job_id=job_data.get('id', 'unknown'),
            overall_score=overall_score,
            component_scores=component_scores,
            passes_hard_filters=passes_filters,
            filter_failures=hard_filter_result['failures'],
            match_type=match_type,
            reasoning=reasoning
        )
    
    def _check_hard_requirements(self, candidate_data: Dict, job_data: Dict) -> Dict[str, Any]:
        """Check hard/mandatory requirements."""
        failures = []
        
        # Minimum experience requirement
        job_min_exp = job_data.get('experience_required', 0)
        candidate_exp = candidate_data.get('years_of_experience', 0)
        
        if candidate_exp < job_min_exp * 0.8:  # Allow 20% flexibility
            failures.append(f"Experience: {candidate_exp}y < required {job_min_exp}y")
        
        # Required education level
        job_edu = job_data.get('education_level')
        candidate_edu = candidate_data.get('education_level')
        if job_edu and candidate_edu:
            if not self._education_qualifies(candidate_edu, job_edu):
                failures.append(f"Education: {candidate_edu} < required {job_edu}")
        
        # Mandatory skills (high-priority skills)
        job_required_skills = set(job_data.get('required_skills', []))
        candidate_skills = set(candidate_data.get('skills', []))
        
        # Must have at least 70% of required skills
        if len(job_required_skills) > 0:
            required_skill_coverage = len(job_required_skills & candidate_skills) / len(job_required_skills)
            if required_skill_coverage < 0.7:
                missing = job_required_skills - candidate_skills
                failures.append(f"Missing critical skills: {', '.join(list(missing)[:3])}")
        
        # Remote preference match (if strict)
        job_remote = job_data.get('remote_required', False)
        candidate_remote = candidate_data.get('remote_willing', True)
        if job_remote and not candidate_remote:
            failures.append("Position requires remote work, candidate prefers on-site")
        
        return {
            'passes': len(failures) == 0,
            'failures': failures,
            'critical_issues': len(failures) > 2
        }
    
    def _score_skills_match(self, candidate_data: Dict, job_data: Dict, features: Dict) -> float:
        """Score skills matching."""
        score = 0
        max_score = 100
        
        skill_count = features.get('skill_overlap_count', 0)
        skill_ratio = features.get('skill_match_ratio', 0)
        
        score += skill_ratio * 50
        
        if skill_count >= 5: score += 30
        elif skill_count >= 3: score += 15
        
        fuzzy_score = features.get('fuzzy_skill_match', 0)
        score += fuzzy_score * 20
        
        return min(score, max_score)
    
    def _score_experience_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Score experience level matching."""
        candidate_exp = candidate_data.get('years_of_experience', 0)
        job_exp = job_data.get('experience_required', 0)
        
        if abs(candidate_exp - job_exp) <= 1: return 100
        elif abs(candidate_exp - job_exp) <= 2: return 85
        elif candidate_exp > job_exp:
            return max(70, 100 - (candidate_exp - job_exp) * 5)
        else:
            return max(30, 70 - (job_exp - candidate_exp) * 10)
    
    def _score_education_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Score education level matching."""
        job_edu = job_data.get('education_level')
        candidate_edu = candidate_data.get('education_level')
        if not job_edu or not candidate_edu: return 50
        
        hierarchy = {'high_school': 1, 'associate': 2, 'bachelor': 3, 'master': 4, 'phd': 5}
        job_level = hierarchy.get(job_edu.lower(), 2)
        candidate_level = hierarchy.get(candidate_edu.lower(), 2)
        
        if candidate_level >= job_level:
            return 100 - (candidate_level - job_level) * 5
        else:
            return max(40, 100 - (job_level - candidate_level) * 20)
    
    def _score_location_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Score location matching."""
        if job_data.get('remote_available', False): return 100
        elif candidate_data.get('location') == job_data.get('location'): return 100
        elif candidate_data.get('remote_willing', True): return 75
        else: return 40
    
    def _score_salary_match(self, candidate_data: Dict, job_data: Dict) -> float:
        """Score salary expectations match."""
        candidate_salary = candidate_data.get('salary_expectation')
        job_min = job_data.get('salary_min')
        job_max = job_data.get('salary_max')
        
        if not candidate_salary or not job_min: return 75
        
        if job_min <= candidate_salary <= job_max: return 100
        elif candidate_salary < job_min: return 90
        else:
            percentage_over = ((candidate_salary - job_max) / job_max) * 100
            return max(40, 100 - percentage_over)
    
    def _calculate_overall_score(self, component_scores: Dict[str, float], passes_filters: bool) -> float:
        """Calculate weighted overall score."""
        weights = {
            'skills_match': 0.35, 'experience_match': 0.25, 'education_match': 0.15,
            'location_match': 0.10, 'salary_match': 0.08, 'semantic_match': 0.07,
        }
        overall = sum(component_scores.get(key, 0) * weight for key, weight in weights.items())
        if not passes_filters: overall *= 0.6
        return round(overall, 2)
    
    def _classify_match(self, score: float, passes_filters: bool) -> str:
        """Classify match quality."""
        if not passes_filters: return 'weak'
        if score >= 85: return 'perfect'
        elif score >= 70: return 'strong'
        elif score >= 55: return 'moderate'
        return 'weak'
    
    def _generate_reasoning(self, candidate_data: Dict, job_data: Dict, scores: Dict[str, float], hard_filters: Dict) -> Dict[str, str]:
        """Generate human-readable reasoning."""
        reasoning = {}
        
        if scores['skills_match'] >= 80: reasoning['skills'] = "Excellent skills match"
        elif scores['skills_match'] >= 60: reasoning['skills'] = "Good skills alignment"
        else: reasoning['skills'] = "Limited skills overlap"
        
        candidate_exp = candidate_data.get('years_of_experience', 0)
        job_exp = job_data.get('experience_required', 0)
        if abs(candidate_exp - job_exp) <= 1: reasoning['experience'] = f"Perfect experience match ({candidate_exp}y)"
        elif candidate_exp > job_exp: reasoning['experience'] = f"Over-qualified ({candidate_exp}y)"
        else: reasoning['experience'] = f"Under-experienced ({candidate_exp}y)"
        
        if hard_filters['failures']: reasoning['concerns'] = "; ".join(hard_filters['failures'][:2])
        else: reasoning['concerns'] = "Meets all hard requirements"
        
        return reasoning
    
    @staticmethod
    def _education_qualifies(candidate_edu: str, job_edu: str) -> bool:
        """Check qualification."""
        hierarchy = ['high_school', 'associate', 'bachelor', 'master', 'phd']
        try:
            cand_level = next(i for i, e in enumerate(hierarchy) if e in candidate_edu.lower())
            job_level = next(i for i, e in enumerate(hierarchy) if e in job_edu.lower())
            return cand_level >= job_level
        except StopIteration:
            return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Matching Engine Ready")
