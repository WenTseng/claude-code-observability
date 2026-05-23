import pytest
from backend.build_turns import build_turn_doc


def make_event(prompt_id, token_in=10, token_out=20, tool_name=None):
    attrs = {"inputTokens": token_in, "outputTokens": token_out}
    if tool_name:
        attrs["tool.name"] = tool_name
        attrs["inputSize"] = 100
        attrs["resultSize"] = 200
    return {"promptId": prompt_id, "attributes": attrs}


def test_token_totals_are_summed():
    events = [make_event("p1", 10, 20), make_event("p1", 5, 8)]
    doc = build_turn_doc(events)
    assert doc["tokenIn"] == 15
    assert doc["tokenOut"] == 28


def test_tool_usage_collected():
    events = [make_event("p1", tool_name="Edit"), make_event("p1", tool_name="Bash")]
    doc = build_turn_doc(events)
    tool_names = [t["toolName"] for t in doc["toolUsage"]]
    assert "Edit" in tool_names
    assert "Bash" in tool_names


def test_prompt_id_preserved():
    events = [make_event("abc-123")]
    doc = build_turn_doc(events)
    assert doc["promptId"] == "abc-123"
