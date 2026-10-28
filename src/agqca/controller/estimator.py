"""Online Bayesian estimator for tracking success probability and effective fidelity."""

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class BayesianEstimate:
    """Beta-distribution posterior parameters for success probability."""

    alpha: float
    beta: float

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def variance(self) -> float:
        total = self.alpha + self.beta
        return (self.alpha * self.beta) / ((total**2) * (total + 1.0))

    @property
    def credible_interval_95(self) -> Tuple[float, float]:
        """Approximate 95% credible interval using normal approximation to beta."""
        m = self.mean
        s = math.sqrt(self.variance)
        return max(0.0, m - 1.96 * s), min(1.0, m + 1.96 * s)


class OnlineFidelityEstimator:
    """Maintains running Bayesian posterior on success and updates estimated fidelity."""

    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0) -> None:
        self.alpha = prior_alpha
        self.beta = prior_beta
        self.estimated_fidelity = 1.0

    def update(self, successes: int, trials: int, k_iterations: int, num_qubits: int) -> BayesianEstimate:
        """Update posterior belief after measuring 'trials' with 'successes'."""
        self.alpha += float(successes)
        self.beta += float(trials - successes)

        post_mean = self.alpha / (self.alpha + self.beta)

        # Invert simple decay model if k > 0 to update fidelity estimate
        if k_iterations > 0 and trials > 0:
            n_space = 1 << num_qubits
            from agqca.oracles.grover import ideal_success_probability

            p_ideal = ideal_success_probability(num_qubits, 1, k_iterations)
            # p_noisy = p_ideal * F^k + (1 - F^k)/N  =>  F^k = (p_noisy - 1/N) / (p_ideal - 1/N)
            denom = p_ideal - (1.0 / n_space)
            if abs(denom) > 1e-4:
                ratio = (post_mean - (1.0 / n_space)) / denom
                if 0.0 < ratio <= 1.0:
                    self.estimated_fidelity = ratio ** (1.0 / k_iterations)
                elif ratio <= 0.0:
                    self.estimated_fidelity = 0.1

        return BayesianEstimate(self.alpha, self.beta)
