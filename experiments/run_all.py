"""Master reproducible experiment runner for Experiments 1 through 6."""

import argparse
import os
import random
import time
from typing import Any, Dict, List

import pandas as pd
import yaml

from agqca.filtering.constraints import PrefixConstraint
from agqca.metrics.stats import bootstrap_ci
from agqca.metrics.tracker import CircuitResourceTracker
from agqca.oracles.mode_b_spn import ReversibleSPNOracle
from agqca.strategies.adaptive import AdaptiveHybridStrategy
from agqca.strategies.base import SearchContext
from agqca.strategies.bbht import BBHTStrategy
from agqca.strategies.brute_force import ClassicalBruteForceStrategy
from agqca.strategies.noise_aware import NoiseAwareGroverStrategy
from agqca.strategies.shallow_restart import ShallowRestartStrategy
from agqca.strategies.standard import StandardGroverStrategy

RAW_DIR = "experiments/raw_data"
AGG_DIR = "experiments/aggregated"
CONFIG_DIR = "experiments/configs"


def ensure_dirs() -> None:
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(AGG_DIR, exist_ok=True)


def get_strategy_by_name(name: str, **kwargs: Any) -> Any:
    if name == "Classical Brute Force":
        return ClassicalBruteForceStrategy()
    elif name == "Standard Grover":
        return StandardGroverStrategy()
    elif name == "BBHT (Exponential Schedule)":
        return BBHTStrategy()
    elif name == "Noise-Aware Grover":
        return NoiseAwareGroverStrategy()
    elif name == "Shallow + Restart":
        return ShallowRestartStrategy()
    elif "Adaptive Hybrid" in name:
        return AdaptiveHybridStrategy(**kwargs)
    raise ValueError(f"Unknown strategy name: {name}")


def run_exp1(mode: str = "small") -> None:
    print("\n=== Running Experiment 1: Scalability Baseline vs Key Size ===")
    with open(os.path.join(CONFIG_DIR, "exp1_scalability.yaml"), "r") as f:
        cfg = yaml.safe_load(f)

    key_sizes = cfg["key_sizes_small"] if mode == "small" else cfg["key_sizes_full"]
    num_seeds = cfg["seeds_small"] if mode == "small" else cfg["seeds_full"]
    strategies = cfg["strategies"]
    noise_level = cfg["noise_level"]

    raw_records: List[Dict[str, Any]] = []

    for n in key_sizes:
        print(f"  Key size n={n} bits...")
        for s_idx in range(num_seeds):
            seed = 1000 * n + s_idx
            rng = random.Random(seed)
            target_key = rng.randint(0, (1 << n) - 1)

            for strat_name in strategies:
                strat = get_strategy_by_name(strat_name)
                ctx = SearchContext(
                    key_size=n,
                    target_key=target_key,
                    plaintext=0x0,
                    target_ciphertext=0x0,
                    verify_fn=lambda k, tk=target_key: k == tk,
                    noise_level=noise_level,
                    shots_per_round=cfg["shots"],
                    max_total_oracle_calls=15000,
                    seed=seed,
                )
                rec = strat.run(ctx)
                data = rec.to_dict()
                data["key_size"] = n
                raw_records.append(data)

    df_raw = pd.DataFrame(raw_records)
    df_raw.to_csv(os.path.join(RAW_DIR, "exp1_scalability_raw.csv"), index=False)

    # Aggregate statistics
    agg_rows = []
    for (n, strat_name), group in df_raw.groupby(["key_size", "strategy_name"]):
        succ = group["is_verified"].astype(float).tolist()
        costs = group["total_effective_cost"].tolist()
        oracles = group["oracle_calls"].tolist()
        depths = group["circuit_depth"].tolist()

        m_succ, l_succ, h_succ = bootstrap_ci(succ)
        m_cost, l_cost, h_cost = bootstrap_ci(costs)
        m_depth, _, _ = bootstrap_ci(depths)
        baseline = float(1 << n) / 2.0
        speedup = baseline / m_cost if m_cost > 0 else 0.0

        agg_rows.append({
            "key_size": n,
            "strategy": strat_name,
            "success_rate": m_succ,
            "success_ci_low": l_succ,
            "success_ci_high": h_succ,
            "mean_total_cost": m_cost,
            "cost_ci_low": l_cost,
            "cost_ci_high": h_cost,
            "mean_oracle_calls": float(pd.Series(oracles).mean()),
            "mean_depth": m_depth,
            "speedup_over_classical": speedup,
        })

    df_agg = pd.DataFrame(agg_rows)
    df_agg.to_csv(os.path.join(AGG_DIR, "exp1_scalability_agg.csv"), index=False)
    print("  Saved raw and aggregated Exp 1 data.")


def run_exp2(mode: str = "small") -> None:
    print("\n=== Running Experiment 2: Noise Level vs Recovery Probability ===")
    with open(os.path.join(CONFIG_DIR, "exp2_noise.yaml"), "r") as f:
        cfg = yaml.safe_load(f)

    n = cfg["key_size"]
    noise_levels = cfg["noise_levels"]
    num_seeds = cfg["seeds_small"] if mode == "small" else cfg["seeds_full"]
    strategies = cfg["strategies"]

    raw_records: List[Dict[str, Any]] = []

    for noise in noise_levels:
        print(f"  Noise level: {noise:.0%}...")
        for s_idx in range(num_seeds):
            seed = 2000 + s_idx
            rng = random.Random(seed)
            target_key = rng.randint(0, (1 << n) - 1)

            for strat_name in strategies:
                strat = get_strategy_by_name(strat_name)
                ctx = SearchContext(
                    key_size=n,
                    target_key=target_key,
                    plaintext=0x0,
                    target_ciphertext=0x0,
                    verify_fn=lambda k, tk=target_key: k == tk,
                    noise_level=noise,
                    shots_per_round=cfg["shots"],
                    max_total_oracle_calls=15000,
                    seed=seed,
                )
                rec = strat.run(ctx)
                data = rec.to_dict()
                raw_records.append(data)

    df_raw = pd.DataFrame(raw_records)
    df_raw.to_csv(os.path.join(RAW_DIR, "exp2_noise_raw.csv"), index=False)

    agg_rows = []
    for (noise, strat_name), group in df_raw.groupby(["noise_level", "strategy_name"]):
        succ = group["is_verified"].astype(float).tolist()
        costs = group["total_effective_cost"].tolist()
        depths = group["circuit_depth"].tolist()

        m_succ, l_succ, h_succ = bootstrap_ci(succ)
        m_cost, l_cost, h_cost = bootstrap_ci(costs)
        m_depth, _, _ = bootstrap_ci(depths)

        agg_rows.append({
            "noise_level": noise,
            "strategy": strat_name,
            "recovery_rate": m_succ,
            "recovery_ci_low": l_succ,
            "recovery_ci_high": h_succ,
            "mean_total_cost": m_cost,
            "cost_ci_low": l_cost,
            "cost_ci_high": h_cost,
            "mean_depth": m_depth,
        })

    df_agg = pd.DataFrame(agg_rows)
    df_agg.to_csv(os.path.join(AGG_DIR, "exp2_noise_agg.csv"), index=False)
    print("  Saved raw and aggregated Exp 2 data.")


def run_exp3(mode: str = "small") -> None:
    print("\n=== Running Experiment 3: Crossover Analysis (Deep vs Shallow+Restart) ===")
    with open(os.path.join(CONFIG_DIR, "exp3_crossover.yaml"), "r") as f:
        cfg = yaml.safe_load(f)

    n = cfg["key_size"]
    noise_sweep = cfg["noise_sweep"]
    num_seeds = cfg["seeds_small"] if mode == "small" else cfg["seeds_full"]
    strategies = cfg["strategies"]

    raw_records: List[Dict[str, Any]] = []

    for noise in noise_sweep:
        for s_idx in range(num_seeds):
            seed = 3000 + s_idx
            rng = random.Random(seed)
            target_key = rng.randint(0, (1 << n) - 1)

            for strat_name in strategies:
                strat = get_strategy_by_name(strat_name)
                ctx = SearchContext(
                    key_size=n,
                    target_key=target_key,
                    plaintext=0x0,
                    target_ciphertext=0x0,
                    verify_fn=lambda k, tk=target_key: k == tk,
                    noise_level=noise,
                    shots_per_round=cfg["shots"],
                    max_total_oracle_calls=15000,
                    seed=seed,
                )
                rec = strat.run(ctx)
                data = rec.to_dict()
                raw_records.append(data)

    df_raw = pd.DataFrame(raw_records)
    df_raw.to_csv(os.path.join(RAW_DIR, "exp3_crossover_raw.csv"), index=False)

    agg_rows = []
    for (noise, strat_name), group in df_raw.groupby(["noise_level", "strategy_name"]):
        succ = group["is_verified"].astype(float).tolist()
        costs = group["total_effective_cost"].tolist()
        m_succ, l_succ, h_succ = bootstrap_ci(succ)
        m_cost, l_cost, h_cost = bootstrap_ci(costs)

        agg_rows.append({
            "noise_level": noise,
            "strategy": strat_name,
            "recovery_rate": m_succ,
            "ci_low": l_succ,
            "ci_high": h_succ,
            "mean_total_cost": m_cost,
        })

    df_agg = pd.DataFrame(agg_rows)
    df_agg.to_csv(os.path.join(AGG_DIR, "exp3_crossover_agg.csv"), index=False)
    print("  Saved raw and aggregated Exp 3 data.")


def run_exp4(mode: str = "small") -> None:
    print("\n=== Running Experiment 4: Search Space Reduction Efficiency ===")
    with open(os.path.join(CONFIG_DIR, "exp4_filtering.yaml"), "r") as f:
        cfg = yaml.safe_load(f)

    n = cfg["key_size"]
    noise = cfg["noise_level"]
    profiles = cfg["constraint_profiles"]
    num_seeds = cfg["seeds_small"] if mode == "small" else cfg["seeds_full"]

    raw_records: List[Dict[str, Any]] = []

    for prof in profiles:
        p_name = prof["name"]
        p_bits = prof["prefix_bits"]

        for s_idx in range(num_seeds):
            seed = 4000 + s_idx
            rng = random.Random(seed)
            target_key = rng.randint(0, (1 << n) - 1)

            constraints = []
            if p_bits > 0:
                shift = n - p_bits
                pref_val = (target_key >> shift) & ((1 << p_bits) - 1)
                constraints.append(
                    PrefixConstraint(key_size=n, prefix_bits=p_bits, prefix_val=pref_val)
                )

            strat = AdaptiveHybridStrategy(constraints=constraints)
            ctx = SearchContext(
                key_size=n,
                target_key=target_key,
                plaintext=0x0,
                target_ciphertext=0x0,
                verify_fn=lambda k, tk=target_key: k == tk,
                noise_level=noise,
                shots_per_round=cfg["shots"],
                max_total_oracle_calls=15000,
                seed=seed,
            )
            rec = strat.run(ctx)
            data = rec.to_dict()
            data["profile"] = p_name
            data["prefix_bits"] = p_bits
            raw_records.append(data)

    df_raw = pd.DataFrame(raw_records)
    df_raw.to_csv(os.path.join(RAW_DIR, "exp4_filtering_raw.csv"), index=False)

    agg_rows = []
    baseline = float(1 << n) / 2.0
    for p_name, group in df_raw.groupby("profile"):
        costs = group["total_effective_cost"].tolist()
        f_costs = group["classical_filter_cost"].tolist()
        m_cost, l_cost, h_cost = bootstrap_ci(costs)
        m_fcost, _, _ = bootstrap_ci(f_costs)
        speedup = baseline / m_cost if m_cost > 0 else 0.0

        agg_rows.append({
            "profile": p_name,
            "mean_filter_cost": m_fcost,
            "mean_total_cost": m_cost,
            "cost_ci_low": l_cost,
            "cost_ci_high": h_cost,
            "effective_speedup": speedup,
        })

    df_agg = pd.DataFrame(agg_rows)
    df_agg.to_csv(os.path.join(AGG_DIR, "exp4_filtering_agg.csv"), index=False)
    print("  Saved raw and aggregated Exp 4 data.")


def run_exp5(mode: str = "small") -> None:
    print("\n=== Running Experiment 5: Full Ablation Study ===")
    with open(os.path.join(CONFIG_DIR, "exp5_ablation.yaml"), "r") as f:
        cfg = yaml.safe_load(f)

    n = cfg["key_size"]
    noise = cfg["noise_level"]
    p_bits = cfg["prefix_bits"]
    configs = cfg["configurations"]
    num_seeds = cfg["seeds_small"] if mode == "small" else cfg["seeds_full"]

    raw_records: List[Dict[str, Any]] = []

    for conf in configs:
        c_name = conf["name"]
        for s_idx in range(num_seeds):
            seed = 5000 + s_idx
            rng = random.Random(seed)
            target_key = rng.randint(0, (1 << n) - 1)

            shift = n - p_bits
            pref_val = (target_key >> shift) & ((1 << p_bits) - 1)
            constraint = PrefixConstraint(key_size=n, prefix_bits=p_bits, prefix_val=pref_val)

            strat = AdaptiveHybridStrategy(
                constraints=[constraint],
                no_filtering=conf["no_filtering"],
                no_adaptivity=conf["no_adaptivity"],
                no_noise_awareness=conf["no_noise_awareness"],
                no_restart=conf["no_restart"],
            )

            ctx = SearchContext(
                key_size=n,
                target_key=target_key,
                plaintext=0x0,
                target_ciphertext=0x0,
                verify_fn=lambda k, tk=target_key: k == tk,
                noise_level=noise,
                shots_per_round=cfg["shots"],
                max_total_oracle_calls=15000,
                seed=seed,
            )
            rec = strat.run(ctx)
            data = rec.to_dict()
            data["configuration"] = c_name
            raw_records.append(data)

    df_raw = pd.DataFrame(raw_records)
    df_raw.to_csv(os.path.join(RAW_DIR, "exp5_ablation_raw.csv"), index=False)

    agg_rows = []
    for c_name, group in df_raw.groupby("configuration"):
        succ = group["is_verified"].astype(float).tolist()
        costs = group["total_effective_cost"].tolist()
        depths = group["circuit_depth"].tolist()

        m_succ, l_succ, h_succ = bootstrap_ci(succ)
        m_cost, l_cost, h_cost = bootstrap_ci(costs)
        m_depth, _, _ = bootstrap_ci(depths)

        agg_rows.append({
            "configuration": c_name,
            "recovery_rate": m_succ,
            "recovery_ci_low": l_succ,
            "recovery_ci_high": h_succ,
            "mean_total_cost": m_cost,
            "cost_ci_low": l_cost,
            "cost_ci_high": h_cost,
            "mean_depth": m_depth,
        })

    df_agg = pd.DataFrame(agg_rows)
    df_agg.to_csv(os.path.join(AGG_DIR, "exp5_ablation_agg.csv"), index=False)
    print("  Saved raw and aggregated Exp 5 data.")


def run_exp6(mode: str = "small") -> None:
    print("\n=== Running Experiment 6: Circuit Resource Scaling for Mode B ===")
    with open(os.path.join(CONFIG_DIR, "exp6_scaling.yaml"), "r") as f:
        cfg = yaml.safe_load(f)

    eval_keys = cfg["evaluated_key_sizes"]
    rounds_map = cfg["rounds_per_key_size"]
    extraps = cfg["extrapolate_key_sizes"]

    scaling_rows = []

    for k_size in eval_keys:
        rounds = rounds_map[k_size]
        oracle = ReversibleSPNOracle(
            key_size=k_size,
            block_size=k_size,
            plaintext=0x1,
            target_ciphertext=0x2,
            rounds=rounds,
        )
        stats = oracle.circuit_stats()
        # Analyze transpiled circuit into basis [u, cx]
        qc = oracle.construct_circuit()
        t_stats = CircuitResourceTracker.analyze_circuit(qc)

        scaling_rows.append({
            "key_size": k_size,
            "rounds": rounds,
            "qubits_total": stats["qubits"],
            "depth": t_stats["depth"],
            "two_qubit_gates": t_stats["two_qubit_gates"],
            "total_gates": t_stats["total_gates"],
            "is_extrapolated": False,
        })

    # Linear and polynomial fits to extrapolate to 32, 64, 128 bits
    for ext_n in extraps:
        ext_rounds = ext_n // 4
        # Extrapolated formula derived from reversible SPN architecture
        # Qubits = key (n) + state (n) + flag (1) = 2*n + 1
        ext_qubits = 2 * ext_n + 1
        # CX gates scale approx 2 * n * rounds + SBox_CX * (n/4) * rounds
        # At n=16, rounds=4: 16 nibbles * 4 = 16 S-boxes * ~95 CX per S-box ~ 1500 CX
        cx_per_sbox = 95
        ext_cx = (ext_n // 4) * ext_rounds * cx_per_sbox * 2 + 2 * ext_n * ext_rounds
        ext_depth = ext_rounds * 188 * 2

        scaling_rows.append({
            "key_size": ext_n,
            "rounds": ext_rounds,
            "qubits_total": ext_qubits,
            "depth": ext_depth,
            "two_qubit_gates": ext_cx,
            "total_gates": ext_cx * 3,
            "is_extrapolated": True,
        })

    df_scaling = pd.DataFrame(scaling_rows)
    df_scaling.to_csv(os.path.join(AGG_DIR, "exp6_scaling_agg.csv"), index=False)
    print("  Saved Exp 6 scaling and extrapolation data.")


def main() -> None:
    parser = argparse.ArgumentParser(description="AdaptiveGrover-QCA Experiment Runner")
    parser.add_argument(
        "--mode",
        choices=["small", "full"],
        default="small",
        help="Run fast small suite (~5 min) or full rigorous suite (~20 min)",
    )
    parser.add_argument(
        "--experiment",
        choices=["1", "2", "3", "4", "5", "6", "all"],
        default="all",
        help="Which experiment to run",
    )
    args = parser.parse_args()

    ensure_dirs()
    t0 = time.time()
    print(f"Starting AdaptiveGrover-QCA Experiment Suite (mode={args.mode})...")

    if args.experiment in ["1", "all"]:
        run_exp1(args.mode)
    if args.experiment in ["2", "all"]:
        run_exp2(args.mode)
    if args.experiment in ["3", "all"]:
        run_exp3(args.mode)
    if args.experiment in ["4", "all"]:
        run_exp4(args.mode)
    if args.experiment in ["5", "all"]:
        run_exp5(args.mode)
    if args.experiment in ["6", "all"]:
        run_exp6(args.mode)

    elapsed = time.time() - t0
    print(f"\nAll experiments completed in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    main()
