import unittest
from src.matching.ranking import RankingEngine

class TestRankingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RankingEngine()
        
    def test_default_weights(self):
        self.assertAlmostEqual(self.engine.weights["model_score"], 0.4)
        self.assertAlmostEqual(self.engine.weights["vector_score"], 0.3)
        self.assertAlmostEqual(self.engine.weights["skill_score"], 0.2)
        self.assertAlmostEqual(self.engine.weights["exp_score"], 0.1)

    def test_calculate_hybrid_score(self):
        candidate = {
            "model_probability": 0.9,
            "embedding_similarity": 0.8,
            "skill_match_ratio": 0.5,
            "experience_score": 1.0
        }
        # Expected: (0.4*0.9) + (0.3*0.8) + (0.2*0.5) + (0.1*1.0)
        # = 0.36 + 0.24 + 0.10 + 0.10 = 0.80
        score = self.engine.calculate_hybrid_score(candidate)
        self.assertAlmostEqual(score, 0.80)

    def test_rank_candidates_sorting(self):
        c1 = {"id": 1, "model_probability": 0.9, "embedding_similarity": 0.9} # High score
        c2 = {"id": 2, "model_probability": 0.1, "embedding_similarity": 0.1} # Low score
        
        ranked = self.engine.rank_candidates([c2, c1])
        self.assertEqual(ranked[0]["id"], 1)
        self.assertEqual(ranked[1]["id"], 2)

    def test_explain_score(self):
        c = {"score_breakdown": {"model": 0.9, "vector": 0.9, "skill": 0.4}}
        reason = self.engine.explain_score(c)
        self.assertIn("High model confidence", reason)
        self.assertIn("Strong semantic match", reason)
        self.assertIn("Missing some required skills", reason)

if __name__ == '__main__':
    unittest.main()
