"""Statistical rigor: Bootstrap confidence intervals, paired comparisons, effect sizes."""

from typing import Dict, List, Tuple

import numpy as np


def bootstrap_ci(
    data: List[float],
    num_bootstrap: int = 2000,
    confidence: float = 0.95,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Calculate sample mean and non-parametric bootstrap confidence interval.

    Args:
        data: List of numerical observations.
        num_bootstrap: Number of bootstrap resamples.
        confidence: Confidence level (default 0.95 for 95% CI).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (mean, lower_ci, upper_ci).
    """
    if not data:
        return 0.0, 0.0, 0.0

    arr = np.array(data, dtype=float)
    if len(arr) == 1:
        val = float(arr[0])
        return val, val, val

    rng = np.random.default_rng(seed)
    n = len(arr)
    boot_indices = rng.integers(0, n, size=(num_bootstrap, n))
    boot_means = np.mean(arr[boot_indices], axis=1)

    alpha = 1.0 - confidence
    lower = float(np.percentile(boot_means, 100.0 * (alpha / 2.0)))
    upper = float(np.percentile(boot_means, 100.0 * (1.0 - alpha / 2.0)))
    mean = float(np.mean(arr))

    return mean, lower, upper


def paired_cohens_d(x: List[float], y: List[float]) -> float:
    """Calculate Cohen's d effect size for paired samples (x - y)."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    diff = np.array(x) - np.array(y)
    std_diff = np.std(diff, ddof=1)
    if std_diff < 1e-12:
        return 0.0
    return float(np.mean(diff) / std_diff)


def compare_strategies(
    strategy_a_results: List[float],
    strategy_b_results: List[float],
    seed: int = 42,
) -> Dict[str, float]:
    """Paired statistical comparison between two strategies on identical seeds/instances."""
    mean_a, low_a, high_a = bootstrap_ci(strategy_a_results, seed=seed)
    mean_b, low_b, high_b = bootstrap_ci(strategy_b_results, seed=seed)
    d = paired_cohens_d(strategy_a_results, strategy_b_results)

    return {
        "mean_a": mean_a,
        "ci_low_a": low_a,
        "ci_high_a": high_a,
        "mean_b": mean_b,
        "ci_low_b": low_b,
        "ci_high_b": high_b,
        "mean_difference": mean_a - mean_b,
        "cohens_d": d,
    }
