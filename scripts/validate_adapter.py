"""Load the saved adapter and mark it available only after real local generation."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.mlx_generate import generate_reply
from app.model_identity import weight_stamp


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, default=Path('.models/qwen3-0.6b-4bit'))
    parser.add_argument('--adapter', type=Path, default=Path('adapters/odyssey-format'))
    args = parser.parse_args()
    config = json.loads((args.adapter / 'adapter_config.json').read_text())
    assert Path(config['model']).resolve() == args.model.resolve(), 'Adapter base model mismatch'
    row = json.loads(Path('training/data/valid.jsonl').read_text().splitlines()[0])
    answer = generate_reply(args.model, row['messages'][:-1], args.adapter)
    report = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'model_path': str(args.model.resolve()),
        'model_config_sha256': sha(args.model / 'config.json'),
        'model_weights': weight_stamp(args.model),
        'adapter_sha256': sha(args.adapter / 'adapters.safetensors'),
        'adapter_config_sha256': sha(args.adapter / 'adapter_config.json'),
        'smoke_answer': answer,
    }
    (args.adapter / 'ready.json').write_text(json.dumps(report, indent=2) + '\n')
    # Small tracked evidence; weights and local paths stay in ignored directories.
    Path('training/adapter-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
