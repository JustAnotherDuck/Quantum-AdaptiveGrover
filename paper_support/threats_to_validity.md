# Threats to Validity

To preserve absolute scientific rigor and intellectual honesty, this document evaluates the threats to validity, modeling assumptions, and boundaries of the empirical findings in AdaptiveGrover-QCA.

---

## 1. Simulation-vs-Hardware Gap

- **Noise Idealizations**: We model noise primarily via independent 1-qubit and 2-qubit depolarizing error channels, augmented by thermal relaxation ($T_1/T_2$) and readout errors. Physical superconducting and trapped-ion hardware exhibit correlated errors, spatial crosstalk, spectator qubit phase drift, and leakage outside the computational subspace that simple depolarizing channels do not fully capture.
- **Transpiler Topology**: Simulations assume all-to-all connectivity or standard heavy-hex layouts. Real devices require SWAP gate routing overhead that scales with circuit width and physical coupling maps.

## 2. Toy Cipher Representativeness

- **Scale Discrepancy**: Simplified AES (16-bit block/key, 2 rounds) and Toy SPN (16-bit block/key, 4 rounds) capture the algebraic structure (Galois field arithmetic, diffusion matrices, non-linear S-boxes), but differ fundamentally in scale from AES-128 (128-bit block/key, 10 rounds) and AES-256 (14 rounds).
- **S-box Complexity**: S-AES uses a 4-bit S-box ($2^4=16$ elements, inversion in GF($2^4$)), whereas AES uses an 8-bit S-box ($2^8=256$ elements, inversion in GF($2^8$)). Synthesizing reversible 8-bit S-boxes requires significantly deeper circuits (e.g. Boyar-Peralta or Itoh-Tsujii logic) than 4-bit S-boxes.

## 3. Oracle Mode Differences

- **Mode A vs Mode B**: Mode A (multi-controlled phase flips) reflects the algorithmic behavior of Grover's iteration loop but does not simulate the physical circuit operations of the cipher. Mode B provides true reversible cipher gate counts and uncomputation costs. Findings regarding gate count scaling should strictly reference Mode B, whereas statistical convergence sweeps across noise levels leverage Mode A.

## 4. Coherent Errors vs Incoherent Depolarization

- The semi-analytic decay model $p_{\text{noisy}}(k) \approx p_{\text{ideal}}(k) F^k + (1 - F^k)/N$ models incoherent state mixing. Coherent over-rotations (systematic calibration drifts) can cause destructive interference that deviates from monotonic exponential decay at high iteration counts.

## 5. Extrapolation Risks

- Extrapolations from 16 bits to 128 bits in Experiment 6 are architectural projections based on reversible gate counts. They do not model physical surface code fault-tolerance overheads, magic state distillation factories, or syndrome measurement decoding latencies.
