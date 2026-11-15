# How the system works

This document walks through what happens from "a PDF on disk" to "an answer on
screen", which file does each step, and the RAG concepts behind it. Read it top to
bottom once; afterwards the code should feel familiar.

- [1. The big picture](#1-the-big-picture)
- [2. Indexing: documents → vectors](#2-indexing-documents--vectors)
- [3. Answering: question → answer](#3-answering-question--answer)
- [4. Code map](#4-code-map)
- [5. Configuration](#5-configuration)
- [6. The three front-ends](#6-the-three-front-ends)
- [7. Docker topology](#7-docker-topology)
- [8. Glossary](#8-glossary)

---

## 1. The big picture

A RAG (Retrieval-Augmented Generation) system answers questions in two phases:

```
 INDEXING (once, or when documents change)
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────────────┐   ┌──────────────┐
 │ PDF/TXT  │──►│ extract  │──►│  split   │──►│ embed each chunk │──►│ Chroma store │
 │  files   │   │  text    │   │ (chunks) │   │ nomic-embed-text │   │ (on disk)    │
 └──────────┘   └──────────┘   └──────────┘   └─────────────────┘   └──────┬───────┘
                                                                           │
 ANSWERING (every question)                                                │
 ┌──────────┐   ┌─────────────────┐   ┌─────────────────────────┐          │
 │ question │──►│ embed question  │──►│ find 5 nearest chunks   │◄─────────┘
 └──────────┘   └─────────────────┘   └───────────┬─────────────┘
                                                  ▼
                       ┌──────────────────────────────────────────────┐
                       │ prompt = instructions + chunks + question     │
                       └───────────────────────┬──────────────────────┘
                                               ▼
                       ┌──────────────────┐   ┌──────────────────────────┐
                       │ LLM (qwen2.5)    │──►│ answer + cited pages     │
                       └──────────────────┘   └──────────────────────────┘
```

The key idea: the LLM never "knows" the handbook. On every question we *find* the
few passages most likely to contain the answer and paste them into the prompt.
The LLM's job is reduced to reading comprehension over ~5,000 characters of text.

Everything runs locally. Two separate programs are involved:

| Program | Role | Talks to |
|---|---|---|
| **Ollama** (`ollama serve`, port 11434) | Runs the neural networks: the embedding model and the LLM | nothing, it only answers HTTP requests |
| **Our Python app** | Reads files, chunks, stores vectors (Chroma, embedded in-process), builds prompts, shows UI | Ollama over HTTP |

Chroma is **not** a separate server here: it is a Python library that stores its
data in a folder (`source_code/vector_store/<index name>/`, a SQLite file plus
HNSW index files).

## 2. Indexing: documents → vectors

Code: `rag/loaders.py` and `rag/store.py::load_or_build`.

### 2.1 Loading and text extraction — `rag/loaders.py`

`load_documents(folder)` looks at every file in the folder and dispatches by
extension through the `LOADERS` table:

- **`.txt` → `load_txt`**: the whole file becomes one `Document`
  (`page_content` = text, `metadata = {"source": filename}`).
- **`.pdf` → `load_pdf`**: uses **pypdf** to extract the selectable text of each
  page. Each page becomes its own `Document` with
  `metadata = {"source", "page", "total_pages"}`. Keeping pages separate is what
  lets answers cite "CS_MajorHandbook.pdf p.7".

Every PDF page goes through `clean_text`:

1. **Unicode NFKC normalisation**: PDFs often store "fi" as one ligature glyph `ﬁ`.
   To the embedding model `ﬁrst` and `first` are different tokens, so a question
   containing "first" would match worse. NFKC turns `ﬁ` back into `f`+`i`.
2. **Whitespace collapsing**: runs of spaces and blank lines are squeezed.

Pages with fewer than 20 characters after cleaning are **skipped** and reported:
they are images (scans, diagrams). pypdf can only read text that is stored as
text; reading text *inside images* would need OCR. In the CS handbook, page 10
is such a page.

> Tables are a weak spot: pypdf outputs table cells left-to-right, line by line,
> so a row like `CS210 | Computer Networks | On holding | CS201` becomes a flat
> line of words, and the column headers are far away. See `docs/FINDINGS.md`.

### 2.2 Chunking — `RecursiveCharacterTextSplitter`

Pages are too long to retrieve as a unit (an answer is usually one sentence or
list in a 3,000-character page), and embedding models summarise long text into a
single vector poorly. So each page is split into **chunks** of at most
`CHUNK_SIZE = 1000` characters, with `CHUNK_OVERLAP = 200` characters shared
between neighbouring chunks so a sentence cut at a boundary still appears whole in
one of them.

"Recursive" means it tries to split at the most natural boundary first: paragraph
breaks (`\n\n`), then line breaks, then spaces, then characters. Chunk metadata
(source, page) is inherited from the page.

The CS handbook (18 text pages) becomes **64 chunks**.

### 2.3 Embedding — `nomic-embed-text` via Ollama

An **embedding model** maps text to a fixed-length vector (here 768 numbers)
such that texts with similar meaning get vectors pointing in similar directions.
`OllamaEmbeddings` sends each chunk to Ollama's `/api/embed` endpoint and gets a
vector back. Ollama returns **unit-length** vectors (length 1.0), which matters
for the scores below.

### 2.4 Storing — Chroma

`Chroma.from_documents(...)` stores each chunk's text, metadata and vector in the
collection, and builds an **HNSW** index (a graph structure for fast approximate
nearest-neighbour search). It persists to
`vector_store/<folder>__<embedding model>__<chunk size>-<overlap>/`
(e.g. `handbooks__nomic-embed-text__1000-200`), so different corpora and
different chunking experiments never share or overwrite an index.

On the next run, `load_or_build` sees the folder exists and simply opens it — no
re-embedding. **It does not notice if documents changed**; that is what
`--rebuild` (CLI) and "Rebuild index" (UI) are for.

## 3. Answering: question → answer

Code: `rag/pipeline.py`. `prepare()` does steps 1–4, `ask()` adds step 5.

1. **Embed the question** with the same embedding model (it must be the same
   model, otherwise the vectors live in different spaces).
2. **Retrieve** (`retrieve`): Chroma returns the `TOP_K = 5` chunks whose vectors
   are closest to the question's, with their **distance**. Chroma's default
   distance is *squared Euclidean (L2²)*.
3. **Score**: each distance is converted to a **cosine similarity**. The vectors
   are unit length, so `d = 2 − 2·cos(θ)` and `cos(θ) = 1 − d/2` (1 = same
   direction, 0 = unrelated). If even the **best** chunk scores below
   `SCORE_THRESHOLD = 0.6`, the question is treated as off-topic (**fallback**).
   0.6 was calibrated on the handbook: every handbook question's best chunk
   scores ≥ 0.656, clearly off-topic questions ≤ 0.55 (DECISIONS D-17).
   > The course baseline used `1/(1+d)` averaged over the five chunks with a
   > threshold of 0.3. That score stays within ~0.48–0.7, so its fallback could
   > never trigger.
4. **Build the prompt** (`build_prompt`): the template `PROMPTS[PROMPT_STYLE]` is
   filled with the chunks, each prefixed by its source tag (`[CS_MajorHandbook.pdf p.7]`),
   separated by `---`, followed by the question and the instructions. Two styles:
   - **`strict`** (default): use only the excerpts; if they don't contain the
     answer reply exactly "I couldn't find that in the documents."; check the
     excerpt is about exactly what was asked (major vs. minor, course code);
     cite source tags. In the fallback case the model is **not called at all** —
     the "not found" sentence is returned directly.
   - **`baseline`**: the course prompt — use the context if relevant, otherwise
     general knowledge. In the fallback case the model is told to use general
     knowledge.
5. **Generate** (`get_llm` → `OllamaLLM.invoke` or `.stream`): Ollama runs the LLM
   on the prompt. Settings: `TEMPERATURE` (randomness; 0 = always pick the most
   likely token) and `MAX_TOKENS = 512` (hard cap on answer length, sent to
   Ollama as `num_predict`).

`ask()` returns `{answer, sources, top_score, avg_score, used_fallback, prompt}`. Every
front-end consumes this same structure.

## 4. Code map

```
source_code/
├── rag/                    ← the library; everything else is a thin front-end
│   ├── config.py           Settings dataclass; reads env vars / .env; index_dir per corpus+config
│   ├── loaders.py          txt + pdf loaders, text cleaning, LOADERS registry
│   ├── store.py            embeddings client, load_or_build (chunk + embed + persist)
│   └── pipeline.py         prompts (strict/baseline), retrieve, prepare, ask, list_models
├── run.py                  CLI: one question → answer + top 3 sources
├── app.py                  Streamlit web UI
├── evaluate.py             batch evaluation over eval/questions.yaml
├── eval/
│   ├── questions.yaml      25 test questions (reference, pages, evidence, key facts) + probes
│   └── results/<run>/      summary.md, results.csv/json/jsonl, labels.yaml, config.json
├── run_txt.py              the untouched course baseline (for comparison)
├── data/
│   ├── handbooks/          CS_MajorHandbook.pdf  (Task 2 knowledge source)
│   └── sample_txt/         the FUV .txt files from the baseline
├── pyproject.toml, uv.lock dependencies (uv); requirements.txt exported for pip
└── .env.example            every configurable setting
docker/
├── Dockerfile              app image
└── docker-compose.yml      ollama + ollama-init + app
docs/                       you are here
```

**Dependency direction:** `run.py`, `app.py`, `evaluate.py` → `rag.pipeline` /
`rag.store` → `rag.loaders`, `rag.config`. Nothing in `rag/` imports a front-end,
so the same pipeline is tested by the CLI, the UI and the evaluation.

## 5. Configuration

All settings live in `rag/config.py::Settings`. Each field reads an environment
variable (or `source_code/.env`) and falls back to a default:

| Variable | Default | Meaning |
|---|---|---|
| `DATA_DIR` | `data/sample_txt` | folder to index (CLI default; UI picks from a dropdown) |
| `VECTOR_STORE` | `vector_store` | parent folder for indexes; one subfolder per corpus + embedding model + chunking |
| `COLLECTION` | `rag_documents` | Chroma collection name |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 1000 / 200 | chunking (a new value builds its own index) |
| `EMBED_MODEL` | `nomic-embed-text` | embedding model (a new model builds its own index) |
| `LLM_MODEL` | `qwen2.5:1.5b` | answer model (CLI, UI and Docker) |
| `TEMPERATURE` | 0.2 | sampling randomness (evaluation forces 0) |
| `MAX_TOKENS` | 512 | max answer length in tokens |
| `TOP_K` | 5 | chunks retrieved per question |
| `SCORE_THRESHOLD` | 0.6 | best-chunk cosine similarity below which the question counts as off-topic |
| `PROMPT_STYLE` | `strict` | `strict` (documents only) or `baseline` (course prompt) |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | where Ollama is |

Relative paths are resolved against `source_code/`, so commands work from any
working directory.

## 6. The three front-ends

### CLI — `run.py`
Parses flags (`-q`, `--data-dir`, `--model`, `--top-k`, `--rebuild`), overrides
the matching `Settings` fields, calls `load_or_build` then `ask`, prints the answer
and the top three sources.

### Web UI — `app.py` (Streamlit)
Streamlit re-runs the whole script top to bottom on every interaction. State that
must survive re-runs lives in `st.session_state`:

- `messages`: the conversation (each assistant message also stores its sources,
  score and model, so the sources panel can be re-drawn for old messages).
- `rebuild`: a counter used to force re-indexing.

The vector store is opened inside `get_db`, decorated with `@st.cache_resource`,
so it is created once per (collection, embedding model, chunk settings) and
shared across re-runs and browser tabs.

Answer flow: `prepare()` (retrieval, under a spinner) → `st.write_stream(llm.stream(prompt))`
(tokens appear as they are generated) → sources expander + fallback warning.
If `prepare()` already produced an answer (strict refusal), it is shown directly.
History is **displayed** but **not sent to the model** (see D-14).

### Evaluation — `evaluate.py`
For each model × question: `ask()`, time it, compute `retrieval_hit` (was any
expected page among the retrieved chunks?), `evidence_hit` (did a retrieved chunk
contain the answer's evidence phrase? — stricter, since a page has several
chunks) and `fact_coverage` (fraction of key
facts found in the answer, case-insensitive substring match), append a line to
`results.jsonl`. At the end, write `results.json`, `results.csv`, `summary.md`.
`--summarize <dir>` regenerates the summary and merges `labels.yaml`.
`--retrieval-only` skips the LLM entirely and reports page/chunk hit rates plus
the best-chunk score of the in-scope questions and of the off-/near-topic probes
in `questions.yaml` — seconds instead of an hour, used for chunking sweeps and
for calibrating the threshold.

## 7. Docker topology

```
 host browser ──► localhost:8501
                      │
 ┌────────────────────┼──────────────── compose network ──────────────────────┐
 │  ┌─────────────────▼───┐   HTTP :11434   ┌──────────────────────┐           │
 │  │ app                  │───────────────►│ ollama               │           │
 │  │ python:3.11-slim     │                │ ollama/ollama:0.12.11│           │
 │  │ streamlit app.py     │                └──────────┬───────────┘           │
 │  └──┬───────────────┬───┘                           │                       │
 │     │               │                    ┌──────────▼───────────┐           │
 │  bind mount     named volume             │ volume: ollama-models│           │
 │  ../source_code/data  vector-store       └──────────▲───────────┘           │
 │  → /app/data    → /app/vector_store                 │ pulls models once     │
 │                                          ┌──────────┴───────────┐           │
 │                                          │ ollama-init (exits)  │           │
 │                                          └──────────────────────┘           │
 └─────────────────────────────────────────────────────────────────────────────┘
```

Start-up order is enforced with `depends_on` conditions:
`ollama` healthy (`ollama list` succeeds) → `ollama-init` pulls models and exits 0
→ `app` starts. Inside the network the app reaches Ollama by its service name,
`http://ollama:11434`.

## 8. Glossary

| Term | Meaning |
|---|---|
| **Embedding** | A vector representing a text's meaning; similar meaning → nearby vectors |
| **Chunk** | A ≤1000-character piece of a page; the unit that is retrieved |
| **Top-k** | Number of nearest chunks retrieved per question (5) |
| **L2² distance** | Squared straight-line distance between vectors; Chroma's default |
| **Cosine similarity** | Angle-based similarity in [-1, 1]; for unit vectors L2² = 2 − 2·cos |
| **HNSW** | Graph-based index for fast approximate nearest-neighbour search |
| **Fallback** | Branch taken when even the best chunk is below the threshold: strict → refuse; baseline → general knowledge |
| **Temperature** | Randomness of token sampling; 0 = deterministic |
| **num_predict** | Ollama's name for the max number of tokens to generate |
| **Hallucination** | Fluent output that is not supported by the source (or by reality) |
| **Retrieval hit** | Our metric: an expected handbook page was among the retrieved chunks |
| **Chunk hit** | Our stricter metric: a retrieved chunk contains the answer's evidence phrase |
| **Fact coverage** | Our metric: share of a question's key facts appearing in the answer |
