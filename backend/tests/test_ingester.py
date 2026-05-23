import json
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch


def make_db():
    db = MagicMock()
    db._ingest_state.find_one.return_value = None
    db.claude_raw_logs.insert_one = MagicMock()
    db._ingest_state.update_one = MagicMock()
    return db


def test_ingest_once_inserts_new_records():
    events = [
        {"promptId": "p1", "attributes": {}},
        {"promptId": "p2", "attributes": {}},
    ]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
        path = f.name

    try:
        with patch.dict(os.environ, {"DATA_FILE": path}):
            import importlib
            import backend.ingester as ingester_mod
            importlib.reload(ingester_mod)
            db = make_db()
            inserted, failed = ingester_mod.ingest_once(db)
        assert inserted == 2
        assert failed == 0
    finally:
        os.unlink(path)


def test_ingest_twice_does_not_double_write():
    event = {"promptId": "p1", "attributes": {}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps(event) + "\n")
        path = f.name

    try:
        with patch.dict(os.environ, {"DATA_FILE": path}):
            import importlib
            import backend.ingester as ingester_mod
            importlib.reload(ingester_mod)
            db = make_db()
            ingester_mod.ingest_once(db)
            offset_after_first = db._ingest_state.update_one.call_args[0][1]["$set"]["byteOffset"]
            db._ingest_state.find_one.return_value = {"byteOffset": offset_after_first}
            inserted2, _ = ingester_mod.ingest_once(db)
        assert inserted2 == 0
    finally:
        os.unlink(path)
