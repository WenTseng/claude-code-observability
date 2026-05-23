"""
Generates fake OTLP-shaped JSONL data for local development.
Usage: python tools/seed.py [--turns N]
"""
import argparse
import json
import os
import random
import uuid
from datetime import datetime, timezone, timedelta

TOOLS = ["Edit", "Write", "Read", "Bash", "Glob", "Grep", "UnknownTool"]
PROMPTS = [
    "Refactor the authentication module to use JWT",
    "Debug why the ingester is skipping records",
    "Write unit tests for the classifier",
    "Explain how byte-offset resume works",
    "Add error handling to the pipeline",
    "Generate documentation for mongo_client.py",
]


def fake_turn(prompt_id: str, ts: datetime) -> list[dict]:
    events = []
    prompt_text = random.choice(PROMPTS)

    events.append({
        "promptId": prompt_id,
        "timestamp": ts.isoformat(),
        "attributes": {
            "event.type": "prompt",
            "prompt.text": prompt_text,
            "inputTokens": random.randint(50, 800),
            "outputTokens": random.randint(100, 1500),
            "durationMs": random.randint(200, 4000),
        },
    })

    for _ in range(random.randint(1, 4)):
        tool = random.choice(TOOLS)
        events.append({
            "promptId": prompt_id,
            "timestamp": (ts + timedelta(milliseconds=random.randint(50, 500))).isoformat(),
            "attributes": {
                "event.type": "tool_call",
                "tool.name": tool,
                "inputSize": random.randint(100, 5000),
                "resultSize": random.randint(50, 3000),
            },
        })

    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--turns", type=int, default=20)
    parser.add_argument("--out", default="data/otel-logs.jsonl")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    total = 0
    with open(args.out, "a") as f:
        for _ in range(args.turns):
            prompt_id = str(uuid.uuid4())
            ts = datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 60))
            for event in fake_turn(prompt_id, ts):
                f.write(json.dumps(event) + "\n")
                total += 1

    print(f"[seed] wrote {args.turns} turns ({total} events) → {args.out}")


if __name__ == "__main__":
    main()
