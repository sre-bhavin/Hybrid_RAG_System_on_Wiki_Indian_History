"""
Unit Tests for RAG System
"""

import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rrf_fusion import reciprocal_rank_fusion

class TestRAG(unittest.TestCase):
    def test_rrf_fusion(self):
        dense = [("chunk1", 0.9), ("chunk2", 0.8)]
        sparse = [("chunk2", 0.7), ("chunk3", 0.6)]
        fused = reciprocal_rank_fusion(dense, sparse)
        self.assertEqual(len(fused), 3)
        # Add more tests

if __name__ == '__main__':
    unittest.main()