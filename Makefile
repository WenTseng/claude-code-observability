.PHONY: up down seed ingest build-turns classify dashboard logs

up:
	docker compose up -d

down:
	docker compose down

seed:
	python tools/seed.py

ingest:
	python backend/ingester.py

build-turns:
	python backend/build_turns.py

classify:
	python backend/build_turns.py --classify

pipeline:
	python tools/show_pipeline.py

test:
	pytest backend/tests/ -v

lint:
	ruff check backend/ tools/

logs:
	docker compose logs -f otelcol
