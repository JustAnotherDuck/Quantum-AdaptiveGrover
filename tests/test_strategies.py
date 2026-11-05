"""Tests for all search strategies and ablation switches."""

from agqca.filtering.constraints import PrefixConstraint
from agqca.strategies.adaptive import AdaptiveHybridStrategy
from agqca.strategies.base import SearchContext
from agqca.strategies.brute_force import ClassicalBruteForceStrategy
from agqca.strategies.noise_aware import NoiseAwareGroverStrategy
from agqca.strategies.null_control import RandomGuessNullControlStrategy
from agqca.strategies.shallow_restart import ShallowRestartStrategy
from agqca.strategies.standard import StandardGroverStrategy


def make_context(key_size: int = 3, target_key: int = 5, noise_level: float = 0.0) -> SearchContext:
    return SearchContext(
        key_size=key_size,
        target_key=target_key,
        plaintext=0x0,
        target_ciphertext=0x0,
        verify_fn=lambda k: k == target_key,
        noise_level=noise_level,
        shots_per_round=128,
        max_total_oracle_calls=5000,
        seed=42,
    )


def test_classical_brute_force_finds_key() -> None:
    """Verify classical brute force finds and verifies true key."""
    ctx = make_context(key_size=4, target_key=10)
    strat = ClassicalBruteForceStrategy()
    rec = strat.run(ctx)
    assert rec.is_verified
    assert rec.found_key == 10
    assert rec.classical_verify_cost > 0


def test_standard_grover_finds_key_noiseless() -> None:
    """Verify standard Grover finds key under zero noise."""
    ctx = make_context(key_size=3, target_key=6, noise_level=0.0)
    strat = StandardGroverStrategy()
    rec = strat.run(ctx)
    assert rec.is_verified
    assert rec.found_key == 6


def test_null_control_strategy() -> None:
    """Verify random-guessing null control evaluates under budget."""
    ctx = make_context(key_size=3, target_key=2, noise_level=0.0)
    strat = RandomGuessNullControlStrategy()
    rec = strat.run(ctx)
    assert rec.strategy_name == "Random Guess (Null Control)"
    assert rec.classical_verify_cost > 0
    assert rec.oracle_calls == 0
    if rec.is_verified:
        assert rec.found_key == 2


def test_noise_aware_grover_finds_key() -> None:
    """Verify noise-aware Grover finds key."""
    ctx = make_context(key_size=3, target_key=3, noise_level=0.02)
    strat = NoiseAwareGroverStrategy()
    rec = strat.run(ctx)
    assert rec.is_verified
    assert rec.found_key == 3


def test_shallow_restart_finds_key_noisy() -> None:
    """Verify shallow restart finds key under noise."""
    ctx = make_context(key_size=3, target_key=4, noise_level=0.05)
    strat = ShallowRestartStrategy()
    rec = strat.run(ctx)
    assert rec.is_verified
    assert rec.found_key == 4


def test_adaptive_hybrid_finds_key_with_filtering() -> None:
    """Verify full adaptive hybrid controller runs with filtering and returns verified key."""
    key_size = 4
    true_key = 0b1011  # 11
    # Add constraint that prefix is 0b10
    constraint = PrefixConstraint(key_size=key_size, prefix_bits=2, prefix_val=0b10)

    ctx = make_context(key_size=key_size, target_key=true_key, noise_level=0.02)
    strat = AdaptiveHybridStrategy(constraints=[constraint])
    rec = strat.run(ctx)

    assert rec.is_verified
    assert rec.found_key == true_key
    assert rec.classical_filter_cost > 0
    assert rec.extra_metadata["candidates_remaining"] == 4  # 16 / 4 = 4 remaining


def test_adaptive_ablations() -> None:
    """Verify all 4 ablation switches execute without error."""
    ctx = make_context(key_size=3, target_key=1, noise_level=0.01)

    for flag in ["no_filtering", "no_adaptivity", "no_noise_awareness", "no_restart"]:
        kwargs = {flag: True}
        strat = AdaptiveHybridStrategy(**kwargs)
        rec = strat.run(ctx)
        assert rec.found_key is not None or not rec.is_verified  # explicit result
