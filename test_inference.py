
import logging
from src.inference.engine import InferenceEngine

logging.basicConfig(level=logging.INFO)

def test_inference():
    print("Initializing Inference Engine...")
    engine = InferenceEngine()
    
    resume_text = """
    Experienced Data Scientist with 5 years in Python, Machine Learning, and NLP.
    Skilled in scikit-learn, TensorFlow, and SQL.
    Masters in Computer Science.
    """
    
    jobs = [
        "Senior Data Scientist role requiring Python, ML, and NLP skills.",
        "Java Developer role for backend systems.",
        "Marketing Manager for social media."
    ]
    
    print("Running Prediction...")
    result = engine.predict(resume_text, jobs, top_k=3)
    
    print("\nPrediction Results:")
    for res in result["recommendations"]:
        print(f"Job Index: {res['job_index']}, Score: {res['score']:.4f}")
        print("Explanation (Top factor):", res["explanation"][0])
        print("-" * 30)
        
    print("\nTest Complete.")

if __name__ == "__main__":
    test_inference()
