"""
Reciprocal Rank Fusion Module

Combines dense and sparse retrieval results using RRF.
"""

from typing import List, Tuple, Dict
import numpy as np

def reciprocal_rank_fusion(dense_results: List[Tuple[str, float]], 
                          sparse_results: List[Tuple[str, float]], 
                          k: int = 60, 
                          top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Combine results using Reciprocal Rank Fusion.
    
    RRF_score(d) = Σ 1/(k + rank_i(d))
    """
    # Create a dict of chunk to scores
    rrf_scores = {}
    
    # Process dense results
    for rank, (chunk, _) in enumerate(dense_results, 1):
        if chunk not in rrf_scores:
            rrf_scores[chunk] = 0
        rrf_scores[chunk] += 1 / (k + rank)
    
    # Process sparse results
    for rank, (chunk, _) in enumerate(sparse_results, 1):
        if chunk not in rrf_scores:
            rrf_scores[chunk] = 0
        rrf_scores[chunk] += 1 / (k + rank)
    
    # Sort by RRF score
    sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_chunks[:top_n]

if __name__ == "__main__":
    # Example usage
    dense = [("chunk1", 0.9), ("chunk2", 0.8)]
    sparse = [("chunk2", 0.7), ("chunk3", 0.6)]
    fused = reciprocal_rank_fusion(dense, sparse)
    print(fused)