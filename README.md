# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
The chosen domain covers course-level feedback, workload expectations, and student experiences within the Master of Computer and Information Technology (MCIT) program. While official university syllabi describe assignments and grading weights, they fail to capture the qualitative, subjective realities of the student journey (e.g., navigating programming paradigm shifts or extreme shifts in workload). This knowledge base aggregates peer insights to allow students to make highly strategic enrollment decisions.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->
The knowledge base utilizes 10 distinct local raw text data files, with each file representing a comprehensive historical log of anonymous student reviews sourced from MCIT Central:

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:** MCIT Central reviews are fundamentally short-form, opinion-dense, and highly localized blocks of text. A small, conservative chunk size of 500 characters prevents individual course insights or highly specific workload figures from being structurally diluted by neighboring reviews within the vector space. The 100-character overlap provides a safety buffer ensuring that continuous context—such as a student shifting from an introductory point to a deeply nuanced observation about exam difficulty or a specific software framework—is not cleanly severed mid-sentence by a mechanical splitting boundary.

**Final chunk count:** 1524

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `sentence-transformers` (`all-MiniLM-L6-v2`)

**Production tradeoff reflection:**
If deploying this for a production-grade university tool, I would weigh:
1. **API vs. Local Latency/Cost:** Moving to an API-driven model like `text-embedding-3-small` offloads local compute constraints but introduces perpetual operational token expenses.
2. **Context Window Limitations:** The local model is bound to a strict 256-token context limit. For incredibly descriptive multi-paragraph narratives, an enterprise embedding model with expanded context boundaries would capture long-form thematic dependencies.
3. **Domain Vocabulary:** Standard embedding spaces easily tokenize generalized vocabulary but struggle to capture hyper-specific technical structures (e.g., semantic confusion between similar course codes like "CIT-591" and "CIT-594"). In production, implementing hybrid lexical search (BM25 + semantic) would resolve exact-match numerical alignment challenges.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->



**System prompt grounding instruction:**
Grounding is enforced through a strict system prompt and pipeline structure. The system prompt explicitly instructs the Groq model (`llama-3.3-70b-versatile`): *"You must answer the user's question USING ONLY the provided context documents. If the provided documents do not contain enough information to answer the question, you must explicitly say 'I don't have enough information on that.' Do NOT use your general knowledge."* Additionally, temperature is set to `0.1` to reduce creative hallucination, and source citations are programmatically attached to the UI output rather than relying on the LLM to manually cite them.

**How source attribution is surfaced in the response:**
Source attribution is guaranteed programmatically rather than relying on the LLM to cite its sources. When the user submits a query, the Gradio UI application intercepts the metadata (`retrieved_sources[i]['source']`) attached to the top-4 chunks returned by ChromaDB. It strips the duplicate filenames, formats them into a bulleted list, and renders them in a dedicated, separate "Retrieved From" UI textbox directly alongside the LLM's text output.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the primary difficulty students face in the second half of CIT-591? | Shifting programming paradigms and habits from Python to Java classes, methods, and debugging. | "I don't have enough information on that. The provided context documents do not mention the specific difficulties students face in the second half of CIT-591. They do discuss the difficulties and structure of CIT-594..." | Off-target | Inaccurate |
| 2 | How many hours per week on average do students spend on CIT-596 compared to CIT-594? | CIT-596 demands a significantly higher weekly workload (averaging ~19.84 hours) compared to CIT-594 (averaging ~10.69 hours). | "I don't have enough information on that. The provided context documents do not contain information about the average hours per week spent on CIT-596, only CIT-593, CIT-592, and CIT-594." | Off-target | Inaccurate |
| 3 | What is covered or recommended for a student taking CIT-593? | The course introduces foundational computer systems, heavily focusing on lower-level hardware concepts, assembly language, and C programming. | Mentions recommendations not to take it with 592, repetitive homework paying off, but mixes up discrete math (592) with 593. | Partially relevant | Partially Accurate |
| 4 | Is CIT-582 considered an intimidating or high-workload elective by student reviewers? | No, it is generally considered a lower-workload elective option, averaging roughly 7.95 hours per week with a lower difficulty profile. | "I don't have enough information on that. The provided context documents do not mention CIT-582. They only discuss CIT-591, CIT-594, and CIT-596." | Off-target | Inaccurate |
| 5 | What specific language backgrounds or toolsets are mentioned as helpful for data tracks like CIS-545? | Prior experience writing code in Python and R makes the tracking and data analysis workflows smoother for students. | Mentions LC-4 assembly, VS Code, and explicitly admits it is inferring Python/R from general knowledge: "Based on the course description, it can be inferred that proficiency in languages such as Python, R... might be helpful. But this is not explicitly mentioned." | Off-target | Inaccurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
What is the primary difficulty students face in the second half of CIT-591?

**What the system returned:**
"I don't have enough information on that. The provided context documents do not mention the specific difficulties students face in the second half of CIT-591. They do discuss the difficulties and structure of CIT-594..."

**Root cause (tied to a specific pipeline stage):**
This is a Retrieval Failure tied directly to the semantic embedding step. The `all-MiniLM-L6-v2` model relies on dense semantic similarity rather than exact keyword matching. Because the query contained strong descriptive words ("difficulty", "second half"), the vector search over-indexed on those emotional concepts and returned reviews from the program's notoriously difficult courses (like CIT-594) rather than the specific course requested. The exact course ID (CIT-591) was outweighed in the vector space, pushing the relevant chunk out of the top-k results.

**What you would change to fix it:**
To fix this, I would implement a hybrid search approach that combines dense semantic search with sparse keyword search (BM25). This would ensure that exact programmatic matches (like "CIT-591") carry enough weight to retrieve the correct course document, while the semantic search handles the conceptual part of the query.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Defining the exact evaluation questions and expected ground-truth answers in `planning.md` beforehand made diagnosing retrieval failures incredibly straightforward. Instead of guessing whether the LLM was hallucinating or if the data simply didn't exist, I knew exactly what chunks *should* have been retrieved, which made identifying the embedding model's vocabulary tradeoff very clear.

**One way your implementation diverged from the spec, and why:**
During the Milestone 3 ingestion phase, the initial plan was to only perform basic whitespace cleaning. However, upon inspecting the raw MCIT Central data, we discovered `` citation anchors littered inline throughout the text. We diverged from the original spec by implementing a specific regex (`r'\[[^\]]*\]'`) to cleanly wipe these artifacts out before chunking, ensuring the ChromaDB vector space wasn't polluted by irrelevant numerical IDs.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I provided the AI with a sample of the raw course text containing inline citation markers like `` and asked it to write a regex to clean them out during the `pipeline.py` ingestion step.
- *What it produced:* It initially produced a faulty regex (`r'\'`) that threw a Python `SyntaxError: unterminated string literal` when run in my WSL terminal.
- *What I changed or overrode:* I rejected its follow-up suggestion and instead proposed an alternative, catch-all bracket-matching logic (`r'\[[^\]]*\]'`). We implemented my logic, which successfully stripped the artifacts without crashing the script.

**Instance 2**

- *What I gave the AI:* I provided the Milestone 5 requirements and asked the AI to generate the Gradio UI and connect it to the Groq `llama-3.3-70b-versatile` client, specifically instructing it to enforce strict grounding.
- *What it produced:* It produced the `app.py` integration script containing the Gradio blocks and the system prompt logic.
- *What I changed or overrode:* I reviewed the generated code to verify and enforce that the LLM `temperature` was explicitly locked at `0.1` to prevent creative hallucination. I also ensured that source citations were being programmatically extracted from the ChromaDB metadata and appended to a separate UI textbox, actively overriding any reliance on the LLM to format its own citations in the response.