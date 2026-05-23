"""
Aggregates raw_logs into claude_turns by prompt_id.
Optionally classifies each turn via classifier.py.
"""
import argparse
import json
import os
from datetime import datetime, timezone

from mongo_client import get_db, raw_logs, turns
from classifier import load_config, classify_turn


def build_turn_doc(events: list[dict]) -> dict:
    first = events[0]
    prompt_id = first.get("promptId", "unknown")
    tool_usage = []
    token_in = 0
    token_out = 0
    duration_ms = 0
    prompt_text = ""

    for e in events:
        attrs = e.get("attributes", {})
        if attrs.get("event.type") == "prompt":
            prompt_text = attrs.get("prompt.text", "")
        if attrs.get("inputTokens"):
            token_in += int(attrs["inputTokens"])
        if attrs.get("outputTokens"):
            token_out += int(attrs["outputTokens"])
        if attrs.get("durationMs"):
            duration_ms += int(attrs["durationMs"])
        tool_name = attrs.get("tool.name")
        if tool_name:
            tool_usage.append(
                {
                    "toolName": tool_name,
                    "inputSize": attrs.get("inputSize", 0),
                    "resultSize": attrs.get("resultSize", 0),
                }
            )

    return {
        "promptId": prompt_id,
        "promptText": prompt_text,
        "toolUsage": tool_usage,
        "tokenIn": token_in,
        "tokenOut": token_out,
        "durationMs": duration_ms,
        "eventCount": len(events),
        "createdAt": datetime.now(timezone.utc),
    }


def run(classify: bool = False):
    db = get_db()
    cfg = load_config() if classify else None
    processed = 0
    reused = 0

    pipeline = [
        {"$group": {"_id": "$promptId", "events": {"$push": "$$ROOT"}}},
    ]
    for group in raw_logs(db).aggregate(pipeline):
        prompt_id = group["_id"]
        if not prompt_id:
            continue

        existing = turns(db).find_one({"promptId": prompt_id})
        if existing and existing.get("feature"):
            reused += 1
            continue

        doc = build_turn_doc(group["events"])

        if classify and cfg:
            classification = classify_turn(doc, cfg)
            doc.update(classification)

        turns(db).update_one(
            {"promptId": prompt_id}, {"$set": doc}, upsert=True
        )
        processed += 1

    print(f"[build_turns] processed={processed} reused={reused}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--classify", action="store_true")
    args = parser.parse_args()
    run(classify=args.classify)
