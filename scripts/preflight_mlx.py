"""Validate config, data, tokenizer, Metal forward pass and base generation. No training."""
import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from scripts.validate_training import data_manifest


def main():
    import mlx.core as mx
    import yaml
    from mlx_lm import load
    from mlx_lm.tuner.datasets import ChatDataset
    from scripts.mlx_generate import generate_reply

    config_path = Path('training/lora.yaml')
    config = yaml.safe_load(config_path.read_text())
    assert config['fine_tune_type'] == 'lora'
    assert 1 <= config['iters'] <= 40
    assert config['batch_size'] == 1 and config['num_layers'] <= 4
    assert config['lora_parameters']['rank'] <= 4
    assert config['max_seq_length'] <= 384 and config['mask_prompt'] is True
    assert config['learning_rate'] <= 0.0001
    manifest = json.loads(Path('training/model.json').read_text())
    assert config['model'] == manifest['local_path']
    assert mx.metal.is_available(), 'Metal GPU is unavailable'
    model, tokenizer = load(config['model'], tokenizer_config={'trust_remote_code': False})
    rows = []
    lengths = {}
    for split in ('train', 'valid'):
        samples = [json.loads(line) for line in (Path(config['data']) / f'{split}.jsonl').read_text().splitlines()]
        dataset = ChatDataset(samples, tokenizer, mask_prompt=True)
        processed = [dataset.process(row) for row in samples]
        assert all(0 < offset < len(tokens) - 1 for tokens, offset in processed), 'No completion tokens after prompt masking'
        tokens = [tokens for tokens, offset in processed]
        assert max(map(len, tokens)) <= config['max_seq_length'], 'Training would truncate an example'
        lengths[split] = {'max_tokens': max(map(len, tokens)), 'min_tokens': min(map(len, tokens))}
        rows.extend(samples)
    tokens = tokenizer.apply_chat_template(rows[0]['messages'][:-1], tokenize=True, add_generation_prompt=True, enable_thinking=False)
    logits = model(mx.array([tokens]))
    mx.eval(logits)
    assert bool(mx.all(mx.isfinite(logits)).item()), 'Forward pass produced non-finite logits'
    del model, logits
    answer = generate_reply(config['model'], rows[-1]['messages'][:-1])
    report = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'platform': platform.platform(),
        'python': platform.python_version(), 'mlx': importlib.metadata.version('mlx'),
        'mlx_lm': importlib.metadata.version('mlx-lm'), 'model': manifest,
        'config_sha256': hashlib.sha256(config_path.read_bytes()).hexdigest(),
        'data': data_manifest(), 'token_lengths': lengths, 'metal_available': True,
        'finite_forward_pass': True, 'base_smoke_answer': answer,
        'training_performed': False,
    }
    Path('training/preflight.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
