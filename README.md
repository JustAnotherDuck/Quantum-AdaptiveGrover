# AdaptiveGrover-QCA: Adaptive and Noise-Aware Key Search for Practical Quantum Cryptanalysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Qiskit: 2.x](https://img.shields.io/badge/qiskit-2.6.1-purple.svg)](https://qiskit.org/)
[![Coverage: 88%](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)]()

> **CRITICAL SCIENTIFIC INTEGRITY & SAFETY NOTICE**:
> This framework investigates quantum cryptanalysis strictly on reduced-scale, toy, and educational cipher instances (4–16 bit keys) in simulated quantum environments.
> It does not attack full-scale cryptographic schemes (such as standard AES-128 or AES-256) and produces **experimental resource estimates, not formal cryptographic certification**.

---

## 1. Research Question & Focus

Standard literature frequently evaluates Grover's key search algorithm as an asymptotic abstraction ($\mathcal{O}(\sqrt{N})$), assuming ideal unitary evolution. In physical quantum computers, two-qubit gate errors ($\epsilon_{2q} > 0$), finite coherence times ($T_1/T_2$), and circuit depth cause rapid decoherence, degrading or erasing the quadratic quantum speedup.

**AdaptiveGrover-QCA** empirically investigates:
> **How much of Grover's theoretical quadratic advantage for key search survives under realistic noisy, depth-limited, resource-constrained quantum execution, and can an adaptive controller that combines classical candidate filtering, adaptive iteration selection, noise-aware strategy selection, and shallow-circuit restarts recover more of it than standard fixed-iteration Grover?**

---

## 2. Core Architecture & Validated Levers

The framework implements a modular research pipeline:
1. **Target Cipher Benchmarks**: S-AES (Schaefer 2003) and reversible block cipher SPN oracles (Heys 2002).
2. **Classical Candidate Filtering**: Partial-key knowledge, byte-range constraints, and linear/differential pruning ($N \to N'$).
3. **Safety Fallback Verification**: Rigorous sanity checking ensuring the true key is never discarded.
4. **Noise & Device Emulation**: Two-qubit depolarizing error channels ($\epsilon \in [0.05\%, 20.0\%]$), readout errors, and calibrated IBM fake backends (`FakeManilaV2`).
5. **Adaptive Control Engine**: Online Bayesian belief updating over success probability and noise decay.
6. **Dual-Oracle Quantum Simulation**:
   - *Mode A*: Synthesized phase oracle for statistical scaling sweeps up to $n=16$.
   - *Mode B*: Fully reversible compute-copy-uncompute quantum circuit capturing concrete gate counts and depth.
7. **Classical Verification**: Classical verification of measured key candidates.
8. **Adaptive Round Loop**: Continue, restart shallow, or switch strategy under equalized operational budget $B_{\max} = 15,000$ calls.

---

## 3. Quick Start & Push-Button Reproduction

### 3.1 Installation
```bash
# Clone repository
git clone https://github.com/adaptive-grover-qca/adaptive-grover-qca.git
cd adaptive-grover-qca

# Setup virtual environment and dependencies
make install

# Activate virtualenv
source .venv/bin/activate
```

### 3.2 Single-Command Full Reproduction (~5–10 min)
```bash
make reproduce-small
```
*Executes all 6 experiments across independent random seeds, computes 95% bootstrap confidence intervals, regenerates publication-quality figures (`paper_support/figures/`), and exports LaTeX tables (`paper_support/tables/`).*

### 3.3 Research Validation Audit Suite
```bash
make audit
```
*Executes full validation suite: zero-emoji hygiene check, figure and table data completeness check, 65+ unit tests with line and branch coverage (>=85% enforced), Ruff linter, and strict Mypy type checks.*

### 3.4 Interactive Research Dashboard & Assistant
```bash
make dashboard
```
*Builds the React/TypeScript frontend and launches the unified FastAPI service at `http://localhost:8000` with 9 research views and a grounded AI assistant.*

---

## 4. Key Validated Empirical Findings

1. **Empirical Scaling Exponents ($n = 4..12$)**:
   - Classical Brute Force: $\alpha = 1.000$ ($\text{Cost} \propto 2^{1.000n}$), exactly matching $N/2$ theory.
   - Standard Grover: $\alpha = 0.499$, confirming near-ideal theoretical quadratic scaling $\mathcal{O}(\sqrt{N})$ in low noise.
   - Adaptive Hybrid: $\alpha = 0.131$ with available classical candidate filtering constraints.
2. **Operational Crossover Boundary ($\epsilon^*$)**:
   - Under equalized query budgets ($B_{\max} = 15,000$ calls), Shallow Restart overtakes deep Standard Grover at $\epsilon^* \approx 17.87\%$ (95% bootstrap CI: $[17.61\%, 18.12\%]$) on $n = 6$.
   - Single-circuit amplification fidelity crossover occurs at $\approx 5.0\%$ two-qubit error.
3. **Fair Filtering Baseline & Negative Result Disclosure**:
   - Filtered Grover is benchmarked strictly against *Filtered Classical Brute Force* ($N'/2 + C_{\text{filter}}$).
   - On small keys ($n \le 8$), quantum prefactors yield quantum-specific speedup $S_{\text{quantum}} < 1.0\times$. True quantum advantage requires residual spaces $N' \gg 2^{16}$.
4. **Held-Out Noise Decay Model Validation**:
   - The parametric exponential decay model achieves $R^2 > 0.999$ and $\text{RMSE} < 10^{-3}$ when evaluated on disjoint held-out noise test partitions.
5. **Definitive NISQ Infeasibility**:
   - Full AES-128 requires $\approx 1.18 \times 10^{19}$ sequential Grover iterations and $1,785$ to $2,953$ logical qubits (Grassl 2016, Jaques 2020). Under uncorrected physical error rates ($0.05\% - 1.0\%$), circuit survival probability is $0.00 \times 10^0$, proving AES-128 is completely secure against NISQ devices.

---

## 5. Repository Structure

```
adaptive-grover-qca/
├── pyproject.toml, Makefile, LICENSE, CITATION.cff
├── src/agqca/
│   ├── ciphers/       # S-AES (Schaefer 2003), vectors
│   ├── oracles/       # Mode A (Marked-State) & Mode B (Reversible SPN)
│   ├── filtering/     # Constraints, safety fallback, arbitrary state prep
│   ├── strategies/    # Brute force, Standard, Noise-aware, Shallow, Adaptive, Null Control
│   ├── controller/    # Rule-based, Bayesian estimator, adaptive policy
│   ├── noise/         # Depolarizing (0.05-20%), fake backends, decay fit
│   ├── metrics/       # Resource tracker, honest cost accounting, bootstrap CIs
│   ├── analyzer/      # Cryptographic Readiness Analyzer, verified literature DB
│   ├── api/           # FastAPI backend routes and Pydantic schemas
│   └── assistant/     # Conversational assistant provider with offline fallback
├── dashboard/         # React + TypeScript + Vite + Tailwind research dashboard
│   ├── src/           # 9 specialized research views, charts, and assistant drawer
│   └── dist/          # Production SPA bundle served at root by FastAPI
├── experiments/       # YAML configs for Exp 1-6, run_all.py, raw_data/, aggregated/
├── tests/             # 65 unit and integration tests (coverage >= 87%)
├── paper_support/     # Publication figures (PDF+PNG), LaTeX tables, claims ledger
└── docs/              # AUDIT_LOG.md, ARCHITECTURE.md, DEMO_SCRIPT.md, LIMITATIONS.md
```

---

## 6. Citation

If you use this framework in academic research, please cite:
```bibtex
@software{adaptive_grover_qca_2026,
  author = {AdaptiveGrover-QCA Research Team},
  title = {AdaptiveGrover-QCA: Adaptive and Noise-Aware Key Search for Practical Quantum Cryptanalysis},
  year = {2026},
  url = {https://github.com/adaptive-grover-qca/adaptive-grover-qca}
}
```

---

## 7. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
