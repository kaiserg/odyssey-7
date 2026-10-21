# Odyssey-7 — Tasks and acceptance criteria

## Phase 1: Cockpit MVP (included)
- [x] Responsive spacecraft-inspired frontend with central chat display
- [x] Original fictional ship manuals
- [x] FastAPI + local Ollama integration
- [x] Base vs RAG switch; retrieved source panel
- [x] TF-IDF lexical retrieval baseline
- [x] Run HTTP end-to-end on Mac M5 Pro (2026-10-20; browser acceptance pending below)

## Phase 2: Semantic vector RAG
- [ ] Add local embedding model and FAISS/Chroma vector store
- [ ] Chunk documents by section with metadata
- [ ] Evaluate retrieval recall@k, citations and abstention
- [ ] Make sources clickable with document excerpts

## Phase 3: Fine-tuning with LoRA
- [ ] Validate MLX-LM and compatible Qwen model on Apple Silicon
- [ ] Create small train/validation JSONL for consistent response FORMAT
- [ ] Train LoRA adapter and compare before/after
- [ ] Enable Fine-tuned + RAG UI mode only when genuinely functional

## Phase 4: Portfolio polish
- [ ] Architecture SVG/Mermaid diagrams and UI screenshots
- [ ] Automated tests, evaluation metrics and reproducible demo
- [ ] Explain RAG vs fine-tuning, limitations, setup, measured results

**Scope guard:** no large corpus, no enterprise platform, no general chatbot training. Prioritize tutorial quality.

## Audit checkpoint — 2026-10-20

Inspected all tracked project source, frontend assets, manuals, documentation and
tests. Phase 1 validation adds input checks, serial chat requests, inference failure
coverage, thinking-prefix filtering, and deterministic abstention for zero retrieval
matches. Full dependency snapshot: `requirements.lock.txt`. Offline suite: 15 passing
tests, with one upstream Starlette/httpx deprecation warning. Local HTTP smoke evidence:
`phase1-smoke.json` (M5 Pro, 48 GB, qwen3:4b). Port 8000 already had a server;
the updated application was tested separately on 8001.

Browser automation was unavailable, so visual/manual browser acceptance remains
unchecked below. No cockpit reference image was supplied or found. The existing
responsive layout has been inspected in source, not visually certified.

- [ ] Verify browser chat interactions and responsive layout on the Mac

Next phase is semantic vector retrieval, section metadata, a small fixed evaluation
set, citation/abstention checks and clickable excerpts. No embeddings download,
training, adapter or comparison metrics are claimed by this checkpoint.
