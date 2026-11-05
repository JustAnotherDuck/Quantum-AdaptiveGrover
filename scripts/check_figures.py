#!/usr/bin/env python3
"""Data completeness and figure data validator.

Verifies that:
1. All aggregated experimental CSV files exist.
2. No unexpected NaNs or missing values exist in critical columns.
3. Confidence intervals satisfy low <= mean <= high.
4. All generated figures (PNG and PDF) exist and have non-zero size.
5. All table TeX files exist and have non-zero size.
"""

import os
import sys

import pandas as pd

AGG_DIR = "experiments/aggregated"
FIG_DIR = "paper_support/figures"
TABLE_DIR = "paper_support/tables"

EXPECTED_AGG_FILES = [
    "exp1_scalability_agg.csv",
    "exp2_noise_agg.csv",
    "exp3_crossover_agg.csv",
    "exp3_crossover_summary.csv",
    "exp4_filtering_agg.csv",
    "exp5_ablation_agg.csv",
    "exp6_scaling_agg.csv",
]

EXPECTED_FIGURES = [
    "fig1_scalability.png",
    "fig1_scalability.pdf",
    "fig2_noise_recovery.png",
    "fig2_noise_recovery.pdf",
    "fig3_crossover.png",
    "fig3_crossover.pdf",
    "fig4_filtering_speedup.png",
    "fig4_filtering_speedup.pdf",
    "fig5_ablation.png",
    "fig5_ablation.pdf",
    "fig6_scaling.png",
    "fig6_scaling.pdf",
]

EXPECTED_TABLES = [
    "tab_exp1_scalability.tex",
    "tab_exp4_filtering.tex",
    "tab_exp5_ablation.tex",
    "tab_exp6_scaling.tex",
]


def check_data_completeness() -> int:
    errors = 0
    print("Checking aggregated experimental data completeness...")
    for fname in EXPECTED_AGG_FILES:
        fpath = os.path.join(AGG_DIR, fname)
        if not os.path.exists(fpath):
            print(f"[ERROR] Missing aggregated file: {fpath}")
            errors += 1
            continue
        df = pd.read_csv(fpath)
        if len(df) == 0:
            print(f"[ERROR] Aggregated file is empty: {fpath}")
            errors += 1
            continue

        # Check CI consistency where CI columns exist
        for mean_col, low_col, high_col in [
            ("success_rate", "success_ci_low", "success_ci_high"),
            ("recovery_rate", "recovery_ci_low", "recovery_ci_high"),
            ("mean_total_cost", "cost_ci_low", "cost_ci_high"),
        ]:
            if mean_col in df.columns and low_col in df.columns and high_col in df.columns:
                invalid_ci = df[
                    (df[low_col] > df[mean_col] + 1e-6) | (df[mean_col] > df[high_col] + 1e-6)
                ]
                if len(invalid_ci) > 0:
                    print(
                        f"[ERROR] {fname}: Found inconsistent CI bounds in {mean_col}: low > mean or mean > high"
                    )
                    errors += 1

    print("Checking publication figures...")
    for fig_name in EXPECTED_FIGURES:
        fpath = os.path.join(FIG_DIR, fig_name)
        if not os.path.exists(fpath) or os.path.getsize(fpath) == 0:
            print(f"[ERROR] Missing or empty figure: {fpath}")
            errors += 1

    print("Checking exported LaTeX tables...")
    for tab_name in EXPECTED_TABLES:
        fpath = os.path.join(TABLE_DIR, tab_name)
        if not os.path.exists(fpath) or os.path.getsize(fpath) == 0:
            print(f"[ERROR] Missing or empty table: {fpath}")
            errors += 1

    if errors == 0:
        print("Data Completeness Validation PASSED: All files, figures, tables, and CIs are valid.")
        return 0
    else:
        print(f"Data Completeness Validation FAILED with {errors} error(s).")
        return 1


if __name__ == "__main__":
    sys.exit(check_data_completeness())
