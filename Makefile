.PHONY: dev run install clean format

dev:
	uv run uvicorn api.server:app --reload --host 0.0.0.0 --port 8000

run:
	uv run python main.py

install:
	uv sync

format:
	uv run ruff format .
	uv run ruff check --fix .

clean:
	rm -rf .venv __pycache__ .ruff_cache