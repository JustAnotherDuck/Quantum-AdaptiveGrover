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
            literature_db if literature_db is not None else load_literature_database(verified_only=True)
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
            r for r in self.literature_db
            if r.cipher.lower() == cipher_name.lower() or (r.key_size == key_size and "AES" in cipher_name)
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
            verdict = "MARGINALLY FEASIBLE: Requires substantial quantum coherence or large filtering."
        elif eff_n <= 64:
            risk_lvl = 3
            risk_lbl = "MEDIUM RISK (Theoretical Quantum Advantage, Infeasible on NISQ)"
            verdict = "NISQ-INFEASIBLE: Depth exceeds physical coherence times by orders of magnitude."
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
