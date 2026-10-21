import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import inference
from app.main import app
from scripts.prepare_training import prepare
from scripts.validate_training import data_manifest
from scripts.evaluate import answer_metrics


def test_training_is_deterministic_and_separate(tmp_path):
    manifest = data_manifest()
    assert manifest['train']['rows'] == 24
    assert manifest['valid']['rows'] == 8
    prepare(tmp_path)
    for split in ('train', 'valid'):
        assert (tmp_path / f'{split}.jsonl').read_bytes() == Path(f'training/data/{split}.jsonl').read_bytes()


def test_missing_adapter_stays_disabled(monkeypatch, tmp_path):
    monkeypatch.setenv('CHAT_BACKEND', 'mlx')
    monkeypatch.setenv('MLX_ADAPTER_PATH', str(tmp_path))
    client = TestClient(app)
    assert client.get('/api/config').json()['fine_tuned_available'] is False
    assert client.post('/api/ask', json={'question': 'oxygen', 'mode': 'finetuned'}).status_code == 400


def test_readiness_checks_hashes_and_model(monkeypatch, tmp_path):
    model, adapter = tmp_path / 'model', tmp_path / 'adapter'
    model.mkdir()
    adapter.mkdir()
    (model / 'config.json').write_text('{}')
    (model / 'model.safetensors').write_bytes(b'base-weights')
    (adapter / 'adapters.safetensors').write_bytes(b'fixture')
    (adapter / 'adapter_config.json').write_text('{}')
    python = tmp_path / 'python'
    python.touch()
    manifest = {'model_path': str(model), 'model_weights': inference.weight_stamp(model), 'model_config_sha256': inference.digest(model / 'config.json'),
                'adapter_sha256': inference.digest(adapter / 'adapters.safetensors'),
                'adapter_config_sha256': inference.digest(adapter / 'adapter_config.json')}
    (adapter / 'ready.json').write_text(json.dumps(manifest))
    monkeypatch.setenv('MLX_MODEL_PATH', str(model))
    monkeypatch.setenv('MLX_ADAPTER_PATH', str(adapter))
    monkeypatch.setenv('MLX_PYTHON', str(python))
    monkeypatch.setenv('CHAT_BACKEND', 'mlx')
    assert inference.adapter_ready()
    monkeypatch.setenv('CHAT_BACKEND', 'ollama')
    assert not inference.adapter_ready()
    monkeypatch.setenv('CHAT_BACKEND', 'mlx')
    (adapter / 'adapters.safetensors').write_bytes(b'modified')
    assert not inference.adapter_ready()


def test_missing_mlx_environment_has_clear_error(monkeypatch, tmp_path):
    monkeypatch.setenv('CHAT_BACKEND', 'mlx')
    monkeypatch.setenv('MLX_PYTHON', str(tmp_path / 'missing'))
    with pytest.raises(inference.InferenceError, match='not configured'):
        asyncio.run(inference.reply([{'role': 'user', 'content': 'hello'}]))


def test_format_metric():
    case = {'expected_sources': ['a'], 'expected_terms': ['SCAN']}
    assert answer_metrics('Answer: SCAN\nSources: [1]', [{'id': 'a'}], case)['format_compliant']
    assert not answer_metrics('Here is SCAN [1]', [{'id': 'a'}], case)['format_compliant']


def test_finetuned_reuses_rag_context_and_no_evidence_guard(monkeypatch):
    from app import main
    monkeypatch.setattr(main, 'adapter_ready', lambda: True)
    monkeypatch.setenv('RAG_RETRIEVER', 'tfidf')
    calls = []
    async def reply(messages, adapted=False):
        calls.append((messages, adapted))
        return 'Answer: Use AUX-02.\nSources: [1]'
    monkeypatch.setattr(main, 'reply', reply)
    client = TestClient(app)
    rag = client.post('/api/ask', json={'question': 'oxygen pressure', 'mode': 'rag'}).json()
    adapted = client.post('/api/ask', json={'question': 'oxygen pressure', 'mode': 'finetuned'}).json()
    assert rag['sources'] == adapted['sources']
    assert calls[0][0] == calls[1][0]
    assert calls[0][1] is False and calls[1][1] is True
    response = client.post('/api/ask', json={'question': 'Who is the captain?', 'mode': 'finetuned'})
    assert response.status_code == 200
    assert response.json()['sources'] == []
    assert len(calls) == 2  # zero evidence never reaches either model


def test_mlx_timeout_reaps_child(monkeypatch, tmp_path):
    (tmp_path / 'config.json').write_text('{}')
    python = tmp_path / 'python'
    python.touch()
    monkeypatch.setenv('MLX_MODEL_PATH', str(tmp_path))
    monkeypatch.setenv('MLX_PYTHON', str(python))
    class Process:
        returncode = None
        killed = False
        async def communicate(self, payload):
            raise asyncio.TimeoutError()
        def kill(self):
            self.killed = True
        async def wait(self):
            self.returncode = -9
    process = Process()
    async def spawn(*args, **kwargs):
        assert kwargs['env']['HF_HUB_OFFLINE'] == '1'
        return process
    monkeypatch.setattr(asyncio, 'create_subprocess_exec', spawn)
    with pytest.raises(inference.InferenceError, match='timed out'):
        asyncio.run(inference.mlx_reply([], False))
    assert process.killed and process.returncode == -9


def test_mlx_interpreter_keeps_virtualenv_symlink(monkeypatch, tmp_path):
    target = tmp_path / 'base-python'
    target.touch()
    interpreter = tmp_path / 'venv-python'
    interpreter.symlink_to(target)
    monkeypatch.setenv('MLX_PYTHON', str(interpreter))
    assert inference.mlx_paths()[2] == interpreter
    assert inference.mlx_paths()[2] != target
