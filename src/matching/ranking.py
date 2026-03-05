from typing import List, Dict, Any
import numpy as np
import logging

logger = logging.getLogger(__name__)

class RankingEngine:
    """
    Advanced Hybrid Ranking Engine for Week 11 Optimization.
    Combines:
    1. Vector Semantic Similarity (Alpha)
    2. Keyword/Skill Overlap (Beta)
    3. Model Probability Score (Gamma)
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        # Weights aligned with Technical Implementation Plan
        self.weights = weights or {
            "model_score": 0.4,     # Learned Probability
            "vector_score": 0.3,    # Semantic Context
            "skill_score": 0.2,     # Hard Skills
            "exp_score": 0.1        # Experience Match
        }
        self._validate_weights()

    def _validate_weights(self):
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0):
            logger.warning(f"Ranking weights do not sum to 1.0: {total}. Normalizing...")
            for k in self.weights:
                self.weights[k] /= total

    def calculate_hybrid_score(self, candidate_data: Dict[str, Any]) -> float:
        """
        Calculate final hybrid score.
        Keys: model_probability, embedding_similarity, skill_match_ratio, experience_score
        """
        try:
            model_prob = candidate_data.get("model_probability", 0.0)
            vec_score = candidate_data.get("embedding_similarity", 0.0)
            skill_score = candidate_data.get("skill_match_ratio", 0.0)
            exp_score = candidate_data.get("experience_score", 0.0) # Default 0 if missing
            
            hybrid_score = (
                (self.weights["model_score"] * model_prob) +
                (self.weights["vector_score"] * vec_score) +
                (self.weights["skill_score"] * skill_score) +
                (self.weights["exp_score"] * exp_score)
            )
            
            return min(max(hybrid_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating hybrid score: {e}")
            return 0.0

    def rank_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ranked = []
        for cand in candidates:
            score = self.calculate_hybrid_score(cand)
            cand["hybrid_score"] = score
            cand["score_breakdown"] = {
                "model": cand.get("model_probability", 0),
                "vector": cand.get("embedding_similarity", 0),
                "skill": cand.get("skill_match_ratio", 0),
                "experience": cand.get("experience_score", 0)
            }
            ranked.append(cand)
        
        return sorted(ranked, key=lambda x: x["hybrid_score"], reverse=True)

    def explain_score(self, candidate: Dict[str, Any]) -> str:
        """Generate explanation based on breakdown and skill gap."""
        breakdown = candidate.get("score_breakdown", {})
        skill_gap = candidate.get("skill_gap", [])
        
        reasons = []
        model_score = breakdown.get("model", 0)
        
        if model_score > 0.8:
            reasons.append("The AI model identifies you as a top-tier candidate for this role.")
        elif model_score > 0.5:
            reasons.append("Good match based on your professional profile.")
        else:
            reasons.append("Match score is based on current skill alignment.")

        if skill_gap:
            reasons.append(f"Matching could be improved by adding: {', '.join(skill_gap[:3])}.")
        else:
            reasons.append("You have all the core skills mentioned in the job role.")
            
        return " ".join(reasons)

    def generate_suggestions(self, skill_gap: List[str]) -> str:
        """Provide actionable advice to help candidates improve their match score."""
        if not skill_gap:
            return "Your profile already strongly matches this role's requirements. High confidence match!"
        
        # Take top 3 most relevant gaps
        gap_display = ", ".join(skill_gap[:3])
        return f"To increase your match probability for this role, consider gaining experience in: {gap_display}. Update your resume once you've acquired these skills."
