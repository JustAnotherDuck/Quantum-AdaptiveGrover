"""Command-Line Interface for AdaptiveGrover-QCA using Typer."""

import subprocess
import sys
from typing import Optional

import typer

from agqca.analyzer.literature import load_literature_database
from agqca.analyzer.readiness import ReadinessAnalyzer
from agqca.analyzer.report import (
    format_html_report,
    format_json_report,
    format_terminal_report,
)

app = typer.Typer(
    name="agqca",
    help="Adaptive and Noise-Aware Key Search for Practical Quantum Cryptanalysis CLI",
    add_completion=False,
)


@app.command()
def analyze(
    cipher: str = typer.Option("AES-128", "--cipher", "-c", help="Target cipher name"),
    key_size: int = typer.Option(128, "--key-size", "-k", help="Cipher key size in bits"),
    known_bits: int = typer.Option(0, "--known-bits", "-b", help="Known/filtered key bits"),
    noise: float = typer.Option(0.001, "--noise", "-n", help="Physical gate error rate"),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, html"
    ),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Save report to file"),
) -> None:
    """Evaluate cryptographic readiness of a cipher under quantum threat."""
    analyzer = ReadinessAnalyzer()
    res = analyzer.evaluate(
        cipher_name=cipher,
        key_size=key_size,
        known_bits=known_bits,
        noise_level=noise,
    )

    if output_format.lower() == "json":
        text = format_json_report(res)
    elif output_format.lower() == "html":
        text = format_html_report(res)
    else:
        text = format_terminal_report(res)

    if output_file:
        with open(output_file, "w") as f:
            f.write(text)
        typer.echo(f"Report saved to {output_file}")
    else:
        typer.echo(text)


@app.command()
def literature() -> None:
    """Display verified quantum cryptanalysis literature references."""
    records = load_literature_database(verified_only=True)
    typer.echo(f"\nLoaded {len(records)} verified literature reference(s):\n")
    for r in records:
        typer.echo(f"• {r.citation_str()}")
        typer.echo(
            f"  Logical Qubits: {r.logical_qubits:,} | Grover Iterations: {r.grover_iterations}"
        )
        typer.echo(f"  Notes: {r.notes}\n")


@app.command()
def reproduce(
    mode: str = typer.Option(
        "small", "--mode", "-m", help="Run mode: small (~5 min) or full (~20 min)"
    ),
) -> None:
    """Execute end-to-end experiment suite and regenerate all figures and tables."""
    typer.echo(f"Executing reproducible experiment suite in '{mode}' mode...")
    cmd = [sys.executable, "experiments/run_all.py", "--mode", mode]
    subprocess.run(cmd, check=True)

    typer.echo("Regenerating publication figures...")
    subprocess.run([sys.executable, "scripts/generate_figures.py"], check=True)

    typer.echo("Exporting LaTeX tables...")
    subprocess.run([sys.executable, "scripts/export_tables.py"], check=True)
    typer.echo("Done! Results saved in experiments/ and paper_support/.")


if __name__ == "__main__":
    app()
