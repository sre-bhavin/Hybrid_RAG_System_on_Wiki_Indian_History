"""
Evaluation Pipeline Module

Runs the full evaluation: load questions, run RAG, compute metrics, generate reports.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.rag_system import HybridRAG
from evaluation.metrics import Evaluator
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from fpdf import FPDF
from typing import List, Dict

class EvaluationPipeline:
    def __init__(self):
        self.rag = HybridRAG()
        self.evaluator = Evaluator()

    def run_evaluation(self, qa_dataset_path: str, corpus_path: str, output_dir: str = 'reports/'):
        """Run full evaluation pipeline."""
        # Load data
        self.rag.load_corpus(corpus_path)
        with open(qa_dataset_path, 'r') as f:
            qa_data = json.load(f)
        
        results = []
        for qa in qa_data:
            result = self.rag.answer_query(qa['question'])
            result.update({
                'ground_truth': qa['ground_truth'],
                'ground_truth_url': qa['source_url'],
                'category': qa['category']
            })
            # Add retrieved chunks with metadata (simplified)
            result['retrieved_chunks'] = [{'url': 'placeholder', 'text': chunk} for chunk in result['context_chunks']]
            results.append(result)
        
        # Compute metrics
        metrics = self.evaluator.evaluate(results)
        
        # Generate reports
        self.generate_csv_report(results, metrics, f'{output_dir}/results.csv')
        self.generate_pdf_report(metrics, results, f'{output_dir}/plots.png', f'{output_dir}/report.pdf')
        self.generate_plots(results, metrics, f'{output_dir}/plots.png')
        
        return metrics, results

    def generate_csv_report(self, results: List[Dict], metrics: Dict, path: str):
        """Generate CSV report."""
        df = pd.DataFrame(results)
        df['MRR'] = metrics['MRR']  # Add overall metrics
        df.to_csv(path, index=False)

    def generate_pdf_report(self, metrics: Dict, results: List[Dict], plots_path: str, path: str):
        """Generate comprehensive PDF report."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(200, 10, txt="Hybrid RAG System Evaluation Report", ln=True, align='C')
        pdf.ln(10)
        
        # Architecture Diagram (text-based)
        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="1. System Architecture", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, txt="""
User Query -> [Dense Retrieval (FAISS)] + [Sparse Retrieval (BM25)] -> RRF Fusion -> Context Chunks -> LLM Generation (Flan-T5) -> Answer

Data Flow:
- URL Collection -> Text Extraction -> Chunking -> Indexing (Dense/Sparse)
- Evaluation: Q&A Generation -> Query Processing -> Metrics (MRR, Similarity, etc.) -> Reports
        """)
        pdf.ln(5)
        
        # Evaluation Results
        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="2. Evaluation Results", ln=True)
        pdf.set_font("Arial", size=10)
        
        # Basic metrics table
        pdf.cell(50, 8, "Metric", 1)
        pdf.cell(50, 8, "Value", 1)
        pdf.ln()
        for key, value in metrics.items():
            if not isinstance(value, dict):
                pdf.cell(50, 8, str(key), 1)
                pdf.cell(50, 8, f"{value:.4f}" if isinstance(value, float) else str(value), 1)
                pdf.ln()
        
        pdf.ln(5)
        
        # Error Analysis
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, txt="Error Analysis", ln=True)
        pdf.set_font("Arial", size=10)
        error_overall = metrics.get('Error_Analysis', {}).get('overall', {})
        for err, count in error_overall.items():
            pdf.cell(100, 8, err.replace('_', ' ').title(), 1)
            pdf.cell(50, 8, str(count), 1)
            pdf.ln()
        
        pdf.ln(5)
        
        # Innovative Approaches
        pdf.set_font("Arial", size=14, style='B')
        pdf.cell(200, 10, txt="3. Innovative Evaluation Approaches", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, txt="""
- Error Analysis: Automatic categorization of failures (retrieval, generation, context) by question type.
- LLM-as-Judge: Uses Flan-T5 to evaluate answers on factual accuracy, completeness, relevance, and coherence.
- Confidence Calibration: Measures calibration with Expected Calibration Error (ECE) and provides calibration curves.
- Ablation Studies: Compare dense-only, sparse-only, and hybrid retrieval performance (not implemented in this run).
        """)
        
        # Include plots
        if os.path.exists(plots_path):
            pdf.add_page()
            pdf.set_font("Arial", size=14, style='B')
            pdf.cell(200, 10, txt="4. Visualizations", ln=True)
            pdf.image(plots_path, x=10, y=30, w=180)
        
        # Sample Results Table
        pdf.add_page()
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, txt="Sample Query Results", ln=True)
        pdf.set_font("Arial", size=8)
        pdf.cell(30, 8, "Query", 1)
        pdf.cell(50, 8, "Answer", 1)
        pdf.cell(20, 8, "MRR", 1)
        pdf.cell(30, 8, "Similarity", 1)
        pdf.ln()
        for i, result in enumerate(results[:5]):  # First 5
            pdf.cell(30, 8, result['query'][:25] + "...", 1)
            pdf.cell(50, 8, result['answer'][:40] + "...", 1)
            pdf.cell(20, 8, f"{metrics.get('MRR', 0):.2f}", 1)
            pdf.cell(30, 8, f"{metrics.get('Semantic_Similarity', 0):.2f}", 1)
            pdf.ln()
        
        pdf.output(path)

    def generate_plots(self, results: List[Dict], metrics: Dict, path: str):
        """Generate plots including error analysis and calibration."""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Response times
        times = [r['response_time'] for r in results]
        axes[0, 0].hist(times, bins=20)
        axes[0, 0].set_title('Response Times')
        
        # Question categories
        categories = [r['category'] for r in results]
        sns.countplot(x=categories, ax=axes[0, 1])
        axes[0, 1].set_title('Question Categories')
        
        # Error analysis overall
        error_overall = metrics['Error_Analysis']['overall']
        axes[0, 2].bar(error_overall.keys(), error_overall.values())
        axes[0, 2].set_title('Error Categories Overall')
        axes[0, 2].tick_params(axis='x', rotation=45)
        
        # Error by category
        error_by_cat = metrics['Error_Analysis']['by_category']
        cats = list(error_by_cat.keys())
        retrieval = [error_by_cat[c]['retrieval'] for c in cats]
        generation = [error_by_cat[c]['generation'] for c in cats]
        context = [error_by_cat[c]['context'] for c in cats]
        
        x = np.arange(len(cats))
        width = 0.25
        axes[1, 0].bar(x - width, retrieval, width, label='Retrieval')
        axes[1, 0].bar(x, generation, width, label='Generation')
        axes[1, 0].bar(x + width, context, width, label='Context')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(cats)
        axes[1, 0].set_title('Errors by Question Type')
        axes[1, 0].legend()
        
        # Calibration curve
        calib = metrics['Confidence_Calibration']
        confs = calib['confidences']
        correct = calib['correctness']
        bins = np.linspace(0, 1, 11)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        accuracies = []
        for i in range(len(bins)-1):
            mask = (np.array(confs) >= bins[i]) & (np.array(confs) < bins[i+1])
            if np.sum(mask) > 0:
                accuracies.append(np.mean(np.array(correct)[mask]))
            else:
                accuracies.append(0)
        
        axes[1, 1].plot(bin_centers, accuracies, 'o-', label='Accuracy')
        axes[1, 1].plot([0, 1], [0, 1], 'r--', label='Perfect Calibration')
        axes[1, 1].set_xlabel('Confidence')
        axes[1, 1].set_ylabel('Accuracy')
        axes[1, 1].set_title('Calibration Curve')
        axes[1, 1].legend()
        
        # LLM Judge scores
        judge_scores = metrics['LLM_as_Judge']
        axes[1, 2].bar(judge_scores.keys(), judge_scores.values())
        axes[1, 2].set_title('LLM-as-Judge Scores')
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(path)

if __name__ == "__main__":
    pipeline = EvaluationPipeline()
    metrics, results = pipeline.run_evaluation('data/qa_dataset.json', 'data/corpus.json')
    print("Evaluation completed.")
    print(" Detailed results saved in reports directory.")
    print(" Metrics:", metrics)
    