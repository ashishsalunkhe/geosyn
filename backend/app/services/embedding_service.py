import numpy as np
from hashlib import sha256
from typing import List, Union

class EmbeddingService:
    """
    Provides local vector embeddings for news signals and macro indicators.
    Enables 'AI/ML on top of Data Lake' using local silicon (CPU or MPS).
    """
    
    _instance = None
    _model = None
    _backend = "uninitialized"
    _dimension = 384

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._backend == "uninitialized":
            self._initialize_backend()

    def _initialize_backend(self) -> None:
        """
        Try to use the sentence-transformers model when available.
        Fall back to a deterministic lightweight embedding so the API can boot
        even when heavyweight ML dependencies are not installed.
        """
        try:
            import torch
            from sentence_transformers import SentenceTransformer

            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"

            print(f"GeoSyn: Initializing Local AI Embedding Model on {device}...")
            self._model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
            self._backend = "sentence-transformers"
            return
        except Exception as exc:
            print(f"GeoSyn: Falling back to lightweight local embeddings ({exc})")
            self._model = None
            self._backend = "fallback"

    def _fallback_embed_one(self, text: str) -> np.ndarray:
        """
        Produce a deterministic normalized vector without external ML deps.
        This keeps clustering operational in constrained environments.
        """
        vector = np.zeros(self._dimension, dtype=np.float32)
        tokens = text.lower().split()
        if not tokens:
            return vector

        for token in tokens:
            digest = sha256(token.encode("utf-8")).digest()
            for idx, byte in enumerate(digest):
                vector[idx % self._dimension] += byte / 255.0

        norm = np.linalg.norm(vector)
        return vector if norm == 0 else vector / norm

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Embeds a string or list of strings into vectors.
        Returns a numpy array of shape (768,) or (N, 768).
        """
        if self._backend == "uninitialized":
            self._initialize_backend()

        if self._model is not None:
            return self._model.encode(text, convert_to_numpy=True)

        if isinstance(text, str):
            return self._fallback_embed_one(text)

        return np.array([self._fallback_embed_one(item) for item in text], dtype=np.float32)

    def compute_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Computes cosine similarity between two vectors.
        """
        if vec_a.ndim == 1: vec_a = vec_a.reshape(1, -1)
        if vec_b.ndim == 1: vec_b = vec_b.reshape(1, -1)
        
        # SentenceTransformer uses normalized vectors, so inner product = cosine similarity
        return np.dot(vec_a, vec_b.T)[0][0]

embedding_service = EmbeddingService()
