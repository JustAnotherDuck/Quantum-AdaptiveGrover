# AdaptiveGrover-QCA System Architecture

## 1. Overview and Core Philosophy

AdaptiveGrover-QCA is an open-source experimental framework for studying quantum cryptanalysis under physical and simulated noise. Standard literature frequently treats Grover's key search algorithm as an asymptotic abstraction ($\mathcal{O}(\sqrt{N})$), overlooking that gate errors, decoherence ($T_1/T_2$), and finite circuit depth quickly degrade quantum advantage.

AdaptiveGrover-QCA integrates four synergistic levers:
1. **Classical Candidate Filtering**: Pre-processing known constraints (partial key bits, parity, weak keys) to reduce search space $N \to N'$.
2. **Noise-Aware Iteration Selection**: Choosing $k$ to minimize total expected cost ($\frac{k}{p_{\text{noisy}}(k)}$) rather than blindly targeting $k_{\text{ideal}} \approx \frac{\pi}{4}\sqrt{N}$.
3. **Shallow-Circuit Restarts**: Restricting circuit depth below the noise-induced degradation threshold and relying on fast classical verification across repeated shallow runs.
4. **Adaptive Online Controller**: Updating posterior belief regarding candidate space, noise degradation, and strategy efficacy after each measurement round.

```
+-------------------------------------------------------------------------+
|                              INPUT LAYER                                |
|  - Cipher (S-AES / Toy SPN / Abstract)                                  |
|  - Key Size n, Known Constraints (Prefix, Parity, Dictionary)           |
|  - Target Plaintext / Ciphertext Pair                                   |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                           CLASSICAL ANALYZER                            |
|  - Candidate Filter (Extracts N' reduced keys, safety check)            |
|  - Classical Brute-Force Cost Model (Worst N, Expected N/2)             |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                           ADAPTIVE CONTROLLER                           |
|  - Online Noise & Fidelity Estimator (Calibration / Decay Model)        |
|  - Policy Engine (Rule-Based, Empirical Regression Surface)             |
|  - Dynamic Decision Loop: Continue / Stop / Restart / Switch Strategy   |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                             QUANTUM ENGINE                              |
|  - State Preparation (Uniform superposition over N' or padded 2^m)      |
|  - Oracle Modes: Mode A (Marked-State Phase) / Mode B (Reversible SPN)  |
|  - Grover Diffuser & Transpilation (Coupling Map, Basis Gates)          |
|  - Execution (Ideal Statevector, Qiskit Aer Depolarizing, Fake IBM)     |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                        VERIFICATION & ANALYTICS                         |
|  - Classical Oracle / Key Verification                                  |
|  - Comprehensive Cost Accounting (Classical Filtering + Quantum Ops)    |
|  - Statistical Validation (Bootstrap 95% CIs, Effect Sizes)             |
+-------------------------------------------------------------------------+
```

---

## 2. Component Specifications

### 2.1 Ciphers (`agqca.ciphers`)
- **`Cipher` Base Class**: Defines `encrypt(plaintext, key)`, `decrypt(ciphertext, key)`, `key_size`, `block_size`, and validation methods.
- **`SimplifiedAES` (S-AES)**: 16-bit block cipher with 16-bit key. Implements NibbleSub via GF($2^4$) inversion, ShiftRows, MixColumns (matrix multiplication in GF($2^4$)), and AddRoundKey across 2 rounds. Validated against published Schaefer (2003) test vectors.
- **Archived Pedagogical SPN (`archive/toyspn.py`)**: Howard Heys's 16-bit pedagogical SPN reference implementation preserved in `archive/` for historical provenance.

### 2.2 Oracles (`agqca.oracles`)
- **Mode A (`MarkedStateOracle`)**: Multi-controlled phase oracle built from precomputed target key indices. Ideal for statistical sweeps ($n \le 12$) and noise sensitivity benchmarking.
- **Mode B (`ReversibleSPNOracle`)**: Fully reversible quantum circuit implementing $U_f: |k\rangle |0\rangle |-\rangle \to |k\rangle |0\rangle (-1)^{[E_k(P)=C]}|-\rangle$. Computes cipher, compares against ciphertext $C$ using an ancilla flag, and uncomputes cipher state to leave ancillae clean. Evaluated at measured key sizes $n \in \{4, 8, 12, 16\}$.

### 2.3 Noise Engine (`agqca.noise`)
- Parameterized depolarizing, readout, and thermal relaxation ($T_1, T_2$) models.
- **Realistic NISQ Regime**: Two-qubit gate error rates $\epsilon_{2q} \in [0.05\%, 1.0\%]$ reflecting current superconducting transmon and trapped-ion hardware.
- **Stress-Test Regime**: $\epsilon_{2q} \in [2.0\%, 20.0\%]$ evaluating resilience against severe decoherence.
- Hardware-calibrated IBM fake backends (`FakeManilaV2`, `FakeSherbrooke`) with strict qubit capacity verification.
- **Semi-Analytic Decay Model**:
  $$p_{\text{noisy}}(k) = p_{\text{ideal}}(k) \cdot F^k + \frac{1 - F^k}{N}$$

### 2.4 Search Strategies (`agqca.strategies`)
All strategies inherit from `BaseStrategy` with equalized total call budgets $B_{\max}$:
- `ClassicalBruteForceStrategy`: Uniform exhaustive search (unfiltered and filtered).
- `RandomGuessNullControlStrategy`: Pure blind random sampling with verification baseline.
- `StandardGroverStrategy`: Fixed optimal iterations ($k \approx \frac{\pi}{4}\sqrt{N}$).
- `NoiseAwareGroverStrategy`: Optimizes iteration count $k^* = \arg\min_k \frac{k}{p_{\text{noisy}}(k)}$.
- `ShallowRestartStrategy`: Depth-capped shallow Grover ($k_{\text{shallow}} \ll k_{\text{ideal}}$) with repeated classical restarts.
- `AdaptiveHybridStrategy`: Full 4-lever controller with online Bayesian fidelity estimation and dynamic policy actions.
- *Note*: Boyer-Brassard-Høyer-Tapp (`BBHTStrategy`) is archived in `archive/bbht.py` as symmetric key search typically addresses known $M=1$ marked keys.

### 2.5 Metrics & Accounting (`agqca.metrics`)
Every run tracks:
- Total classical filtering queries ($C_{\text{filter}}$)
- Quantum iterations ($k_{\text{total}}$) and oracle calls
- Transpiled depth, total gates, 2-qubit (CX/CZ) gate count
- Classical candidate verifications ($C_{\text{verify}}$)
- Total effective wall-clock and equivalent query cost:
  $$\text{Total Cost} = C_{\text{filter}} + \sum_{\text{rounds}} (k_i \cdot \text{Cost}_{\text{oracle}}) + C_{\text{verify}}$$

### 2.6 Readiness Analyzer (`agqca.analyzer`)
Evaluates symmetric cipher security against quantum attacks using verified literature references (Grassl et al. 2016, Jaques et al. 2020) and conservative noisy circuit models. Outputs:
- Ideal Grover iterations ($2^{n/2}$)
- Logical qubit and gate requirements from verified publications
- Feasibility score under user-defined depth and error budget
- Standard mandatory disclaimer: "Experimental estimate; not a formal cryptographic certification; no claim that current hardware can break the analyzed cipher."
