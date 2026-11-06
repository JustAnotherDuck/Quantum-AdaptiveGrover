"""Rule-based decision policy for adaptive quantum cryptanalysis."""

from agqca.controller.policy import (
    ActionType,
    ControllerPolicy,
    ControllerState,
    PolicyAction,
)
from agqca.noise.decay_fit import optimal_noisy_iterations
from agqca.oracles.grover import optimal_grover_iterations


class RuleBasedPolicy(ControllerPolicy):
    """Heuristic rule-based policy selecting strategies based on noise thresholds and history."""

    @property
    def name(self) -> str:
        return "Rule-Based Adaptive Policy"

    def decide(self, state: ControllerState) -> PolicyAction:
        k_ideal = optimal_grover_iterations(state.key_size, num_marked=1)
        base_shots = max(1, state.shots_per_round)

        # Budget guard: if we've consumed too many calls without success, terminate
        if state.cumulative_oracle_calls > 30000:
            return PolicyAction(
                action_type=ActionType.TERMINATE,
                iterations=0,
                shots=0,
                strategy_name="None",
                reason="Exceeded cumulative oracle budget.",
            )

        # Severe noise regime (noise > 6%): deep circuits decohere rapidly, use shallow restart
        if state.noise_level > 0.06:
            k_shallow = max(1, k_ideal // 3)
            return PolicyAction(
                action_type=ActionType.RESTART_SHALLOW,
                iterations=k_shallow,
                shots=base_shots,
                strategy_name="Shallow + Restart",
                reason=f"High noise ({state.noise_level:.1%}) favors shallow restarts over deep Grover.",
            )

        # Mild noise regime (1% < noise <= 6%): use noise-aware iteration minimization
        if state.noise_level > 0.01:
            k_opt, _ = optimal_noisy_iterations(
                num_qubits=state.key_size,
                num_marked=1,
                fidelity=state.estimated_fidelity,
            )
            return PolicyAction(
                action_type=ActionType.RUN_QUANTUM,
                iterations=k_opt,
                shots=base_shots,
                strategy_name="Noise-Aware Grover",
                reason=f"Moderate noise ({state.noise_level:.1%}) optimized at k={k_opt} (vs k_ideal={k_ideal}).",
            )

        # Clean / near-ideal regime (noise <= 1%): standard Grover
        return PolicyAction(
            action_type=ActionType.RUN_QUANTUM,
            iterations=k_ideal,
            shots=base_shots,
            strategy_name="Standard Grover",
            reason=f"Low/zero noise ({state.noise_level:.1%}) justifies full optimal depth k={k_ideal}.",
        )
