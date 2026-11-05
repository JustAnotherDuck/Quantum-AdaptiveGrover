"""Illustrative Expected Trends (Pre-Experiment Theoretical Sketches).

CRITICAL NOTICE (NON-NEGOTIABLE RULE 1):
This script generates illustrative theoretical sketches based purely on analytical formulas
and asymptotic complexity models. It does NOT contain or represent measured experimental data.
All figures produced by this script are clearly watermarked as 'Illustrative Expected Trend'.
"""

import os

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = "paper_support/figures"


def generate_illustrative_plots() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Theoretical Speedup vs Key Size (O(N) vs O(sqrt(N)))
    n_bits = np.arange(4, 25)
    n_space = 2.0**n_bits
    classical_cost = n_space / 2.0
    grover_ideal = (np.pi / 4.0) * np.sqrt(n_space)

    plt.style.use(
        "seaborn-v0_8-colorblind" if "seaborn-v0_8-colorblind" in plt.style.available else "default"
    )
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)

    ax.plot(n_bits, classical_cost, label="Classical Exhaustive Search O(N)", color="#d95f02", lw=2)
    ax.plot(
        n_bits,
        grover_ideal,
        label="Ideal Grover Search O(√N)",
        color="#7570b3",
        lw=2,
        linestyle="--",
    )

    ax.set_yscale("log")
    ax.set_xlabel("Key Length n (bits)")
    ax.set_ylabel("Expected Oracle / Verification Operations")
    ax.set_title("Illustrative Expected Trend: Asymptotic Scaling")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()

    # Watermark
    ax.text(
        0.5,
        0.5,
        "Illustrative Expected Trend\n(Theoretical Asymptotic)",
        transform=ax.transAxes,
        fontsize=14,
        color="gray",
        alpha=0.3,
        ha="center",
        va="center",
        rotation=25,
    )

    fig.tight_layout()
    pdf_path = os.path.join(OUTPUT_DIR, "fig_illustrative_asymptotic.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig_illustrative_asymptotic.png")
    fig.savefig(pdf_path)
    fig.savefig(png_path)
    plt.close(fig)
    print(f"Generated illustrative sketches: {pdf_path}, {png_path}")


if __name__ == "__main__":
    generate_illustrative_plots()
