"""Unit tests for Quantum Readiness Analyzer and Literature Database."""

import json

from agqca.analyzer.literature import load_literature_database
from agqca.analyzer.readiness import SAFETY_DISCLAIMER, ReadinessAnalyzer
from agqca.analyzer.report import (
    format_html_report,
    format_json_report,
    format_terminal_report,
)


def test_literature_database_loads_verified_records() -> None:
    """Verify literature database loads verified records with required fields."""
    records = load_literature_database(verified_only=True)
    assert len(records) >= 3
    for r in records:
        assert r.verified
        assert r.logical_qubits > 0
        assert r.year >= 2016
        assert len(r.authors) > 0
        assert r.doi != ""


def test_readiness_evaluation_aes128() -> None:
    """Verify AES-128 readiness evaluation flags NISQ infeasibility and includes disclaimer."""
    analyzer = ReadinessAnalyzer()
    res = analyzer.evaluate("AES-128", 128)

    assert res.quantum_risk_level == 1
    assert "INFEASIBLE" in res.feasibility_verdict
    assert SAFETY_DISCLAIMER in res.mandatory_disclaimer
    assert len(res.literature_estimates) >= 1


def test_readiness_evaluation_saes_reduced() -> None:
    """Verify S-AES 16-bit evaluation is classified as feasible in simulation."""
    analyzer = ReadinessAnalyzer()
    res = analyzer.evaluate("S-AES", 16)

    assert res.quantum_risk_level == 5
    assert "FEASIBLE" in res.feasibility_verdict
    assert res.ideal_iterations > 1


def test_all_report_formats_contain_disclaimer() -> None:
    """Non-negotiable rule 2 check: disclaimer must be present in table, JSON, and HTML."""
    analyzer = ReadinessAnalyzer()
    res = analyzer.evaluate("ToySPN", 16)

    txt = format_terminal_report(res)
    assert "EXPERIMENTAL ESTIMATE ONLY" in txt

    js = format_json_report(res)
    data = json.loads(js)
    assert "EXPERIMENTAL ESTIMATE ONLY" in data["mandatory_disclaimer"]

    html = format_html_report(res)
    assert "EXPERIMENTAL ESTIMATE ONLY" in html


def test_readiness_intermediate_sizes() -> None:
    analyzer = ReadinessAnalyzer()
    res24 = analyzer.evaluate("Custom-24", 24)
    assert res24.quantum_risk_level == 4
    assert "MARGINALLY FEASIBLE" in res24.feasibility_verdict

    res48 = analyzer.evaluate("Custom-48", 48)
    assert res48.quantum_risk_level == 3
    assert "MEDIUM RISK" in res48.quantum_risk_label


def test_literature_database_all_records() -> None:
    records = load_literature_database(verified_only=False)
    assert len(records) >= 4
    for r in records:
        assert r.citation_str() != ""
