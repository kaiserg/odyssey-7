"""Download a small pinned MLX conversion; never execute remote model code."""
import json
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download

REPO = 'mlx-community/Qwen3-0.6B-4bit'
MANIFEST = Path('training/model.json')

if __name__ == '__main__':
    revision = json.loads(MANIFEST.read_text())['revision'] if MANIFEST.exists() else HfApi().model_info(REPO).sha
    destination = Path('.models/qwen3-0.6b-4bit')
    MANIFEST.write_text(json.dumps({'repo': REPO, 'revision': revision,
                                    'local_path': str(destination), 'license': 'Apache-2.0'}, indent=2) + '\n')
    snapshot_download(REPO, revision=revision, local_dir=destination,
                      allow_patterns=['*.json', '*.safetensors', '*.jinja', 'merges.txt', '*.model'])
    print(MANIFEST.read_text())
