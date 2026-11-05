"""Export aggregated experimental results as LaTeX-ready tables."""

import os

import pandas as pd

AGG_DIR = "experiments/aggregated"
TABLE_DIR = "paper_support/tables"


def export_exp1_table() -> None:
    path = os.path.join(AGG_DIR, "exp1_scalability_agg.csv")
    if not os.path.exists(path):
        return
    df = pd.read_csv(path)

    latex = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Scalability Baseline vs Key Size (Exp 1: Noise = 2\\%). Values report mean [95\\% CI].}",
        "\\label{tab:exp1_scalability}",
        "\\begin{tabular}{llrccc}",
        "\\hline",
        "\\textbf{Key ($n$)} & \\textbf{Strategy} & \\textbf{Success Rate} & \\textbf{Total Cost} & \\textbf{Depth} & \\textbf{Speedup} \\\\",
        "\\hline",
    ]

    for _, row in df.iterrows():
        succ_str = (
            f"{row['success_rate']:.2f} [{row['success_ci_low']:.2f}, {row['success_ci_high']:.2f}]"
        )
        cost_str = f"{row['mean_total_cost']:.1f}"
        depth_str = f"{int(row['mean_depth'])}"
        speedup_str = f"{row['speedup_over_classical']:.2f}\\times"
        latex.append(
            f"{int(row['key_size'])} & {row['strategy']} & {succ_str} & {cost_str} & {depth_str} & {speedup_str} \\\\"
        )

    latex.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\end{table}",
        ]
    )

    with open(os.path.join(TABLE_DIR, "tab_exp1_scalability.tex"), "w") as f:
        f.write("\n".join(latex) + "\n")


def export_exp5_table() -> None:
    path = os.path.join(AGG_DIR, "exp5_ablation_agg.csv")
    if not os.path.exists(path):
        return
    df = pd.read_csv(path)

    latex = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Framework Ablation Study (Exp 5: $n=4$, Noise = 3\\%).}",
        "\\label{tab:exp5_ablation}",
        "\\begin{tabular}{lccc}",
        "\\hline",
        "\\textbf{Configuration} & \\textbf{Recovery Rate [95\\% CI]} & \\textbf{Mean Total Cost} & \\textbf{Depth} \\\\",
        "\\hline",
    ]

    for _, row in df.iterrows():
        succ_str = f"{row['recovery_rate']:.2f} [{row['recovery_ci_low']:.2f}, {row['recovery_ci_high']:.2f}]"
        latex.append(
            f"{row['configuration']} & {succ_str} & {row['mean_total_cost']:.1f} & {int(row['mean_depth'])} \\\\"
        )

    latex.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\end{table}",
        ]
    )

    with open(os.path.join(TABLE_DIR, "tab_exp5_ablation.tex"), "w") as f:
        f.write("\n".join(latex) + "\n")


def export_exp4_table() -> None:
    path = os.path.join(AGG_DIR, "exp4_filtering_agg.csv")
    if not os.path.exists(path):
        return
    df = pd.read_csv(path)

    latex = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Candidate Filtering Baseline Decomposition (Exp 4). Separates classical search-space reduction from quantum gain.}",
        "\\label{tab:exp4_filtering}",
        "\\begin{tabular}{lcccccc}",
        "\\hline",
        "\\textbf{Profile} & \\textbf{Reduction ($N/N'$)} & \\textbf{Unfilt. Cost} & \\textbf{Filt. Classical} & \\textbf{Filt. Grover} & \\textbf{Quantum Gain} & \\textbf{Total Gain} \\\\",
        "\\hline",
    ]

    for _, row in df.iterrows():
        p_name = row["profile"]
        red_str = f"{row['filtering_reduction_factor']:.1f}\\times"
        unfilt_str = f"{row['unfiltered_classical_cost']:.1f}"
        filtc_str = f"{row['filtered_classical_cost']:.1f}"
        q_str = f"{row['filtered_grover_cost']:.1f}"
        qgain_str = f"{row['quantum_specific_speedup']:.2f}\\times"
        totgain_str = f"{row['end_to_end_speedup']:.2f}\\times"
        latex.append(
            f"{p_name} & {red_str} & {unfilt_str} & {filtc_str} & {q_str} & {qgain_str} & {totgain_str} \\\\"
        )

    latex.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\end{table}",
        ]
    )

    with open(os.path.join(TABLE_DIR, "tab_exp4_filtering.tex"), "w") as f:
        f.write("\n".join(latex) + "\n")


def export_exp6_table() -> None:
    path = os.path.join(AGG_DIR, "exp6_scaling_agg.csv")
    if not os.path.exists(path):
        return
    df = pd.read_csv(path)

    latex = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Reversible SPN Circuit Resource Scaling (Mode B Measured $n \\le 16$) and Published Literature Reference.}",
        "\\label{tab:exp6_scaling}",
        "\\begin{tabular}{lccccc}",
        "\\hline",
        "\\textbf{Target} & \\textbf{Key ($n$)} & \\textbf{Qubits} & \\textbf{Depth} & \\textbf{2Q Gates (CX)} & \\textbf{Type} \\\\",
        "\\hline",
    ]

    for _, row in df.iterrows():
        t_type = "Measured" if row["is_measured"] else "Published Literature"
        latex.append(
            f"{row['target']} & {int(row['key_size'])} & {int(row['qubits_total'])} & {int(row['depth'])} & {int(row['two_qubit_gates'])} & {t_type} \\\\"
        )

    latex.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\end{table}",
        ]
    )

    with open(os.path.join(TABLE_DIR, "tab_exp6_scaling.tex"), "w") as f:
        f.write("\n".join(latex) + "\n")


def main() -> None:
    os.makedirs(TABLE_DIR, exist_ok=True)
    print("Exporting LaTeX tables from aggregated data...")
    export_exp1_table()
    export_exp4_table()
    export_exp5_table()
    export_exp6_table()
    print(f"All tables saved to {TABLE_DIR}.")


if __name__ == "__main__":
    main()
