"""Quantum state preparation over filtered and arbitrary (non-power-of-2) candidate sets."""

import math
from typing import List

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation


class FilteredSpaceMapper:
    """Maps a list of N' candidate keys into a quantum register."""

    def __init__(self, candidates: List[int]) -> None:
        if not candidates:
            raise ValueError("Candidate set cannot be empty.")
        self.candidates = sorted(list(set(candidates)))
        self.num_candidates = len(self.candidates)
        # Required qubits to index the candidate set
        self.index_qubits = max(1, math.ceil(math.log2(self.num_candidates)))
        self.is_power_of_two = (1 << self.index_qubits) == self.num_candidates

    def candidate_to_index(self, key: int) -> int:
        """Find the index in the reduced space corresponding to a key."""
        try:
            return self.candidates.index(key)
        except ValueError:
            raise KeyError(f"Key {key:#x} is not in the candidate set.") from None

    def index_to_candidate(self, index: int) -> int:
        """Map measured index back to candidate key."""
        if 0 <= index < self.num_candidates:
            return self.candidates[index]
        # If measured outside valid range (in padded non-power-of-two case)
        return self.candidates[index % self.num_candidates]

    def construct_state_prep_circuit(self) -> QuantumCircuit:
        """Prepare exact uniform superposition over the N' candidate indices."""
        qc = QuantumCircuit(self.index_qubits, name="Prep_Nprime")

        if self.is_power_of_two:
            # Standard Hadamard transform across all index qubits
            qc.h(range(self.index_qubits))
        else:
            # Exact uniform superposition vector over N' states padded to 2^m
            n_padded = 1 << self.index_qubits
            amplitudes = np.zeros(n_padded, dtype=complex)
            norm = 1.0 / math.sqrt(self.num_candidates)
            for idx in range(self.num_candidates):
                amplitudes[idx] = norm
            state_prep = StatePreparation(amplitudes)
            qc.append(state_prep, range(self.index_qubits))

        return qc
