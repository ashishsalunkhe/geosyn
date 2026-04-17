from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from typing import List, Union

class EmbeddingService:
    """
    Provides local vector embeddings for news signals and macro indicators.
    Enables 'AI/ML on top of Data Lake' using local silicon (CPU or MPS).
    """
    
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            # Determine the best available local device
            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
                
            print(f"GeoSyn: Initializing Local AI Embedding Model on {device}...")
            # Using a production-grade, lightweight symmetric embedding model
            self._model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Embeds a string or list of strings into vectors.
        Returns a numpy array of shape (768,) or (N, 768).
        """
        return self._model.encode(text, convert_to_numpy=True)

    def compute_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Computes cosine similarity between two vectors.
        """
        if vec_a.ndim == 1: vec_a = vec_a.reshape(1, -1)
        if vec_b.ndim == 1: vec_b = vec_b.reshape(1, -1)
        
        # SentenceTransformer uses normalized vectors, so inner product = cosine similarity
        return np.dot(vec_a, vec_b.T)[0][0]

embedding_service = EmbeddingService()
