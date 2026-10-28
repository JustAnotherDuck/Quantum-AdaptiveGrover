"""Generate publication-ready vector figures (PDF + PNG) from aggregated experimental data."""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

AGG_DIR = "experiments/aggregated"
FIG_DIR = "paper_support/figures"


def setup_matplotlib() -> None:
    plt.rcParams.update({
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
        "figure.titlesize": 13,
        "lines.linewidth": 1.75,
        "lines.markersize": 6,
    })


def plot_fig1_scalability() -> None:
    path = os.path.join(AGG_DIR, "exp1_scalability_agg.csv")
    if not os.path.exists(path):
        print("  Skipping Fig 1: data not found.")
        return
    df = pd.read_csv(path)

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    colors = {
        "Classical Brute Force": "#d95f02",
        "Standard Grover": "#7570b3",
        "Adaptive Hybrid (Proposed)": "#1b9e77",
    }
    markers = {
        "Classical Brute Force": "o",
        "Standard Grover": "s",
        "Adaptive Hybrid (Proposed)": "^",
    }

    for strat, group in df.groupby("strategy"):
        group = group.sort_values("key_size")
        color = colors.get(strat, "#333333")
        marker = markers.get(strat, "o")

        ax.plot(
            group["key_size"],
            group["mean_total_cost"],
            label=strat,
            color=color,
            marker=marker,
        )
        ax.fill_between(
            group["key_size"],
            group["cost_ci_low"],
            group["cost_ci_high"],
            color=color,
            alpha=0.15,
        )

    ax.set_yscale("log")
    ax.set_xlabel("Key Search Space n (bits)")
    ax.set_ylabel("Total Effective Cost (Operations)")
    ax.set_title("Exp 1: Scalability Baseline vs Key Size (Noise = 2%)")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()
    fig.tight_layout()

    fig.savefig(os.path.join(FIG_DIR, "fig1_scalability.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig1_scalability.png"))
    plt.close(fig)

    with open(os.path.join(FIG_DIR, "fig1_scalability_caption.md"), "w") as f:
        f.write(
            "**Figure 1: Scalability Baseline vs Key Size.** Total effective cost comparison "
            "between classical brute-force, standard fixed Grover, and the proposed adaptive hybrid "
            "across key sizes n in [3, 5] bits under 2% depolarizing gate noise. Shaded bands represent "
            "95% bootstrap confidence intervals computed over independent seeds. Source: `exp1_scalability_agg.csv`."
        )


def plot_fig2_noise_recovery() -> None:
    path = os.path.join(AGG_DIR, "exp2_noise_agg.csv")
    if not os.path.exists(path):
        print("  Skipping Fig 2: data not found.")
        return
    df = pd.read_csv(path)

    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=300)
    palette = {
        "Classical Brute Force": "#666666",
        "Standard Grover": "#d95f02",
        "BBHT (Exponential Schedule)": "#7570b3",
        "Noise-Aware Grover": "#e7298a",
        "Shallow + Restart": "#e6ab02",
        "Adaptive Hybrid (Proposed)": "#1b9e77",
    }

    for strat, group in df.groupby("strategy"):
        group = group.sort_values("noise_level")
        color = palette.get(strat, "#333333")

        ax.errorbar(
            group["noise_level"] * 100.0,
            group["recovery_rate"],
            yerr=[
                group["recovery_rate"] - group["recovery_ci_low"],
                group["recovery_ci_high"] - group["recovery_rate"],
            ],
            label=strat,
            color=color,
            marker="o",
            capsize=3,
        )

    ax.set_xlabel("Depolarizing Error Rate (%)")
    ax.set_ylabel("Key Recovery Success Rate")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Exp 2: Strategy Recovery Rate vs Physical Noise Level")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower left", fontsize=8)
    fig.tight_layout()

    fig.savefig(os.path.join(FIG_DIR, "fig2_noise_recovery.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig2_noise_recovery.png"))
    plt.close(fig)

    with open(os.path.join(FIG_DIR, "fig2_noise_recovery_caption.md"), "w") as f:
        f.write(
            "**Figure 2: Noise Resilience across Search Strategies.** Key recovery probability as "
            "depolarizing error sweeps from 0% to 20% on n=4 bit key search. While deep fixed Grover degrades "
            "sharply past 5% noise, noise-aware and adaptive shallow-restart mechanisms maintain high recovery rates. "
            "Error bars depict 95% bootstrap confidence intervals. Source: `exp2_noise_agg.csv`."
        )


def plot_fig3_crossover() -> None:
    path = os.path.join(AGG_DIR, "exp3_crossover_agg.csv")
    if not os.path.exists(path):
        print("  Skipping Fig 3: data not found.")
        return
    df = pd.read_csv(path)

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    for strat, group in df.groupby("strategy"):
        group = group.sort_values("noise_level")
        ax.plot(
            group["noise_level"] * 100.0,
            group["recovery_rate"],
            label=strat,
            marker="s",
        )

    ax.set_xlabel("Gate Error Rate (%)")
    ax.set_ylabel("Key Recovery Rate")
    ax.set_title("Exp 3: Crossover Analysis (Deep Grover vs Shallow + Restart)")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()
    fig.tight_layout()

    fig.savefig(os.path.join(FIG_DIR, "fig3_crossover.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig3_crossover.png"))
    plt.close(fig)

    with open(os.path.join(FIG_DIR, "fig3_crossover_caption.md"), "w") as f:
        f.write(
            "**Figure 3: Crossover Noise Boundary.** Identification of the crossover error rate where "
            "shallow-circuit restarts overtake deep standard Grover. Above ~5-6% noise, accumulated decoherence "
            "in deep circuits causes single-shot Grover failure, whereas shallow circuits preserve fidelity. "
            "Source: `exp3_crossover_agg.csv`."
        )


def plot_fig4_filtering() -> None:
    path = os.path.join(AGG_DIR, "exp4_filtering_agg.csv")
    if not os.path.exists(path):
        print("  Skipping Fig 4: data not found.")
        return
    df = pd.read_csv(path)

    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    x = range(len(df))
    ax.bar(x, df["effective_speedup"], color="#1b9e77", width=0.55, edgecolor="black")

    ax.set_xticks(x)
    ax.set_xticklabels(df["profile"], rotation=15, ha="right")
    ax.set_ylabel("Effective Speedup over Classical Brute Force")
    ax.set_title("Exp 4: Search Space Reduction vs Effective Speedup")
    ax.axhline(1.0, color="red", linestyle="--", label="Classical Parity (1.0x)")
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.legend()
    fig.tight_layout()

    fig.savefig(os.path.join(FIG_DIR, "fig4_filtering_speedup.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig4_filtering_speedup.png"))
    plt.close(fig)

    with open(os.path.join(FIG_DIR, "fig4_filtering_speedup_caption.md"), "w") as f:
        f.write(
            "**Figure 4: Candidate Filtering Efficiency.** Measured speedup factor over classical brute force "
            "as search space constraints reduce candidate cardinality, including classical pre-filtering overhead. "
            "Source: `exp4_filtering_agg.csv`."
        )


def plot_fig5_ablation() -> None:
    path = os.path.join(AGG_DIR, "exp5_ablation_agg.csv")
    if not os.path.exists(path):
        print("  Skipping Fig 5: data not found.")
        return
    df = pd.read_csv(path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=300)

    y_pos = np.arange(len(df))
    ax1.barh(y_pos, df["recovery_rate"], color="#7570b3", edgecolor="black")
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(df["configuration"], fontsize=8)
    ax1.set_xlabel("Key Recovery Rate")
    ax1.set_xlim(0, 1.05)
    ax1.set_title("Recovery Rate by Ablation")
    ax1.grid(True, axis="x", linestyle=":", alpha=0.6)

    ax2.barh(y_pos, df["mean_total_cost"], color="#d95f02", edgecolor="black")
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])
    ax2.set_xlabel("Mean Total Effective Cost")
    ax2.set_title("Total Cost by Ablation")
    ax2.grid(True, axis="x", linestyle=":", alpha=0.6)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig5_ablation.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig5_ablation.png"))
    plt.close(fig)

    with open(os.path.join(FIG_DIR, "fig5_ablation_caption.md"), "w") as f:
        f.write(
            "**Figure 5: Framework Ablation Study.** Recovery probability and total computational cost "
            "when isolating each of the four framework levers: (1) candidate filtering, (2) adaptive controller, "
            "(3) noise-awareness, and (4) shallow restarts. Source: `exp5_ablation_agg.csv`."
        )


def plot_fig6_scaling() -> None:
    path = os.path.join(AGG_DIR, "exp6_scaling_agg.csv")
    if not os.path.exists(path):
        print("  Skipping Fig 6: data not found.")
        return
    df = pd.read_csv(path)

    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=300)

    eval_data = df[~df["is_extrapolated"]]
    ext_data = df[df["is_extrapolated"]]

    # Qubits and 2Q gates
    ax.plot(eval_data["key_size"], eval_data["qubits_total"], "o-", color="#1b9e77", label="Qubits (Measured)")
    ax.plot(ext_data["key_size"], ext_data["qubits_total"], "o--", color="#1b9e77", alpha=0.6, label="Qubits (Extrapolated)")

    ax.plot(eval_data["key_size"], eval_data["depth"], "s-", color="#d95f02", label="Transpiled Depth (Measured)")
    ax.plot(ext_data["key_size"], ext_data["depth"], "s--", color="#d95f02", alpha=0.6, label="Transpiled Depth (Extrapolated)")

    ax.set_yscale("log")
    ax.set_xlabel("Cipher Key Size (bits)")
    ax.set_ylabel("Circuit Resources (Log Scale)")
    ax.set_title("Exp 6: Reversible Cipher Circuit Scaling (Mode B)")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=8)
    fig.tight_layout()

    fig.savefig(os.path.join(FIG_DIR, "fig6_scaling.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig6_scaling.png"))
    plt.close(fig)

    with open(os.path.join(FIG_DIR, "fig6_scaling_caption.md"), "w") as f:
        f.write(
            "**Figure 6: Reversible SPN Circuit Resource Scaling.** Physical qubits and transpiled circuit depth "
            "for Mode B reversible cipher oracles. Solid markers represent measured gate synthesis up to 16 bits; "
            "dashed markers show architectural extrapolations up to 128-bit key recovery. Source: `exp6_scaling_agg.csv`."
        )


def main() -> None:
    os.makedirs(FIG_DIR, exist_ok=True)
    setup_matplotlib()
    print("Generating publication-quality figures from experimental data...")
    plot_fig1_scalability()
    plot_fig2_noise_recovery()
    plot_fig3_crossover()
    plot_fig4_filtering()
    plot_fig5_ablation()
    plot_fig6_scaling()
    print(f"All figures saved to {FIG_DIR}.")


if __name__ == "__main__":
    main()
