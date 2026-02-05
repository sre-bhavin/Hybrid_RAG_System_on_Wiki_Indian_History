"""
Evaluation Metrics Module

Implements MRR and custom metrics.
"""

import numpy as np
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from src.generation import Generator

class Evaluator:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.judge_llm = Generator('google/flan-t5-base')  # For LLM-as-Judge

    def mean_reciprocal_rank(self, results: List[Dict]) -> float:
        """Calculate MRR at URL level."""
        rr_sum = 0
        for result in results:
            retrieved_urls = [chunk['url'] for chunk in result['retrieved_chunks']]  # Assume retrieved_chunks have metadata
            ground_truth_url = result['ground_truth_url']
            if ground_truth_url in retrieved_urls:
                rank = retrieved_urls.index(ground_truth_url) + 1
                rr_sum += 1 / rank
        return rr_sum / len(results) if results else 0

    def semantic_similarity(self, generated_answers: List[str], ground_truths: List[str]) -> float:
        """Custom metric: Semantic similarity between generated and ground truth."""
        gen_embeddings = self.embedder.encode(generated_answers)
        gt_embeddings = self.embedder.encode(ground_truths)
        similarities = cosine_similarity(gen_embeddings, gt_embeddings)
        return np.mean([similarities[i, i] for i in range(len(similarities))])

    def answer_relevance(self, answers: List[str], questions: List[str]) -> float:
        """Custom metric: Relevance of answer to question."""
        # Simple implementation: cosine similarity
        ans_embeddings = self.embedder.encode(answers)
        q_embeddings = self.embedder.encode(questions)
        similarities = cosine_similarity(ans_embeddings, q_embeddings)
        return np.mean([similarities[i, i] for i in range(len(similarities))])

    def error_analysis(self, results: List[Dict]) -> Dict:
        """Categorize failures by type and question category."""
        error_categories = {
            'retrieval_failure': 0,  # Ground truth URL not in top retrieved
            'generation_hallucination': 0,  # Low semantic similarity (<0.5)
            'context_irrelevant': 0,  # Low answer relevance (<0.5)
            'no_error': 0
        }
        category_errors = {cat: {'retrieval': 0, 'generation': 0, 'context': 0, 'none': 0} for cat in ['factual', 'comparative', 'inferential', 'multi-hop']}
        
        for result in results:
            retrieved_urls = [chunk['url'] for chunk in result['retrieved_chunks']]
            gt_url = result['ground_truth_url']
            sem_sim = self.semantic_similarity([result['answer']], [result['ground_truth']])
            rel = self.answer_relevance([result['answer']], [result['query']])
            category = result['category']
            
            if gt_url not in retrieved_urls:
                error_categories['retrieval_failure'] += 1
                category_errors[category]['retrieval'] += 1
            elif sem_sim < 0.5:
                error_categories['generation_hallucination'] += 1
                category_errors[category]['generation'] += 1
            elif rel < 0.5:
                error_categories['context_irrelevant'] += 1
                category_errors[category]['context'] += 1
            else:
                error_categories['no_error'] += 1
                category_errors[category]['none'] += 1
        
        return {'overall': error_categories, 'by_category': category_errors}

    def llm_as_judge(self, results: List[Dict]) -> Dict:
        """Use LLM to evaluate answers on multiple criteria."""
        scores = {'factual_accuracy': [], 'completeness': [], 'relevance': [], 'coherence': []}
        explanations = []
        
        for result in results:
            question = result['query']
            answer = result['answer']
            ground_truth = result['ground_truth']
            
            prompt = f"Evaluate the following answer on a scale of 1-5 for each criterion. Provide scores and brief explanation.\n\nQuestion: {question}\nAnswer: {answer}\nGround Truth: {ground_truth}\n\nCriteria:\n- Factual Accuracy: How factually correct is the answer?\n- Completeness: How complete is the answer?\n- Relevance: How relevant is the answer to the question?\n- Coherence: How coherent and well-structured is the answer?\n\nOutput format: Factual: X, Completeness: X, Relevance: X, Coherence: X\nExplanation: ..."
            
            evaluation = self.judge_llm.generate(prompt, [""], max_length=200).strip()
            # Parse scores (simple parsing)
            try:
                lines = evaluation.split('\n')
                score_line = lines[0]
                exp_line = ' '.join(lines[1:]) if len(lines) > 1 else ""
                
                # Extract numbers
                import re
                nums = re.findall(r'\d+', score_line)
                if len(nums) >= 4:
                    scores['factual_accuracy'].append(int(nums[0]))
                    scores['completeness'].append(int(nums[1]))
                    scores['relevance'].append(int(nums[2]))
                    scores['coherence'].append(int(nums[3]))
                else:
                    # Default if parsing fails
                    for key in scores:
                        scores[key].append(3)
                explanations.append(exp_line)
            except:
                for key in scores:
                    scores[key].append(3)
                explanations.append("Parsing failed")
        
        avg_scores = {k: np.mean(v) for k, v in scores.items()}
        return {'average_scores': avg_scores, 'explanations': explanations}

    def confidence_calibration(self, results: List[Dict]) -> Dict:
        """Estimate confidence and measure calibration."""
        confidences = []
        correctness = []
        
        for result in results:
            # Estimate confidence as average of semantic similarity and relevance (proxy)
            sem_sim = self.semantic_similarity([result['answer']], [result['ground_truth']])
            rel = self.answer_relevance([result['answer']], [result['query']])
            confidence = (sem_sim + rel) / 2  # Simple average as confidence score
            confidences.append(confidence)
            
            # Correctness: 1 if high similarity, else 0
            correctness.append(1 if sem_sim > 0.7 else 0)
        
        # Compute calibration metrics
        confidences = np.array(confidences)
        correctness = np.array(correctness)
        
        # Expected Calibration Error (ECE)
        bins = np.linspace(0, 1, 11)
        ece = 0
        for i in range(len(bins)-1):
            mask = (confidences >= bins[i]) & (confidences < bins[i+1])
            if np.sum(mask) > 0:
                avg_conf = np.mean(confidences[mask])
                avg_acc = np.mean(correctness[mask])
                ece += np.abs(avg_conf - avg_acc) * (np.sum(mask) / len(confidences))
        
        return {
            'confidences': confidences.tolist(),
            'correctness': correctness.tolist(),
            'expected_calibration_error': ece,
            'mean_confidence': np.mean(confidences),
            'accuracy': np.mean(correctness)
        }

    def evaluate(self, results: List[Dict]) -> Dict:
        """Run all metrics."""
        mrr = self.mean_reciprocal_rank(results)
        sem_sim = self.semantic_similarity([r['answer'] for r in results], [r['ground_truth'] for r in results])
        rel = self.answer_relevance([r['answer'] for r in results], [r['query'] for r in results])
        
        error_analysis = self.error_analysis(results)
        llm_judge = self.llm_as_judge(results)
        calibration = self.confidence_calibration(results)
        
        return {
            'MRR': mrr,
            'Semantic_Similarity': sem_sim,
            'Answer_Relevance': rel,
            'Error_Analysis': error_analysis,
            'LLM_as_Judge': llm_judge['average_scores'],
            'Confidence_Calibration': {
                'ECE': calibration['expected_calibration_error'],
                'Mean_Confidence': calibration['mean_confidence'],
                'Accuracy': calibration['accuracy'],
                'confidences': calibration['confidences'],
                'correctness': calibration['correctness']
            }
        }

# Justifications and Details:
#
# Semantic Similarity:
# Justification: Measures how closely the generated answer matches the ground truth in meaning, useful for open-ended questions.
# Calculation Method: Encode generated answers and ground truths using SentenceTransformer ('all-MiniLM-L6-v2'). Compute cosine similarity between paired embeddings. Average the diagonal similarities: Score = mean(cosine_sim[i][i] for i in range(len(pairs))).
# Interpretation: Scores range from -1 to 1; higher values (closer to 1) indicate semantically similar answers. Values above 0.8 suggest good alignment; below 0.5 may indicate hallucinations or inaccuracies.
#
# Answer Relevance:
# Justification: Ensures the answer is pertinent to the query, detecting off-topic responses.
# Calculation Method: Encode answers and questions using the same SentenceTransformer. Compute cosine similarity between answer and question embeddings for each pair. Average the similarities: Score = mean(cosine_sim[i][i] for i in range(len(pairs))).
# Interpretation: Scores from -1 to 1; higher values indicate answers are more relevant to the question. Scores above 0.7 are generally good; low scores suggest the answer doesn't address the query.