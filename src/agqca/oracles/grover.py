"""Grover circuit construction, diffuser synthesis, and analytic theory formulas."""

import math

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from agqca.oracles.base import Oracle


def construct_diffuser(num_qubits: int) -> QuantumCircuit:
    """Construct standard Grover inversion-about-the-average diffuser: 2|s><s| - I."""
    qc = QuantumCircuit(num_qubits, name="Diffuser")

    # 1. Apply H gates to all qubits
    qc.h(range(num_qubits))

    # 2. Apply X gates to all qubits
    qc.x(range(num_qubits))

    # 3. Apply Multi-controlled Z gate
    if num_qubits == 1:
        qc.z(0)
    elif num_qubits == 2:
        qc.cz(0, 1)
    else:
        target = num_qubits - 1
        controls = list(range(num_qubits - 1))
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)

    # 4. Uncompute X gates
    qc.x(range(num_qubits))

    # 5. Uncompute H gates
    qc.h(range(num_qubits))

    return qc


def ideal_grover_angle(num_qubits: int, num_marked: int) -> float:
    """Calculate the rotation angle theta = arcsin(sqrt(M / N))."""
    n_space = 1 << num_qubits
    if num_marked <= 0:
        return 0.0
    if num_marked >= n_space:
        return math.pi / 2
    return math.asin(math.sqrt(num_marked / n_space))


def ideal_success_probability(num_qubits: int, num_marked: int, iterations: int) -> float:
    """Calculate the theoretical noiseless success probability: sin^2((2k+1)theta)."""
    theta = ideal_grover_angle(num_qubits, num_marked)
    return math.sin((2 * iterations + 1) * theta) ** 2


def optimal_grover_iterations(num_qubits: int, num_marked: int = 1) -> int:
    """Calculate optimal integer iteration count: round(pi / (4 * theta) - 0.5)."""
    if num_marked <= 0:
        return 0
    theta = ideal_grover_angle(num_qubits, num_marked)
    if theta == 0.0:
        return 0
    k_float = (math.pi / (4 * theta)) - 0.5
    return max(0, round(k_float))


def build_grover_circuit(
    oracle: Oracle,
    iterations: int,
    measure: bool = True,
) -> QuantumCircuit:
    """Build a complete Grover search circuit with given oracle and iteration count."""
    n_key = oracle.num_key_qubits
    n_ancilla = oracle.num_ancilla_qubits

    key_reg = QuantumRegister(n_key, name="key")
    regs = [key_reg]

    if n_ancilla > 0:
        ancilla_reg = QuantumRegister(n_ancilla, name="ancilla")
        regs.append(ancilla_reg)
    else:
        ancilla_reg = None

    if measure:
        creg = ClassicalRegister(n_key, name="c_key")
        qc = QuantumCircuit(*regs, creg, name=f"Grover_k{iterations}")
    else:
        qc = QuantumCircuit(*regs, name=f"Grover_k{iterations}")

    # State preparation: Uniform superposition over key register
    qc.h(key_reg)

    oracle_circ = oracle.construct_circuit()
    diffuser_circ = construct_diffuser(n_key)

    # Grover iteration loop
    for _ in range(iterations):
        # Oracle invocation
        if n_ancilla > 0:
            qc.compose(oracle_circ, qubits=list(key_reg) + list(ancilla_reg), inplace=True)
        else:
            qc.compose(oracle_circ, qubits=list(key_reg), inplace=True)

        # Diffuser on key qubits
        qc.compose(diffuser_circ, qubits=list(key_reg), inplace=True)

    if measure:
        qc.measure(key_reg, creg)

    return qc
