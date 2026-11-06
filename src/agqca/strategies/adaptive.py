"""Adaptive Hybrid Controller Strategy (The Proposed Framework).

Integrates:
1. Classical candidate filtering with safety fallback
2. Online noise and fidelity estimation
3. Adaptive policy-driven strategy and iteration selection
4. Shallow-circuit restarts and multi-round Bayesian belief tracking
5. Honest total cost accounting across classical and quantum operations
"""

import random
import time
from typing import Any, Dict, List, Optional

from qiskit_aer import AerSimulator

from agqca.controller.estimator import OnlineFidelityEstimator
from agqca.controller.policy import (
    ActionType,
    ControllerPolicy,
    ControllerState,
    PolicyAction,
)
from agqca.controller.rule_policy import RuleBasedPolicy
from agqca.filtering.constraints import CandidateFilter, Constraint
from agqca.filtering.superposition import FilteredSpaceMapper
from agqca.metrics.tracker import CircuitResourceTracker, ExecutionRecord
from agqca.noise.models import build_depolarizing_noise_model
from agqca.oracles.grover import build_grover_circuit, optimal_grover_iterations
from agqca.oracles.mode_a import MarkedStateOracle
from agqca.strategies.base import BaseStrategy, SearchContext


class AdaptiveHybridStrategy(BaseStrategy):
    """The AdaptiveGrover-QCA proposed controller framework."""

    def __init__(
        self,
        policy: Optional[ControllerPolicy] = None,
        constraints: Optional[List[Constraint]] = None,
        # Ablation switches
        no_filtering: bool = False,
        no_adaptivity: bool = False,
        no_noise_awareness: bool = False,
        no_restart: bool = False,
    ) -> None:
        self.policy = policy or RuleBasedPolicy()
        self.constraints = constraints or []
        self.no_filtering = no_filtering
        self.no_adaptivity = no_adaptivity
        self.no_noise_awareness = no_noise_awareness
        self.no_restart = no_restart

    @property
    def name(self) -> str:
        ablations = []
        if self.no_filtering:
            ablations.append("no-filter")
        if self.no_adaptivity:
            ablations.append("no-adapt")
        if self.no_noise_awareness:
            ablations.append("no-noise-aware")
        if self.no_restart:
            ablations.append("no-restart")

        if ablations:
            return f"Adaptive Hybrid ({', '.join(ablations)})"
        return "Adaptive Hybrid (Proposed)"

    def run(self, context: SearchContext) -> ExecutionRecord:
        start_time = time.time()
        rng = random.Random(context.seed)

        # ----------------------------------------------------
        # Lever 1: Classical Candidate Filtering
        # ----------------------------------------------------
        classical_filter_cost = 0
        if not self.no_filtering and self.constraints:
            filter_engine = CandidateFilter(
                key_size=context.key_size,
                constraints=self.constraints,
                allow_fallback=True,
            )
            filter_res = filter_engine.filter_space(true_key=context.target_key)
            candidates = filter_res.candidates
            classical_filter_cost = filter_res.classical_cost
        else:
            candidates = list(range(1 << context.key_size))

        candidate_space_size = len(candidates)
        mapper = FilteredSpaceMapper(candidates)
        n_search_qubits = mapper.index_qubits

        # Locate target key in mapped candidate space
        try:
            target_idx = mapper.candidate_to_index(context.target_key)
        except KeyError:
            # Should never happen if fallback was safe
            candidates = list(range(1 << context.key_size))
            mapper = FilteredSpaceMapper(candidates)
            n_search_qubits = mapper.index_qubits
            target_idx = mapper.candidate_to_index(context.target_key)

        # ----------------------------------------------------
        # Lever 2: Noise & Fidelity Initialization
        # ----------------------------------------------------
        estimator = OnlineFidelityEstimator()
        if not self.no_noise_awareness and context.noise_level > 1e-9:
            est_fidelity = max(0.05, (1.0 - context.noise_level) ** (2 * n_search_qubits))
        else:
            est_fidelity = 1.0
        estimator.estimated_fidelity = est_fidelity

        oracle = MarkedStateOracle(n_search_qubits, [target_idx])
        noise_model = (
            build_depolarizing_noise_model(context.noise_level)
            if context.noise_level > 1e-9
            else None
        )
        sim = AerSimulator(noise_model=noise_model)

        total_oracle_calls = 0
        total_iterations = 0
        verify_cost = 0
        found_key: Optional[int] = None
        is_verified = False
        rounds_executed = 0
        decisions_log: List[Dict[str, Any]] = []
        last_stats = {
            "depth": 0,
            "qubits": n_search_qubits,
            "two_qubit_gates": 0,
            "total_gates": 0,
        }

        # ----------------------------------------------------
        # Levers 3 & 4: Adaptive Control Loop & Shallow Restarts
        # ----------------------------------------------------
        max_rounds = 1 if self.no_restart else 20

        while (
            rounds_executed < max_rounds
            and total_oracle_calls < context.max_total_oracle_calls
            and not is_verified
        ):
            rounds_executed += 1

            controller_state = ControllerState(
                key_size=n_search_qubits,
                candidate_space_size=candidate_space_size,
                noise_level=0.0 if self.no_noise_awareness else context.noise_level,
                current_round=rounds_executed,
                cumulative_oracle_calls=total_oracle_calls,
                cumulative_verify_cost=verify_cost,
                estimated_fidelity=estimator.estimated_fidelity,
                observed_success_rate=estimator.alpha / (estimator.alpha + estimator.beta),
                shots_per_round=context.shots_per_round,
            )

            # Policy decision
            if self.no_adaptivity:
                # Fixed standard Grover without adaptivity
                k_ideal = optimal_grover_iterations(n_search_qubits, num_marked=1)
                action = PolicyAction(
                    action_type=ActionType.RUN_QUANTUM,
                    iterations=k_ideal,
                    shots=context.shots_per_round,
                    strategy_name="Fixed Grover",
                    reason="Ablation: Adaptivity disabled.",
                )
            else:
                action = self.policy.decide(controller_state)

            if action.action_type == ActionType.TERMINATE:
                decisions_log.append(
                    {
                        "round": rounds_executed,
                        "strategy": "None",
                        "action": "TERMINATE",
                        "iterations": 0,
                        "shots": 0,
                        "measured_key": 0,
                        "oracle_calls": 0,
                        "success": False,
                        "noise_estimate": estimator.estimated_fidelity,
                        "reason": action.reason,
                    }
                )
                break

            k = max(1, action.iterations)
            shots = max(1, action.shots)

            total_iterations += k
            total_oracle_calls += k * shots

            # Build Grover circuit
            qc = build_grover_circuit(oracle, iterations=k, measure=True)
            last_stats = CircuitResourceTracker.analyze_circuit(qc)

            counts = (
                sim.run(
                    qc,
                    shots=shots,
                    seed_simulator=rng.randint(1, 10000000),
                )
                .result()
                .get_counts()
            )

            # Process measurement outcomes
            round_matches = 0
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            measured_bitstr = sorted_counts[0][0] if sorted_counts else "0"
            measured_idx = int(measured_bitstr, 2)
            round_measured_key = mapper.index_to_candidate(measured_idx)

            # Test measured candidate keys classically
            for bitstr, count in sorted_counts:
                idx = int(bitstr, 2)
                candidate_key = mapper.index_to_candidate(idx)
                verify_cost += 1
                if context.verify_fn(candidate_key):
                    found_key = candidate_key
                    is_verified = True
                    round_matches += count
                    break

            # Online Bayesian update
            estimator.update(
                successes=round_matches,
                trials=shots,
                k_iterations=k,
                num_qubits=n_search_qubits,
            )

            decisions_log.append(
                {
                    "round": rounds_executed,
                    "strategy": action.strategy_name,
                    "action": action.action_type.value,
                    "iterations": k,
                    "shots": shots,
                    "measured_key": round_measured_key,
                    "oracle_calls": k * shots,
                    "success": is_verified,
                    "noise_estimate": estimator.estimated_fidelity,
                    "reason": action.reason,
                }
            )

            if is_verified or self.no_restart:
                break

        wall_time = time.time() - start_time
        total_cost = float(classical_filter_cost + total_oracle_calls + verify_cost)
        per_attempt_success = bool(is_verified and rounds_executed == 1)

        return ExecutionRecord(
            strategy_name=self.name,
            target_key=context.target_key,
            found_key=found_key,
            is_verified=is_verified,
            iterations=total_iterations,
            oracle_calls=total_oracle_calls,
            classical_filter_cost=classical_filter_cost,
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
                "rounds": rounds_executed,
                "candidates_remaining": candidate_space_size,
                "decisions": decisions_log,
                "final_estimated_fidelity": estimator.estimated_fidelity,
                "per_attempt_success": per_attempt_success,
                "eventual_success": is_verified,
            },
        )
