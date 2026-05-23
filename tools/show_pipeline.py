"""
CLI tool: prints a sample turn's journey from raw → classified.
Usage: python tools/show_pipeline.py [--prompt-id <id>]
"""
import argparse
import json
from mongo_client import get_db, raw_logs, turns


def show(prompt_id: str | None = None):
    db = get_db()

    if prompt_id:
        turn = turns(db).find_one({"promptId": prompt_id})
    else:
        turn = turns(db).find_one(sort=[("createdAt", -1)])

    if not turn:
        print("No turns found. Run `make seed && make ingest && make build-turns` first.")
        return

    pid = turn["promptId"]
    raw_count = raw_logs(db).count_documents({"promptId": pid})

    print(f"\n{'='*60}")
    print(f"prompt_id : {pid}")
    print(f"raw events: {raw_count}")
    print(f"{'─'*60}")
    print(f"prompt    : {turn.get('promptText', '')[:120]}")
    print(f"tokens    : in={turn.get('tokenIn')} out={turn.get('tokenOut')}")
    print(f"duration  : {turn.get('durationMs')}ms")
    print(f"tools     : {[t['toolName'] for t in turn.get('toolUsage', [])]}")
    print(f"{'─'*60}")
    if turn.get("L1"):
        print(f"category  : {turn.get('L1')} / {turn.get('L2')}")
        print(f"source    : {turn.get('_classifySource')}")
        print(f"reason    : {turn.get('reason')}")
    else:
        print("(not classified yet — run `make classify`)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-id", default=None)
    args = parser.parse_args()
    show(args.prompt_id)
