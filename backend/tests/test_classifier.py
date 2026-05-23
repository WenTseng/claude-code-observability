import pytest
from backend.classifier import match_whitelist


CFG = {
    "toolWhitelist": {
        "Edit": {"category": "Code", "L1": "Edit", "L2": "file-edit"},
        "Bash": {"category": "Debug", "L1": "Debug", "L2": "shell"},
    }
}


def test_whitelist_hit_returns_category():
    tool_usage = [{"toolName": "Edit"}]
    result = match_whitelist(tool_usage, CFG)
    assert result is not None
    assert result["L1"] == "Edit"


def test_whitelist_miss_returns_none():
    tool_usage = [{"toolName": "UnknownTool"}]
    result = match_whitelist(tool_usage, CFG)
    assert result is None


def test_whitelist_first_match_wins():
    tool_usage = [{"toolName": "Edit"}, {"toolName": "Bash"}]
    result = match_whitelist(tool_usage, CFG)
    assert result["L1"] == "Edit"


def test_empty_tool_usage_returns_none():
    result = match_whitelist([], CFG)
    assert result is None
