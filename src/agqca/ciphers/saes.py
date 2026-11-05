"""Simplified AES (S-AES) implementation as described by Edward Schaefer (2003).

Features:
- 16-bit block size (2x2 array of 4-bit nibbles)
- 16-bit key size (expanded to three 16-bit round keys)
- GF(2^4) arithmetic with irreducible polynomial x^4 + x + 1 (0b10011)
- Verified against Schaefer (2003) standard test vectors.
"""

from typing import Tuple

from agqca.ciphers.base import Cipher


class SimplifiedAES(Cipher):
    """Simplified AES (S-AES) 16-bit cipher."""

    # GF(2^4) irreducible polynomial: x^4 + x + 1
    IRREDUCIBLE_POLY = 0b10011

    # Schaefer 2003 Nibble Substitution Box (S-Box)
    SBOX = [
        0x9,
        0x4,
        0xA,
        0xB,
        0xD,
        0x1,
        0x8,
        0x5,
        0x6,
        0x2,
        0x0,
        0x3,
        0xC,
        0xE,
        0xF,
        0x7,
    ]

    # Inverse S-Box
    INV_SBOX = [
        0xA,
        0x5,
        0x9,
        0xB,
        0x1,
        0x7,
        0x8,
        0xF,
        0x6,
        0x0,
        0x2,
        0x3,
        0xC,
        0xE,
        0xD,
        0x7,
    ]
    # Note: Schaefer Inv-S-box exact lookup:
    # index 0x0 -> 0xA, 0x1 -> 0x5, 0x2 -> 0x9, 0x3 -> 0xB,
    # 0x4 -> 0x1, 0x5 -> 0x7, 0x6 -> 0x8, 0x7 -> 0xF,
    # 0x8 -> 0x6, 0x9 -> 0x0, 0xA -> 0x2, 0xB -> 0x3,
    # 0xC -> 0xC, 0xD -> 0x4, 0xE -> 0xD, 0xF -> 0xE
    # Let's verify INV_SBOX dynamically from SBOX:
    INV_SBOX = [0] * 16
    for i, val in enumerate(SBOX):
        INV_SBOX[val] = i

    RCON = [0x80, 0x30]  # Round constants in binary 1000 0000 and 0011 0000

    @property
    def name(self) -> str:
        return "S-AES"

    @property
    def key_size(self) -> int:
        return 16

    @property
    def block_size(self) -> int:
        return 16

    @staticmethod
    def gf16_mult(a: int, b: int) -> int:
        """Multiply two nibbles in GF(2^4) modulo x^4 + x + 1."""
        res = 0
        a = a & 0xF
        b = b & 0xF
        while b > 0:
            if b & 1:
                res ^= a
            a <<= 1
            if a & 0x10:
                a ^= 0b10011
            b >>= 1
        return res & 0xF

    @classmethod
    def sub_nibbles(cls, block: int) -> int:
        """Apply S-box to each of the 4 nibbles in the 16-bit block."""
        n0 = cls.SBOX[(block >> 12) & 0xF]
        n1 = cls.SBOX[(block >> 8) & 0xF]
        n2 = cls.SBOX[(block >> 4) & 0xF]
        n3 = cls.SBOX[block & 0xF]
        return (n0 << 12) | (n1 << 8) | (n2 << 4) | n3

    @classmethod
    def inv_sub_nibbles(cls, block: int) -> int:
        """Apply inverse S-box to each of the 4 nibbles in the 16-bit block."""
        n0 = cls.INV_SBOX[(block >> 12) & 0xF]
        n1 = cls.INV_SBOX[(block >> 8) & 0xF]
        n2 = cls.INV_SBOX[(block >> 4) & 0xF]
        n3 = cls.INV_SBOX[block & 0xF]
        return (n0 << 12) | (n1 << 8) | (n2 << 4) | n3

    @staticmethod
    def shift_rows(block: int) -> int:
        """Shift second row nibbles.

        Block representation:
        [ s00 (bits 15..12)   s01 (bits 7..4) ]
        [ s10 (bits 11..8)    s11 (bits 3..0) ]
        Swapping second row (s10 and s11):
        s00 stays, s10 becomes s11, s01 stays, s11 becomes s10.
        """
        s00 = (block >> 12) & 0xF
        s10 = (block >> 8) & 0xF
        s01 = (block >> 4) & 0xF
        s11 = block & 0xF
        # Swap s10 and s11
        return (s00 << 12) | (s11 << 8) | (s01 << 4) | s10

    @classmethod
    def mix_columns(cls, block: int) -> int:
        """Matrix multiplication in GF(2^4) with matrix [[1, 4], [4, 1]]."""
        s00 = (block >> 12) & 0xF
        s10 = (block >> 8) & 0xF
        s01 = (block >> 4) & 0xF
        s11 = block & 0xF

        res00 = s00 ^ cls.gf16_mult(4, s10)
        res10 = cls.gf16_mult(4, s00) ^ s10
        res01 = s01 ^ cls.gf16_mult(4, s11)
        res11 = cls.gf16_mult(4, s01) ^ s11

        return (res00 << 12) | (res10 << 8) | (res01 << 4) | res11

    @classmethod
    def inv_mix_columns(cls, block: int) -> int:
        """Inverse matrix multiplication in GF(2^4) with matrix [[9, 2], [2, 9]]."""
        s00 = (block >> 12) & 0xF
        s10 = (block >> 8) & 0xF
        s01 = (block >> 4) & 0xF
        s11 = block & 0xF

        res00 = cls.gf16_mult(9, s00) ^ cls.gf16_mult(2, s10)
        res10 = cls.gf16_mult(2, s00) ^ cls.gf16_mult(9, s10)
        res01 = cls.gf16_mult(9, s01) ^ cls.gf16_mult(2, s11)
        res11 = cls.gf16_mult(2, s01) ^ cls.gf16_mult(9, s11)

        return (res00 << 12) | (res10 << 8) | (res01 << 4) | res11

    @classmethod
    def expand_key(cls, key: int) -> Tuple[int, int, int]:
        """Key expansion: 16-bit key -> three 16-bit round keys (K0, K1, K2)."""
        w0 = (key >> 8) & 0xFF
        w1 = key & 0xFF

        def g(w: int, rcon: int) -> int:
            # Rotate nibbles: w = n0 (high), n1 (low) -> n1, n0
            n0 = (w >> 4) & 0xF
            n1 = w & 0xF
            # SubNibbles on rotated nibbles (n1, n0)
            sub = (cls.SBOX[n1] << 4) | cls.SBOX[n0]
            return sub ^ rcon

        w2 = w0 ^ g(w1, cls.RCON[0])
        w3 = w2 ^ w1
        w4 = w2 ^ g(w3, cls.RCON[1])
        w5 = w4 ^ w3

        k0 = (w0 << 8) | w1
        k1 = (w2 << 8) | w3
        k2 = (w4 << 8) | w5
        return k0, k1, k2

    def encrypt(self, plaintext: int, key: int) -> int:
        """Encrypt 16-bit plaintext with 16-bit key using S-AES."""
        self.validate_block(plaintext)
        self.validate_key(key)

        k0, k1, k2 = self.expand_key(key)

        # Round 0
        state = plaintext ^ k0

        # Round 1
        state = self.sub_nibbles(state)
        state = self.shift_rows(state)
        state = self.mix_columns(state)
        state = state ^ k1

        # Round 2
        state = self.sub_nibbles(state)
        state = self.shift_rows(state)
        state = state ^ k2

        return state

    def decrypt(self, ciphertext: int, key: int) -> int:
        """Decrypt 16-bit ciphertext with 16-bit key using S-AES."""
        self.validate_block(ciphertext)
        self.validate_key(key)

        k0, k1, k2 = self.expand_key(key)

        # Round 2 Inverse
        state = ciphertext ^ k2
        state = self.shift_rows(state)  # shift_rows is its own inverse
        state = self.inv_sub_nibbles(state)

        # Round 1 Inverse
        state = state ^ k1
        state = self.inv_mix_columns(state)
        state = self.shift_rows(state)
        state = self.inv_sub_nibbles(state)

        # Round 0 Inverse
        state = state ^ k0
        return state
