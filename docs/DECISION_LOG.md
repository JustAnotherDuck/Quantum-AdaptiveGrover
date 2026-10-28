# AdaptiveGrover-QCA Decision Log

This log records every non-obvious architecture, algorithmic, and methodological decision made during the development of AdaptiveGrover-QCA, along with the concrete rationale and trade-offs.

---

## DEC-0001: Framework Working Name
- **Date**: 2026-10-29
- **Decision**: Retain the proposed name **AdaptiveGrover-QCA** (Adaptive Grover Quantum Cryptanalysis).
- **Rationale**: Accurately describes the core contribution (adaptive, noise-aware control applied to quantum cryptanalysis) while maintaining clear distinction between standard theoretical Grover search and application-oriented controller-guided execution.

## DEC-0002: Target Toy Ciphers Selection
- **Date**: 2026-10-29
- **Decision**: Implement two distinct toy ciphers:
  1. **Simplified AES (S-AES)** (Schaefer, 2003): 16-bit block, 16-bit key, 2 rounds with NibbleSub (GF($2^4$) inversion + affine mapping), ShiftRows, MixColumns (GF($2^4$) matrix multiplication), and Round Key Addition.
  2. **Toy SPN (Heys-style)**: 16-bit block, 16-bit key, 4 rounds with four 4-bit S-boxes, a 16-bit bit-level permutation layer, and XOR round key scheduling.
- **Rationale**: S-AES directly mirrors the algebraic and structural properties of standard AES-128 (galois field arithmetic, mix columns matrix, key schedule), making resource projections credible. The Heys SPN provides a distinct structural contrast (bit-permutation diffusion vs matrix diffusion) to test whether controller behavior generalizes across cipher designs.

## DEC-0003: Dual Oracle Architecture (Mode A vs Mode B)
- **Date**: 2026-10-29
- **Decision**:
  - **Mode A (Marked-State Oracle)**: Synthesizes multi-controlled phase flips directly for the known target key(s). Employs Gray-code decomposition or multi-controlled Z gates. Fast, allowing simulations up to $n=14-16$ qubits. Explicitly annotated in all outputs as reflecting algorithmic iterations rather than physical cipher gate counts.
  - **Mode B (Reversible Cipher Circuit Oracle)**: Synthesizes the full reversible quantum circuit: $|k\rangle |0\rangle |0\rangle \to |k\rangle |E_k(P)\rangle |0\rangle \to |k\rangle |E_k(P)\rangle |E_k(P) \stackrel{?}{=} C\rangle \to |k\rangle |0\rangle |(-1)^{[E_k(P)=C]}\rangle$.
- **Rationale**: Mode B gives ground-truth gate counts, depth, and ancilla scaling for reversible cipher execution, but is constrained in simulation by qubit memory. Mode A allows extensive statistical sweeps ($\ge 30$ seeds) across noise rates and strategy space. Providing both ensures physical fidelity without sacrificing statistical rigor.

## DEC-0004: Noise Modeling Convention & Transpilation Baseline
- **Date**: 2026-10-29
- **Decision**: Gate errors are modeled via depolarizing noise channels parameterized by error rates $\epsilon \in \{0.00, 0.02, 0.05, 0.10, 0.15, 0.20\}$. In the default convention, 2-qubit gates (CX/CZ) receive error rate $\epsilon_{2q} = \epsilon$, while single-qubit gates receive $\epsilon_{1q} = \epsilon / 10$ to reflect realistic superconducting qubit characteristics. Readout errors are symmetric bit-flip channels. Fake IBM backends (e.g., FakeManila) provide full calibration-derived T1/T2 and crosstalk context.
- **Rationale**: Symmetric depolarizing noise where 2-qubit gates dominate reflects physical hardware realities where two-qubit entangling gates are typically an order of magnitude noisier than single-qubit gates.

## DEC-0005: Empirical Noisy Decay Formulation
- **Date**: 2026-10-29
- **Decision**: Formulate the noisy success probability as:
  $$p_{\text{noisy}}(k) = p_{\text{ideal}}(k) \cdot F^k + \frac{1 - F^k}{N}$$
  where $p_{\text{ideal}}(k) = \sin^2((2k+1)\theta)$, $\theta = \arcsin(\sqrt{M/N})$, and $F \in (0, 1]$ represents the effective per-iteration Grover fidelity parameter.
- **Rationale**: Under depolarizing noise, the quantum state $\rho_k$ after $k$ Grover iterations decays towards the maximally mixed state $I/N$. Measuring the maximally mixed state yields the target key with random guessing probability $1/N$. This model captures both the coherent rotation dampening and the incoherent floor.

## DEC-0006: Objective Function for Noise-Aware and Shallow-Restart Strategies
- **Date**: 2026-10-29
- **Decision**: Optimize strategy parameters (iteration count $k$, shallow cutoff $k_{\text{shallow}}$) by minimizing the **expected total oracle cost to first verified key**:
  $$\mathbb{E}[\text{Cost}] = \frac{k}{p_{\text{noisy}}(k)} + C_{\text{verify}}$$
  rather than simply maximizing single-shot success probability $p(k)$.
- **Rationale**: In noisy regimes, pushing iterations to the ideal $k_{\text{ideal}} \approx \frac{\pi}{4}\sqrt{N}$ causes catastrophic decoherence, yielding low $p(k)$. Running fewer iterations $k < k_{\text{ideal}}$ produces a lower single-shot success probability but at drastically lower depth, allowing multiple rapid restarts with lower aggregate cost.

## DEC-0007: Classical Candidate Filtering & Non-Power-of-Two Superposition
- **Date**: 2026-10-29
- **Decision**: Filtering reduces search space from $N$ to $N'$. For quantum search, if $N'$ is a power of 2 ($2^m$), standard Hadamard initialization is used. If $N'$ is not a power of 2, prepare exact uniform superposition over $N'$ states using state preparation decomposition or embed into the next power of 2 ($2^{\lceil \log_2 N' \rceil}$) with non-target ancilla markers, ensuring honest accounting of ancilla and search space overhead.
- **Rationale**: Real-world cryptographic constraints (e.g. byte ranges or parity checks) do not always produce power-of-two candidate sets. Handling arbitrary $N'$ accurately prevents artificial distortion of quantum speedup.
