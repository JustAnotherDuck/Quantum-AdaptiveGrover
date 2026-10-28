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
    raise ValueError(f"Unknown fake backend '{name}'. Available include FakeManilaV2, FakeSherbrooke.")


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
