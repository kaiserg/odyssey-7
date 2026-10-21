"""Offline integration tests; real model verification is a separate smoke run."""
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize('path', ['/', '/static/app.js', '/static/style.css', '/api/docs'])
def test_startup_routes(path):
    assert client.get(path).status_code == 200

@pytest.mark.parametrize('question', ['', '   ', 'x' * 4001])
def test_invalid_questions(question):
    assert client.post('/api/ask', json={'question': question}).status_code == 422


def test_unimplemented_mode():
    assert client.post('/api/ask', json={'question': 'Oxygen?', 'mode': 'fine-tuned'}).status_code == 400


@pytest.mark.parametrize('mode', ['base', 'rag'])
def test_model_request_and_traceability(monkeypatch, mode):
    async def post(self, url, **kwargs):
        payload = kwargs['json']
        assert payload['stream'] is False
        assert payload['think'] is False
        system = payload['messages'][0]['content']
        if mode == 'rag':
            assert '[1] life-support.md / Oxygen Emergency LS-04' in system
            assert 'AUX-02' in system
        else:
            assert 'AUX-02' not in system
        return httpx.Response(200, json={'message': {'content': 'Internal prefix</think>Example answer [1]'}}, request=httpx.Request('POST', url))
    monkeypatch.setattr(httpx.AsyncClient, 'post', post)
    response = client.post('/api/ask', json={'question': 'oxygen pressure drops', 'mode': mode})
    assert response.status_code == 200
    data = response.json()
    assert data['mode'] == mode
    assert data['answer'] == 'Example answer [1]'
    if mode == 'rag':
        assert data['sources'][0]['source'] == 'life-support.md'
        assert 'AUX-02' in data['sources'][0]['text']
    else:
        assert data['sources'] == []


@pytest.mark.parametrize('failure', ['offline', 'malformed', 'empty'])
def test_model_failures(monkeypatch, failure):
    async def post(self, url, **kwargs):
        if failure == 'offline':
            raise httpx.ConnectError('offline')
        body = {} if failure == 'malformed' else {'message': {'content': ''}}
        return httpx.Response(200, json=body, request=httpx.Request('POST', url))
    monkeypatch.setattr(httpx.AsyncClient, 'post', post)
    response = client.post('/api/ask', json={'question': 'oxygen'})
    assert response.status_code == 503
    assert 'Ollama unavailable' in response.json()['detail']


def test_no_evidence_abstains_without_model(monkeypatch):
    async def unexpected(*args, **kwargs):
        pytest.fail('No-evidence requests must not invoke Ollama')
    monkeypatch.setattr(httpx.AsyncClient, 'post', unexpected)
    response = client.post('/api/ask', json={'question': 'Who is the captain?'})
    assert response.status_code == 200
    assert response.json() == {'answer': 'Not found in the provided manual.', 'sources': [], 'mode': 'rag'}
