.PHONY: help install test lint format clean experiments reproduce-small figures tables dashboard audit check

PYTHON ?= .venv/bin/python
UV ?= uv
export MPLCONFIGDIR := /tmp/mpl

help:
	@echo "AdaptiveGrover-QCA Makefile"
	@echo "  install          - Create virtualenv and install all dependencies"
	@echo "  test             - Run all unit, property, and integration tests"
	@echo "  lint             - Run ruff linter and mypy type checks"
	@echo "  audit            - Run full research validation audit suite (hygiene, figures, tests, linter)"
	@echo "  dashboard        - Build React frontend and launch unified FastAPI research server"
	@echo "  experiments      - Run full experiment suite (Exp 1-6)"
	@echo "  reproduce-small  - Fast end-to-end reproducible run (~5-10 min)"
	@echo "  figures          - Generate publication-quality figures"
	@echo "  tables           - Generate LaTeX tables from experimental data"
	@echo "  clean            - Remove virtualenv, build artifacts, and cache files"

install:
	$(UV) venv
	$(UV) pip install -e ".[dev]"
	cd dashboard && npm install && npm run build

test:
	$(PYTHON) -m pytest tests --cov=agqca --cov-report=term-missing

lint:
	$(PYTHON) -m ruff check src tests experiments scripts
	$(PYTHON) -m mypy src

format:
	$(PYTHON) -m ruff format src tests experiments scripts

audit:
	$(PYTHON) scripts/check_hygiene.py
	$(PYTHON) scripts/check_figures.py
	$(PYTHON) -m pytest tests --cov=agqca --cov-fail-under=85
	$(PYTHON) -m ruff check src tests experiments scripts
	$(PYTHON) -m mypy src

dashboard:
	npm --prefix dashboard run build
	$(PYTHON) -m uvicorn agqca.api.server:app --host 0.0.0.0 --port 8000

experiments:
	$(PYTHON) experiments/run_all.py --mode full

reproduce-small:
	$(PYTHON) experiments/run_all.py --mode small
	$(PYTHON) scripts/generate_figures.py
	$(PYTHON) scripts/export_tables.py

figures:
	$(PYTHON) scripts/generate_figures.py

tables:
	$(PYTHON) scripts/export_tables.py

clean:
	rm -rf .venv build dist *.egg-info .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
