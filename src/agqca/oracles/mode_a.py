"""Mode A: Marked-State Phase Oracle.

Constructs a phase oracle directly from classically precomputed marked key states.
Provides fast quantum simulation for algorithm validation and statistical sweeps.

IMPORTANT: Gate counts from Mode A reflect simulation-only oracles, not the physical
circuit cost of evaluating the target cipher.
"""

from typing import Iterable, Set

from qiskit import QuantumCircuit

from agqca.oracles.base import Oracle


class MarkedStateOracle(Oracle):
    """Mode A Oracle: Flips the phase of specified marked key states."""

    def __init__(self, num_qubits: int, marked_states: Iterable[int]) -> None:
        if num_qubits < 1:
            raise ValueError("num_qubits must be at least 1")
        self._num_qubits = num_qubits
        self._marked_states: Set[int] = set(marked_states)
        for s in self._marked_states:
            if not (0 <= s < (1 << num_qubits)):
                raise ValueError(
                    f"Marked state {s} out of bounds for {num_qubits} qubits (max {(1 << num_qubits) - 1})"
                )

    @property
    def mode(self) -> str:
        return "Mode A (Simulation-Only Marked State)"

    @property
    def num_key_qubits(self) -> int:
        return self._num_qubits

    @property
    def num_ancilla_qubits(self) -> int:
        return 0

    @property
    def marked_states(self) -> Set[int]:
        return set(self._marked_states)

    def construct_circuit(self) -> QuantumCircuit:
        """Construct the phase oracle circuit."""
        qc = QuantumCircuit(self._num_qubits, name="Oracle_ModeA")

        for state in sorted(self._marked_states):
            # Apply X to qubits where the bit is 0
            for i in range(self._num_qubits):
                if not ((state >> i) & 1):
                    qc.x(i)

            if self._num_qubits == 1:
                qc.z(0)
            elif self._num_qubits == 2:
                qc.cz(0, 1)
            else:
                # Multi-controlled Z using H + MCX + H on the last qubit
                target = self._num_qubits - 1
                controls = list(range(self._num_qubits - 1))
                qc.h(target)
                qc.mcx(controls, target)
                qc.h(target)

            # Uncompute X gates
            for i in range(self._num_qubits):
                if not ((state >> i) & 1):
                    qc.x(i)

        return qc
