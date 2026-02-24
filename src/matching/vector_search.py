import faiss
import numpy as np
import logging
from typing import List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorSearchEngine:
    """
    Scalable Vector Search using FAISS (Facebook AI Similarity Search).
    """
    
    def __init__(self, dimension: int = 384, index_path: Optional[Path] = None):
        """
        Args:
            dimension: dimensionality of embeddings (384 for all-MiniLM-L6-v2)
        """
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.ids = [] # Map index ID to real ID (e.g. filename or database ID)
        
        if index_path and index_path.exists():
            self.load_index(index_path)
        else:
            # Create a flat (brute-force) L2 index by default.
            # For larger datasets (100k+), use IVFFlat.
            self.index = faiss.IndexFlatL2(dimension)
            logger.info(f"Initialized new FAISS index (dim={dimension})")

    def add_vectors(self, vectors: np.ndarray, ids: List[str]):
        """Add vectors to the index."""
        if len(vectors) != len(ids):
            raise ValueError("Vectors and IDs must have same length")
            
        vectors = np.ascontiguousarray(vectors.astype('float32'))
        
        if self.index.ntotal == 0:
            self.index.add(vectors)
        else:
            self.index.add(vectors)
            
        self.ids.extend(ids)
        logger.info(f"Added {len(vectors)} vectors. Total: {self.index.ntotal}")

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for nearest neighbors.
        Returns list of (id, distance).
        """
        if self.index.ntotal == 0:
            return []
            
        query_vector = np.ascontiguousarray(query_vector.reshape(1, -1).astype('float32'))
        
        # D is squared Euclidean distance
        D, I = self.index.search(query_vector, k)
        
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx != -1 and idx < len(self.ids):
                 results.append((self.ids[idx], float(dist)))
                 
        return results

    def save_index(self, path: Path):
        """Save index to disk."""
        if self.index:
            faiss.write_index(self.index, str(path))
            # TODO: Save IDs mapping separately (e.g. pickle or json)
            logger.info(f"Index saved to {path}")

    def load_index(self, path: Path):
        """Load index from disk."""
        self.index = faiss.read_index(str(path))
        # TODO: Load IDs mapping
        logger.info(f"Loaded index from {path}. Total vectors: {self.index.ntotal}")
