"""Abstract base class and metadata for quantum cryptanalysis oracles."""

from abc import ABC, abstractmethod
from typing import Dict

from qiskit import QuantumCircuit


class Oracle(ABC):
    """Abstract base class for Grover oracles."""

    @property
    @abstractmethod
    def mode(self) -> str:
        """Oracle mode: 'Mode A (Marked-State)' or 'Mode B (Reversible Cipher)'."""
        pass

    @property
    @abstractmethod
    def num_key_qubits(self) -> int:
        """Number of qubits representing the key search space."""
        pass

    @property
    @abstractmethod
    def num_ancilla_qubits(self) -> int:
        """Number of helper/ancilla qubits used by the oracle."""
        pass

    @property
    def total_qubits(self) -> int:
        """Total qubits required by the oracle."""
        return self.num_key_qubits + self.num_ancilla_qubits

    @abstractmethod
    def construct_circuit(self) -> QuantumCircuit:
        """Generate and return the quantum circuit implementing the oracle."""
        pass

    def circuit_stats(self) -> Dict[str, int]:
        """Compute gate counts and depth of the oracle circuit."""
        qc = self.construct_circuit()
        ops = dict(qc.count_ops())
        ops["total_gates"] = sum(ops.values())
        ops["depth"] = qc.depth()
        ops["qubits"] = qc.num_qubits
        return ops
