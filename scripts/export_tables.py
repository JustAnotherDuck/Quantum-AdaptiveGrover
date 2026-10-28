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
        succ_str = f"{row['success_rate']:.2f} [{row['success_ci_low']:.2f}, {row['success_ci_high']:.2f}]"
        cost_str = f"{row['mean_total_cost']:.1f}"
        depth_str = f"{int(row['mean_depth'])}"
        speedup_str = f"{row['speedup_over_classical']:.2f}\\times"
        latex.append(
            f"{int(row['key_size'])} & {row['strategy']} & {succ_str} & {cost_str} & {depth_str} & {speedup_str} \\\\"
        )

    latex.extend([
        "\\hline",
        "\\end{tabular}",
        "\\end{table}",
    ])

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

    latex.extend([
        "\\hline",
        "\\end{tabular}",
        "\\end{table}",
    ])

    with open(os.path.join(TABLE_DIR, "tab_exp5_ablation.tex"), "w") as f:
        f.write("\n".join(latex) + "\n")


def export_exp6_table() -> None:
    path = os.path.join(AGG_DIR, "exp6_scaling_agg.csv")
    if not os.path.exists(path):
        return
    df = pd.read_csv(path)

    latex = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Reversible SPN Circuit Resource Scaling (Mode B). Asterisk (*) indicates extrapolated values.}",
        "\\label{tab:exp6_scaling}",
        "\\begin{tabular}{rccccc}",
        "\\hline",
        "\\textbf{Key ($n$)} & \\textbf{Rounds} & \\textbf{Total Qubits} & \\textbf{Transpiled Depth} & \\textbf{2Q Gates (CX)} & \\textbf{Status} \\\\",
        "\\hline",
    ]

    for _, row in df.iterrows():
        status = "Extrapolated*" if row["is_extrapolated"] else "Measured"
        latex.append(
            f"{int(row['key_size'])} & {int(row['rounds'])} & {int(row['qubits_total'])} & {int(row['depth'])} & {int(row['two_qubit_gates'])} & {status} \\\\"
        )

    latex.extend([
        "\\hline",
        "\\end{tabular}",
        "\\end{table}",
    ])

    with open(os.path.join(TABLE_DIR, "tab_exp6_scaling.tex"), "w") as f:
        f.write("\n".join(latex) + "\n")


def main() -> None:
    os.makedirs(TABLE_DIR, exist_ok=True)
    print("Exporting LaTeX tables from aggregated data...")
    export_exp1_table()
    export_exp5_table()
    export_exp6_table()
    print(f"All tables saved to {TABLE_DIR}.")


if __name__ == "__main__":
    main()
