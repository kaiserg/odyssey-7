# Odyssey-7 — Tasks and acceptance criteria

**Language / Idioma:** English · [Español](es/ROADMAP.md)

## Phase 1: Cockpit MVP

- [x] Responsive spacecraft-inspired frontend with central chat display
- [x] Original fictional ship manuals
- [x] FastAPI + local Ollama integration
- [x] Base vs RAG switch; retrieved source panel
- [x] TF-IDF lexical retrieval baseline
- [x] Run HTTP end-to-end on Mac M5 Pro (2026-10-20)
- [x] Verify browser chat interactions and responsive layout on the Mac

Phase 1 is committed as `cbafc26`. The real HTTP smoke record is
`docs/phase1-smoke.json`; it predates semantic retrieval. Early validation covered HTTP only. Phase 4 subsequently used native Chrome control
for real chat, sources, mode switching, mobile layout and outage checks. The local
cockpit concept was found in Downloads during screenshot capture and used to guide
frame/amber-trim refinement; it was not copied into the repository.

## Phase 2: Semantic vector RAG

- [x] Add local embedding model and FAISS vector store
- [x] Chunk documents by section with metadata
- [x] Evaluate retrieval recall@k, citations and abstention
- [x] Make sources clickable with document excerpts

The implementation uses the already installed `qwen3-embedding:4b` through Ollama,
normalized vectors and FAISS exact inner-product search in RAM. Six section chunks
retain stable IDs, original lines, full-document hashes and excerpt URLs. Restart
after editing manuals. TF-IDF remains an explicit baseline, with no silent fallback.

The fixed evaluation dataset contains six answerable and four unsupported questions.
Recorded retrieval recall@3 is 1.0 for both methods. Unsupported retrieval abstention
is 0.75 for vectors at the initial 0.55 threshold and 0.25 for TF-IDF. These are tiny
fixture measurements, not general accuracy results or held-out threshold calibration.
A related scrubber excerpt is retrieved for an unsupported replacement interval.

Validation: 24 offline tests pass (one upstream Starlette/httpx deprecation warning),
installed dependencies are compatible, JavaScript syntax passes, and live HTTP checks
cover static routes, configuration, all six excerpt links and vector no-hit abstention.
The completed twenty-request Base/RAG run is saved in `evaluation/base-rag.json`.
RAG matched all expected terms and cited an expected section on all six supported
questions; all four unsupported answers used the canonical abstention. BASE often
acknowledged uncertainty but also invented procedures or values. Its zero score on
the canonical-phrase abstention metric does not mean it never expressed uncertainty.
Citation checks are label/section heuristics, not claim-level factuality verification.
See `evaluation/README.md` for commands and metric limitations.

Phase 2 is complete at the API and local inference level. Browser acceptance was completed in Phase 4. Phase 3 below records the subsequent MLX pipeline validation and bounded training.

## Phase 3: Fine-tuning with LoRA

- [x] Validate MLX-LM and compatible Qwen model on Apple Silicon
- [x] Create small train/validation JSONL for consistent response FORMAT
- [x] Train LoRA adapter and compare before/after
- [x] Enable Fine-tuned + RAG UI mode only when genuinely functional

Completed on the M5 Pro with MLX 0.32.4 and MLX-LM 0.32.2 in a separate optional
environment. Pinned `mlx-community/Qwen3-0.6B-4bit` revision is recorded in
`training/model.json`. Preflight checked the actual masked-prompt data path, maximum
127 tokens, Metal access, finite logits and generation before any weight update.
A one-step adapter train/reload smoke passed before the bounded 40-step run.

The run used 24 synthetic format examples and eight separate validation examples,
rank 4 on four layers, about 0.360M trainable parameters (0.060% of the base).
The manuals and ten evaluation questions were not used for training. Model weights,
caches and the approximately 1.4 MB adapter remain ignored local artifacts;
small configs, data, logs and measured reports are tracked.

`evaluation/mlx-three-way.json` compares all three modes on the same small MLX base.
Both RAG variants receive identical model messages. Strict supported-answer format
compliance was 1/6 without the adapter and 5/6 with it. Both cited expected sections
on 6/6 and canonically abstained on 4/4 unsupported questions; three of those
abstentions happen before model generation. Both still gave the wrong nominal
oxygen pressure, and the adapted navigation answer omitted reset steps. This is a
formatting demonstration, not a general accuracy improvement.

The API enables fine-tuned mode only with `CHAT_BACKEND=mlx` and a successfully
validated compatible local adapter. A real HTTP check exercised all three modes;
32 offline tests pass, and both environment dependency checks pass. The worker
preserves its virtual-environment interpreter path, stays offline and has bounded
generation/timeout cleanup. Browser visual acceptance was subsequently completed in Phase 4.

See `docs/FINETUNING.md`, `training/preflight.json`, `training/smoke.json`,
`training/training.log`, `training/adapter-validation.json` and
`training/http-smoke.json` for reproduction and evidence. No larger training run
or evaluation-driven hyperparameter sweep was performed.

## Phase 4: Portfolio polish

- [x] Architecture Mermaid diagrams and reproducible tutorial commands
- [x] UI screenshots and reference-based cockpit refinement
- [x] Automated API/retrieval tests and reproducible evaluation runner
- [x] Complete three-way comparison with measured results
- [x] Explain RAG vs fine-tuning, limitations and local setup

Phase 4 adds an orbital viewport, original SVG vessel schematic, instrument panels,
mode explanations, responsive layouts, accessible control labels/focus states and
source snapshots for each response. No new frontend framework, external fonts,
training or model changes were needed. Configuration labels avoid fabricated health
or telemetry claims. A shorter-desktop footer overlap was caught and fixed visually.

Real desktop and mobile captures are in `docs/screenshots/`. Native Chrome checks
exercise Base/RAG/fine-tuned generation, captain abstention, excerpt expansion,
document hash links, old-answer evidence restoration, mobile transmission, missing
adapter gating and deliberate service outages with recovery. Tests remain 32 passing;
JavaScript syntax and diff checks pass. See `docs/BROWSER_VALIDATION.md` and
`docs/DEMO.md` for evidence, reproduction and a reviewer walkthrough.

The four planned demonstration phases are complete. Remaining optional work includes
Safari/Firefox and physical-device checks, a formal accessibility audit, and a larger
independent evaluation set with semantic factuality review. The current tiny model
still makes documented factual errors; no broader accuracy claim is made.

**Scope guard:** no large corpus, no enterprise platform, no general chatbot
training. Prioritize a working educational demonstration and honest evidence.

## Bilingual explanatory documentation

The [Spanish learning path](es/README.md) covers setup, RAG, MLX LoRA, evaluation,
a demo walkthrough, browser-validation evidence and a bilingual glossary. Paired
language links connect it to the English guides. This is documentation only:
application code, UI, manuals, datasets and measured reports remain unchanged.
No Spanish-language model evaluation or additional training is claimed.
