"""Abstract base class and utilities for educational and toy ciphers."""

from abc import ABC, abstractmethod


class Cipher(ABC):
    """Abstract base class for symmetric ciphers used in quantum cryptanalysis experiments."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the cipher."""
        pass

    @property
    @abstractmethod
    def key_size(self) -> int:
        """Key length in bits."""
        pass

    @property
    @abstractmethod
    def block_size(self) -> int:
        """Plaintext and ciphertext block size in bits."""
        pass

    @abstractmethod
    def encrypt(self, plaintext: int, key: int) -> int:
        """Encrypt an integer plaintext block using an integer key.

        Args:
            plaintext: Block integer in [0, 2^block_size - 1].
            key: Key integer in [0, 2^key_size - 1].

        Returns:
            Ciphertext integer in [0, 2^block_size - 1].
        """
        pass

    @abstractmethod
    def decrypt(self, ciphertext: int, key: int) -> int:
        """Decrypt an integer ciphertext block using an integer key.

        Args:
            ciphertext: Block integer in [0, 2^block_size - 1].
            key: Key integer in [0, 2^key_size - 1].

        Returns:
            Plaintext integer in [0, 2^block_size - 1].
        """
        pass

    def validate_key(self, key: int) -> None:
        """Ensure key is within valid bit bounds."""
        if not (0 <= key < (1 << self.key_size)):
            raise ValueError(
                f"Key {key:#x} out of range for {self.key_size}-bit key space."
            )

    def validate_block(self, block: int) -> None:
        """Ensure block is within valid bit bounds."""
        if not (0 <= block < (1 << self.block_size)):
            raise ValueError(
                f"Block {block:#x} out of range for {self.block_size}-bit block space."
            )
