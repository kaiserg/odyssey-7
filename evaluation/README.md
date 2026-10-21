# Small reproducible evaluation

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
can change outputs. Review raw responses alongside every metric. A fine-tuned
comparison is deferred until a validated MLX pipeline and adapter exist.

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
