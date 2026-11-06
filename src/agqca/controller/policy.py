"""Policy interfaces and controller state representation for adaptive quantum search."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ActionType(str, Enum):
    RUN_QUANTUM = "RUN_QUANTUM"
    RESTART_SHALLOW = "RESTART_SHALLOW"
    SWITCH_STRATEGY = "SWITCH_STRATEGY"
    FALLBACK_CLASSICAL = "FALLBACK_CLASSICAL"
    TERMINATE = "TERMINATE"


@dataclass
class PolicyAction:
    """Action decision issued by the controller policy."""

    action_type: ActionType
    iterations: int
    shots: int
    strategy_name: str
    reason: str


@dataclass
class ControllerState:
    """Dynamic state observed by the adaptive controller across rounds."""

    key_size: int
    candidate_space_size: int
    noise_level: float
    current_round: int
    cumulative_oracle_calls: int
    cumulative_verify_cost: int
    estimated_fidelity: float
    observed_success_rate: float
    shots_per_round: int = 64
    history: List[Dict[str, Any]] = field(default_factory=list)


class ControllerPolicy(ABC):
    """Abstract policy interface for adaptive decision making."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Policy name."""
        pass

    @abstractmethod
    def decide(self, state: ControllerState) -> PolicyAction:
        """Issue an action decision based on current state observations."""
        pass
