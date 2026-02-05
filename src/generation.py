"""
Response Generation Module

Uses an open-source LLM to generate answers based only on provided context.
"""

from transformers import pipeline
import torch
from typing import List

class Generator:
    def __init__(self, model_name: str = 'google/flan-t5-base'):
        # Use Flan-T5 for better instruction-following and reduced hallucination
        self.pipeline = pipeline('text2text-generation', model=model_name, device=0 if torch.cuda.is_available() else -1)

    def generate(self, query: str, context: List[str], max_length: int = 200) -> str:
        """Generate answer given query and context, based only on context."""
        context_text = ' '.join(context)
        prompt = f"Answer the question based only on the following context. If the answer is not in the context, say 'I don't know'.\n\nContext: {context_text}\n\nQuestion: {query}"
        
        result = self.pipeline(prompt, max_new_tokens=max_length, do_sample=False, num_return_sequences=1)
        answer = result[0]['generated_text'].strip()
        
        # Post-process to ensure it doesn't hallucinate
        if "I don't know" in answer or len(answer.split()) < 3:
            return answer
        # Check if answer is grounded in context (simple check)
        context_lower = context_text.lower()
        answer_lower = answer.lower()
        if not any(word in context_lower for word in answer_lower.split() if len(word) > 3):
            return "I don't know"
        return answer

    def generate_question(self, context: str, category: str, max_length: int = 50) -> str:
        """Generate a question based on context."""
        prompt = f"Generate a {category} question based on this text: {context}\nQuestion:"
        
        result = self.pipeline(prompt, max_new_tokens=max_length, do_sample=True, temperature=0.7, num_return_sequences=1)
        question = result[0]['generated_text'].strip()
        
        # Clean up the question
        if question.startswith("Question:"):
            question = question[9:].strip()
        if question.endswith("?"):
            return question
        return question + "?"

if __name__ == "__main__":
    gen = Generator()
    answer = gen.generate("What is machine learning?", ["Machine learning is a subset of artificial intelligence."])
    print("Generated Answer:", answer)