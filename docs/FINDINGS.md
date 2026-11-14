# Evaluation findings (baseline run)

What the baseline evaluation showed and *why* each failure happened. This is raw
material for the report's evaluation and limitations sections.

Run: `source_code/eval/results/20261114-1616-baseline/` — 25 questions,
`nomic-embed-text`, chunk 1000/200, top-k 5, temperature 0, CPU only
(i7-1365U, no GPU). Labels are in `labels.yaml` in that folder.

## 1. Headline numbers

| Model | Correct | Incomplete | Ambiguous | Incorrect | Page hit | Chunk hit | Fact coverage | Median latency |
|---|---|---|---|---|---|---|---|---|
| qwen2.5:0.5b | 9 | 1 | 3 | **12** | 23/23 | 21/23 | 0.68 | 24 s |
| qwen2.5:1.5b | 18 | 2 | 3 | 2 | 23/23 | 21/23 | 0.80 | 45 s |
| qwen2.5:3b | **19** | 1 | 3 | 2 | 23/23 | 21/23 | 0.87 | 110 s |

*Page hit* = a chunk from an expected page was retrieved. *Chunk hit* = a retrieved
chunk actually contained the answer (an `evidence` phrase from `questions.yaml`).
Retrieval is identical for all three models (it doesn't depend on the LLM).

- **Retrieval mostly worked, but the page-level metric hid two misses.** A page
  can split into several chunks, so "right page" ≠ "right text". At chunk level,
  retrieval missed `req-major-courses` and `req-core` (§2). Those two questions
  were failed by *every* model — no model can answer from text it never sees.
- **The other failures are generation failures:** the answer was in the prompt
  and the model misread, mixed, or ignored it.
- **Size matters most at the bottom.** 0.5b → 1.5b doubles the correct answers;
  1.5b → 3b adds one more at 2.5× the latency. Diminishing returns.
- **Out-of-scope questions:** 0.5b hallucinated both (tuition "$50,000 per year
  at Alibaba Cloud", a "Professor Xie" heading the department). 1.5b and 3b both
  correctly said the handbook doesn't contain the answer.

## 2. Failure pattern: chunk boundaries vs. document sections

*Questions:* `req-major-courses` (all 3 incorrect), `req-core` (1.5b/3b
incomplete), `req-declare-major`, `req-declare-minor` (3b), `req-minor` (0.5b),
`req-major-credits` (0.5b).

Page 7 is split into two chunks by the 1000-character splitter:

| Chunk | Contains |
|---|---|
| p7 #0 | end of the exploratory-course text, compulsory courses, **major requirements list** |
| p7 #1 | **rule to declare the major** ("at least two CS courses"), **minor requirements**, rule to declare the minor |

**Retrieval miss (`req-major-courses`).** For "Which specific courses are
required for the Computer Science major?", chunk p7 #0 is not in the top 8. Its
vector is diluted by the unrelated exploratory/compulsory text at its start,
while p7 #1 — which literally says "declare Computer Science as their major" —
ranks first. Every model then answered with the minor's six-course list,
because that's the course list it was given.

**Retrieval miss (`req-core`).** The Core course names sit at the very end of
page 6, in a different chunk from the descriptive paragraph about the Core. The
descriptive chunk was retrieved (and matched the question better), the list
wasn't — so 1.5b and 3b gave a correct but name-less description.

**Generation mix-ups.** Where the right chunk *was* retrieved, chunk p7 #1 still
puts four look-alike blocks side by side (declare major / minor list / declare
minor). 3b quoted the minor-declaration rule correctly then "reasoned" its way
to "seven courses"; 0.5b and 1.5b attached minor requirements to the major
declaration.

*Why:* fixed-size chunking ignores the document's structure, so one chunk can
mix sections and one section can be split from its heading.
*Possible fixes:* split on headings (structure-aware chunking), smaller chunks,
prefix each chunk with its section heading, or retrieve more chunks (top-k 8–10)
at a latency cost.

## 3. Failure pattern: flattened tables

*Questions:* `course-cs210-availability` (0.5b, 1.5b incorrect; 3b ambiguous),
`course-advanced-list` (0.5b/1.5b ambiguous).

pypdf extracts the course catalogue as lines like
`CS210 Computer Networks On holding CS201`, with the column headers
(AVAILABILITY, PREREQUISITES) on a different line. 1.5b answered "once a year" —
the value in the rows above and below. 3b quoted "On holding" correctly but then
"explained" it as once a year. 0.5b and 1.5b decorated an otherwise correct list
with values from other tables: "(CS TBA)" from the cross-listing table, "(16
credits)" from the major requirements ("four advanced courses (16 credits)").

*Possible fixes:* table-aware extraction (pdfplumber, PyMuPDF), or converting
each table row to a sentence ("CS210 Computer Networks: availability On
holding; prerequisite CS201") before indexing.

## 4. Failure pattern: faithful to a wrong source

*Question:* `req-degree-name` (all 3 models ambiguous).

The handbook's degree-requirements section says completing the program awards
"A Bachelor of Science in **Applied Mathematics**" — a copy-paste error from
another handbook (the cover says B.S. Computer Science). All three models
repeated it. RAG makes the model *faithful to the retrieved text*, which is
usually what we want, but it means errors in the source become errors in the
answer. Detecting this would need cross-checking against other passages (the
cover page was not retrieved for this question).

## 5. The automatic score is not enough

Fact coverage (does the answer contain the key strings?) disagreed with the hand
labels in both directions:

| Question / model | Coverage | Label | What happened |
|---|---|---|---|
| `req-declare-minor` / 3b | 1.0 | incorrect | Quotes the rule, then concludes "at least **seven** CS courses" |
| `course-cs210-availability` / 3b | 1.0 | ambiguous | Says "On holding", then misreads it as once a year |
| `req-exploratory` / 0.5b | 0.5 | incorrect | Answers a different question; "two" matched by accident |
| `req-major-credits` / 1.5b | 1.0 | correct | …but its shown arithmetic sums to 44, not 56 |
| `req-core` / 1.5b, 3b | 0.0 | incomplete | Correctly describes the Core, just never names the courses |

Substring matching can't see *reasoning errors* or answers to the wrong
question. That's why the labels were done by hand; an LLM-as-judge (e.g. a
larger model grading against the reference) is the scalable alternative.

## 6. Small-model behaviours (0.5b)

- **Answering a nearby question:** for prerequisites (`course-prereq-cs302`) and
  availability (`cs210`) it summarised the course description instead.
- **Over-long, padded answers:** "Context Analysis / Guidelines Analysis"
  essays (`capstone-honors`) that never answer yes/no.
- **Repetition loop:** `outcomes-plo` produced 238,039 characters in 44 minutes.
  Fixed by capping generation at 512 tokens (DECISIONS D-12).
- **Hallucination with false citations:** the tuition answer *cites the
  handbook* ("can be found in the Major Outline section") for an invented fact.

## 7. Things that worked well

- Direct factual look-ups in prose: prerequisites in course descriptions
  (CS311 → CS313), CS201's language (Java), CS207's project (Android/Java),
  capstone GPA (3.5), PEOs, careers, graduate programs — correct for 1.5b and 3b,
  mostly for 0.5b too.
- Lists that sit together in one chunk (intermediate courses, CS311 topics).
- Page-level citations made every one of these failures diagnosable in minutes.

## 8. System-level observations (baseline)

- **The fallback branch was dead code** with these embeddings: 0 fallbacks in 75
  answers; an off-topic question still scored 0.49 against a threshold of 0.3.
  Fixed in D-17.
- **The prompt permits guessing** ("use your general knowledge"). Larger models
  ignored that and declined; 0.5b took it literally. Addressed in D-18.
- **Latency is dominated by prompt processing on CPU**: ~5,000 characters of
  context per question. Fewer/shorter chunks would speed things up at some
  recall risk.

## 9. Improvement experiments

Three changes were tested against the baseline, each on the same 25 questions
at temperature 0. Folders under `source_code/eval/results/`; labels in each
folder's `labels.yaml`.

### 9.1 Retrieval-only checks (no LLM, seconds each)

**Relevance threshold** (cosine similarity of the best chunk, threshold 0.6):

| Probe set | Best-chunk scores | Fallback |
|---|---|---|
| 23 handbook questions | min 0.656, median 0.785 | 0/23 ✔ |
| 6 off-topic (pho, weather, World Cup, France, dorms, add/drop) | 0.41–0.55 | 6/6 ✔ |
| 4 near-topic (tuition, dept. head, scholarships, football) | 0.62–0.69 | 0/4 ✘ |

Similarity can reject clearly unrelated questions but not unanswered questions
about the same domain — those need the prompt.

**Chunk size sweep** (answer chunk in top 5, 23 questions): 1000/200 → 21,
**800/150 → 23**, 600/100 → 20, 500/100 → 19, 400/80 → 19; top-k 8 doesn't rescue
1000/200 (21). Smaller chunks separate course descriptions from their headings.

### 9.2 End-to-end runs

| Run | Model | Prompt | Chunks | Correct | Incompl. | Ambig. | Incorrect | OOS invented | Median latency |
|---|---|---|---|---|---|---|---|---|---|
| baseline | 1.5b | course | 1000/200 | 18 | 2 | 3 | 2 | 0/2 | 45 s |
| A | 1.5b | strict | 1000/200 | 18 | 3 | 1 | 3 | 0/2 | 55 s |
| B | 1.5b | strict | 800/150 | 17 | 2 | 3 | 3 | 0/2 | 47 s |
| baseline | 0.5b | course | 1000/200 | 9 | 1 | 3 | 12 | 2/2 | 24 s |
| C | 0.5b | strict | 800/150 | 10 | 0 | 8 | 7 | 0/2 | 22 s |

**A — strict prompt (1.5b).** Same number of correct answers. What changed:
- *Better:* no invented extras — the major-declaration answer drops the false
  "and fulfil the minor requirements"; the advanced-course list loses the bogus
  "(16 credits)" tags. Answers are shorter and cite source tags.
- *Worse:* terseness — the minor answer says "six courses" without listing them;
  the intermediate list drops one course; for the capstone question it claims
  the excerpts mention no alternative although they do.
- Out-of-scope: the exact "I couldn't find that in the documents." sentence.

**B — strict + 800/150 chunks (1.5b).** Better retrieval didn't translate into
more correct answers:
- *Fixed:* Core courses (all four named), capstone alternative (correct), major
  courses (now partially right: CS101/201/302).
- *Broken:* CS311 topics answered with **CS313's** description (the two course
  descriptions are near-identical and the new boundaries put CS313 first); the
  minor question answered with the declaration rule; the credits answer invents
  "80 credits in total".
- Lesson: changing chunk boundaries perturbs the context of *every* question;
  with 25 questions, ±1 correct answer is noise.

**C — strict + 800/150 (0.5b).** The strict prompt fixes the worst 0.5b
behaviour: no invented tuition or department head, incorrect 12 → 7. But a new
failure mode appears: 9 of 25 answers start with "I couldn't find that in the
documents." and then keep going — 7 of them for questions the handbook does
answer (sometimes correctly) — it copies the
instruction's sentence instead of applying the rule. Small models follow the
*form* of instructions more than their logic.

### 9.3 What was adopted

- **Threshold fix + strict prompt** became the defaults (D-17, D-18): equal
  accuracy for 1.5b, no general-knowledge guessing, instant refusals for
  off-topic questions.
- **Chunking stays 1000/200** (D-20): no net gain from 800/150.

### 9.4 Still worth trying

1. **Structure-aware chunking** — split on headings and prefix each chunk with
   its section title, so "Major Requirements" / "Minor Requirements" travel with
   their lists. Addresses the dominant failure (§2) without tuning a number.
2. **Table rows → sentences** for the catalogue pages, e.g. "CS210 Computer
   Networks — availability: On holding; prerequisite: CS201". Targets §3.
3. **Few-shot examples in the strict prompt** showing a refusal *and* a normal
   answer, to stop 0.5b from mixing the two.
4. **A larger test set or an LLM judge** so that differences of 1–2 answers can
   be distinguished from noise.
