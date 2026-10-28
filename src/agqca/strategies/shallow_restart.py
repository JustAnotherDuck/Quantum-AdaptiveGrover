"""Shallow-circuit restart strategy for depth-limited quantum processors."""

import random
import time
from typing import Optional

from qiskit_aer import AerSimulator

from agqca.metrics.tracker import CircuitResourceTracker, ExecutionRecord
from agqca.noise.models import build_depolarizing_noise_model
from agqca.oracles.grover import build_grover_circuit, optimal_grover_iterations
from agqca.oracles.mode_a import MarkedStateOracle
from agqca.strategies.base import BaseStrategy, SearchContext


class ShallowRestartStrategy(BaseStrategy):
    """Depth-capped shallow Grover with repeated fast classical restarts."""

    def __init__(self, k_shallow: Optional[int] = None) -> None:
        self.k_shallow_override = k_shallow

    @property
    def name(self) -> str:
        return "Shallow + Restart"

    def run(self, context: SearchContext) -> ExecutionRecord:
        start_time = time.time()
        rng = random.Random(context.seed)

        k_ideal = optimal_grover_iterations(context.key_size, num_marked=1)
        # Cap shallow iterations: either override or roughly 1/3 of k_ideal (at least 1)
        if self.k_shallow_override is not None:
            k_shallow = max(1, self.k_shallow_override)
        else:
            k_shallow = max(1, k_ideal // 3)

        oracle = MarkedStateOracle(context.key_size, [context.target_key])
        qc = build_grover_circuit(oracle, iterations=k_shallow, measure=True)
        circuit_stats = CircuitResourceTracker.analyze_circuit(qc)

        noise_model = (
            build_depolarizing_noise_model(context.noise_level)
            if context.noise_level > 1e-9
            else None
        )
        sim = AerSimulator(noise_model=noise_model)

        total_oracle_calls = 0
        total_iterations = 0
        verify_cost = 0
        restarts = 0
        found_key: Optional[int] = None
        is_verified = False

        # Run shallow circuit in single-shot or small-batch restarts
        shots_per_restart = 8
        while total_oracle_calls < context.max_total_oracle_calls:
            restarts += 1
            total_iterations += k_shallow
            total_oracle_calls += k_shallow * shots_per_restart

            counts = sim.run(
                qc,
                shots=shots_per_restart,
                seed_simulator=rng.randint(1, 1000000),
            ).result().get_counts()

            # Classically test measured candidates in this restart
            for bitstr in counts.keys():
                candidate = int(bitstr, 2)
                verify_cost += 1
                if context.verify_fn(candidate):
                    found_key = candidate
                    is_verified = True
                    break

            if is_verified:
                break

        wall_time = time.time() - start_time
        total_cost = float(total_oracle_calls + verify_cost)

        return ExecutionRecord(
            strategy_name=self.name,
            target_key=context.target_key,
            found_key=found_key,
            is_verified=is_verified,
            iterations=total_iterations,
            oracle_calls=total_oracle_calls,
            classical_filter_cost=0,
            classical_verify_cost=verify_cost,
            total_effective_cost=total_cost,
            circuit_depth=circuit_stats["depth"],
            qubits_total=circuit_stats["qubits"],
            two_qubit_gates=circuit_stats["two_qubit_gates"],
            total_gates=circuit_stats["total_gates"],
            shots=total_oracle_calls,
            noise_level=context.noise_level,
            wall_clock_time=wall_time,
            seed=context.seed,
            extra_metadata={
                "k_shallow": k_shallow,
                "restarts": restarts,
            },
        )
