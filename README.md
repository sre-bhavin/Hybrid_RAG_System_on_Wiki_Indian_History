# Hybrid RAG System

This project implements a Hybrid Retrieval-Augmented Generation (RAG) system combining dense vector retrieval, sparse keyword retrieval (BM25), and Reciprocal Rank Fusion (RRF) to answer questions from 500 Wikipedia articles.


## Project Structure

- `data/`: Contains datasets, including fixed_urls.json and preprocessed corpus.
- `src/`: Core implementation modules.
- `notebooks/`: Jupyter notebooks for exploration and development.
- `evaluation/`: Scripts for question generation, metrics, and evaluation pipeline.
- `ui/`: User interface code (Streamlit/Gradio/Flask).
- `reports/`: Generated reports and results.
- `tests/`: Unit tests.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Hybrid RAG System Architecture                       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                                                                  
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐
│   Data Sources  │    │  Data Collection│    │    Indexing     │    │   Storage    │
│                 │    │                 │    │                 │    │             │
│ • Wikipedia API │───▶│ • URL Collection│───▶│ • Dense (FAISS) │───▶│ • FAISS     │
│ • Fixed URLs    │    │ • Text Extraction│    │ • Sparse (BM25) │    │   Index     │
│ • Random URLs   │    │ • Chunking       │    │                 │    │ • BM25      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    │   Index     │
                                                                     └─────────────┘
                                                                            │
                                                                            ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐
│   User Query    │    │   Retrieval     │    │    Fusion       │    │ Generation  │
│                 │    │                 │    │                 │    │             │
│ • Question      │───▶│ • Dense Search  │───▶│ • RRF Fusion    │───▶│ • Flan-T5   │
│                 │    │ • Sparse Search │    │ • Top-K Results │    │ • Grounded  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    │   Answer    │
                                                                     └─────────────┘
                                                                            │
                                                                            ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐
│   User Interface│    │   Evaluation    │    │   Metrics       │    │   Reports    │
│                 │    │                 │    │                 │    │             │
│ • Streamlit UI  │    │ • Question Gen  │    │ • MRR, Sim, Rel│    │ • PDF Report │
│ • Tables/Display│    │ • Pipeline      │    │ • Error Analysis│    │ • CSV Data  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    │ • Plots     │
                                                                     └─────────────┘
```

### Component Descriptions:
- **Data Sources**: Wikipedia articles via API and predefined URLs.
- **Data Collection**: Gathers URLs, extracts text, cleans and chunks content.
- **Indexing**: Creates dense (semantic) and sparse (keyword) indices for fast retrieval.
- **Storage**: Persists indices and corpus data.
- **Retrieval**: Searches dense and sparse indices for relevant chunks.
- **Fusion**: Combines results using Reciprocal Rank Fusion (RRF).
- **Generation**: Uses LLM to generate grounded answers from retrieved context.
- **User Interface**: Web app for querying and displaying results.
- **Evaluation**: Automated testing with metrics, error analysis, and reporting.

### Data Flow:
1. Data collection and indexing (one-time setup).
2. User query triggers retrieval and fusion.
3. Context passed to generation for answer.
4. Results displayed in UI and evaluated for metrics.

## Installation

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Generate fixed URLs (run once): `python src/url_collection.py` - Generates 200 fixed Wikipedia URLs related to Indian history and saves them to `data/fixed_urls.json` with metadata.

## Usage

### Testing
- Run unit tests: `pytest tests/` - Runs all unit tests to validate system components.
- To run a specific test file: `pytest tests/test_rag.py` - Runs tests specifically for the RAG system, including RRF fusion validation.

### Data Collection
- Run `python src/data_collection.py` to collect and preprocess Wikipedia articles (fixed + random URLs generated on-the-fly) - Extracts text from URLs, cleans and chunks it, and saves the corpus to `data/corpus.json`.

### Building Vector database and Indices
- Dense: `python src/dense_retrieval.py` - Builds and saves the FAISS dense vector index for semantic retrieval to `data/dense_index.faiss`.
- Sparse: `python src/sparse_retrieval.py` - Builds and saves the BM25 sparse index for keyword-based retrieval to `data/sparse_index.pkl`.

### Running the System
- UI: `streamlit run ui/app.py` - Launches the Streamlit web interface for querying the RAG system and viewing results in tables.

### Evaluation
1. Generate Q&A dataset: `python evaluation/question_generation.py` - Generates a Q&A dataset from the corpus using LLMs for evaluation and saves it to `data/qa_dataset.json`.
2. Run full evaluation pipeline: `python evaluation/evaluation_pipeline.py` - Runs queries through the RAG system, computes metrics (MRR, semantic similarity, relevance, error analysis, LLM-as-Judge, confidence calibration), and generates reports (CSV, PDF, plots) in the `reports/` directory.



## Evaluation Metrics

The evaluation pipeline computes three key metrics to assess system performance:

### Mean Reciprocal Rank (MRR)
- **Justification**: Measures the average reciprocal rank of the first relevant retrieved item, focusing on retrieval accuracy.
- **Calculation Method**: For each query, find the rank of the ground truth URL in retrieved URLs. Compute reciprocal rank (1/rank) if found, else 0. Average over all queries: MRR = (1/Q) * Σ(1/rank_i), where Q is number of queries.
- **Interpretation**: Higher MRR (closer to 1) indicates better retrieval performance, with relevant items ranked higher. Values near 0 suggest poor ranking.

### Semantic Similarity
- **Justification**: Measures how closely the generated answer matches the ground truth in meaning, useful for open-ended questions.
- **Calculation Method**: Encode generated answers and ground truths using SentenceTransformer ('all-MiniLM-L6-v2'). Compute cosine similarity between paired embeddings. Average the diagonal similarities: Score = mean(cosine_sim[i][i] for i in range(len(pairs))).
- **Interpretation**: Scores range from -1 to 1; higher values (closer to 1) indicate semantically similar answers. Values above 0.8 suggest good alignment; below 0.5 may indicate hallucinations or inaccuracies.

### Answer Relevance
- **Justification**: Ensures the answer is pertinent to the query, detecting off-topic responses.
- **Calculation Method**: Encode answers and questions using the same SentenceTransformer. Compute cosine similarity between answer and question embeddings for each pair. Average the similarities: Score = mean(cosine_sim[i][i] for i in range(len(pairs))).
- **Interpretation**: Scores from -1 to 1; higher values indicate answers are more relevant to the question. Scores above 0.7 are generally good; low scores suggest the answer doesn't address the query.

### Error Analysis
- **Justification**: Categorizes failures into retrieval, generation, and context issues to identify system weaknesses.
- **Calculation Method**: For each result, check if ground truth URL is retrieved (retrieval failure), semantic similarity <0.5 (generation hallucination), or relevance <0.5 (context irrelevant). Count by category and overall.
- **Interpretation**: High retrieval failures indicate indexing issues; high generation hallucinations suggest LLM problems; context issues point to retrieval relevance problems.

### LLM-as-Judge
- **Justification**: Uses an LLM to provide human-like evaluation of answer quality on multiple criteria.
- **Calculation Method**: Prompt Flan-T5 to score answers 1-5 on factual accuracy, completeness, relevance, and coherence. Parse scores and average across results.
- **Interpretation**: Scores from 1-5; higher scores indicate better quality. Provides automated explanations for qualitative assessment.

### Confidence Calibration
- **Justification**: Measures how well the system's confidence correlates with actual correctness.
- **Calculation Method**: Estimate confidence as average of semantic similarity and relevance. Compute Expected Calibration Error (ECE) by binning confidence and comparing to accuracy.
- **Interpretation**: Lower ECE indicates better calibration. Perfect calibration follows the diagonal in calibration curves.
