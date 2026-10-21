"""Create tiny synthetic format examples, independent of manuals and evaluation."""
import json
from pathlib import Path

from app.prompts import FORMAT


def examples(start, count):
    rows = []
    for i in range(start, start + count):
        unit = f'Training beacon Z{i:02d}'
        if i % 4 == 0:
            question = f'What is the service interval for {unit}?'
            excerpt = f'[1] {unit} has a violet status lamp.'
            answer = 'Answer: Not found in the provided manual.\nSources: none'
        else:
            command = ['SCAN', 'HOLD', 'CHECK'][i % 3]
            question = f'Which command enables {unit}?'
            label = 1 + i % 2
            excerpt = f'[{label}] To enable {unit}, select {command}-{i:02d}.'
            answer = f'Answer: Select {command}-{i:02d}.\nSources: [{label}]'
        system = ('This is a fictional educational simulation. Use ONLY the manual excerpts below. '
                  'Cite supporting excerpts with their numeric labels, such as [1]. '
                  'If the excerpts do not answer the question, say: Not found in the provided manual. '
                  + FORMAT + '\n' + excerpt)
        rows.append({'messages': [{'role': 'system', 'content': system},
                                  {'role': 'user', 'content': question},
                                  {'role': 'assistant', 'content': answer}]})
    return rows


def prepare(directory=Path('training/data')):
    directory.mkdir(parents=True, exist_ok=True)
    for split, start, count in [('train', 1, 24), ('valid', 101, 8)]:
        rows = examples(start, count)
        (directory / f'{split}.jsonl').write_text(''.join(json.dumps(row) + '\n' for row in rows))


if __name__ == '__main__':
    prepare()
    print('Wrote 24 training and 8 validation examples. No manuals/evaluation data read.')
