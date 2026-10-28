"""Physical and parameterized noise models for noisy quantum simulation."""

from typing import List, Optional

from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    depolarizing_error,
    thermal_relaxation_error,
)

# Standard error rates specified in research protocol
STANDARD_NOISE_LEVELS = [0.00, 0.02, 0.05, 0.10, 0.15, 0.20]


def build_depolarizing_noise_model(
    error_2q: float,
    error_1q: Optional[float] = None,
    readout_error: float = 0.0,
    basis_1q: Optional[List[str]] = None,
    basis_2q: Optional[List[str]] = None,
) -> NoiseModel:
    """Build a parameterized depolarizing noise model.

    Convention:
    - 2-qubit gate error is error_2q.
    - 1-qubit gate error defaults to error_2q / 10 (superconducting ratio).
    - Readout error is a symmetric bit-flip channel with probability readout_error.

    Args:
        error_2q: Depolarizing probability for 2-qubit gates (0.0 to 1.0).
        error_1q: Depolarizing probability for 1-qubit gates (defaults to error_2q / 10).
        readout_error: Probability of classical measurement bit-flip.
        basis_1q: 1-qubit gate names to apply noise to (default: ['u', 'u1', 'u2', 'u3', 'h', 'x', 'sx', 'rz']).
        basis_2q: 2-qubit gate names to apply noise to (default: ['cx', 'cz', 'swap', 'ecr']).

    Returns:
        Qiskit Aer NoiseModel instance.
    """
    noise_model = NoiseModel()

    if error_1q is None:
        error_1q = error_2q / 10.0

    if basis_1q is None:
        basis_1q = ["u", "u1", "u2", "u3", "h", "x", "sx", "rz"]
    if basis_2q is None:
        basis_2q = ["cx", "cz", "swap", "ecr"]

    # 1-Qubit depolarizing error
    if error_1q > 1e-9:
        err_1q = depolarizing_error(min(error_1q, 0.75), 1)
        noise_model.add_all_qubit_quantum_error(err_1q, basis_1q)

    # 2-Qubit depolarizing error
    if error_2q > 1e-9:
        err_2q = depolarizing_error(min(error_2q, 0.75), 2)
        noise_model.add_all_qubit_quantum_error(err_2q, basis_2q)

    # Readout error
    if readout_error > 1e-9:
        p01 = readout_error
        p10 = readout_error
        ro_matrix = [[1.0 - p01, p01], [p10, 1.0 - p10]]
        ro_err = ReadoutError(ro_matrix)
        noise_model.add_all_qubit_readout_error(ro_err)

    return noise_model


def build_thermal_noise_model(
    t1: float = 50e-6,
    t2: float = 70e-6,
    time_1q: float = 35e-9,
    time_2q: float = 300e-9,
    error_2q: float = 0.01,
) -> NoiseModel:
    """Build a thermal relaxation noise model (T1/T2 decoherence) combined with gate errors.

    Args:
        t1: Longitudinal relaxation time in seconds.
        t2: Transverse dephasing time in seconds (T2 <= 2 * T1).
        time_1q: Duration of 1-qubit gates in seconds.
        time_2q: Duration of 2-qubit gates in seconds.
        error_2q: Residual depolarizing error for 2-qubit gates.

    Returns:
        Qiskit Aer NoiseModel with relaxation errors.
    """
    noise_model = NoiseModel()
    t2 = min(t2, 2.0 * t1)

    therm_1q = thermal_relaxation_error(t1, t2, time_1q)
    noise_model.add_all_qubit_quantum_error(therm_1q, ["u", "x", "sx", "h"])

    therm_2q = thermal_relaxation_error(t1, t2, time_2q).expand(
        thermal_relaxation_error(t1, t2, time_2q)
    )
    if error_2q > 1e-9:
        dep_2q = depolarizing_error(error_2q, 2)
        therm_2q = therm_2q.compose(dep_2q)

    noise_model.add_all_qubit_quantum_error(therm_2q, ["cx", "cz"])
    return noise_model
