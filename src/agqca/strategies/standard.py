"""Standard Grover search strategy (fixed optimal iterations, single deep run)."""

import time
from typing import Optional

from qiskit_aer import AerSimulator

from agqca.metrics.tracker import CircuitResourceTracker, ExecutionRecord
from agqca.noise.models import build_depolarizing_noise_model
from agqca.oracles.grover import build_grover_circuit, optimal_grover_iterations
from agqca.oracles.mode_a import MarkedStateOracle
from agqca.strategies.base import BaseStrategy, SearchContext


class StandardGroverStrategy(BaseStrategy):
    """Standard Grover algorithm with fixed optimal iterations k_ideal."""

    @property
    def name(self) -> str:
        return "Standard Grover"

    def run(self, context: SearchContext) -> ExecutionRecord:
        start_time = time.time()
        k_ideal = optimal_grover_iterations(context.key_size, num_marked=1)

        oracle = MarkedStateOracle(context.key_size, [context.target_key])
        qc = build_grover_circuit(oracle, iterations=k_ideal, measure=True)

        # Track circuit properties
        circuit_stats = CircuitResourceTracker.analyze_circuit(qc)

        noise_model = (
            build_depolarizing_noise_model(context.noise_level)
            if context.noise_level > 1e-9
            else None
        )
        sim = AerSimulator(noise_model=noise_model)
        shots = min(context.shots_per_round, 1024)
        result = sim.run(qc, shots=shots, seed_simulator=context.seed).result()
        counts = result.get_counts()

        # Sort measured bitstrings by frequency
        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)

        found_key: Optional[int] = None
        is_verified = False
        verify_cost = 0

        # Classically verify measured candidates until found or exhausted
        for bitstr, _ in sorted_counts:
            candidate = int(bitstr, 2)
            verify_cost += 1
            if context.verify_fn(candidate):
                found_key = candidate
                is_verified = True
                break

        wall_time = time.time() - start_time
        total_oracle_calls = k_ideal * shots
        total_cost = float(total_oracle_calls + verify_cost)

        return ExecutionRecord(
            strategy_name=self.name,
            target_key=context.target_key,
            found_key=found_key,
            is_verified=is_verified,
            iterations=k_ideal,
            oracle_calls=total_oracle_calls,
            classical_filter_cost=0,
            classical_verify_cost=verify_cost,
            total_effective_cost=total_cost,
            circuit_depth=circuit_stats["depth"],
            qubits_total=circuit_stats["qubits"],
            two_qubit_gates=circuit_stats["two_qubit_gates"],
            total_gates=circuit_stats["total_gates"],
            shots=shots,
            noise_level=context.noise_level,
            wall_clock_time=wall_time,
            seed=context.seed,
            extra_metadata={
                "k_ideal": k_ideal,
                "unique_candidates_checked": verify_cost,
            },
        )
