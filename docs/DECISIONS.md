# Decision log

Every non-obvious choice made in this project: what was chosen, what else was
possible, and why. Numbered so the report and commits can refer to them
("see D-12"). Items marked **open** are known issues not yet acted on.

| # | Area | Decision |
|---|---|---|
| D-1 | Scope | Use the **CS** major handbook for Task 2 |
| D-2 | Tooling | **uv** instead of conda for the Python environment |
| D-3 | Dependencies | Drop torch / sentence-transformers / ragas from the course requirements |
| D-4 | Code structure | Refactor the single script into a `rag/` package; keep `run_txt.py` untouched |
| D-5 | PDF | **pypdf**, one Document per page |
| D-6 | PDF | NFKC-normalise extracted text |
| D-7 | PDF | Skip image-only pages instead of adding OCR |
| D-8 | Indexing | One index per document folder; explicit `--rebuild` |
| D-9 | Models | Keep `nomic-embed-text`; compare qwen2.5 0.5b / 1.5b / 3b |
| D-10 | Models | **qwen2.5:1.5b** as the default answer model |
| D-11 | Evaluation | Temperature 0, automatic signals + hand labels |
| D-12 | Robustness | Cap answers at 512 tokens |
| D-13 | UI | **Streamlit**, streaming answers, sources panel |
| D-14 | UI | Conversation history is shown but not sent to the model |
| D-15 | Docker | Ollama in its own container + one-shot model-pull job |
| D-16 | Docker | Documents as bind mount, index as named volume; Podman-compatible |
| D-17 | Retrieval | **open** — the fallback threshold never triggers |
| D-18 | Prompt | **open** — the baseline prompt invites general-knowledge answers |
| D-19 | Repository | What is (not) committed |

---

### D-1 · Use the CS handbook
- **Options:** any of the 11 provided handbooks.
- **Chosen:** `CS_MajorHandbook.pdf` (19 pages).
- **Why:** it's the student's own field, so answers can be judged without
  constantly re-reading the source. It also has a good mix of content types for
  testing: prose, bullet lists, flattened tables (catalogue, prerequisites), an
  image-only page, and even an internal contradiction (p.6 says "B.S. in Applied
  Mathematics").

### D-2 · uv instead of conda
- **Options:** conda (course instructions), venv + pip, uv.
- **Chosen:** uv with Python 3.11, project in `source_code/pyproject.toml`, exact
  versions locked in `uv.lock`.
- **Why:** uv was already installed and conda was not; it resolves and installs in
  seconds; the lock file makes the environment reproducible. `requirements.txt`
  is **exported** from the lock (`uv export`), so the course's
  `conda create … && pip install -r requirements.txt` path still works.
- **Python 3.11** rather than the system 3.14: chromadb and its native
  dependencies are not reliably available for 3.14 yet. `requires-python` is
  `>=3.10,<3.13`.

### D-3 · Leaner dependencies
- **Removed:** `torch`, `sentence-transformers`, `transformers`, `ragas`,
  `datasets`, `unstructured`, `langchain`, `langchain-community`.
- **Why:** embeddings come from Ollama, so nothing runs PyTorch in-process. Torch
  alone is ~2 GB with CUDA wheels; leaving it out keeps install time and the
  Docker image small (1.06 GB, most of it chromadb's onnxruntime and Streamlit).
  `ragas` would need an LLM judge and many extra packages; a simpler custom
  evaluation (D-11) is easier to explain in the report.
- **Kept / added:** `langchain-core`, `langchain-text-splitters`,
  `langchain-chroma`, `langchain-ollama`, `chromadb`, `pypdf`, `streamlit`,
  `python-dotenv`, `pyyaml`.

### D-4 · `rag/` package
- **Why:** three front-ends (CLI, web UI, evaluation) need the *same* pipeline.
  Copy-pasting the baseline three times would let them drift apart; with one
  package, a fix (e.g. D-12) applies everywhere.
- Settings moved from module constants to a `Settings` dataclass that reads
  environment variables, which is what lets Docker configure the app.
- `run_txt.py` is kept **unchanged** (only its data path) as the reference
  baseline for the report.

### D-5 · pypdf, one Document per page
- **Options:** pypdf, PyMuPDF (faster, better layout, AGPL licence),
  pdfplumber (better tables, slower), unstructured (heavy), LangChain's
  `PyPDFLoader` (a wrapper around pypdf).
- **Chosen:** pypdf directly — it's the course suggestion, pure Python
  (no system libraries in Docker), and fine for text-based PDFs.
- **Per page** so each chunk carries a page number, which makes answers
  checkable ("p.7") and makes the evaluation's retrieval metric possible.
- **Trade-off:** tables come out flattened (see FINDINGS §3).

### D-6 · NFKC normalisation
- The handbook contains ligature glyphs (`ﬁ`, `ﬂ`). They tokenise differently
  from plain letters, weakening matches between question and chunk. NFKC maps
  them to plain letters. The TOC also has broken glyphs (`Descrip;on`) from the
  PDF's font encoding; those can't be fixed generically and are left as is.

### D-7 · Skip image-only pages (no OCR)
- Page 10 of the CS handbook has no text layer (2 characters). OCR (e.g.
  Tesseract) would add a large system dependency for one page that is probably a
  diagram. The loader reports skipped pages so the gap is visible. Listed as a
  limitation / future improvement.

### D-8 · One index per folder, explicit rebuild
- The baseline stored the index inside the data folder and reused it whenever
  the folder existed — even after documents changed, silently answering from
  stale data.
- **Chosen:** `vector_store/<folder name>/`, plus `--rebuild` (CLI) /
  "Rebuild index" (UI).
- **Not done:** automatic change detection (hashing files). Simple to add later,
  but explicit rebuilds are easier to reason about and demonstrate.

### D-9 · Models compared
- **Embeddings:** `nomic-embed-text` kept from the baseline. Retrieval found the
  answer-bearing chunk for 21/23 answerable questions, and the two misses are
  caused by chunk boundaries (FINDINGS §2) rather than the embedding model, so
  chunking is the better lever to try first.
- **LLMs:** qwen2.5 **0.5b / 1.5b / 3b** — same family, so the comparison isolates
  *model size* (the assignment FAQ suggests exactly these). `gemma3:4b` and
  `qwen3:30b-a3b` are installed and selectable in the UI but were not in the
  formal comparison (different families confound size with training; 30b is too
  slow on this CPU for 75 questions).

### D-10 · Default answer model: qwen2.5:1.5b
- From the hand labels: correct answers 9 / 18 / 19 of 25 for 0.5b / 1.5b / 3b;
  median latency 24 / 45 / 110 s on this CPU.
- 1.5b gets almost all of 3b's accuracy at ~40% of its latency, and unlike 0.5b
  it did not invent answers to out-of-scope questions. The UI and Docker default
  to it. (The CLI keeps the baseline's 0.5b default so `run.py` with no flags
  behaves like the course sample; pass `--model`.)

### D-11 · Evaluation design
- **25 questions** written from a full read of the handbook, spread over
  requirements, policies, courses/prerequisites, outcomes, careers, assessment,
  plus 2 out-of-scope questions (tuition, department head) to test hallucination.
  Several are deliberately tricky (major vs. minor on the same page, a fact only
  in a table, the handbook's own typo).
- **Temperature 0** so differences come from the model, not sampling luck, and
  re-runs are reproducible.
- **Automatic signals:** *retrieval hit* separates retrieval failures from
  generation failures; *fact coverage* (substring match of key facts) gives a
  quick score. Retrieval is measured twice: *page hit* (an expected page was
  retrieved) and *chunk hit* (a retrieved chunk contains the question's
  `evidence` phrase). Chunk hit was added after the page metric reported 23/23
  while two questions' answer chunks had in fact not been retrieved — a page can
  split into several chunks. The baseline run's chunk hits were backfilled by
  re-running retrieval alone (deterministic, independent of the LLM; the
  re-run reproduced every recorded page list exactly).
- **Hand labels** (correct / incomplete / ambiguous / incorrect) are the real
  judgement — the assignment asks for these categories. They are stored in
  `labels.yaml` next to the results so they're easy to review and the raw
  results stay untouched. Labels disagreed with fact coverage often enough to be
  worth discussing (FINDINGS §5).
- Results are written incrementally (`results.jsonl`) and runs can `--resume`;
  added after the first full run (≈2 h on CPU) showed no progress and would have
  lost everything if interrupted.

### D-12 · 512-token answer cap
- During the baseline run, qwen2.5:0.5b fell into a repetition loop on the
  learning-outcomes question and generated 238,039 characters over 44 minutes.
  Ollama's default is effectively unlimited. 512 tokens (~350 words) is far more
  than any good answer needs. Configurable via `MAX_TOKENS`.
- The baseline results were produced **before** this cap; that run is kept
  as-is because the loop is itself a finding.

### D-13 · Streamlit, streaming, sources panel
- **Options:** Streamlit, Gradio, Flask/FastAPI + HTML.
- **Chosen:** Streamlit — already in the course requirements, `st.chat_message` /
  `st.chat_input` give a chat layout and `st.session_state` gives history with
  little code.
- **Streaming** (`st.write_stream`): on CPU an answer takes 30–60 s; showing
  tokens as they arrive makes the wait tolerable and visibly "alive".
- **Sources panel**: every answer shows the cited pages, relevance scores and the
  retrieved text. This makes the system auditable — a user (or grader) can check
  whether a wrong answer came from bad retrieval or a bad reading.
- **Sidebar controls** (collection, model, top-k, temperature, threshold, upload,
  rebuild) exist mostly to make the demo video and experiments easy.

### D-14 · History is not sent to the model
- The UI keeps and displays the whole conversation, which satisfies "basic
  conversation history". But each question is retrieved and answered
  independently.
- **Why:** sending history makes prompts longer (slower on CPU) and small models
  get confused by it; proper follow-up support needs *query rewriting* (turn
  "what does it cover?" into "what does CS311 cover?" before retrieval), which is
  a separate LLM call. Listed as future work.

### D-15 · Ollama in its own container, plus an init job
- **Options:** (a) install Ollama inside the app image; (b) app container uses
  the host's Ollama; (c) separate `ollama` service.
- **Chosen:** (c). One process per container; the official image is maintained
  upstream; models live in a named volume and survive rebuilds of the app image.
  (b) is fragile: the host Ollama listens on 127.0.0.1 only and host networking
  differs between Docker, Podman and OSes.
- **`ollama-init`** pulls `MODELS` (default `nomic-embed-text qwen2.5:1.5b`) and
  exits; `app` waits for it with `service_completed_successfully`, so
  `compose up` on a fresh machine works with no manual `ollama pull`.
- Image pinned to `0.12.11` (same as the host) so behaviour matches development.

### D-16 · Volumes; Podman compatibility
- **Documents:** bind mount `source_code/data → /app/data` so you can drop in a
  PDF and click "Rebuild index" without rebuilding the image. (`:Z` relabels it
  for SELinux on Fedora; harmless elsewhere.)
- **Index:** named volume `vector-store`, so it persists across restarts but
  doesn't litter the source tree with root-owned files.
- App runs as a **non-root** user (uid 1000).
- The machine has Podman, not Docker. The files are standard Compose and work
  with both; verified with `podman compose` (podman-compose 1.6). Podman's
  default OCI image format ignores `HEALTHCHECK` (harmless warning).

### D-17 · open — the fallback threshold never triggers
- The baseline converts L2² distance to `1/(1+d)` and falls back below 0.3.
  Ollama's embeddings are unit length, so `d = 2 − 2·cos` and in practice
  `d ≈ 0.4–1.1`, giving scores ≈ 0.48–0.7. Measured: "What is the recipe for
  pho?" scores **0.49**; a real handbook question 0.67. The threshold (0.3) is
  below both, so the fallback **never** fires — confirmed: 0 fallbacks in 75
  evaluation answers, including the out-of-scope ones.
- **Possible fixes** (to try as a Task-2 improvement experiment):
  1. use cosine similarity directly (`collection_metadata={"hnsw:space": "cosine"}`,
     score = 1 − d) and set the threshold from data (e.g. ~0.55 between the
     off-topic and on-topic examples);
  2. or keep L2 and raise the threshold to ~0.55.
- Not changed yet so the baseline results stay comparable; a before/after run
  makes a good report section.

### D-18 · open — the prompt invites general-knowledge answers
- Instruction 2 of the baseline prompt says "If the context is insufficient, use
  your general knowledge." For a handbook assistant that's risky: 0.5b used it to
  invent tuition fees and a department head. A stricter prompt ("answer only from
  the context; otherwise say you don't know; cite pages") is a cheap, likely
  improvement worth measuring. Not changed yet for the same reason as D-17.

### D-19 · What is committed
- **Committed:** code, configs, the CS handbook PDF, the FUV sample texts,
  evaluation questions, results and labels (they are deliverables).
- **Not committed:** the other 10 handbooks (not needed; keep the repo small —
  they're in the original zip); the course assignment PDFs in `docs/` (the
  instructor's material, not ours to redistribute — `.gitignore`d);
  `vector_store/` (rebuilt from documents); `.venv/`; `.env`; videos.
