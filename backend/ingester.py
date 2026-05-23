"""
Reads data/otel-logs.jsonl with byte-offset resume.
Writes new events to claude_raw_logs. Never double-writes.
"""
import json
import os
import time
from datetime import datetime, timezone

from mongo_client import get_db, raw_logs, ingest_state


DATA_FILE = os.getenv("DATA_FILE", "data/otel-logs.jsonl")


def get_offset(db):
    doc = ingest_state(db).find_one({"_id": "ingester"})
    return doc["byteOffset"] if doc else 0


def save_offset(db, offset):
    ingest_state(db).update_one(
        {"_id": "ingester"},
        {"$set": {"byteOffset": offset, "updatedAt": datetime.now(timezone.utc)}},
        upsert=True,
    )


def ingest_once(db):
    offset = get_offset(db)
    inserted = 0
    failed = 0

    with open(DATA_FILE, "rb") as f:
        f.seek(offset)
        for raw_line in f:
            offset += len(raw_line)
            line = raw_line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
                doc["_ingestedAt"] = datetime.now(timezone.utc)
                raw_logs(db).insert_one(doc)
                inserted += 1
            except Exception as e:
                db.claude_ingest_failures.insert_one(
                    {"raw": line.decode("utf-8", errors="replace"), "error": str(e)}
                )
                failed += 1
        save_offset(db, offset)

    return inserted, failed


if __name__ == "__main__":
    db = get_db()
    print(f"[ingester] starting, data file: {DATA_FILE}")
    inserted, failed = ingest_once(db)
    print(f"[ingester] done — inserted={inserted} failed={failed}")
