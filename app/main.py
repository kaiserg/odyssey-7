import os
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title='Odyssey-7 AI Lab')
app.mount('/static',StaticFiles(directory=ROOT/'app/static'),name='static')
chunks=[]
for file in sorted((ROOT/'documents').glob('*.md')):
    for part in file.read_text().split('\n## '):
        if len(part)>30:chunks.append({'source':file.name,'section':part.splitlines()[0].strip('# '),'text':part})
vectorizer=TfidfVectorizer(stop_words='english',ngram_range=(1,2))
index=vectorizer.fit_transform([c['text'] for c in chunks])
class Ask(BaseModel):
    question:str
    mode:str='rag'
@app.get('/')
def home():return FileResponse(ROOT/'app/static/index.html')
@app.get('/api/docs')
def docs():return [{'source':c['source'],'section':c['section']} for c in chunks]
@app.post('/api/ask')
async def ask(q:Ask):
    if q.mode not in ('rag','base'):raise HTTPException(400,'Fine-tuning is planned, not implemented')
    hits=[]
    if q.mode=='rag' and q.question.strip():
        scores=cosine_similarity(vectorizer.transform([q.question]),index)[0]
        hits=[dict(chunks[i],score=round(float(scores[i]),3)) for i in sorted(range(len(scores)),key=lambda i:-scores[i])[:3] if scores[i]>0]
    context='\n'.join(f"[{i}] {x['source']} / {x['section']}: {x['text']}" for i,x in enumerate(hits,1))
    system=('Use ONLY these fictional ship manual excerpts. Cite [1], [2]. If unsupported say Not found in the provided manual.\n'+context) if q.mode=='rag' else 'You have no Odyssey-7 manual. Admit uncertainty about ship-specific facts.'
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r=await client.post(os.getenv('OLLAMA_URL','http://localhost:11434')+'/api/chat',json={'model':os.getenv('OLLAMA_MODEL','qwen3:4b'),'stream':False,'messages':[{'role':'system','content':system},{'role':'user','content':q.question}],'options':{'temperature':0.2}})
            r.raise_for_status();answer=r.json()['message']['content']
    except (httpx.HTTPError,KeyError,ValueError) as e:raise HTTPException(503,'Ollama unavailable. Start Ollama and pull qwen3:4b.') from e
    return {'answer':answer,'sources':hits,'mode':q.mode}
