# Handbook chatbot evaluation

- Run: `20261114-1912-A-strict-1.5b`
- Embeddings: `nomic-embed-text`, chunk 1000/200, top-k 5, temperature 0.0, prompt `strict`, threshold 0.6, max tokens 512
- Questions: 25

| Model | Page hit | Chunk hit | Avg fact coverage | Median latency (s) | Max latency (s) | Fallbacks |
|---|---|---|---|---|---|---|
| `qwen2.5:1.5b` | 23/23 | 21/23 | 0.75 | 55.2 | 100.1 | 0 |

## Hand labels

| Model | correct | incomplete | ambiguous | incorrect |
|---|---|---|---|---|
| `qwen2.5:1.5b` | 18 | 3 | 1 | 3 |

## Answers

### `req-major-credits` — How many credits are required for the Computer Science major requirements?

*Category:* program requirements · *Expected pages:* [2, 7]

> **Reference:** The major requirements total 56 credits.

**qwen2.5:1.5b** (retrieved pages [7, 4, 7, 8, 11], hit=True, chunk_hit=True, coverage=1.0, 62.7s)

*Label: **correct** — 56 credits, with citation.*

56 credits

Source Tag: CS_MajorHandbook.pdf p.7

### `req-major-courses` — Which specific courses are required for the Computer Science major?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** CS 101 Introduction to Programming, CS 201 Data Structures & Algorithms, CS 203 Computer Organization, MATH 202 Discrete Math, three intermediate courses, CS 302 Algorithms & Theory of Computing, four advanced courses, and Capstone I and II (or two additional intermediate/advanced courses).

**qwen2.5:1.5b** (retrieved pages [7, 13, 8, 14, 4], hit=True, chunk_hit=False, coverage=0.33, 60.9s)

*Label: **incorrect** — CS101, CS201 and CS104 - CS104 is not required; misses CS203, MATH202, CS302 etc. Major-list chunk still not retrieved.*

The specific courses required for the Computer Science major are:

- Introduction to Programming (CS 101)
- Data Structures & Algorithms (CS 201)
- Introduction to Computer Science (CS 104)

These courses form the foundational structure of the major, providing students with a comprehensive understanding of computer science and its applications.

### `req-declare-major` — What do I need to complete before I can formally declare Computer Science as my major?

*Category:* academic policies · *Expected pages:* [7]

> **Reference:** At least two Computer Science courses (MATH 202 Discrete Math also counts).

**qwen2.5:1.5b** (retrieved pages [7, 4, 8, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 70.4s)

*Label: **correct** — Exact rule, no invented extras (baseline added a false 'minor requirements' condition).*

To formally declare Computer Science as your major, you must complete at least two Computer Science courses (MATH 202 - Discrete Math is also counted).

### `req-declare-minor` — How many CS courses must be completed to declare a minor in Computer Science?

*Category:* academic policies · *Expected pages:* [7]

> **Reference:** At least one Computer Science course (MATH 202 Discrete Math also counts).

**qwen2.5:1.5b** (retrieved pages [7, 11, 13, 8, 13], hit=True, chunk_hit=True, coverage=1.0, 58.0s)

*Label: **correct** — Exact rule.*

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted).

### `req-minor` — What are the requirements for a minor in Computer Science?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** 24 credits / six courses: one programming course (CS 101, CS 103 or CS 104), one 100- or 200-level CS course, CS 201 Data Structures & Algorithms, one intermediate course, one 200- or 300-level CS course, and one advanced course.

**qwen2.5:1.5b** (retrieved pages [7, 11, 4, 14, 8], hit=True, chunk_hit=True, coverage=0.33, 59.5s)

*Label: **incomplete** — Gives the declaration rule and 'six courses total' but not which courses (baseline listed all six).*

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted). The minor requires six courses total.

### `req-exploratory` — How many exploratory courses can be counted toward the major?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** Up to 2 of the 6 exploratory courses (8 credits) can be counted toward the major.

**qwen2.5:1.5b** (retrieved pages [7, 6, 7, 11, 6], hit=True, chunk_hit=True, coverage=0.5, 63.7s)

*Label: **correct** — 2 courses (terse; omits the 8 credits).*

2 courses can be counted toward the major.

### `req-core` — What are the Core courses in the general curriculum?

*Category:* program requirements · *Expected pages:* [6]

> **Reference:** Four Core courses (16 credits): Global Humanities, Modern Vietnamese Culture and Society, Design and Systems Thinking, and one QUEST course (Quantitative Reasoning, Scientific Inquiry, Programming for Data Science and Visualization, or Introduction to Statistics).

**qwen2.5:1.5b** (retrieved pages [6, 5, 8, 8, 8], hit=True, chunk_hit=False, coverage=0.0, 52.4s)

*Label: **incomplete** — Description without course names - list chunk not retrieved.*

Core courses consist of four core courses designed to ignite new ways of thinking and learning, build essential skills, and connect to Fulbright's intellectual community. These courses are taken during the first two or three semesters.

### `req-degree-name` — What degree is awarded after completing the program requirements?

*Category:* program requirements · *Expected pages:* [1, 6]

> **Reference:** A Bachelor of Science in Computer Science (B.S. Computer Science). Note: page 6 of the handbook mistakenly says "Bachelor of Science in Applied Mathematics" - a copy-paste error in the source document.

**qwen2.5:1.5b** (retrieved pages [6, 6, 5, 3, 6], hit=True, chunk_hit=True, coverage=0.0, 45.1s)

*Label: **ambiguous** — Repeats the handbook's 'Applied Mathematics' error.*

A Bachelor of Science in Applied Mathematics is awarded after completing the program requirements.

### `capstone-eligibility` — What are the eligibility requirements for the CS capstone project?

*Category:* academic policies · *Expected pages:* [9]

> **Reference:** A minimum major GPA of 3.5 and approval of a successful application (details in the Computer Science Capstone Handbook).

**qwen2.5:1.5b** (retrieved pages [9, 16, 7, 17, 4], hit=True, chunk_hit=True, coverage=1.0, 66.5s)

*Label: **correct** — GPA 3.5 + approved application.*

The eligibility criteria for enrollment in CS 401: Capstone I include a minimum major GPA of 3.5 and approval of a successful application. More detailed guidelines for the Capstone in Computer Science can be found in the Computer Science Capstone Handbook.

### `capstone-honors` — Do I have to do a capstone to graduate, and what is the alternative?

*Category:* academic policies · *Expected pages:* [7, 8]

> **Reference:** No. Doing the capstone (CS 401/402) lets students graduate with honors; the alternative is to take two more intermediate or advanced courses and graduate without honors.

**qwen2.5:1.5b** (retrieved pages [9, 8, 3, 6, 5], hit=True, chunk_hit=True, coverage=0.0, 50.4s)

*Label: **incorrect** — Claims the excerpts don't mention an alternative; the honors/two-course rule was in the retrieved text.*

No, there is no mention of a capstone requirement for graduation in the provided excerpts. The document only states that students must have a minimum major GPA of 3.5 and approval to enroll in CS 401/402: Capstone Project. It does not specify an alternative to this requirement.

### `course-advanced-list` — Can you list some of the advanced courses offered in the CS major?

*Category:* course offerings · *Expected pages:* [8, 9]

> **Reference:** Examples: Foundations of Software Engineering, Database Systems, Computer Security, Cloud Computing, Human-Computer Interaction, Computer Graphics, Game Design & Development, Machine Learning, Deep Learning, Advanced Deep Learning, Computer Vision, Natural Language Processing, Optimization, Computational Social Media, Bioinformatics.

**qwen2.5:1.5b** (retrieved pages [8, 13, 11, 7, 4], hit=True, chunk_hit=True, coverage=1.0, 59.0s)

*Label: **correct** — Clean list without the invented annotations; cites p.13 although the list is on p.8.*

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

**qwen2.5:1.5b** (retrieved pages [8, 13, 11, 8, 7], hit=True, chunk_hit=True, coverage=1.0, 59.3s)

*Label: **incomplete** — 4 of 5 - drops Introduction to Artificial Intelligence.*

The intermediate courses in the CS major are:

• Software construction
• Programming Language Paradigms
• Operating Systems
• Computer Networks

These courses cover important and basic knowledge in various aspects of computer science.

### `course-prereq-cs311` — What is the prerequisite for CS311 Advanced Deep Learning?

*Category:* course offerings · *Expected pages:* [13, 18]

> **Reference:** CS313 Deep Learning for AI (which itself requires CS208).

**qwen2.5:1.5b** (retrieved pages [18, 18, 18, 17, 16], hit=True, chunk_hit=True, coverage=1.0, 54.0s)

*Label: **correct** — CS313.*

The prerequisite for CS311 Advanced Deep Learning is CS313.

### `course-prereq-cs302` — What are the prerequisites for CS302 Algorithms & Theory of Computing?

*Category:* course offerings · *Expected pages:* [13, 17]

> **Reference:** CS201 Data Structures & Algorithms and MATH202 Discrete Math.

**qwen2.5:1.5b** (retrieved pages [17, 18, 14, 18, 12], hit=True, chunk_hit=True, coverage=1.0, 62.0s)

*Label: **correct** — CS201 and MATH 202.*

The prerequisites for CS302 Algorithms & Theory of Computing are CS201 and MATH 202.

### `course-cs201-language` — Which programming language is mainly used in CS201 Data Structures & Algorithms?

*Category:* course offerings · *Expected pages:* [14]

> **Reference:** Java (with some Python/C++ implementations also introduced).

**qwen2.5:1.5b** (retrieved pages [14, 16, 11, 15, 18], hit=True, chunk_hit=True, coverage=1.0, 51.0s)

*Label: **correct** — Java, with citation.*

Java is the main programming language used in CS201 Data Structures & Algorithms.
Source Tag: [CS_MajorHandbook.pdf p.14]

### `course-cs207-content` — What do students build in CS207 Software Construction?

*Category:* course offerings · *Expected pages:* [15]

> **Reference:** They work in teams to design software with UML (use-case, sequence and class diagrams) and implement the design by building Android applications in Java.

**qwen2.5:1.5b** (retrieved pages [15, 16, 11, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 44.3s)

*Label: **correct** — Android apps in Java, UML.*

Students build Android applications using Java to implement their design via UML models such as use-case, sequence, and class diagrams.

### `course-cs210-availability` — How often is CS210 Computer Networks offered?

*Category:* course offerings · *Expected pages:* [13]

> **Reference:** It is listed as "On holding" (not currently scheduled), prerequisite CS201.

**qwen2.5:1.5b** (retrieved pages [16, 13, 17, 13, 16], hit=True, chunk_hit=True, coverage=0.0, 55.2s)

*Label: **incorrect** — 'Once a year' - neighbouring table row, as in the baseline.*

CS210 Computer Networks is offered once a year.

### `course-cs311-topics` — What topics does the Advanced Deep Learning course cover?

*Category:* course offerings · *Expected pages:* [18]

> **Reference:** Transfer Learning, GANs, Reinforcement Learning, Attention and Transformer Networks, Graph Neural Networks, plus applications such as NLP, robotics, autonomous driving and time-series.

**qwen2.5:1.5b** (retrieved pages [18, 18, 18, 8, 16], hit=True, chunk_hit=True, coverage=1.0, 46.8s)

*Label: **correct** — All topics and applications.*

The Advanced Deep Learning course covers diverse topics including Transfer Learning, Generative Adversarial Networks (GAN), Reinforcement Learning (RL), Attention and Transformer Networks, Graph Neural Networks (GNN). It also addresses advanced applications of deep learning such as natural language processing, robotics, autonomous driving systems, time-series applications, etc.

### `outcomes-plo` — What are the program learning outcomes of the CS major?

*Category:* learning outcomes · *Expected pages:* [5, 11]

> **Reference:** PLO1: understand fundamental CS (core concepts, compare methods, solve problems in theory and systems). PLO2: explain emerging aspects of CS (AI, ML, data science, business analytics, digital media). PLO3: develop real-world applications using knowledge of CS and other disciplines.

**qwen2.5:1.5b** (retrieved pages [4, 11, 5, 12, 12], hit=True, chunk_hit=True, coverage=1.0, 100.1s)

*Label: **correct** — Core LOs and Major LOs, as in the baseline.*

The program learning outcomes of the CS major are derived from two main components:

1. **Core Learning Outcomes (Core LOs)**:
   - Students will be able to demonstrate global awareness and respect for diverse perspectives.
   - Students will be able to locate and critically analyze information and present evidence-based arguments in written and oral forms.

2. **Major Learning Outcomes (Major LOs)**:
   - Demonstrate an understanding of fundamental computer science by illustrating core concepts, comparing methods, analyzing and solving problems in both theory and systems.
   - Explain emerging aspects of the computer science discipline (e.g., artificial intelligence, machine learning, data science, business analytics, digital media, etc.).
   - Develop real-world applications (e.g., software systems and frameworks, mobile apps, data pipeline, etc.) by using knowledge of computer science and other disciplines.
   - Apply design and systems thinking processes to analyze and solve real-world problems.

These outcomes are presented in tables and mapped to the FUV Graduate Attributes.

### `outcomes-peo` — What are the Program Educational Objectives (PEOs)?

*Category:* learning outcomes · *Expected pages:* [4]

> **Reference:** PEO1: skills/knowledge for industry employment or graduate school. PEO2: professional and personal ethics, collaboration and communication. PEO3: cultivate innovators and thinkers to solve CS-related challenges.

**qwen2.5:1.5b** (retrieved pages [4, 4, 4, 4, 11], hit=True, chunk_hit=True, coverage=1.0, 54.3s)

*Label: **correct** — PEO1-3 verbatim with citation.*

PEO1. To equip students with the necessary skills and knowledge to gain employment in industry or to study in graduate schools.
PEO2. To ingrain in students a strong code of professional and personal ethics, and the ability to effectively and creatively collaborate and communicate in the workplace and beyond.
PEO3. To cultivate students to become innovators and thinkers to solve computer science related challenges.

Source: [CS_MajorHandbook.pdf p.4]

### `careers` — What jobs have Computer Science graduates gone on to?

*Category:* career paths · *Expected pages:* [5]

> **Reference:** Software engineer, testing engineer, AI engineer, data engineer, business analyst, product owner, product development manager.

**qwen2.5:1.5b** (retrieved pages [6, 5, 4, 4, 4], hit=True, chunk_hit=True, coverage=1.0, 52.5s)

*Label: **correct** — All seven roles with citation.*

Graduates with the B.S. Computer Science have successfully gained employment as:

• Software engineer
• Testing engineer
• AI engineer
• Data engineer
• Business analyst
• Product owner
• Product development manager

Source: [CS_MajorHandbook.pdf p.4]

### `grad-programs` — Which graduate programs have CS students been admitted to?

*Category:* career paths · *Expected pages:* [6]

> **Reference:** MSc/PhD Computer Science, MSc Data Science, MSc Bioinformatics (in the US and Europe).

**qwen2.5:1.5b** (retrieved pages [6, 13, 5, 4, 7], hit=True, chunk_hit=True, coverage=1.0, 51.6s)

*Label: **correct** — Right three programs.*

CS students have successfully applied to graduate programs in the United States and Europe, including:

• MSc/PhD Computer Science
• MSc Data Science
• MSc Bioinformatics

These programs are designed for graduates with a B.S. in Computer Science who aim to pursue advanced studies or careers in technology-related fields.

### `teaching-assessment` — How are students assessed in the Computer Science major?

*Category:* teaching & assessment · *Expected pages:* [12]

> **Reference:** Active and collaborative learning with continuous formative assessment (discussion, in-class activities, applied learning) plus summative methods; examples include programming tests, quizzes, exams, group presentations, class projects and the capstone.

**qwen2.5:1.5b** (retrieved pages [12, 4, 7, 12, 1], hit=True, chunk_hit=True, coverage=1.0, 56.5s)

*Label: **correct** — Formative assessment and the listed examples.*

Students are assessed through continuous formative assessment methods such as discussion, in-class activities, and applied learning. Assessment examples include programming tests, quizzes, exams, group presentations, and capstone projects.

### `oos-tuition` — How much is the tuition fee for the Computer Science program?

*Category:* out of scope · *Expected pages:* —

> **Reference:** Not stated in the handbook - the chatbot should say it does not know.

**qwen2.5:1.5b** (retrieved pages [6, 4, 7, 8, 13], hit=None, chunk_hit=None, coverage=None, 46.1s)

*Label: **correct** — Exact 'not found' sentence.*

I couldn't find that in the documents.

### `oos-department-head` — Who is the head of the Computer Science department?

*Category:* out of scope · *Expected pages:* —

> **Reference:** Not stated in the handbook - the chatbot should say it does not know.

**qwen2.5:1.5b** (retrieved pages [4, 12, 5, 6, 14], hit=None, chunk_hit=None, coverage=None, 52.8s)

*Label: **correct** — Exact 'not found' sentence.*

I couldn't find that in the documents.
