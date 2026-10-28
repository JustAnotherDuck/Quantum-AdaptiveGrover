# Reproduction Guide: AdaptiveGrover-QCA

This guide enables full, push-button reproduction of all experimental benchmarks, statistical tables, publication figures, and interactive demos from a clean clone.

---

## 1. System Requirements

- **Operating System**: macOS (tested on Apple Silicon arm64, macOS 15+) or Linux (x86_64 / aarch64)
- **Python**: Version 3.11 or 3.12 (tested on 3.12.4)
- **Tooling**: `uv` package manager (>= 0.4.0) or standard `pip`

---

## 2. One-Line Fast Reproduction (~5–10 Minutes)

To run the complete small-scale experimental suite (Exp 1–6), recompute all statistical tables, and regenerate publication figures:

```bash
make reproduce-small
```

This runs:
1. `experiments/run_all.py --mode small` across independent random seeds.
2. `scripts/generate_figures.py` to regenerate vector PDF and PNG figures in `paper_support/figures/`.
3. `scripts/export_tables.py` to regenerate LaTeX tables in `paper_support/tables/`.

---

## 3. Step-by-Step Manual Reproduction

### Step 1: Environment Setup
```bash
# Create virtual environment and install pinned dependencies
make install

# Activate virtual environment
source .venv/bin/activate
```

### Step 2: Run Verification Test Suite
```bash
make test
```
*Validates 45+ unit, theory, cipher, oracle, and property tests with coverage report.*

### Step 3: Run Full Benchmark Suite (~20–30 Minutes)
```bash
make experiments
```
*Executes full 35-seed statistical sweeps across all key sizes and noise rates.*

### Step 4: Launch Interactive Demo
```bash
make demo
```
*Launches Streamlit app at `http://localhost:8501`.*

---

## 4. Hardware and Software Specifications

The baseline benchmark numbers in this repository were measured on:
- **Processor**: Apple M-series (Apple Silicon arm64)
- **Memory**: 16 GB Unified Memory
- **Compiler / Runtime**: Python 3.12.4, Qiskit 2.6.1, Qiskit-Aer 0.18.2
- **Random Seeds**: Pinned in configs (`seed = 1000 * n + s_idx`).
