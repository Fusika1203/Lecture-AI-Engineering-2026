# Lecture 03 Answers

## Exercises

- *Differences between the Lecture 01 (bare LLM) and agent answers:*
  
  I asked both "What are the 3 homework levels in the AIE2026 course?" with `gemini-3.5-flash-lite`.
  
  `app.ask` said it has no information about "the AIE2026 course" and asked me to paste the syllabus. It did not make anything up this time, but it could not answer either (18 input tokens, 77 output tokens).
  
  `app.agent` answered correctly: Basic (review lecture content), Implementation (write your own code), and Advanced (research and experimentation). It also added that one level is enough, and it ended with "Lecture 01". This matches the `homework-levels` entry in `data/glossary.json` almost word for word, so the answer clearly came from the glossary and not from the model's own knowledge. It also followed the "give hints, not answers" rule and added a line asking me to think about which level fits my goals.

- *Tool calls shown by `--trace` (tool names and arguments):*
  
  For "What is the difference between LoRA and QLoRA?", there was only one call:
  
  ```text
  [tool call]   search_glossary({'query': 'LoRA'})
  [tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "A PEFT method that freezes pretrained weights, ...
  ```
  
  I expected a second search for "QLoRA", but it never happened. When I called `search_glossary('LoRA')` directly, it returned LoRA, Rank (LoRA r), and QLoRA, because of the partial match ("lora" is inside "qlora"). So the model already had both definitions after the first call and decided it did not need another search. The query had a single term, as the docstring asks.

- *Number of LLM calls for one question (`requests`):*
  
  `requests=2`, `tool_calls=1`. The first request decides to call `search_glossary`, and the second one writes the answer from the result. Input was 897 tokens (compared with 18 for `app.ask`), because the instructions, the tool descriptions, and the tool result are all sent to the model.

- *Tool added and the description in its docstring:*
  
  I added `make_quiz(lecture: int)` to `app/tools.py` and registered it with `agent.tool_plain(tools.make_quiz)`. It picks one random glossary term from the given lecture and returns JSON with `question` ("What does X mean?"), `answer` (the definition), and `lecture`. If the lecture has no terms, for example `lecture=0`, it returns "No glossary terms found for Lecture 00. Sessions with terms: 01, 02, 03, 04, 06" instead of raising an error.
  
  The docstring says to use it when the learner asks for a review question, a quiz, or a self-check, gives "Give me one review question from Lecture 02" as an example, and says to show only the question first and keep the answer until the learner has tried.
  
  Results: `--list-tools` shows `make_quiz` with the docstring, `uv run pytest -q` gives 15 passed, and `--trace "Give me one review question from Lecture 02"` shows `[tool call] make_quiz({'lecture': 2})` (`requests=2`). The agent replied with just "What does LoRA mean?" and kept the answer hidden. One thing I noticed: it did not end with "Lecture 02" this time, even though `INSTRUCTIONS` asks for that in every answer. My guess is that "show only the question" in the docstring won over the general rule. I did not change `INSTRUCTIONS`, because the model called the tool without any extra hint.

## Homework

- **Level attempted:** Advanced, option (a): rebuild the agent with Google ADK

- **What you did:**
  
  I added `adk_agent/glossary_agent/` with two files. `__init__.py` is just `from . import agent`, and `agent.py` builds the agent:
  
  ```python
  root_agent = Agent(
      model="gemini-3.5-flash-lite",
      name="glossary_agent",
      instruction=INSTRUCTIONS,
      tools=[tools.search_glossary, tools.get_lecture_summary, tools.make_quiz],
  )
  ```
  
  `INSTRUCTIONS` and the three tools are imported from `app/`, so the prompt and the tool code are exactly the same as in the exercise. I did not touch anything in `app/`.
  
  I ran it on my own Windows PC (Git Bash) with google-adk 2.14.0, which installed fine next to the pinned `google-genai==2.31.0`:
  
  ```bash
  PYTHONPATH=. uv run --with google-adk adk run adk_agent/glossary_agent
  ```
  
  I used the interactive mode once, and for the comparison I passed each question directly with `--in_memory --jsonl`. Plain `adk run` only prints the answer, but `--jsonl` prints every event, including `functionCall`, `functionResponse`, and token counts, so I could read the tool calls the same way as with `--trace`. `--in_memory` also stops ADK from creating a `.adk/` session folder in the repo. I asked the same three questions as in the exercise and ran some of them twice on both versions.
  
  I also tried `PYTHONPATH=. uv run --with google-adk adk web adk_agent` once. The Dev UI opened at http://127.0.0.1:8000 and listed `glossary_agent`, and the LoRA/QLoRA question gave the same result there (two `search_glossary` calls). Unlike my `--in_memory` runs, `adk web` saved the session to `adk_agent/glossary_agent/.adk/session.db`, so I added `.adk/` to `.gitignore` to keep it out of the commit.

- **Results:**
  
  | Question                                              | Pydantic AI (`app.agent --trace`)                                                                                                                                   | ADK (`adk run --jsonl`)                                                                                                                                                |
  | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | What are the 3 homework levels in the AIE2026 course? | Two traced runs, both the same: `get_lecture_summary` for lectures 1, 2, 3, and 4, then `search_glossary('homework')`. 5 tool calls, 6 requests, 9,096 input tokens | Two runs, both the same: one `search_glossary('homework levels')`. 2 requests, 1,113 input tokens                                                                      |
  | What is the difference between LoRA and QLoRA?        | Run 1: only `search_glossary('LoRA')` (897 tokens). Run 2: `LoRA` and then `QLoRA` (1,373 tokens). 2 requests both times                                            | `search_glossary('LoRA')` and `search_glossary('QLoRA')` in the same turn. 2 requests, 1,497 tokens                                                                    |
  | Give me one review question from Lecture 02           | `make_quiz({'lecture': 2})`, 2 requests. The first run replied with only "What does LoRA mean?" and no lecture number                                               | `make_quiz({'lecture': 2})`, 2 requests, 1,057 tokens. "Here is a review question from Lecture 02: What does Pretraining mean? Give it your best shot... (Lecture 02)" |
  
  The answers themselves were almost the same on both sides: same definitions, the same kind of "think about..." hint at the end, and the lecture number in brackets. That makes sense, since the instructions and tools are shared.
  
  In interactive mode I asked for a review question, got "What does Fine-tuning mean?", and answered "training only a small part of the model instead of all weights". The agent said I was actually describing PEFT, explained the difference, and asked a follow-up question. So the session remembered the quiz from the previous turn. Our `app.agent` CLI cannot do this, because it answers one question and exits.
  
  **Differences in the code:**
  
  - Model: ADK takes the model name when the agent is created. Pydantic AI gets the model at `run_sync(..., model=build_model())`, which is why the tests can swap in `TestModel` without an API key.
  - Tools: ADK takes a plain list in `tools=[...]`. Pydantic AI registers them one by one with `agent.tool_plain()`. Both read the function name, type hints, and docstring to build the tool description, so I did not have to change the tools at all.
  - Naming: ADK needs a `name`, the variable has to be called `root_agent`, and the folder needs an `__init__.py`, because `adk run` finds the agent by convention.
  - What comes for free: with ADK I got a chat loop, sessions, conversation history, and an event log (`--jsonl`) without writing any extra code. In `app/agent.py` we wrote `argparse`, `print_trace`, and `print_tools` ourselves. On the other hand, our own code is short and easy to read, and testing it without the API is simple.

- **Observations and questions:**
  
  The biggest surprise was the homework-levels question. Same model, same instructions, same tools, but the Pydantic AI version went through four lecture summaries before searching the glossary and used about eight times more tokens than ADK. The final answer was still correct. I ran it twice and got the same path both times, while ADK searched the glossary directly both times. I am not sure why. My guess is that the two frameworks send the tool descriptions to Gemini in slightly different ways (format, order, or how the docstring is parsed), and that is enough to change the model's first decision. I would like to know how to check what each framework actually sends to the model.
  
  The LoRA/QLoRA difference, on the other hand, does not look like a framework difference. Pydantic AI did one search in one run and two in the other, so it is normal variation. With only two runs each, I cannot say much more than that.
  
  ADK also used slightly more input tokens per request (1,497 vs 1,373 for the same two searches). I think ADK adds a few lines of its own to the system instruction, such as the agent name, but I have not checked this.
  
  Overall, ADK felt like a framework: you follow its folder layout and naming, and you get the CLI, the web UI, and sessions in return. Pydantic AI felt more like a library that you call from your own code. Pydantic AI makes it easier to see what is going on inside the loop, but if I wanted a chat app with memory quickly, ADK would save a lot of work.
