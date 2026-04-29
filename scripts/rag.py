import json
import re
from pathlib import Path
from typing import List, Tuple


class SimpleRAG:
    def __init__(self, knowledge_file: str):
        self.qa_pairs = self._load_knowledge(knowledge_file)

    def _load_knowledge(self, filepath: str) -> List[Tuple[str, str]]:
        pairs = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                text = data.get('text', '')
                if '<|user|>' in text and '<|assistant|>' in text:
                    parts = text.split('<|assistant|>')
                    if len(parts) >= 2:
                        question = parts[0].replace('<|user|>', '').strip()
                        answer = parts[1].strip()
                        pairs.append((question, answer))
        return pairs

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        scored = []
        for question, answer in self.qa_pairs:
            question_lower = question.lower()
            question_words = set(re.findall(r'\w+', question_lower))
            
            overlap = len(query_words & question_words)
            if overlap > 0:
                if any(word in question_lower for word in query_words):
                    scored.append((overlap, question, answer))
        
        scored.sort(reverse=True)
        return [a for _, q, a in scored[:top_k]]


def get_context_for_query(query: str) -> str:
    rag = SimpleRAG('./data/processed/train_book_content.jsonl')
    results = rag.retrieve(query, top_k=2)
    if results:
        return "\n".join(results)
    return ""