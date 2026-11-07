# Lecture 03 Answers

## Exercises

- Differences between the Lecture 01 (bare LLM) and agent answers:

  I asked both "What are the 3 homework levels in the AIE2026 course?" with `gemini-3.5-flash-lite`.

  `app.ask` said it has no information about "the AIE2026 course" and asked me to paste the syllabus. It did not make anything up this time, but it could not answer either (18 input tokens, 77 output tokens).

  `app.agent` answered correctly: Basic (review lecture content), Implementation (write your own code), and Advanced (research and experimentation). It also added that one level is enough and that homework is not graded, and it ended with "Lecture 01". This matches the `homework-levels` entry in `data/glossary.json` almost word for word, so the answer clearly came from the glossary and not from the model's own knowledge. It also followed the "give hints, not answers" rule and added a line asking me to think about which level fits my goals.

- Tool calls shown by `--trace` (tool names and arguments):

  For "What is the difference between LoRA and QLoRA?" there was only one call:

  ```text
  [tool call]   search_glossary({'query': 'LoRA'})
  [tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "A PEFT method that freezes pretrained weights, ...
  ```

  I expected a second search for "QLoRA", but it never happened. When I called `search_glossary('LoRA')` directly, it returned LoRA, Rank (LoRA r), and QLoRA, because of the partial match ("lora" is inside "qlora"). So the model already had both definitions after the first call and decided it did not need another search. The query had a single term, as the docstring asks.

- Number of LLM calls for one question (`requests`):

  `requests=2`, `tool_calls=1`. The first request decides to call `search_glossary`, and the second one writes the answer from the result. Input was 897 tokens (compared with 18 for `app.ask`), because the instructions, the tool descriptions, and the tool result are all sent to the model.

- Tool added and the description in its docstring:

  I added `make_quiz(lecture: int)` to `app/tools.py` and registered it with `agent.tool_plain(tools.make_quiz)`. It picks one random glossary term from the given lecture and returns JSON with `question` ("What does X mean?"), `answer` (the definition), and `lecture`. If the lecture has no terms, for example `lecture=0`, it returns "No glossary terms found for Lecture 00. Sessions with terms: 01, 02, 03, 04, 06" instead of raising an error.

  The docstring says to use it when the learner asks for a review question, a quiz, or a self-check, gives "Give me one review question from Lecture 02" as an example, and says to show only the question first and keep the answer until the learner has tried.

  Results: `--list-tools` shows `make_quiz` with the docstring, `uv run pytest -q` gives 15 passed, and `--trace "Give me one review question from Lecture 02"` shows `[tool call] make_quiz({'lecture': 2})` (`requests=2`). The agent replied with just "What does LoRA mean?" and kept the answer hidden. One thing I noticed: it did not end with "Lecture 02" this time, even though `INSTRUCTIONS` asks for that in every answer. My guess is that "show only the question" in the docstring won over the general rule. I did not change `INSTRUCTIONS`, because the model called the tool without any extra hint.

## Homework

- Level attempted: Basic / Implementation / Advanced
- What you did:
- Results:
- Observations and questions:
