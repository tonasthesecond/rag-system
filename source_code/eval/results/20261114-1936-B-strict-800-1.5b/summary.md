# Handbook chatbot evaluation

- Run: `20261114-1936-B-strict-800-1.5b`
- Embeddings: `nomic-embed-text`, chunk 800/150, top-k 5, temperature 0.0, prompt `strict`, threshold 0.6, max tokens 512
- Questions: 25

| Model | Page hit | Chunk hit | Avg fact coverage | Median latency (s) | Max latency (s) | Fallbacks |
|---|---|---|---|---|---|---|
| `qwen2.5:1.5b` | 23/23 | 23/23 | 0.79 | 46.5 | 72.3 | 0 |

## Hand labels

| Model | correct | incomplete | ambiguous | incorrect |
|---|---|---|---|---|
| `qwen2.5:1.5b` | 16 | 2 | 4 | 3 |

## Answers

### `req-major-credits` — How many credits are required for the Computer Science major requirements?

*Category:* program requirements · *Expected pages:* [2, 7]

> **Reference:** The major requirements total 56 credits.

**qwen2.5:1.5b** (retrieved pages [7, 7, 8, 4, 11], hit=True, chunk_hit=True, coverage=1.0, 54.4s)

*Label: **ambiguous** — Says 56, then invents a total of 80 credits (adds the minor's 24) and a 32/48 core/elective split.*

The Computer Science major requires at least **56 credits** to fulfill its requirements. This includes:

- Major Requirements (56 credits)
- Minor Requirements (24 credits)

Total required credits for the major are 80 credits, with 32 of those being core courses and 48 being electives.

### `req-major-courses` — Which specific courses are required for the Computer Science major?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** CS 101 Introduction to Programming, CS 201 Data Structures & Algorithms, CS 203 Computer Organization, MATH 202 Discrete Math, three intermediate courses, CS 302 Algorithms & Theory of Computing, four advanced courses, and Capstone I and II (or two additional intermediate/advanced courses).

**qwen2.5:1.5b** (retrieved pages [7, 13, 8, 14, 7], hit=True, chunk_hit=True, coverage=0.5, 51.9s)

*Label: **incomplete** — CS101, CS201, CS302 are right (major list now retrieved) but CS203, MATH202, intermediate/advanced courses and capstone are missing.*

The specific courses required for the Computer Science major are:

- CS 101: Introduction to Programming (4 credits)
- CS 201: Data Structures & Algorithms (4 credits)
- CS 302: Algorithms & Theory of Computing (4 credits)

These courses fulfill the core requirements of the major.

### `req-declare-major` — What do I need to complete before I can formally declare Computer Science as my major?

*Category:* academic policies · *Expected pages:* [7]

> **Reference:** At least two Computer Science courses (MATH 202 Discrete Math also counts).

**qwen2.5:1.5b** (retrieved pages [7, 7, 4, 8, 14], hit=True, chunk_hit=True, coverage=1.0, 52.8s)

*Label: **correct** — Exact rule.*

To formally declare Computer Science as your major, you must complete at least two Computer Science courses (MATH 202 - Discrete Math is also counted).

### `req-declare-minor` — How many CS courses must be completed to declare a minor in Computer Science?

*Category:* academic policies · *Expected pages:* [7]

> **Reference:** At least one Computer Science course (MATH 202 Discrete Math also counts).

**qwen2.5:1.5b** (retrieved pages [7, 11, 11, 7, 13], hit=True, chunk_hit=True, coverage=1.0, 51.4s)

*Label: **correct** — Exact rule.*

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted). This requirement ensures that the student has met the minimum qualification for declaring a minor.

### `req-minor` — What are the requirements for a minor in Computer Science?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** 24 credits / six courses: one programming course (CS 101, CS 103 or CS 104), one 100- or 200-level CS course, CS 201 Data Structures & Algorithms, one intermediate course, one 200- or 300-level CS course, and one advanced course.

**qwen2.5:1.5b** (retrieved pages [7, 7, 11, 8, 4], hit=True, chunk_hit=True, coverage=0.0, 47.3s)

*Label: **incorrect** — Answers how to DECLARE a minor instead of the minor's requirements.*

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted).

### `req-exploratory` — How many exploratory courses can be counted toward the major?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** Up to 2 of the 6 exploratory courses (8 credits) can be counted toward the major.

**qwen2.5:1.5b** (retrieved pages [7, 6, 11, 7, 6], hit=True, chunk_hit=True, coverage=1.0, 47.8s)

*Label: **correct** — Up to 2 courses (8 credits).*

According to the document excerpts, up to 2 courses (8 credits) can be counted toward the major from the three categories of E1-Arts and Humanities, E2-Social Sciences, and STEM.

### `req-core` — What are the Core courses in the general curriculum?

*Category:* program requirements · *Expected pages:* [6]

> **Reference:** Four Core courses (16 credits): Global Humanities, Modern Vietnamese Culture and Society, Design and Systems Thinking, and one QUEST course (Quantitative Reasoning, Scientific Inquiry, Programming for Data Science and Visualization, or Introduction to Statistics).

**qwen2.5:1.5b** (retrieved pages [6, 5, 6, 8, 6], hit=True, chunk_hit=True, coverage=1.0, 47.7s)

*Label: **correct** — All four Core courses - fixed by 800-char chunks (list chunk now retrieved).*

The Core courses in the general curriculum are:

- Global Humanities
- Modern Vietnamese Culture and Society
- Design and Systems Thinking
- Quantitative Understanding and Empirical Scientific Thinking (QUEST)

These four courses provide foundational knowledge across different areas of study.

### `req-degree-name` — What degree is awarded after completing the program requirements?

*Category:* program requirements · *Expected pages:* [1, 6]

> **Reference:** A Bachelor of Science in Computer Science (B.S. Computer Science). Note: page 6 of the handbook mistakenly says "Bachelor of Science in Applied Mathematics" - a copy-paste error in the source document.

**qwen2.5:1.5b** (retrieved pages [6, 5, 6, 5, 3], hit=True, chunk_hit=True, coverage=0.0, 37.6s)

*Label: **ambiguous** — Repeats the handbook's 'Applied Mathematics' error.*

A Bachelor of Science in Applied Mathematics is awarded after completing the program requirements.

### `capstone-eligibility` — What are the eligibility requirements for the CS capstone project?

*Category:* academic policies · *Expected pages:* [9]

> **Reference:** A minimum major GPA of 3.5 and approval of a successful application (details in the Computer Science Capstone Handbook).

**qwen2.5:1.5b** (retrieved pages [9, 7, 16, 17, 15], hit=True, chunk_hit=True, coverage=1.0, 45.9s)

*Label: **correct** — GPA 3.5 + approved application.*

The eligibility criteria for enrollment in CS 401: Capstone I include a minimum major GPA of 3.5 and approval of a successful application. More detailed guidelines for the Capstone in Computer Science can be found in the Computer Science Capstone Handbook.

### `capstone-honors` — Do I have to do a capstone to graduate, and what is the alternative?

*Category:* academic policies · *Expected pages:* [7, 8]

> **Reference:** No. Doing the capstone (CS 401/402) lets students graduate with honors; the alternative is to take two more intermediate or advanced courses and graduate without honors.

**qwen2.5:1.5b** (retrieved pages [8, 9, 3, 2, 5], hit=True, chunk_hit=True, coverage=1.0, 39.8s)

*Label: **correct** — Not required; two more intermediate/advanced courses, graduate without honors.*

No, you do not have to do a capstone to graduate. Instead, students can choose to complete two more intermediate or advanced courses to graduate without honors.

### `course-advanced-list` — Can you list some of the advanced courses offered in the CS major?

*Category:* course offerings · *Expected pages:* [8, 9]

> **Reference:** Examples: Foundations of Software Engineering, Database Systems, Computer Security, Cloud Computing, Human-Computer Interaction, Computer Graphics, Game Design & Development, Machine Learning, Deep Learning, Advanced Deep Learning, Computer Vision, Natural Language Processing, Optimization, Computational Social Media, Bioinformatics.

**qwen2.5:1.5b** (retrieved pages [8, 13, 11, 7, 8], hit=True, chunk_hit=True, coverage=1.0, 47.7s)

*Label: **correct** — Clean list; cites p.13 although the list is on p.8.*

Advanced Courses:
• Foundations of Software Engineering
• Database Systems
• Computer Security
• Cloud Computing
• Human-Computer Interaction
• Computer Graphics
• Game Design & Development
• Machine Learning
• Deep Learning
• Advanced Deep Learning
• Computer Vision
• Natural Language Processing
• Optimization
• Computational Social Media

Source: [CS_MajorHandbook.pdf p.13]

### `course-intermediate-list` — What are the intermediate courses in the CS major?

*Category:* course offerings · *Expected pages:* [8]

> **Reference:** Sample intermediate courses: Software Construction, Programming Language Paradigms, Operating Systems, Computer Networks, Introduction to Artificial Intelligence.

**qwen2.5:1.5b** (retrieved pages [8, 13, 11, 11, 8], hit=True, chunk_hit=True, coverage=1.0, 38.8s)

*Label: **incomplete** — 4 of 5 - drops Introduction to Artificial Intelligence.*

The intermediate courses in the CS major are:

• Software construction
• Programming Language Paradigms
• Operating Systems
• Computer Networks

These courses provide foundational knowledge across various aspects of computer science.

### `course-prereq-cs311` — What is the prerequisite for CS311 Advanced Deep Learning?

*Category:* course offerings · *Expected pages:* [13, 18]

> **Reference:** CS313 Deep Learning for AI (which itself requires CS208).

**qwen2.5:1.5b** (retrieved pages [18, 18, 18, 17, 16], hit=True, chunk_hit=True, coverage=1.0, 44.4s)

*Label: **correct** — CS313.*

The prerequisite for CS311 Advanced Deep Learning is CS313.

### `course-prereq-cs302` — What are the prerequisites for CS302 Algorithms & Theory of Computing?

*Category:* course offerings · *Expected pages:* [13, 17]

> **Reference:** CS201 Data Structures & Algorithms and MATH202 Discrete Math.

**qwen2.5:1.5b** (retrieved pages [17, 12, 18, 18, 14], hit=True, chunk_hit=True, coverage=1.0, 52.6s)

*Label: **correct** — CS201 and MATH 202.*

The prerequisites for CS302 Algorithms & Theory of Computing are CS201 and MATH 202.

### `course-cs201-language` — Which programming language is mainly used in CS201 Data Structures & Algorithms?

*Category:* course offerings · *Expected pages:* [14]

> **Reference:** Java (with some Python/C++ implementations also introduced).

**qwen2.5:1.5b** (retrieved pages [14, 16, 11, 15, 18], hit=True, chunk_hit=True, coverage=1.0, 46.2s)

*Label: **correct** — Java.*

Java is the main programming language used in CS201 Data Structures & Algorithms.

### `course-cs207-content` — What do students build in CS207 Software Construction?

*Category:* course offerings · *Expected pages:* [15]

> **Reference:** They work in teams to design software with UML (use-case, sequence and class diagrams) and implement the design by building Android applications in Java.

**qwen2.5:1.5b** (retrieved pages [15, 16, 13, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 46.5s)

*Label: **correct** — Android apps in Java, UML.*

Students build Android applications using Java to implement their design via UML models such as use-case, sequence, and class diagrams.

### `course-cs210-availability` — How often is CS210 Computer Networks offered?

*Category:* course offerings · *Expected pages:* [13]

> **Reference:** It is listed as "On holding" (not currently scheduled), prerequisite CS201.

**qwen2.5:1.5b** (retrieved pages [16, 13, 17, 13, 16], hit=True, chunk_hit=True, coverage=0.0, 51.9s)

*Label: **incorrect** — 'Once a year' - neighbouring table row.*

CS210 Computer Networks is offered once a year.

### `course-cs311-topics` — What topics does the Advanced Deep Learning course cover?

*Category:* course offerings · *Expected pages:* [18]

> **Reference:** Transfer Learning, GANs, Reinforcement Learning, Attention and Transformer Networks, Graph Neural Networks, plus applications such as NLP, robotics, autonomous driving and time-series.

**qwen2.5:1.5b** (retrieved pages [18, 18, 18, 18, 15], hit=True, chunk_hit=True, coverage=0.25, 37.8s)

*Label: **incorrect** — Gives CS313 Deep Learning for AI's topics (data augmentation, RNNs). The two descriptions are near-identical; new chunk boundaries put CS313's text first.*

The Advanced Deep Learning course covers topics including introductive deep learning, popular deep neural networks, data augmentation, transfer learning, and recurrent neural networks. It also addresses advanced applications of deep learning such as natural language processing, robotics, autonomous driving systems, time-series applications, etc.

### `outcomes-plo` — What are the program learning outcomes of the CS major?

*Category:* learning outcomes · *Expected pages:* [5, 11]

> **Reference:** PLO1: understand fundamental CS (core concepts, compare methods, solve problems in theory and systems). PLO2: explain emerging aspects of CS (AI, ML, data science, business analytics, digital media). PLO3: develop real-world applications using knowledge of CS and other disciplines.

**qwen2.5:1.5b** (retrieved pages [4, 5, 12, 11, 11], hit=True, chunk_hit=True, coverage=0.33, 72.3s)

*Label: **ambiguous** — Mixes lists: presents Core LO 3 ('formulate quantitative inquiries') as a Major LO.*

**Program Learning Outcomes**

The Computer Science (CS) major aims to educate students with foundational knowledge and skills in computer science and relevant disciplines. These outcomes are derived from two main components of the curriculum:

1. **Core Learning Outcomes (Core LOs)**:
   - Students will be able to demonstrate global awareness and respect for diverse perspectives.
   - They will be able to locate and critically analyze information and present evidence-based arguments in written and oral forms.

2. **Major Learning Outcomes (Major LOs)**:
   - Students will be able to formulate quantitative inquiries and solve problems using both theory and systems.
   - They will explain emerging aspects of the computer science discipline, including artificial intelligence, machine learning, data science, business analytics, digital media, etc.

These outcomes are mapped to FUV Graduate Attributes (GA1-9) and include skills such as critical thinking, communication, problem-solving, and global awareness.

### `outcomes-peo` — What are the Program Educational Objectives (PEOs)?

*Category:* learning outcomes · *Expected pages:* [4]

> **Reference:** PEO1: skills/knowledge for industry employment or graduate school. PEO2: professional and personal ethics, collaboration and communication. PEO3: cultivate innovators and thinkers to solve CS-related challenges.

**qwen2.5:1.5b** (retrieved pages [4, 4, 4, 4, 5], hit=True, chunk_hit=True, coverage=1.0, 43.3s)

*Label: **correct** — PEO1-3 verbatim.*

PEO1. To equip students with the necessary skills and knowledge to gain employment in industry or to study in graduate schools.
PEO2. To ingrain in students a strong code of professional and personal ethics, and the ability to effectively and creatively collaborate and communicate in the workplace and beyond.
PEO3. To cultivate students to become innovators and thinkers to solve computer science related challenges.

### `careers` — What jobs have Computer Science graduates gone on to?

*Category:* career paths · *Expected pages:* [5]

> **Reference:** Software engineer, testing engineer, AI engineer, data engineer, business analyst, product owner, product development manager.

**qwen2.5:1.5b** (retrieved pages [5, 6, 5, 4, 4], hit=True, chunk_hit=True, coverage=1.0, 40.3s)

*Label: **correct** — All seven roles.*

Computer Science graduates have successfully gained employment as software engineers, testing engineers, AI engineers, data engineers, business analysts, product owners, and product development managers.

### `grad-programs` — Which graduate programs have CS students been admitted to?

*Category:* career paths · *Expected pages:* [6]

> **Reference:** MSc/PhD Computer Science, MSc Data Science, MSc Bioinformatics (in the US and Europe).

**qwen2.5:1.5b** (retrieved pages [6, 13, 5, 5, 4], hit=True, chunk_hit=True, coverage=1.0, 38.6s)

*Label: **correct** — Right three programs.*

CS students have successfully applied to graduate programs in the United States and Europe, including:

• MSc/PhD Computer Science
• MSc Data Science
• MSc Bioinformatics

### `teaching-assessment` — How are students assessed in the Computer Science major?

*Category:* teaching & assessment · *Expected pages:* [12]

> **Reference:** Active and collaborative learning with continuous formative assessment (discussion, in-class activities, applied learning) plus summative methods; examples include programming tests, quizzes, exams, group presentations, class projects and the capstone.

**qwen2.5:1.5b** (retrieved pages [12, 4, 12, 1, 7], hit=True, chunk_hit=True, coverage=1.0, 49.7s)

*Label: **ambiguous** — Right, but wrongly adds that summative assessment is not specified.*

Students are assessed through continuous formative assessment methods such as discussion, in-class activities, and applied learning. Assessment examples include programming tests, quizzes, exams, group presentations, and capstone projects. The document does not specify summative assessments but mentions that teaching and assessment principles emphasize active and collaborative learning.

Source tags: [CS_MajorHandbook.pdf p.12], [CS_MajorHandbook.pdf p.4]

### `oos-tuition` — How much is the tuition fee for the Computer Science program?

*Category:* out of scope · *Expected pages:* —

> **Reference:** Not stated in the handbook - the chatbot should say it does not know.

**qwen2.5:1.5b** (retrieved pages [6, 13, 8, 4, 14], hit=None, chunk_hit=None, coverage=None, 40.3s)

*Label: **correct** — Exact 'not found' sentence.*

I couldn't find that in the documents.

### `oos-department-head` — Who is the head of the Computer Science department?

*Category:* out of scope · *Expected pages:* —

> **Reference:** Not stated in the handbook - the chatbot should say it does not know.

**qwen2.5:1.5b** (retrieved pages [4, 6, 5, 4, 13], hit=None, chunk_hit=None, coverage=None, 37.1s)

*Label: **correct** — Exact 'not found' sentence.*

I couldn't find that in the documents.
