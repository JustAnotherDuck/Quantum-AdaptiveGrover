"""Resource tracking for quantum circuit execution and cost estimation."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from qiskit import QuantumCircuit, transpile


@dataclass
class ExecutionRecord:
    """Detailed telemetry record for a single strategy execution run."""

    strategy_name: str
    target_key: int
    found_key: Optional[int]
    is_verified: bool
    iterations: int
    oracle_calls: int
    classical_filter_cost: int
    classical_verify_cost: int
    total_effective_cost: float
    circuit_depth: int
    qubits_total: int
    two_qubit_gates: int
    total_gates: int
    shots: int
    noise_level: float
    wall_clock_time: float
    seed: int
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_name": self.strategy_name,
            "target_key": self.target_key,
            "found_key": self.found_key,
            "is_verified": self.is_verified,
            "iterations": self.iterations,
            "oracle_calls": self.oracle_calls,
            "classical_filter_cost": self.classical_filter_cost,
            "classical_verify_cost": self.classical_verify_cost,
            "total_effective_cost": self.total_effective_cost,
            "circuit_depth": self.circuit_depth,
            "qubits_total": self.qubits_total,
            "two_qubit_gates": self.two_qubit_gates,
            "total_gates": self.total_gates,
            "shots": self.shots,
            "noise_level": self.noise_level,
            "wall_clock_time": self.wall_clock_time,
            "seed": self.seed,
            **self.extra_metadata,
        }


class CircuitResourceTracker:
    """Calculates gate counts, transpiled depth, and entangling gate resources."""

    @staticmethod
    def analyze_circuit(
        qc: QuantumCircuit,
        basis_gates: Optional[list[str]] = None,
        optimization_level: int = 1,
    ) -> Dict[str, int]:
        """Transpile and return exact gate counts, 2q gates, and depth."""
        if basis_gates is None:
            basis_gates = ["u", "cx"]

        tqc = transpile(
            qc,
            basis_gates=basis_gates,
            optimization_level=optimization_level,
        )
        ops = dict(tqc.count_ops())
        two_q = sum(ops.get(g, 0) for g in ["cx", "cz", "ecr", "swap"])
        total_g = sum(ops.values())

        return {
            "depth": tqc.depth(),
            "total_gates": total_g,
            "two_qubit_gates": two_q,
            "qubits": tqc.num_qubits,
        }
