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
- **`SimplifiedAES` (S-AES)**: 16-bit block cipher with 16-bit key. Implements NibbleSub via GF($2^4$) inversion, ShiftRows, MixColumns (matrix multiplication in GF($2^4$)), and AddRoundKey across 2 rounds. Includes standard test vectors.
- **`ToySPN`**: 16-bit Substitution-Permutation Network cipher. Implements 4 rounds of four 4-bit S-boxes with bit-level permutation diffusion and round key mixing.

### 2.2 Oracles (`agqca.oracles`)
- **Mode A (`MarkedStateOracle`)**: Multi-controlled phase oracle built from the precomputed valid key indices. Ideal for statistical sweeps ($n \le 16$).
- **Mode B (`ReversibleCipherOracle`)**: Fully reversible quantum circuit implementing $U_f: |k\rangle |0\rangle |-\rangle \to |k\rangle |0\rangle (-1)^{[E_k(P)=C]}|-\rangle$. Computes cipher, compares against ciphertext $C$ using ancilla flag, and uncomputes cipher state to leave ancillae clean.

### 2.3 Noise Engine (`agqca.noise`)
- Configurable noise channels:
  - Depolarizing 1-qubit and 2-qubit errors ($0\% \le \epsilon \le 20\%$)
  - Readout bit-flip errors
  - Thermal relaxation ($T_1, T_2$)
  - IBM Fake Backends (`FakeManila`, `FakeSherbrooke`)
- **Semi-Analytic Decay Model**:
  $$p_{\text{noisy}}(k) = p_{\text{ideal}}(k) \cdot F^k + \frac{1 - F^k}{N}$$

### 2.4 Search Strategies (`agqca.strategies`)
All strategies inherit from `BaseStrategy`:
- `ClassicalBruteForceStrategy`
- `StandardGroverStrategy`
- `BBHTStrategy` (Boyer-Brassard-Høyer-Tapp for unknown $M$)
- `NoiseAwareGroverStrategy` ($\min k / p_{\text{noisy}}(k)$)
- `ShallowRestartStrategy` ($k \le k_{\text{shallow}} \ll k_{\text{ideal}}$)
- `AdaptiveHybridStrategy` (Full controller integration)

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
