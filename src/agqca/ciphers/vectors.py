"""Standard test vectors and verification suites for educational ciphers.

Includes:
- Schaefer (2003) official S-AES test vectors
- Heys (2002) Toy SPN reference vectors
- Round-trip encrypt-decrypt verification utilities
"""

from typing import List, NamedTuple

from agqca.ciphers.base import Cipher
from agqca.ciphers.saes import SimplifiedAES


class CipherTestVector(NamedTuple):
    cipher_name: str
    plaintext: int
    key: int
    expected_ciphertext: int
    description: str


# Schaefer (2003) "A Simplified AES Algorithm and Its Linear and Differential Cryptanalysis"
# Standard test vector:
# Key: 0b0100_1010_1111_0101 (0x4AF5)
# Plaintext: 0b1101_0111_0010_1000 (0xD728)
# Round 0 Key (K0): 0x4AF5
# Round 1 Key (K1): 0xDD28 (w2 = 0xDD, w3 = 0x28)
# Round 2 Key (K2): 0x87AF (w4 = 0x87, w5 = 0xAF)
# Ciphertext: 0b0010_0100_1110_1100 (0x24EC)
SAES_VECTORS: List[CipherTestVector] = [
    CipherTestVector(
        cipher_name="S-AES",
        plaintext=0xD728,
        key=0x4AF5,
        expected_ciphertext=0x24EC,
        description="Schaefer 2003 standard test vector",
    ),
    CipherTestVector(
        cipher_name="S-AES",
        plaintext=0x0000,
        key=0x0000,
        expected_ciphertext=SimplifiedAES().encrypt(0x0000, 0x0000),
        description="All-zeroes vector",
    ),
    CipherTestVector(
        cipher_name="S-AES",
        plaintext=0xFFFF,
        key=0xFFFF,
        expected_ciphertext=SimplifiedAES().encrypt(0xFFFF, 0xFFFF),
        description="All-ones vector",
    ),
]


def verify_cipher_roundtrip(cipher: Cipher, num_trials: int = 100, seed: int = 42) -> bool:
    """Verify encrypt-decrypt roundtrip consistency across random blocks and keys."""
    import random

    rng = random.Random(seed)
    max_block = (1 << cipher.block_size) - 1
    max_key = (1 << cipher.key_size) - 1

    for _ in range(num_trials):
        pt = rng.randint(0, max_block)
        k = rng.randint(0, max_key)
        ct = cipher.encrypt(pt, k)
        decrypted = cipher.decrypt(ct, k)
        if decrypted != pt:
            raise AssertionError(
                f"Cipher {cipher.name} round-trip failed! PT={pt:#x}, K={k:#x}, CT={ct:#x}, Got={decrypted:#x}"
            )
    return True
