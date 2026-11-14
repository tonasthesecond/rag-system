---
title: "Building and Improving a Local Retrieval-Augmented Generation System"
subtitle: "CS311 Advanced Deep Learning — Final Project Report"
author: "[Your name] — [Student ID]"
date: "November 2026"
---

# 1. Introduction

Large language models answer fluently but have no access to private or recent
documents, and when they don't know something they tend to produce a plausible
answer anyway. Retrieval-Augmented Generation (RAG) addresses both problems by
retrieving relevant passages from a document collection and placing them in the
prompt, so that the model answers from evidence rather than memory.

This project extends the course's baseline RAG script into a complete local
question-answering system over the Fulbright **B.S. Computer Science Major
Handbook**. Everything runs on a laptop without a GPU: Ollama serves the
embedding model (`nomic-embed-text`) and the answer models (Qwen2.5 0.5B, 1.5B
and 3B), Chroma stores the vectors, and a Streamlit web interface provides the
chat front-end. The system is packaged with Docker Compose.

The work covers the four implementation tasks — PDF support (Task 1), a handbook
chatbot with a systematic evaluation (Task 2), Docker deployment (Task 3) and a
web interface (Task 4) — plus a set of improvement experiments motivated by the
evaluation. The main findings are that (i) model size matters a great deal at the
small end (0.5B → 1.5B doubles the number of correct answers) and much less
beyond it, (ii) most errors are *generation* errors on correctly retrieved text,
but the two hardest questions failed because of *chunking*, and (iii) several
weaknesses inherited from the baseline — a relevance threshold that could never
trigger and a prompt that invites guessing — were responsible for the worst
behaviour of the smallest model.

Source code, evaluation data and documentation are in the GitHub repository:
**[repository URL]**.

# 2. System architecture

## 2.1 Pipeline

The system has two phases. **Indexing** happens once per document collection:
files are loaded, their text is extracted and split into overlapping chunks,
each chunk is converted into a 768-dimensional embedding vector by
`nomic-embed-text`, and the vectors are stored in a persistent Chroma
collection. **Answering** happens for every question: the question is embedded
with the same model, the five nearest chunks are retrieved, a prompt is built
from an instruction template, the chunks (each tagged with its source file and
page) and the question, and the prompt is sent to the answer model.

```
PDF/TXT ─► extract text ─► chunk ─► embed ─► Chroma
                                              │ top-5
question ─► embed ─► nearest-neighbour search ┘
                              │
            prompt(instructions + chunks + question) ─► Qwen2.5 ─► answer + cited pages
```

## 2.2 Components and code structure

| Component | Choice | Notes |
|---|---|---|
| Model server | Ollama 0.12.11 | Serves both embedding and answer models over HTTP |
| Embeddings | `nomic-embed-text` | 768-d, unit-length vectors |
| Vector store | Chroma (embedded) | HNSW index persisted to disk |
| Answer models | Qwen2.5 0.5B / 1.5B / 3B | Same family, so size is the only variable |
| PDF extraction | pypdf | Pure Python, one document per page |
| Web UI | Streamlit | Chat layout, streamed answers |
| Deployment | Docker Compose | Tested with Podman |

The baseline was a single script. I refactored it into a small `rag/` package
(configuration, loaders, store, pipeline) used by three thin front-ends: a
command-line tool, the web interface, and an evaluation script. This guarantees
that the system I evaluated is exactly the system users interact with, and that a
fix in the pipeline reaches every front-end. All settings (models, chunk size,
top-k, thresholds, prompt style) are read from environment variables, which is
also how Docker configures the application.

Development ran on an Intel i7-1365U laptop with 30 GB of RAM and no discrete
GPU, so all inference is CPU-bound. This constraint shaped several decisions,
notably the choice of small models and the emphasis on latency.

# 3. Task 1 — PDF support

The baseline only read `.txt` files. I added a PDF loader based on pypdf and a
small registry that dispatches files to loaders by extension, so a folder can mix
PDF and text documents.

Three details turned out to matter:

1. **One document per page.** Each PDF page becomes a separate document carrying
   its page number. Chunks inherit it, so every answer can cite
   "CS_MajorHandbook.pdf p.7". This makes answers verifiable and enabled the
   retrieval metrics used in the evaluation.
2. **Text normalisation.** The handbook stores ligatures such as "ﬁ" as single
   glyphs, which the embedding model tokenises differently from "fi". Unicode
   NFKC normalisation and whitespace clean-up are applied to every page.
3. **Image-only pages.** pypdf only reads text stored as text. Page 10 of the
   handbook contains no extractable text (it is likely a diagram), so the loader
   skips pages with fewer than 20 characters and reports them. Recovering such
   content would require OCR.

I also fixed a baseline behaviour that would have caused confusing results: the
original code reused an existing vector store whenever its folder existed, even
if the documents had changed. Indexes are now stored per document collection and
configuration, and can be rebuilt explicitly (`--rebuild` in the CLI, a button in
the UI). The CS handbook produces 64 chunks with the baseline chunk settings.

# 4. Task 2 — Handbook chatbot and evaluation

## 4.1 Method

I selected the Computer Science handbook (19 pages) and wrote **25 test
questions** after reading it in full. They cover program requirements (credits,
required courses, the minor, Core curriculum), academic policies (declaring a
major or minor, capstone eligibility), course offerings (lists, prerequisites,
content, availability), learning outcomes and objectives, career paths and
assessment. Two questions — tuition fees and the department head — are **out of
scope**, to test whether the system admits when the handbook has no answer.
Several questions were deliberately difficult: the major and minor requirements
sit next to each other on the same page, one fact appears only in a table, and
one question touches an error in the handbook itself.

Each question has a reference answer, the page(s) containing it, an *evidence*
phrase that occurs only in the passage holding the answer, and a list of key
facts. The evaluation script runs every question against each model at
temperature 0 (so differences come from the models, not sampling) and records:

- **Page hit / chunk hit** — whether a retrieved chunk came from an expected
  page, and whether a retrieved chunk actually contained the evidence phrase;
- **Key-fact coverage** — the share of key facts found in the answer;
- **Latency**;
- a **hand label** for each answer: *correct*, *incomplete* (true but missing
  key parts), *ambiguous* (mixes correct and wrong statements, or faithfully
  repeats an error in the source) or *incorrect*.

## 4.2 Results

| Model | Correct | Incomplete | Ambiguous | Incorrect | Chunk hit | Fact coverage | Median latency |
|---|---|---|---|---|---|---|---|
| Qwen2.5 0.5B | 9 | 1 | 3 | 12 | 21/23 | 0.68 | 24 s |
| Qwen2.5 1.5B | 18 | 2 | 3 | 2 | 21/23 | 0.80 | 45 s |
| Qwen2.5 3B | 19 | 1 | 3 | 2 | 21/23 | 0.87 | 110 s |

*Baseline configuration: course prompt, chunks of 1,000 characters with 200
overlap, top-5 retrieval.*

Going from 0.5B to 1.5B doubles the number of correct answers; going from 1.5B to
3B adds one more at 2.5 times the latency. On the two out-of-scope questions the
0.5B model invented answers, while 1.5B and 3B both said the handbook did not
contain the information. I therefore made 1.5B the default model.

## 4.3 Examples and analysis

**Correct answers.** Direct factual look-ups in prose were reliable for the 1.5B
and 3B models: the prerequisite of CS311 (CS313), the main language of CS201
(Java), what students build in CS207 (Android applications in Java, designed
with UML), the capstone eligibility rule (major GPA of at least 3.5 and an
approved application), the program educational objectives, the career paths and
the graduate programs alumni were admitted to.

**Incorrect — retrieval failure.** Asked *"Which specific courses are required
for the Computer Science major?"*, all three models listed the **minor's**
six-course structure. The page-level metric suggested retrieval had succeeded,
but at chunk level it had not: page 7 is split into two chunks, and the one
holding the major's course list begins with unrelated text about exploratory and
compulsory courses, which dilutes its embedding. It did not appear even in the
top eight results, while the chunk that mentions "declare Computer Science as
their major" — followed by the minor requirements — ranked first. The models
answered from the only course list they were shown. The question about Core
courses failed the same way (*incomplete*): the course names are in a different
chunk from the descriptive paragraph that was retrieved.

**Incorrect — misreading a table.** pypdf flattens tables into lines such as
`CS210 Computer Networks On holding CS201`, separated from their column headers.
Asked how often CS210 is offered, the 1.5B model answered "once a year" — the
value in the neighbouring rows. The 3B model quoted "On holding" correctly but
then explained that this "typically means once a year" (*ambiguous*). Similar
leakage decorated otherwise correct course lists with "(CS TBA)" or "(16
credits)" taken from other tables.

**Incorrect — reasoning on correct context.** The 3B model quoted the rule for
declaring a minor exactly ("at least one Computer Science course") and then
concluded that a student must complete "at least seven CS courses", adding the
six minor courses to it. The key-fact score rated this answer 1.0, which
illustrates why automatic substring metrics are not enough.

**Incorrect — hallucination.** For the tuition question the 0.5B model answered:
*"The tuition fee for the Computer Science program at Alibaba Cloud is $50,000
per year. This information can be found in the 'Major Outline' section of the
CS_MajorHandbook.pdf document."* It also named an invented "Professor Xie" as
department head. Both answers cite the handbook for facts it does not contain.
The baseline prompt explicitly tells the model to use its general knowledge when
the context is insufficient, and the smallest model took that literally.

**Ambiguous — faithful to a wrong source.** The handbook's degree-requirements
section states that completing the program awards "a Bachelor of Science in
Applied Mathematics", evidently copied from another handbook. All three models
repeated it. RAG makes models faithful to retrieved text, which normally reduces
hallucination but also propagates errors in the source.

**Degenerate output.** On the learning-outcomes question the 0.5B model fell into
a repetition loop and generated 238,039 characters over 44 minutes. I added a
512-token generation limit to prevent this.

## 4.4 Improvement experiments

The analysis suggested three changes: a relevance threshold that actually works,
a prompt that forbids answering from general knowledge, and different chunking.

**Relevance threshold.** Because the embeddings are unit-length, cosine
similarity can be computed exactly from Chroma's distance as 1 − d/2. I changed
the score to cosine similarity and the fallback rule to "the *best* chunk scores
below a threshold", then calibrated the threshold with a retrieval-only check
(no LLM, a few seconds per run) on the 23 answerable questions and ten probe
questions. Every handbook question's best chunk scored at least 0.656, and six
clearly unrelated questions (a pho recipe, the weather, the World Cup) scored at
most 0.55, so a threshold of 0.6 rejects all six and none of the real
questions. Four *near-topic* probes — tuition, the department head, scholarships,
a football team — scored 0.62–0.69, overlapping with real questions: similarity
alone cannot tell that the handbook does not answer them.

**Strict prompt.** The new prompt tells the model to use only the excerpts, to
reply with a fixed sentence ("I couldn't find that in the documents.") when they
do not contain the answer, to check that the excerpt matches what was asked
(major versus minor, the right course code) and to cite sources. When the
threshold triggers, the system returns the fixed sentence without calling the
model.

**Chunking.** A retrieval-only sweep over chunk sizes measured whether the chunk
containing each answer was retrieved: 21/23 at 1,000/200 characters, 23/23 at
800/150, and 19–20/23 at 600 characters or less. Smaller chunks were worse
because they separate course descriptions from the course code they describe.

The end-to-end results (temperature 0, same 25 questions, hand-labelled):

| Run | Model | Prompt | Chunks | Correct | Incompl. | Ambig. | Incorrect | Out-of-scope invented |
|---|---|---|---|---|---|---|---|---|
| Baseline | 1.5B | course | 1000/200 | 18 | 2 | 3 | 2 | 0 / 2 |
| A | 1.5B | strict | 1000/200 | 18 | 3 | 1 | 3 | 0 / 2 |
| B | 1.5B | strict | 800/150 | 17 | 2 | 3 | 3 | 0 / 2 |
| Baseline | 0.5B | course | 1000/200 | 9 | 1 | 3 | 12 | 2 / 2 |
| C | 0.5B | strict | 800/150 | 10 | 0 | 8 | 7 | 0 / 2 |

For the 1.5B model the strict prompt did not change accuracy, but it changed the
*kind* of errors. Answers no longer contained invented extras — the
major-declaration answer dropped a false "and fulfil the minor requirements",
and the advanced-course list lost its spurious "(16 credits)" labels — but some
became too terse: the minor question was answered with "six courses" without
naming them. For the 0.5B model the strict prompt removed both hallucinated
out-of-scope answers and reduced incorrect answers from 12 to 7. It also exposed
a new failure: in 9 of 25 answers the model printed the refusal sentence and then
answered anyway, copying the *form* of the instruction rather than following it.

Better retrieval (run B) did not produce more correct answers. The 800-character
chunks fixed both retrieval failures — the Core courses were now listed and the
capstone alternative was answered correctly — but moving every chunk boundary
changed the context of other questions. Most strikingly, the question about
CS311's topics was answered with the description of CS313, a prerequisite course
whose description is almost identical. With 25 questions, a difference of one
answer is within noise.

I adopted the threshold fix and the strict prompt as defaults, since they match
the baseline's accuracy while never answering from general knowledge, and kept
1,000/200 chunks. The experiments suggest that the remaining errors need
structural changes — chunks that follow the document's headings, and tables
converted to sentences — rather than further tuning of numbers.

# 5. Task 3 — Docker deployment

The deployment is defined in `docker/docker-compose.yml` and consists of three
services:

- **ollama** runs the official Ollama image (pinned to version 0.12.11, the same
  as on the development machine). Downloaded models are stored in a named volume
  so they survive container rebuilds.
- **ollama-init** is a one-shot job that waits until Ollama is healthy, pulls the
  embedding model and the default answer model, and exits. This makes the stack
  self-contained: on a fresh machine `docker compose up` is the only step.
- **app** is built from `docker/Dockerfile`: a `python:3.11-slim` image with only
  the application's dependencies, running Streamlit on port 8501 as a non-root
  user. It starts only after `ollama-init` has completed successfully, and
  reaches Ollama by its service name on the internal network.

The document folder is bind-mounted from the host, so new PDFs can be added
without rebuilding the image, and the Chroma index is kept in a named volume. I
reduced the image size by removing PyTorch, sentence-transformers and RAGAS from
the course's requirement list, since embeddings are computed by Ollama; the
resulting image is about 1 GB.

The development machine runs Podman rather than Docker, so the stack was tested
with `podman compose`; the files are standard Compose and work with both. The
test confirmed the start-up ordering (Ollama healthy → models pulled → app
started), index construction inside the container, and a correct answer to a
question asked through the containerised CLI and web interface.

# 6. Task 4 — Web interface

The Streamlit interface presents a chat: questions in a fixed input box at the
bottom, the conversation above it. Because CPU inference takes 30–60 seconds per
answer, answers are **streamed** token by token, which makes the wait visibly
productive. Every answer has an expandable **sources panel** listing the cited
pages, their relevance scores and the retrieved text, and a warning is shown when
the answer was produced without relevant documents. This panel turned out to be
the most useful feature during development: it shows immediately whether a wrong
answer came from retrieval or from the model.

A sidebar lets the user choose the document collection and any installed Ollama
model, adjust top-k, temperature, the relevance threshold and the prompt style,
upload new PDF or text files and rebuild the index, and clear the conversation.
On an empty conversation, example questions are offered as buttons.

Conversation history is kept in Streamlit's session state and displayed, but
each question is answered independently. Sending previous turns to the model
would make prompts longer and slower, and resolving follow-ups such as "what
does *it* cover?" properly requires rewriting the question before retrieval —
listed below as future work.

# 7. Observations and lessons learned

**Measure retrieval at the right granularity.** My first retrieval metric
counted a hit when any chunk from the expected page was retrieved, and reported
23/23. Checking individual answers showed that two of those "hits" had retrieved
the wrong chunk of the right page. Adding a chunk-level metric changed the
explanation of the hardest failures from "the model confused major and minor" to
"the model was never shown the major's requirements".

**Automatic scores need human review.** Key-fact coverage disagreed with my
labels in both directions: it rewarded an answer that quoted a rule correctly and
then drew a wrong conclusion, and penalised correct but differently worded
answers. Labelling 75 answers by hand took time but produced most of the insight
in this report.

**Inherited defaults deserve scrutiny.** The baseline converts Chroma's squared
L2 distance to a score with 1/(1+d) and falls back to general knowledge when the
average score is below 0.3. Because Ollama's embeddings are unit-length, the
distance is 2 − 2·cos θ and the score stays between roughly 0.48 and 0.7 — an
off-topic question about a pho recipe scored 0.49. The fallback could never
trigger: zero fallbacks occurred in 75 baseline answers.

**Smaller is not always better for chunks.** I expected smaller chunks to
separate the major and minor requirements; a retrieval-only sweep showed the
opposite. Chunks of 400–600 characters separated course descriptions from their
course codes, lowering chunk-level recall from 21/23 to 19–20/23, while 800
characters with 150 overlap retrieved the right chunk for all 23 answerable
questions.

**Engineering for slow experiments.** The first full evaluation took about two
hours on the CPU, wrote nothing until it finished and printed no progress. I
changed the script to save every answer as it is produced and to resume
interrupted runs, and added a retrieval-only mode that evaluates chunking choices
in seconds.

# 8. Limitations and future work

- **Tables and images.** Flattened tables cause most remaining factual errors;
  image-only pages are skipped. Table-aware extraction (e.g. pdfplumber),
  converting table rows to sentences before indexing, and OCR would address this.
- **Chunking.** Fixed-size chunking ignores the document's structure. Splitting
  on headings, or prefixing each chunk with its section title, should be more
  robust than tuning a character count on a 25-question test set.
- **Out-of-scope detection.** Similarity thresholds separate clearly off-topic
  questions but not questions about the same domain that the handbook does not
  answer (tuition, scholarships); those depend on the model following the prompt.
- **Follow-up questions.** Conversation history is not used for retrieval;
  query rewriting would allow pronouns and ellipsis.
- **Evaluation scale.** 25 questions labelled by one person is enough to find
  failure patterns but not to measure small differences reliably. An LLM-as-judge
  with a larger model could scale the labelling.
- **Hardware.** On CPU the 3B model needs almost two minutes per answer; a GPU
  would make larger, more accurate models practical.

# 9. Conclusion

The project produced a working local RAG system that answers questions about the
Computer Science handbook with page-level citations, through a command line, a
web interface and a reproducible container deployment. Systematic evaluation
showed that a 1.5B-parameter model is a good trade-off on CPU, that most errors
come from reading retrieved text rather than from retrieval itself, and that the
remaining retrieval failures come from where chunks are cut. The evaluation also
exposed problems in the baseline design — an ineffective relevance threshold and
a prompt that invites hallucination — and the improvement experiments quantify
the effect of fixing them.

# Appendix — Reproducing the results

```bash
cd source_code
uv sync                                     # or: pip install -r requirements.txt
ollama pull nomic-embed-text && ollama pull qwen2.5:1.5b
# baseline prompt, three models (see note below)
uv run python evaluate.py --prompt baseline --models qwen2.5:0.5b qwen2.5:1.5b qwen2.5:3b
# experiments A, B, C
uv run python evaluate.py --prompt strict --models qwen2.5:1.5b
uv run python evaluate.py --prompt strict --chunk-size 800 --chunk-overlap 150 --models qwen2.5:1.5b
uv run python evaluate.py --prompt strict --chunk-size 800 --chunk-overlap 150 --models qwen2.5:0.5b
# retrieval-only checks (threshold calibration, chunk sweep)
uv run python evaluate.py --retrieval-only --chunk-size 800 --chunk-overlap 150
uv run streamlit run app.py                 # web interface
docker compose -f ../docker/docker-compose.yml up --build   # container deployment
```

All results, including every answer, its label and the settings used, are in
`source_code/eval/results/`. Note: the baseline run predates the 512-token
generation cap and the new relevance score; re-running it today applies both,
so the 0.5B repetition loop cannot recur and fallbacks may differ.
