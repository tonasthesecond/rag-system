---
title: "Building and Improving a Local Retrieval-Augmented Generation System"
subtitle: "CS311 Advanced Deep Learning: Final Project Report"
author: "Doan Ngoc Khanh Quan, 240069"
date: "November 2026"
---

# 1. Introduction

Language models answer fluently, but they cannot see private documents, and when they don't know something they tend to make up a believable answer. Retrieval-Augmented Generation (RAG) helps with both problems: before the model answers, the system looks up the most relevant passages from a set of documents and gives them to the model, so the answer is based on evidence instead of memory.

This project turns the course's basic RAG script into a complete question-answering system for the Fulbright **B.S. Computer Science Major Handbook**. It runs locally on a laptop with no graphics card, using Ollama for the models, Chroma for storing the documents and a Streamlit web page for the chat. It is packaged with Docker Compose so it can be started on another machine with one command.

The work covers the four required tasks: PDF support (Task 1), a handbook chatbot with an evaluation (Task 2), Docker deployment (Task 3) and a web interface (Task 4). I also ran a few improvement experiments based on what the evaluation showed. The main findings are:

- Model size matters a lot at the small end. The middle model gave about twice as many correct answers as the smallest, and the largest added little.
- Most mistakes were the model misreading text that was found correctly. The hardest questions failed because the right text was never shown to the model, due to how the documents were cut into pieces.
- Two weaknesses inherited from the starting script caused the worst behavior of the smallest model: a safety check that never triggered, and a prompt that invited guessing.

The code, evaluation data and documentation are at **https://github.com/tonasthesecond/rag-system**

# 2. How the system works

The system has two phases. In **indexing**, the documents are read and split into small overlapping pieces called chunks. Each chunk is turned into a list of numbers (an embedding) that captures its meaning, and these are stored in a database. In **answering**, the question is turned into numbers the same way, the five closest chunks are retrieved, and a prompt is built from instructions, those chunks (labelled with file and page) and the question. The prompt is sent to the answer model.

```
PDF/TXT ─► read text ─► split into chunks ─► embed ─► Chroma database
                                                          │ best 5 chunks
question ─► embed ─► find closest chunks ─────────────────┘
                              │
        prompt (instructions + chunks + question) ─► Qwen2.5 ─► answer + cited pages
```

I used Ollama to run both the embedding model (`nomic-embed-text`) and three answer models from the same family (Qwen2.5 0.5B, 1.5B and 3B), so size is the only difference between them. The starting point was a single script, which I reorganized into a small `rag/` package shared by a command-line tool, the web page and the evaluation script. This way the system I evaluated is exactly the one people use. All settings can be changed through environment variables, which is also how Docker configures the app. Everything runs on the processor, so the models are slow, and this shaped many decisions.

# 3. Task 1: PDF support

The starting script could only read `.txt` files. I added a PDF reader, so one folder can mix both types. Three details mattered:

1. **One document per page.** Each page keeps its page number, so every answer can cite a source such as "CS_MajorHandbook.pdf p.7". This makes answers checkable and made the evaluation possible.
2. **Cleaning the text.** The PDF stores some letter pairs, like "fi", as a single special character, which the embedding model treats differently. I normalize every page so these match.
3. **Pages without text.** One page of the handbook is only an image. The loader skips such pages and reports them. Recovering them would need OCR.

I also fixed a quiet problem: the starting script reused an old database whenever its folder existed, even if the documents had changed. Databases are now stored per document set and configuration, and can be rebuilt on request.

# 4. Task 2: Handbook chatbot and evaluation

## 4.1 Method

I chose the Computer Science handbook and wrote 25 test questions after reading it fully, covering requirements, policies, course details, learning goals and careers. Two questions, about tuition and the department head, are **not answered anywhere in the handbook**, to test whether the system admits when it doesn't know. Several others were hard on purpose: the major and minor requirements sit side by side on one page, one fact appears only in a table, and one question touches a mistake in the handbook itself.

Each question has a reference answer, the page it is on and a list of key facts. I asked every question to each model with randomness switched off, then read every answer and labelled it **correct**, **incomplete** (true but missing key parts), **ambiguous** (mixes right and wrong, or repeats a mistake in the source) or **incorrect**.

## 4.2 Results

| Model | Correct | Incorrect | Speed per answer |
|---|---|---|---|
| Qwen2.5 0.5B | 9 | 12 | under half a minute |
| Qwen2.5 1.5B | 18 | 2 | under a minute |
| Qwen2.5 3B | 19 | 2 | almost two minutes |

The smallest model was fast but often wrong, and on the two unanswerable questions it invented answers. The middle model was a big improvement, and the largest added one correct answer at more than twice the waiting time. Both larger models correctly said the handbook did not contain the missing information. I made the middle model the default.

## 4.3 Examples and analysis

**Correct answers.** Simple look-ups in ordinary text worked well for the two larger models. They correctly gave the prerequisite of CS311 (CS313), the main language of CS201 (Java), what students build in CS207 (Android apps designed with UML), the rules for starting the capstone, the program's goals, career paths and graduate programs.

**Incorrect: the right text was never found.** Asked which courses the major requires, all three models described the **minor's** courses instead. The right page was retrieved, but it is split into two chunks, and the one holding the major's list starts with unrelated text, which weakens its match to the question. A neighboring chunk about declaring a major, followed by the minor's requirements, ranked much higher.

**Incomplete: only part of the answer was shown.** Asked for the Core courses, the middle and largest models said there are four and described what they are for, but named none, because the chunk with the names was not retrieved. With the strict prompt, the middle model listed only four of the five intermediate courses.

**Incorrect: tables were misread.** The PDF reader flattens tables into plain lines, away from their column headings. Asked how often CS210 is offered, the middle model said "once a year", taken from a neighboring row. The largest model quoted the table correctly ("On holding") and then said this "typically means once a year".

**Incorrect: a wrong conclusion from correct text.** The largest model quoted the rule for declaring a minor exactly ("at least one Computer Science course") and then concluded that students need seven, by adding the minor's six courses on top. My automatic score rated this answer as perfect, which shows why it cannot replace reading the answers.

**Incorrect: invented facts.** For the tuition question, the smallest model said: *"The tuition fee for the Computer Science program at Alibaba Cloud is $50,000 per year. This information can be found in the 'Major Outline' section of the CS_MajorHandbook.pdf document."* It also invented a "Professor Xie" as department head. The starting prompt tells the model to use its own knowledge when the text is not enough, and this model took that too literally.

**Ambiguous: faithful to a mistake.** The handbook says that finishing the program awards "a Bachelor of Science in Applied Mathematics", which looks copied from another handbook by accident. All three models repeated it. RAG keeps models close to the text, which reduces made-up answers but also passes along errors in the source.

The smallest model also once got stuck repeating itself for about 44 minutes, so I added a limit on answer length.

## 4.4 Improvement experiments

The analysis pointed to three fixes.

**A relevance check that works.** The starting script was meant to refuse when the retrieved text looked unrelated, but its scoring gave almost every question a similar score, even one about a pho recipe. I replaced it with a proper similarity score and chose the cutoff by testing real and unrelated questions. Clearly unrelated questions are now rejected. Questions on the same topic that the handbook doesn't answer, like tuition, still get through, so for those the system relies on the prompt.

**A strict prompt.** The new prompt tells the model to use only the given excerpts, to reply with a fixed sentence ("I couldn't find that in the documents.") when they don't contain the answer, to check that the excerpt matches what was asked (major versus minor) and to cite its sources.

**Smaller chunks.** A quick retrieval-only test showed that chunks of 800 characters found the right text for every answerable question, the original 1,000 missed two, and chunks smaller than that did worse because they separate a course's description from its code.

I then re-ran the full evaluation for three experiments: **A** changes only the prompt, **B** adds smaller chunks, and **C** is B with the smallest model.

| Run | Model | Change | Correct | Incorrect |
|---|---|---|---|---|
| Start | 1.5B | none | 18 | 2 |
| A | 1.5B | strict prompt | 18 | 3 |
| B | 1.5B | strict prompt, smaller chunks | 16 | 3 |
| Start | 0.5B | none | 9 | 12 |
| C | 0.5B | strict prompt, smaller chunks | 10 | 7 |

For the middle model, the strict prompt did not change the number of correct answers but did change the kind of mistakes: it stopped adding made-up extras, though some answers became too short. For the smallest model, it stopped the invented answers and cut incorrect answers from 12 to 7. It also revealed a new problem: in more than a third of its answers, the model wrote the "couldn't find" sentence and then answered anyway.

Smaller chunks (run B) fixed both retrieval failures but did not give more correct answers, because moving every chunk boundary changed the context for other questions. For example, the question about CS311's topics was answered with the description of CS313, a prerequisite whose description is almost identical. With only 25 questions, a difference of one or two answers says little.

I adopted the relevance fix and the strict prompt as defaults, since they keep accuracy the same while never answering from general knowledge, and I kept the original chunk size. The remaining errors seem to need bigger changes, like cutting chunks along the handbook's headings and turning tables into sentences.

# 5. Task 3: Docker deployment

The setup in `docker/docker-compose.yml` has three parts. **ollama** runs the official image, with downloaded models kept in a volume so they survive rebuilds. **ollama-init** is a one-time job that waits until Ollama is ready, downloads the needed models and exits, so a fresh machine needs only `docker compose up`. **app** is a slim Python image that runs the web page as a non-root user and starts only after the models are ready.

The documents folder is shared from the host, so new PDFs can be added without rebuilding, and the database has its own volume. I removed several heavy libraries from the course's requirement list (PyTorch, sentence-transformers and RAGAS), since Ollama already creates the embeddings, which keeps the image small.

My machine uses Podman, so I tested with `podman compose`. The files are standard Compose and work with both. The test confirmed the start-up order, that the database is built inside the container, and that questions are answered correctly through the command line and the web page.

# 6. Task 4: Web interface

The Streamlit page is a chat with the conversation above and a fixed question box below. Since answers are slow on a laptop, they are **streamed** word by word. Each answer has an expandable **sources panel** showing the cited pages, how closely each matched and the retrieved text, plus a warning if no relevant documents were found. This panel was the most useful feature during development, because it shows right away whether a wrong answer came from retrieval or from the model.

A sidebar lets the user choose the document set and model, change the main settings, upload new files, rebuild the database and clear the chat. The chat history is displayed, but each question is answered on its own. Handling follow-ups like "what does *it* cover?" needs the question to be rewritten before searching, which I list as future work.

# 7. Lessons learned

**Check retrieval in detail.** My first check counted a success whenever the right page was found, and it never failed. Looking at individual answers showed two of those successes had found the wrong chunk on that page. This changed the explanation of the hardest failures from "the model confused major and minor" to "the model was never shown the major's requirements".

**Automatic scores need a human check.** The key-fact score disagreed with my labels in both directions, rewarding a wrong conclusion built on a correct quote and penalizing correct answers with different wording. Labelling every answer by hand took time but gave most of the insight in this report.

**Inherited defaults deserve a second look.** The starting relevance check used a formula that didn't suit the embeddings, so it never triggered in any baseline answer. Nobody would have noticed without looking at the numbers behind it.

**Smaller chunks are not always better.** I expected small chunks to keep the major and minor apart, but testing showed the opposite: very small chunks cut course descriptions away from their codes.

**Plan for slow experiments.** My first full evaluation took about two hours, saved nothing until it finished and showed no progress. I changed it to save each answer as it is produced, to resume interrupted runs, and added a quick retrieval-only mode.

# 8. Limitations and future work

- **Tables and images.** Flattened tables cause most remaining factual errors. Reading tables properly, turning rows into sentences before indexing, and OCR for image pages would help.
- **Chunking.** Cutting at fixed lengths ignores the document's structure. Splitting at headings should be more reliable than tuning a size on a small test set.
- **Questions the handbook doesn't answer.** The relevance check catches clearly unrelated questions, but not on-topic ones like tuition, which depend on the model following the prompt.
- **Follow-up questions.** The chat history is not used when searching.
- **Size of the evaluation.** Twenty-five questions labelled by one person can reveal failure patterns but not small differences.
- **Hardware.** On a processor, the largest model is too slow to be practical. A graphics card would allow larger, more accurate models.

# 9. Conclusion

The project produced a working local RAG system that answers questions about the Computer Science handbook with page citations, through a command line, a web page and a reproducible container setup. The evaluation showed that the middle-sized model is the best trade-off on a laptop, that most errors come from the model misreading retrieved text, and that the remaining retrieval failures come from where the text is cut. It also exposed two problems in the starting design, an ineffective relevance check and a prompt that invites guessing, and the experiments showed what fixing them changes.

# Appendix: Reproducing the results

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

All results, including every answer, its label and the settings used, are in `source_code/eval/results/`. Note: the baseline run was made before the answer length limit and the new relevance score were added. Re-running it today applies both, so the repetition problem cannot recur and the fallback behavior may differ.
