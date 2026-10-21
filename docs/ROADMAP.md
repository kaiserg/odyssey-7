# Odyssey-7 — Tasks and acceptance criteria

## Phase 1: Cockpit MVP (included)
- [x] Responsive spacecraft-inspired frontend with central chat display
- [x] Original fictional ship manuals
- [x] FastAPI + local Ollama integration
- [x] Base vs RAG switch; retrieved source panel
- [x] TF-IDF lexical retrieval baseline
- [ ] Run end-to-end on Mac M5 Pro

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
