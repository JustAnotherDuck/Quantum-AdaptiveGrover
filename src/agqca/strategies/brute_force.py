"""Classical brute-force baseline strategy."""

import random
import time
from typing import List, Optional

from agqca.metrics.tracker import ExecutionRecord
from agqca.strategies.base import BaseStrategy, SearchContext


class ClassicalBruteForceStrategy(BaseStrategy):
    """Classical exhaustive search baseline, supporting both unfiltered and filtered spaces."""

    def __init__(
        self,
        candidates: Optional[List[int]] = None,
        classical_filter_cost: int = 0,
        strategy_label: Optional[str] = None,
    ) -> None:
        self.candidates = candidates
        self.filter_cost = classical_filter_cost
        self._label = strategy_label

    @property
    def name(self) -> str:
        if self._label:
            return self._label
        if self.candidates is not None:
            return "Classical Brute Force (Filtered)"
        return "Classical Brute Force"

    def run(self, context: SearchContext) -> ExecutionRecord:
        start_time = time.time()
        rng = random.Random(context.seed)

        if self.candidates is not None:
            keys = list(self.candidates)
            total_keys = len(keys)
        else:
            total_keys = 1 << context.key_size
            keys = list(range(total_keys))
        rng.shuffle(keys)

        trials = 0
        found_key: Optional[int] = None
        is_verified = False

        for k in keys:
            trials += 1
            if context.verify_fn(k):
                found_key = k
                is_verified = True
                break
            if trials >= context.max_total_oracle_calls:
                break

        wall_time = time.time() - start_time

        return ExecutionRecord(
            strategy_name=self.name,
            target_key=context.target_key,
            found_key=found_key,
            is_verified=is_verified,
            iterations=0,
            oracle_calls=0,
            classical_filter_cost=self.filter_cost,
            classical_verify_cost=trials,
            total_effective_cost=float(self.filter_cost + trials),
            circuit_depth=0,
            qubits_total=0,
            two_qubit_gates=0,
            total_gates=0,
            shots=0,
            noise_level=context.noise_level,
            wall_clock_time=wall_time,
            seed=context.seed,
            extra_metadata={
                "search_space_N": total_keys,
                "expected_trials": total_keys / 2.0,
                "worst_trials": total_keys,
            },
        )
