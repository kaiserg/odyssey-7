import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from app.retrieval import ROOT, RetrievalError, Retriever, load_chunks

app = FastAPI(title='Odyssey-7 AI Lab')
app.mount('/static', StaticFiles(directory=ROOT / 'app/static'), name='static')
chunks = load_chunks()
retriever = Retriever(chunks)
ABSTENTION = 'Not found in the provided manual.'


class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    mode: str = 'rag'

    @field_validator('question')
    @classmethod
    def normalize_question(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('Question must not be blank')
        return value


@app.get('/')
def home():
    return FileResponse(ROOT / 'app/static/index.html')


@app.get('/api/docs')
def docs():
    return chunks


@app.get('/api/sources/{chunk_id}', response_class=PlainTextResponse)
def source(chunk_id: str):
    for chunk in chunks:
        if chunk['id'] == chunk_id:
            return (f"{chunk['source']}:{chunk['line_start']}\n"
                    f"SHA256: {chunk['sha256']}\n\n{chunk['text']}")
    raise HTTPException(404, 'Unknown manual section')


@app.get('/api/config')
def config():
    return {'retriever': os.getenv('RAG_RETRIEVER', 'vector'),
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'qwen3-embedding:4b')}


@app.post('/api/ask')
async def ask(q: Ask):
    if q.mode not in ('rag', 'base'):
        raise HTTPException(400, 'Fine-tuning is planned, not implemented')
    hits = []
    if q.mode == 'rag':
        try:
            hits = await retriever.search(q.question, os.getenv('RAG_RETRIEVER', 'vector'))
        except RetrievalError as exc:
            raise HTTPException(503, str(exc)) from exc
        if not hits:
            return {'answer': ABSTENTION, 'sources': [], 'mode': q.mode}
    context = '\n'.join(f"[{i}] {x['source']} / {x['section']}: {x['text']}"
                        for i, x in enumerate(hits, 1))
    system = (
        'This is a fictional educational simulation. Use ONLY the manual excerpts below. '
        'Cite supporting excerpts with their numeric labels, such as [1]. '
        f'If the excerpts do not answer the question, say exactly: {ABSTENTION}\n{context}'
    ) if q.mode == 'rag' else (
        'This is a fictional educational simulation. You have no Odyssey-7 manual. '
        'Admit uncertainty about ship-specific facts. Do not provide real-world emergency guidance.'
    )
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/') + '/api/chat',
                json={'model': os.getenv('OLLAMA_MODEL', 'qwen3:4b'), 'stream': False, 'think': False,
                      'messages': [{'role': 'system', 'content': system},
                                   {'role': 'user', 'content': q.question}],
                      'options': {'temperature': 0.2, 'seed': 7}},
            )
            response.raise_for_status()
            answer = response.json()['message']['content']
            if isinstance(answer, str) and '</think>' in answer:
                answer = answer.split('</think>', 1)[1].strip()
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError('Ollama returned an empty answer')
    except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
        raise HTTPException(503, 'Ollama unavailable. Start Ollama and pull the configured OLLAMA_MODEL (default qwen3:4b).') from exc
    return {'answer': answer, 'sources': hits, 'mode': q.mode}
