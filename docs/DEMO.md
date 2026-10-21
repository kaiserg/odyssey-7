# A three-minute Odyssey-7 walkthrough

**Language / Idioma:** English · [Español](es/DEMO.md)

## Prepare once

For the default local Ollama demo, follow the README quick start. For all three
modes, first reproduce and validate the small adapter using [FINETUNING.md](FINETUNING.md).
Then start the app:

```bash
CHAT_BACKEND=mlx .venv/bin/uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. The lab panel shows the configured model and backend;
these are configuration labels, not a promise that inference is reachable. In the
MLX configuration, all three modes use the same Qwen3 0.6B base. A clone without
locally prepared weights and adapter will not enable Fine-tuned + RAG.

## Walk through the experiment

1. **Start without evidence.** Select Base and ask `What do I do when oxygen
   pressure drops?`. Base sees no manual. It may admit uncertainty or invent
   procedures. The evidence panel must remain empty.
2. **Add retrieval.** Select RAG and repeat the exact question. Expand the oxygen
   excerpt in the archive. Follow its link to inspect the file, original line and
   full-document hash. Check the answer against the excerpt rather than trusting
   the citation label alone.
3. **Add the adapter.** Select Fine-tuned + RAG and repeat. Look for the two-line
   `Answer:` / `Sources:` format. Use each answer's **Inspect evidence** button to
   restore its own source list. The new mode should change the model's formatting,
   not the facts available from the manuals.
4. **Ask for an absent fact.** Use `Who is the captain?`. In the retrieval modes,
   no excerpt passes the threshold, so the application abstains without generation.
   This demonstrates an application guard, not a trained-model capability.
5. **Show a harder gap.** Ask `How often must the CO2 scrubber be replaced?`.
   Related text may be retrieved, but it contains no interval. This requires model
   abstention even when context is present.
6. **End with the evidence.** Open [the measured comparison](../evaluation/README.md#mlx-three-way-formatting-experiment).
   The adapter improved strict formatting from 1/6 to 5/6 supported answers, but
   both RAG modes gave the wrong nominal oxygen pressure, and the adapted
   navigation answer omitted reset steps. A better format is not better factuality.

## Explain the engineering choices

- Six Markdown sections make retrieval and source mapping easy to inspect.
- Ollama embeddings and an exact FAISS index keep the retrieval service local and
  avoid a separate database daemon. TF-IDF stays available as a baseline.
- The adapter trains on 24 synthetic format examples, not manual facts or the ten
  evaluation questions. Eight separate synthetic validation examples check the
  narrow training task.
- A separate MLX environment keeps optional GPU dependencies out of the app.
- Preflight and a one-step adapter reload precede the bounded 40-step training run.
- Source IDs, document hashes, model revision, dependency snapshots and raw reports
  make the demonstration inspectable. Exact model text may vary across environments.

## Reproduce the recorded checks

```bash
.venv/bin/python -m pytest -q
uv pip check --python .venv/bin/python
uv pip check --python .venv-mlx/bin/python
CHAT_BACKEND=mlx .venv/bin/python -m scripts.evaluate --generate --include-finetuned --output runs/mlx-three-way.json
```

The ten-question set is a teaching fixture, not a general benchmark. Browser checks
and real screenshots are documented in [BROWSER_VALIDATION.md](BROWSER_VALIDATION.md).
This is a fictional educational simulation; none of its procedures are real safety
instructions.
