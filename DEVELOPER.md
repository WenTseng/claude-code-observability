# Developer Notes

Design decisions and trade-offs for contributors.

## Why byte-offset resume in the ingester?

The OTel collector appends to a JSONL file continuously. The ingester needs to
be restartable without re-processing already-ingested lines. We store the last
byte offset in a `_ingest_state` MongoDB document. On restart, `f.seek(offset)`
jumps directly to the unread portion. Mid-write lines (no trailing `\n`) are
naturally skipped since `readline()` returns an incomplete line only when the
file is still being written — the next run picks it up.

Failures are written to a `claude_ingest_failures` collection rather than
halting the pipeline, so one bad event doesn't block thousands of valid ones.

## Why whitelist-first classification?

Calling the LLM for every turn is expensive and slow. In practice, a small set
of tools (`Edit`, `Write`, `Bash`, `Read`) covers the majority of turns. The
whitelist short-circuits these at near-zero cost. Only ambiguous turns fall
through to the LLM. This keeps p99 classification cost low while maintaining
accuracy for unusual intents.

`classifier_config.json` is the single source of truth for both the whitelist
and the LLM system prompt — no logic duplication between ingestion and replay.

## Why prompt_id grouping instead of session-level?

Claude Code emits one `prompt_id` per user turn. Grouping at this level gives
the most meaningful unit of analysis: one row in `claude_turns` = one thing
the user asked. Session-level grouping loses per-turn cost and duration data.

## Token cost fields

`inputSize` / `resultSize` are byte lengths of tool inputs/outputs, not token
counts. We deliberately avoid raw `tool_input` / `tool_result` payloads (PII
risk, storage cost). Token counts come from the OTel span attributes directly.

## LLM cost optimization roadmap

- [ ] `sha1(prompt_text)` cache — identical prompts skip the LLM entirely
- [ ] Whitelist coverage reporting — surface which tools are unclassified
- [ ] Batch classification — group low-confidence turns for a single API call
- [ ] Prompt caching with Anthropic's cache-control headers

## Adding a new tool to the whitelist

Edit `backend/classifier_config.json`:

```json
"YourTool": { "category": "Code", "L1": "Edit", "L2": "your-action" }
```

Re-run `make build-turns` — existing classified turns are reused, only new
turns with `YourTool` as the top tool get the whitelist match.
