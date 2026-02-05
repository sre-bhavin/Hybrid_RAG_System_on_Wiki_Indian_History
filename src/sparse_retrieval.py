"""
Sparse Keyword Retrieval Module

Implements BM25 for keyword-based retrieval.
"""

from rank_bm25 import BM25Okapi
import json
import pickle
import numpy as np
from typing import List, Tuple, Dict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

class SparseRetriever:
    def __init__(self):
        self.bm25 = None
        self.chunks = []
        self.stop_words = set(stopwords.words('english'))

    def preprocess_text(self, text: str) -> List[str]:
        """Tokenize and remove stopwords."""
        tokens = word_tokenize(text.lower())
        return [token for token in tokens if token not in self.stop_words and token.isalnum()]

    def build_index(self, corpus: List[Dict]):
        """Build BM25 index."""
        self.chunks = [item['text'] for item in corpus]
        tokenized_corpus = [self.preprocess_text(chunk) for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Retrieve top-K chunks."""
        tokenized_query = self.preprocess_text(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = [(self.chunks[idx], scores[idx]) for idx in top_indices]
        return results

    def save_index(self, path: str):
        """Save BM25 index and chunks to disk."""
        data = {'bm25': self.bm25, 'chunks': self.chunks}
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def load_index(self, path: str):
        """Load BM25 index and chunks from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.bm25 = data['bm25']
        self.chunks = data['chunks']

if __name__ == "__main__":
    with open('data/corpus.json', 'r') as f:
        corpus = json.load(f)
    retriever = SparseRetriever()
    retriever.build_index(corpus)
    retriever.save_index('data/sparse_index.pkl')
    print("Sparse index built and saved.")