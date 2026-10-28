# Research Methods and Experimental Protocol

This document provides a precise, reproducible specification of the experimental methodologies, mathematical models, noise parameterizations, and statistical procedures used in **AdaptiveGrover-QCA**.

---

## 1. Algorithmic Formulations

### 1.1 Grover Search & Analytic Noiseless Formulation
In an unconstrained search space of size $N = 2^n$ with $M$ marked states, the initial state is prepared in uniform superposition:
$$|s\rangle = \frac{1}{\sqrt{N}}\sum_{x=0}^{N-1} |x\rangle = \cos(\theta) |s_{\perp}\rangle + \sin(\theta) |w\rangle$$
where $|w\rangle$ is the uniform superposition over marked states, $|s_{\perp}\rangle$ is the orthogonal subspace, and the Grover rotation angle is:
$$\theta = \arcsin\left(\sqrt{\frac{M}{N}}\right)$$

After $k$ iterations of the Grover operator $G = -(I - 2|s\rangle\langle s|) O_f$, the exact theoretical success probability is:
$$p_{\text{ideal}}(k) = \sin^2((2k+1)\theta)$$
The optimal integer iteration count is given by:
$$k_{\text{opt}} = \left\lfloor \frac{\pi}{4\theta} \right\rceil$$

### 1.2 Semi-Analytic Noisy Decay Model
Under local depolarizing channels, quantum states depolarize towards the maximally mixed state $I/N$. We model the noisy success probability as:
$$p_{\text{noisy}}(k) = p_{\text{ideal}}(k) \cdot F^k + \frac{1 - F^k}{N}$$
where $F \in (0, 1]$ is the effective per-iteration Grover fidelity parameter. $F$ is fitted empirically via non-linear least squares (`scipy.optimize.curve_fit`) bounded in $[0.01, 1.0]$.

### 1.3 Objective Cost Function
Unlike ideal Grover analysis which optimizes $p(k)$, the noise-aware controller minimizes the expected total oracle cost to first verified key:
$$\mathbb{E}[\text{Cost}] = \frac{k}{p_{\text{noisy}}(k)} + C_{\text{verify}}$$

---

## 2. Noise & Transpilation Specifications

### 2.1 Parameterized Depolarizing Noise
Gate noise channels are swept across standard error levels $\epsilon \in \{0.00, 0.02, 0.05, 0.10, 0.15, 0.20\}$:
- **Two-Qubit Gates (CX, CZ, SWAP)**: Depolarizing error rate $\epsilon_{2q} = \epsilon$.
- **Single-Qubit Gates (U, X, SX, RZ)**: Depolarizing error rate $\epsilon_{1q} = \epsilon / 10$.
- **Readout Errors**: Symmetric bit-flip channel with $p_{\text{ro}} = \epsilon / 2$.

### 2.2 Transpilation Standards
Every circuit analyzed for physical depth and gate metrics is transpiled using Qiskit's transpiler with:
- `basis_gates = ['u', 'cx']`
- `optimization_level = 1`

---

## 3. Statistical Protocol

1. **Replication & Seeding**: All experiment sweeps run across $\ge 15$ (small mode) or $\ge 35$ (full mode) independent random seeds.
2. **Paired Comparisons**: When comparing strategies (e.g. Classical vs Standard vs Adaptive), identical instances and noise seeds are fed to all strategies to eliminate instance variance.
3. **Bootstrap Confidence Intervals**: 95% confidence intervals are non-parametrically computed using 2,000 bootstrap resamples ($B = 2000$, $\alpha = 0.05$).
4. **Effect Size**: Standardized mean differences are reported via Cohen's $d$:
   $$d = \frac{\bar{x}_A - \bar{x}_B}{s_{\text{diff}}}$$

---

## 4. Software & Hardware Platform

- **Operating System**: macOS (Darwin 24.3.0, Apple Silicon arm64)
- **Python**: 3.12.4
- **Core Dependencies**:
  - `qiskit`: 2.6.1
  - `qiskit-aer`: 0.18.2
  - `qiskit-ibm-runtime`: 0.51.0
  - `numpy`: 2.5.4
  - `scipy`: 1.18.1
  - `pandas`: 3.1.0
  - `matplotlib`: 3.11.2
