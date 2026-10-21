import asyncio
import json
from pathlib import Path

import httpx
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import retrieval
from app.main import app
from scripts.evaluate import answer_metrics


def test_section_metadata_and_links():
    chunks = retrieval.load_chunks()
    assert len(chunks) == 6
    assert len({c['id'] for c in chunks}) == 6
    client = TestClient(app)
    for chunk in chunks:
        content = (retrieval.ROOT / 'documents' / chunk['source']).read_text()
        assert content.splitlines()[chunk['line_start'] - 1] == '## ' + chunk['section']
        assert len(chunk['sha256']) == 64
        response = client.get(chunk['url'])
        assert response.status_code == 200
        assert chunk['text'] in response.text
    assert client.get('/api/sources/missing').status_code == 404


def test_vector_search_cache_threshold_and_model_change(monkeypatch):
    calls = []
    async def fake_embed(texts, model):
        calls.append((texts, model))
        return np.eye(2, dtype='float32') if len(texts) == 2 else np.array([[1, 0]], dtype='float32')
    monkeypatch.setattr(retrieval, 'embed', fake_embed)
    engine = retrieval.Retriever([{'text': 'oxygen pressure', 'id': 'oxygen'}, {'text': 'navigation reset', 'id': 'nav'}])
    async def run():
        hits = await engine.search('air pressure', threshold=0.5)
        assert [h['id'] for h in hits] == ['oxygen']
        assert await engine.search('air pressure', threshold=1.1) == []
        assert len(calls) == 3  # documents embedded once, two query calls
        monkeypatch.setenv('EMBEDDING_MODEL', 'another-model')
        await engine.search('air pressure')
        assert len(calls) == 5
    asyncio.run(run())


@pytest.mark.parametrize('body', [{}, {'embeddings': [[0, 0]]}, {'embeddings': [[1], [2]]}, {'embeddings': [[float('nan')]]}])
def test_invalid_embeddings(monkeypatch, body):
    async def post(self, url, **kwargs):
        # NaN is deliberately injected after JSON parsing.
        response = httpx.Response(200, json={}, request=httpx.Request('POST', url))
        response.json = lambda: body
        return response
    monkeypatch.setattr(httpx.AsyncClient, 'post', post)
    with pytest.raises(retrieval.RetrievalError):
        asyncio.run(retrieval.embed(['question'], 'test-model'))


def test_embedding_failure_api(monkeypatch):
    async def post(*args, **kwargs):
        raise httpx.ConnectError('offline')
    monkeypatch.setattr(httpx.AsyncClient, 'post', post)
    monkeypatch.setenv('RAG_RETRIEVER', 'vector')
    response = TestClient(app).post('/api/ask', json={'question': 'oxygen'})
    assert response.status_code == 503
    assert 'embeddings unavailable' in response.json()['detail']


def test_dataset_and_citation_scoring():
    cases = [json.loads(line) for line in Path('evaluation/questions.jsonl').read_text().splitlines()]
    ids = {c['id'] for c in retrieval.load_chunks()}
    assert len(cases) == len({c['id'] for c in cases}) == 10
    assert all(set(c['expected_sources']) <= ids for c in cases)
    case = cases[0]
    result = answer_metrics('LS-P1 AUX-02 MR-17 [1] [9]', [{'id': case['expected_sources'][0]}], case)
    assert result['expected_term_coverage'] == 1
    assert result['invalid_citation_count'] == 1
    assert result['cites_expected_section'] is True


def test_vector_api_uses_semantic_hits(monkeypatch):
    from app import main
    engine = retrieval.Retriever(retrieval.load_chunks())
    async def fake_embed(texts, model):
        if len(texts) == 6:
            return np.eye(6, dtype='float32')
        # A paraphrase without lexical overlap still selects the oxygen section.
        return np.array([[1, 0, 0, 0, 0, 0]], dtype='float32')
    async def post(self, url, **kwargs):
        assert 'AUX-02' in kwargs['json']['messages'][0]['content']
        return httpx.Response(200, json={'message': {'content': 'Use AUX-02 [1]'}}, request=httpx.Request('POST', url))
    monkeypatch.setattr(retrieval, 'embed', fake_embed)
    monkeypatch.setattr(main, 'retriever', engine)
    monkeypatch.setattr(httpx.AsyncClient, 'post', post)
    monkeypatch.setenv('RAG_RETRIEVER', 'vector')
    response = TestClient(app).post('/api/ask', json={'question': 'The atmosphere is getting thin'})
    assert response.status_code == 200
    data = response.json()
    assert data['sources'][0]['id'] == 'life-support:oxygen-emergency-ls-04'
    assert data['answer'] == 'Use AUX-02 [1]'
