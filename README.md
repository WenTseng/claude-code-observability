# Claude Code Observability

> Self-host pipeline that turns Claude Code's OpenTelemetry stream into a
> classified, queryable conversation log — with intent classification and a
> Grafana dashboard out of the box.

[![CI](https://github.com/WenTseng/claude-code-observability/actions/workflows/ci.yml/badge.svg)](https://github.com/WenTseng/claude-code-observability/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)

## Architecture

```
Claude Code        OTLP/HTTP       OTel Collector      JSONL
(local CLI)   ──────────────▶   (docker, :4318)  ──────────▶  data/*.jsonl
                                                                    │
                                                          ingester (cron / manual)
                                                                    │
                                                                    ▼
                                                            MongoDB: raw_logs
                                                                    │
                                                        build_turns + classifier
                                                                    │
                                                                    ▼
                                                            MongoDB: turns
                                                                    │
                                                                    ▼
                                                          Grafana Dashboard :3000
```

## Quickstart

```bash
git clone https://github.com/WenTseng/claude-code-observability.git
cd claude-code-observability
cp .env.example .env          # add your ANTHROPIC_API_KEY
docker compose up -d
make seed                     # generate fake telemetry to play with
make ingest
make build-turns
make classify
open http://localhost:3000    # Grafana — admin / admin
```

5 minutes end-to-end. No cloud account needed.

## What this does

- **Captures** every Claude Code turn (prompt + tool calls + response) via OTLP
- **Groups** raw events into conversation turns by `prompt_id`
- **Classifies** each turn's intent: whitelist short-circuit + Claude fallback
- **Visualizes** adoption, cost, and tool-usage in Grafana

## Design highlights

- **Byte-offset resume** in the ingester — re-run anytime, never double-write
- **Whitelist-first classifier** — most turns never reach the LLM (cost control)
- **Atomic turn writes** — aggregation and classification land together
- **Pluggable identity** — works with bare `os.getenv("USER")`, ready to swap

See [DEVELOPER.md](DEVELOPER.md) for full rationale and design decisions.

## Project status

- [x] Phase 0 — Repo & structure
- [ ] Phase 1 — Collector + Mongo + seed data verified
- [ ] Phase 2 — Ingester (byte-offset resume)
- [ ] Phase 3 — Build turns (prompt_id aggregation)
- [ ] Phase 4 — Classifier (whitelist + LLM fallback)
- [ ] Phase 5 — Grafana dashboard
- [ ] Phase 6 — Docs, demo GIF, CI

## License

MIT
