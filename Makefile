.PHONY: help install test lint format clean experiments reproduce-small figures tables demo check

PYTHON ?= .venv/bin/python
UV ?= uv
export MPLCONFIGDIR := /tmp/mpl

help:
	@echo "AdaptiveGrover-QCA Makefile"
	@echo "  install          - Create virtualenv and install all dependencies"
	@echo "  test             - Run all unit, property, and integration tests"
	@echo "  lint             - Run ruff linter and mypy type checks"
	@echo "  format           - Format code with ruff"
	@echo "  experiments      - Run full experiment suite (Exp 1-6)"
	@echo "  reproduce-small  - Fast end-to-end reproducible run (~5-10 min)"
	@echo "  figures          - Generate publication-quality figures"
	@echo "  tables           - Generate LaTeX tables from experimental data"
	@echo "  demo             - Launch interactive Streamlit demo"
	@echo "  clean            - Remove virtualenv, build artifacts, and cache files"

install:
	$(UV) venv
	$(UV) pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests --cov=src/agqca --cov-report=term-missing --cov-report=html

lint:
	$(PYTHON) -m ruff check src tests experiments scripts demo
	$(PYTHON) -m mypy src

format:
	$(PYTHON) -m ruff format src tests experiments scripts demo

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

demo:
	$(PYTHON) -m streamlit run demo/app.py

clean:
	rm -rf .venv build dist *.egg-info .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
