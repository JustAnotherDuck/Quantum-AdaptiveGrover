"""Report formatting routines for Quantum Readiness Analyzer (Terminal, JSON, HTML)."""

import json

from agqca.analyzer.readiness import ReadinessEvaluation


def format_terminal_report(eval_res: ReadinessEvaluation) -> str:
    """Format readiness evaluation as a formatted terminal text display."""
    lines = [
        "=" * 78,
        " QUANTUM CRYPTOGRAPHIC READINESS ANALYZER REPORT",
        "=" * 78,
        f" Target Cipher        : {eval_res.cipher_name}",
        f" Full Key Length      : {eval_res.key_size} bits",
        f" Effective Key Space  : {eval_res.effective_key_size} bits",
        f" Ideal Grover Queries : {eval_res.ideal_oracle_calls_str}",
        f" Risk Assessment      : Level {eval_res.quantum_risk_level}/5 - {eval_res.quantum_risk_label}",
        f" Estimated NISQ Depth : {eval_res.estimated_nisq_depth:.2e} gates",
        f" NISQ Survival Prob   : {eval_res.nisq_survival_probability:.2e}",
        "-" * 78,
        " FEASIBILITY VERDICT:",
        f"  {eval_res.feasibility_verdict}",
        "-" * 78,
    ]

    if eval_res.literature_estimates:
        lines.append(" VERIFIED LITERATURE ESTIMATES:")
        for lit in eval_res.literature_estimates:
            lines.append(f"  • {lit.citation_str()}")
            lines.append(
                f"    - Logical Qubits: {lit.logical_qubits:,} | T-Depth: {lit.t_depth or 'N/A'}"
            )
            lines.append(f"    - Notes: {lit.notes}")
        lines.append("-" * 78)

    lines.extend([
        " MANDATORY SAFETY & SCIENTIFIC DISCLAIMER:",
        f"  {eval_res.mandatory_disclaimer}",
        "=" * 78,
    ])
    return "\n".join(lines)


def format_json_report(eval_res: ReadinessEvaluation, indent: int = 2) -> str:
    """Format readiness evaluation as JSON string."""
    return json.dumps(eval_res.to_dict(), indent=indent)


def format_html_report(eval_res: ReadinessEvaluation) -> str:
    """Format readiness evaluation as a clean, printable HTML document."""
    lit_html = ""
    for lit in eval_res.literature_estimates:
        lit_html += f"""
        <div class="literature-item">
            <strong>{lit.paper_title}</strong> ({lit.year})<br>
            <em>{", ".join(lit.authors)}</em> — <code>{lit.venue}</code> (DOI: <a href="https://doi.org/{lit.doi}">{lit.doi}</a>)<br>
            Logical Qubits: <strong>{lit.logical_qubits:,}</strong> | T-Depth: <strong>{lit.t_depth or 'N/A'}</strong><br>
            <span class="notes">{lit.notes}</span>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Quantum Readiness Report - {eval_res.cipher_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; color: #222; }}
        h1 {{ color: #1b9e77; border-bottom: 2px solid #1b9e77; padding-bottom: 8px; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 14px; }}
        .risk-1 {{ background: #e6f4ea; color: #137333; }}
        .risk-5 {{ background: #fce8e6; color: #c5221f; }}
        .card {{ background: #f8f9fa; border-left: 4px solid #1b9e77; padding: 16px; margin: 20px 0; }}
        .disclaimer {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 20px 0; font-size: 13px; }}
        .literature-item {{ margin: 12px 0; padding: 8px; border-bottom: 1px solid #eee; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
        th {{ background: #f1f3f4; }}
    </style>
</head>
<body>
    <h1>Quantum Cryptographic Readiness Evaluation</h1>
    <p>Target: <strong>{eval_res.cipher_name}</strong> ({eval_res.key_size}-bit key)</p>

    <div class="disclaimer">
        <strong>CRITICAL NOTICE:</strong> {eval_res.mandatory_disclaimer}
    </div>

    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Cipher Analyzed</td><td>{eval_res.cipher_name}</td></tr>
        <tr><td>Key Length</td><td>{eval_res.key_size} bits</td></tr>
        <tr><td>Effective Key Length (post-constraints)</td><td>{eval_res.effective_key_size} bits</td></tr>
        <tr><td>Ideal Grover Queries</td><td>{eval_res.ideal_oracle_calls_str}</td></tr>
        <tr><td>Estimated Circuit Depth</td><td>{eval_res.estimated_nisq_depth:.2e} gates</td></tr>
        <tr><td>NISQ Survival Probability</td><td>{eval_res.nisq_survival_probability:.2e}</td></tr>
        <tr><td>Quantum Risk Level</td><td>Level {eval_res.quantum_risk_level} / 5</td></tr>
    </table>

    <div class="card">
        <h3>Feasibility Verdict</h3>
        <p>{eval_res.feasibility_verdict}</p>
    </div>

    <h3>Verified Literature Quantum Resource Estimates</h3>
    {lit_html if lit_html else "<p>No specific literature entries match this reduced configuration.</p>"}
</body>
</html>
"""
    return html
