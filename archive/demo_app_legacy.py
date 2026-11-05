"""Interactive Streamlit Demo for AdaptiveGrover-QCA."""

import os
import random

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from agqca.analyzer.readiness import SAFETY_DISCLAIMER, ReadinessAnalyzer
from agqca.filtering.constraints import PrefixConstraint
from agqca.strategies.adaptive import AdaptiveHybridStrategy
from agqca.strategies.base import SearchContext
from agqca.strategies.brute_force import ClassicalBruteForceStrategy
from agqca.strategies.noise_aware import NoiseAwareGroverStrategy
from agqca.strategies.shallow_restart import ShallowRestartStrategy
from agqca.strategies.standard import StandardGroverStrategy

CACHED_DIR = os.path.join(os.path.dirname(__file__), "cached_results")

st.set_page_config(
    page_title="AdaptiveGrover-QCA Research Demo",
    page_icon="",
    layout="wide",
)

# Header Banner
st.title("AdaptiveGrover-QCA: Adaptive & Noise-Aware Key Search")
st.markdown(
    "**A Reproducible Framework for Practical Quantum Cryptanalysis under Physical Noise**"
)

# Mandatory Safety Disclaimer Alert
st.warning(f"️ **SCIENTIFIC INTEGRITY & SAFETY NOTICE**: {SAFETY_DISCLAIMER}")

# Sidebar controls
st.sidebar.header("️ Experiment Controls")
exec_mode = st.sidebar.radio(
    "Execution Mode",
    ["Fast Offline Demo (Precomputed Cache)", "Live Quantum Simulation"],
    index=0,
)

cipher_choice = st.sidebar.selectbox(
    "Target Cipher",
    ["S-AES (16-bit key)", "Toy SPN (16-bit key)", "Abstract Marked-State Search"],
)

if exec_mode == "Live Quantum Simulation":
    key_size = st.sidebar.slider("Key Search Register (n bits)", min_value=3, max_value=6, value=4)
else:
    key_size = 4

noise_level = st.sidebar.slider(
    "Depolarizing Error Rate",
    min_value=0.0,
    max_value=0.20,
    value=0.02,
    step=0.01,
    format="%.2f",
)

enable_filtering = st.sidebar.checkbox("Apply Classical Pre-Filtering (Known Prefix)", value=True)
prefix_bits = st.sidebar.slider("Known Prefix Bits", min_value=0, max_value=2, value=1) if enable_filtering else 0

tabs = st.tabs([
    " Strategy Benchmarks",
    " Controller Decision Trace",
    " Circuit & Resource Cost",
    " Cryptographic Readiness Analyzer",
])

# -------------------------------------------------------------
# TAB 1: Strategy Benchmarks
# -------------------------------------------------------------
with tabs[0]:
    st.subheader("Performance Comparison Across Search Strategies")

    if exec_mode == "Fast Offline Demo (Precomputed Cache)":
        cached_path = os.path.join(CACHED_DIR, "exp2_noise_agg.csv")
        if os.path.exists(cached_path):
            df_cache = pd.read_csv(cached_path)
            st.markdown("### Measured Key Recovery Rate vs Physical Noise Level")

            fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
            for strat, grp in df_cache.groupby("strategy"):
                grp = grp.sort_values("noise_level")
                ax.plot(grp["noise_level"] * 100.0, grp["recovery_rate"], marker="o", label=strat)
            ax.set_xlabel("Depolarizing Noise Rate (%)")
            ax.set_ylabel("Key Recovery Rate")
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(fontsize=8)
            st.pyplot(fig)
            plt.close(fig)

            st.dataframe(df_cache[["noise_level", "strategy", "recovery_rate", "mean_total_cost"]])
        else:
            st.info("Cached experiment data not found. Run `make reproduce-small` to generate.")
    else:
        st.markdown(f"Running live comparison on $n={key_size}$ bits at noise rate {noise_level:.1%}...")
        if st.button(" Run Live Quantum Search"):
            target_key = random.randint(0, (1 << key_size) - 1)
            ctx = SearchContext(
                key_size=key_size,
                target_key=target_key,
                plaintext=0x0,
                target_ciphertext=0x0,
                verify_fn=lambda k: k == target_key,
                noise_level=noise_level,
                shots_per_round=64,
                max_total_oracle_calls=8000,
                seed=42,
            )

            strategies = [
                ClassicalBruteForceStrategy(),
                StandardGroverStrategy(),
                NoiseAwareGroverStrategy(),
                ShallowRestartStrategy(),
                AdaptiveHybridStrategy(),
            ]

            results = []
            for s in strategies:
                with st.spinner(f"Simulating {s.name}..."):
                    rec = s.run(ctx)
                    results.append({
                        "Strategy": rec.strategy_name,
                        "Key Recovered?": " Yes" if rec.is_verified else "❌ No",
                        "Target Key": hex(rec.target_key),
                        "Found Key": hex(rec.found_key) if rec.found_key is not None else "None",
                        "Total Cost (Ops)": rec.total_effective_cost,
                        "Oracle Calls": rec.oracle_calls,
                        "Verify Tests": rec.classical_verify_cost,
                        "Circuit Depth": rec.circuit_depth,
                    })

            st.table(pd.DataFrame(results))

# -------------------------------------------------------------
# TAB 2: Controller Decision Trace
# -------------------------------------------------------------
with tabs[1]:
    st.subheader("Adaptive Controller Round Trace & Bayesian Online Belief")
    st.markdown(
        "Demonstrates how the controller inspects noise decay, selects optimal iteration counts, "
        "and triggers shallow restarts or strategy switches across multiple rounds."
    )

    if st.button(" Simulate Adaptive Controller Execution"):
        target_k = random.randint(0, (1 << key_size) - 1)
        constraints = []
        if enable_filtering and prefix_bits > 0:
            shift = key_size - prefix_bits
            pval = (target_k >> shift) & ((1 << prefix_bits) - 1)
            constraints.append(PrefixConstraint(key_size, prefix_bits, pval))

        ctx = SearchContext(
            key_size=key_size,
            target_key=target_k,
            plaintext=0x0,
            target_ciphertext=0x0,
            verify_fn=lambda k: k == target_k,
            noise_level=noise_level,
            shots_per_round=32,
            seed=random.randint(1, 99999),
        )

        strat = AdaptiveHybridStrategy(constraints=constraints)
        rec = strat.run(ctx)

        decisions = rec.extra_metadata.get("decisions", [])
        st.success(f"Search Outcome: **{'VERIFIED KEY FOUND' if rec.is_verified else 'FAILED'}** (Key = {hex(rec.target_key)})")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rounds", rec.extra_metadata.get("rounds", 1))
        col2.metric("Filtering Cost", rec.classical_filter_cost)
        col3.metric("Quantum Oracle Calls", rec.oracle_calls)
        col4.metric("Verification Queries", rec.classical_verify_cost)

        st.markdown("### Round Decision History")
        st.dataframe(pd.DataFrame(decisions))

# -------------------------------------------------------------
# TAB 3: Circuit & Resource Breakdown
# -------------------------------------------------------------
with tabs[2]:
    st.subheader("Mode B Reversible Circuit Architecture & Gate Scaling")
    cached_scaling = os.path.join(CACHED_DIR, "exp6_scaling_agg.csv")
    if os.path.exists(cached_scaling):
        df_scale = pd.read_csv(cached_scaling)
        st.dataframe(df_scale)

        fig, ax = plt.subplots(figsize=(7, 3.5), dpi=150)
        ax.plot(df_scale["key_size"], df_scale["qubits_total"], "o-", label="Logical Qubits", color="#1b9e77")
        ax.plot(df_scale["key_size"], df_scale["two_qubit_gates"], "s-", label="2-Qubit Gates (CX)", color="#d95f02")
        ax.set_yscale("log")
        ax.set_xlabel("Key Size (bits)")
        ax.set_ylabel("Resource Count (Log Scale)")
        ax.set_title("Reversible Cipher Circuit Gate & Qubit Scaling")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Run `make reproduce-small` to populate circuit scaling statistics.")

# -------------------------------------------------------------
# TAB 4: Cryptographic Readiness Analyzer
# -------------------------------------------------------------
with tabs[3]:
    st.subheader("Quantum Cryptographic Readiness Assessment")
    st.markdown(
        "Evaluate the practical quantum vulnerability of standard and educational symmetric ciphers "
        "grounded in verified published literature and conservative noisy circuit bounds."
    )

    ana_cipher = st.selectbox("Analyze Cipher", ["AES-128", "AES-192", "AES-256", "S-AES", "ToySPN"])
    ana_keysize = 128 if "128" in ana_cipher else (192 if "192" in ana_cipher else (256 if "256" in ana_cipher else 16))
    ana_known = st.slider("Known Partial Key Bits (Pre-filtered)", 0, ana_keysize - 2, 0)

    analyzer = ReadinessAnalyzer()
    evaluation = analyzer.evaluate(ana_cipher, ana_keysize, known_bits=ana_known, noise_level=noise_level)

    c1, c2, c3 = st.columns(3)
    c1.metric("Effective Key Space", f"{evaluation.effective_key_size} bits")
    c2.metric("Ideal Grover Queries", evaluation.ideal_oracle_calls_str)
    c3.metric("Quantum Risk Level", f"{evaluation.quantum_risk_level} / 5")

    st.markdown("### Feasibility Verdict")
    st.info(evaluation.feasibility_verdict)

    if evaluation.literature_estimates:
        st.markdown("### Verified Literature Resource Estimations")
        for lit in evaluation.literature_estimates:
            with st.expander(f" {lit.citation_str()}"):
                st.write(f"- **Logical Qubits**: {lit.logical_qubits:,}")
                st.write(f"- **T-Depth**: {lit.t_depth or 'N/A'}")
                st.write(f"- **Grover Iterations**: {lit.grover_iterations}")
                st.write(f"- **Notes**: {lit.notes}")
