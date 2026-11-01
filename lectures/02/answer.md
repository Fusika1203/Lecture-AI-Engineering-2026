# Lecture 02 Answers

## Exercises

- Model and settings used (from `config` in `result.json`):
  
  `Qwen/Qwen3.5-0.8B`, LoRA without quantization, `lora_r` 16, `lora_alpha` 32, `lr` 2e-4, 20 epochs (40 steps), `warmup_steps` 6, seed 42, greedy generation (`do_sample: False`), `max_new_tokens` 96. Libraries: transformers 5.18.0, peft 0.21.1, trl 1.14.2, torch 2.11.0+cu130. Files: [results/baseline/](results/baseline/).

- Did you run training yourself (`executed_training_myself`): **Yes**. I ran all sections (0 to 8) on a Colab T4.

- Training: 6,389,760 of 758,782,784 parameters were trained (0.84%). The loss went 1.700 (step 10) → 0.075 (step 20) → 0.020 (step 30) → 0.015 (step 40). Training took 173 seconds.

- Before training: `format_rate` = 0.952 (20/21) / `content_rate` = 0.381 (8/21)

- After training: `format_rate` = 1.000 (21/21) / `content_rate` = 0.905 (19/21)

- Questions that regressed: none (`regressed: []`).

- Failures remaining after training and their types:
  
  | Question                                | Expected `needs_review` | Output after training                                                                                     | Type                                                                             |
  | --------------------------------------- | ----------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
  | Can I submit a format other than PDF?   | false (in the FAQ)      | "This FAQ does not contain that information. Confirmation from the course organizers is needed." (`true`) | Evasion: asked for confirmation although the FAQ has the answer                  |
  | Do office hours require an appointment? | true (not in the FAQ)   | "Questions are welcome during office hours every Tuesday from 17:00 to 18:00." (`false`)                  | Assertion without evidence: it answered with a different FAQ item (office hours) |
  
  No output had a broken format after training.

- Results of knowledge questions (section 6; classification before → after training) and observations:
  
  | Question                                               | In the FAQ | Before → after              |
  | ------------------------------------------------------ | ---------- | --------------------------- |
  | When is the final assignment deadline for this course? | No         | asserted → asserted         |
  | What is the instructor's name?                         | No         | needs_review → needs_review |
  | What is the topic of the next lecture?                 | No         | needs_review → needs_review |
  | When is the assignment deadline? (control)             | Yes        | asserted → asserted         |
  
  The final-assignment question is the clearest failure. Both before and after training, the model answered "September 30 at 23:59", which is the deadline of the normal assignment. It seems to match the word "deadline" and reuse the FAQ item. Training did not change this. The other two unknown questions already got `needs_review: true` before training; training only changed the wording to the exact sentence from the training data.

- What changed and what stayed the same with training:
  
  **Changed:**
  
  1. **The `needs_review` flag on questions in the FAQ.** Before training, the model often gave the right answer but set `needs_review: true` (7 of 15 questions with evidence, for example "Late submissions are accepted within 48 hours…" with `true`). After training, 14 of 15 were correct.
  2. **Short "No" answers to questions not in the FAQ.** Before training, the model answered "No" with `needs_review: false` to three questions that are not in the FAQ (lecture recordings, citation style, office-hour appointments). After training, two of them became confirmation requests.
  3. **Wording.** After training, the answers copy the FAQ sentences and the training answer almost word for word. Before training, it gave short answers such as "Tuesday from 17:00 to 18:00".
  
  **Stayed the same:**
  
  1. **Judgment on new kinds of questions.** The model still answers with a related FAQ item when a question is close in topic but not covered (office-hour appointments, final assignment deadline).
  2. **The JSON format was already mostly fine.** In my run, only one output broke the format before training (it copied the whole FAQ into `answer` and dropped `needs_review`). The instructions say many outputs lacked keys in the original Japanese run. In this English version, the main problem before training was the `needs_review` value, not the format.
  
  **Notes on the scoring:** the content check needs exact keywords. "Is there a character count limit for assignments?" failed before training even though the answer ("No character count limit … is mentioned in the FAQ.", `true`) is reasonable, because it does not contain the word "Confirmation". So, part of the improvement in `content_rate` comes from learning the exact wording, not only better judgment.
  
  **Section 8 (4-bit, no training):** weight memory went from 3.01 GB to 0.76 GB. `format_rate` was 1.0, but `content_rate` fell from 0.381 to 0.048 (1/21). The 4-bit model set `needs_review: true` almost everywhere and often answered with the assignment deadline. Quantization alone changed the outputs a lot.

## Homework

- Level attempted: Basic

- Settings or data changed:
  
  I lowered the learning rate `lr` from 2e-4 to 5e-5 (4 times smaller) and kept everything else the same: `lora_r` 16, `lora_alpha` 32, 20 epochs (40 steps), `warmup_steps` 6, seed 42, the same data and the same greedy generation. I restarted the Colab session and ran the notebook from the top on a T4. Files: [results/baseline/](results/baseline/) and [results/lr5e-5/](results/lr5e-5/).

- Results (comparison tables or numbers):
  
  | Setting              | `format_rate` (after) | `content_rate` (after) | Final loss (step 40) | Training time | Regressions |
  | -------------------- | --------------------- | ---------------------- | -------------------- | ------------- | ----------- |
  | `lr` 2e-4 (original) | 1.000 (21/21)         | 0.905 (19/21)          | 0.015                | 173 s         | none        |
  | `lr` 5e-5            | 1.000 (21/21)         | 0.857 (18/21)          | 0.101                | 175 s         | none        |
  
  Before training, both runs had exactly the same outputs (`format_rate` 0.952, `content_rate` 0.381), so the comparison only reflects training.
  
  **Training loss**
  
  | Step | `lr` 2e-4 | `lr` 5e-5 |
  | ---- | --------- | --------- |
  | 10   | 1.700     | 2.338     |
  | 20   | 0.075     | 0.979     |
  | 30   | 0.020     | 0.249     |
  | 40   | 0.015     | 0.101     |
  
  **What actually differed between the two runs**
  
  - The 15 questions with evidence in the FAQ got the same answers in both runs, word for word.
  - `needs_review` was correct for 19 of 21 questions in both runs. The two failures are the same questions ("Can I submit a format other than PDF?" and "Do office hours require an appointment?").
  - The only extra failure with `lr`= 5e-5 is "Is there a character count limit for assignments?". The model answered "Information regarding character count limits is not included in the provided FAQ." with `needs_review: true`, which is the right decision, but the sentence does not contain "Confirmation", so the keyword check failed.
  - With `lr`= 2e-4, all five confirmation requests (for the questions without evidence, except the appointment question) were the exact training sentence ("This FAQ does not contain that information. Confirmation from the course organizers is needed."). With `lr`= 5e-5, the model wrote its own versions, such as "Information regarding grade release is not included in the provided FAQ. Confirmation is needed."
  - The knowledge questions (section 6) had the same classifications in both runs. The final-assignment question was still answered with "September 30 at 23:59".
  - Training time did not change, because the learning rate does not change the amount of computation.
  
  In short, the lower learning rate left the loss about seven times higher, and the model copied the training wording less closely. The decisions the model made did not change at all. The 0.905 → 0.857 drop comes from one sentence that missed a keyword.

- Discussion of when fine-tuning is and is not suitable:
  
  In this exercise, fine-tuning clearly changed how the model answers. After 3 minutes of training on 14 examples, every output was valid JSON, and almost all answers to questions covered by the FAQ came back as the FAQ sentence itself. The `needs_review` flag on these questions also became correct (14 of 15, compared with 7 of 15 before training). This is the kind of change that the lecture describes as "behavior": a fixed output style that the model should follow every time, even without long instructions.
  
  What training did not fix is the judgment about whether the FAQ actually supports an answer. The two errors that remained after training point in opposite directions. The model refused to answer a question the FAQ does cover ("Can I submit a format other than PDF?") and answered a question that it does not cover by reusing a related item ("Do office hours require an appointment?" → office hours on Tuesday). The question about the final assignment deadline was answered with the normal assignment deadline both before and after training. My reading is that the model learned what kind of question usually gets which kind of answer, rather than learning to check the FAQ. With only 14 training examples, this is perhaps not surprising, but it means that a high score on the test set does not show that the model is reliable on new questions.
  
  The learning-rate experiment supports this. A four times lower learning rate changed the loss a lot (0.015 vs 0.101) and changed the wording of the answers, but every `needs_review` decision stayed the same. The loss and part of `content_rate` measure how closely the model copies the training text, which is not the same as judging correctly. I would not have seen this if I had only compared the summary numbers.
  
  From these results, I think fine-tuning is a good fit when:
  
  - the goal is a stable output format, tone, or procedure that is used many times, and prompts or structured output are not enough;
  - there are enough consistent examples, and a separate evaluation set that also includes questions that the system should not answer;
  - the facts the model needs are given in the input each time (as the FAQ was here), so training only has to teach how to use them.
  
  It is a poor fit when:
  
  - the goal is new or changing knowledge, such as deadlines that change every time. These are better provided in the input through retrieval (RAG), so they can be updated without retraining;
  - the model has to decide whether information is present in unseen situations. Here, the decision should be checked outside the model as well; for example, by retrieval scores or by a human for uncertain cases;
  - the format problem is already small. In my run, the base model already followed the JSON format in 20 of 21 cases before training, so a format check in code or structured output would probably have been enough for the format alone.
  
  The 4-bit result in section 8 is also a warning for practice. Without any training, loading the same model in 4-bit changed `content_rate` from 0.381 to 0.048. Any change to the base model or how it is loaded needs the same evaluation again, and an adapter trained on one setup should not be assumed to work on another.
  
  **Limitations:** I ran each setting once, on 21 test questions. A difference of one question between runs is within what could change from run to run, so I base my conclusions on the types of errors and on the per-question outputs, not on the small differences in the rates.
