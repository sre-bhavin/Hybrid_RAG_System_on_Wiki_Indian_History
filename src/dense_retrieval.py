"""
Dense Vector Retrieval Module

Uses sentence embeddings and FAISS for vector retrieval.
"""

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from typing import List, Tuple, Dict

class DenseRetriever:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def build_index(self, corpus: List[Dict]):
        """Build FAISS index from corpus."""
        self.chunks = [item['text'] for item in corpus if 'text' in item]
        if not self.chunks:
            raise ValueError("Corpus is empty or missing 'text' fields.")
        embeddings = self.model.encode(self.chunks, show_progress_bar=True)
        if not isinstance(embeddings, np.ndarray):
            raise TypeError("Embeddings are not a numpy array.")
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine
        faiss.normalize_L2(embeddings)  # Normalize for cosine
        self.index.add(embeddings)

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Retrieve top-K chunks for a query."""
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        scores, indices = self.index.search(query_embedding, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            results.append((self.chunks[idx], score))
        return results

    def save_index(self, path: str):
        """Save index to disk."""
        faiss.write_index(self.index, path)

    def load_index(self, path: str):
        """Load index from disk."""
        self.index = faiss.read_index(path)

if __name__ == "__main__":
    with open('data/corpus.json', 'r') as f:
        corpus = json.load(f)
    retriever = DenseRetriever()
    retriever.build_index(corpus)
    retriever.save_index('data/dense_index.faiss')