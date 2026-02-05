"""
Main RAG System Module

Combines all components for the hybrid RAG pipeline.
"""

from src.dense_retrieval import DenseRetriever
from src.sparse_retrieval import SparseRetriever
from src.rrf_fusion import reciprocal_rank_fusion
from src.generation import Generator
import json
import time
from typing import Dict

class HybridRAG:
    def __init__(self):
        self.dense_retriever = DenseRetriever()
        self.sparse_retriever = SparseRetriever()
        self.generator = Generator()
        self.corpus = []

    def load_corpus(self, path: str):
        """Load preprocessed corpus."""
        with open(path, 'r') as f:
            self.corpus = json.load(f)
        self.dense_retriever.build_index(self.corpus)
        self.sparse_retriever.build_index(self.corpus)

    def answer_query(self, query: str, top_k: int = 10, top_n: int = 5) -> Dict:
        """Answer a query using hybrid RAG."""
        start_time = time.time()
        
        # Retrieve from dense
        dense_results = self.dense_retriever.retrieve(query, top_k)
        
        # Retrieve from sparse
        sparse_results = self.sparse_retriever.retrieve(query, top_k)
        
        # Fuse with RRF
        fused_results = reciprocal_rank_fusion(dense_results, sparse_results, top_n=top_n)
        context_chunks = [chunk for chunk, _ in fused_results]
        
        # Generate answer
        answer = self.generator.generate(query, context_chunks)
        
        response_time = time.time() - start_time
        
        return {
            'query': query,
            'answer': answer,
            'context_chunks': context_chunks,
            'dense_results': dense_results,
            'sparse_results': sparse_results,
            'fused_results': fused_results,
            'response_time': response_time
        }

if __name__ == "__main__":
    rag = HybridRAG()
    rag.load_corpus('data/corpus.json')
    result = rag.answer_query("What is machine learning?")
    print(result)