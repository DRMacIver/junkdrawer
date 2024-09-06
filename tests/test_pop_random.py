from hypothesis import given, strategies as st
from drmaciver_junkdrawer.poprandom import pop_random
from drmaciver_junkdrawer.maskedsequence import MaskedSequence
import pytest
from random import Random


@given(
    values=st.lists(st.integers(), min_size=1),
    random=st.randoms(use_true_random=False, note_method_calls=True),
    use_masked_sequence=st.booleans(),
)
def test_pop_random_down_to_empty(values, random, use_masked_sequence):
    if use_masked_sequence:
        target = MaskedSequence(values)
    else:
        target = list(values)
    result = []
    while target:
        assert len(target) + len(result) == len(values)
        result.append(pop_random(target, random))

    assert sorted(result) == sorted(values)


def test_fails_on_empty():
    with pytest.raises(IndexError):
        pop_random((), Random(0))
