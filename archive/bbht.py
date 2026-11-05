"""Boyer-Brassard-Hoyer-Tapp (BBHT) exponential schedule Grover search."""

import math
import random
import time
from typing import Optional

from qiskit_aer import AerSimulator

from agqca.metrics.tracker import CircuitResourceTracker, ExecutionRecord
from agqca.noise.models import build_depolarizing_noise_model
from agqca.oracles.grover import build_grover_circuit
from agqca.oracles.mode_a import MarkedStateOracle
from agqca.strategies.base import BaseStrategy, SearchContext


class BBHTStrategy(BaseStrategy):
    """BBHT algorithm for quantum search with unknown marked item count M.

    Iterates through geometrically increasing iteration bounds m, picking k in [0, m-1].
    """

    @property
    def name(self) -> str:
        return "BBHT (Exponential Schedule)"

    def run(self, context: SearchContext) -> ExecutionRecord:
        start_time = time.time()
        rng = random.Random(context.seed)

        n = context.key_size
        n_space = 1 << n
        max_m = math.sqrt(n_space)
        lam = 6.0 / 5.0  # Standard BBHT multiplier lambda = 1.2

        oracle = MarkedStateOracle(n, [context.target_key])
        noise_model = (
            build_depolarizing_noise_model(context.noise_level)
            if context.noise_level > 1e-9
            else None
        )
        sim = AerSimulator(noise_model=noise_model)

        m = 1.0
        total_oracle_calls = 0
        total_iterations = 0
        verify_cost = 0
        found_key: Optional[int] = None
        is_verified = False
        last_stats = {"depth": 0, "qubits": n, "two_qubit_gates": 0, "total_gates": 0}

        round_num = 0
        while total_oracle_calls < context.max_total_oracle_calls:
            round_num += 1
            # Choose integer k uniformly at random from [0, floor(m)]
            k = rng.randint(0, max(0, int(m)))
            total_iterations += k

            # Build and run circuit with 1 shot (or small shot batch)
            shots = 1
            total_oracle_calls += k * shots

            if k > 0:
                qc = build_grover_circuit(oracle, iterations=k, measure=True)
                last_stats = CircuitResourceTracker.analyze_circuit(qc)
                counts = sim.run(qc, shots=shots, seed_simulator=rng.randint(1, 100000)).result().get_counts()
                measured_str = list(counts.keys())[0]
                candidate = int(measured_str, 2)
            else:
                # k=0 is random guessing
                candidate = rng.randint(0, n_space - 1)

            verify_cost += 1
            if context.verify_fn(candidate):
                found_key = candidate
                is_verified = True
                break

            # Increase bound m geometrically up to sqrt(N)
            m = min(lam * m, max_m)

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
            circuit_depth=last_stats["depth"],
            qubits_total=last_stats["qubits"],
            two_qubit_gates=last_stats["two_qubit_gates"],
            total_gates=last_stats["total_gates"],
            shots=total_oracle_calls,
            noise_level=context.noise_level,
            wall_clock_time=wall_time,
            seed=context.seed,
            extra_metadata={
                "rounds": round_num,
                "final_m": m,
            },
        )
