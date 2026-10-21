"""Six section chunks, a lexical baseline, and an in-memory FAISS cosine index."""
import asyncio
import hashlib
import os
import re
from pathlib import Path

import faiss
import httpx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]


def load_chunks(directory=ROOT / 'documents'):
    chunks = []
    for file in sorted(directory.glob('*.md')):
        content = file.read_text(encoding='utf-8')
        headings = list(re.finditer(r'^## (.+)$', content, re.MULTILINE))
        for i, heading in enumerate(headings):
            section = heading.group(1).strip()
            end = headings[i + 1].start() if i + 1 < len(headings) else len(content)
            text = content[heading.start():end].strip()
            slug = re.sub(r'[^a-z0-9]+', '-', section.lower()).strip('-')
            chunk_id = f'{file.stem}:{slug}'
            chunks.append({
                'id': chunk_id, 'source': file.name, 'section': section, 'text': text,
                'line_start': content[:heading.start()].count('\n') + 1,
                'sha256': hashlib.sha256(content.encode()).hexdigest(),
                'url': f'/api/sources/{chunk_id}',
            })
    if not chunks:
        raise ValueError('No manual sections found')
    return chunks


class RetrievalError(Exception):
    """Local embedding service or vector response is unavailable/invalid."""


async def embed(texts, model):
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/') + '/api/embed',
                json={'model': model, 'input': texts, 'truncate': False},
            )
            response.raise_for_status()
            vectors = np.asarray(response.json()['embeddings'], dtype='float32')
        if (vectors.ndim != 2 or vectors.shape[0] != len(texts) or vectors.shape[1] == 0
                or not np.isfinite(vectors).all() or np.any(np.linalg.norm(vectors, axis=1) == 0)):
            raise ValueError('Invalid embedding shape or values')
        faiss.normalize_L2(vectors)
        return vectors
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise RetrievalError(f'Local embeddings unavailable. Start Ollama and pull {model}.') from exc


class Retriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.lexical = self.vectorizer.fit_transform([c['text'] for c in chunks])
        self.index = None
        self.model = None
        self.lock = asyncio.Lock()

    async def search(self, question, backend='vector', k=3, threshold=None):
        if backend == 'tfidf':
            scores = cosine_similarity(self.vectorizer.transform([question]), self.lexical)[0]
            order = np.argsort(-scores, kind='stable')[:k]
            minimum = 0 if threshold is None else threshold
            return [dict(self.chunks[i], score=float(scores[i])) for i in order if scores[i] > minimum]
        if backend != 'vector':
            raise RetrievalError('RAG_RETRIEVER must be vector or tfidf')
        model = os.getenv('EMBEDDING_MODEL', 'qwen3-embedding:4b')
        async with self.lock:
            if self.index is None or self.model != model:
                vectors = await embed([c['text'] for c in self.chunks], model)
                index = faiss.IndexFlatIP(vectors.shape[1])
                index.add(vectors)
                self.index, self.model = index, model
            # Keep model and index consistent if configuration changes between calls.
            query = await embed([question], model)
            if query.shape[1] != self.index.d:
                raise RetrievalError('Embedding dimensions changed; restart the app and verify the model.')
            scores, positions = self.index.search(query, min(k, len(self.chunks)))
        minimum = float(os.getenv('RAG_MIN_SCORE', '0.55')) if threshold is None else threshold
        return [dict(self.chunks[i], score=float(score))
                for score, i in zip(scores[0], positions[0]) if i >= 0 and score >= minimum]
