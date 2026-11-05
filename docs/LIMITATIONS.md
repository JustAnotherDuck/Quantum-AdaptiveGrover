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
### 1.4 Regime D: Small Key Spaces with Classical Filtering ($n \le 8$)
- **Observation**: When classical filtering reduces candidate cardinality $N \to N'$, filtered classical brute force searches among $N'$ candidates with expected cost $N'/2 + C_{\text{filter}}$.
- **Result**: On small registers ($n \le 8$), the constant prefactors of quantum circuit compilation, transpilation, measurement shots, and classical candidate verification outweigh the asymptotic Grover speedup. Filtered Grover achieves a quantum-specific speedup over filtered classical brute force of $< 1.0\times$ (typically $0.35\times$ to $0.45\times$).
- **Conclusion**: Classical search-space reduction ($N/N'$) accounts for the end-to-end reduction over unfiltered classical brute force. Quantum advantage only emerges asymptotically when candidate space $N'$ is sufficiently large ($N' \gg 2^{16}$) and circuit noise is kept below threshold.

---

## 2. Hardware and Simulation Boundaries

1. **Strict Measurement Bounds ($n \le 16$)**: Quantum circuit synthesis and gate counts for Mode B reversible circuits are strictly limited to measured instances up to $n = 16$ bits (33 total qubits). Synthetic 128-bit extrapolations from toy ciphers have been explicitly removed following the validation audit; all AES-128 and AES-256 projections cited in this repository are taken directly from published peer-reviewed literature (Grassl et al. 2016, Jaques et al. 2020) and are clearly demarcated as external estimates.
2. **Noise Model Realism**: Physical quantum hardware exhibits non-Markovian noise, spectator crosstalk, and frequency collision drifts. While this framework models 1q/2q depolarizing errors, readout bit-flips, thermal relaxation ($T_1/T_2$), and IBM fake backends (`FakeManilaV2`), physical quantum processors will experience additional device-specific fidelity degradation.
3. **Absolute Prohibition on Cryptographic Attack Claims**: All attacks run strictly on educational, pedagogical, and scaled-down ciphers (S-AES, Mode B SPN). This software produces experimental complexity estimates, not formal cryptographic vulnerabilities, and makes no claim that current or near-term quantum hardware poses a threat to production AES-128 or AES-256.
