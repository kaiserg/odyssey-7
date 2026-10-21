"""Optional MLX subprocess keeps GPU dependencies out of the app environment."""
import asyncio
import hashlib
import json
import os
from pathlib import Path

import httpx

from app.model_identity import weight_stamp

ROOT = Path(__file__).resolve().parents[1]


class InferenceError(Exception):
    pass


def local_path(variable, default):
    return (ROOT / os.getenv(variable, default)).resolve()


def mlx_paths():
    return (local_path('MLX_MODEL_PATH', '.models/qwen3-0.6b-4bit'),
            local_path('MLX_ADAPTER_PATH', 'adapters/odyssey-format'),
            # Preserve the interpreter symlink so Python recognizes its virtual environment.
            (ROOT / os.getenv('MLX_PYTHON', '.venv-mlx/bin/python')).absolute())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adapter_ready():
    if os.getenv('CHAT_BACKEND', 'ollama') != 'mlx':
        return False
    model, adapter, python = mlx_paths()
    try:
        manifest = json.loads((adapter / 'ready.json').read_text())
        return (python.is_file() and manifest['model_path'] == str(model)
                and manifest['model_config_sha256'] == digest(model / 'config.json')
                and manifest['model_weights'] == weight_stamp(model)
                and manifest['adapter_sha256'] == digest(adapter / 'adapters.safetensors')
                and manifest['adapter_config_sha256'] == digest(adapter / 'adapter_config.json'))
    except (OSError, ValueError, KeyError, TypeError):
        return False


async def mlx_reply(messages, adapted):
    model, adapter, python = mlx_paths()
    if not python.is_file() or not (model / 'config.json').is_file():
        raise InferenceError('MLX is not configured. Follow docs/FINETUNING.md to prepare the optional environment and model.')
    if adapted and not adapter_ready():
        raise InferenceError('No validated compatible adapter. Run the adapter validation command first.')
    command = [str(python), '-m', 'scripts.mlx_generate', '--model', str(model)]
    if adapted:
        command += ['--adapter', str(adapter)]
    process = None
    try:
        # Local-only: model loading must not trigger a download in the web request.
        env = {**os.environ, 'HF_HUB_OFFLINE': '1', 'TOKENIZERS_PARALLELISM': 'false'}
        process = await asyncio.create_subprocess_exec(
            *command, cwd=ROOT, env=env, stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await asyncio.wait_for(
            process.communicate(json.dumps({'messages': messages}).encode()), timeout=120)
        if process.returncode:
            raise InferenceError('Local MLX inference failed. Verify the model, adapter and Metal access with scripts.validate_adapter.')
        answer = json.loads(stdout)['answer']
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError('Empty answer')
        return answer
    except (OSError, ValueError, KeyError, TypeError, asyncio.TimeoutError) as exc:
        raise InferenceError('Local MLX inference unavailable or timed out. Check the optional environment and model.') from exc
    finally:
        if process is not None and process.returncode is None:
            process.kill()
            await process.wait()


async def reply(messages, adapted=False):
    backend = os.getenv('CHAT_BACKEND', 'ollama')
    if backend == 'mlx':
        return await mlx_reply(messages, adapted)
    if backend != 'ollama' or adapted:
        raise InferenceError('Use CHAT_BACKEND=mlx for the fine-tuned comparison, or ollama for the original demo.')
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/') + '/api/chat',
                json={'model': os.getenv('OLLAMA_MODEL', 'qwen3:4b'), 'stream': False, 'think': False,
                      'messages': messages, 'options': {'temperature': 0.2, 'seed': 7}},
            )
            response.raise_for_status()
            answer = response.json()['message']['content']
            if isinstance(answer, str) and '</think>' in answer:
                answer = answer.split('</think>', 1)[1].strip()
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError('Ollama returned an empty answer')
            return answer
    except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
        raise InferenceError('Ollama unavailable. Start Ollama and pull the configured OLLAMA_MODEL (default qwen3:4b).') from exc
