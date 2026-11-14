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

## 8. System-level observations

- **The fallback branch is dead code** with these embeddings (DECISIONS D-17):
  0 fallbacks in 75 answers; an off-topic question still scores 0.49 against a
  threshold of 0.3.
- **The prompt permits guessing** ("use your general knowledge", D-18). Larger
  models ignored that and declined; 0.5b took it literally.
- **Latency is dominated by prompt processing on CPU**: ~5,000 characters of
  context per question. Fewer/shorter chunks would speed things up at some
  recall risk.

## 9. Improvement experiments worth running next

Each is one config/prompt change plus one evaluation run (use 1.5b to keep it
~20 min), and gives a before/after table for the report:

1. **Strict prompt** — answer only from context, say "not in the handbook"
   otherwise, cite pages. Expect: 0.5b stops hallucinating; maybe fewer padded answers.
2. **Fix the threshold** (cosine space, threshold ~0.55). Expect: out-of-scope
   questions hit the fallback.
3. **Smaller chunks** (e.g. 500/100). Expect: less major/minor mixing; risk of
   splitting lists.
4. **Table rows → sentences** for the catalogue pages. Expect: CS210 fixed.
