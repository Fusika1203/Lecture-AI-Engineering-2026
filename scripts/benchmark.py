"""Lecture 01 Advanced homework: measure latency and token counts across models and questions.

Usage:
    uv run python scripts/benchmark.py baseline   # lite models x 4 questions x 3 runs
    uv run python scripts/benchmark.py strong     # stronger "thinking" models (20 requests/day each)
    uv run python scripts/benchmark.py context    # same question with data/glossary.json in the prompt
    uv run python scripts/benchmark.py burst      # back-to-back calls to observe the per-minute limit

Every call (successful or not) is appended to results/benchmark.csv, and every answer to
results/answers.jsonl. Calls are spaced to stay under each model's free-tier RPM, except in
the burst experiment, which deliberately ignores it.
"""

import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import errors, types

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.config import get_api_key  # noqa: E402

QUESTIONS = {
    "lora": "What is LoRA?",
    "homework-levels": "What are the 3 homework levels in the AIE2026 course?",
    "lec-start-tag": "What is a lecNN-start tag in the AIE2026 course?",
    "lec02": "What will we learn in Lecture 02 of AIE2026?",
}

# Free-tier limits shown in AI Studio on 2026-10-25: (RPM, RPD)
LIMITS = {
    "gemini-3.5-flash-lite": (15, 500),
    "gemini-3.1-flash-lite": (15, 500),
    "gemini-3.8-flash": (5, 20),
    "gemini-3.6-flash": (5, 20),
    "gemini-3-flash-preview": (5, 20),
}

# experiment: (model -> runs per question, question ids, server timeout in seconds)
EXPERIMENTS = {
    "baseline": ({"gemini-3.5-flash-lite": 3, "gemini-3.1-flash-lite": 3}, list(QUESTIONS), None),
    # Thinking models can take minutes; the SDK forwards the client timeout to the server
    # (X-Server-Timeout), so a short timeout turns slow answers into 504 errors.
    "strong": (
        {"gemini-3.8-flash": 2, "gemini-3.6-flash": 4, "gemini-3-flash-preview": 4},
        list(QUESTIONS),
        300,
    ),
    "context": ({"gemini-3.5-flash-lite": 3, "gemini-3.1-flash-lite": 3}, ["homework-levels"], None),
}
BURST_MODEL, BURST_CALLS = "gemini-3.5-flash-lite", 20

CSV_PATH = ROOT / "results" / "benchmark.csv"
ANSWERS_PATH = ROOT / "results" / "answers.jsonl"
FIELDS = [
    "experiment", "timestamp", "model", "question_id", "run", "server_timeout_s", "latency_s",
    "input_tokens", "output_tokens", "thinking_tokens", "total_tokens", "answer_chars",
    "error", "error_message",
]


def build_prompt(experiment: str, qid: str) -> str:
    if experiment == "context":
        glossary = (ROOT / "data" / "glossary.json").read_text(encoding="utf-8")
        return (
            "Answer the question using the course glossary below.\n\n"
            f"<glossary>\n{glossary}\n</glossary>\n\nQuestion: {QUESTIONS[qid]}"
        )
    if experiment == "burst":
        return "Reply with the single word OK."
    return QUESTIONS[qid]


def call(client: genai.Client, model: str, prompt: str, timeout_s: int | None) -> tuple[dict, str]:
    config = types.GenerateContentConfig(
        http_options=types.HttpOptions(timeout=timeout_s * 1000) if timeout_s else None
    )
    start = time.perf_counter()
    try:
        response = client.models.generate_content(model=model, contents=prompt, config=config)
    except errors.APIError as e:
        err = {"error": e.code, "error_message": (e.message or "")[:200]}
    except Exception as e:  # connection reset, client-side timeout, ...
        err = {"error": type(e).__name__, "error_message": str(e)[:200]}
    else:
        u = response.usage_metadata
        text = response.text or ""
        return {
            "latency_s": round(time.perf_counter() - start, 2),
            "input_tokens": u.prompt_token_count,
            "output_tokens": u.candidates_token_count,
            "thinking_tokens": u.thoughts_token_count or 0,
            "total_tokens": u.total_token_count,
            "answer_chars": len(text),
            "error": "",
        }, text
    err["latency_s"] = round(time.perf_counter() - start, 2)
    return err, ""


def plan(experiment: str) -> list[tuple[str, str, int, float]]:
    """Return (model, question_id, run, min seconds between calls) for each call."""
    if experiment == "burst":
        return [(BURST_MODEL, "burst", i, 0) for i in range(1, BURST_CALLS + 1)]
    models, qids, _ = EXPERIMENTS[experiment]
    calls = []
    for model, runs in models.items():
        interval = 60 / LIMITS[model][0] + 1  # 1 s margin under the RPM limit
        calls += [(model, q, r, interval) for r in range(1, runs + 1) for q in qids]
    return calls


def main() -> None:
    experiment = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    if experiment not in (*EXPERIMENTS, "burst"):
        raise SystemExit(f"unknown experiment: {experiment}")
    timeout_s = EXPERIMENTS[experiment][2] if experiment in EXPERIMENTS else None
    client = genai.Client(api_key=get_api_key())
    calls = plan(experiment)

    CSV_PATH.parent.mkdir(exist_ok=True)
    new_file = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f, \
            ANSWERS_PATH.open("a", encoding="utf-8") as answers:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for i, (model, qid, run, interval) in enumerate(calls, 1):
            t0 = time.perf_counter()
            row = {
                "experiment": experiment,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "model": model, "question_id": qid, "run": run,
                "server_timeout_s": timeout_s or "",
            }
            result, text = call(client, model, build_prompt(experiment, qid), timeout_s)
            row.update(result)
            writer.writerow(row)
            f.flush()
            answers.write(json.dumps({**{k: row[k] for k in ("experiment", "model", "question_id", "run")},
                                      "answer": text}, ensure_ascii=False) + "\n")
            answers.flush()
            print(f"[{i}/{len(calls)}] {model} {qid} run{run}: {row['latency_s']}s "
                  f"in={row.get('input_tokens')} out={row.get('output_tokens')} "
                  f"think={row.get('thinking_tokens')} err={row['error'] or '-'}", flush=True)
            wait = interval - (time.perf_counter() - t0)
            if wait > 0 and i < len(calls):
                time.sleep(wait)


if __name__ == "__main__":
    main()
