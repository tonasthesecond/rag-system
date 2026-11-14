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
| 2 | CS handbook chatbot + evaluation | 🔄 evaluation running |
| 3 | Docker deployment | ✅ done |
| 4 | Web UI (Streamlit) | ✅ done |
| 5 | Report | ⏳ |
| 6 | Video demos | ⏳ |
| 7 | GitHub + README | ⏳ |

## Repository layout

```
source_code/        all application code and data
  rag/              pipeline package: config, loaders (txt/pdf), store, pipeline
  app.py            Streamlit web UI
  run.py            command-line Q&A
  evaluate.py       runs the handbook test set against several models
  eval/             test questions (questions.yaml) and results
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

### 4. Web interface

```bash
cd source_code
uv run streamlit run app.py      # http://localhost:8501
```

Chat with conversation history, streamed answers and a sources panel with the
cited handbook pages. The sidebar switches the document collection and answer
model, tunes top-k / temperature, uploads new PDFs and rebuilds the index.

### 5. Evaluate (Task 2)

```bash
cd source_code
uv run python evaluate.py --models qwen2.5:0.5b qwen2.5:1.5b qwen2.5:3b
```

Writes `eval/results/<timestamp>/{summary.md,results.csv,results.json}` with each
model's answers, retrieved pages, retrieval hit rate, key-fact coverage and latency.

Configuration (models, chunk size, top-k, Ollama URL) can be set via environment
variables or a `.env` file; see `source_code/.env.example`.

## Docker deployment (Task 3)

The compose stack runs Ollama and the app in two containers; a one-shot
`ollama-init` service downloads the models on first start.

```bash
# Docker
docker compose -f docker/docker-compose.yml up --build -d
# Podman (pip/uv install podman-compose first)
podman compose -f docker/docker-compose.yml up --build -d

# open http://localhost:8501
docker compose -f docker/docker-compose.yml logs -f app     # follow logs
docker compose -f docker/docker-compose.yml down            # stop (volumes kept)
```

- Use a different answer model: `LLM_MODEL=qwen2.5:3b MODELS="nomic-embed-text qwen2.5:3b" docker compose ... up`
  (or pick any pulled model in the UI sidebar).
- Documents are bind-mounted from `source_code/data`, so new PDFs don't need a rebuild;
  the Chroma index persists in the `vector-store` volume.
- Run the CLI inside the container:
  `docker compose -f docker/docker-compose.yml exec app python run.py -q "..."`
- Podman's default OCI image format ignores `HEALTHCHECK`; build with
  `podman build --format docker ...` if you want it.

## Known limitations

- Text inside images or scanned pages is not extracted (no OCR); page 10 of the CS
  handbook is image-only and is skipped during indexing.
- Small models (e.g. `qwen2.5:0.5b`) can contradict the retrieved context or mix
  up related sections (e.g. major vs. minor requirements).
