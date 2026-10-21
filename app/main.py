import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from app.retrieval import ROOT, RetrievalError, Retriever, load_chunks
from app.inference import InferenceError, adapter_ready, mlx_paths, reply
from app.prompts import ABSTENTION, messages_for

app = FastAPI(title='Odyssey-7 AI Lab')
app.mount('/static', StaticFiles(directory=ROOT / 'app/static'), name='static')
chunks = load_chunks()
retriever = Retriever(chunks)


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
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'qwen3-embedding:4b'),
            'chat_backend': os.getenv('CHAT_BACKEND', 'ollama'),
            'chat_model': str(mlx_paths()[0].name) if os.getenv('CHAT_BACKEND') == 'mlx' else os.getenv('OLLAMA_MODEL', 'qwen3:4b'),
            'fine_tuned_available': adapter_ready()}


@app.post('/api/ask')
async def ask(q: Ask):
    if q.mode not in ('rag', 'base', 'finetuned'):
        raise HTTPException(400, 'Unknown mode')
    if q.mode == 'finetuned' and not adapter_ready():
        raise HTTPException(400, 'Fine-tuned mode requires CHAT_BACKEND=mlx and a validated local adapter')
    hits = []
    if q.mode in ('rag', 'finetuned'):
        try:
            hits = await retriever.search(q.question, os.getenv('RAG_RETRIEVER', 'vector'))
        except RetrievalError as exc:
            raise HTTPException(503, str(exc)) from exc
        if not hits:
            return {'answer': ABSTENTION, 'sources': [], 'mode': q.mode}
    messages = messages_for(q.question, hits, q.mode != 'base')
    try:
        answer = await reply(messages, adapted=q.mode == 'finetuned')
    except InferenceError as exc:
        raise HTTPException(503, str(exc)) from exc
    return {'answer': answer, 'sources': hits, 'mode': q.mode}
