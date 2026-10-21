"""Offline checks used before model download or training."""
import hashlib
import json
from pathlib import Path


def data_manifest():
    evaluation_questions = {json.loads(line)['question'].strip().lower()
                            for line in Path('evaluation/questions.jsonl').read_text().splitlines()}
    result = {}
    seen = set()
    for split in ('train', 'valid'):
        path = Path('training/data') / f'{split}.jsonl'
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        assert rows, f'Empty {split} split'
        for row in rows:
            messages = row['messages']
            assert [m['role'] for m in messages] == ['system', 'user', 'assistant']
            assert all(isinstance(m['content'], str) and m['content'].strip() for m in messages)
            question = messages[1]['content'].strip().lower()
            assert question not in evaluation_questions, 'Evaluation question leaked into training'
            assert question not in seen, 'Duplicate train/validation question'
            seen.add(question)
            answer = messages[2]['content']
            assert answer.startswith('Answer: ') and '\nSources: ' in answer
            assert len(answer.splitlines()) == 2
        result[split] = {'rows': len(rows), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    return result


if __name__ == '__main__':
    print(json.dumps(data_manifest(), indent=2))
