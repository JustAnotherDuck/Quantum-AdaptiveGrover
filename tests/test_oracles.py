"""Tests for Mode A and Mode B quantum oracles and equivalence."""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from agqca.oracles.grover import build_grover_circuit, optimal_grover_iterations
from agqca.oracles.mode_a import MarkedStateOracle
from agqca.oracles.mode_b_spn import ReversibleSPNOracle


def test_mode_a_marked_state_inversion() -> None:
    """Verify Mode A applies exact -1 phase to marked states and +1 to unmarked states."""
    n = 3
    marked = [2, 5]
    oracle = MarkedStateOracle(num_qubits=n, marked_states=marked)
    circ = oracle.construct_circuit()

    sv_init = Statevector.from_label("0" * n)
    # Put all qubits into uniform superposition
    h_circ = QuantumCircuit(n)
    h_circ.h(range(n))
    sv = sv_init.evolve(h_circ)

    # Evolve through oracle
    sv_out = sv.evolve(circ)
    amps_in = sv.data
    amps_out = sv_out.data

    for state in range(1 << n):
        if state in marked:
            # Should have flipped sign: out = -in
            assert np.isclose(amps_out[state], -amps_in[state], atol=1e-7)
        else:
            # Should be unchanged: out = in
            assert np.isclose(amps_out[state], amps_in[state], atol=1e-7)


def test_mode_a_and_mode_b_statevector_equivalence() -> None:
    """Verify Mode A and Mode B produce identical statevectors on key register for 4-bit SPN."""
    key_size = 4
    block_size = 4
    true_key = 0x9
    plaintext = 0x3

    # For 1-round 4-bit SPN, compute target ciphertext:
    # Key addition: pt ^ key = 0x3 ^ 0x9 = 0xA
    # Sbox(0xA) = 0x6
    # Final key addition: 0x6 ^ 0x9 = 0xF
    sbox = [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8, 0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7]
    expected_ct = sbox[plaintext ^ true_key] ^ true_key

    mode_a = MarkedStateOracle(num_qubits=key_size, marked_states=[true_key])
    mode_b = ReversibleSPNOracle(
        key_size=key_size,
        block_size=block_size,
        plaintext=plaintext,
        target_ciphertext=expected_ct,
        rounds=1,
    )

    # Mode A circuit: H on key, then Mode A oracle
    qc_a = QuantumCircuit(key_size)
    qc_a.h(range(key_size))
    qc_a.compose(mode_a.construct_circuit(), inplace=True)
    sv_a = Statevector.from_instruction(qc_a)

    # Mode B circuit: H on key register, Mode B oracle (acts on key + state + flag)
    # Ancillae start in |0>, oracle computes and cleanly uncomputes
    k_reg = QuantumRegister(key_size, "k")
    s_reg = QuantumRegister(block_size, "s")
    f_reg = QuantumRegister(1, "f")
    qc_b = QuantumCircuit(k_reg, s_reg, f_reg)
    qc_b.h(k_reg)
    qc_b.compose(mode_b.construct_circuit(), inplace=True)
    sv_b = Statevector.from_instruction(qc_b)

    # In sv_b, state and flag qubits must end in |0>, so non-zero amplitudes occur only when ancillae = 0.
    # Check that key amplitudes match Mode A exactly:
    amps_a = sv_a.data
    # Total qubits in sv_b = 4 + 4 + 1 = 9
    # Basis state index in Qiskit: |flag, state, key> = key + (state << 4) + (flag << 8)
    for k in range(1 << key_size):
        expected_amp = amps_a[k]
        # In Mode B, the key is at the lowest 4 qubits, state and flag should be 0
        actual_amp = sv_b.data[k]
        assert np.isclose(actual_amp, expected_amp, atol=1e-5), (
            f"Key {k:#x}: Mode A amp={expected_amp}, Mode B amp={actual_amp}"
        )


def test_mode_b_grover_search_recovers_key() -> None:
    """Verify Grover search with Mode B oracle successfully recovers true 4-bit key."""
    key_size = 4
    block_size = 4
    true_key = 0x6
    plaintext = 0xB

    sbox = [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8, 0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7]
    expected_ct = sbox[plaintext ^ true_key] ^ true_key

    oracle = ReversibleSPNOracle(
        key_size=key_size,
        block_size=block_size,
        plaintext=plaintext,
        target_ciphertext=expected_ct,
        rounds=1,
    )

    k_opt = optimal_grover_iterations(key_size, 1)
    qc = build_grover_circuit(oracle, iterations=k_opt, measure=True)

    sim = AerSimulator()
    counts = sim.run(qc, shots=2000, seed_simulator=123).result().get_counts()

    # True key in binary:
    target_bin = format(true_key, f"0{key_size}b")
    prob_measured = counts.get(target_bin, 0) / 2000.0

    # With k_opt=3 for n=4, theoretical success is ~0.96
    assert prob_measured > 0.85, f"Recovery probability {prob_measured} too low for Mode B Grover"


def test_mode_b_circuit_stats() -> None:
    """Verify Mode B reports realistic gates and ancilla counts."""
    oracle = ReversibleSPNOracle(key_size=4, block_size=4, plaintext=0x1, target_ciphertext=0x2)
    stats = oracle.circuit_stats()
    assert stats["qubits"] == 9  # 4 key + 4 state + 1 flag
    assert stats["depth"] > 0
    assert stats["total_gates"] > 0
