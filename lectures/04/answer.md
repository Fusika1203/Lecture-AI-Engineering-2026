# Lecture 04 Answers

## Exercises

- Agreement by criterion (before revision): Grounding 8/9, Scope 10/10, Hint 10/10, Clarity 9/10, Lecture marker 10/10 (overall 9/9, coverage 9/10 = 90%, model `gemini-3.5-flash-lite`)
  - Disagreements: #04 Clarity and #06 Grounding were both missed failures (LLM = pass, me = fail). For #04 the LLM called a repetitive answer ("In other words" twice) concise. For #06 it said the code "does not contradict any glossary entry".
- Number of items needing review (before revision): 1 (#05 Grounding, "What is RAG?")
- Criterion revised and the policy added: Grounding. Policy: fail. I added "A general explanation of an absent term counts as asserting guesses (fail), even if the answer first states that the term is not in the glossary" and removed the issue from "Unresolved Questions". My reason: the agent's job is to answer from the glossary, so anything beyond "it is not in the glossary" is unsupported, even if it is correct in general. The answer also guesses a related session ("Lecture 04").
- Agreement by criterion and number of review items (after revision): Grounding 8/9, Scope 10/10, Hint 10/10, Clarity 10/10, Lecture marker 10/10 (overall 9/9, coverage 90%). Items needing review: still 1. #05 Grounding stayed unsure.
  - I ran it a second time to check: #05 was unsure again, and Grounding dropped to 7/9 (#08 Grounding and #04 Clarity flipped to missed failures).
  - Why #05 did not change: the LLM's reason quotes the case's own expected behavior, which still says "The rubric has not yet decided whether a general explanation is acceptable". The reference and the rubric now disagree, and the LLM follows the reference. So the policy has to be written in both places, not only in the rubric.
- Items where your labels differed from the instructor's, and your reasons: Grounding on #05, #06, and #08 (I chose fail, the instructor chose pass; all other criteria agree). I read Grounding strictly: content not supported by the references fails, not only content that contradicts them. #05 adds a general definition and a guessed session. #06 asserts implementation details (file paths, `output_type`) that are not in the glossary entries. #08 prints glossary text without any glossary entry in the references, so it cannot be checked. The instructor reads Grounding as "no contradiction". The rubric's first line supports that reading, but its second line ("instead of asserting guesses") supports mine.
- **Observations and questions:**
  - The code check for the Lecture marker is strict: #07 (weather refusal, ends with "Related session: none") and #09 (empty input) are good answers but fail overall only because there is no "Lecture N". On the other hand, #10 passes the marker check with "Lecture 14", a session that does not exist. A format check cannot tell whether the marker makes sense.
  - The LLM is lenient on Clarity: it called #04 concise even though the rubric names this exact pattern as a failure.
  - Even with temperature 0, judgments on criteria I did not touch (#04 Clarity, #08 Grounding) changed between two runs with the same rubric. One run per rubric version is not enough to say whether an edit helped.
  - **My question:** in an earlier test with a "pass" policy, #05 became pass immediately. Does the LLM accept a lenient policy more easily than a strict one when the reference text is ambiguous?

## Homework

- Level attempted: Advanced

- What you did: I investigated GPQA Diamond. I downloaded the Diamond split from Hugging Face, answered 3 problems myself, and read the paper to find out who wrote the questions, how they were validated, and how answers are graded. I picked the subdomains based on my background (B.Sc. in Biotechnology, now an M.S. in AI): two biology questions close to my field and one chemistry question outside it. The answers and self-assessments are my own.
  
  - Dataset: https://huggingface.co/datasets/Idavidrein/gpqa (gated; config `gpqa_diamond`)
  - Paper: Rein et al., "GPQA: A Graduate-Level Google-Proof Q&A Benchmark", https://arxiv.org/abs/2311.12022

- Results:
  
  - **Problems I read** (summaries only)
    
    | #   | Domain / subdomain            | Writer's difficulty estimate | Validators correct (expert / non-expert) | My result              |
    | --- | ----------------------------- | ---------------------------- | ---------------------------------------- | ---------------------- |
    | 1   | Biology / Molecular Biology   | Hard undergraduate           | 2/2, 1/3                                 | Correct, about 2.5 min |
    | 2   | Biology / Genetics            | Hard graduate                | 2/2, 0/3                                 | Wrong, about 3.5 min   |
    | 3   | Chemistry / Organic Chemistry | Hard undergraduate           | 2/2, 1/3                                 | Wrong, about 30 s      |
    
    1. Molecular Biology (somewhat familiar): it mainly tests recall of specialized knowledge. I reasoned part of the way and chose correctly without any search. Hard for an LLM: it needs one precise, specialized fact, and a general explanation of the topic does not lead to the answer.
    2. Genetics (somewhat familiar): it asks for reasoning, not just recall. I tried, but I had forgotten the background I learned years ago, so in the end I guessed and got it wrong. None of the three non-expert validators got it right either. Hard for an LLM: chaining several reasoning steps correctly.
    3. Organic Chemistry (outside my field): I could not even tell what kind of reasoning was needed, so I guessed within 30 seconds. For me the barrier was the domain vocabulary itself, before any reasoning.
  
  - **Contributors**: 61 contractors hired through Upwork, all holding or pursuing a PhD in biology, physics, or chemistry. Average pay was about $95/hour, with bonuses tied to the result: a writer earned more when both experts answered correctly and when non-experts answered incorrectly.
  
  - **Creation and validation**: each question goes through five steps. (1) An expert writes the question, four options, and an explanation of why the answer is right and the distractors are wrong. (2) A second expert in the same domain answers it and gives feedback. (3) The writer may revise. (4) A third expert answers the revised question. (5) Three non-experts (PhD-level people from other domains) answer it with unlimited time and full web access, but no LLMs; they spent 37 minutes per question on average.
  
  - **Filtering**: 564 questions were written. 18 were held out, leaving 546 (Extended). The Main set keeps 448. Diamond keeps only 198, where both experts answered correctly (or the second expert made a clearly explained mistake) and at most one of the three non-experts did. So about 64% of the Extended questions did not make it into Diamond.
  
  - **Grading**: four-option multiple choice, scored by accuracy against the single correct option. Random guessing gives 25%. In the paper, experts reached 81.3% on Diamond, non-experts 22.1%, and GPT-4 with few-shot chain of thought 38.8%.
  
  - **Comparison with the Lecture 04 evaluation set**
    
    |                      | GPQA Diamond                                       | Lecture 04 set                                                                   |
    | -------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------- |
    | Size                 | 198 (filtered from 564)                            | 10                                                                               |
    | Authors              | 61 PhD-level experts                               | 1 instructor                                                                     |
    | Validation per item  | 2 experts + 3 non-experts, plus one revision round | Instructor's own labels; each student labels again, and disagreement is expected |
    | Rejected items       | Most questions filtered out by validator agreement | None; edge cases are included on purpose                                         |
    | What "correct" means | One correct option, agreed by two experts          | Pass conditions on 4 criteria, with no single reference answer                   |
    | Grading              | Exact answer matching (code)                       | LLM judge for 4 criteria, code for the Lecture marker, humans for unsure items   |
    | Subjective criteria  | None                                               | Clarity, by design                                                               |
    | Purpose              | Measure the capability of frontier models          | Check whether the LLM grader can be trusted for our own agent                    |

- **Observations and questions:**
  
  - GPQA spends most of its effort before grading: many experts and strict filtering make sure each item has one defensible answer, so grading can be a simple string match. Our set does the opposite: the answers are open-ended, so the effort moves into the rubric and into checking the grader against human labels.
  - Even in GPQA, the expert validators agreed with the answer only 65% of the time (74% after discounting clear mistakes). This matches the lecture's point that reference labels can be wrong, and that the instructor's labels in Lecture 04 are not an answer key.
  - My score (1/3) is close to the non-expert accuracy in the paper (22% on Diamond), even though two questions were in biology, near my background. Knowledge I learned years ago was not enough; the questions need current, specialized expertise, which is exactly what the expert/non-expert filter selects for.
  - **My question:** the leaderboard on the Hugging Face dataset page shows top models at around 90–94% on Diamond, higher than the 81% of the expert validators in the paper. Once models pass the experts who validated the questions, are the remaining errors model mistakes or mistakes in the reference answers? And how useful is the benchmark after that point?
