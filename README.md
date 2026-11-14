# Local RAG System

A fully local Retrieval-Augmented Generation chatbot that answers questions about
PDF and text documents, built for the CS311 Advanced Deep Learning final project.
Everything (embeddings, vector search, and the LLM) runs on your own machine via
[Ollama](https://ollama.com) and [Chroma](https://www.trychroma.com).

The main knowledge source is the **Fulbright Computer Science Major Handbook**
(`source_code/data/handbooks/CS_MajorHandbook.pdf`).

```
Documents (PDF/TXT) ─► chunk ─► embed (nomic-embed-text) ─► Chroma
                                                              │ top-k
Question ──────────────────────────────► embed ─► search ─────┘
                                                              ▼
                                       prompt(context + question) ─► LLM (qwen2.5) ─► answer + cited pages
```

## Project status

| Task | Description | Status |
|------|-------------|--------|
| 1 | PDF file support | ✅ done |
| 2 | CS handbook chatbot + evaluation | ⏳ |
| 3 | Docker deployment | ⏳ |
| 4 | Web UI (Streamlit) | ⏳ |
| 5 | Report | ⏳ |
| 6 | Video demos | ⏳ |
| 7 | GitHub + README | ⏳ |

## Repository layout

```
source_code/        all application code and data
  rag/              pipeline package: config, loaders (txt/pdf), store, pipeline
  run.py            command-line Q&A
  run_txt.py        original course baseline (unchanged, for reference)
  data/sample_txt/  FUV sample text corpus
  data/handbooks/   CS major handbook PDF
docker/             Dockerfile and compose configuration
report/             final report (PDF)
demo_video/         demo videos (or links to them)
```

## Quick start

### 1. Ollama and models

```bash
# install: https://ollama.com/download, then
ollama serve                  # if not already running as a service
ollama pull nomic-embed-text  # embedding model
ollama pull qwen2.5:1.5b      # answer model (also try qwen2.5:0.5b / qwen2.5:3b)
```

### 2. Python environment

With [uv](https://docs.astral.sh/uv/) (recommended):

```bash
cd source_code
uv sync
```

Or with pip/conda (Python 3.10–3.12):

```bash
cd source_code
conda create -n rag python=3.11 && conda activate rag
pip install -r requirements.txt
```

### 3. Ask questions

```bash
cd source_code
# CS handbook (first run builds the index)
uv run python run.py --data-dir data/handbooks --model qwen2.5:1.5b \
    -q "What courses are required for the Computer Science major?"

# FUV sample text corpus (default)
uv run python run.py -q "Where is the FUV campus?"

# force re-indexing after changing documents or chunk settings
uv run python run.py --data-dir data/handbooks --rebuild
```

Configuration (models, chunk size, top-k, Ollama URL) can be set via environment
variables or a `.env` file; see `source_code/.env.example`.

## Known limitations

- Text inside images or scanned pages is not extracted (no OCR); page 10 of the CS
  handbook is image-only and is skipped during indexing.
- Small models (e.g. `qwen2.5:0.5b`) can contradict the retrieved context or mix
  up related sections (e.g. major vs. minor requirements).
