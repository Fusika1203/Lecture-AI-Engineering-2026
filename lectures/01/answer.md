# Lecture 01 Answers

## Exercises

- Model's answer to the course-specific question (the 3 homework levels; a summary is fine):
  
  `gemini-3.5-flash-lite` said it has no information about the AIE2026 course and could not list the levels. I ran it twice and got the same kind of answer both times. It did not make anything up.

- What you noticed when comparing it with the correct meaning in the glossary:
  
  The glossary says the 3 levels are Basic (review the lecture), Implementation (write your own code) and Advanced (research and experiments). Doing any one of them completes the homework. The bare model knows none of this, because the course is not in its training data. Saying "I don't know" is the safe answer, but it does not always happen. In my homework experiments, stronger models answered the same question by inventing a course. When I put the glossary into the prompt, every model answered correctly.

- Token counts you displayed (input / output):
  
  I added code to `app/ask.py` that prints `response.usage_metadata.prompt_token_count` (input) and `candidates_token_count` (output).
  
  | Question                                              | Input | Output     |
  | ----------------------------------------------------- | ----- | ---------- |
  | What are the 3 homework levels in the AIE2026 course? | 18    | 45         |
  | What is LoRA? (3 runs)                                | 6     | 657 to 726 |

## Homework

- Level attempted: **Advanced**

- What you did:
  
  I wrote `scripts/benchmark.py`. It calls the API many times, measures the response time and token counts of every call, and saves everything, including failed calls, to `results/benchmark.csv`. The full answers are saved to `results/answers.jsonl`. The script waits between calls so it stays under each model's per-minute limit.
  
  I ran four experiments with the four questions from the exercise. One question is general (LoRA) and three are about this course.
  
  | Experiment | What it tests                                                  | Calls |
  | ---------- | -------------------------------------------------------------- | ----- |
  | baseline   | Two light models, 3 runs per question                          | 35    |
  | strong     | Three stronger "thinking" models                               | 40    |
  | context    | The homework question, with the glossary added to the prompt   | 6     |
  | burst      | 20 calls in a row without waiting, to hit the per-minute limit | 20    |
  
  After that, I compared my call log with the usage numbers in Google AI Studio. I chose the experiments, ran them with my own API key, and checked the results against AI Studio myself. To reproduce: `uv run python scripts/benchmark.py baseline` (or `strong`, `context`, `burst`).

- Results:
  
  **Free-tier limits** (from AI Studio)
  
  | Model                                                      | Requests per minute | Tokens per minute | Requests per day |
  | ---------------------------------------------------------- | ------------------- | ----------------- | ---------------- |
  | gemini-3.5-flash-lite, gemini-3.1-flash-lite               | 15                  | 250,000           | 500              |
  | gemini-3.8-flash, gemini-3.6-flash, gemini-3-flash-preview | 5                   | 250,000           | 20               |
  
  **Speed and tokens by model** (successful calls only)
  
  | Model                  | Success | Typical time | Slowest | Output tokens | Thinking tokens |
  | ---------------------- | ------- | ------------ | ------- | ------------- | --------------- |
  | gemini-3.5-flash-lite  | 12 / 12 | 2.4 s        | 112 s   | 320           | 0               |
  | gemini-3.1-flash-lite  | 12 / 12 | 2.9 s        | 8 s     | 551           | 0               |
  | gemini-3-flash-preview | 16 / 16 | 6.4 s        | 12 s    | 583           | 671             |
  | gemini-3.6-flash       | 11 / 16 | 11 s         | 145 s   | 433           | 776             |
  | gemini-3.8-flash       | 4 / 19  | 150 s        | 301 s   | 448           | 653             |
  
  "Typical time" is the median. Token numbers are averages.
  
  **Time and output tokens by question**
  
  | Question          | 3.5-flash-lite | 3.1-flash-lite | 3-flash-preview | 3.6-flash |
  | ----------------- | -------------- | -------------- | --------------- | --------- |
  | LoRA (general)    | 3.7 s, 696     | 4.3 s, 788     | 8.3 s, 857      | 14 s, 804 |
  | 3 homework levels | 1.4 s, 125     | 2.0 s, 340     | 6.4 s, 407      | 11 s, 340 |
  | lecNN-start tag   | 2.9 s, 337     | 2.9 s, 605     | 5.8 s, 492      | 12 s, 498 |
  | Lecture 02        | 1.3 s, 121     | 2.8 s, 469     | 6.3 s, 576      | 7 s, 245  |
  
  **Context experiment:** adding the glossary raised the input from 18 to 7,446 tokens. The time stayed around 1 to 6 seconds, and all 6 answers were correct.
  
  **Burst experiment:** calls 1 to 14 worked. Calls 15 and 16 were rejected with error 429 (too many requests). Calls 17 to 19 worked again, and call 20 was rejected.
  
  **Which calls count toward the daily limit**
  
  | Model                 | My calls | Failed                         | AI Studio count | Meaning                    |
  | --------------------- | -------- | ------------------------------ | --------------- | -------------------------- |
  | gemini-3.5-flash-lite | 39       | 3 (error 429)                  | 36              | 429 errors are not counted |
  | gemini-3.6-flash      | 16       | 5 (error 503)                  | 16              | 503 errors are counted     |
  | gemini-3.8-flash      | 19       | 15 (503, 504, connection lost) | 19              | All failures are counted   |

- Observations and questions:
  
  1. **Stronger is not more honest.** On the homework-levels question, the light model said it did not know. The stronger models (3-flash-preview and 3.6-flash) confidently described three "difficulty levels" that do not exist. 3-flash-preview even linked the course to different universities in different runs. With the glossary in the prompt, this problem disappeared. This shows why later lectures add tools and retrieval (RAG).
  
  2. **Thinking models use hidden tokens.** The stronger models produce more thinking tokens than visible answer tokens. These tokens are included in the total count, so they cost time and money even though the user never sees them. This is the main reason these models are slower.
  
  3. **The daily limit is the real bottleneck on the free tier.** The stronger models allow only 20 calls per day, and failed calls still use them up. gemini-3.8-flash used 19 of 20 calls but gave only 4 answers. A program that retries immediately after every server error could waste a whole day's quota in a few minutes.
  
  4. **429 and 503 errors should be handled differently.** A 429 error is free and returns in under a second, so it is fine to wait and try again. A 503 error still counts toward the daily limit, so retries need a maximum number of attempts.
  
  5. **The per-minute limit is not a simple counter.** In the burst test, some calls were rejected and then the next ones worked again. It is safer to handle 429 errors in the code than to count requests by hand. Even with my waiting time (13 seconds for 5 per minute), AI Studio showed that I reached exactly 5 / 5.
  
  6. **The token-per-minute limit only matters for long prompts.** With 250,000 tokens and 15 requests per minute, the token limit only matters when one request has more than about 16,700 input tokens. I guess a prompt with long documents (as in RAG) can reach that.
  
  7. **Problems found during the experiment:**
     
     - My first version set a 60-second timeout. The library sends this timeout to the server, so the server stopped slow answers and returned error 504. Five of the early gemini-3.8-flash failures came from this. With a 300-second timeout, the same model answered in 72 to 182 seconds.
     - One slow response (112 s) was first thought to be an automatic retry. The library's source code and the AI Studio counts show that no retry happened, so it was simply a slow response.
     - The first script stopped on a lost connection and lost some failure records. I restored them from the console output.
  
  8. **Limits of this test:** only 2 to 4 runs per model and question, on one day and one network. The numbers show trends, not reliable statistics. I did not test temperature, because Google deprecated it in July 2026.
  
  
