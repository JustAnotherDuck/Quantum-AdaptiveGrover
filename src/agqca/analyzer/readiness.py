"""Quantum Cryptographic Readiness Analyzer engine."""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from agqca.analyzer.literature import LiteratureRecord, load_literature_database

SAFETY_DISCLAIMER = (
    "EXPERIMENTAL ESTIMATE ONLY: Not a formal cryptographic certification. "
    "This research framework evaluates reduced-scale instances in simulation. "
    "No claim is made that current quantum hardware can break AES-128 or AES-256."
)


@dataclass
class ReadinessEvaluation:
    """Readiness analysis report for a cipher instance under quantum threat."""

    cipher_name: str
    key_size: int
    effective_key_size: int
    ideal_iterations: float
    ideal_oracle_calls_str: str
    literature_estimates: List[LiteratureRecord]
    quantum_risk_level: int  # 1 (Safe) to 5 (Critical)
    quantum_risk_label: str
    feasibility_verdict: str
    estimated_nisq_depth: float
    nisq_survival_probability: float
    mandatory_disclaimer: str = SAFETY_DISCLAIMER
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cipher_name": self.cipher_name,
            "key_size": self.key_size,
            "effective_key_size": self.effective_key_size,
            "ideal_iterations": self.ideal_iterations,
            "ideal_oracle_calls_str": self.ideal_oracle_calls_str,
            "quantum_risk_level": self.quantum_risk_level,
            "quantum_risk_label": self.quantum_risk_label,
            "feasibility_verdict": self.feasibility_verdict,
            "estimated_nisq_depth": self.estimated_nisq_depth,
            "nisq_survival_probability": self.nisq_survival_probability,
            "literature_estimates": [r.model_dump() for r in self.literature_estimates],
            "mandatory_disclaimer": self.mandatory_disclaimer,
            "details": self.details,
        }


class ReadinessAnalyzer:
    """Analyzes cipher security against quantum search attacks."""

    def __init__(self, literature_db: Optional[List[LiteratureRecord]] = None) -> None:
        self.literature_db = (
            literature_db
            if literature_db is not None
            else load_literature_database(verified_only=True)
        )

    def evaluate(
        self,
        cipher_name: str,
        key_size: int,
        known_bits: int = 0,
        noise_level: float = 0.001,  # 0.1% gate error
    ) -> ReadinessEvaluation:
        """Evaluate quantum attack readiness for given cipher parameters.

        Args:
            cipher_name: e.g. 'AES-128', 'AES-256', 'S-AES', 'ToySPN'.
            key_size: Total key length in bits.
            known_bits: Number of bits known classically (pre-filtering reduction).
            noise_level: Physical gate error rate.

        Returns:
            ReadinessEvaluation with metrics, literature references, and safety disclaimers.
        """
        eff_n = max(1, key_size - known_bits)
        ideal_k = (math.pi / 4.0) * (2.0 ** (eff_n / 2.0))
        oracle_calls_str = f"2^{eff_n / 2.0:.1f} (≈ {ideal_k:.2e})"

        # Find matching verified literature records
        matched_lit = [
            r
            for r in self.literature_db
            if r.cipher.lower() == cipher_name.lower()
            or (r.key_size == key_size and "AES" in cipher_name)
        ]

        # Estimate depth per iteration (approx 200-3000 layers per round)
        depth_per_iter = 2500 if key_size >= 128 else 200
        total_depth = ideal_k * depth_per_iter

        # NISQ survival probability: P_surv ≈ (1 - epsilon)^depth
        if total_depth > 1e6 or noise_level * total_depth > 500:
            survival_prob = 0.0
        else:
            survival_prob = float((1.0 - noise_level) ** total_depth)

        # Risk level determination
        if eff_n <= 16:
            risk_lvl = 5
            risk_lbl = "CRITICAL (Demonstrably Recoverable in Small Scale / Simulation)"
            verdict = "FEASIBLE: Search space is small enough for simulated NISQ quantum attacks."
        elif eff_n <= 32:
            risk_lvl = 4
            risk_lbl = "HIGH THEORETICAL VULNERABILITY (Reduced Key Space)"
            verdict = (
                "MARGINALLY FEASIBLE: Requires substantial quantum coherence or large filtering."
            )
        elif eff_n <= 64:
            risk_lvl = 3
            risk_lbl = "MEDIUM RISK (Theoretical Quantum Advantage, Infeasible on NISQ)"
            verdict = (
                "NISQ-INFEASIBLE: Depth exceeds physical coherence times by orders of magnitude."
            )
        else:
            risk_lvl = 1
            risk_lbl = "LOW IMMEDIATE RISK (Standard Cryptographic Key Length)"
            verdict = (
                "TOTALLY INFEASIBLE ON NISQ HARDWARE: Requires large-scale fault-tolerant quantum "
                "computer with error-corrected logical qubits (e.g. millions of physical qubits)."
            )

        return ReadinessEvaluation(
            cipher_name=cipher_name,
            key_size=key_size,
            effective_key_size=eff_n,
            ideal_iterations=ideal_k,
            ideal_oracle_calls_str=oracle_calls_str,
            literature_estimates=matched_lit,
            quantum_risk_level=risk_lvl,
            quantum_risk_label=risk_lbl,
            feasibility_verdict=verdict,
            estimated_nisq_depth=total_depth,
            nisq_survival_probability=survival_prob,
            details={
                "known_bits": known_bits,
                "noise_rate_tested": noise_level,
                "depth_per_iteration": depth_per_iter,
            },
        )


@dataclass
class CipherReadinessReport:
    """Detailed cryptographic cipher readiness report aligned with API schema."""

    cipher_name: str
    key_size: int
    block_size: int
    ideal_grover_iterations_exp: int
    logical_qubits_required: int
    circuit_depth_estimate: int
    two_qubit_gates: int
    total_gates: int
    physical_error_rate: float
    circuit_survival_probability: float
    nisq_feasibility_verdict: str
    literature_source: str
    disclaimer: str = SAFETY_DISCLAIMER


def evaluate_cipher_readiness(
    cipher_name: str,
    physical_gate_error: float = 0.001,
    surface_code_threshold: float = 0.01,
) -> CipherReadinessReport:
    """Evaluate cipher quantum attack feasibility against verified literature and NISQ limits."""
    name_upper = cipher_name.upper()
    if "AES-128" in name_upper:
        key_size = 128
        block_size = 128
        ideal_exp = 64
        logical_qubits = 1785
        depth = 1416000000000000000000
        two_q = 54400 * 11800000000000000000
        total_g = 120000 * 11800000000000000000
        survival = 0.0
        verdict = (
            "Infeasible on NISQ: Depth (~10^21) and logical qubit requirement (1,785-2,953) "
            "exceed NISQ limits by over 18 orders of magnitude. Requires fault-tolerant quantum computing."
        )
        source = "Jaques et al. (EUROCRYPT 2020) & Grassl et al. (PQCrypto 2016)"
    elif "AES-192" in name_upper:
        key_size = 192
        block_size = 128
        ideal_exp = 96
        logical_qubits = 4449
        depth = 4488 * 18900000000000000000000000000
        two_q = 1428480 * 18900000000000000000000000000
        total_g = 2000000 * 18900000000000000000000000000
        survival = 0.0
        verdict = (
            "Infeasible on NISQ: Depth (~10^31) and logical qubit requirement (4,449) "
            "far exceed any near-term quantum system. Requires fault-tolerant quantum computing."
        )
        source = "Grassl et al. (PQCrypto 2016)"
    elif "AES-256" in name_upper:
        key_size = 256
        block_size = 128
        ideal_exp = 128
        logical_qubits = 6681
        depth = 5236 * 2420000000000000000000000000000000000000
        two_q = 1666560 * 2420000000000000000000000000000000000000
        total_g = 3000000 * 2420000000000000000000000000000000000000
        survival = 0.0
        verdict = (
            "Infeasible on NISQ: Depth (~10^41) and logical qubit requirement (6,681) "
            "far exceed physical coherence limits. Requires fault-tolerant quantum computing."
        )
        source = "Grassl et al. (PQCrypto 2016)"
    elif "S-AES" in name_upper:
        key_size = 16
        block_size = 16
        ideal_exp = 8
        logical_qubits = 24
        depth = 40200
        two_q = 1500
        total_g = 4200
        survival = float(max(0.0, (1.0 - physical_gate_error) ** min(depth, 50000)))
        verdict = "Feasible in Simulation / Scaled NISQ Benchmark: Infeasible on NISQ without error mitigation due to depth."
        source = "Feldhofer et al. (Reduced S-AES Benchmark)"
    else:
        key_size = 16
        block_size = 16
        ideal_exp = 8
        logical_qubits = 16
        depth = 5000
        two_q = 400
        total_g = 1200
        survival = float(max(0.0, (1.0 - physical_gate_error) ** min(depth, 50000)))
        verdict = (
            "Feasible in Simulation / Scaled NISQ Benchmark: Infeasible on NISQ for long depths."
        )
        source = "Heys (1996) / AGQCA Benchmark Suite"

    return CipherReadinessReport(
        cipher_name=cipher_name,
        key_size=key_size,
        block_size=block_size,
        ideal_grover_iterations_exp=ideal_exp,
        logical_qubits_required=logical_qubits,
        circuit_depth_estimate=min(depth, 2**63 - 1),
        two_qubit_gates=min(two_q, 2**63 - 1),
        total_gates=min(total_g, 2**63 - 1),
        physical_error_rate=physical_gate_error,
        circuit_survival_probability=survival,
        nisq_feasibility_verdict=verdict,
        literature_source=source,
        disclaimer=SAFETY_DISCLAIMER,
    )
