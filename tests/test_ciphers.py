"""Unit and regression tests for educational and toy ciphers."""

import pytest

from agqca.ciphers.saes import SimplifiedAES
from agqca.ciphers.vectors import SAES_VECTORS, verify_cipher_roundtrip


def test_saes_schaefer_official_vector() -> None:
    """Test against the published Schaefer (2003) test vector."""
    cipher = SimplifiedAES()
    vec = SAES_VECTORS[0]
    ct = cipher.encrypt(vec.plaintext, vec.key)
    assert ct == vec.expected_ciphertext, f"Expected {vec.expected_ciphertext:#06x}, got {ct:#06x}"
    pt = cipher.decrypt(ct, vec.key)
    assert pt == vec.plaintext, f"Expected {vec.plaintext:#06x}, got {pt:#06x}"


def test_saes_round_keys() -> None:
    """Verify Schaefer (2003) round key expansion on official test key."""
    key = 0x4AF5
    k0, k1, k2 = SimplifiedAES.expand_key(key)
    assert k0 == 0x4AF5
    assert k1 == 0xDD28
    assert k2 == 0x87AF


def test_saes_roundtrip_random() -> None:
    """Verify S-AES encrypt-decrypt roundtrip over 100 pseudo-random inputs."""
    cipher = SimplifiedAES()
    assert verify_cipher_roundtrip(cipher, num_trials=100, seed=12345)


def test_saes_out_of_bounds() -> None:
    """Verify input validation on invalid block and key sizes."""
    cipher = SimplifiedAES()
    with pytest.raises(ValueError):
        cipher.encrypt(0x10000, 0x1234)
    with pytest.raises(ValueError):
        cipher.encrypt(0x1234, 0x10000)
    with pytest.raises(ValueError):
        cipher.decrypt(-1, 0x1234)


def test_saes_gf16_and_nibbles() -> None:
    """Verify GF(2^4) multiplication and nibble transformation primitives."""
    # Test GF(2^4) multiplication: 0x4 * 0x4 in x^4 + x + 1
    # 0b0100 * 0b0100 = 0b10000 = 0b10011 ^ 0b00011 = 0x3
    res = SimplifiedAES.gf16_mult(0x4, 0x4)
    assert res == 0x3
    # Test identity
    assert SimplifiedAES.gf16_mult(0x7, 0x1) == 0x7
    assert SimplifiedAES.gf16_mult(0x9, 0x0) == 0x0
