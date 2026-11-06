"""Pydantic schemas for the AdaptiveGrover-QCA REST API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SimulateRequest(BaseModel):
    strategy_name: str = Field(
        "Adaptive Hybrid (Proposed)", description="Search strategy to execute"
    )
    key_size: int = Field(4, ge=2, le=12, description="Key search register size in bits")
    target_key: Optional[int] = Field(
        None, description="Optional target key; randomly sampled if None"
    )
    noise_level: float = Field(
        0.02, ge=0.0, le=0.5, description="Two-qubit gate depolarizing error rate"
    )
    shots_per_round: int = Field(128, ge=1, le=1024, description="Measurement shots per round")
    max_total_oracle_calls: int = Field(
        15000, ge=100, le=50000, description="Total evaluation budget B_max"
    )
    seed: int = Field(42, description="RNG seed for reproducibility")
    prefix_bits: int = Field(0, ge=0, le=8, description="Known prefix constraint bits")
    no_filtering: bool = Field(False, description="Ablation switch: disable classical filtering")
    no_adaptivity: bool = Field(False, description="Ablation switch: disable adaptive policy")
    no_noise_awareness: bool = Field(False, description="Ablation switch: disable noise awareness")
    no_restart: bool = Field(False, description="Ablation switch: disable shallow restarts")


class RoundLogItem(BaseModel):
    round: int
    action: str
    iterations: int = 0
    shots: int = 0
    measured_key: int = 0
    oracle_calls: int = 0
    success: bool = False
    noise_estimate: Optional[float] = None


class ExecutionRecordResponse(BaseModel):
    strategy_name: str
    target_key: int
    found_key: Optional[int] = None
    is_verified: bool
    iterations: int
    oracle_calls: int
    classical_filter_cost: int
    classical_verify_cost: int
    total_effective_cost: float
    circuit_depth: int
    qubits_total: int
    two_qubit_gates: int
    total_gates: int
    shots: int
    noise_level: float
    wall_clock_time: float
    seed: int
    # Compatibility aliases for dashboard frontend
    total_oracle_calls: int = 0
    classical_verification_calls: int = 0
    wall_clock_seconds: float = 0.0
    rounds_executed: int = 1
    final_search_space_size: int = 0
    round_logs: List[RoundLogItem] = Field(default_factory=list)
    per_attempt_success: bool = False
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class ReadinessRequest(BaseModel):
    cipher: str = Field("AES-128", description="Cipher name (e.g. AES-128, AES-256, S-AES)")
    physical_error_rate: float = Field(
        0.001, ge=0.0, le=0.1, description="Physical hardware error rate"
    )
    code_threshold: float = Field(
        0.01, ge=0.001, le=0.05, description="Surface code fault tolerance threshold"
    )


class ReadinessResponse(BaseModel):
    cipher: str
    key_size: int
    block_size: int
    ideal_grover_iterations: str
    logical_qubits_required: int
    circuit_depth_estimate: int
    two_qubit_gates: int
    total_gates: int
    physical_error_rate: float
    circuit_survival_probability: float
    nisq_feasibility_verdict: str
    literature_source: str
    safety_disclaimer: str
    code_distance: int = 0
    physical_qubits_required: int = 0
    single_round_survival: float = 0.0
    threshold_margin: float = 0.0


class AssistantChatRequest(BaseModel):
    message: str = Field(..., description="User query or command")
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list, description="Prior conversation messages"
    )
    confirmed_execution: bool = Field(
        False, description="User confirmation flag for simulation runs"
    )


class AssistantChatResponse(BaseModel):
    reply: str
    extracted_config: Optional[SimulateRequest] = None
    requires_confirmation: bool = False
    grounded_evidence: List[str] = Field(default_factory=list)
    safety_disclaimer: str
