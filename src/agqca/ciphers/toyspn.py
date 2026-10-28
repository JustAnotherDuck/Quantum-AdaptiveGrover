"""4-Round 16-bit Toy Substitution-Permutation Network (Toy SPN).

Based on Howard Heys (2002) "A Tutorial on Linear and Differential Cryptanalysis".
Features:
- 16-bit block size (4 nibbles)
- 16-bit key size
- 4 rounds of key mixing, non-linear S-box substitution, and bit permutation.
- Full round-trip invertibility and classical reference implementation.
"""

from typing import List

from agqca.ciphers.base import Cipher


class ToySPN(Cipher):
    """Classic 16-bit, 4-round Substitution-Permutation Network cipher."""

    # Heys (2002) standard 4-bit S-box
    SBOX = [
        0xE, 0x4, 0xD, 0x1,
        0x2, 0xF, 0xB, 0x8,
        0x3, 0xA, 0x6, 0xC,
        0x5, 0x9, 0x0, 0x7,
    ]

    # Invert S-box dynamically
    INV_SBOX = [0] * 16
    for i, val in enumerate(SBOX):
        INV_SBOX[val] = i

    # Heys 16-bit permutation: maps bit index i to P[i] (0 = MSB, 15 = LSB)
    # P(i): 0->0, 1->4, 2->8, 3->12, 4->1, 5->5, 6->9, 7->13,
    #       8->2, 9->6, 10->10, 11->14, 12->3, 13->7, 14->11, 15->15
    PERMUTATION = [
        0, 4, 8, 12,
        1, 5, 9, 13,
        2, 6, 10, 14,
        3, 7, 11, 15,
    ]

    # Inverse permutation
    INV_PERMUTATION = [0] * 16
    for i, val in enumerate(PERMUTATION):
        INV_PERMUTATION[val] = i

    @property
    def name(self) -> str:
        return "ToySPN"

    @property
    def key_size(self) -> int:
        return 16

    @property
    def block_size(self) -> int:
        return 16

    @staticmethod
    def _rol16(val: int, shift: int) -> int:
        """Circular left shift for 16-bit unsigned integer."""
        shift %= 16
        return ((val << shift) | (val >> (16 - shift))) & 0xFFFF

    @classmethod
    def expand_keys(cls, key: int) -> List[int]:
        """Derive five 16-bit round keys (K1, K2, K3, K4, K5) from a 16-bit master key."""
        return [
            cls._rol16(key, 0),
            cls._rol16(key, 3),
            cls._rol16(key, 7),
            cls._rol16(key, 11),
            cls._rol16(key, 14),
        ]

    @classmethod
    def sub_nibbles(cls, block: int) -> int:
        """Apply S-box to each 4-bit nibble."""
        n0 = cls.SBOX[(block >> 12) & 0xF]
        n1 = cls.SBOX[(block >> 8) & 0xF]
        n2 = cls.SBOX[(block >> 4) & 0xF]
        n3 = cls.SBOX[block & 0xF]
        return (n0 << 12) | (n1 << 8) | (n2 << 4) | n3

    @classmethod
    def inv_sub_nibbles(cls, block: int) -> int:
        """Apply inverse S-box to each 4-bit nibble."""
        n0 = cls.INV_SBOX[(block >> 12) & 0xF]
        n1 = cls.INV_SBOX[(block >> 8) & 0xF]
        n2 = cls.INV_SBOX[(block >> 4) & 0xF]
        n3 = cls.INV_SBOX[block & 0xF]
        return (n0 << 12) | (n1 << 8) | (n2 << 4) | n3

    @classmethod
    def permute(cls, block: int) -> int:
        """Apply bit-level permutation layer."""
        out = 0
        for src_bit, dst_bit in enumerate(cls.PERMUTATION):
            if (block >> (15 - src_bit)) & 1:
                out |= 1 << (15 - dst_bit)
        return out

    @classmethod
    def inv_permute(cls, block: int) -> int:
        """Apply inverse bit-level permutation layer."""
        out = 0
        for src_bit, dst_bit in enumerate(cls.INV_PERMUTATION):
            if (block >> (15 - src_bit)) & 1:
                out |= 1 << (15 - dst_bit)
        return out

    def encrypt(self, plaintext: int, key: int) -> int:
        """Encrypt 16-bit plaintext block under 16-bit key."""
        self.validate_block(plaintext)
        self.validate_key(key)

        round_keys = self.expand_keys(key)
        state = plaintext

        # Rounds 1 to 3: Key mixing, Substitution, Permutation
        for r in range(3):
            state ^= round_keys[r]
            state = self.sub_nibbles(state)
            state = self.permute(state)

        # Round 4: Key mixing, Substitution (no permutation), Final key mixing
        state ^= round_keys[3]
        state = self.sub_nibbles(state)
        state ^= round_keys[4]

        return state

    def decrypt(self, ciphertext: int, key: int) -> int:
        """Decrypt 16-bit ciphertext block under 16-bit key."""
        self.validate_block(ciphertext)
        self.validate_key(key)

        round_keys = self.expand_keys(key)
        state = ciphertext

        # Invert Round 4
        state ^= round_keys[4]
        state = self.inv_sub_nibbles(state)
        state ^= round_keys[3]

        # Invert Rounds 3 down to 1
        for r in reversed(range(3)):
            state = self.inv_permute(state)
            state = self.inv_sub_nibbles(state)
            state ^= round_keys[r]

        return state
