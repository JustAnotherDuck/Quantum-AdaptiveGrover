"""Tests for candidate filtering, constraints, and non-power-of-two state preparation."""

from hypothesis import given, settings
from hypothesis import strategies as st

from agqca.filtering.constraints import (
    CandidateFilter,
    ParityConstraint,
    PrefixConstraint,
    SuffixConstraint,
)
from agqca.filtering.superposition import FilteredSpaceMapper


def test_prefix_constraint() -> None:
    """Verify PrefixConstraint filtering behavior."""
    key_size = 6
    c = PrefixConstraint(key_size=key_size, prefix_bits=2, prefix_val=0b11)
    # Valid keys: 0b11xxxx (48 to 63)
    assert c.is_satisfied(0b110000)
    assert c.is_satisfied(0b111111)
    assert not c.is_satisfied(0b101111)
    assert not c.is_satisfied(0b001111)


def test_suffix_constraint() -> None:
    """Verify SuffixConstraint filtering behavior."""
    c = SuffixConstraint(suffix_bits=3, suffix_val=0b101)
    assert c.is_satisfied(0b000101)
    assert c.is_satisfied(0b111101)
    assert not c.is_satisfied(0b111000)


def test_parity_constraint() -> None:
    """Verify ParityConstraint filtering behavior."""
    c_even = ParityConstraint(even_parity=True)
    c_odd = ParityConstraint(even_parity=False)
    assert c_even.is_satisfied(0b0011)  # 2 ones -> even
    assert not c_even.is_satisfied(0b0111)  # 3 ones -> odd
    assert c_odd.is_satisfied(0b0111)


def test_safety_fallback_triggered() -> None:
    """Verify safety fallback triggers when filtering would wrongly discard true key."""
    key_size = 4
    true_key = 0b0010  # Prefix is 0b00
    # Impose a false prefix constraint requiring 0b11
    bad_constraint = PrefixConstraint(key_size=key_size, prefix_bits=2, prefix_val=0b11)

    filter_engine = CandidateFilter(
        key_size=key_size,
        constraints=[bad_constraint],
        allow_fallback=True,
    )
    result = filter_engine.filter_space(true_key=true_key)

    assert not result.is_safe
    assert result.fallback_used
    assert true_key in result.candidates
    assert len(result.candidates) == (1 << key_size)


@given(
    key_size=st.integers(min_value=3, max_value=6),
    prefix_val=st.integers(min_value=0, max_value=3),
)
@settings(max_examples=30)
def test_hypothesis_filter_never_loses_true_key_when_consistent(
    key_size: int, prefix_val: int
) -> None:
    """Property test: when constraint matches true key, true key is always in candidate set."""
    prefix_bits = 2
    shift = key_size - prefix_bits
    # Pick a random true key that has this prefix
    suffix = 1
    true_key = (prefix_val << shift) | suffix

    constraint = PrefixConstraint(key_size=key_size, prefix_bits=prefix_bits, prefix_val=prefix_val)
    engine = CandidateFilter(key_size=key_size, constraints=[constraint], allow_fallback=True)
    res = engine.filter_space(true_key=true_key)

    assert res.is_safe
    assert not res.fallback_used
    assert true_key in res.candidates


def test_non_power_of_two_space_mapper() -> None:
    """Verify FilteredSpaceMapper properly maps arbitrary non-power-of-two sets."""
    candidates = [3, 7, 11, 14, 19]  # 5 candidates -> requires ceil(log2(5)) = 3 qubits
    mapper = FilteredSpaceMapper(candidates)
    assert mapper.num_candidates == 5
    assert mapper.index_qubits == 3
    assert not mapper.is_power_of_two

    # Round trip mapping
    for i, c in enumerate(sorted(candidates)):
        assert mapper.candidate_to_index(c) == i
        assert mapper.index_to_candidate(i) == c

    # Circuit construction should not error
    qc = mapper.construct_state_prep_circuit()
    assert qc.num_qubits == 3
