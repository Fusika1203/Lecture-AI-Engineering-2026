# Lecture 05 Answers

## Exercises

- Answering model (`[model]` shown during execution): `gemini-3.5-flash-lite`
- Comparison question: "In Lecture 02, what does LoRA freeze and what does it train? What does QLoRA add?" (the same wording for every method)
- Target materials (also record the difference in scope between full context and the other methods): Full context reads all 8 documents in `lectures.json` (398 pages, 369,491 characters). Vector search, Tree, and Graph only cover the main materials for Lectures 01–03 (214 pages). So full context sees almost twice as many pages as the other methods, and the comparison is not under equal scope.

### Results by Method

| Method | Key points and correctness of the answer | Cited pages and evidence | Time (seconds) | Input/output tokens | Model responses | Estimated generation API cost (USD) |
|---|---|---|---|---|---|---|
| Full context | Correct. LoRA freezes the original weights W and trains only the two small matrices A and B (the low-rank delta). QLoRA also compresses W to 4 bits, about 1/4 of the memory, and still trains the LoRA adapters | Lecture 02 p.52 (= translated PDF p.75) and p.51. p.52 alone has all the evidence; p.51 (PEFT overview) also says "QLoRA: also compress the base model to 4 bits" | 3.83 | 95,824 / 261 | 1 | $0.029400 |
| Vector search | Correct, same key points as full context. LoRA freezes W and trains only A and B; QLoRA also compresses the frozen base weights to 4 bits | Lecture 2 p.52 for LoRA, pp.51–52 for QLoRA. Both pages were in the search results and both support the answer | 3.82 | 3,007 / 172 | 2 | $0.001332 |
| Tree | Correct, and a little more detail ("less than 1% of the total parameters" from p.52). It also added a long analogy that is not needed | It read the full text of p.52 only, which is enough. But the answer gives no page number, only the section name "When and how to adapt the selected model" | 5.84 | 9,442 / 309 | 5 | $0.003605 |
| Graph | Correct, same key points as vector search | Cites `[lec02-main-p051, lec02-main-p052]` (raw page IDs) and "slides 51 and 52". Both pages support the answer, but the format is not "Lecture N / PDF p.N" | 4.74 | 5,188 / 205 | 2 | $0.002069 |

<!-- State when a method was not run or a cost was unavailable. Use a separate table for each additional question. -->

### Question 2 (multi-page)

Question: "In the Lecture 03 examples, how does compaction differ from memory across sessions? Do all daily notes go into long-term memory?" Same model and settings as above.

Before running it, I read the evidence pages in `lectures.json`. Lecture 03 p.39 ("Example: Claude"): compaction works inside the context of the same session and replaces old history with a summary; memory (memory tool, auto memory) is external storage that is written out and loaded back across sessions. p.40 ("Example: OpenClaw"): a nightly review moves only what passes a threshold from the daily notes into `MEMORY.md`; one-off lookups stay in the daily notes. p.13 ("Memory") explains the general idea of writing out and loading back. For Lecture 03 the translated PDF page numbers are the same as the Japanese ones.

| Method | Key points and correctness of the answer | Cited pages and evidence | Time (seconds) | Input/output tokens | Model responses | Estimated generation API cost (USD) |
|---|---|---|---|---|---|---|
| Full context | Correct on both parts | p.38, 39 (compaction), p.13, 39 (memory), p.40 (daily notes). All support the answer | 4.35 | 95,828 / 364 | 1 | $0.029658 |
| Vector search | Correct on both parts | Translated PDF p.39 and p.65 for compaction vs. memory, p.40 for daily notes. p.65 ("Supplement: Latest developments in memory") also says compaction and file-based memory both "save and re-inject", so it is valid extra evidence | 5.86 | 6,420 / 277 | 3 | $0.002618 |
| Tree | **Not answered.** It read the full text of p.39 and p.40, then replied only with guiding questions ("Does it happen within the current context/session, or…?") and told me to read the two slides | Points to p.39 and 40, but gives no answer to check | 8.12 | 8,278 / 377 | 6 | $0.003426 |
| Graph | Correct on both parts | p.39 (compaction), pp.38–39 (memory), p.40 (daily notes) | 4.64 | 4,876 / 262 | 2 | $0.002118 |

- Pages found by running search alone, and what their text confirmed: I ran `uv run python -m app.retrieval "LoRA QLoRA difference"`. All 5 results come from Lecture 02, section "When and how to adapt the selected model".
  1. p.52 (= translated PDF p.75) "LoRA and QLoRA: adapting a large model on one GPU": the evidence page, ranked first. It says W is frozen, only A and B are trained, and QLoRA stores W at 4 bits (about 1/4 of the memory).
  2. p.51 "PEFT: train only part of a model": also supports the answer. It has one line each for LoRA and QLoRA, but less detail than p.52.
  3. p.60 "Today's exercise: correct output format with QLoRA": mentions QLoRA, but only as the exercise tool. It does not say what is frozen or trained.
  4. Translated PDF p.79 "Evidence and debate: RAG often works better for adding knowledge": mentions LoRA (it "learns less and forgets less"), but it is about FT vs. RAG, not the question.
  5. p.61 "Exercise steps and deliverables": only says "Train with QLoRA". Similar words, no evidence.
  - So 2 of the 5 pages are real evidence, and the other 3 only share the terms. Search alone does not show a score, so from the output I cannot tell how close the evidence pages were to the others.
- Tool calls shown by `--trace` (names, arguments, counts, table-of-contents paths followed by Tree, etc.):
  - Vector search: 1 call, `search_materials({'query': 'LoRA freeze train QLoRA add'})`. The model wrote its own keyword query from the question, searched once, and answered (2 model responses: one to call the tool, one to answer). The trace only shows the start of the tool result, so I ran the same query with `search()` to see all 5 pages and their cosine distances: p.52 (0.275), p.51 (0.281), p.47 "Evidence and debate: RAG often works better" (0.316), p.60 (0.319), p.61 (0.338). Compared with my STEP 2 query, p.47 replaced translated PDF p.79 (the same slide under a different page label), and the top 2 stayed the same.
  - Tree: 4 calls, 5 model responses. Path: `browse_tree({})` (lecture list) → `lec02-main` → section `lec02-main-s045` "When and how to adapt the selected model" → page `lec02-main-p052` (1,238 characters of full text). It went straight to the right page without backtracking. The section list showed 18 page titles, and it picked p.52 by its title. The "first sentence" preview did not help: for almost every page in that section the preview is just the slide header "4/4: when and how to adapt the selected model".
  - Graph: 1 call, `search_graph({'query': 'Lecture 02 LoRA freeze train QLoRA'})`. I ran the same query with `search_graph()` to see what came back: 3 seeds (p.52, p.60, p.51) and 7 expanded pages, 10 pages and 11,019 characters in total. 6 of the 7 expanded pages came through `next_page` edges (p.53, p.59, p.61, p.50, then p.62 and p.49 at 2 hops). Only p.47 came through a term (p.52 → LoRA → p.47).
  - Question 2, vector search: 2 calls. `search_materials('compaction memory sessions daily notes long-term memory')` returned p.65, 38, 39, 40, 13, so all three evidence pages were already there (distances 0.323–0.360, very close together). Then the model searched again with `'OpenClaw memory daily notes long-term memory threshold'`, which put p.40 first (0.257).
  - Question 2, Tree: 5 calls, 6 model responses. Path: lecture list → `lec03-main` → section `lec03-main-s037` (Part 6 Memory) → page p.39 → page p.40. It found the right section from its title and read both evidence pages. It did not read p.13, which is in another section (Part 2).
  - Question 2, Graph: 1 call. Seeds were p.65, p.39, p.38, so vector search alone missed p.40 this time. The graph added it as the next page after p.39 (1 hop). The other 6 expanded pages were not evidence (p.64, 66, 63, 67 are other "Supplement" pages, p.37 is the Part 6 title page, p.41 is about Skills).
- Examples where retrieved information was insufficient, or was retrieved but not used in the answer:
  - Full context: no input-limit error, and the answer used the right evidence. One small citation problem: for the QLoRA point it wrote "Japanese source p.51, p.52 · corresponding translated PDF p.75". In `page_sources.json` only p.52 maps to translated PDF p.75. p.51 is a new translation with no page in the translated PDF. The answer is right, but the citation mixes two pages under one label.
  - Vector search: the evidence was retrieved and used correctly. The 3 noise pages (p.47, p.60, p.61) were not cited. But the answer cites "p.52", which is the Japanese source page number. In the English PDF that slide is p.75, so a reader checking the English slides would not find it on p.52.
  - Tree: the right page was read and used, but the answer has no page citation at all, so I could not check it without the trace.
  - Graph: both evidence pages were already seeds (found by plain vector search). None of the 7 expanded pages added evidence for this question; they are neighbors such as the Lecture 2 summary and "Next: AI agents". They only made the input longer (5,188 tokens vs. 3,007 for vector search).
  - Question 2, Tree: the clearest "retrieved but not used" case. It read exactly the right pages (p.39 and p.40), but answered with hints only. I think the cause is the instruction "Guide learners with hints on how to think, rather than writing homework answers for them" (it is in all four instruction sets), and my question looked like a homework question. The other three methods have the same line and still answered, so this run alone does not show whether Tree is more affected or it was just this run.
  - Question 2, Graph: a case where the graph helped. The vector seeds missed p.40, and the `next_page` edge from p.39 brought it in. Here "adjacent page" worked because p.39 and p.40 are two examples on the same topic.
- Method you would adopt for this use case, your reasons, and limitations of the comparison conditions: For a Q&A assistant over lecture slides, I would use vector search. It was correct on both questions, cost the least (3,007 and 6,420 input tokens), and gave page numbers I could check. On question 2 the model fixed a weak first search by itself with a second query. Graph is a good backup for questions that span adjacent slides (it found p.40 when the seeds missed it), but on question 1 it only added noise. I would not use full context: it was always correct, but it used about 15–32 times more input tokens and about 11–22 times the estimated cost per question and would not scale to more lectures. Limitations: full context covered 398 pages and the others 214; each method ran only once per question; and both questions are short and use the same words as the slides, so they are easy for vector search.
- Observations and questions:
  - Full context did not fail here. The cost is the problem: about 96,000 input tokens for one question, when the evidence is one page of about 700 characters. Every question pays for all 398 pages again.
  - Vector search gave the same correct answer with about 1/32 of the input tokens (3,007 vs. 95,824) and about 1/22 of the estimated cost ($0.001332 vs. $0.029400). The time was almost the same (3.82 s vs. 3.83 s), because search added one extra model response and an embedding call, while full context only needed one response.
  - The two evidence pages are closer to the query (0.275, 0.281) than the noise pages (0.316 and more). The gap is small (about 0.035), so a fixed distance cut-off might work for this question but I am not sure it would work for others.
  - All four methods answered this single-page question correctly. They differ in cost and in the citation format: full context and vector search give page numbers (Japanese source numbers), Graph gives raw page IDs, and Tree gives none. For my own use, a correct answer that I cannot trace back to a page is less useful.
  - Tree is the most expensive of the three search methods (5 responses, 9,442 tokens), because the model reads a long table of contents at each level. For a single-page question this structure gives no benefit over one vector search.
  - Graph expands by position (next page), not by meaning. On question 1 the adjacent slides were not evidence; on question 2 one adjacent slide (p.40) was exactly the missing evidence. Whether "next page" helps depends on how the slides are ordered.
  - Each method needed more model responses on question 2 (vector 2 → 3, Tree 5 → 6), but the input tokens grew only for vector search (3,007 → 6,420) because it searched twice.
  - **My question:** Tree reached the right pages on both questions only through page titles, because the first-sentence previews are mostly slide headers ("4/4: …"). Would Tree still work on slides whose titles do not match the question's words?

## Homework

<!-- Completing any one of Basic, Implementation, or Advanced is sufficient. -->

- Level attempted: Advanced

- What you did (files, settings, or processing changed, or retrieval method designed): I built "Graph v2", a change to how the Graph method chooses candidate pages. The data stay the same: one page per chunk in `lectures.json`, the page/term graph in `graph.json`, and one 768-dimensional vector per page in `index.sqlite3`. I did not rebuild the index.

  - **Why I changed Graph.** In the Exercises, the original Graph returned 10 pages, and most of the expanded pages were noise. It ranks expanded pages by hop count and term rarity, not by how close they are to the question. I also looked at the graph itself. Of the 72 terms, 27 appear on no page in Lectures 01–03, and a few are hubs ("AI agent" on 54 pages, "Tool" on 45, "Fine-tuning" on 39). Two hops from 3 seeds already reach 100–112 of the 214 pages. So I did not add the unused `related_term` edges: they would make the pool even bigger.
  - **Design (in `app/retrieval.py`, `search_graph_v2`).**
    1. Same seeds (vector top 3) and the same candidate pool as the original Graph (`next_page` and `mentions`, up to 2 hops).
    2. Drop section cover pages. I use the rule "page title == section name". It matches 15 pages, all under 230 characters, such as "Part 5 Structured output and tool calls".
    3. Split the pool by relation. A 1-hop candidate can only be an adjacent slide (same flow of the lecture). A 2-hop candidate is almost always a page sharing a term with a seed (same topic, possibly another section or lecture).
    4. Rank each group by cosine distance to the query, using the vectors already stored in the index. The query is embedded once, as in the original, so there are no extra API calls.
    5. Keep the 2 closest adjacent pages and the 1 closest term page (`GRAPH_V2_ADJACENT = 2`, `GRAPH_V2_TERM = 1` in `app/config.py`). Together with the 3 seeds that is at most 6 pages instead of 10.
  - **A first version that failed.** My first version ranked the whole pool by distance and kept the top 3. On Question 1 it lost p.34 ("Structured output"). With a pool of 112 pages, "closest in the pool" becomes almost the same as global vector search, so the graph structure stopped mattering. Ranking by hops first fixed Question 1 but lost p.13 on Question 2. Separate slots for the two relations kept the needed page in both cases.
  - **Keeping the comparison fair.** `--graph2` registers the new function under the same tool name (`search_graph`), with the same description and the same `GRAPH_INSTRUCTIONS`, so the model cannot tell the two Graph modes apart. To check whether a gain comes from the graph or just from "more pages", I also ran basic RAG with 6 results (`AIE_RAG_TOP_K=6`, a new environment override in `app/config.py`). I refactored the original `search` and `search_graph` into shared helpers and checked that they still return exactly the same results as before on 31 stored page vectors used as queries. `tests/test_graph_v2.py` adds 5 tests that use stored vectors, so no API calls (22 tests pass in total).
  - I used an AI coding assistant to write the code. I ran every command myself, and I checked the evidence pages and the answers against `lectures.json`.

- Comparison question and conditions held fixed (model, target materials, etc.): Model `gemini-3.5-flash-lite`; the same 214 pages (Lectures 01–03); same instructions; one run per method and question.
  - Question 1 (spans two lectures): "Lecture 02 says fine-tuning can fix the output format. How does Lecture 03 get structured output instead, and what does constrained decoding add?" Evidence I identified first: Lecture 02 p.53 (FT changes output format, but try prompts and the API's format controls first; this also confirms the premise of the question), Lecture 03 p.34 (define a schema, then have the model return JSON), and p.35 (constrained decoding drops next-token candidates that do not fit the schema, so non-conforming output is never generated).
  - Question 2 (spans two sections, the same as Question 2 in the Exercises): evidence Lecture 03 p.13 (Part 2), p.39, and p.40 (Part 6).
  - With the full question text as the query, vector top 5 missed p.34 on Question 1 (it was 9th) and p.13 on Question 2 only just made it (5th). Graph v2 returned all 3 evidence pages for both questions in 6 pages (about 5,400–5,500 characters, against 9,300–11,000 for the original Graph). Without "Lecture 02/03" in Question 1, vector search did worse, and p.34 fell out of the top 10.

- Results (answers and evidence before/after, `--trace` output, time, token counts, estimated generation API cost, etc.): The pages each run received were checked by rerunning the agent's own query (logs in `lectures/05/logs/homework/`).

  **Question 1**

  | Method | Answer | Pages received (evidence) | Time (s) | Input/output tokens | Responses | Est. cost (USD) |
  |---|---|---|---|---|---|---|
  | Vector top 5 | Correct; cites p.34, p.35, p.62 | 2 searches ("Lecture 03 structured output constrained decoding", "… schema json"), 7 different pages; all 3 evidence pages | 5.94 | 6,453 / 379 | 3 | $0.002883 |
  | Vector top 6 | Correct; cites p.34, p.35, p.62 | 2 searches, 8 different pages; all 3 | 6.24 | 7,098 / 281 | 3 | $0.002832 |
  | Graph (original) | Correct, but **no page citations** | 1 search, 10 pages; all 3 | 4.02 | 4,501 / 252 | 2 | $0.001980 |
  | Graph v2 | Correct, but partly written as hints ("Review Lecture 3, pages 34–35… Consider: …"); cites p.34–35 | 1 search, 6 pages; p.34 and p.35, **not p.53** | 3.94 | 3,013 / 246 | 2 | $0.001519 |

  **Question 2**

  | Method | Answer | Pages received (evidence) | Time (s) | Input/output tokens | Responses | Est. cost (USD) |
  |---|---|---|---|---|---|---|
  | Vector top 5 (Exercise run) | Correct; cites p.39, p.65, p.40 | 2 searches; all 3 | 5.86 | 6,420 / 277 | 3 | $0.002618 |
  | Vector top 6 | Correct; cites p.13, p.39, p.40, p.65 | 1 search, 6 pages; all 3 | 4.30 | 2,879 / 266 | 2 | $0.001529 |
  | Graph (Exercise run) | Correct | 1 search, 10 pages; **missed p.13** | 4.64 | 4,876 / 262 | 2 | $0.002118 |
  | Graph v2 | Correct; cites p.38–39, p.39, p.40 | 1 search, 6 pages; all 3 (p.13 through the term "Memory": p.65 → Memory → p.13) | 4.02 | 3,179 / 279 | 2 | $0.001651 |

- Examples of improvements and remaining failures or limitations:
  - Improvement: against the original Graph, v2 used fewer input tokens on both questions (3,013 vs. 4,501; 3,179 vs. 4,876), and on Question 2 it also found p.13, a page in another section that the original Graph and Tree both missed.
  - Improvement: on Question 1, v2 needed one search, while basic RAG searched twice and used about twice the input (6,453 tokens).
  - Not what I expected: when the agent writes its own short query ("Lecture 03 structured output constrained decoding") instead of passing my full question, basic RAG finds p.34 easily, so on Question 1 the agent with basic RAG did not fail. The gap I measured with the full question did not show up in the agent runs. The real gain is efficiency, not correctness.
  - Failure: the agent's query left out Lecture 02, and v2's single term slot went to p.62 (the Appendix on structured output) instead of p.53. The original Graph, with 10 pages, still had p.53. None of the four answers really used p.53, because the question only states it as a premise, so the answer did not suffer this time.
  - Failure: the cover-page rule only applies to expanded pages. A cover page can still come in as a seed (p.33 did on Question 1).
  - Limitation: basic RAG with 6 results was as good as v2 on Question 2 and even cheaper (2,879 tokens). So for these questions, part of the gain comes from the smaller page budget, not only from the graph.
  - Limitation: one run per setting and two questions. Basic RAG needed 2 searches for Question 2 in the Exercise run, but only 1 with 6 results, which may be run-to-run variation. The slot sizes (2 + 1) were chosen while looking at these two questions, so they may not generalize.

- Observations and questions:
  - Would I adopt it? For lecture Q&A, I would keep basic vector search as the default and use Graph v2 instead of the original Graph when I want related pages in one call. v2 is cheaper than the original Graph and finds pages across sections, but it did not beat basic RAG with a similar page budget on correctness.
  - The most useful thing I learned is that "more relations" can make retrieval worse. With hub terms, two hops reach half of the materials, and ranking that pool by distance is just vector search again. The structure only helps if adjacent pages and term pages are treated as different signals.
  - Answer style changed between runs with the same instructions (v2 on Question 1 gave partial hints, as Tree did in the Exercises). The hint instruction affects correctness checks as much as retrieval does.
  - **My question:** the agent rewrites the question into a short query, and that rewrite decided more than the retrieval method did. Should a retrieval comparison fix the query (call the retriever directly), or measure the full agent like this homework does?
