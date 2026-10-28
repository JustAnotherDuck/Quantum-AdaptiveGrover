"""Constraint definitions and classical candidate filtering engine."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


class Constraint(ABC):
    """Abstract base class for cryptographic key constraints."""

    @abstractmethod
    def is_satisfied(self, candidate: int) -> bool:
        """Check if a candidate key satisfies the constraint."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the constraint."""
        pass


class PrefixConstraint(Constraint):
    """Enforces that the highest prefix_bits of the key match prefix_val."""

    def __init__(self, key_size: int, prefix_bits: int, prefix_val: int) -> None:
        self.key_size = key_size
        self.prefix_bits = prefix_bits
        self.prefix_val = prefix_val & ((1 << prefix_bits) - 1)
        self.shift = key_size - prefix_bits

    def is_satisfied(self, candidate: int) -> bool:
        return ((candidate >> self.shift) & ((1 << self.prefix_bits) - 1)) == self.prefix_val

    @property
    def description(self) -> str:
        return f"Prefix({self.prefix_bits}b={self.prefix_val:#x})"


class SuffixConstraint(Constraint):
    """Enforces that the lowest suffix_bits of the key match suffix_val."""

    def __init__(self, suffix_bits: int, suffix_val: int) -> None:
        self.suffix_bits = suffix_bits
        self.suffix_val = suffix_val & ((1 << suffix_bits) - 1)
        self.mask = (1 << suffix_bits) - 1

    def is_satisfied(self, candidate: int) -> bool:
        return (candidate & self.mask) == self.suffix_val

    @property
    def description(self) -> str:
        return f"Suffix({self.suffix_bits}b={self.suffix_val:#x})"


class ParityConstraint(Constraint):
    """Enforces that the popcount (Hamming weight) of the key has specified parity."""

    def __init__(self, even_parity: bool = True) -> None:
        self.even_parity = even_parity

    def is_satisfied(self, candidate: int) -> bool:
        parity = bin(candidate).count("1") % 2
        return (parity == 0) if self.even_parity else (parity == 1)

    @property
    def description(self) -> str:
        return f"Parity({'even' if self.even_parity else 'odd'})"


class DictionaryConstraint(Constraint):
    """Enforces that the key belongs to a known dictionary or weak-key set."""

    def __init__(self, allowed_keys: Iterable[int]) -> None:
        self.allowed_set = set(allowed_keys)

    def is_satisfied(self, candidate: int) -> bool:
        return candidate in self.allowed_set

    @property
    def description(self) -> str:
        return f"Dictionary(size={len(self.allowed_set)})"


@dataclass
class FilteringResult:
    """Output produced by classical candidate filtering."""

    original_size: int
    reduced_size: int
    reduction_ratio: float
    candidates: List[int]
    classical_cost: int
    is_safe: bool
    fallback_used: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_size": self.original_size,
            "reduced_size": self.reduced_size,
            "reduction_ratio": self.reduction_ratio,
            "classical_cost": self.classical_cost,
            "is_safe": self.is_safe,
            "fallback_used": self.fallback_used,
        }


class CandidateFilter:
    """Applies constraints to filter the search space with guaranteed safety verification."""

    def __init__(
        self,
        key_size: int,
        constraints: Optional[List[Constraint]] = None,
        allow_fallback: bool = True,
    ) -> None:
        self.key_size = key_size
        self.total_keys = 1 << key_size
        self.constraints = constraints or []
        self.allow_fallback = allow_fallback

    def filter_space(
        self,
        true_key: Optional[int] = None,
    ) -> FilteringResult:
        """Filter the key space under active constraints.

        Args:
            true_key: Ground truth key for safety checking. If filtering discards
                      the true key, safely fall back to full space if allow_fallback=True.

        Returns:
            FilteringResult containing filtered candidate keys and honest accounting.
        """
        cost = 0
        filtered: List[int] = []

        for candidate in range(self.total_keys):
            cost += 1  # Each candidate check costs 1 classical test
            satisfied = True
            for c in self.constraints:
                if not c.is_satisfied(candidate):
                    satisfied = False
                    break
            if satisfied:
                filtered.append(candidate)

        is_safe = True
        fallback_used = False

        if true_key is not None:
            if true_key not in filtered:
                is_safe = False
                if self.allow_fallback:
                    # Fallback safely to full unfiltered space
                    filtered = list(range(self.total_keys))
                    fallback_used = True

        reduction_ratio = (
            float(self.total_keys) / float(len(filtered)) if len(filtered) > 0 else 1.0
        )

        return FilteringResult(
            original_size=self.total_keys,
            reduced_size=len(filtered),
            reduction_ratio=reduction_ratio,
            candidates=filtered,
            classical_cost=cost,
            is_safe=is_safe,
            fallback_used=fallback_used,
        )
