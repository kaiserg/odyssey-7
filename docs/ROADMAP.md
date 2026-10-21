# Odyssey-7 — Tasks and acceptance criteria

## Phase 1: Cockpit MVP

- [x] Responsive spacecraft-inspired frontend with central chat display
- [x] Original fictional ship manuals
- [x] FastAPI + local Ollama integration
- [x] Base vs RAG switch; retrieved source panel
- [x] TF-IDF lexical retrieval baseline
- [x] Run HTTP end-to-end on Mac M5 Pro (2026-10-20)
- [ ] Verify browser chat interactions and responsive layout on the Mac

Phase 1 is committed as `cbafc26`. The real HTTP smoke record is
`docs/phase1-smoke.json`; it predates semantic retrieval. Browser automation was
unavailable and no cockpit reference image was supplied or found. Visual acceptance
remains explicit work, even though static routes and API integration pass.

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

Phase 2 is complete at the API and local inference level. Browser acceptance remains
pending in Phase 1; the next implementation phase is MLX pipeline validation, with
training deferred until the pipeline and configuration pass their own checks.

## Phase 3: Fine-tuning with LoRA

- [ ] Validate MLX-LM and compatible Qwen model on Apple Silicon
- [ ] Create small train/validation JSONL for consistent response FORMAT
- [ ] Train LoRA adapter and compare before/after
- [ ] Enable Fine-tuned + RAG UI mode only when genuinely functional

No training, adapter, MLX inference path or fine-tuned comparison is claimed. Validate
a small pipeline and configuration before any training; keep evaluation questions
out of training data.

## Phase 4: Portfolio polish

- [x] Architecture Mermaid diagrams and reproducible tutorial commands
- [ ] UI screenshots and reference-based cockpit refinement
- [x] Automated API/retrieval tests and reproducible evaluation runner
- [ ] Complete three-way comparison with measured results
- [x] Explain RAG vs fine-tuning, limitations and local setup

**Scope guard:** no large corpus, no enterprise platform, no general chatbot
training. Prioritize a working educational demonstration and honest evidence.
