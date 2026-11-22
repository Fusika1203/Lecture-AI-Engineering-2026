# Lecture 05 Answers

## Exercises

- Answering model (`[model]` shown during execution): `gemini-3.5-flash-lite`
- Comparison question: "In Lecture 02, what does LoRA freeze and what does it train? What does QLoRA add?" (the same wording for every method)
- Target materials (also record the difference in scope between full context and the other methods): Full context reads all 8 documents in `lectures.json` (398 pages). Vector search, Tree, and Graph cover only the main materials for Lectures 01–03 (214 pages).

### Results by Method

| Method        | Key points and correctness of the answer                                                                                                                                               | Cited pages and evidence                                                                                                                                 | Time (seconds) | Input/output tokens | Model responses | Estimated generation API cost (USD) |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------------- | --------------- | ----------------------------------- |
| Full context  | Correct. LoRA freezes the original weights W and trains only the two small matrices A and B (the low-rank delta). QLoRA also compresses W to 4 bits and still trains the LoRA adapters | Lecture 02 p.52 (= translated PDF p.75) and p.51. p.52 alone has all the evidence, and p.51 (PEFT overview) also mentions the 4-bit compression in QLoRA | 3.83           | 95,824 / 261        | 1               | 0.029400                            |
| Vector search | Correct, with the same key points as full context                                                                                                                                      | Lecture 02 p.52 for LoRA and pp.51–52 for QLoRA. Both pages were in the search results, and both support the answer                                      | 3.82           | 3,007 / 172         | 2               | 0.001332                            |
| Tree          | Correct, with a little more detail ("less than 1% of the total parameters" from p.52), plus a long analogy that was not needed                                                         | It read only the full text of p.52, which is enough. However, the answer gives no page number, only the section name                                     | 5.84           | 9,442 / 309         | 5               | 0.003605                            |
| Graph         | Correct, with the same key points as vector search                                                                                                                                     | It cites raw page IDs (`lec02-main-p051`, `lec02-main-p052`). Both pages support the answer, but the format is not "Lecture N / PDF p.N"                 | 4.74           | 5,188 / 205         | 2               | 0.002069                            |

<!-- State when a method was not run or a cost was unavailable. Use a separate table for each additional question. -->

### Question 2 (multi-page)

Question: "In the Lecture 03 examples, how does compaction differ from memory across sessions? Do all daily notes go into long-term memory?" The same model and settings were used as above.

Before running it, the evidence pages were checked in `lectures.json`. Lecture 03 p.39 ("Example: Claude") explains that compaction works inside one session and replaces old history with a summary, while memory is external storage that is written out and loaded back across sessions. p.40 ("Example: OpenClaw") explains that a nightly review moves only what passes a threshold from the daily notes into `MEMORY.md`, and one-off lookups stay in the daily notes. p.13 ("Memory") explains the general idea. For Lecture 03, the translated PDF page numbers are the same as the Japanese ones.

| Method        | Key points and correctness of the answer                                                                                             | Cited pages and evidence                                                                                                                     | Time (seconds) | Input/output tokens | Model responses | Estimated generation API cost (USD) |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------------- | --------------- | ----------------------------------- |
| Full context  | Correct on both parts                                                                                                                | p.13, 38, 39, and 40. All of them support the answer                                                                                         | 4.35           | 95,828 / 364        | 1               | 0.029658                            |
| Vector search | Correct on both parts                                                                                                                | p.39 and p.65 for compaction vs. memory, and p.40 for daily notes. p.65 ("Supplement: Latest developments in memory") is also valid evidence | 5.86           | 6,420 / 277         | 3               | 0.002618                            |
| Tree          | **Not answered.** It read the full text of p.39 and p.40, but replied only with guiding questions and told me to read the two slides | It points to p.39 and p.40, but there is no answer to check                                                                                  | 8.12           | 8,278 / 377         | 6               | 0.003426                            |
| Graph         | Correct on both parts                                                                                                                | p.38, 39, and 40                                                                                                                             | 4.64           | 4,876 / 262         | 2               | 0.002118                            |

- Pages found by running search alone, and what their text confirmed: Running `uv run python -m app.retrieval "LoRA QLoRA difference"` returned 5 results, all from the same Lecture 02 section. p.52 ("LoRA and QLoRA: adapting a large model on one GPU") ranked first, and its text confirms that W is frozen, only A and B are trained, and QLoRA stores W at 4 bits. p.51 (PEFT) ranked second and also supports the answer, but with less detail. The other three pages (p.60, p.61, and the "Evidence and debate" slide) only share the words LoRA or QLoRA and do not answer the question.
- Tool calls shown by `--trace` (names, arguments, counts, table-of-contents paths followed by Tree, etc.):
  - Vector search: 1 call, `search_materials({'query': 'LoRA freeze train QLoRA add'})`. The model wrote its own keyword query, searched once, and then answered.
  - Tree: 4 calls. Path: lecture list → `lec02-main` → section "When and how to adapt the selected model" → page `lec02-main-p052`. It went straight to the right page and chose it by its title. The first-sentence previews did not help, because for almost every page in that section, the preview is just the slide header "4/4: when and how to adapt the selected model".
  - Graph: 1 call, `search_graph({'query': 'Lecture 02 LoRA freeze train QLoRA'})`. It returned 3 seed pages (p.52, p.60, and p.51) and 7 expanded pages. Most of the expanded pages were neighboring slides, such as the Lecture 02 summary.
  - Question 2, vector search: 2 calls. The first search already returned all three evidence pages, and then the model searched again with "OpenClaw" in the query, which put p.40 first.
  - Question 2, Tree: 5 calls. Path: lecture list → `lec03-main` → section "Part 6 Memory" → p.39 → p.40. It did not read p.13, which is in another section.
  - Question 2, Graph: 1 call. The seed pages missed p.40, but the graph added it as the page after p.39.
- Examples where retrieved information was insufficient, or was retrieved but not used in the answer:
  - Full context: there was no input-limit error, and the answer used the right evidence. However, for the QLoRA point, it put p.51 and p.52 under one label, "translated PDF p.75", although only p.52 corresponds to that page.
  - Vector search: the evidence was retrieved and used correctly. However, the answer cites "p.52", which is the Japanese page number. In the English PDF, that slide is p.75.
  - Tree: it read and used the right page, but since the answer has no page citation, I could only check it through the trace.
  - Graph: both evidence pages were already among the seeds. The expanded pages added no evidence and only made the input longer.
  - Question 2, Tree: this is the clearest "retrieved but not used" case. It read exactly the right pages but answered only with hints. I think the cause is the instruction "Guide learners with hints on how to think, rather than writing homework answers for them", since my question looked like a homework question. The other methods have the same instruction and still answered, so one run is not enough to say whether Tree is more affected.
  - Question 2, Graph: here, the graph helped. The seeds missed p.40, and the next-page link from p.39 brought it in, because p.39 and p.40 are two examples on the same topic.
- Method you would adopt for this use case, your reasons, and limitations of the comparison conditions: For a Q&A assistant over lecture slides, I would use vector search. It was correct on both questions, cost the least, and gave page numbers that I could check. On Question 2, the model also improved a weak first search by itself. Graph is a good backup for questions that span adjacent slides, but on Question 1, it only added noise. I would not use full context: it was always correct, but it used more than ten times the input tokens and cost, and it would not scale to more lectures. Limitations: full context covered more pages than the other methods, each method ran only once per question, and both questions use the same words as the slides, which makes them easy for vector search.
- Observations and questions:
  - Full context did not fail here. The problem is cost: about 96,000 input tokens for one question, when the evidence is a single slide.
  - Vector search gave the same correct answer with about 3,000 input tokens. The time was almost the same (3.82 s vs. 3.83 s), because search adds an extra model response and an embedding call.
  - All four methods answered the single-page question correctly. They differ in cost and in how they cite pages: full context and vector search give Japanese page numbers, Graph gives raw page IDs, and Tree gives none. For my own use, a correct answer that I cannot trace back to a page is less useful.
  - Tree was the most expensive of the three search methods, because the model reads a long table of contents at each level. For a single-page question, this gives no benefit over one vector search.
  - Graph expands by position (the next slide), not by meaning. On Question 1, the adjacent slides were not evidence, but on Question 2, one adjacent slide was exactly the missing evidence.
  - **My question:** Tree found the right pages only through page titles, because the previews are mostly slide headers. Would Tree still work on slides whose titles do not match the words in the question?

## Homework

<!-- Completing any one of Basic, Implementation, or Advanced is sufficient. -->

- Level attempted: Advanced

- What you did (files, settings, or processing changed, or retrieval method designed): I built "Graph v2", which changes how the Graph method chooses candidate pages. The data stay the same (`lectures.json`, `graph.json`, and the vectors in `index.sqlite3`), so I did not rebuild the index.
  
  - **Why I changed Graph.** In the Exercises, the original Graph returned 10 pages, and most of the expanded pages were noise, because it ranks them by hop count and term rarity, not by how close they are to the question. Some terms in the graph are also very common (for example, "AI agent" appears on 54 of the 214 pages), so two hops from the seeds already reach about half of the pages. For this reason, I did not add the unused `related_term` edges, since they would make the candidate pool even bigger.
  - **Design (`search_graph_v2` in `app/retrieval.py`).**
    1. Use the same seeds (vector top 3) and the same candidate pool as the original Graph.
    2. Drop section cover pages, such as "Part 5 Structured output and tool calls", using the rule "page title == section name".
    3. Split the candidates by relation. A 1-hop candidate is an adjacent slide, and a 2-hop candidate is almost always a page that shares a term with a seed.
    4. Rank each group by cosine distance to the query, using the vectors already stored in the index, so there are no extra API calls.
    5. Keep the 2 closest adjacent pages and the 1 closest term page. With the 3 seeds, this gives at most 6 pages instead of 10.
  - **A first version that failed.** My first version ranked all candidates by distance and kept the top 3. On Question 1, it lost an evidence page (p.34), because with such a large pool, "closest in the pool" is almost the same as plain vector search. Ranking by hop count first fixed Question 1, but it lost an evidence page on Question 2. Giving the two relations separate slots kept the needed pages in both cases.
  - **Keeping the comparison fair.** `--graph2` registers the new function under the same tool name and description as `--graph`, with the same instructions, so the model cannot tell the two modes apart. To check whether a gain comes from the graph or just from the number of pages, I also ran basic RAG with 6 results (`AIE_RAG_TOP_K=6`). Tests were added in `tests/test_graph_v2.py`, and since they use stored vectors, they need no API calls.

- Comparison question and conditions held fixed (model, target materials, etc.): the model `gemini-3.5-flash-lite`, the same 214 pages, the same instructions, and one run per method and question.
  
  - Question 1 (spans two lectures): "Lecture 02 says fine-tuning can fix the output format. How does Lecture 03 get structured output instead, and what does constrained decoding add?" Evidence: Lecture 02 p.53 (fine-tuning can change the output format, which confirms the premise of the question), Lecture 03 p.34 (define a schema and have the model return JSON), and p.35 (constrained decoding drops tokens that do not fit the schema).
  - Question 2 (spans two sections, the same as Question 2 in the Exercises): evidence on Lecture 03 p.13, p.39, and p.40.
  - When I searched with the full text of Question 1, vector top 5 missed p.34, while Graph v2 returned all the evidence pages for both questions with 6 pages instead of 10.

- Results (answers and evidence before/after, `--trace` output, time, token counts, estimated generation API cost, etc.): The pages each run received were checked by running the agent's own search query again.
  
  **Question 1**
  
  | Method           | Answer                               | Pages received                                 | Time (s) | Input/output tokens | Responses | Est. cost (USD) |
  | ---------------- | ------------------------------------ | ---------------------------------------------- | -------- | ------------------- | --------- | --------------- |
  | Vector top 5     | Correct                              | 2 searches; all 3 evidence pages               | 5.94     | 6,453 / 379         | 3         | 0.002883        |
  | Vector top 6     | Correct                              | 2 searches; all 3                              | 6.24     | 7,098 / 281         | 3         | 0.002832        |
  | Graph (original) | Correct, but no page citations       | 1 search, 10 pages; all 3                      | 4.02     | 4,501 / 252         | 2         | 0.001980        |
  | Graph v2         | Correct, but partly written as hints | 1 search, 6 pages; p.34 and p.35, but not p.53 | 3.94     | 3,013 / 246         | 2         | 0.001519        |
  
  **Question 2**
  
  | Method                      | Answer  | Pages received                                            | Time (s) | Input/output tokens | Responses | Est. cost (USD) |
  | --------------------------- | ------- | --------------------------------------------------------- | -------- | ------------------- | --------- | --------------- |
  | Vector top 5 (Exercise run) | Correct | 2 searches; all 3                                         | 5.86     | 6,420 / 277         | 3         | 0.002618        |
  | Vector top 6                | Correct | 1 search, 6 pages; all 3                                  | 4.30     | 2,879 / 266         | 2         | 0.001529        |
  | Graph (Exercise run)        | Correct | 1 search, 10 pages; missed p.13                           | 4.64     | 4,876 / 262         | 2         | 0.002118        |
  | Graph v2                    | Correct | 1 search, 6 pages; all 3 (p.13 through the term "Memory") | 4.02     | 3,179 / 279         | 2         | 0.001651        |

- Examples of improvements and remaining failures or limitations:
  
  - Improvement: compared with the original Graph, v2 used fewer input tokens on both questions, and on Question 2, it also found p.13, a page in another section that the original Graph and Tree both missed.
  - Improvement: on Question 1, v2 needed only one search, while basic RAG searched twice and used about twice as many input tokens.
  - Not what I expected: the agent does not pass my full question to the search tool. It writes its own short query, and with that query, basic RAG found p.34 easily. So the gap that I saw with the full question did not appear in the agent runs, and the real gain was efficiency rather than correctness.
  - Failure: on Question 1, the agent's query left out Lecture 02, so the single term slot of v2 went to an appendix page instead of p.53. The original Graph, with 10 pages, still had p.53. Since the question only uses p.53 as a premise, the answer did not suffer this time.
  - Failure: the cover-page rule only applies to expanded pages, so a cover page can still come in as a seed.
  - Limitation: basic RAG with 6 results was as good as v2 on Question 2 and even cheaper. So part of the gain comes from the smaller number of pages, not only from the graph.
  - Limitation: each setting was run only once on two questions, and the slot sizes (2 + 1) were chosen while looking at these two questions, so they may not generalize.

- Observations and questions:
  
  - Would I adopt it? For lecture Q&A, I would keep basic vector search as the default, and I would use Graph v2 instead of the original Graph when I want related pages in one call. v2 is cheaper than the original Graph and finds pages across sections, but it did not beat basic RAG with a similar number of pages.
  - The most useful thing I learned is that more relations can make retrieval worse. When common terms connect half of the materials, ranking all the connected pages by distance turns into plain vector search again. The graph structure helps only when adjacent pages and term pages are treated as different signals.
  - With the same instructions, the answer style changed between runs (v2 on Question 1 gave partial hints, as Tree did in the Exercises), so the hint instruction affects the results as much as the retrieval method does.
  - **My question:** the agent rewrites the question into a short search query, and in my runs, that rewrite mattered more than the retrieval method. Should a retrieval comparison fix the query by calling the retriever directly, or measure the whole agent as this homework does?
