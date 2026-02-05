"""
User Interface Module

Streamlit app for the RAG system.
"""

import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.rag_system import HybridRAG
import json
import pandas as pd

# Load RAG system
@st.cache_resource
def load_rag():
    rag = HybridRAG()
    rag.load_corpus('data/corpus.json')
    return rag

rag = load_rag()

st.title("Hybrid RAG System")

query = st.text_input("Enter your question:")

if st.button("Ask"):
    if query:
        result = rag.answer_query(query)
        
        st.subheader("Answer:")
        st.write(result['answer'])
        
        st.subheader("Retrieved Chunks:")
        for i, chunk in enumerate(result['context_chunks']):
            st.write(f"**Chunk {i+1}:** {chunk}...")
        
        st.subheader("Scores:")
        # Create lookup dicts
        dense_dict = {chunk: score for chunk, score in result['dense_results']}
        sparse_dict = {chunk: score for chunk, score in result['sparse_results']}
        rrf_dict = {chunk: score for chunk, score in result['fused_results']}
        
        # Build table data
        table_data = []
        for i, chunk in enumerate(result['context_chunks'], 1):
            dense_score = dense_dict.get(chunk, 'N/A')
            sparse_score = sparse_dict.get(chunk, 'N/A')
            rrf_score = rrf_dict.get(chunk, 'N/A')
            table_data.append({
                'Chunk Number': i,
                'Chunk': chunk[:50] + '...' if len(chunk) > 50 else chunk,
                'Dense Score': dense_score,
                'Sparse Score': sparse_score,
                'RRF Score': rrf_score
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, hide_index=True)
        
        st.write(f"Response Time: {result['response_time']:.2f} seconds")
    else:
        st.error("Please enter a question.")
