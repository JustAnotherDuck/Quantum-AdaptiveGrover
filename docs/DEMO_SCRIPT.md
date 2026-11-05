# AdaptiveGrover-QCA: 3–5 Minute Interactive Research Demo Script

This script provides structured talking points, navigation cues, and contingency procedures for demonstrating the **AdaptiveGrover-QCA** research platform to academic reviewers, colleagues, or industry stakeholders.

---

## 0. Launching the Research Dashboard (< 30 seconds)

### Command to Launch
```bash
make dashboard
```
*Builds the React frontend and launches the unified FastAPI service at `http://localhost:8000`.*

### Offline Fallback Procedure
If operating in an isolated or offline network environment, the platform runs completely self-contained. All simulation models, Bayesian controllers, and the interactive research assistant operate locally with deterministic offline reasoning.

---

## 1. Opening & Scientific Integrity Disclaimer (Minute 0:00 – 0:45)

**Talking Point**:
> *"Welcome. Today we demonstrate **AdaptiveGrover-QCA**, an experimental framework addressing a core question in quantum cryptanalysis: **How much of Grover's theoretical quadratic advantage actually survives under realistic noisy, depth-limited quantum execution, and can an adaptive controller recover search efficiency?**"*

**Visual Action**:
- Point out the prominent amber banner at the top of the **Overview** view:
  > *"Before presenting any metrics, our framework adheres to strict scientific integrity standards: all evaluations operate on reduced-scale ciphers in simulation. No claim is made that near-term NISQ hardware can break AES-128 or AES-256. Full AES key recovery requires fault-tolerant logical qubits that do not exist today."*

---

## 2. Overview & Empirical Scaling Exponents (Minute 0:45 – 1:30)

**Visual Action**:
- Stay on the **Overview** tab.
- Highlight the **Core Experimental Results Matrix** table:
  - Classical Brute Force: $\alpha = 1.000$ (Theory: $\mathcal{O}(N)$)
  - Standard Grover: $\alpha = 0.499$ (Theory: $\mathcal{O}(\sqrt{N})$)
  - Adaptive Hybrid: $\alpha = 0.131$ (Sub-quadratic with classical filtering)

**Talking Point**:
> *"Under low noise, our empirical measurements up to $n = 12$ bits confirm that Grover achieves an empirical scaling exponent $\alpha = 0.499$, validating theoretical quadratic scaling. But what happens when physical gate error is introduced?"*

---

## 3. Noise Crossover & The Shallow Restart Boundary (Minute 1:30 – 2:30)

**Visual Action**:
- Click on **"Noise Crossover"** in the top navigation bar.
- Point to the interactive ECharts degradation curves:
  - Vermillion line: Standard Grover (collapsing rapidly past 5% noise).
  - Blue line: Shallow + Restart (sustaining search capability).
  - Green line: Adaptive Hybrid.

**Talking Point**:
> *"Here we observe the central physical trade-off:*
> - *Standard Grover relies on coherent phase interference across all iterations. Once gate noise exceeds 5%, deeper circuits suffer catastrophic decoherence, flattening success to uniform noise.*
> - *Notice the crossover boundary $\epsilon^* \approx 17.87\%$ (95% bootstrap CI: $[17.61\%, 18.12\%]$): beyond this point, shallow circuits with restarts strictly outperform deep coherent Grover under an equalized budget of 15,000 calls.*
> - *The single-circuit coherence horizon occurs even earlier, around 5% error."*

---

## 4. Fair Filtering Baseline: Separating Classical from Quantum (Minute 2:30 – 3:15)

**Visual Action**:
- Click on **"Filtering Cost"**.
- Select 2 prefix constraint bits.
- Point to the **Decomposition Table** and the quantum speedup column $S_{\text{quantum}}$.

**Talking Point**:
> *"A critical finding of our validation audit is the **fair filtering baseline**:*
> - *Filtering down candidate space from $N \to N'$ provides a classical reduction factor $N/N'$.*
> - *To prevent false claims of quantum advantage, we benchmark filtered Grover against **filtered classical brute force**.*
> - *On small key spaces ($n \le 8$), quantum gate overheads and classical verification result in a quantum-specific speedup $S_{\text{quantum}} < 1.0\times$. True quantum advantage emerges only asymptotically when $N' \gg 2^{16}$."*

---

## 5. AES Readiness & Interactive Assistant (Minute 3:15 – 4:30)

**Visual Action**:
- Click on **"AES Readiness"**.
- Select **`AES-128`** and adjust the Physical Error Rate slider.
- Point to the NISQ Feasibility Assessment Verdict: **"Infeasible on NISQ"** with survival probability $0.00 \times 10^0$.
- Click **"Research Assistant"** in the top right to open the conversational drawer.
- Click the suggestion chip: *"Can quantum computers break AES-128?"*
- Show the grounded reply citing Grassl et al. (2016) and Jaques et al. (2020).

**Talking Point**:
> *"When industry asks whether current quantum computers threaten AES, our Readiness Analyzer provides a peer-reviewed, grounded answer.*
> - *AES-128 requires over $1.18 \times 10^{19}$ sequential Grover iterations and between 1,785 and 2,953 logical qubits.*
> - *On NISQ hardware with 0.1% physical error, the circuit survival probability is mathematically zero.*
> - *Full AES remains completely secure against near-term quantum devices."*

---

## 6. Closing & Audit Verification (Minute 4:30 – 5:00)

**Visual Action**:
- Click on **"Methods & Audit"**.
- Show the 8 completed audit action items (A1 through A8).
- Conclude:
  > *"All experimental code, aggregated data, figures, and tables are fully reproducible via `make audit` and `make reproduce-small`."*
