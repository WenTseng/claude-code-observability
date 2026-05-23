"""
Classifies a turn's intent.
1. Whitelist short-circuit: if the top tool matches, skip LLM.
2. LLM fallback: call Claude via Anthropic SDK.
"""
import json
import os
import anthropic


def load_config(path="backend/classifier_config.json"):
    with open(path) as f:
        return json.load(f)


def match_whitelist(tool_usage: list[dict], cfg: dict) -> dict | None:
    whitelist = cfg.get("toolWhitelist", {})
    for tool in tool_usage:
        name = tool.get("toolName", "")
        if name in whitelist:
            return whitelist[name]
    return None


def classify_with_llm(prompt_text: str, cfg: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model=cfg.get("llm_model", "claude-haiku-4-5-20251001"),
        max_tokens=256,
        temperature=cfg.get("llm_temperature", 0),
        system=cfg["system_prompt"],
        messages=[{"role": "user", "content": prompt_text[:2000]}],
    )
    text = message.content[0].text.strip()
    return json.loads(text)


def classify_turn(turn: dict, cfg: dict) -> dict:
    tool_usage = turn.get("toolUsage", [])
    result = match_whitelist(tool_usage, cfg)
    source = "whitelist"
    if result is None:
        result = classify_with_llm(turn.get("promptText", ""), cfg)
        source = "llm"
    return {**result, "_classifySource": source}
