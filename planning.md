# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
The chosen domain covers course-level feedback, workload expectations, and student experiences within the Master of Computer and Information Technology (MCIT) program. While official university syllabi describe assignments, grading weights, and formal prerequisites, they fail to capture the qualitative, subjective realities of the student journey. This includes crucial insights like navigating difficult programming paradigm shifts (e.g., Python to Java) or managing extreme shifts in workload between foundational classes. This knowledge base aggregates peer insights to allow students to make highly strategic, informed data-driven enrollment decisions.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->
The knowledge base utilizes 10 distinct local raw text data files, with each file representing a comprehensive historical log of anonymous student reviews for a specific core or elective course sourced from MCIT Central:

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | cit_591_reviews.txt | Introduction to Software Development reviews | documents/cit_591_reviews.txt |
| 2 | cit_592_reviews.txt | Mathematical Foundations of Computer Science reviews | documents/cit_592_reviews.txt |
| 3 | cit_593_reviews.txt | Introduction to Computer Systems reviews | documents/cit_593_reviews.txt |
| 4 | cit_594_reviews.txt | Data Structures and Software Design reviews | documents/cit_594_reviews.txt |
| 5 | cit_595_reviews.txt | Computer Systems Programming reviews | documents/cit_595_reviews.txt |
| 6 | cit_596_reviews.txt | Algorithms & Computation reviews | documents/cit_596_reviews.txt |
| 7 | cis_521_reviews.txt | Artificial Intelligence reviews | documents/cis_521_reviews.txt |
| 8 | cis_545_reviews.txt | Big Data Analytics reviews | documents/cis_545_reviews.txt |
| 9 | cis_550_reviews.txt | Database & Information Systems reviews | documents/cis_550_reviews.txt |
| 10 | cit_582_reviews.txt | Blockchain & Cryptography reviews | documents/cit_582_reviews.txt |
---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Reasoning:** MCIT Central reviews are fundamentally short-form, opinion-dense, and highly localized blocks of text. A small, conservative chunk size of 500 characters prevents individual course insights or highly specific workload figures from being structurally diluted by neighboring reviews within the vector space. The 100-character overlap provides a safety buffer ensuring that continuous context—such as a student shifting from an introductory point to a deeply nuanced observation about exam difficulty or a specific software framework—is not cleanly severed mid-sentence by a mechanical splitting boundary.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** sentence-transformers (all-MiniLM-L6-v2)

**Top-k:** k=4 retrieved chunks per query

**Production tradeoff reflection:**
If scaling this system to support a live, production-grade tool for all active university students, several key enterprise architecture tradeoffs would need to be weighed against this local baseline:
1. **API vs. Local Latency/Cost:** Moving to an API-driven model like OpenAI's `text-embedding-3-small` offloads local compute constraints and leverages optimized infrastructure, but introduces perpetual operational token expenses.
2. **Context Window Limitations:** The `all-MiniLM-L6-v2` model is bound to a strict 256-token context limit. For incredibly descriptive multi-paragraph student narratives, an enterprise embedding model with expanded context boundaries would capture long-form thematic dependencies without requiring aggressive segment isolation.
3. **Domain Vocabulary:** Standard embedding spaces easily tokenize generalized vocabulary but can struggle to capture hyper-specific technical structures unique to a curriculum (e.g., semantic confusion between similar course codes like CIT-593 and CIT-595). In production, implementing hybrid lexical search (combining BM25 keyword matching with dense vector tracking) would resolve numerical alignment challenges.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the primary difficulty students face in the second half of CIT-591? | Shifting programming paradigms and habits from Python to Java classes, methods, and debugging. |
| 2 | How many hours per week on average do students spend on CIT-596 compared to CIT-594? | CIT-596 demands a significantly higher weekly workload (averaging ~19.84 hours) compared to CIT-594 (averaging ~10.69 hours). |
| 3 | What is covered or recommended for a student taking CIT-593? | The course introduces foundational computer systems, heavily focusing on lower-level hardware concepts, assembly language, and C programming. |
| 4 | Is CIT-582 considered an intimidating or high-workload elective by student reviewers? | No, it is generally considered a lower-workload elective option, averaging roughly 7.95 hours per week with a lower difficulty profile. |
| 5 | What specific language backgrounds or toolsets are mentioned as helpful for data tracks like CIS-545? | Prior experience writing code in Python and R makes the tracking and data analysis workflows smoother for students. |
---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Context/Metric Fragment Splitting:** Because student reviews contain tight pairings of raw metrics and qualitative thoughts (e.g., stating "25 hrs/wk" immediately followed by an explanation of why the homework felt overwhelming), a mechanical character split risks separating the numerical statistic from its descriptive rationale, leaving the retrieved chunk missing half its context.
2. **General Knowledge Slippage & Drift:** If a user submits a query regarding a computer science elective or academic pathway not explicitly tracked within our 10 defined course documents, the underlying LLM could inadvertently rely on its native pre-training weights to generate general advice rather than strictly enforcing the grounding prompt to declare an absence of context.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```mermaid
graph TD
    A[Raw Text Files: documents/] -->|Milestone 3: Ingestion| B[Cleaning & Normalization Pipeline]
    B -->|Milestone 3: Character Splitting| C[500-Char Text Chunks + Source Metadata]
    C -->|Milestone 4: SentenceTransformer| D[(ChromaDB Local Vector Index)]
    E[User Query via Interface] -->|Milestone 4: Semantic Retrieval| D
    D -->|Top-k=4 Chunks + Sources| F[Grounded Prompts Configuration]
    F -->|Milestone 5: Groq Client Llama-3.3-70b| G[Cited & Grounded UI Output]

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
