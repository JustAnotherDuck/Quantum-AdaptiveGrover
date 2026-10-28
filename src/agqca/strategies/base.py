"""Abstract Strategy interface for quantum cryptanalysis search methods."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict

from agqca.metrics.tracker import ExecutionRecord


@dataclass
class SearchContext:
    """Execution context and constraints for a search run."""

    key_size: int
    target_key: int
    plaintext: int
    target_ciphertext: int
    verify_fn: Callable[[int], bool]
    noise_level: float = 0.0
    shots_per_round: int = 1024
    max_total_oracle_calls: int = 50000
    seed: int = 42
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseStrategy(ABC):
    """Abstract base class for key search strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the strategy."""
        pass

    @abstractmethod
    def run(self, context: SearchContext) -> ExecutionRecord:
        """Execute the search strategy under given context and return execution telemetry.

        Must always return a verified key or explicit failure (found_key=None, is_verified=False).
        Never return an unverified guess.
        """
        pass
