"""One bounded MLX inference call over JSON stdin/stdout, in the optional MLX venv."""
import argparse
import json
import sys
from pathlib import Path


def generate_reply(model_path, messages, adapter_path=None, max_tokens=256):
    import mlx.core as mx
    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_sampler
    mx.random.seed(7)
    model, tokenizer = load(str(model_path), adapter_path=str(adapter_path) if adapter_path else None,
                            tokenizer_config={'trust_remote_code': False})
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                          enable_thinking=False)
    answer = generate(model, tokenizer, prompt=prompt, max_tokens=max_tokens,
                      sampler=make_sampler(temp=0), verbose=False)
    if '</think>' in answer:
        answer = answer.split('</think>', 1)[1].strip()
    if not answer.strip():
        raise ValueError('MLX generated an empty answer')
    return answer.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--adapter', type=Path)
    args = parser.parse_args()
    if not (args.model / 'config.json').is_file():
        parser.error('Expected a downloaded local MLX model')
    messages = json.load(sys.stdin)['messages']
    answer = generate_reply(args.model, messages, args.adapter)
    print(json.dumps({'answer': answer}))
