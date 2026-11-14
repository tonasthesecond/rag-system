# Handbook chatbot evaluation

- Run: `20261114-1955-C-strict-800-0.5b`
- Embeddings: `nomic-embed-text`, chunk 800/150, top-k 5, temperature 0.0, prompt `strict`, threshold 0.6, max tokens 512
- Questions: 25

| Model | Page hit | Chunk hit | Avg fact coverage | Median latency (s) | Max latency (s) | Fallbacks |
|---|---|---|---|---|---|---|
| `qwen2.5:0.5b` | 23/23 | 23/23 | 0.59 | 21.8 | 47.9 | 0 |

## Hand labels

| Model | correct | incomplete | ambiguous | incorrect |
|---|---|---|---|---|
| `qwen2.5:0.5b` | 10 | 0 | 8 | 7 |

## Answers

### `req-major-credits` — How many credits are required for the Computer Science major requirements?

*Category:* program requirements · *Expected pages:* [2, 7]

> **Reference:** The major requirements total 56 credits.

**qwen2.5:0.5b** (retrieved pages [7, 7, 8, 4, 11], hit=True, chunk_hit=True, coverage=0.0, 30.5s)

*Label: **incorrect** — 'Couldn't find' + the major-declaration rule; never says 56.*

I couldn't find that in the documents.
The Computer Science major requires students to complete at least two computer science courses (MATH 202 - Discrete Math is also counted).

### `req-major-courses` — Which specific courses are required for the Computer Science major?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** CS 101 Introduction to Programming, CS 201 Data Structures & Algorithms, CS 203 Computer Organization, MATH 202 Discrete Math, three intermediate courses, CS 302 Algorithms & Theory of Computing, four advanced courses, and Capstone I and II (or two additional intermediate/advanced courses).

**qwen2.5:0.5b** (retrieved pages [7, 13, 8, 14, 7], hit=True, chunk_hit=True, coverage=0.17, 28.9s)

*Label: **incorrect** — Gives the declaration rule instead of the course list.*

To formally declare Computer Science as their major, the student must complete at least two Computer Science courses (MATH 202 - Discrete Math is also counted).

### `req-declare-major` — What do I need to complete before I can formally declare Computer Science as my major?

*Category:* academic policies · *Expected pages:* [7]

> **Reference:** At least two Computer Science courses (MATH 202 Discrete Math also counts).

**qwen2.5:0.5b** (retrieved pages [7, 7, 4, 8, 14], hit=True, chunk_hit=True, coverage=0.5, 24.1s)

*Label: **ambiguous** — 'At least two CS courses' is right, but it names them as CS101 and CS203 and adds invented steps.*

To formally declare Computer Science as your major, you must complete at least two computer science courses (CS 101 - Introduction to Programming and CS 203 - Computer Organization). You can take one programming course (e.g., CS 104) or a data structures & algorithms course (e.g., CS 201), and then choose three intermediate courses that cover the major aspects in computer science. After completing these courses, you will have flexibility to select four elective advanced courses to explore your areas of interest deeper.

### `req-declare-minor` — How many CS courses must be completed to declare a minor in Computer Science?

*Category:* academic policies · *Expected pages:* [7]

> **Reference:** At least one Computer Science course (MATH 202 Discrete Math also counts).

**qwen2.5:0.5b** (retrieved pages [7, 11, 11, 7, 13], hit=True, chunk_hit=True, coverage=0.0, 21.8s)

*Label: **incorrect** — Says two courses (it's one) - copied from the major rule.*

To declare a minor in Computer Science, students must complete at least two computer science courses (MATH 202 - Discrete Math is also counted).

### `req-minor` — What are the requirements for a minor in Computer Science?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** 24 credits / six courses: one programming course (CS 101, CS 103 or CS 104), one 100- or 200-level CS course, CS 201 Data Structures & Algorithms, one intermediate course, one 200- or 300-level CS course, and one advanced course.

**qwen2.5:0.5b** (retrieved pages [7, 7, 11, 8, 4], hit=True, chunk_hit=True, coverage=0.67, 31.4s)

*Label: **ambiguous** — Says 'couldn't find', then dumps a partly wrong list (two intermediate courses, CS201 missing) and table fragments.*

I couldn't find that in the documents.
Minor Requirements:
The minor requires students to take a total of six courses:

• One programming course (4 credits)
• One 100-level or 200-level CS course (4 credits)
• Two intermediate courses (4 credits)
• One 200-level or 300-level CS course (4 credits)
• One advanced course (4 credits)

Major Requirements:
To formally declare a minor in Computer Science, the student must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted).

Sample Minor Plan:
Year 1 Year 2 Year 3 Year 4
Core Curriculum
Introduction to CS
1 Major course
2 ELECTIVES
Computer Science I
Computer Science II
3 Major courses
3 ELECTIVES
Intermediate CS course
Intermediate CS course
5 Major courses
1 ELECTIVES
Advanced CS course
5 Major courses
2 ELECTIVES

### `req-exploratory` — How many exploratory courses can be counted toward the major?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** Up to 2 of the 6 exploratory courses (8 credits) can be counted toward the major.

**qwen2.5:0.5b** (retrieved pages [7, 6, 11, 7, 6], hit=True, chunk_hit=True, coverage=0.5, 16.0s)

*Label: **correct** — 2 courses.*

2 courses

### `req-core` — What are the Core courses in the general curriculum?

*Category:* program requirements · *Expected pages:* [6]

> **Reference:** Four Core courses (16 credits): Global Humanities, Modern Vietnamese Culture and Society, Design and Systems Thinking, and one QUEST course (Quantitative Reasoning, Scientific Inquiry, Programming for Data Science and Visualization, or Introduction to Statistics).

**qwen2.5:0.5b** (retrieved pages [6, 5, 6, 8, 6], hit=True, chunk_hit=True, coverage=1.0, 19.9s)

*Label: **ambiguous** — Right names but lists six 'Core courses' - the QUEST options shown as separate Core courses.*

Core courses in the general curriculum include:

1. Global Humanities
2. Modern Vietnamese Culture and Society
3. Design and Systems Thinking
4. Quantitative Understanding and Empirical Scientific Thinking (QUEST)
5. Programming for Data Science and Visualization
6. Introduction to Statistics

These core courses serve as the foundation of American liberal arts education, igniting new ways of thinking and learning, building essential skills, and connecting to Fulbright’s intellectual community.

### `req-degree-name` — What degree is awarded after completing the program requirements?

*Category:* program requirements · *Expected pages:* [1, 6]

> **Reference:** A Bachelor of Science in Computer Science (B.S. Computer Science). Note: page 6 of the handbook mistakenly says "Bachelor of Science in Applied Mathematics" - a copy-paste error in the source document.

**qwen2.5:0.5b** (retrieved pages [6, 5, 6, 5, 3], hit=True, chunk_hit=True, coverage=0.0, 26.7s)

*Label: **ambiguous** — Repeats the handbook's 'Applied Mathematics' error.*

Bachelor of Science in Applied Mathematics

### `capstone-eligibility` — What are the eligibility requirements for the CS capstone project?

*Category:* academic policies · *Expected pages:* [9]

> **Reference:** A minimum major GPA of 3.5 and approval of a successful application (details in the Computer Science Capstone Handbook).

**qwen2.5:0.5b** (retrieved pages [9, 7, 16, 17, 15], hit=True, chunk_hit=True, coverage=0.0, 30.1s)

*Label: **incorrect** — Dumps the major requirements list instead.*

• Major Requirements (56 credits)
• CS 101: Introduction to Programming (4 credits)
• CS 201: Data Structures & Algorithms (4 credits)
• CS 203: Computer Organization (4 credits)
• MATH 202: Discrete Math (4 credits)
• Three intermediate courses (12 credits)
• CS 302: Algorithms & Theory of Computing (4 credits)
• Four advanced courses (16 credits)
• Capstone I and Capstone II (8 credits)
OR two additional intermediate courses (8 credits)
OR two additional advanced courses (8 credits)
OR an additional intermediate course and an additional advanced course (8 credits)

### `capstone-honors` — Do I have to do a capstone to graduate, and what is the alternative?

*Category:* academic policies · *Expected pages:* [7, 8]

> **Reference:** No. Doing the capstone (CS 401/402) lets students graduate with honors; the alternative is to take two more intermediate or advanced courses and graduate without honors.

**qwen2.5:0.5b** (retrieved pages [8, 9, 3, 2, 5], hit=True, chunk_hit=True, coverage=0.0, 26.4s)

*Label: **incorrect** — 'Couldn't find' followed by unrelated text about foundational courses.*

I couldn't find that in the documents.
Flexibility in their choice of four elective advanced courses to explore their areas of interest deeper is one of the Founda’onal Courses. Students can choose from Introduction to Programming, Data Structures & Algorithms, Computer Organization, Discrete Mathematics, and Algorithms & Theory of Computing.

### `course-advanced-list` — Can you list some of the advanced courses offered in the CS major?

*Category:* course offerings · *Expected pages:* [8, 9]

> **Reference:** Examples: Foundations of Software Engineering, Database Systems, Computer Security, Cloud Computing, Human-Computer Interaction, Computer Graphics, Game Design & Development, Machine Learning, Deep Learning, Advanced Deep Learning, Computer Vision, Natural Language Processing, Optimization, Computational Social Media, Bioinformatics.

**qwen2.5:0.5b** (retrieved pages [8, 13, 11, 7, 8], hit=True, chunk_hit=True, coverage=1.0, 17.5s)

*Label: **correct** — Clean list.*

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

### `course-intermediate-list` — What are the intermediate courses in the CS major?

*Category:* course offerings · *Expected pages:* [8]

> **Reference:** Sample intermediate courses: Software Construction, Programming Language Paradigms, Operating Systems, Computer Networks, Introduction to Artificial Intelligence.

**qwen2.5:0.5b** (retrieved pages [8, 13, 11, 11, 8], hit=True, chunk_hit=True, coverage=1.0, 16.2s)

*Label: **correct** — All five.*

Intermediate Courses:
• Software construction
• Programming Language Paradigms
• Operating Systems
• Computer Networks
• Introduction to Artificial Intelligence

### `course-prereq-cs311` — What is the prerequisite for CS311 Advanced Deep Learning?

*Category:* course offerings · *Expected pages:* [13, 18]

> **Reference:** CS313 Deep Learning for AI (which itself requires CS208).

**qwen2.5:0.5b** (retrieved pages [18, 18, 18, 17, 16], hit=True, chunk_hit=True, coverage=1.0, 19.8s)

*Label: **correct** — CS313.*

The prerequisite for CS311 Advanced Deep Learning is CS313.

### `course-prereq-cs302` — What are the prerequisites for CS302 Algorithms & Theory of Computing?

*Category:* course offerings · *Expected pages:* [13, 17]

> **Reference:** CS201 Data Structures & Algorithms and MATH202 Discrete Math.

**qwen2.5:0.5b** (retrieved pages [17, 12, 18, 18, 14], hit=True, chunk_hit=True, coverage=1.0, 26.0s)

*Label: **correct** — CS201 and MATH 202 (baseline 0.5b missed this).*

The prerequisites for CS302 Algorithms & Theory of Computing are CS201 and MATH 202.

### `course-cs201-language` — Which programming language is mainly used in CS201 Data Structures & Algorithms?

*Category:* course offerings · *Expected pages:* [14]

> **Reference:** Java (with some Python/C++ implementations also introduced).

**qwen2.5:0.5b** (retrieved pages [14, 16, 11, 15, 18], hit=True, chunk_hit=True, coverage=1.0, 22.8s)

*Label: **correct** — Java plus some Python/C++.*

Java is the main programming language used in the course, but some Python/C++ implementations are also introduced.

### `course-cs207-content` — What do students build in CS207 Software Construction?

*Category:* course offerings · *Expected pages:* [15]

> **Reference:** They work in teams to design software with UML (use-case, sequence and class diagrams) and implement the design by building Android applications in Java.

**qwen2.5:0.5b** (retrieved pages [15, 16, 13, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 41.6s)

*Label: **correct** — Android apps in Java.*

Students build Android applications using Java in CS207 Software Construction.

### `course-cs210-availability` — How often is CS210 Computer Networks offered?

*Category:* course offerings · *Expected pages:* [13]

> **Reference:** It is listed as "On holding" (not currently scheduled), prerequisite CS201.

**qwen2.5:0.5b** (retrieved pages [16, 13, 17, 13, 16], hit=True, chunk_hit=True, coverage=0.0, 25.2s)

*Label: **incorrect** — 'Couldn't find', then 'offered on a yearly basis'.*

I couldn't find that in the documents.
The course is offered on a yearly basis and does not have a specific frequency mentioned.

### `course-cs311-topics` — What topics does the Advanced Deep Learning course cover?

*Category:* course offerings · *Expected pages:* [18]

> **Reference:** Transfer Learning, GANs, Reinforcement Learning, Attention and Transformer Networks, Graph Neural Networks, plus applications such as NLP, robotics, autonomous driving and time-series.

**qwen2.5:0.5b** (retrieved pages [18, 18, 18, 18, 15], hit=True, chunk_hit=True, coverage=0.0, 18.5s)

*Label: **incorrect** — Copies a fragment of the CS208/CS307 machine-learning description.*

Decision Tree, Random Forest, Support Vector Machine, Deep Neural Network); unsupervised learning (K-means clustering, Hierarchical clustering). The course will also discuss recent applications of machine learning, such as to robotics, autonomous driving systems, face and speech recognition, text and web data processing, etc.

### `outcomes-plo` — What are the program learning outcomes of the CS major?

*Category:* learning outcomes · *Expected pages:* [5, 11]

> **Reference:** PLO1: understand fundamental CS (core concepts, compare methods, solve problems in theory and systems). PLO2: explain emerging aspects of CS (AI, ML, data science, business analytics, digital media). PLO3: develop real-world applications using knowledge of CS and other disciplines.

**qwen2.5:0.5b** (retrieved pages [4, 5, 12, 11, 11], hit=True, chunk_hit=True, coverage=1.0, 47.9s)

*Label: **ambiguous** — 'Couldn't find', then the three PLOs correctly plus an invented fourth.*

I couldn't find that in the documents.
Program Learning Outcomes of the CS Major:

1. Demonstrate an understanding of fundamental computer science by illustrating core concepts, comparing methods, analyzing and solving problems in both theory and systems.
2. Explain emerging aspects of the computer science discipline (e.g., artificial intelligence, machine learning, data science, business analytics, digital media, etc.).
3. Develop real-world applications (e.g., software systems and frameworks, mobile apps, data pipeline, etc.) by using knowledge of computer science and other disciplines.
4. Apply theoretical concepts to practical problems in various fields such as data analysis, artificial intelligence, machine learning, and business analytics.

The program learning outcomes are derived from the two main components of the curriculum: the Core Curriculum and the Major Curriculum. They consist of Core Learning Outcomes (Core LOs) and Major Learning Outcomes (Major LOs). These outcomes are presented in the following tables and are also mapped to the FUV Graduate Attributes.
Short Name Core LOs FUV Graduate
Attribute
CoreLO 1 Students will be able to demonstrate global awareness and respect for diverse perspectives.
GA1, GA3, GA8
CoreLO 2 Students will be able to locate and critically analyze information and present evidence-based arguments in written and oral forms.
GA1, GA4, GA5,
GA6, GA7, GA9
AvaiCoreLO 3 Students will be able to formulate quantitative inquiries and solve problems using mathematical models.
GA1, GA2, GA3, GA4, GA5, GA6, GA7, GA8, GA9, GA10, GA11, GA12, GA13, GA14, GA15
AvaiCoreLO 4 Students will be able to analyze and evaluate data using statistical methods.
GA1, GA2, GA3, GA4, GA5, GA6, GA7, GA8, GA9, GA10, GA11, GA12, GA13, GA14, GA15
AvaiCoreLO 5 Students will be able to design and implement algorithms for solving problems.
GA1, GA2, GA3, GA4, GA5, GA6, GA7, GA8, GA9, GA10, GA11, GA12, GA13, GA14, GA15
AvaiCoreLO 6 Students will be able to use software tools and platforms for data

### `outcomes-peo` — What are the Program Educational Objectives (PEOs)?

*Category:* learning outcomes · *Expected pages:* [4]

> **Reference:** PEO1: skills/knowledge for industry employment or graduate school. PEO2: professional and personal ethics, collaboration and communication. PEO3: cultivate innovators and thinkers to solve CS-related challenges.

**qwen2.5:0.5b** (retrieved pages [4, 4, 4, 4, 5], hit=True, chunk_hit=True, coverage=0.67, 18.3s)

*Label: **ambiguous** — Loose paraphrase of the PEOs mixed with invented 'Computer Science I-IV' courses.*

Program Educational Objectives (PEOs): The Computer Science major at Fulbright is designed to prepare students for work in industry or continue their lifelong learning as well as potential graduate-level studies. It aims to equip students with necessary skills and knowledge to gain employment in the technology economy, solve computer science-related challenges, and become innovators and thinkers who can address global issues through innovative solutions. The major curriculum includes core courses such as Computer Science I, II, III, and IV, along with elective courses in areas like Artificial Intelligence, Machine Learning, Data Science, Business Analytics, and more. Students will be exposed to a student-centered, interdisciplinary, and future-focused approach to education, fostering their ability to collaborate effectively and communicate across different disciplines.

### `careers` — What jobs have Computer Science graduates gone on to?

*Category:* career paths · *Expected pages:* [5]

> **Reference:** Software engineer, testing engineer, AI engineer, data engineer, business analyst, product owner, product development manager.

**qwen2.5:0.5b** (retrieved pages [5, 6, 5, 4, 4], hit=True, chunk_hit=True, coverage=1.0, 16.5s)

*Label: **correct** — All seven roles.*

Graduates with the B.S. Computer Science have successfully gained employment as:

• Software engineer
• Testing engineer
• AI engineer
• Data engineer
• Business analyst
• Product owner
• Product development manager

These positions are typical for graduates of a B.S. Computer Science program, which prepares students with an adaptable skill set to respond to the speed of technological change and develop solutions for the problems of today and tomorrow.

### `grad-programs` — Which graduate programs have CS students been admitted to?

*Category:* career paths · *Expected pages:* [6]

> **Reference:** MSc/PhD Computer Science, MSc Data Science, MSc Bioinformatics (in the US and Europe).

**qwen2.5:0.5b** (retrieved pages [6, 13, 5, 5, 4], hit=True, chunk_hit=True, coverage=1.0, 12.6s)

*Label: **ambiguous** — 'Couldn't find', then the correct three programs.*

I couldn't find that in the documents.
MSc/PhD Computer Science
MSc Data Science
MSc Bioinformatics

### `teaching-assessment` — How are students assessed in the Computer Science major?

*Category:* teaching & assessment · *Expected pages:* [12]

> **Reference:** Active and collaborative learning with continuous formative assessment (discussion, in-class activities, applied learning) plus summative methods; examples include programming tests, quizzes, exams, group presentations, class projects and the capstone.

**qwen2.5:0.5b** (retrieved pages [12, 4, 12, 1, 7], hit=True, chunk_hit=True, coverage=1.0, 17.6s)

*Label: **ambiguous** — 'Couldn't find', then a correct summary.*

I couldn't find that in the documents.
Students are assessed through continuous formative assessment of student learning through discussion (instructor-led and student-led), in-class activities, and applied learning. They also receive quizzes, exams, group presentations, capstone projects, and field trips to demonstrate their understanding of fundamental computer science concepts.

### `oos-tuition` — How much is the tuition fee for the Computer Science program?

*Category:* out of scope · *Expected pages:* —

> **Reference:** Not stated in the handbook - the chatbot should say it does not know.

**qwen2.5:0.5b** (retrieved pages [6, 13, 8, 4, 14], hit=None, chunk_hit=None, coverage=None, 17.7s)

*Label: **correct** — Declines (baseline 0.5b invented $50,000 'at Alibaba Cloud').*

I couldn't find that in the documents.
The excerpt does not provide information about tuition fees for Computer Science programs. Therefore, I cannot accurately answer this question based on the given excerpts.

### `oos-department-head` — Who is the head of the Computer Science department?

*Category:* out of scope · *Expected pages:* —

> **Reference:** Not stated in the handbook - the chatbot should say it does not know.

**qwen2.5:0.5b** (retrieved pages [4, 6, 5, 4, 13], hit=None, chunk_hit=None, coverage=None, 16.4s)

*Label: **correct** — Declines (baseline 0.5b invented 'Professor Xie').*

I couldn't find that in the documents.
The Computer Science department is headed by the head of the department, who is not specified in the given excerpts.
