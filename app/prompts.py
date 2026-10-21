"""Shared response contract for the formatting experiment."""
ABSTENTION = 'Not found in the provided manual.'
FORMAT = 'Respond with two lines: Answer: <answer> and Sources: <citation labels or none>.'


def messages_for(question, hits, use_rag):
    context = '\n'.join(f"[{i}] {x['source']} / {x['section']}: {x['text']}"
                        for i, x in enumerate(hits, 1))
    system = (
        'This is a fictional educational simulation. Use ONLY the manual excerpts below. '
        'Cite supporting excerpts with their numeric labels, such as [1]. '
        f'If the excerpts do not answer the question, say: {ABSTENTION} '
        f'{FORMAT}\n{context}'
    ) if use_rag else (
        'This is a fictional educational simulation. You have no Odyssey-7 manual. '
        'Admit uncertainty about ship-specific facts. Do not provide real-world emergency guidance. '
        + FORMAT
    )
    return [{'role': 'system', 'content': system}, {'role': 'user', 'content': question}]
