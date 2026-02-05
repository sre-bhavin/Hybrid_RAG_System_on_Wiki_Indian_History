"""
Question Generation Module

Generate Q&A pairs from the corpus using LLMs.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.generation import Generator
import json
import random
from typing import List, Dict

class QuestionGenerator:
    def __init__(self):
        self.generator = Generator('google/flan-t5-base')  # Use a better model for generation

    def generate_questions(self, corpus: List[Dict], num_questions: int = 100) -> List[Dict]:
        """Generate diverse Q&A pairs."""
        questions = []
        categories = ['factual', 'comparative', 'inferential', 'multi-hop']
        
        for _ in range(num_questions):
            chunk = random.choice(corpus)
            category = random.choice(categories)
            
            # Prompt for question generation
            prompt = f"Generate a {category} question based on this text: {chunk['text']}\nQuestion:"
            question = self.generator.generate_question(chunk['text'], category, max_length=50).strip()
            
            # Generate answer
            answer = self.generator.generate(question, [chunk['text']], max_length=100).strip()
            
            questions.append({
                'question': question,
                'ground_truth': answer,
                'source_url': chunk['url'],
                'source_chunk_id': chunk['chunk_id'],
                'category': category
            })
        
        return questions

if __name__ == "__main__":
    with open('data/corpus.json', 'r') as f:
        corpus = json.load(f)
    gen = QuestionGenerator()
    qa_pairs = gen.generate_questions(corpus, 100)
    with open('data/qa_dataset.json', 'w') as f:
        json.dump(qa_pairs, f)
    print("Generated QA pairs saved to data/qa_dataset.json")