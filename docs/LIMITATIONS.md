# Limitations and Negative Results

In accordance with the scientific integrity principles of AdaptiveGrover-QCA, this document records the architectural limitations, empirical boundaries, and observed negative results of the framework.

---

## 1. Regimes Where the Adaptive Controller Does Not Beat Baselines (Negative Results)

### 1.1 Regime A: Zero and Near-Zero Noise ($\epsilon < 0.5\%$)
- **Observation**: Under perfect or near-ideal gate fidelity, standard fixed-iteration Grover operates at the theoretical quadratic optimum ($k_{\text{ideal}} \approx \frac{\pi}{4}\sqrt{N/M}$ with single-run success $p > 95\%$).
- **Result**: The adaptive controller yields **no improvement** over standard Grover in query complexity. Furthermore, the classical overhead of online Bayesian belief updates and multi-round decision tracking adds slight classical wall-clock overhead ($\approx 5–10\%$).
- **Conclusion**: In fault-tolerant, noise-free regimes, adaptivity is redundant; standard fixed Grover remains the optimal choice.

### 1.2 Regime B: Catastrophic Noise ($\epsilon > 25\%$)
- **Observation**: When two-qubit gate error rates exceed 20–25%, the effective per-iteration fidelity $F$ drops below 0.10. At this level of degradation, even a single Grover iteration ($k=1$) mixes the quantum state into near-uniform randomness.
- **Result**: No quantum strategy (neither deep, shallow-restart, nor adaptive) beats classical brute force.
- **Conclusion**: Quantum advantage vanishes completely. The controller detects this condition via the Bayesian estimator and falls back to classical verification.

### 1.3 Regime C: Classical Filtering Without Constraints
- **Observation**: When no cryptographic constraints (e.g. prefix, suffix, parity, or dictionary) are known beforehand, candidate filtering tests all $N$ keys, costing $N$ classical checks and achieving a reduction ratio of $1.0\times$.
- **Result**: Imposing classical filtering when no constraints exist strictly degrades overall efficiency, adding $N$ classical operations to the quantum search cost.
- **Conclusion**: Classical pre-filtering must only be activated when structural or leakage constraints exist.

---

## 2. Hardware and Simulation Boundaries

1. **Statevector Simulation Ceiling**: Full statevector simulation of Mode B reversible circuits is constrained to $n \le 16$ bits ($2^{33}$ amplitudes for 16-bit key + 16-bit state + flag would require $>64$ GB RAM). Large-scale resource projections ($n = 32, 64, 128$) are architectural gate-count extrapolations, not executed statevectors.
2. **Noise Model Realism**: Physical quantum devices exhibit non-Markovian 1/f noise, drift, and crosstalk that are approximated here by standard Lindbladian depolarizing channels and $T_1/T_2$ relaxation.
3. **No Claim on Live Cryptosystems**: All attacks run on educational reduced ciphers (S-AES, Toy SPN). This software cannot ingest real-world ciphertexts or attack production AES-128 / AES-256 implementations.
