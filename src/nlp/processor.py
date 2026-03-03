import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import logging
from typing import List, Dict, Set
import re

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Advanced NLP processing using spaCy and NLTK."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.info(f"Downloading spaCy model {model_name}...")
            spacy.cli.download(model_name)
            self.nlp = spacy.load(model_name)
            
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract Names, Organizations, and Locations using spaCy NER."""
        doc = self.nlp(text)
        entities = {
            "PERSON": [],
            "ORG": [],
            "GPE": [],  # Locations
            "DATE": []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text.strip())
        
        # Deduplicate
        for key in entities:
            entities[key] = sorted(list(set(entities[key])))
            
        return entities

    def clean_text(self, text: str) -> str:
        """Normalize and clean text using spaCy (fast and accurate)."""
        # Convert to lowercase and simple regex clean for safety
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Lemmatize and filter (skip stop words, punctuation, and whitespace)
        cleaned_tokens = [
            token.lemma_ for token in doc 
            if not token.is_stop and not token.is_punct and token.text.strip()
        ]
        
        return " ".join(cleaned_tokens)

    def get_sentences(self, text: str) -> List[str]:
        """Split text into sentences using spaCy."""
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]
