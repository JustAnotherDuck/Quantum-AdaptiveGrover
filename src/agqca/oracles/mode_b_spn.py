"""Mode B: Reversible Quantum Circuit Cipher Oracle.

Implements a full compute-copy-uncompute reversible quantum circuit for symmetric
key recovery:
    |k>|P>|->  -->  |k>|E_k(P)>|->
               -->  (-1)^[E_k(P)==C] |k>|E_k(P)>|->
               -->  (-1)^[E_k(P)==C] |k>|P>|->

This mode captures ground-truth physical gate counts, transpiled depth, ancilla
overheads, and realistic noise propagation through cipher arithmetic.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import UnitaryGate

from agqca.ciphers.toyspn import ToySPN
from agqca.oracles.base import Oracle


class ReversibleSPNOracle(Oracle):
    """Mode B Reversible Oracle for Substitution-Permutation Network cipher.

    Supports configurable block/key sizes (e.g. 4, 8, 16 bits) and rounds.
    """

    def __init__(
        self,
        key_size: int,
        block_size: int,
        plaintext: int,
        target_ciphertext: int,
        rounds: int = 1,
    ) -> None:
        if key_size != block_size:
            raise ValueError(f"Key size ({key_size}) must equal block size ({block_size}) for SPN oracle")
        if key_size % 4 != 0:
            raise ValueError(f"Key size ({key_size}) must be a multiple of 4 (nibble-aligned)")

        self._key_size = key_size
        self._block_size = block_size
        self._plaintext = plaintext & ((1 << block_size) - 1)
        self._ciphertext = target_ciphertext & ((1 << block_size) - 1)
        self._rounds = rounds

        # Precompute 4-bit S-box unitary gate
        self._sbox_gate = self._build_sbox_gate()

    @property
    def mode(self) -> str:
        return "Mode B (Reversible Cipher Circuit)"

    @property
    def num_key_qubits(self) -> int:
        return self._key_size

    @property
    def num_ancilla_qubits(self) -> int:
        # State register (block_size) + 1 phase-kickback ancilla
        return self._block_size + 1

    @property
    def plaintext(self) -> int:
        return self._plaintext

    @property
    def target_ciphertext(self) -> int:
        return self._ciphertext

    @classmethod
    def _build_sbox_gate(cls) -> UnitaryGate:
        """Construct the 4-qubit unitary operator representing Heys 4-bit S-box."""
        sbox = ToySPN.SBOX
        mat = np.zeros((16, 16), dtype=complex)
        for x, y in enumerate(sbox):
            mat[y, x] = 1.0
        return UnitaryGate(mat, label="SBox")

    def _apply_forward_cipher(
        self,
        qc: QuantumCircuit,
        key_reg: QuantumRegister,
        state_reg: QuantumRegister,
    ) -> None:
        """Apply forward encryption E_k(state)."""
        num_nibbles = self._block_size // 4

        for r in range(self._rounds):
            # 1. Key Addition: CNOT from key register to state register
            for i in range(self._block_size):
                qc.cx(key_reg[i], state_reg[i])

            # 2. S-box Layer: apply 4-qubit unitary to each nibble
            for nib in range(num_nibbles):
                nibble_qubits = [state_reg[nib * 4 + q] for q in range(4)]
                qc.append(self._sbox_gate, nibble_qubits)

            # 3. Permutation Layer (only between rounds, if multi-round)
            if r < self._rounds - 1 and self._block_size == 16:
                # Bit permutation
                perm = ToySPN.PERMUTATION
                # In quantum circuits, wire permutation can be achieved via SWAPs
                # For 16 bits, swap wires to match Heys permutation:
                visited = [False] * 16
                for i in range(16):
                    if not visited[i]:
                        dest = perm[i]
                        if dest != i and not visited[dest]:
                            qc.swap(state_reg[i], state_reg[dest])
                            visited[i] = True
                            visited[dest] = True

        # Final Round Key Addition
        for i in range(self._block_size):
            qc.cx(key_reg[i], state_reg[i])

    def construct_circuit(self) -> QuantumCircuit:
        """Construct complete compute-copy-uncompute reversible oracle circuit."""
        key_reg = QuantumRegister(self._key_size, name="k")
        state_reg = QuantumRegister(self._block_size, name="state")
        flag_reg = QuantumRegister(1, name="flag")

        qc = QuantumCircuit(key_reg, state_reg, flag_reg, name="Oracle_ModeB")

        # Initialize flag qubit into |-> state for phase kickback
        qc.x(flag_reg[0])
        qc.h(flag_reg[0])

        # Initialize state register with known plaintext P
        for i in range(self._block_size):
            if (self._plaintext >> i) & 1:
                qc.x(state_reg[i])

        # Step 1: COMPUTE forward cipher E_k(P)
        self._apply_forward_cipher(qc, key_reg, state_reg)

        # Step 2: COMPARE with target ciphertext C
        # Apply X to state qubits where C has bit 0
        for i in range(self._block_size):
            if not ((self._ciphertext >> i) & 1):
                qc.x(state_reg[i])

        # Multi-controlled X onto flag qubit (phase kickback)
        qc.mcx(list(state_reg), flag_reg[0])

        # Uncompute comparison X gates
        for i in range(self._block_size):
            if not ((self._ciphertext >> i) & 1):
                qc.x(state_reg[i])

        # Step 3: UNCOMPUTE forward cipher E_k(P) in reverse
        forward_sub = QuantumCircuit(key_reg, state_reg, name="ForwardCipher")
        self._apply_forward_cipher(forward_sub, key_reg, state_reg)
        reverse_sub = forward_sub.inverse()
        qc.compose(reverse_sub, qubits=list(key_reg) + list(state_reg), inplace=True)

        # Uncompute plaintext initialization
        for i in range(self._block_size):
            if (self._plaintext >> i) & 1:
                qc.x(state_reg[i])

        # Return flag qubit from |-> to |0>
        qc.h(flag_reg[0])
        qc.x(flag_reg[0])

        return qc
