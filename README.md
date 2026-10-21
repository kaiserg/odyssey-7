# Odyssey-7 — RAG & Fine-Tuning Lab 🚀

A visual, local-first educational project comparing **Base LLM vs RAG**, with **LoRA fine-tuning planned**. The UI resembles a spaceship cockpit; the center display handles chat inputs and outputs.

**Implemented:** fictional Markdown manuals, responsive cockpit, FastAPI, Ollama inference, lexical TF-IDF retrieval, document section panel. **Not yet implemented:** semantic vector RAG and LoRA fine-tuning.

## Quick start (macOS / VS Code)

Install Python 3.13, uv and Ollama. From the extracted project folder:

```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt
ollama pull qwen3:4b
# Start Ollama if not already running: ollama serve
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and compare **BASE** and **RAG** modes with the oxygen-pressure question. Ollama must be running locally; otherwise the UI reports an explicit error. No cloud API key is required.

See [step-by-step tutorial](docs/TUTORIAL.md) and [task roadmap](docs/ROADMAP.md).

**Educational simulation only:** spaceship procedures are fictional, not real safety instructions.
