"""Unit and integration tests for FastAPI backend routes and assistant layer."""

import pytest
from fastapi.testclient import TestClient

from agqca.api.server import app

client = TestClient(app)


def test_health_endpoint() -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_overview_endpoint() -> None:
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert "project_name" in data
    assert "research_question" in data
    assert len(data["key_findings"]) >= 4
    assert "disclaimer" in data


def test_strategies_endpoint() -> None:
    res = client.get("/api/strategies")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    ids = [s["id"] for s in data]
    assert "adaptive_hybrid" in ids
    assert "standard_grover" in ids
    assert "null_control" in ids


def test_experiments_endpoint() -> None:
    res = client.get("/api/experiments?exp=all")
    assert res.status_code == 200
    data = res.json()
    assert "exp1" in data
    assert "exp2" in data
    assert "exp3" in data
    assert "exp4" in data
    assert "exp5" in data
    assert "exp6" in data
    assert len(data["exp1"]) > 0


def test_simulate_endpoint_adaptive() -> None:
    payload = {
        "strategy_name": "Adaptive Hybrid (Proposed)",
        "key_size": 3,
        "target_key": 5,
        "noise_level": 0.01,
        "shots_per_round": 64,
        "max_total_oracle_calls": 5000,
        "seed": 42,
    }
    res = client.post("/api/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["strategy_name"] == "Adaptive Hybrid (Proposed)"
    assert data["is_verified"] is True
    assert data["found_key"] == 5
    assert data["total_effective_cost"] > 0


def test_simulate_endpoint_standard() -> None:
    payload = {
        "strategy_name": "Standard Grover",
        "key_size": 3,
        "target_key": 2,
        "noise_level": 0.0,
        "shots_per_round": 64,
        "max_total_oracle_calls": 5000,
        "seed": 100,
    }
    res = client.post("/api/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_verified"] is True
    assert data["found_key"] == 2


def test_readiness_endpoint() -> None:
    payload = {
        "cipher": "AES-128",
        "physical_error_rate": 0.001,
        "code_threshold": 0.01,
    }
    res = client.post("/api/readiness", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["cipher"] == "AES-128"
    assert data["logical_qubits_required"] in [1785, 2953]
    assert data["circuit_survival_probability"] == 0.0
    assert "Infeasible on NISQ" in data["nisq_feasibility_verdict"]
    assert "Grassl" in data["literature_source"] or "Jaques" in data["literature_source"]


def test_circuits_endpoint() -> None:
    res = client.get("/api/circuits?key_size=4")
    assert res.status_code == 200
    data = res.json()
    assert "mode_a" in data
    assert "mode_b" in data
    assert data["mode_a"]["stats"]["depth"] > 0
    assert data["mode_b"]["stats"]["depth"] > 0


def test_assistant_chat_endpoint_offline() -> None:
    # Query regarding AES security
    payload = {
        "message": "Can quantum computers break AES-128 today?",
        "conversation_history": [],
        "confirmed_execution": False,
    }
    res = client.post("/api/assistant/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "secure against NISQ" in data["reply"]
    assert "safety_disclaimer" in data
    assert len(data["grounded_evidence"]) > 0


def test_assistant_chat_simulation_intent() -> None:
    # Query asking to run simulation
    payload = {
        "message": "Simulate standard Grover on 4 bits with 5% noise",
        "conversation_history": [],
        "confirmed_execution": False,
    }
    res = client.post("/api/assistant/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["extracted_config"] is not None
    assert data["extracted_config"]["key_size"] == 4
    assert pytest.approx(data["extracted_config"]["noise_level"], 0.001) == 0.05
    assert data["requires_confirmation"] is True


def test_simulate_endpoint_all_strategies() -> None:
    strategies = [
        "Classical Brute Force",
        "Random Guess (Null Control)",
        "Noise-Aware Grover",
        "Shallow + Restart",
    ]
    for strat in strategies:
        payload = {
            "strategy_name": strat,
            "key_size": 3,
            "target_key": 1,
            "noise_level": 0.0,
            "shots_per_round": 32,
            "max_total_oracle_calls": 5000,
            "seed": 42,
        }
        res = client.post("/api/simulate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["strategy_name"] == strat


def test_simulate_stream_endpoint() -> None:
    res = client.get("/api/simulate/stream?key_size=3&noise_level=0.01&prefix_bits=1&seed=42")
    assert res.status_code == 200
    assert "text/event-stream" in res.headers["content-type"]
    text = res.text
    assert "round_idx" in text or "start" in text


def test_readiness_endpoint_variants() -> None:
    for cipher in ["AES-192", "AES-256", "S-AES", "ToySPN"]:
        res = client.post("/api/readiness", json={"cipher": cipher, "physical_error_rate": 0.01})
        assert res.status_code == 200
        data = res.json()
        assert data["cipher"] == cipher
        assert "safety_disclaimer" in data


def test_assistant_chat_all_intents() -> None:
    # 1. Crossover query
    res = client.post(
        "/api/assistant/chat",
        json={"message": "What is the noise crossover threshold?", "conversation_history": []},
    )
    assert res.status_code == 200
    assert "crossover" in res.json()["reply"].lower()

    # 2. Filtering cost query
    res = client.post(
        "/api/assistant/chat",
        json={"message": "Explain the filtering cost baseline", "conversation_history": []},
    )
    assert res.status_code == 200
    assert "filter" in res.json()["reply"].lower()

    # 3. Methods query
    res = client.post(
        "/api/assistant/chat",
        json={"message": "What is the methodology and limitations?", "conversation_history": []},
    )
    assert res.status_code == 200
    assert "method" in res.json()["reply"].lower()

    # 4. Confirmed execution
    res = client.post(
        "/api/assistant/chat",
        json={
            "message": "Run Grover on 4 bits",
            "conversation_history": [],
            "confirmed_execution": True,
        },
    )
    assert res.status_code == 200
    assert "Executed" in res.json()["reply"]
