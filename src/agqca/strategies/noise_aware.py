"""Noise-aware optimal-iteration Grover search strategy."""

import time
from typing import Optional

from qiskit_aer import AerSimulator

from agqca.metrics.tracker import CircuitResourceTracker, ExecutionRecord
from agqca.noise.decay_fit import optimal_noisy_iterations
from agqca.noise.models import build_depolarizing_noise_model
from agqca.oracles.grover import build_grover_circuit
from agqca.oracles.mode_a import MarkedStateOracle
from agqca.strategies.base import BaseStrategy, SearchContext


class NoiseAwareGroverStrategy(BaseStrategy):
    """Grover strategy optimizing iterations k to minimize expected cost k / p_noisy(k)."""

    @property
    def name(self) -> str:
        return "Noise-Aware Grover"

    def run(self, context: SearchContext) -> ExecutionRecord:
        start_time = time.time()

        # Estimate effective fidelity from noise level
        # Physical heuristic: F ≈ (1 - error_2q)^N_2q_per_iter
        # For standard Mode A oracle, approx 6-10 two-qubit gates per iteration
        est_2q_gates = max(4, 2 * context.key_size)
        fidelity = max(0.05, (1.0 - context.noise_level) ** est_2q_gates)

        k_opt, expected_cost = optimal_noisy_iterations(
            num_qubits=context.key_size,
            num_marked=1,
            fidelity=fidelity,
        )

        oracle = MarkedStateOracle(context.key_size, [context.target_key])
        qc = build_grover_circuit(oracle, iterations=k_opt, measure=True)
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

        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)

        found_key: Optional[int] = None
        is_verified = False
        verify_cost = 0

        for bitstr, _ in sorted_counts:
            candidate = int(bitstr, 2)
            verify_cost += 1
            if context.verify_fn(candidate):
                found_key = candidate
                is_verified = True
                break

        wall_time = time.time() - start_time
        total_oracle_calls = k_opt * shots
        total_cost = float(total_oracle_calls + verify_cost)

        return ExecutionRecord(
            strategy_name=self.name,
            target_key=context.target_key,
            found_key=found_key,
            is_verified=is_verified,
            iterations=k_opt,
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
                "k_noise_aware": k_opt,
                "estimated_fidelity": fidelity,
                "expected_theoretical_cost": expected_cost,
            },
        )
