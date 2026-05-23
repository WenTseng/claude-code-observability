# Collector

Uses `otel/opentelemetry-collector-contrib` to receive OTLP/HTTP from Claude Code CLI on port 4318 and write raw events to `data/otel-logs.jsonl`.

The file exporter appends one JSON object per line. The ingester reads this file with byte-offset resume so it can restart without re-processing.
