"""Integration with IBM Quantum fake backends for device-realistic noise simulation."""

from typing import Any, Dict

import qiskit_ibm_runtime.fake_provider as fp
from qiskit_aer.noise import NoiseModel


def get_fake_backend(name: str = "FakeManilaV2") -> Any:
    """Retrieve an IBM Quantum Fake Backend instance by name.

    Args:
        name: Name of backend class (e.g., 'FakeManilaV2', 'FakeSherbrooke').

    Returns:
        BackendV2 instance.
    """
    if hasattr(fp, name):
        backend_cls = getattr(fp, name)
        return backend_cls()
    raise ValueError(
        f"Unknown fake backend '{name}'. Available include FakeManilaV2, FakeSherbrooke."
    )


def get_fake_backend_noise_model(name: str = "FakeManilaV2") -> NoiseModel:
    """Extract Qiskit Aer NoiseModel from an IBM Fake Backend.

    Args:
        name: Name of the fake backend.

    Returns:
        NoiseModel calibrated from backend properties.
    """
    backend = get_fake_backend(name)
    return NoiseModel.from_backend(backend)


def get_fake_backend_properties(name: str = "FakeManilaV2") -> Dict[str, Any]:
    """Retrieve summarized physical properties for report generation."""
    backend = get_fake_backend(name)
    basis_gates = list(backend.operation_names)
    num_qubits = backend.num_qubits

    return {
        "name": name,
        "num_qubits": num_qubits,
        "basis_gates": basis_gates,
    }


def check_backend_capacity(backend_or_name: Any, required_qubits: int) -> bool:
    """Validate that the target backend has sufficient physical qubits.

    Args:
        backend_or_name: Backend instance or name string.
        required_qubits: Number of qubits required by the quantum circuit.

    Returns:
        True if capacity is sufficient.

    Raises:
        ValueError: If required_qubits exceeds physical capacity of the backend.
    """
    if isinstance(backend_or_name, str):
        backend = get_fake_backend(backend_or_name)
    else:
        backend = backend_or_name

    num_qubits = backend.num_qubits
    if required_qubits > num_qubits:
        raise ValueError(
            f"Circuit requires {required_qubits} qubits, but backend '{getattr(backend, 'name', str(backend))}' "
            f"only possesses {num_qubits} physical qubits."
        )
    return True
