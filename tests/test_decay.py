"""Tests for noise models, fake backends, and noisy decay model fitting."""

import numpy as np
from qiskit_aer import AerSimulator

from agqca.noise.decay_fit import (
    fit_decay_model,
    optimal_noisy_iterations,
    predict_noisy_success,
)
from agqca.noise.fake_backends import get_fake_backend_noise_model, get_fake_backend_properties
from agqca.noise.models import build_depolarizing_noise_model
from agqca.oracles.grover import build_grover_circuit, ideal_success_probability
from agqca.oracles.mode_a import MarkedStateOracle


def test_decay_model_at_fidelity_one_equals_ideal() -> None:
    """Verify p_noisy(k) at F=1.0 strictly matches analytic noiseless p_ideal(k)."""
    for n in [3, 4, 5]:
        for k in [1, 2, 3]:
            p_noisy = predict_noisy_success(n, 1, k, fidelity=1.0)
            p_ideal = ideal_success_probability(n, 1, k)
            assert np.isclose(p_noisy, p_ideal, atol=1e-7)


def test_fit_decay_model_synthetic() -> None:
    """Verify decay fitter accurately recovers a known synthetic fidelity parameter."""
    n = 4
    true_f = 0.85
    k_vals = list(range(1, 8))
    # Generate synthetic noisy points with slight noise
    probs = [predict_noisy_success(n, 1, k, true_f) for k in k_vals]

    res = fit_decay_model(k_vals, probs, num_qubits=n, num_marked=1)
    assert np.isclose(res.fidelity, true_f, atol=1e-3)
    assert res.r_squared > 0.99
    assert res.rmse < 1e-3


def test_noisy_simulation_success_decreases_with_noise() -> None:
    """Verify simulation success probability decreases as depolarizing gate noise increases."""
    n = 3
    marked = [3]
    k = 1  # 1 iteration is optimal for n=3, M=1
    oracle = MarkedStateOracle(n, marked)
    qc = build_grover_circuit(oracle, iterations=k, measure=True)

    target_bin = format(marked[0], f"0{n}b")
    shots = 5000

    rates = [0.00, 0.05, 0.15]
    measured_probs = []

    for err in rates:
        noise = build_depolarizing_noise_model(error_2q=err)
        sim = AerSimulator(noise_model=noise)
        counts = sim.run(qc, shots=shots, seed_simulator=100).result().get_counts()
        p = counts.get(target_bin, 0) / shots
        measured_probs.append(p)

    # At 0.00, success should be close to ideal ~0.78
    assert measured_probs[0] > 0.70
    # Higher noise levels must degrade success monotonically
    assert measured_probs[0] > measured_probs[1] > measured_probs[2]


def test_optimal_noisy_iterations_shifts_lower_under_noise() -> None:
    """Verify optimal k under heavy noise shifts to fewer iterations to minimize k / p(k)."""
    n = 6  # k_ideal = 6
    k_noisy_clean, cost_clean = optimal_noisy_iterations(n, 1, fidelity=0.99)
    k_noisy_degraded, cost_degraded = optimal_noisy_iterations(n, 1, fidelity=0.50)

    assert k_noisy_degraded <= k_noisy_clean
    assert cost_degraded > cost_clean


def test_fake_backend_noise_model_execution() -> None:
    """Verify FakeManilaV2 noise model loads and executes a small Grover circuit."""
    props = get_fake_backend_properties("FakeManilaV2")
    assert props["num_qubits"] == 5

    noise_model = get_fake_backend_noise_model("FakeManilaV2")
    oracle = MarkedStateOracle(num_qubits=3, marked_states=[2])
    qc = build_grover_circuit(oracle, iterations=1, measure=True)

    sim = AerSimulator(noise_model=noise_model)
    counts = sim.run(qc, shots=500, seed_simulator=42).result().get_counts()
    assert len(counts) > 0
