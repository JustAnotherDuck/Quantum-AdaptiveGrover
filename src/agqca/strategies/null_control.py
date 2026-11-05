"""Random-guessing null control strategy.

Establishes an empirical baseline: random classical sampling with verification,
subject to the exact same evaluation budget B_max. Confirms whether quantum
or hybrid strategies provide genuine amplification over blind random search.
"""

import random
import time
from typing import Optional

from agqca.metrics.tracker import ExecutionRecord
from agqca.strategies.base import BaseStrategy, SearchContext


class RandomGuessNullControlStrategy(BaseStrategy):
    """Null control baseline: uniform random guessing with verification."""

    @property
    def name(self) -> str:
        return "Random Guess (Null Control)"

    def run(self, context: SearchContext) -> ExecutionRecord:
        start_time = time.time()
        rng = random.Random(context.seed)
        space_size = 1 << context.key_size

        found_key: Optional[int] = None
        is_verified = False
        verify_cost = 0
        budget = context.max_total_oracle_calls

        # Sample uniformly with verification up to budget B_max
        while verify_cost < budget:
            guess = rng.randint(0, space_size - 1)
            verify_cost += 1
            if context.verify_fn(guess):
                found_key = guess
                is_verified = True
                break

        wall_time = time.time() - start_time
        total_cost = float(verify_cost)
        per_attempt_success = bool(is_verified and verify_cost == 1)

        return ExecutionRecord(
            strategy_name=self.name,
            target_key=context.target_key,
            found_key=found_key,
            is_verified=is_verified,
            iterations=0,
            oracle_calls=0,
            classical_filter_cost=0,
            classical_verify_cost=verify_cost,
            total_effective_cost=total_cost,
            circuit_depth=0,
            qubits_total=0,
            two_qubit_gates=0,
            total_gates=0,
            shots=verify_cost,
            noise_level=context.noise_level,
            wall_clock_time=wall_time,
            seed=context.seed,
            extra_metadata={
                "null_control": True,
                "evaluations": verify_cost,
                "budget_exhausted": not is_verified and verify_cost >= budget,
                "per_attempt_success": per_attempt_success,
                "eventual_success": is_verified,
            },
        )
