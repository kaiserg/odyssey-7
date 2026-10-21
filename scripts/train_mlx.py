"""Bounded training gated on unchanged preflight and a successful one-step smoke."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from scripts.validate_training import data_manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true', help='Run exactly one update and test adapter loading')
    args = parser.parse_args()
    import yaml
    config = yaml.safe_load(Path('training/lora.yaml').read_text())
    preflight = json.loads(Path('training/preflight.json').read_text())
    config_hash = hashlib.sha256(Path('training/lora.yaml').read_bytes()).hexdigest()
    assert preflight['config_sha256'] == config_hash, 'Config changed: rerun preflight'
    assert preflight['data'] == data_manifest(), 'Data changed: rerun preflight'
    assert preflight['model'] == json.loads(Path('training/model.json').read_text()), 'Model changed: rerun preflight'
    assert preflight['finite_forward_pass'] and preflight['metal_available']
    if not args.smoke:
        smoke = json.loads(Path('training/smoke.json').read_text())
        assert smoke['config_sha256'] == config_hash and smoke['data'] == preflight['data']
        assert smoke['model'] == preflight['model'] and smoke['adapter_load_and_generation_passed']
    command = [sys.executable, '-m', 'mlx_lm', 'lora', '--config', 'training/lora.yaml']
    if args.smoke:
        command += ['--iters', '1', '--adapter-path', 'adapters/smoke']
    label = 'smoke' if args.smoke else 'training'
    start = time.monotonic()
    env = {**os.environ, 'HF_HUB_OFFLINE': '1', 'TOKENIZERS_PARALLELISM': 'false', 'NO_COLOR': '1', 'TERM': 'dumb'}
    with Path(f'training/{label}.log').open('w') as log:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env) as process:
            for line in process.stdout:
                clean = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', line)
                print(clean, end='', flush=True)
                log.write(clean)
            if process.wait():
                raise RuntimeError(f'{label} failed; see training/{label}.log')
    report = {'config_sha256': config_hash, 'data': preflight['data'], 'model': preflight['model'],
              'iterations': 1 if args.smoke else config['iters'], 'elapsed_seconds': time.monotonic() - start,
              'command': command}
    if args.smoke:
        from scripts.mlx_generate import generate_reply
        sample = json.loads(Path('training/data/valid.jsonl').read_text().splitlines()[0])
        report['smoke_answer'] = generate_reply('.models/qwen3-0.6b-4bit', sample['messages'][:-1], 'adapters/smoke')
        report['adapter_load_and_generation_passed'] = True
    Path(f'training/{label}.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
