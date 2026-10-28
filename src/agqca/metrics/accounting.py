"""Honest full-cost accounting and speedup calculations."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CostBreakdown:
    """Rigorous cost accounting balancing classical overhead and quantum queries."""

    classical_filtering_cost: int
    quantum_oracle_calls: int
    classical_verification_cost: int
    total_cost: float
    classical_baseline_expected: float
    effective_speedup: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classical_filtering_cost": self.classical_filtering_cost,
            "quantum_oracle_calls": self.quantum_oracle_calls,
            "classical_verification_cost": self.classical_verification_cost,
            "total_cost": self.total_cost,
            "classical_baseline_expected": self.classical_baseline_expected,
            "effective_speedup": self.effective_speedup,
        }


def compute_honest_cost(
    classical_filter_cost: int,
    quantum_oracle_calls: int,
    classical_verify_cost: int,
    total_search_space: int,
    oracle_weight: float = 1.0,
) -> CostBreakdown:
    """Compute honest total cost and effective speedup over classical brute force.

    Total Cost = Filter_Cost + (Quantum_Oracle_Calls * Oracle_Weight) + Verify_Cost.
    Classical Baseline Expected Cost = N / 2.
    Effective Speedup = Baseline / Total_Cost.

    Args:
        classical_filter_cost: Classical evaluations in candidate filtering.
        quantum_oracle_calls: Total quantum circuit Grover oracle queries.
        classical_verify_cost: Classical evaluations to verify candidate keys.
        total_search_space: Full unconstrained search space N = 2^n.
        oracle_weight: Multiplier for quantum oracle complexity relative to classical test.

    Returns:
        CostBreakdown object.
    """
    total = (
        float(classical_filter_cost)
        + float(quantum_oracle_calls) * oracle_weight
        + float(classical_verify_cost)
    )
    baseline = float(total_search_space) / 2.0
    speedup = baseline / total if total > 0 else 0.0

    return CostBreakdown(
        classical_filtering_cost=classical_filter_cost,
        quantum_oracle_calls=quantum_oracle_calls,
        classical_verification_cost=classical_verify_cost,
        total_cost=total,
        classical_baseline_expected=baseline,
        effective_speedup=speedup,
    )
