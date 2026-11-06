"""FastAPI Backend Server for AdaptiveGrover-QCA Interactive Research Dashboard."""

import asyncio
import json
import os
import random
from typing import Any, AsyncGenerator, Dict, List

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from agqca.analyzer.readiness import evaluate_cipher_readiness
from agqca.api.schemas import (
    AssistantChatRequest,
    AssistantChatResponse,
    ExecutionRecordResponse,
    ReadinessRequest,
    ReadinessResponse,
    RoundLogItem,
    SimulateRequest,
)
from agqca.assistant.provider import MANDATORY_DISCLAIMER, ResearchAssistantProvider
from agqca.filtering.constraints import CandidateFilter, Constraint, PrefixConstraint
from agqca.metrics.tracker import CircuitResourceTracker
from agqca.oracles.grover import build_grover_circuit, optimal_grover_iterations
from agqca.oracles.mode_a import MarkedStateOracle
from agqca.oracles.mode_b_spn import ReversibleSPNOracle
from agqca.strategies.adaptive import AdaptiveHybridStrategy
from agqca.strategies.base import BaseStrategy, SearchContext
from agqca.strategies.brute_force import ClassicalBruteForceStrategy
from agqca.strategies.noise_aware import NoiseAwareGroverStrategy
from agqca.strategies.null_control import RandomGuessNullControlStrategy
from agqca.strategies.shallow_restart import ShallowRestartStrategy
from agqca.strategies.standard import StandardGroverStrategy

app = FastAPI(
    title="AdaptiveGrover-QCA Research API",
    description="Backend service for Quantum Cryptanalysis Simulation, Benchmarking, and Interactive Dashboard",
    version="1.0.0",
)

# Enable CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant_provider = ResearchAssistantProvider()
AGG_DIR = "experiments/aggregated"


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "AdaptiveGrover-QCA API", "version": "1.0.0"}


@app.get("/api/overview")
def get_overview() -> Dict[str, Any]:
    """Retrieve executive summary, key findings, and core benchmark metrics."""
    return {
        "project_name": "AdaptiveGrover-QCA",
        "working_title": "Adaptive and Noise-Aware Key Search for Practical Quantum Cryptanalysis",
        "research_question": (
            "How much of Grover's theoretical quadratic advantage for key search survives "
            "under realistic noisy, depth-limited, resource-constrained quantum execution, "
            "and can an adaptive controller that combines classical candidate filtering, "
            "adaptive iteration selection, noise-aware strategy selection, and shallow-circuit "
            "restarts recover more of it than standard fixed-iteration Grover?"
        ),
        "key_findings": [
            {
                "title": "Decoherence Collapse",
                "finding": "Standard fixed-iteration Grover suffers catastrophic decoherence past ~5% gate error on unmitigated circuits.",
            },
            {
                "title": "Crossover Boundary",
                "finding": "Empirical crossover occurs at ~17.8% noise (95% CI: [17.6%, 18.1%]) where shallow restarts achieve lower cost than deep Grover.",
            },
            {
                "title": "Fair Filtering Decomposition",
                "finding": "Classical filtering reduces candidate space by N/N', but on small spaces (n <= 8) quantum constant prefactors yield quantum speedup < 1.0x.",
            },
            {
                "title": "AES-128 Infeasibility",
                "finding": "Full AES-128 is completely secure against NISQ hardware, requiring >1,785 logical qubits and fault-tolerant computing.",
            },
        ],
        "disclaimer": MANDATORY_DISCLAIMER,
    }


@app.get("/api/strategies")
def list_strategies() -> List[Dict[str, Any]]:
    """List available search strategies with their properties and parameter specs."""
    return [
        {
            "id": "adaptive_hybrid",
            "name": "Adaptive Hybrid (Proposed)",
            "description": "Full 4-lever controller with candidate filtering, online Bayesian fidelity updates, noise-aware tuning, and shallow restarts.",
            "type": "quantum_hybrid",
        },
        {
            "id": "standard_grover",
            "name": "Standard Grover",
            "description": "Fixed theoretical optimal iterations k = pi/4 * sqrt(N). Single or multi-round deep execution.",
            "type": "quantum_fixed",
        },
        {
            "id": "shallow_restart",
            "name": "Shallow + Restart",
            "description": "Depth-capped shallow Grover (k <= k_ideal/3) with rapid classical measurement restarts.",
            "type": "quantum_shallow",
        },
        {
            "id": "noise_aware",
            "name": "Noise-Aware Grover",
            "description": "Optimizes iteration count to minimize expected cost k / p_noisy(k) based on noise calibration.",
            "type": "quantum_tuned",
        },
        {
            "id": "classical_brute_force",
            "name": "Classical Brute Force",
            "description": "Exhaustive uniform classical search across full (or filtered) candidate register.",
            "type": "classical_baseline",
        },
        {
            "id": "null_control",
            "name": "Random Guess (Null Control)",
            "description": "Uniform random sampling with verification baseline to confirm genuine quantum amplification.",
            "type": "null_control",
        },
    ]


@app.get("/api/experiments")
def get_experiment_data(
    exp: str = Query("all", description="Experiment ID: exp1..exp6 or all"),
) -> Dict[str, Any]:
    """Retrieve precomputed aggregated experimental datasets."""
    files = {
        "exp1": "exp1_scalability_agg.csv",
        "exp2": "exp2_noise_agg.csv",
        "exp3": "exp3_crossover_agg.csv",
        "exp3_summary": "exp3_crossover_summary.csv",
        "exp4": "exp4_filtering_agg.csv",
        "exp5": "exp5_ablation_agg.csv",
        "exp6": "exp6_scaling_agg.csv",
    }
    result = {}
    for key, fname in files.items():
        if exp not in ["all", key]:
            continue
        path = os.path.join(AGG_DIR, fname)
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Clean NaNs to None for valid JSON serialization
            records = df.where(pd.notnull(df), None).to_dict(orient="records")
            result[key] = records
        else:
            result[key] = []
    return result


@app.post("/api/simulate", response_model=ExecutionRecordResponse)
def run_simulation(req: SimulateRequest) -> ExecutionRecordResponse:
    """Execute a single key search run and return complete execution telemetry."""
    target_key = req.target_key
    if target_key is None:
        rng = random.Random(req.seed)
        target_key = rng.randint(0, (1 << req.key_size) - 1)

    constraints: List[Constraint] = []
    filtered_candidates: Optional[List[int]] = None
    filter_cost: int = 0
    if req.prefix_bits > 0:
        shift = req.key_size - req.prefix_bits
        pref_val = (target_key >> shift) & ((1 << req.prefix_bits) - 1)
        constraints.append(
            PrefixConstraint(
                key_size=req.key_size, prefix_bits=req.prefix_bits, prefix_val=pref_val
            )
        )
        filter_engine = CandidateFilter(
            key_size=req.key_size,
            constraints=constraints,
            allow_fallback=True,
        )
        filter_res = filter_engine.filter_space(true_key=target_key)
        filtered_candidates = filter_res.candidates
        filter_cost = filter_res.classical_cost

    def verify_candidate(k: int, tk: int = target_key) -> bool:
        return k == tk

    ctx = SearchContext(
        key_size=req.key_size,
        target_key=target_key,
        plaintext=0x0,
        target_ciphertext=0x0,
        verify_fn=verify_candidate,
        noise_level=req.noise_level,
        shots_per_round=req.shots_per_round,
        max_total_oracle_calls=req.max_total_oracle_calls,
        seed=req.seed,
    )

    strat: BaseStrategy
    if req.strategy_name == "Classical Brute Force":
        strat = ClassicalBruteForceStrategy(
            candidates=filtered_candidates,
            classical_filter_cost=filter_cost,
        )
    elif req.strategy_name == "Random Guess (Null Control)":
        strat = RandomGuessNullControlStrategy()
    elif req.strategy_name == "Standard Grover":
        strat = StandardGroverStrategy(single_run=req.no_restart)
    elif req.strategy_name == "Noise-Aware Grover":
        strat = NoiseAwareGroverStrategy()
    elif req.strategy_name == "Shallow + Restart":
        strat = ShallowRestartStrategy()
    else:
        strat = AdaptiveHybridStrategy(
            constraints=constraints,
            no_filtering=req.no_filtering,
            no_adaptivity=req.no_adaptivity,
            no_noise_awareness=req.no_noise_awareness,
            no_restart=req.no_restart,
        )

    rec = strat.run(ctx)
    extra = rec.extra_metadata or {}
    decisions = extra.get("decisions", [])
    round_logs: List[RoundLogItem] = []

    if decisions:
        for i, dec in enumerate(decisions):
            round_logs.append(
                RoundLogItem(
                    round=dec.get("round", i + 1),
                    action=str(dec.get("action", dec.get("strategy", "search_iteration"))),
                    iterations=int(dec.get("iterations", 0)),
                    shots=int(dec.get("shots", 0)),
                    measured_key=int(dec.get("measured_key", rec.found_key if rec.found_key is not None else 0)),
                    oracle_calls=int(
                        dec.get("oracle_calls", int(dec.get("iterations", 0)) * int(dec.get("shots", 0)))
                    ),
                    success=bool(dec.get("success", False)),
                    noise_estimate=float(dec.get("noise_estimate", rec.noise_level)),
                )
            )
    else:
        rounds_cnt = max(1, int(extra.get("rounds", 1)))
        calls_per_round = rec.oracle_calls // rounds_cnt
        iter_per_round = rec.iterations // rounds_cnt
        shots_per_round = rec.shots // rounds_cnt if rec.shots else 0
        for r in range(1, rounds_cnt + 1):
            is_last = r == rounds_cnt
            round_logs.append(
                RoundLogItem(
                    round=r,
                    action="quantum_search"
                    if rec.oracle_calls > 0
                    else "classical_verification",
                    iterations=iter_per_round,
                    shots=shots_per_round,
                    measured_key=int(rec.found_key)
                    if (is_last and rec.is_verified and rec.found_key is not None)
                    else 0,
                    oracle_calls=calls_per_round,
                    success=bool(rec.is_verified if is_last else False),
                    noise_estimate=float(rec.noise_level),
                )
            )

    return ExecutionRecordResponse(
        strategy_name=rec.strategy_name,
        target_key=rec.target_key,
        found_key=rec.found_key,
        is_verified=rec.is_verified,
        iterations=rec.iterations,
        oracle_calls=rec.oracle_calls,
        classical_filter_cost=rec.classical_filter_cost,
        classical_verify_cost=rec.classical_verify_cost,
        total_effective_cost=rec.total_effective_cost,
        circuit_depth=rec.circuit_depth,
        qubits_total=rec.qubits_total,
        two_qubit_gates=rec.two_qubit_gates,
        total_gates=rec.total_gates,
        shots=rec.shots,
        noise_level=rec.noise_level,
        wall_clock_time=rec.wall_clock_time,
        seed=rec.seed,
        total_oracle_calls=rec.oracle_calls,
        classical_verification_calls=rec.classical_verify_cost,
        wall_clock_seconds=rec.wall_clock_time,
        rounds_executed=int(extra.get("rounds", max(1, len(round_logs)))),
        final_search_space_size=int(extra.get("candidates_remaining", 1 << req.key_size)),
        round_logs=round_logs,
        per_attempt_success=bool(extra.get("per_attempt_success", False)),
        extra_metadata=extra,
    )


@app.get("/api/simulate/stream")
async def stream_simulation(
    key_size: int = Query(4, ge=2, le=8),
    noise_level: float = Query(0.02, ge=0.0, le=0.5),
    prefix_bits: int = Query(0, ge=0, le=4),
    seed: int = Query(42),
) -> StreamingResponse:
    """Stream live round-by-round controller actions via Server-Sent Events (SSE)."""

    async def event_generator() -> AsyncGenerator[str, None]:
        rng = random.Random(seed)
        target_key = rng.randint(0, (1 << key_size) - 1)

        stream_constraints: List[Constraint] = []
        if prefix_bits > 0:
            shift = key_size - prefix_bits
            pref_val = (target_key >> shift) & ((1 << prefix_bits) - 1)
            stream_constraints.append(
                PrefixConstraint(key_size=key_size, prefix_bits=prefix_bits, prefix_val=pref_val)
            )

        def stream_verify(k: int, tk: int = target_key) -> bool:
            return k == tk

        ctx = SearchContext(
            key_size=key_size,
            target_key=target_key,
            plaintext=0x0,
            target_ciphertext=0x0,
            verify_fn=stream_verify,
            noise_level=noise_level,
            shots_per_round=32,
            max_total_oracle_calls=15000,
            seed=seed,
        )

        strat: BaseStrategy = AdaptiveHybridStrategy(constraints=stream_constraints)


        # Yield start event
        yield f"data: {json.dumps({'event': 'start', 'key_size': key_size, 'target_key': target_key, 'noise_level': noise_level})}\n\n"
        await asyncio.sleep(0.05)

        rec = strat.run(ctx)
        decisions = rec.extra_metadata.get("decisions", [])
        for step in decisions:
            yield f"data: {json.dumps({'event': 'round', 'data': step})}\n\n"
            await asyncio.sleep(0.08)

        # Yield completion
        summary = {
            "event": "complete",
            "is_verified": rec.is_verified,
            "found_key": rec.found_key,
            "total_effective_cost": rec.total_effective_cost,
            "oracle_calls": rec.oracle_calls,
            "classical_verify_cost": rec.classical_verify_cost,
            "wall_clock_time": rec.wall_clock_time,
        }
        yield f"data: {json.dumps(summary)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/readiness", response_model=ReadinessResponse)
def evaluate_readiness(req: ReadinessRequest) -> ReadinessResponse:
    """Evaluate cryptographic readiness of a symmetric cipher against NISQ quantum search."""
    rep = evaluate_cipher_readiness(
        cipher_name=req.cipher,
        physical_gate_error=req.physical_error_rate,
        surface_code_threshold=req.code_threshold,
    )
    return ReadinessResponse(
        cipher=rep.cipher_name,
        key_size=rep.key_size,
        block_size=rep.block_size,
        ideal_grover_iterations=f"2^{rep.ideal_grover_iterations_exp}",
        logical_qubits_required=rep.logical_qubits_required,
        circuit_depth_estimate=rep.circuit_depth_estimate,
        two_qubit_gates=rep.two_qubit_gates,
        total_gates=rep.total_gates,
        physical_error_rate=rep.physical_error_rate,
        circuit_survival_probability=rep.circuit_survival_probability,
        nisq_feasibility_verdict=rep.nisq_feasibility_verdict,
        literature_source=rep.literature_source,
        safety_disclaimer=rep.disclaimer,
        code_distance=rep.code_distance,
        physical_qubits_required=rep.physical_qubits_required,
        single_round_survival=rep.single_round_survival,
        threshold_margin=rep.threshold_margin,
    )


@app.get("/api/circuits")
def get_circuit_resources(key_size: int = Query(4, ge=2, le=8)) -> Dict[str, Any]:
    """Return circuit statistics and QASM snippets for Mode A and Mode B."""
    # Mode A
    oracle_a = MarkedStateOracle(num_qubits=key_size, marked_states=[1])
    k_ideal = optimal_grover_iterations(key_size, num_marked=1)
    qc_a = build_grover_circuit(oracle_a, iterations=k_ideal, measure=True)
    stats_a = CircuitResourceTracker.analyze_circuit(qc_a)

    # Mode B (if nibble aligned)
    stats_b = None
    if key_size in [4, 8]:
        oracle_b = ReversibleSPNOracle(
            key_size=key_size,
            block_size=key_size,
            plaintext=0x1,
            target_ciphertext=0x2,
            rounds=1 if key_size == 4 else 2,
        )
        qc_b = oracle_b.construct_circuit()
        stats_b = CircuitResourceTracker.analyze_circuit(qc_b)

    return {
        "key_size": key_size,
        "mode_a": {
            "name": f"Mode A Phase Oracle ({key_size} qubits, k={k_ideal})",
            "stats": stats_a,
            "qasm_snippet": qc_a.qasm()[:1200] if hasattr(qc_a, "qasm") else "",
        },
        "mode_b": {
            "name": f"Mode B Reversible SPN Oracle ({key_size} bits)",
            "stats": stats_b,
        }
        if stats_b
        else None,
    }


@app.post("/api/assistant/chat", response_model=AssistantChatResponse)
def assistant_chat(req: AssistantChatRequest) -> AssistantChatResponse:
    """Natural-language scientific assistant with parameter extraction and grounded validation."""
    return assistant_provider.process_message(
        message=req.message,
        conversation_history=req.conversation_history,
        confirmed_execution=req.confirmed_execution,
    )


# Serve built React dashboard single-page application if available
dist_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "dashboard",
    "dist",
)
if not os.path.exists(dist_dir):
    dist_dir = "dashboard/dist"
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
