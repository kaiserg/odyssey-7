# Small reproducible evaluation

**Language / Idioma:** English · [Español](../docs/es/EVALUACION.md)

`questions.jsonl` contains six answerable questions (one per manual section) and
four unsupported questions. Each has a stable ID, expected chunk IDs and simple
expected answer terms. The corpus is deliberately tiny; this is a demonstration
fixture rather than a representative benchmark. Do not train on these questions.

Run from the repository root with the virtual environment active:

```bash
python -m scripts.evaluate --backend tfidf --output runs/tfidf.json
python -m scripts.evaluate --output runs/vector.json
python -m scripts.evaluate --generate --output runs/base-rag.json
```

Vector evaluation needs Ollama and `qwen3-embedding:4b`. Generation additionally
needs `qwen3:4b` and makes twenty chat requests. No GPU training is involved.
The JSON reports retain raw answers, ranked section IDs/scores, thresholds, model
names, timestamp, Python/platform information, corpus hashes and dataset hash.

Metrics:

- **Recall@3:** fraction of the expected sections appearing among up to three
  retrieved hits, averaged over the six supported questions. Thresholded hits can
  be fewer than three. Unsupported questions are excluded from recall.
- **Unsupported retrieval abstention:** fraction of the four unsupported questions
  with zero hits. This is distinct from answer abstention: the LLM can abstain even
  when it receives related excerpts.
- **Answer abstention:** presence of the app's canonical “Not found in the provided
  manual.” phrase. Other honest uncertainty phrasing can be missed by this metric.
- **Expected-term coverage:** case-insensitive substring matches averaged per
  supported question. Spelled-out numbers and numeric equivalents may score
  differently. This is not a factuality or semantic correctness judge.
- **Citation to expected section:** at least one numeric citation maps to an
  expected retrieved section. Also count labels outside the supplied source range.
  These checks do not establish claim-level support or detect uncited inventions.

Recorded retrieval run on the M5 Pro / 48 GB, 2026-10-20:

| Retriever | Recall@3, six supported | No-hit rate, four unsupported |
| --- | --- | --- |
| TF-IDF | 1.0 | 0.25 |
| Qwen embeddings + FAISS, threshold 0.55 | 1.0 | 0.75 |

See `tfidf-retrieval.json` and `vector-retrieval.json`. The vector retriever still
returns a routine-check section for the unsupported scrubber replacement interval.
This illustrates why semantic similarity cannot guarantee answerability.
The threshold is an initial demonstration setting; no held-out calibration or
statistical significance is claimed. Model updates and floating-point differences
can change outputs. Review raw responses alongside every metric. The separate MLX comparison below uses a validated pipeline and a smaller base model.

## Recorded answer comparison

`base-rag.json` contains all twenty local chat results using `qwen3:4b`, with the
same questions in each mode (temperature 0.2, seed 7, thinking disabled). For RAG,
expected-term coverage and citation-to-expected-section rate were both 1.0 across
six supported questions, with zero out-of-range citation labels. All four unsupported
questions received the canonical abstention, including the scrubber interval question
that retrieved a related excerpt.

BASE's expected-term coverage was approximately 0.067 and it had no source citations.
Its exact-phrase abstention metric is 0.0, but manual inspection shows uncertainty
on the captain, password, scrubber interval and live fuel questions. Do not interpret
that metric as zero honest uncertainty. BASE also supplied invented nominal pressures,
reset codes and thruster procedures in some supported-question responses. The saved
raw outputs include unsupported real-world claims; they are model artifacts to
inspect, not instructional material. No claim-level factuality score is reported.

## MLX three-way formatting experiment

`mlx-three-way.json` records the same ten questions using the pinned Qwen3 0.6B
4-bit MLX model in every mode. Both RAG modes receive identical model messages.
Only Fine-tuned + RAG loads the 40-step rank-4 adapter. All modes receive the same
two-line formatting instruction, use greedy sampling, seed 7 and a 256-token limit.
Commands and training evidence are in [the MLX tutorial](../docs/FINETUNING.md).

| Metric | Base | RAG | Fine-tuned + RAG |
| --- | --- | --- | --- |
| Strict format, six supported | 0/6 | 1/6 | 5/6 |
| Mean expected-term coverage | 0.000 | 0.500 | 0.533 |
| Cites expected section, six supported | 0/6 | 6/6 | 6/6 |
| Canonical abstention, four unsupported | 0/4 | 4/4 | 4/4 |
| Out-of-range numeric citation labels | 2 | 0 | 0 |

The formatting result is useful but narrow. Manual review of the raw answers shows:

- Both RAG variants gave **19.0 kPa** as nominal oxygen pressure, where the expected
  routine-check value is **21.0 kPa**. Merely citing the right section did not prevent
  mixing facts from adjacent excerpts.
- Adapted navigation answered the docking prohibition but **omitted the reset
  sequence**, which unadapted RAG had provided. Better formatting can lose content.
- The adapted route answer supplied the correct two confirmations; unadapted RAG
  only named the source file for that question.
- Both RAG variants correctly answered the power question with “15 percent,” but
  the fixture expects “fifteen,” so substring coverage scores that answer as zero.
  The metric was kept unchanged rather than revised after seeing the outputs.
- BASE expressed uncertainty on several unsupported questions without using the
  canonical phrase; its 0/4 metric is not a measure of all honest uncertainty.
- Three unsupported questions had no retrieval hits, so their RAG abstentions were
  application rules rather than evidence of adapter learning. The scrubber question
  did reach both models and both abstained.

This is one small, fixed demonstration set, not a claim of statistical significance
or broad generalization. The synthetic validation loss fell from 3.020 to 0.001;
near-template training/validation examples make that an easy task, not proof of
better document Q&A. No further training was selected using these evaluation
answers. Earlier Ollama Qwen3 4B results are a separate experiment with different
weights, runtime, prompts and sampling, and cannot establish an adapter effect.
