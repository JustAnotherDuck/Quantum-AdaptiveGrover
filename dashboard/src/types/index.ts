export interface OverviewData {
  project_name: string;
  research_question: string;
  key_findings: string[];
  disclaimer: string;
}

export interface StrategyInfo {
  id: string;
  name: string;
  description: string;
}

export interface RoundLog {
  round: number;
  action: string;
  iterations: number;
  shots: number;
  measured_key: number;
  oracle_calls: number;
  success: boolean;
  noise_estimate?: number;
}

export interface ExecutionRecord {
  strategy_name: string;
  target_key?: number;
  found_key: number | null;
  is_verified: boolean;
  total_oracle_calls: number;
  classical_verification_calls: number;
  total_effective_cost: number;
  wall_clock_seconds: number;
  rounds_executed: number;
  final_search_space_size: number;
  round_logs: RoundLog[];
  per_attempt_success?: boolean;
  oracle_calls?: number;
  classical_filter_cost?: number;
  classical_verify_cost?: number;
  wall_clock_time?: number;
  iterations?: number;
  circuit_depth?: number;
  qubits_total?: number;
  two_qubit_gates?: number;
  total_gates?: number;
  shots?: number;
  noise_level?: number;
  seed?: number;
  extra_metadata?: Record<string, any>;
}

export interface ReadinessData {
  cipher: string;
  key_size: number;
  block_size: number;
  ideal_grover_iterations: string;
  logical_qubits_required: number;
  circuit_depth_estimate: number;
  two_qubit_gates: number;
  total_gates: number;
  physical_error_rate: number;
  circuit_survival_probability: number;
  nisq_feasibility_verdict: string;
  literature_source: string;
  safety_disclaimer: string;
  code_distance?: number;
  physical_qubits_required?: number;
  single_round_survival?: number;
  threshold_margin?: number;
}

export interface CircuitData {
  key_size: number;
  mode_a: {
    name: string;
    stats: {
      num_qubits: number;
      depth: number;
      total_gates: number;
      two_qubit_gates: number;
      gate_counts: Record<string, number>;
    };
    qasm_snippet: string;
  };
  mode_b?: {
    name: string;
    stats: {
      num_qubits: number;
      depth: number;
      total_gates: number;
      two_qubit_gates: number;
      gate_counts: Record<string, number>;
    };
  } | null;
}

export interface AssistantResponse {
  reply: string;
  extracted_config?: {
    strategy_name: string;
    key_size: number;
    noise_level: number;
    prefix_bits: number;
    shots_per_round: number;
    max_total_oracle_calls: number;
  } | null;
  requires_confirmation: boolean;
  grounded_evidence: string[];
  safety_disclaimer: string;
}
