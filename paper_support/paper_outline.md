# Target Research Manuscript Outline

Suggested structure for the forthcoming academic research paper based on the AdaptiveGrover-QCA framework.

---

### Section 1: Introduction
- Motivation: Asymptotic speedup vs physical NISQ realities.
- Research Question: How much quadratic advantage survives under gate noise, depth limits, and decoherence?
- Summary of Proposed Framework: 4 synergistic levers (filtering, noise-awareness, shallow restarts, adaptive controller).
- Non-Negotiable Safety Stance: Clarification of reduced-scale experimental scope and absence of live attack capabilities.

### Section 2: Theoretical Foundations & Noisy Decay Model
- Grover search mathematics and optimal iteration bounds.
- Derivation of the semi-analytic noisy decay model:
  $$p_{\text{noisy}}(k) = p_{\text{ideal}}(k) F^k + \frac{1 - F^k}{N}$$
- Objective function: Minimizing $\mathbb{E}[\text{Cost}] = \frac{k}{p_{\text{noisy}}(k)} + C_{\text{verify}}$.

### Section 3: Architecture & Dual Oracle Implementation
- Target educational ciphers: Simplified AES (S-AES) and 4-Round 16-bit Toy SPN.
- Mode A (Marked-State Phase Oracle) for extensive statistical sweeps.
- Mode B (Reversible Cipher Circuit Oracle): Compute-copy-uncompute reversible quantum compilation.

### Section 4: Adaptive Control & Classical Filtering
- Classical constraint processing and non-power-of-two state preparation.
- Safety fallback guarantee.
- Controller policies (Rule-based vs Data-driven regression surface).
- Online Bayesian posterior tracking.

### Section 5: Experimental Evaluation & Empirical Results
- **Exp 1**: Scalability baseline across key sizes (Fig 1, Table 1).
- **Exp 2**: Noise resilience across 0% to 20% error rates (Fig 2).
- **Exp 3**: Crossover analysis: identifying the ~5-6% noise threshold where shallow restarts dominate deep Grover (Fig 3).
- **Exp 4**: Classical filtering efficiency and super-linear speedup gains (Fig 4).
- **Exp 5**: Ablation study isolating the 4 individual levers (Fig 5, Table 2).
- **Exp 6**: Mode B reversible circuit resource scaling and extrapolation to 128-bit keys (Fig 6, Table 3).

### Section 6: Cryptographic Readiness Analyzer
- Integration with verified literature (Grassl 2016, Jaques 2020).
- Feasibility verdicts under physical noise budgets.
- Quantitative proof of NISQ security for AES-128 and AES-256.

### Section 7: Discussion, Threats to Validity & Limitations
- Threats to validity (simulation-hardware gap, toy cipher representativeness, coherent vs incoherent noise).
- Negative results: Regimes where adaptivity yields diminishing returns.

### Section 8: Conclusion & Future Work
- Summary of core contributions.
- Future roadmap: Physical IBM Quantum hardware execution, RL-based policy training, and distributed multi-target search.
