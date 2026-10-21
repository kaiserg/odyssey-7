"""Run from the repository root: python -m scripts.evaluate [--generate]."""
import argparse
import asyncio
import hashlib
import json
import os
import platform
import re
from datetime import datetime, timezone
from pathlib import Path

from app.main import ABSTENTION, Ask, ask, chunks, retriever
from app.inference import adapter_ready, digest, mlx_paths
from app.prompts import messages_for


def answer_metrics(answer, sources, case):
    labels = [int(x) for x in re.findall(r'\[(\d+)\]', answer)]
    valid = [x for x in labels if 1 <= x <= len(sources)]
    expected = set(case['expected_sources'])
    return {
        'abstained': ABSTENTION.lower() in answer.lower(),
        'format_compliant': bool(re.fullmatch(r'Answer: [^\n]+\nSources: (?:none|\[\d+\](?:[ ,]*\[\d+\])*)\s*', answer.strip())),
        'citation_labels': labels,
        'invalid_citation_count': len(labels) - len(valid),
        'cites_expected_section': any(sources[x - 1]['id'] in expected for x in valid),
        'expected_term_coverage': (sum(term.lower() in answer.lower() for term in case['expected_terms'])
                                   / len(case['expected_terms'])) if case['expected_terms'] else None,
    }


def model_manifest():
    path = Path('training/model.json')
    if os.getenv('CHAT_BACKEND') != 'mlx' or not path.is_file():
        return None
    manifest = json.loads(path.read_text())
    return manifest if Path(manifest['local_path']).resolve() == mlx_paths()[0] else None


async def evaluate(args):
    cases = [json.loads(line) for line in Path('evaluation/questions.jsonl').read_text().splitlines()]
    os.environ['RAG_RETRIEVER'] = args.backend
    modes = ('base', 'rag', 'finetuned') if args.include_finetuned else ('base', 'rag')
    rows = []
    for case in cases:
        hits = await retriever.search(case['question'], args.backend, threshold=args.threshold)
        expected = set(case['expected_sources'])
        found = {h['id'] for h in hits}
        row = {**case, 'retrieved': [{'id': h['id'], 'score': h['score']} for h in hits],
               'recall_at_3': len(expected & found) / len(expected) if expected else None,
               'retrieval_abstained': not hits}
        if args.generate:
            # The API uses the same configured threshold as the retrieval report.
            if args.threshold is not None:
                os.environ['RAG_MIN_SCORE'] = str(args.threshold)
            row['answers'] = {}
            for mode in modes:
                result = await ask(Ask(question=case['question'], mode=mode))
                row['answers'][mode] = {**result, **answer_metrics(result['answer'], result['sources'], case)}
        if args.generate and args.include_finetuned:
            assert messages_for(case['question'], row['answers']['rag']['sources'], True) == messages_for(case['question'], row['answers']['finetuned']['sources'], True), 'RAG prompts differ'
        rows.append(row)
        print(case['id'], row['recall_at_3'], 'no hits' if not hits else hits[0]['id'], flush=True)
    supported = [r for r in rows if r['expected_sources']]
    unsupported = [r for r in rows if not r['expected_sources']]
    report = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'platform': platform.platform(),
        'python': platform.python_version(), 'backend': args.backend,
        'embedding_model': os.getenv('EMBEDDING_MODEL', 'qwen3-embedding:4b'),
        'chat_backend': os.getenv('CHAT_BACKEND', 'ollama'),
        'chat_model': str(mlx_paths()[0]) if os.getenv('CHAT_BACKEND') == 'mlx' else os.getenv('OLLAMA_MODEL', 'qwen3:4b'),
        'generation_options': {'temperature': 0, 'seed': 7, 'max_tokens': 256} if os.getenv('CHAT_BACKEND') == 'mlx' else {'temperature': 0.2, 'seed': 7},
        'model_manifest': model_manifest(),
        'model_config_sha256': digest(mlx_paths()[0] / 'config.json') if os.getenv('CHAT_BACKEND') == 'mlx' else None,
        'adapter_sha256': digest(mlx_paths()[1] / 'adapters.safetensors') if args.include_finetuned else None,
        'min_score': args.threshold if args.threshold is not None else (float(os.getenv('RAG_MIN_SCORE', '0.55')) if args.backend == 'vector' else 0),
        'dataset_sha256': hashlib.sha256(Path('evaluation/questions.jsonl').read_bytes()).hexdigest(),
        'corpus_sha256': {c['source']: c['sha256'] for c in chunks},
        'summary': {
            'supported_questions': len(supported), 'unsupported_questions': len(unsupported),
            'mean_recall_at_3': sum(r['recall_at_3'] for r in supported) / len(supported),
            'unsupported_retrieval_abstention_rate': sum(r['retrieval_abstained'] for r in unsupported) / len(unsupported),
        }, 'results': rows,
    }
    if args.generate:
        for mode in modes:
            report['summary'][mode] = {
                'supported_format_compliance_rate': sum(r['answers'][mode]['format_compliant'] for r in supported) / len(supported),
                'unsupported_answer_abstention_rate': sum(r['answers'][mode]['abstained'] for r in unsupported) / len(unsupported),
                'supported_expected_term_coverage': sum(r['answers'][mode]['expected_term_coverage'] for r in supported) / len(supported),
                'supported_citation_to_expected_section_rate': sum(r['answers'][mode]['cites_expected_section'] for r in supported) / len(supported),
                'invalid_citation_count': sum(r['answers'][mode]['invalid_citation_count'] for r in rows),
            }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=['tfidf', 'vector'], default='vector')
    parser.add_argument('--threshold', type=float)
    parser.add_argument('--generate', action='store_true', help='Also call local chat model in Base and RAG modes')
    parser.add_argument('--include-finetuned', action='store_true', help='Compare all three modes using the same MLX base model')
    parser.add_argument('--output', default='runs/evaluation.json')
    args = parser.parse_args()
    if args.include_finetuned and (not args.generate or not adapter_ready()):
        parser.error('--include-finetuned requires --generate, CHAT_BACKEND=mlx and a validated adapter')
    if args.backend == 'tfidf' and args.threshold is not None:
        parser.error('--threshold is for vector retrieval; TF-IDF uses positive lexical scores')
    asyncio.run(evaluate(args))
