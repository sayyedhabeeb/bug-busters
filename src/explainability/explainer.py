"""
Explainability and interpretability for predictions.
Provides reasoning for why certain matches are recommended.
"""

from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class MatchExplainer:
    """Explain why recommendations were made."""
    
    def explain_match(
        self,
        candidate_id: str,
        job_id: str,
        match_result: Dict[str, Any],
        component_scores: Dict[str, float],
        raw_features: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a match.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            match_result: Result from matching engine
            component_scores: Scores for each component
            raw_features: Raw feature values
        
        Returns:
            Detailed explanation
        """
        
        explanation = {
            'candidate_id': candidate_id,
            'job_id': job_id,
            'overall_match_score': match_result.get('overall_score', 0),
            'match_quality': match_result.get('match_type', 'unknown'),
            'component_breakdown': self._explain_components(component_scores),
            'key_factors': self._identify_key_factors(component_scores, raw_features),
            'concerns': self._identify_concerns(match_result),
            'recommendation': self._generate_recommendation(match_result),
            'details': self._generate_detailed_explanation(component_scores, raw_features)
        }
        
        return explanation
    
    def _explain_components(self, scores: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Explain each component's contribution."""
        explanations = {}
        
        for component, score in scores.items():
            if component == 'skills_match':
                explanations[component] = {
                    'score': score,
                    'explanation': self._explain_skills(score),
                    'weight': '35%'
                }
            elif component == 'experience_match':
                explanations[component] = {
                    'score': score,
                    'explanation': self._explain_experience(score),
                    'weight': '25%'
                }
            elif component == 'education_match':
                explanations[component] = {
                    'score': score,
                    'explanation': self._explain_education(score),
                    'weight': '15%'
                }
            elif component == 'location_match':
                explanations[component] = {
                    'score': score,
                    'explanation': self._explain_location(score),
                    'weight': '10%'
                }
            elif component == 'salary_match':
                explanations[component] = {
                    'score': score,
                    'explanation': self._explain_salary(score),
                    'weight': '8%'
                }
            elif component == 'semantic_match':
                explanations[component] = {
                    'score': score,
                    'explanation': self._explain_semantic(score),
                    'weight': '7%'
                }
        
        return explanations
    
    def _explain_skills(self, score: float) -> str:
        """Explain skills score."""
        if score >= 90:
            return "Excellent skill alignment - candidate has nearly all required skills"
        elif score >= 75:
            return "Strong skill match - candidate has most required skills"
        elif score >= 60:
            return "Good skill overlap - candidate has key skills with some gaps"
        elif score >= 40:
            return "Moderate skills - candidate has some relevant skills"
        else:
            return "Limited skills - significant skill gaps would require training"
    
    def _explain_experience(self, score: float) -> str:
        """Explain experience score."""
        if score >= 95:
            return "Perfect experience level match"
        elif score >= 80:
            return "Strong experience level - well-matched to role requirements"
        elif score >= 70:
            return "Adequate experience - sufficient for the role"
        elif score >= 50:
            return "Mixed experience - somewhat below or above requirements"
        else:
            return "Significant experience mismatch - likely overqualified or underqualified"
    
    def _explain_education(self, score: float) -> str:
        """Explain education score."""
        if score >= 95:
            return "Education perfectly matches job requirements"
        elif score >= 80:
            return "Excellent educational background"
        elif score >= 60:
            return "Adequate educational qualifications"
        elif score >= 40:
            return "Below desired education level but potentially acceptable"
        else:
            return "Significant education gap"
    
    def _explain_location(self, score: float) -> str:
        """Explain location score."""
        if score >= 95:
            return "Perfect location match or remote position"
        elif score >= 80:
            return "Good location match - close or remote option available"
        elif score >= 60:
            return "Moderate location - willing to relocate or remote possible"
        else:
            return "Location mismatch - significant relocation needed"
    
    def _explain_salary(self, score: float) -> str:
        """Explain salary score."""
        if score >= 90:
            return "Salary expectations well-aligned with job offer"
        elif score >= 75:
            return "Reasonable salary expectations"
        elif score >= 50:
            return "Some salary expectation misalignment"
        else:
            return "Significant salary expectations gap"
    
    def _explain_semantic(self, score: float) -> str:
        """Explain semantic similarity."""
        if score >= 0.8:
            return "Strong semantic similarity - similar language and domain"
        elif score >= 0.6:
            return "Good semantic match - related domain and terminology"
        elif score >= 0.4:
            return "Moderate semantic similarity - some domain overlap"
        else:
            return "Low semantic similarity - different domains"
    
    def _identify_key_factors(
        self,
        component_scores: Dict[str, float],
        raw_features: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify top factors contributing to the match."""
        # Get top 3 scoring components
        top_components = sorted(
            component_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        factors = []
        for component, score in top_components:
            factors.append({
                'factor': component,
                'contribution': score,
                'relative_importance': 'High' if score >= 75 else 'Medium'
            })
        
        return factors
    
    def _identify_concerns(self, match_result: Dict[str, Any]) -> List[str]:
        """Identify and list concerns about the match."""
        concerns = []
        
        if not match_result.get('passes_hard_filters', True):
            failures = match_result.get('filter_failures', [])
            concerns.extend(failures)
        
        component_scores = match_result.get('component_scores', {})
        
        # Check for weak areas
        if component_scores.get('skills_match', 100) < 50:
            concerns.append("Skills gap - would require training")
        
        if component_scores.get('experience_match', 100) < 40:
            concerns.append("Experience level significantly mismatched")
        
        if component_scores.get('location_match', 100) < 60:
            concerns.append("Location may be challenging")
        
        return concerns
    
    def _generate_recommendation(self, match_result: Dict[str, Any]) -> str:
        """Generate overall recommendation."""
        match_type = match_result.get('match_type', 'unknown')
        
        if match_type == 'perfect':
            return "Highly recommended - excellent match across all criteria"
        elif match_type == 'strong':
            return "Recommended - strong match with minor gaps"
        elif match_type == 'moderate':
            return "Consider - acceptable match but some gaps to address"
        elif match_type == 'weak':
            return "Not recommended - significant mismatches exist"
        else:
            return "Recommendation pending additional review"
    
    def _generate_detailed_explanation(
        self,
        component_scores: Dict[str, float],
        raw_features: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate detailed numeric explanation."""
        return {
            'component_scores': component_scores,
            'top_scoring_features': sorted(
                raw_features.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'low_scoring_features': sorted(
                raw_features.items(),
                key=lambda x: x[1]
            )[:3]
        }


class FeatureImportanceAnalyzer:
    """Analyze feature importance using SHAP or similar."""
    
    def __init__(self, model=None):
        self.model = model
    
    def get_feature_importance(
        self,
        features: Dict[str, float],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top N important features for a prediction.
        
        Args:
            features: Input features
            top_n: Number of top features to return
        
        Returns:
            List of features ranked by importance
        """
        
        importance_scores = self._compute_importance(features)
        
        top_features = sorted(
            importance_scores.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:top_n]
        
        return [
            {
                'feature': name,
                'importance': score,
                'impact': 'positive' if score > 0 else 'negative'
            }
            for name, score in top_features
        ]
    
    def _compute_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """Compute feature importance scores."""
        # Normalize features
        max_val = max(features.values()) if features else 1
        min_val = min(features.values()) if features else 0
        range_val = max_val - min_val if max_val != min_val else 1
        
        importance = {}
        for name, value in features.items():
            # Normalize to -1 to 1
            normalized = (value - min_val) / range_val * 2 - 1
            importance[name] = normalized
        
        return importance


class RecommendationReasoning:
    """Generate human-readable reasoning for recommendations."""
    
    @staticmethod
    def generate_summary(explanation: Dict[str, Any]) -> str:
        """Generate one-line summary."""
        match_type = explanation.get('match_quality', 'unknown')
        score = explanation.get('overall_match_score', 0)
        
        return f"{match_type.capitalize()} match (Score: {score:.1f}/100) - {explanation.get('recommendation', 'Review needed')}"
    
    @staticmethod
    def generate_detailed_report(explanation: Dict[str, Any]) -> str:
        """Generate detailed report."""
        report = []
        report.append("=" * 60)
        report.append("MATCH ANALYSIS REPORT")
        report.append("=" * 60)
        
        # Overall
        report.append(f"\nOverall Score: {explanation['overall_match_score']:.1f}/100")
        report.append(f"Match Type: {explanation['match_quality']}")
        
        # Components
        report.append("\nComponent Breakdown:")
        for component, details in explanation['component_breakdown'].items():
            report.append(f"  • {component}: {details['score']:.1f}/100 ({details['weight']})")
            report.append(f"    {details['explanation']}")
        
        # Key Factors
        report.append("\nKey Success Factors:")
        for i, factor in enumerate(explanation['key_factors'], 1):
            report.append(f"  {i}. {factor['factor']}: {factor['contribution']:.1f}")
        
        # Concerns
        if explanation['concerns']:
            report.append("\nConcerns:")
            for concern in explanation['concerns']:
                report.append(f"  ⚠ {concern}")
        
        # Recommendation
        report.append(f"\nRecommendation: {explanation['recommendation']}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
