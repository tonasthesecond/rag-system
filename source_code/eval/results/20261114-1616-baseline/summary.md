# Handbook chatbot evaluation

- Run: `20261114-1616-baseline`
- Embeddings: `nomic-embed-text`, chunk 1000/200, top-k 5, temperature 0.0, prompt `baseline`, threshold 0.3 (baseline rule: average of 1/(1+d); never triggered), max tokens unlimited
- Questions: 25

| Model | Page hit | Chunk hit | Avg fact coverage | Median latency (s) | Max latency (s) | Fallbacks |
|---|---|---|---|---|---|---|
| `qwen2.5:0.5b` | 23/23 | 21/23 | 0.68 | 24.0 | 2643.2 | 0 |
| `qwen2.5:1.5b` | 23/23 | 21/23 | 0.8 | 44.7 | 78.4 | 0 |
| `qwen2.5:3b` | 23/23 | 21/23 | 0.87 | 110.1 | 173.6 | 0 |

## Hand labels

| Model | correct | incomplete | ambiguous | incorrect |
|---|---|---|---|---|
| `qwen2.5:0.5b` | 9 | 1 | 3 | 12 |
| `qwen2.5:1.5b` | 18 | 2 | 3 | 2 |
| `qwen2.5:3b` | 19 | 1 | 3 | 2 |

## Answers

### `req-major-credits` — How many credits are required for the Computer Science major requirements?

*Category:* program requirements · *Expected pages:* [2, 7]

> **Reference:** The major requirements total 56 credits.

**qwen2.5:0.5b** (retrieved pages [7, 4, 7, 8, 11], hit=True, chunk_hit=True, coverage=0.0, 26.3s)

*Label: **incorrect** — Describes the declaration rule and the MINOR requirements; never gives 56.*

To formally declare Computer Science as their major, students must complete at least two Computer Science courses (MATH 202 - Discrete Math is also counted). The minor requires students to take a total of six courses:

1. One programming course (4 credits) which can be either CS 101: Introduction to Programming or CS 103: Programming for Data Science and Visualization.
2. One 100-level or 200-level CS course (4 credits).
3. Two intermediate courses (4 credits each).
4. One 200-level or 300-level CS course (4 credits).
5. One advanced course (4 credits).

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted).

**qwen2.5:1.5b** (retrieved pages [7, 4, 7, 8, 11], hit=True, chunk_hit=True, coverage=1.0, 78.4s)

*Label: **correct** — 56 is right. Its shown arithmetic (4+4+4+4+3x4+16) actually sums to 44 - it drops CS302 and the capstone - but the final number is copied from the text.*

The Computer Science major requires a total of 56 credits for its requirements. This includes:

1. **Core Curriculum**: 
   - CS 101: Introduction to Programming (4 credits)
   - CS 201: Data Structures & Algorithms (4 credits)
   - CS 203: Computer Organization (4 credits)
   - MATH 202: Discrete Math (4 credits)

2. **Intermediate Courses**: 
   - Three intermediate courses, each worth 4 credits.

3. **Advanced Courses**:
   - Four advanced courses, each worth 4 credits.
   - Capstone I and Capstone II (8 credits)
   OR two additional intermediate courses (8 credits)
   OR two additional advanced courses (8 credits)
   OR an additional intermediate course and an additional advanced course (8 credits)

Adding these up: 
\[ 4 + 4 + 4 + 4 + 3 \times 4 + 16 = 56 \text{ credits} \]

Therefore, the total number of required credits for the Computer Science major is **56**.

**qwen2.5:3b** (retrieved pages [7, 4, 7, 8, 11], hit=True, chunk_hit=True, coverage=1.0, 112.8s)

*Label: **correct** — 56 is right; 'exploratory courses and electives' as part of the 56 is loosely worded.*

The Computer Science major requires a total of 56 credits as outlined in the handbook. This includes core courses like CS 101 and MATH 202, intermediate and advanced courses, exploratory courses, and electives.

### `req-major-courses` — Which specific courses are required for the Computer Science major?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** CS 101 Introduction to Programming, CS 201 Data Structures & Algorithms, CS 203 Computer Organization, MATH 202 Discrete Math, three intermediate courses, CS 302 Algorithms & Theory of Computing, four advanced courses, and Capstone I and II (or two additional intermediate/advanced courses).

**qwen2.5:0.5b** (retrieved pages [7, 13, 8, 14, 4], hit=True, chunk_hit=False, coverage=0.33, 24.9s)

*Label: **incorrect** — Confuses the course list with the 'two courses to declare' rule; lists only CS101 and MATH202.*

For the Computer Science major, students are required to complete at least two courses:

1. CS 101: Introduction to Programming (which counts as one course)
2. MATH 202: Discrete Math (which also counts as a separate course)

These courses provide foundational knowledge in computer science and mathematics necessary for the major.

**qwen2.5:1.5b** (retrieved pages [7, 13, 8, 14, 4], hit=True, chunk_hit=False, coverage=0.5, 65.3s)

*Label: **incorrect** — Lists the MINOR requirements (six courses, CS103/CS104 options) as if they were the major's. Retrieval failure: the major-list chunk was not retrieved (not even in the top 8); the minor chunk ranked first.*

For the Computer Science major, students must complete at least two courses from the following list:

1. CS 101: Introduction to Programming (4 credits)
2. One programming course from either:
   a) CS 103: Programming for Data Science and Visualization
   b) CS 104: Introduction to Computer Science

Additionally, students must complete six courses in total as part of the minor requirements:

1. One programming course (4 credits)
2. One 100-level or 200-level CS course (4 credits)
3. CS 201 – Data Structures & Algorithms (4 credits)
4. One intermediate course (4 credits)
5. One 200-level or 300-level CS course (4 credits)
6. One advanced course (4 credits)

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted).

**qwen2.5:3b** (retrieved pages [7, 13, 8, 14, 4], hit=True, chunk_hit=False, coverage=0.5, 111.7s)

*Label: **incorrect** — Also gives the minor structure and invents 'CS 202' / 'CS 301' as examples; omits CS203 and CS302.*

For the Computer Science (CS) major at this institution, students are required to complete a total of five foundational courses and then take three intermediate courses. The specific courses include:

1. Introduction to Programming (CS 101 or CS 103 or CS 104)
2. Data Structures & Algorithms (CS 201)
3. One 100-level or 200-level Computer Science course
4. One intermediate course (e.g., a course like CS 202, which is not specified in the provided context but would be part of the intermediate courses requirement)
5. One advanced course (e.g., a course like CS 301, also unspecified but fitting the advanced course requirement)

Additionally, students must take MATH 202 - Discrete Math as it counts towards both major and minor requirements.

### `req-declare-major` — What do I need to complete before I can formally declare Computer Science as my major?

*Category:* academic policies · *Expected pages:* [7]

> **Reference:** At least two Computer Science courses (MATH 202 Discrete Math also counts).

**qwen2.5:0.5b** (retrieved pages [7, 4, 8, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 27.0s)

*Label: **incorrect** — First sentence is right, then invents extra requirements (six courses, three advanced courses...).*

To formally declare Computer Science as your major, you must complete at least two Computer Science courses (MATH 202 - Discrete Math is also counted). These courses are essential for the minor requirements and will help you gain foundational knowledge in computer science. Additionally, you need to take six courses that meet the minimum requirement of one programming course (4 credits) or CS 103: Programming for Data Science and Visualization, two intermediate courses (4 credits), three advanced courses (4 credits), and one advanced course (4 credits). These courses will help you develop your skills in computer science and prepare you for future studies.

**qwen2.5:1.5b** (retrieved pages [7, 4, 8, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 57.8s)

*Label: **ambiguous** — Correct rule, but adds that you must also 'fulfill the minor requirements', which is false.*

To formally declare Computer Science as their major, a student must complete at least two Computer Science courses (MATH 202 - Discrete Math is also counted). Additionally, they need to fulfill the minor requirements by completing six courses in total.

**qwen2.5:3b** (retrieved pages [7, 4, 8, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 104.7s)

*Label: **ambiguous** — Says 'two CS courses OR MATH 202' (should be: MATH 202 counts as one) and invents a CS104 requirement.*

To formally declare Computer Science as a major, you need to complete at least two Computer Science courses or MATH 202 - Discrete Math. Additionally, you must have completed Introduction to Computer Science (CS104) and one other Computer Science course from the list of required courses for the major.

### `req-declare-minor` — How many CS courses must be completed to declare a minor in Computer Science?

*Category:* academic policies · *Expected pages:* [7]

> **Reference:** At least one Computer Science course (MATH 202 Discrete Math also counts).

**qwen2.5:0.5b** (retrieved pages [7, 11, 13, 8, 13], hit=True, chunk_hit=True, coverage=1.0, 20.7s)

*Label: **correct** — At least one CS course, MATH 202 counts.*

To formally declare a minor in Computer Science, students must complete at least one computer science course (MATH 202 - Discrete Math is also counted).

**qwen2.5:1.5b** (retrieved pages [7, 11, 13, 8, 13], hit=True, chunk_hit=True, coverage=1.0, 48.3s)

*Label: **correct** — Verbatim from the handbook.*

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted).

**qwen2.5:3b** (retrieved pages [7, 11, 13, 8, 13], hit=True, chunk_hit=True, coverage=1.0, 94.4s)

*Label: **incorrect** — Quotes the rule correctly, then 'reasons' that you need at least seven courses. Auto coverage scored this 1.0.*

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted). In addition to this foundational course, students need to take six courses as part of the minor requirements. Therefore, to meet the minimum requirement for declaring a minor, students must complete at least seven CS courses in total.

### `req-minor` — What are the requirements for a minor in Computer Science?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** 24 credits / six courses: one programming course (CS 101, CS 103 or CS 104), one 100- or 200-level CS course, CS 201 Data Structures & Algorithms, one intermediate course, one 200- or 300-level CS course, and one advanced course.

**qwen2.5:0.5b** (retrieved pages [7, 11, 4, 14, 8], hit=True, chunk_hit=True, coverage=0.67, 40.3s)

*Label: **incorrect** — Garbled list: two intermediate courses, advanced course twice, CS201 missing; also mixes in the major rule.*

To formally declare Computer Science as their major, a student must complete at least two Computer Science courses (MATH 202 - Discrete Math is also counted). The minor requires students to take a total of six courses:

1. One programming course (4 credits) which can be either CS 101: Introduction to Programming or CS 103: Programming for Data Science and Visualization.
2. One 100-level or 200-level CS course (4 credits).
3. Two intermediate courses (4 credits each).
4. One advanced course (4 credits).
5. One advanced course (4 credits).

To formally declare a minor in Computer Science, the student must complete at least one Computer Science course (MATH 202 - Discrete Math is also counted).

**qwen2.5:1.5b** (retrieved pages [7, 11, 4, 14, 8], hit=True, chunk_hit=True, coverage=1.0, 62.7s)

*Label: **correct** — All six courses with the right options.*

The minor in Computer Science requires students to complete a total of six courses:
• One programming course (4 credits) which can be either CS 101: Introduction to Programming, CS 103: Programming for Data Science and Visualization, or CS 104: Introduction to Computer Science.
• One 100-level or 200-level CS course (4 credits).
• CS 201 – Data Structures & Algorithms (4 credits).
• One intermediate course (4 credits).
• One 200-level or 300-level CS course (4 credits).
• One advanced course (4 credits).

**qwen2.5:3b** (retrieved pages [7, 11, 4, 14, 8], hit=True, chunk_hit=True, coverage=1.0, 117.0s)

*Label: **correct** — All six courses (programming-course options not spelled out).*

To formally declare a minor in Computer Science, students must complete at least one Computer Science course (MATH 202 - Discrete Math can also be counted). The minor requires the completion of six courses in total. These include:
- One programming course (4 credits)
- One 100-level or 200-level CS course (4 credits)
- CS 201 – Data Structures & Algorithms (4 credits)
- One intermediate course (4 credits)
- One 200-level or 300-level CS course (4 credits)
- One advanced course (4 credits)

### `req-exploratory` — How many exploratory courses can be counted toward the major?

*Category:* program requirements · *Expected pages:* [7]

> **Reference:** Up to 2 of the 6 exploratory courses (8 credits) can be counted toward the major.

**qwen2.5:0.5b** (retrieved pages [7, 6, 7, 11, 6], hit=True, chunk_hit=True, coverage=0.5, 29.6s)

*Label: **incorrect** — Answers the major-declaration question instead. Auto coverage 0.5 is a false positive (matched 'two').*

To formally declare Computer Science as their major, the student must complete at least two Computer Science courses (MATH 202 - Discrete Math is also counted).

**qwen2.5:1.5b** (retrieved pages [7, 6, 7, 11, 6], hit=True, chunk_hit=True, coverage=1.0, 57.8s)

*Label: **correct** — Up to 2 courses (8 credits).*

Up to 2 courses (8 credits) can be counted toward the major from the exploratory courses chosen from Arts and Humanities, Social Sciences, and STEM categories.

**qwen2.5:3b** (retrieved pages [7, 6, 7, 11, 6], hit=True, chunk_hit=True, coverage=1.0, 115.0s)

*Label: **correct** — Up to 2 of the 6 exploratory courses (8 credits).*

According to the handbook, up to 2 exploratory courses (8 credits) can be counted toward the major out of the total of 6 exploratory courses available.

### `req-core` — What are the Core courses in the general curriculum?

*Category:* program requirements · *Expected pages:* [6]

> **Reference:** Four Core courses (16 credits): Global Humanities, Modern Vietnamese Culture and Society, Design and Systems Thinking, and one QUEST course (Quantitative Reasoning, Scientific Inquiry, Programming for Data Science and Visualization, or Introduction to Statistics).

**qwen2.5:0.5b** (retrieved pages [6, 5, 8, 8, 8], hit=True, chunk_hit=False, coverage=0.5, 50.8s)

*Label: **incorrect** — Presents the Core LEARNING OUTCOMES as if they were course names.*

The Core curriculum serves as the foundation of American liberal arts education and consists of four core courses designed to ignite new ways of thinking and learning, build essential skills, and connect to Fulbright’s intellectual community. These courses include:

1. **Global Awareness and Respect for Diverse Perspectives (GA1)**: Students will be able to demonstrate global awareness and respect for diverse perspectives.
2. **Locate and Critically Analyze Information and Present Evidence-Based Arguments in Written and Oral Forms (GA1, GA4, GA5, GA6, GA7, GA9)**: Students will be able to locate and critically analyze information and present evidence-based arguments in written and oral forms.
3. **Formulate Quantitative Inquiries and Apply Mathematical, Statistical, or Scientific Methods (GA1, GA4, GA5, GA7, GA9)**: Students will be able to formulate quantitative inquiries and apply appropriate mathematical, statistical, or scientific methods to answer them.
4. **Apply Design and Systems Thinking Processes to Analyze and Solve Real-World Problems (GA1, GA2, GA4, GA5)**: Students will be able to apply design and systems thinking processes to analyze and solve real-world problems.

These core courses are foundational for students' academic journey and serve as the basis for their future studies.

**qwen2.5:1.5b** (retrieved pages [6, 5, 8, 8, 8], hit=True, chunk_hit=False, coverage=0.0, 43.4s)

*Label: **incomplete** — Says there are four Core courses but names none. Retrieval failure: the chunk with the course list (end of p.6) was not retrieved; a different p.6 chunk was.*

The Core curriculum consists of four core courses designed to ignite new ways of thinking and learning, build essential skills, and connect to Fulbright's intellectual community in the first two or three semesters. These foundational courses serve as the basis for American liberal arts education.

**qwen2.5:3b** (retrieved pages [6, 5, 8, 8, 8], hit=True, chunk_hit=False, coverage=0.0, 97.8s)

*Label: **incomplete** — Same as 1.5b: generic description, no course names (list chunk not retrieved).*

The Core curriculum consists of four core courses designed to ignite new ways of thinking and learning, build essential skills, and connect students to Fulbright's intellectual community. These courses are taken in the first two or three semesters of the program.

### `req-degree-name` — What degree is awarded after completing the program requirements?

*Category:* program requirements · *Expected pages:* [1, 6]

> **Reference:** A Bachelor of Science in Computer Science (B.S. Computer Science). Note: page 6 of the handbook mistakenly says "Bachelor of Science in Applied Mathematics" - a copy-paste error in the source document.

**qwen2.5:0.5b** (retrieved pages [6, 6, 5, 3, 6], hit=True, chunk_hit=True, coverage=0.0, 30.9s)

*Label: **ambiguous** — Says 'B.S. in Applied Mathematics' - faithful to a copy-paste error on p.6 of the handbook.*

After completing the program requirements, a Bachelor of Science in Applied Mathematics is awarded. This degree aligns with the broader goals of the Fulbright Program, which emphasizes both breadth and depth of knowledge, critical thinking, and a lifelong love of learning—hallmarks of a liberal arts education.

**qwen2.5:1.5b** (retrieved pages [6, 6, 5, 3, 6], hit=True, chunk_hit=True, coverage=0.0, 40.0s)

*Label: **ambiguous** — Same source error; doesn't notice it conflicts with 'B.S. Computer Science' on p.1.*

A Bachelor of Science in Applied Mathematics is awarded after successfully completing the program requirements.

**qwen2.5:3b** (retrieved pages [6, 6, 5, 3, 6], hit=True, chunk_hit=True, coverage=0.0, 117.3s)

*Label: **ambiguous** — Same source error.*

A Bachelor of Science in Applied Mathematics is awarded after successfully completing the program requirements.

### `capstone-eligibility` — What are the eligibility requirements for the CS capstone project?

*Category:* academic policies · *Expected pages:* [9]

> **Reference:** A minimum major GPA of 3.5 and approval of a successful application (details in the Computer Science Capstone Handbook).

**qwen2.5:0.5b** (retrieved pages [9, 16, 7, 17, 4], hit=True, chunk_hit=True, coverage=1.0, 35.5s)

*Label: **correct** — GPA 3.5 + approved application.*

The eligibility criteria for the CS capstone project include a minimum major GPA of 3.5 and approval of a successful application. More detailed guidelines can be found in the Computer Science Capstone Handbook.

**qwen2.5:1.5b** (retrieved pages [9, 16, 7, 17, 4], hit=True, chunk_hit=True, coverage=1.0, 40.8s)

*Label: **correct** — GPA 3.5 + approved application.*

The eligibility criteria for enrollment in CS 401: Capstone Project include a minimum major GPA of 3.5 and approval of a successful application. More detailed guidelines can be found in the Computer Science Capstone Handbook.

**qwen2.5:3b** (retrieved pages [9, 16, 7, 17, 4], hit=True, chunk_hit=True, coverage=1.0, 173.5s)

*Label: **correct** — GPA 3.5 + approved application.*

To be eligible for enrollment in CS 401 (Capstone I), students must meet two main criteria:
a) Have a minimum major GPA of 3.5, and
b) Successfully complete and receive approval on their application to the Capstone project. More detailed guidelines can be found in the Computer Science Capstone Handbook.

### `capstone-honors` — Do I have to do a capstone to graduate, and what is the alternative?

*Category:* academic policies · *Expected pages:* [7, 8]

> **Reference:** No. Doing the capstone (CS 401/402) lets students graduate with honors; the alternative is to take two more intermediate or advanced courses and graduate without honors.

**qwen2.5:0.5b** (retrieved pages [9, 8, 3, 6, 5], hit=True, chunk_hit=True, coverage=0.5, 46.3s)

*Label: **incorrect** — Long 'analysis' that never answers yes/no and claims extra courses are required.*

To determine whether you need to complete a capstone project for graduation, let's analyze the given context and guidelines:

### Context Analysis:
1. **Major GPA Requirement**: The context mentions that CS 401/402 requires a minimum major GPA of 3.5.
2. **Capstone Project Eligibility Criteria**:
   - Capstone I includes a minimum major GPA of 3.5.
   - More detailed guidelines for the Capstone in Computer Science can be found in the Computer Science Capstone Handbook.

### Guidelines Analysis:
1. **Foundational Courses**: The context mentions two additional intermediate or advanced courses that are not part of CS 401/402 but are still required for graduation (e.g., Introduction to Programming, Data Structures & Algorithms).
2. **Graduate A0ributes**:
   - Knowledge: Students will acquire knowledge through interdisciplinary innovation.
   - Skills: Students develop four intellectual and practical competencies.

### Conclusion:
- Since the context mentions that CS 401/402 requires a minimum major GPA of 3.5, it is clear that you need to complete this course for graduation.
- The additional courses (Introduction to Programming and Data Structures & Algorithms) are not part of the core curriculum but are still required.

### Alternative:
If you choose to skip CS 401/402, you can still graduate by completing the Foundational Courses. However, if you want to focus on a different major or field of study, you might consider taking elective courses that reflect your personal interests and complement your chosen major.

In summary, yes, you need to complete a capstone project for graduation. If you choose not to take CS 401/402, you can still graduate by completing the Foundational Courses.

**qwen2.5:1.5b** (retrieved pages [9, 8, 3, 6, 5], hit=True, chunk_hit=True, coverage=0.0, 42.9s)

*Label: **incomplete** — 'No' is right, but the 'alternative' it gives is the capstone eligibility criteria, not the two-course option.*

No, you do not have to complete a capstone project to graduate. The alternative for students who meet the eligibility criteria for enrollment in CS 401: Capstone I includes a minimum major GPA of 3.5 and approval of a successful application. More detailed guidelines can be found in the Computer Science Capstone Handbook.

**qwen2.5:3b** (retrieved pages [9, 8, 3, 6, 5], hit=True, chunk_hit=True, coverage=0.5, 105.5s)

*Label: **correct** — Not required; alternative is extra intermediate/advanced courses and graduating without honors.*

No, a capstone project is not required to graduate from CS (Computer Science) at Fulbright University Vietnam. However, students must meet certain eligibility criteria for enrollment in the Capstone Project course, including a minimum major GPA of 3.5 and approval of their application. If a student does not complete the Capstone Project, they can fulfill this requirement by taking additional intermediate or advanced courses to graduate without honors.

### `course-advanced-list` — Can you list some of the advanced courses offered in the CS major?

*Category:* course offerings · *Expected pages:* [8, 9]

> **Reference:** Examples: Foundations of Software Engineering, Database Systems, Computer Security, Cloud Computing, Human-Computer Interaction, Computer Graphics, Game Design & Development, Machine Learning, Deep Learning, Advanced Deep Learning, Computer Vision, Natural Language Processing, Optimization, Computational Social Media, Bioinformatics.

**qwen2.5:0.5b** (retrieved pages [8, 13, 11, 7, 4], hit=True, chunk_hit=True, coverage=1.0, 28.4s)

*Label: **ambiguous** — List is right but every course is tagged '(CS TBA)', leaked from the cross-listing table.*

The Advanced Courses offered in the Computer Science major include:

• Foundations of Software Engineering (CS TBA)
• Database Systems (CS TBA)
• Computer Security (CS TBA)
• Cloud Computing (CS TBA)
• Human-Computer Interaction (CS TBA)
• Computer Graphics (CS TBA)
• Game Design & Development (CS TBA)
• Machine Learning (CS TBA)
• Deep Learning (CS TBA)
• Advanced Deep Learning (CS TBA)
• Computer Vision (CS TBA)
• Natural Language Processing (CS TBA)
• Optimization (CS TBA)
• Computational Social Media (CS TBA)

**qwen2.5:1.5b** (retrieved pages [8, 13, 11, 7, 4], hit=True, chunk_hit=True, coverage=1.0, 54.3s)

*Label: **ambiguous** — List is right but every course is labelled '(16 credits)' - that is the total for four advanced courses.*

The sample advanced courses listed in the document include:

• Foundations of Software Engineering (16 credits)
• Database Systems (16 credits)
• Computer Security (16 credits)
• Cloud Computing (16 credits)
• Human-Computer Interaction (16 credits)
• Computer Graphics (16 credits)
• Game Design & Development (16 credits)
• Machine Learning (16 credits)
• Deep Learning (16 credits)
• Advanced Deep Learning (16 credits)
• Computer Vision (16 credits)
• Natural Language Processing (16 credits)
• Optimization (16 credits)
• Computational Social Media (16 credits)

**qwen2.5:3b** (retrieved pages [8, 13, 11, 7, 4], hit=True, chunk_hit=True, coverage=1.0, 122.6s)

*Label: **correct** — Clean list (Bioinformatics missing: it sits on the next page/chunk).*

Some of the advanced courses offered in the CS major include:

- Foundations of Software Engineering
- Database Systems
- Computer Security
- Cloud Computing
- Human-Computer Interaction
- Computer Graphics
- Game Design & Development
- Machine Learning
- Deep Learning
- Advanced Deep Learning
- Computer Vision
- Natural Language Processing
- Optimization
- Computational Social Media

### `course-intermediate-list` — What are the intermediate courses in the CS major?

*Category:* course offerings · *Expected pages:* [8]

> **Reference:** Sample intermediate courses: Software Construction, Programming Language Paradigms, Operating Systems, Computer Networks, Introduction to Artificial Intelligence.

**qwen2.5:0.5b** (retrieved pages [8, 13, 11, 8, 7], hit=True, chunk_hit=True, coverage=1.0, 17.6s)

*Label: **correct** — All five.*

The Intermediate Courses in the Computer Science major include:

• Software construction
• Programming Language Paradigms
• Operating Systems
• Computer Networks
• Introduction to Artificial Intelligence

These courses provide foundational knowledge and practical experience in various aspects of computer science, preparing students for their future studies.

**qwen2.5:1.5b** (retrieved pages [8, 13, 11, 8, 7], hit=True, chunk_hit=True, coverage=1.0, 44.7s)

*Label: **correct** — All five.*

The intermediate courses in the CS major are:

• Software construction
• Programming Language Paradigms
• Operating Systems
• Computer Networks
• Introduction to Artificial Intelligence

**qwen2.5:3b** (retrieved pages [8, 13, 11, 8, 7], hit=True, chunk_hit=True, coverage=1.0, 109.1s)

*Label: **correct** — All five.*

In the Computer Science (CS) major, intermediate courses include a variety of topics such as Software Construction, Programming Language Paradigms, Operating Systems, Computer Networks, and Introduction to Artificial Intelligence. These courses are designed to build upon foundational knowledge and cover important aspects in computer science.

### `course-prereq-cs311` — What is the prerequisite for CS311 Advanced Deep Learning?

*Category:* course offerings · *Expected pages:* [13, 18]

> **Reference:** CS313 Deep Learning for AI (which itself requires CS208).

**qwen2.5:0.5b** (retrieved pages [18, 18, 18, 17, 16], hit=True, chunk_hit=True, coverage=1.0, 17.8s)

*Label: **correct** — CS313 (then describes CS313 using CS311's own description - minor).*

The prerequisite for CS311 Advanced Deep Learning is CS313, which covers advanced architectures of deep neural networks and algorithms along with deriving practical AI solutions in various domains such as economics, fintech, computer vision, natural language processing.

**qwen2.5:1.5b** (retrieved pages [18, 18, 18, 17, 16], hit=True, chunk_hit=True, coverage=1.0, 40.9s)

*Label: **correct** — CS313.*

The prerequisite for CS311 Advanced Deep Learning is CS313.

**qwen2.5:3b** (retrieved pages [18, 18, 18, 17, 16], hit=True, chunk_hit=True, coverage=1.0, 102.7s)

*Label: **correct** — CS313.*

The prerequisite for CS311 Advanced Deep Learning is CS313.

### `course-prereq-cs302` — What are the prerequisites for CS302 Algorithms & Theory of Computing?

*Category:* course offerings · *Expected pages:* [13, 17]

> **Reference:** CS201 Data Structures & Algorithms and MATH202 Discrete Math.

**qwen2.5:0.5b** (retrieved pages [17, 18, 14, 18, 12], hit=True, chunk_hit=True, coverage=0.0, 24.0s)

*Label: **incorrect** — Summarises the course content; never states the prerequisites.*

To find the shortest path between two cities on a map, schedule courses at FUV, or detect if a computer program is a virus or not, CS302: Algorithms & Theory of Computing course aims to provide students with efficient algorithms and techniques. Three common techniques (divide-and-conquer, greedy, and dynamic programming) are introduced to help students design efficient algorithms for problems in practice. Students will also learn basic computational models (finite automaton, push-down automaton, and Turing machine) to understand the concepts of decidability and tractability. By this course, students can prove if a problem is hard to solve efficiently or even cannot be solved by any algorithm.

**qwen2.5:1.5b** (retrieved pages [17, 18, 14, 18, 12], hit=True, chunk_hit=True, coverage=1.0, 50.7s)

*Label: **correct** — CS201 and MATH 202.*

The prerequisites for CS302 Algorithms & Theory of Computing are CS201 and MATH 202.

**qwen2.5:3b** (retrieved pages [17, 18, 14, 18, 12], hit=True, chunk_hit=True, coverage=1.0, 123.5s)

*Label: **correct** — CS201 and MATH 202.*

The prerequisites for CS302 Algorithms & Theory of Computing are CS201 and MATH 202.

### `course-cs201-language` — Which programming language is mainly used in CS201 Data Structures & Algorithms?

*Category:* course offerings · *Expected pages:* [14]

> **Reference:** Java (with some Python/C++ implementations also introduced).

**qwen2.5:0.5b** (retrieved pages [14, 16, 11, 15, 18], hit=True, chunk_hit=True, coverage=1.0, 17.0s)

*Label: **correct** — Java.*

CS201 mainly uses Java as the main programming language in its course "Data Structures & Algorithms". This choice reflects the focus on theoretical concepts and abstraction within CS201, which emphasizes learning fundamental data structures and algorithms.

**qwen2.5:1.5b** (retrieved pages [14, 16, 11, 15, 18], hit=True, chunk_hit=True, coverage=1.0, 39.8s)

*Label: **correct** — Java.*

The main programming language used in CS201 Data Structures & Algorithms is Java.

**qwen2.5:3b** (retrieved pages [14, 16, 11, 15, 18], hit=True, chunk_hit=True, coverage=1.0, 100.9s)

*Label: **correct** — Java, plus some Python/C++.*

The main programming language used in CS201 Data Structures & Algorithms is Java. Some Python/C++ implementations are also introduced as part of the course.

### `course-cs207-content` — What do students build in CS207 Software Construction?

*Category:* course offerings · *Expected pages:* [15]

> **Reference:** They work in teams to design software with UML (use-case, sequence and class diagrams) and implement the design by building Android applications in Java.

**qwen2.5:0.5b** (retrieved pages [15, 16, 11, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 16.3s)

*Label: **correct** — Android apps in Java, UML design in teams.*

Students build Android applications using Java in CS207 Software Construction course. They learn about class, object, information hiding, encapsulation, inheritance, interface, polymorphism, design patterns, multi-threading, database connection, unit testing, and Unified Modeling Language (UML). Students work in teams to practice designing software using UML models such as use-case, sequence, and class diagrams.

**qwen2.5:1.5b** (retrieved pages [15, 16, 11, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 34.9s)

*Label: **correct** — Android apps in Java, UML.*

Students in CS207 Software Construction build Android applications using Java to practice designing software systems and implementing designs through UML models such as use-case, sequence, and class diagrams.

**qwen2.5:3b** (retrieved pages [15, 16, 11, 14, 4], hit=True, chunk_hit=True, coverage=1.0, 87.3s)

*Label: **correct** — Android apps in Java, UML.*

In CS207 Software Construction, students build their skills and experience in developing software systems by applying object-oriented (OO) concepts and design principles. They work on projects where they practice designing software using UML models such as use-case, sequence, and class diagrams, and implement the designs via building Android applications using Java.

### `course-cs210-availability` — How often is CS210 Computer Networks offered?

*Category:* course offerings · *Expected pages:* [13]

> **Reference:** It is listed as "On holding" (not currently scheduled), prerequisite CS201.

**qwen2.5:0.5b** (retrieved pages [16, 13, 17, 13, 16], hit=True, chunk_hit=True, coverage=0.0, 21.5s)

*Label: **incorrect** — Describes the course; doesn't answer how often it is offered.*

CS210 Computer Networks is an in-depth study of computer networks. It explores issues, concepts and techniques essential for building modern computer networks with a focus on architectures, protocols and implementation issues. The course aims to gain a solid knowledge on technologies that build the infrastructure for modern networked applications such as cloud computing, Web browsing, social networking, multimedia streaming, etc.

**qwen2.5:1.5b** (retrieved pages [16, 13, 17, 13, 16], hit=True, chunk_hit=True, coverage=0.0, 42.3s)

*Label: **incorrect** — 'Once a year' - read from a neighbouring row of the flattened catalogue table.*

CS210 Computer Networks is offered once a year.

**qwen2.5:3b** (retrieved pages [16, 13, 17, 13, 16], hit=True, chunk_hit=True, coverage=1.0, 113.9s)

*Label: **ambiguous** — Quotes 'On holding' correctly, then says that 'typically means once a year'. Auto coverage scored 1.0.*

According to the provided context from [CS_MajorHandbook.pdf p.16], CS210: Computer Networks is offered "On holding" which typically means it is offered once a year.

### `course-cs311-topics` — What topics does the Advanced Deep Learning course cover?

*Category:* course offerings · *Expected pages:* [18]

> **Reference:** Transfer Learning, GANs, Reinforcement Learning, Attention and Transformer Networks, Graph Neural Networks, plus applications such as NLP, robotics, autonomous driving and time-series.

**qwen2.5:0.5b** (retrieved pages [18, 18, 18, 8, 16], hit=True, chunk_hit=True, coverage=1.0, 17.2s)

*Label: **correct** — All topics (repeats itself).*

The Advanced Deep Learning course covers advanced architectures of deep neural networks and algorithms, including Transfer Learning, Generative Adversarial Network (GAN), Reinforcement Learning (RL), Attention and Transformer Networks, Graph Neural Network (GNN). The course also delves into topics such as network (GAN), reinforcement learning (RL), attention and transformer networks, graph neural networks. Additionally, it covers advanced applications of deep learning in various domains like natural language processing, robotics, autonomous driving systems, time-series applications, etc.

**qwen2.5:1.5b** (retrieved pages [18, 18, 18, 8, 16], hit=True, chunk_hit=True, coverage=1.0, 35.6s)

*Label: **correct** — All topics and applications.*

The Advanced Deep Learning course covers diverse topics including Transfer Learning, Generative Adversarial Networks (GAN), Reinforcement Learning (RL), Attention and Transformer Networks, Graph Neural Networks (GNN). Additionally, it addresses advanced applications of deep learning in areas such as natural language processing, robotics, autonomous driving systems, time-series applications, etc.

**qwen2.5:3b** (retrieved pages [18, 18, 18, 8, 16], hit=True, chunk_hit=True, coverage=1.0, 86.6s)

*Label: **correct** — All topics and applications.*

The Advanced Deep Learning course covers advanced architectures of deep neural networks and algorithms, including Transfer Learning, Generative Adversarial Networks (GAN), Reinforcement Learning (RL), Attention and Transformer Networks, and Graph Neural Networks (GNN). It also addresses advanced applications in various domains such as natural language processing, robotics, autonomous driving systems, time-series applications, etc.

### `outcomes-plo` — What are the program learning outcomes of the CS major?

*Category:* learning outcomes · *Expected pages:* [5, 11]

> **Reference:** PLO1: understand fundamental CS (core concepts, compare methods, solve problems in theory and systems). PLO2: explain emerging aspects of CS (AI, ML, data science, business analytics, digital media). PLO3: develop real-world applications using knowledge of CS and other disciplines.

**qwen2.5:0.5b** (retrieved pages [4, 11, 5, 12, 12], hit=True, chunk_hit=True, coverage=1.0, 2643.2s)

*Label: **incorrect** — Repetition loop: 238,039 characters over 44 minutes; unusable even though it starts roughly right.*

The program learning outcomes for the Computer Science (CS) major are derived from two main components of the curriculum: the Core Curriculum and the Major Curriculum. The Core Curriculum consists of Core Learning Outcomes (Core LOs) and Major Learning Outcomes (Major LOs). These outcomes are presented in the following tables and are also mapped to the FUV Graduate Attributes.

1. **Core Learning Outcomes (Core LOs):**
   - **Global Awareness:** Students will demonstrate global awareness and respect for diverse perspectives.
   - **Theory and Systems Analysis:** Students will be able to locate and critically analyze information and present evidence-based arguments in written and oral forms, as well as through group discussions.

2. **Major Learning Outcomes (Major LOs):**
   - **Fundamental Computer Science:** Students will demonstrate an understanding of fundamental computer science by illustrating core concepts, comparing methods, analyzing and solving problems in both theory and systems.
   - **Emerging Aspects of Computer Science:** Students will explain emerging aspects of the computer science discipline (e.g., artificial intelligence, machine learning, data science, business analytics, digital media, etc.).
   - **Real-World Applications:** Students will develop real-world applications by using knowledge of computer science and other disciplines.

The program learning outcomes are derived from these two components and are presented in the following tables:

| Program Learning Outcomes | Core LOs | Major LOs |
|---------------------------|---------|----------|
| Demonstrate an understanding
of fundamental computer science | Illustrate core concepts, compare methods, analyze and solve problems in both theory and systems. | Explain emerging aspects of the computer science discipline (e.g., artificial intelligence, machine learning, data science, business analytics, digital media, etc.). |
| Explain emerging aspects of the computer science discipline | Demonstrate an understanding of fundamental computer science by illustrating core concepts, compare methods, analyze and solve problems in both theory and systems. | Develop real-world applications (e.g., software systems and frameworks, mobile apps, data pipeline, etc.) by using knowledge of computer science and other disciplines. |
| Develop real-world applications | Demonstrate an understanding of fundamental computer science by illustrating core concepts, compare methods, analyze and solve problems in 

*[... truncated: answer was 238,039 characters]*

**qwen2.5:1.5b** (retrieved pages [4, 11, 5, 12, 12], hit=True, chunk_hit=True, coverage=1.0, 75.6s)

*Label: **correct** — Core LOs (3 of 5 listed) plus all three Major LOs; the handbook defines PLOs as both.*

The Computer Science (CS) major program learning outcomes are derived from two main components of the curriculum: Core Learning Outcomes and Major Learning Outcomes. These outcomes consist of:

1. **Core Learning Outcomes**:
   - Students will be able to demonstrate global awareness and respect for diverse perspectives.
   - Students will be able to locate and critically analyze information and present evidence-based arguments in written and oral forms.
   - Students will be able to formulate quantitative inquiries and apply appropriate mathematical, statistical, or scientific methods to answer them.

2. **Major Learning Outcomes**:
   - Demonstrate an understanding of fundamental computer science by illustrating core concepts, comparing methods, analyzing and solving problems in both theory and systems.
   - Explain emerging aspects of the computer science discipline (e.g., artificial intelligence, machine learning, data science, business analytics, digital media, etc.).
   - Develop real-world applications (e.g., software systems and frameworks, mobile apps, data pipeline, etc.) by using knowledge of computer science and other disciplines.
   - Apply design and systems thinking processes to analyze and solve real-world problems.

These outcomes are presented in tables and mapped to the FUV Graduate Attributes.

**qwen2.5:3b** (retrieved pages [4, 11, 5, 12, 12], hit=True, chunk_hit=True, coverage=1.0, 173.6s)

*Label: **correct** — The three PLOs; teaching methods from the next table column are blended into the wording.*

The Program Learning Outcomes (PLOs) for the Computer Science major include:

1. **Demonstrate an understanding of fundamental computer science by illustrating core concepts, comparing methods, analyzing and solving problems in both theory and systems.**
2. **Explain emerging aspects of the computer science discipline such as artificial intelligence, machine learning, data science, business analytics, digital media, etc., through reading, lectures, lab work, group discussions, class projects, quizzes, exams, presentations, and capstone projects.**
3. **Develop real-world applications (e.g., software systems and frameworks, mobile apps, data pipeline, etc.) by using knowledge of computer science and other disciplines through lectures, labs, field trips, class projects, presentations, and capstone projects.**

These PLOs are aligned with the Core Learning Outcomes and Major Learning Outcomes, which in turn map to FUV Graduate Attributes.

### `outcomes-peo` — What are the Program Educational Objectives (PEOs)?

*Category:* learning outcomes · *Expected pages:* [4]

> **Reference:** PEO1: skills/knowledge for industry employment or graduate school. PEO2: professional and personal ethics, collaboration and communication. PEO3: cultivate innovators and thinkers to solve CS-related challenges.

**qwen2.5:0.5b** (retrieved pages [4, 4, 4, 4, 11], hit=True, chunk_hit=True, coverage=1.0, 20.4s)

*Label: **correct** — All three PEOs.*

The Program Educational Objectives (PEOs) for the Computer Science major at Fulbright are:

1. To equip students with the necessary skills and knowledge to gain employment in industry or study in graduate schools.
2. To instill a strong code of professional and personal ethics, and the ability to effectively and creatively collaborate and communicate in the workplace and beyond.
3. To cultivate students into innovators and thinkers who can solve computer science-related challenges.

The PEOs are based on the provided context documents, which outline the educational objectives for the Computer Science major at Fulbright.

**qwen2.5:1.5b** (retrieved pages [4, 4, 4, 4, 11], hit=True, chunk_hit=True, coverage=1.0, 43.0s)

*Label: **correct** — All three PEOs verbatim.*

The Program Educational Objectives (PEOs) are:

To equip students with the necessary skills and knowledge to gain employment in industry or study in graduate schools.

To ingrain in students a strong code of professional and personal ethics, and the ability to effectively and creatively collaborate and communicate in the workplace and beyond.

To cultivate students to become innovators and thinkers to solve computer science related challenges.

**qwen2.5:3b** (retrieved pages [4, 4, 4, 4, 11], hit=True, chunk_hit=True, coverage=1.0, 104.7s)

*Label: **correct** — All three PEOs, paraphrased.*

The Program Educational Objectives (PEOs) aim to equip students with necessary skills and knowledge to gain employment in industry or study in graduate schools. They also focus on instilling strong professional ethics, effective collaboration, and creativity in the workplace. Additionally, PEOs encourage students to develop as innovators capable of solving computer science-related challenges.

### `careers` — What jobs have Computer Science graduates gone on to?

*Category:* career paths · *Expected pages:* [5]

> **Reference:** Software engineer, testing engineer, AI engineer, data engineer, business analyst, product owner, product development manager.

**qwen2.5:0.5b** (retrieved pages [6, 5, 4, 4, 4], hit=True, chunk_hit=True, coverage=0.25, 17.4s)

*Label: **incomplete** — Vague fields ('software engineering, data science, AI') instead of the listed job titles.*

Computer Science graduates have successfully gained employment in various fields such as software engineering, data science, AI, and business analytics. They are also pursuing graduate studies to further their education and explore potential career paths beyond traditional computer science programs.

**qwen2.5:1.5b** (retrieved pages [6, 5, 4, 4, 4], hit=True, chunk_hit=True, coverage=1.0, 43.1s)

*Label: **correct** — All seven roles.*

Computer Science graduates have successfully secured employment in various roles such as software engineer, testing engineer, AI engineer, data engineer, business analyst, product owner, and product development manager.

**qwen2.5:3b** (retrieved pages [6, 5, 4, 4, 4], hit=True, chunk_hit=True, coverage=1.0, 102.4s)

*Label: **correct** — All seven roles.*

Computer Science graduates from Fulbright have gone on to various jobs including software engineer, testing engineer, AI engineer, data engineer, business analyst, product owner, and product development manager. They also have the opportunity to further specialize in areas such as software engineering, artificial intelligence and machine learning, data science, or business analytics.

### `grad-programs` — Which graduate programs have CS students been admitted to?

*Category:* career paths · *Expected pages:* [6]

> **Reference:** MSc/PhD Computer Science, MSc Data Science, MSc Bioinformatics (in the US and Europe).

**qwen2.5:0.5b** (retrieved pages [6, 13, 5, 4, 7], hit=True, chunk_hit=True, coverage=1.0, 19.7s)

*Label: **correct** — Right three programs; the 'cross-listed' remark is invented but harmless.*

Based on the provided context from "CS_MajorHandbook.pdf", computer science students have successfully applied to graduate programs in the United States and Europe. These programs include:

1. Master's/PhD Computer Science (e.g., MSc/PhD Computer Science)
2. Master's Data Science
3. Master's Bioinformatics

The context mentions that these programs are cross-listed with computer science, indicating they overlap with other graduate programs in the field of computer science.

**qwen2.5:1.5b** (retrieved pages [6, 13, 5, 4, 7], hit=True, chunk_hit=True, coverage=1.0, 40.7s)

*Label: **correct** — Right three programs.*

CS students have successfully applied and been admitted to graduate programs in the United States and Europe, including MSc/PhD Computer Science, MSc Data Science, and MSc Bioinformatics.

**qwen2.5:3b** (retrieved pages [6, 13, 5, 4, 7], hit=True, chunk_hit=True, coverage=1.0, 97.2s)

*Label: **correct** — Right three programs.*

Computer Science (CS) students have successfully applied to graduate programs in the United States and Europe. These programs include MSc/PhD Computer Science, MSc Data Science, and MSc Bioinformatics.

### `teaching-assessment` — How are students assessed in the Computer Science major?

*Category:* teaching & assessment · *Expected pages:* [12]

> **Reference:** Active and collaborative learning with continuous formative assessment (discussion, in-class activities, applied learning) plus summative methods; examples include programming tests, quizzes, exams, group presentations, class projects and the capstone.

**qwen2.5:0.5b** (retrieved pages [12, 4, 7, 12, 1], hit=True, chunk_hit=True, coverage=1.0, 27.7s)

*Label: **ambiguous** — Generic filler; invents 'final exams in each course' and self-assessment.*

In the Computer Science major, students are assessed through a combination of summative and formative assessment methods. Summative assessments include final exams in each course, which measure their mastery of theoretical concepts and practical skills. Formative assessments involve ongoing feedback from instructors, peers, and self-assessment activities.

The major also emphasizes continuous learning through courses that incorporate both traditional lectures and interactive discussions. These courses help students develop critical thinking, problem-solving, and communication skills essential for success in the field. Additionally, the program encourages students to engage with real-world applications by offering capstone projects that integrate their coursework into practical solutions relevant to industry needs.

Formative assessments are crucial as they provide immediate feedback on student learning, helping instructors identify areas where students need additional support or guidance. Regular participation and engagement in these activities contribute to a supportive learning environment that fosters continuous improvement and personal growth within the Computer Science major.

**qwen2.5:1.5b** (retrieved pages [12, 4, 7, 12, 1], hit=True, chunk_hit=True, coverage=1.0, 52.5s)

*Label: **correct** — Formative + summative with the listed examples.*

Students in the Computer Science (CS) major are assessed through a combination of formative and summative methods. Continuous assessment includes discussion-based activities, in-class exercises, applied learning projects, programming tests, quizzes, exams, group presentations, and capstone projects. Summative assessments include final exams and capstone evaluations to measure mastery of the material.

**qwen2.5:3b** (retrieved pages [12, 4, 7, 12, 1], hit=True, chunk_hit=True, coverage=1.0, 124.6s)

*Label: **correct** — Right, though it mixes teaching methods (lectures, labs) into assessment methods.*

In the Computer Science major, students are assessed through a variety of methods including lectures, labs, group discussions, programming tests, quizzes, exams, and capstone projects. Continuous formative assessment is also provided through in-class activities and applied learning to support active and collaborative learning.

### `oos-tuition` — How much is the tuition fee for the Computer Science program?

*Category:* out of scope · *Expected pages:* —

> **Reference:** Not stated in the handbook - the chatbot should say it does not know.

**qwen2.5:0.5b** (retrieved pages [6, 4, 7, 8, 13], hit=None, chunk_hit=None, coverage=None, 17.2s)

*Label: **incorrect** — Hallucinates '$50,000 per year at Alibaba Cloud' and cites the handbook for it.*

The tuition fee for the Computer Science program at Alibaba Cloud is $50,000 per year. This information can be found in the "Major Outline" section of the CS_MajorHandbook.pdf document, which provides details about the course structure and progression for the major.

**qwen2.5:1.5b** (retrieved pages [6, 4, 7, 8, 13], hit=None, chunk_hit=None, coverage=None, 46.0s)

*Label: **correct** — Says the handbook doesn't contain it.*

The document does not provide specific tuition fee information for the Computer Science program. However, it mentions that students have successfully applied to graduate programs in the United States and Europe, indicating that they are eligible to pursue higher education at a cost. For accurate tuition fees, one would need to consult the official university website or contact the admissions office directly.

**qwen2.5:3b** (retrieved pages [6, 4, 7, 8, 13], hit=None, chunk_hit=None, coverage=None, 110.1s)

*Label: **correct** — Says the handbook doesn't contain it.*

The provided context does not contain any specific information about tuition fees for the Computer Science program at the institution. For accurate and up-to-date information on tuition fees, I would recommend checking the official university website or contacting the admissions office directly.

### `oos-department-head` — Who is the head of the Computer Science department?

*Category:* out of scope · *Expected pages:* —

> **Reference:** Not stated in the handbook - the chatbot should say it does not know.

**qwen2.5:0.5b** (retrieved pages [4, 12, 5, 6, 14], hit=None, chunk_hit=None, coverage=None, 19.0s)

*Label: **incorrect** — Invents 'Professor Xie' and courses he teaches.*

The head of the Computer Science department is Professor Xie, who teaches courses in CS301 Algorithms & Theory of Computing M I, CS302 Algorithms & Theory of Computing M I, and CS307 Machine Learning M I. He also serves as the coordinator for the CS306 Computer Security M R M/A course.

**qwen2.5:1.5b** (retrieved pages [4, 12, 5, 6, 14], hit=None, chunk_hit=None, coverage=None, 51.3s)

*Label: **correct** — Says the handbook doesn't mention it.*

Based on the provided documents, there is no explicit mention of who the head of the Computer Science department is. The information focuses on program descriptions, course offerings, and career paths for graduates, but does not provide details about administrative leadership within the department.

**qwen2.5:3b** (retrieved pages [4, 12, 5, 6, 14], hit=None, chunk_hit=None, coverage=None, 136.7s)

*Label: **correct** — Says the handbook doesn't mention it.*

Based on the provided context from the Computer Science (CS) major handbook, there is no specific mention of who the head of the department is. The information focuses on program descriptions, learning objectives, career paths, and course details rather than administrative roles such as department heads. For accurate and up-to-date information about departmental leadership, it would be best to consult the most recent official university or college documents or contact the institution directly.
