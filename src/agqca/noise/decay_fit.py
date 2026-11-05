"""Semi-analytic noisy Grover decay model and empirical fitting routines."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.optimize import curve_fit

from agqca.oracles.grover import ideal_success_probability


@dataclass
class DecayFitResult:
    """Results from fitting empirical noisy Grover success probabilities."""

    fidelity: float  # Effective per-iteration fidelity F in (0, 1]
    r_squared: float  # Coefficient of determination R^2
    rmse: float  # Root Mean Squared Error
    mae: float  # Mean Absolute Error
    num_samples: int
    residuals: List[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fidelity": self.fidelity,
            "r_squared": self.r_squared,
            "rmse": self.rmse,
            "mae": self.mae,
            "num_samples": self.num_samples,
        }


def predict_noisy_success(
    num_qubits: int,
    num_marked: int,
    iterations: int,
    fidelity: float,
) -> float:
    """Predict noisy Grover success probability using the semi-analytic decay model:

        p_noisy(k) = p_ideal(k) * F^k + (1 - F^k) / N

    Args:
        num_qubits: Key search register width (N = 2^n).
        num_marked: Number of marked states M.
        iterations: Number of Grover iterations k.
        fidelity: Effective fidelity per iteration F in (0.0, 1.0].

    Returns:
        Predicted success probability in [0.0, 1.0].
    """
    n_space = 1 << num_qubits
    p_ideal = ideal_success_probability(num_qubits, num_marked, iterations)
    f_k = fidelity**iterations
    p_noisy = p_ideal * f_k + (1.0 - f_k) / float(n_space)
    return float(np.clip(p_noisy, 0.0, 1.0))


def fit_decay_model(
    k_values: List[int],
    observed_probs: List[float],
    num_qubits: int,
    num_marked: int = 1,
) -> DecayFitResult:
    """Fit the effective fidelity parameter F from measured (k, p_k) data pairs.

    Args:
        k_values: List of iteration counts [k_1, k_2, ...].
        observed_probs: Measured success probabilities [p_1, p_2, ...].
        num_qubits: Search space qubits n.
        num_marked: Marked states M.

    Returns:
        DecayFitResult with estimated fidelity and goodness-of-fit metrics.
    """
    k_arr = np.array(k_values, dtype=float)
    obs_arr = np.array(observed_probs, dtype=float)

    def decay_func(k: np.ndarray, f: float) -> np.ndarray:
        preds = [predict_noisy_success(num_qubits, num_marked, int(ki), f) for ki in k]
        return np.array(preds)

    # Initial guess F = 0.90, bounded strictly between 0.01 and 1.0
    popt, _ = curve_fit(
        decay_func,
        k_arr,
        obs_arr,
        p0=[0.90],
        bounds=(0.01, 1.00),
    )
    fidelity = float(popt[0])

    preds = decay_func(k_arr, fidelity)
    residuals = obs_arr - preds
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((obs_arr - np.mean(obs_arr)) ** 2))
    r_squared = 1.0 - (ss_res / (ss_tot + 1e-12))
    rmse = float(np.sqrt(np.mean(residuals**2)))
    mae = float(np.mean(np.abs(residuals)))

    return DecayFitResult(
        fidelity=fidelity,
        r_squared=r_squared,
        rmse=rmse,
        mae=mae,
        num_samples=len(k_values),
        residuals=residuals.tolist(),
    )


def optimal_noisy_iterations(
    num_qubits: int,
    num_marked: int,
    fidelity: float,
    max_k: Optional[int] = None,
) -> Tuple[int, float]:
    """Find the iteration count k that minimizes expected cost: k / p_noisy(k).

    Args:
        num_qubits: Search space qubits n.
        num_marked: Marked items M.
        fidelity: Effective fidelity parameter F.
        max_k: Search bound for k (default: 2 * k_ideal).

    Returns:
        Tuple of (optimal_k, minimum_cost).
    """
    from agqca.oracles.grover import optimal_grover_iterations

    k_ideal = optimal_grover_iterations(num_qubits, num_marked)
    if max_k is None:
        max_k = max(2, int(2.5 * k_ideal))

    best_k = 1
    best_cost = float("inf")

    for k in range(1, max_k + 1):
        p_k = predict_noisy_success(num_qubits, num_marked, k, fidelity)
        if p_k > 1e-6:
            cost = k / p_k
            if cost < best_cost:
                best_cost = cost
                best_k = k

    return best_k, best_cost


@dataclass
class HeldOutValidationResult:
    """Out-of-sample held-out validation report for semi-analytic decay model."""

    train_fidelity: float
    train_r_squared: float
    test_r_squared: float
    test_rmse: float
    test_mae: float
    max_test_error: float
    test_samples: int
    failure_regimes: List[str]
    residuals: List[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "train_fidelity": self.train_fidelity,
            "train_r_squared": self.train_r_squared,
            "test_r_squared": self.test_r_squared,
            "test_rmse": self.test_rmse,
            "test_mae": self.test_mae,
            "max_test_error": self.max_test_error,
            "test_samples": self.test_samples,
            "failure_regimes": self.failure_regimes,
        }


def validate_decay_model_held_out(
    train_k: List[int],
    train_probs: List[float],
    test_k: List[int],
    test_probs: List[float],
    num_qubits: int,
    num_marked: int = 1,
) -> HeldOutValidationResult:
    """Validate fitted decay model on disjoint held-out test data.

    Evaluates R^2, RMSE, MAE, and diagnoses failure regimes where the
    semi-analytic model departs from full-density-matrix or Aer simulation.
    """
    train_fit = fit_decay_model(train_k, train_probs, num_qubits, num_marked)
    fitted_f = train_fit.fidelity

    test_preds = np.array(
        [predict_noisy_success(num_qubits, num_marked, k, fitted_f) for k in test_k]
    )
    test_obs = np.array(test_probs, dtype=float)

    residuals = test_obs - test_preds
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((test_obs - np.mean(test_obs)) ** 2))
    test_r2 = 1.0 - (ss_res / (ss_tot + 1e-12))
    test_rmse = float(np.sqrt(np.mean(residuals**2)))
    test_mae = float(np.mean(np.abs(residuals)))
    max_err = float(np.max(np.abs(residuals)))

    failure_regimes: List[str] = []
    # Diagnose regime 1: deep decoherence saturation
    n_space = 1 << num_qubits
    floor_p = 1.0 / float(n_space)
    if any(k > 3 * max(train_k) for k in test_k):
        failure_regimes.append(
            "Extrapolation to k >> train_k: phase drift deviates from scalar exponential decay"
        )
    if any(abs(obs - floor_p) < 0.02 and pred > 0.15 for obs, pred in zip(test_obs, test_preds, strict=False)):
        failure_regimes.append(
            "Catastrophic decoherence floor: observed signal completely depolarized to 1/N"
        )
    if test_rmse > 0.20:
        failure_regimes.append(
            "High noise regime: model underestimates multi-qubit correlated error propagation"
        )

    return HeldOutValidationResult(
        train_fidelity=fitted_f,
        train_r_squared=train_fit.r_squared,
        test_r_squared=test_r2,
        test_rmse=test_rmse,
        test_mae=test_mae,
        max_test_error=max_err,
        test_samples=len(test_k),
        failure_regimes=failure_regimes,
        residuals=residuals.tolist(),
    )
