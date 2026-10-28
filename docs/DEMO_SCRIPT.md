# AdaptiveGrover-QCA: 3–5 Minute Interactive Demo Script

This script provides talking points, navigation cues, and contingency fallbacks for presenting **AdaptiveGrover-QCA** to academic peers, reviewers, or executive audiences.

---

## 0. Demo Prerequisites & Launch (< 30 seconds)

### Command to Launch
```bash
make demo
```
*Browser automatically opens at `http://localhost:8501`.*

### Contingency Fallback
If running in an environment without browser access or live Qiskit simulation is slow, ensure **"Fast Offline Demo (Precomputed Cache)"** is selected in the sidebar. This loads saved experimental data instantaneously with zero quantum simulation latency.

---

## 1. Opening & Scientific Integrity Disclaimer (Minute 0:00 – 0:45)

**Talking Point**:
> *"Welcome. Today we present **AdaptiveGrover-QCA**, a reproducible research framework addressing a foundational question in quantum cryptanalysis: **How much of Grover's theoretical quadratic advantage actually survives under realistic noisy, depth-limited quantum execution, and can an adaptive controller recover that advantage?**"*

**Visual Action**:
- Point out the prominent top alert banner:
  > *"First, as a non-negotiable rule of scientific integrity: this framework operates strictly on educational and reduced-scale ciphers in simulation. It does **not** attack full AES-128 or AES-256 and produces experimental estimates, not formal cryptographic certification."*

---

## 2. Tab 1: Strategy Benchmarks & Noise Degradation (Minute 0:45 – 1:45)

**Visual Action**:
- Navigate to **"📊 Strategy Benchmarks"**.
- Point to **Figure 2** (Recovery Rate vs Depolarizing Noise Rate).

**Talking Point**:
> *"Here we examine the survival of quantum advantage across physical gate error rates from 0% to 20%.*
> - *Under zero noise, standard Grover achieves near-perfect recovery with $O(\sqrt{N})$ queries.*
> - *However, look at the orange curve: once noise exceeds 5%, standard Grover suffers catastrophic decoherence. The circuit depth is too great, and the single-shot success probability collapses to random guessing.*
> - *Now observe our **Adaptive Hybrid Controller (green curve)**: by dynamically modulating iteration counts, applying classical filtering, and restarting shallow circuits, it maintains over 85% recovery even at 15–20% physical noise."*

---

## 3. Tab 2: Controller Decision Trace (Minute 1:45 – 2:45)

**Visual Action**:
- Click on **"🤖 Controller Decision Trace"**.
- Set noise slider to `0.05` (5%) and check `Apply Classical Pre-Filtering`.
- Click **"▶️ Simulate Adaptive Controller Execution"**.

**Talking Point**:
> *"Let's look under the hood at how the adaptive controller reasons in real time.*
> 1. *First, the **Classical Analyzer** filters the 16-state key space down to 4 candidates using known constraints, with strict safety verification ensuring the true key was not discarded.*
> 2. *Second, the **Adaptive Controller** inspects the 5% noise environment and chooses a shallow iteration count ($k=1$ or $k=2$) rather than the theoretical ideal ($k=3$), because minimizing $\mathbb{E}[\text{Cost}] = \frac{k}{p_{\text{noisy}}(k)}$ beats maximizing single-shot $p(k)$.*
> 3. *Third, after each measurement round, an **Online Bayesian Estimator** updates posterior beliefs over success rates, triggering rapid restarts until the classical verification oracle confirms the ground-truth key."*

---

## 4. Tab 4: Cryptographic Readiness Analyzer (Minute 2:45 – 3:45)

**Visual Action**:
- Navigate to **"🛡️ Cryptographic Readiness Analyzer"**.
- Select **`AES-128`**.

**Talking Point**:
> *"Finally, we look at the Readiness Analyzer. When industry asks 'Can a quantum computer break AES-128 today?', this tool provides a grounded, literature-verified answer.*
> - *Ideal Grover requires $\approx 2^{64}$ sequential operations.*
> - *Grounded in verified literature (Grassl et al. 2016 and Jaques et al. 2020), a full attack requires between 1,785 and 2,953 logical qubits and millions of physical error-corrected qubits.*
> - *Under realistic NISQ error rates without fault tolerance, circuit survival probability is literally zero ($0.00 \times 10^0$).*
> - *The verdict is unequivocal: **AES-128 is completely safe against NISQ devices**, requiring decades of fault-tolerant error-correction scaling before presenting any practical threat."*

---

## 5. Q&A and Conclusion (Minute 3:45 – 4:00)

**Talking Point**:
> *"In summary, AdaptiveGrover-QCA shows that combining classical filtering, noise-aware depth control, and shallow restarts bridges the gap between asymptotic quantum theory and physical NISQ constraints. The full benchmark suite can be reproduced with a single `make reproduce-small` command. Thank you, and I welcome questions."*
