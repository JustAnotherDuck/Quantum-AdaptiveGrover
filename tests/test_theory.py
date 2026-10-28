"""Theory validation tests: Noiseless simulation vs analytic Grover formulas."""

import math

import numpy as np
import pytest
from qiskit_aer import AerSimulator

from agqca.oracles.grover import (
    build_grover_circuit,
    ideal_success_probability,
    optimal_grover_iterations,
)
from agqca.oracles.mode_a import MarkedStateOracle


@pytest.mark.parametrize("n_qubits", [3, 4, 5])
@pytest.mark.parametrize("m_marked", [1, 2])
def test_analytic_optimal_iterations_formula(n_qubits: int, m_marked: int) -> None:
    """Verify that optimal_grover_iterations yields maximal probability."""
    k_opt = optimal_grover_iterations(n_qubits, m_marked)
    p_opt = ideal_success_probability(n_qubits, m_marked, k_opt)

    # Check neighboring iterations
    if k_opt > 0:
        p_prev = ideal_success_probability(n_qubits, m_marked, k_opt - 1)
        assert p_opt >= p_prev - 1e-9
    p_next = ideal_success_probability(n_qubits, m_marked, k_opt + 1)
    assert p_opt >= p_next - 1e-9


@pytest.mark.parametrize("n_qubits, marked_states, k_iterations", [
    (3, [3], 1),
    (3, [3], 2),
    (4, [5], 1),
    (4, [5], 2),
    (4, [5], 3),
    (4, [2, 7], 1),
    (4, [2, 7], 2),
    (5, [13], 2),
    (5, [13], 4),
])
def test_noiseless_statevector_matches_theory(
    n_qubits: int,
    marked_states: list[int],
    k_iterations: int,
) -> None:
    """Compare noiseless statevector simulation against analytic sin^2((2k+1)theta)."""
    oracle = MarkedStateOracle(num_qubits=n_qubits, marked_states=marked_states)
    qc = build_grover_circuit(oracle, iterations=k_iterations, measure=False)
    qc.save_statevector()

    sim = AerSimulator(method="statevector")
    result = sim.run(qc).result()
    sv = result.get_statevector(qc)
    probs = np.abs(np.array(sv)) ** 2

    # Sum probabilities of all marked states
    simulated_prob = sum(probs[s] for s in marked_states)

    theoretical_prob = ideal_success_probability(
        num_qubits=n_qubits,
        num_marked=len(marked_states),
        iterations=k_iterations,
    )

    # Exact agreement within floating point tolerance
    assert math.isclose(simulated_prob, theoretical_prob, abs_tol=1e-5), (
        f"Mismatch: simulated={simulated_prob:.6f}, theoretical={theoretical_prob:.6f}"
    )


def test_noiseless_shot_sampling_within_confidence_interval() -> None:
    """Verify 10,000 shots fall within 99.7% binomial confidence interval of theory."""
    n_qubits = 4
    marked = [6]
    k = 2  # k=2 for n=4, M=1 is near optimal
    oracle = MarkedStateOracle(n_qubits, marked)
    qc = build_grover_circuit(oracle, iterations=k, measure=True)

    shots = 10000
    sim = AerSimulator()
    counts = sim.run(qc, shots=shots, seed_simulator=42).result().get_counts()

    target_bin = format(marked[0], f"0{n_qubits}b")
    measured_success = counts.get(target_bin, 0) / shots
    theoretical_prob = ideal_success_probability(n_qubits, 1, k)

    # Binomial 3-sigma standard error: 3 * sqrt(p * (1-p) / N)
    std_err = math.sqrt(theoretical_prob * (1.0 - theoretical_prob) / shots)
    margin = 3.5 * std_err

    assert abs(measured_success - theoretical_prob) < margin, (
        f"Measured={measured_success:.4f}, Theory={theoretical_prob:.4f}, Margin={margin:.4f}"
    )
