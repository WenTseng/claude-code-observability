import os
from pymongo import MongoClient

_client = None


def get_db():
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        _client = MongoClient(uri)
    db_name = os.getenv("MONGO_DB", "claude_observability")
    return _client[db_name]


def raw_logs(db=None):
    return (db or get_db()).claude_raw_logs


def turns(db=None):
    return (db or get_db()).claude_turns


def ingest_state(db=None):
    return (db or get_db())._ingest_state
