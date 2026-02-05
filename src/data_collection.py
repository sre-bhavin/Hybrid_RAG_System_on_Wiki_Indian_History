"""
Data Collection Module

This module handles collecting Wikipedia URLs, extracting text, cleaning, and chunking.
"""

import json
import wikipedia
import nltk
from nltk.tokenize import sent_tokenize
import re
from typing import List, Dict, Tuple
from url_collection import generate_random_urls

# Download NLTK data if needed
nltk.download('punkt')
nltk.download('punkt_tab')

def load_fixed_urls(file_path: str) -> List[str]:
    """Load fixed URLs from JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return [item['url'] for item in data]

def sample_random_urls(num_urls: int = 300) -> List[str]:
    """Generate random Indian history Wikipedia URLs."""
    urls_data = generate_random_urls(num_urls)
    return [item['url'] for item in urls_data]

def extract_text_from_url(url: str) -> str:
    """Extract main text content from a Wikipedia URL using wikipedia library."""
    try:
        # Extract title from URL
        title = url.split('/')[-1].replace('_', ' ')
        page = wikipedia.page(title, auto_suggest=False)
        return page.content
    except Exception as e:
        print(f"Error extracting {url}: {e}")
        return ""

def clean_text(text: str) -> str:
    """Clean and preprocess text."""
    # Implement cleaning: remove extra spaces, etc.
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """Chunk text into smaller pieces with overlap."""
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        words = sentence.split()
        if current_length + len(words) > chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                # Overlap: keep last few sentences
                overlap_sentences = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    s_words = s.split()
                    if overlap_length + len(s_words) > overlap:
                        break
                    overlap_sentences.insert(0, s)
                    overlap_length += len(s_words)
                current_chunk = overlap_sentences
                current_length = overlap_length
        current_chunk.append(sentence)
        current_length += len(words)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def preprocess_corpus(urls: List[str]) -> List[Dict]:
    """Preprocess the entire corpus: extract, clean, chunk."""
    corpus = []
    for url in urls:
        text = extract_text_from_url(url)
        # if len(text.split()) < 200:
        #     continue  # Skip short pages
        print(f"Processing URL: {url} with {len(text.split())} words.")
        cleaned_text = clean_text(text)
        chunks = chunk_text(cleaned_text)
        for i, chunk in enumerate(chunks):
            corpus.append({
                'url': url,
                'title': url.split('/')[-1].replace('_', ' '),
                'chunk_id': f"{url}_{i}",
                'text': chunk
            })
    return corpus

if __name__ == "__main__":
    fixed_urls = load_fixed_urls('data/fixed_urls.json')
    random_urls = load_fixed_urls('data/random_urls.json') # sample_random_urls(300)
    all_urls = fixed_urls + random_urls
    print(f"Total URLs to process: {len(all_urls)}")
    corpus = preprocess_corpus(all_urls)
    # Save corpus
    with open('data/corpus.json', 'w') as f:
        json.dump(corpus, f)