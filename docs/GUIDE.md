# Operator's guide

Practical how-tos. For *why* things are the way they are, see `DECISIONS.md`;
for *how* they work, see `ARCHITECTURE.md`. All commands assume you start in the
repository root unless they `cd` somewhere.

- [Daily use](#daily-use)
- [Common changes](#common-changes)
- [Evaluation workflow](#evaluation-workflow)
- [Docker / Podman](#docker--podman)
- [Git workflow](#git-workflow)
- [Troubleshooting](#troubleshooting)

---

## Daily use

### Check Ollama is up
```bash
systemctl status ollama          # host service (Fedora package)
ollama list                      # installed models
ollama ps                        # models currently loaded in RAM
curl -s localhost:11434/api/version
```

### Ask one question (CLI)
```bash
cd source_code
uv run python run.py --data-dir data/handbooks --model qwen2.5:1.5b \
    -q "What is the prerequisite for CS311?"
```
`uv run` uses the project's `.venv` automatically; no need to activate it.
If you prefer activating: `source source_code/.venv/bin/activate`, then plain `python run.py ...`.

### Web UI
```bash
cd source_code
uv run streamlit run app.py            # opens http://localhost:8501
```
Stop with Ctrl+C. If 8501 is taken (e.g. the Docker stack is running), add
`--server.port 8502`.

## Common changes

### Add or replace documents
1. Put PDF/TXT files into a folder under `source_code/data/` (an existing one or a
   new one — every subfolder with PDF/TXT files appears in the UI dropdown).
2. Rebuild that folder's index:
   - CLI: `uv run python run.py --data-dir data/<folder> --rebuild -q "..."`
   - UI: sidebar → *Add documents* (upload) or *Rebuild index*.

> The index is **not** refreshed automatically. Forgetting to rebuild means the
> chatbot answers from the old documents.

### Use another handbook
The other 10 handbooks are in the original `final-project.zip`
(`sample_code/major_handbook_pdfs/`). Copy one into a new folder, e.g.
`source_code/data/econ/`, and select it in the UI.

### Try a different answer model
```bash
ollama pull qwen2.5:3b                         # or gemma3:4b, llama3.2:3b, ...
uv run python run.py --model qwen2.5:3b -q "..."
```
In the UI, any installed model shows up in the *Answer model* dropdown.
No rebuild needed — the answer model doesn't touch the index.

### Change the embedding model or chunking
These change the vectors, so the index **must** be rebuilt:
```bash
cd source_code
ollama pull mxbai-embed-large
EMBED_MODEL=mxbai-embed-large CHUNK_SIZE=600 CHUNK_OVERLAP=100 \
    uv run python run.py --data-dir data/handbooks --rebuild -q "..."
```
To make it permanent: `cp .env.example .env` and edit `.env`.
Tip: use a different `VECTOR_STORE=vector_store_mxbai` per experiment so you can
switch back without re-embedding.

### Change the prompt
Edit `PROMPT_TEMPLATE` in `source_code/rag/pipeline.py`. It must keep the
`{context}` and `{question}` placeholders. Applies to CLI, UI and evaluation.
Re-run the evaluation to measure the effect.

### Add a Python dependency
```bash
cd source_code
uv add <package>                                    # updates pyproject.toml + uv.lock
uv export --no-hashes --no-dev --format requirements-txt -o requirements.txt
```
Re-export `requirements.txt` — the Docker image installs from it.

### Lint
```bash
cd source_code && uv run ruff check .
```

## Evaluation workflow

### Run
```bash
cd source_code
uv run python evaluate.py --tag myexperiment                       # 3 default models
uv run python evaluate.py --models qwen2.5:1.5b --tag prompt-v2    # one model
uv run python evaluate.py --models qwen2.5:1.5b --only req-core careers   # a few questions
```
Rough cost on this laptop (CPU): 0.5b ≈ 10 min, 1.5b ≈ 20 min, 3b ≈ 45 min for
all 25 questions. Progress prints as `[n/total]`.

### Resume after an interruption
```bash
uv run python evaluate.py --resume eval/results/<run-folder>      # same --models/--only as before
```

### Label answers
1. Copy `eval/results/20261114-1616-baseline/labels.yaml` into the new run folder
   and edit it (labels: `correct`, `incomplete`, `ambiguous`, `incorrect`).
2. Merge labels into the CSV and summary:
   ```bash
   uv run python evaluate.py --summarize eval/results/<run-folder>
   ```
3. Read `summary.md` (label counts at the top, every answer with its label below).

### Add test questions
Append to `eval/questions.yaml`: `id`, `category`, `question`, `reference`,
`pages` (1-based PDF page numbers that contain the answer; `[]` if none),
`key_facts` (strings the answer must contain; `"a|b"` = either), optional `note`.

## Docker / Podman

Replace `podman compose` with `docker compose` if you use Docker.

```bash
podman compose -f docker/docker-compose.yml up -d --build   # start (first time pulls ~1.3 GB of models)
podman compose -f docker/docker-compose.yml ps              # status
podman compose -f docker/docker-compose.yml logs -f app     # app logs (Ctrl+C to stop following)
podman compose -f docker/docker-compose.yml down            # stop & remove containers (keeps volumes)
podman compose -f docker/docker-compose.yml down -v         # also delete models + index volumes
```

Useful one-offs:
```bash
# Ask a question inside the running app container
podman exec rag-system_app_1 python run.py -q "What GPA is needed for the capstone?"
# Pull an extra model into the containerised Ollama
podman exec rag-system_ollama_1 ollama pull qwen2.5:3b
# Start with a different default model
LLM_MODEL=qwen2.5:3b MODELS="nomic-embed-text qwen2.5:3b" podman compose -f docker/docker-compose.yml up -d
# Rebuild only the app image after code changes
podman compose -f docker/docker-compose.yml up -d --build app
```

On Podman the compose provider is `podman-compose`; it was installed with
`uv tool install podman-compose`.

## Git workflow

- One commit per meaningful step, message = *what* in the subject, *why* in the body.
- `git log --oneline` should read like the project's story; it's graded (Task 7).
- Never commit `vector_store/`, `.venv/`, `.env`, videos, or the course PDFs — the
  `.gitignore` handles this.
- The GitHub remote is not created yet. When it is:
  ```bash
  gh repo create rag-system --public --source . --push     # or --private
  ```

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `httpx.ConnectError` / "Could not reach the model" | Ollama isn't running: `sudo systemctl start ollama` (host) or check the `ollama` container. |
| `model "xyz" not found` | `ollama pull xyz` (or `podman exec rag-system_ollama_1 ollama pull xyz`). |
| Answers ignore newly added documents | Index is stale → `--rebuild` / *Rebuild index*. |
| Error about embedding dimension mismatch | You changed `EMBED_MODEL` without rebuilding. Rebuild, or delete `source_code/vector_store/<folder>`. |
| UI port 8501 already in use | The Docker stack is running; stop it or use `--server.port 8502`. |
| Very slow answers | Expected on CPU: 1.5b ≈ 45 s, 3b ≈ 110 s. Use a smaller model or lower top-k. First question after idle also loads the model (~5 s). |
| Answer is a long repetitive wall of text | Shouldn't happen since `MAX_TOKENS=512`; if it does, lower `MAX_TOKENS` or use temperature > 0. |
| `HEALTHCHECK is not supported for OCI image format` | Harmless Podman warning; build with `--format docker` to keep the healthcheck. |
| `podman compose` says no provider found | `uv tool install podman-compose`. |
| Permission denied on `/app/data` in the container (SELinux) | The `:Z` on the bind mount handles this; if you removed it, add it back. |
