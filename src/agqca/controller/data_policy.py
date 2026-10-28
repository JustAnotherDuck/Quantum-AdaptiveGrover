"""Data-driven regression/surface lookup policy for adaptive control."""

from agqca.controller.policy import (
    ActionType,
    ControllerPolicy,
    ControllerState,
    PolicyAction,
)
from agqca.oracles.grover import optimal_grover_iterations


class DataDrivenPolicy(ControllerPolicy):
    """Data-driven policy using regression surface over noise, depth, and success rate."""

    @property
    def name(self) -> str:
        return "Data-Driven Regression Policy"

    def decide(self, state: ControllerState) -> PolicyAction:
        k_ideal = optimal_grover_iterations(state.key_size, num_marked=1)

        if state.cumulative_oracle_calls > 30000:
            return PolicyAction(
                action_type=ActionType.TERMINATE,
                iterations=0,
                shots=0,
                strategy_name="None",
                reason="Budget cap reached.",
            )

        # Regression surface model: optimal depth scale factor alpha(noise, n)
        # alpha in (0, 1] scales k_ideal down based on noise level
        # Fit from empirical calibration surface: alpha ≈ 1 / (1 + 15 * noise^1.2)
        scale_factor = 1.0 / (1.0 + 15.0 * (state.noise_level**1.2))
        k_target = max(1, int(round(k_ideal * scale_factor)))

        if state.noise_level >= 0.08:
            return PolicyAction(
                action_type=ActionType.RESTART_SHALLOW,
                iterations=k_target,
                shots=16,
                strategy_name="Shallow + Restart",
                reason=f"Surface indicates shallow regime (scale={scale_factor:.2f}, k={k_target}).",
            )
        else:
            return PolicyAction(
                action_type=ActionType.RUN_QUANTUM,
                iterations=k_target,
                shots=64,
                strategy_name="Noise-Aware Grover",
                reason=f"Surface selected k={k_target} (scale={scale_factor:.2f}).",
            )
