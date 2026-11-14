# Demo video scripts (Task 6)

Four videos, one per task. The rubric asks each one to show **how** the task was
implemented, **why**, and the **output**. Aim for 3–5 minutes each; screen
recording with voice-over is enough.

**Recording tips**
- Terminal font ≥ 16 pt; browser zoom 125%. Close unrelated tabs/notifications.
- CPU answers take 30–60 s with `qwen2.5:1.5b`. Either keep talking over the wait
  (explain what's happening) or cut the wait in editing — but don't speed up the
  terminal output itself.
- Pre-warm the model before recording so the first answer isn't slower:
  `ollama run qwen2.5:1.5b "hi" >/dev/null`
- If the videos are too large for Canvas, upload to Google Drive / OneDrive and
  put the links in the report and the Canvas comment.
- Suggested file names: `task1_pdf_support.mp4`, `task2_handbook_chatbot.mp4`,
  `task3_docker.mp4`, `task4_web_ui.mp4` (videos are git-ignored; keep them in
  this folder for the submission zip).

---

## Video 1 — PDF support (Task 1)

**Before recording:** `cd source_code`; make sure the handbook index exists or not
(showing it being built is better: delete `vector_store/handbooks__*`).

| # | Show | Say |
|---|---|---|
| 1 | `run_txt.py` in the editor, the `glob("*.txt")` line | "The course baseline only reads .txt files." |
| 2 | `rag/loaders.py`: `load_pdf`, `clean_text`, `LOADERS` | "I added a pypdf loader. Each page becomes its own document with its page number, so answers can cite pages. Text is NFKC-normalised — the handbook uses ligature characters like 'ﬁ' that hurt matching. Pages with no text layer are skipped and reported; reading those would need OCR." |
| 3 | Run `uv run python run.py --data-dir data/handbooks --model qwen2.5:1.5b --rebuild -q "What is the prerequisite for CS311 Advanced Deep Learning?"` | Point at: "Loading: CS_MajorHandbook.pdf", "skipped 1 page … [10]", "Indexing N chunks". |
| 4 | The answer and "Sources: CS_MajorHandbook.pdf p.18" | "The answer — CS313 — comes from page 18 of the PDF, and the system tells us which page." |
| 5 | Open the PDF at page 18 next to the terminal | "And here it is in the original document." |
| 6 | (Optional) run once more without `--rebuild` | "Second run reuses the saved index — no re-embedding." |

## Video 2 — Handbook chatbot and evaluation (Task 2)

**Before recording:** have `eval/questions.yaml`, the baseline `summary.md` and
`labels.yaml` open in tabs; know which examples you'll show.

| # | Show | Say |
|---|---|---|
| 1 | The handbook PDF, quickly scroll | "I chose the CS major handbook." |
| 2 | 2–3 live questions with `run.py` (e.g. capstone GPA, CS201 language, careers) | Correct answers with page citations. |
| 3 | `eval/questions.yaml` — one entry | "25 questions across requirements, policies, courses, outcomes, careers, plus 2 out-of-scope ones. Each has a reference answer, the pages, an evidence phrase and key facts." |
| 4 | `evaluate.py --help`, then start a short run: `uv run python evaluate.py --models qwen2.5:1.5b --only careers capstone-eligibility --tag demo` | "The script runs every question against several models at temperature 0 and records answers, retrieval hits, key-fact coverage and latency." |
| 5 | Baseline `summary.md` table + label table | "0.5b: 9 correct, 12 incorrect; 1.5b: 18 correct; 3b: 19 correct but 2.5× slower. So 1.5b is the default." |
| 6 | One example per category from `summary.md` / `labels.yaml`: **correct** (CS311 prereq), **incorrect** (major courses → minor list; 0.5b tuition hallucination "Alibaba Cloud"), **incomplete** (Core courses without names), **ambiguous** (Applied Mathematics typo; CS210 "On holding = once a year") | For each, the reason: chunk boundary, flattened table, source error, small model. |
| 7 | The improvement results table (report §4.4) | "Strict prompt + working threshold + 800-character chunks: …" (numbers from the experiment runs). |

## Video 3 — Docker deployment (Task 3)

**Before recording:** stop the local Streamlit; `podman compose -f docker/docker-compose.yml down`.
To show the full first-start (model download) delete the volumes first
(`down -v`) — this downloads ~1.3 GB, so maybe record that part separately or
skip it and say what it does.

| # | Show | Say |
|---|---|---|
| 1 | `docker/Dockerfile` | "Slim Python 3.11 image, only the app's dependencies — no PyTorch because Ollama does the embeddings — runs Streamlit as a non-root user." |
| 2 | `docker/docker-compose.yml` | "Three services: Ollama itself, a one-shot job that pulls the models, and the app, which starts only after the models exist. Documents are bind-mounted so new PDFs don't need a rebuild; models and the index live in named volumes." |
| 3 | `podman compose -f docker/docker-compose.yml up -d --build` | (say: "I use Podman; the same file works with `docker compose`.") |
| 4 | `podman ps` | All three containers; ollama-init exited (0). |
| 5 | `podman logs rag-system_ollama-init_1 \| tail` | The model pulls succeeded. |
| 6 | `podman exec rag-system_app_1 python run.py -q "What GPA is required for the capstone?"` | An answer from inside the container — index built with the containerised Ollama. |
| 7 | Browser → http://localhost:8501, ask one question | The UI served from the container. |
| 8 | `podman compose -f docker/docker-compose.yml down` then `up -d` again | "Volumes persist: no re-download, no re-index." |

## Video 4 — Web interface (Task 4)

**Before recording:** `cd source_code && uv run streamlit run app.py` (or use the
Docker stack); clear the conversation.

| # | Show | Say |
|---|---|---|
| 1 | Empty page with example buttons | "Streamlit chat interface; example questions to start." |
| 2 | Click an example; let the answer stream | "Answers stream token by token — on CPU an answer takes ~45 s, so this matters." |
| 3 | Expand the **sources** panel | "Every answer shows the cited pages, relevance scores and the exact retrieved text, so you can check it." |
| 4 | Ask 2 more questions; scroll up | "Conversation history is kept." |
| 5 | Ask an off-topic question ("What is the recipe for pho?") with the **strict** prompt | Fallback warning + "I couldn't find that in the documents." |
| 6 | Sidebar: switch model (0.5b ↔ 1.5b), show top-k / temperature / prompt toggle | "Everything is configurable for experiments." |
| 7 | Upload a PDF (any PDF) → *Save & re-index*, ask about it | "New documents can be added from the browser." (Afterwards delete the uploaded file from `data/handbooks/` and rebuild.) |
| 8 | *Clear conversation* | |
| 9 | (Optional) the code: `app.py` `st.chat_message`, `st.write_stream`, `st.session_state` | "History is stored in session state; the pipeline is the same `rag` package as the CLI." |
