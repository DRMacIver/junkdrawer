from hypothesis import given, strategies as st, assume
from bisect import bisect_left
from drmaciver_junkdrawer.guessing import binary_search_with_guess, find_integer


@st.composite
def guess_targets(draw):
    switchovers = draw(st.lists(st.integers(min_value=0), min_size=1, unique=True))
    switchovers.sort()
    if len(switchovers) % 2 == 0:
        switchovers.pop()

    def result(n):
        i = bisect_left(switchovers, n)
        return i % 2 == 0

    result.__name__ = f"switchover({switchovers})"
    result.switchovers = switchovers  # type: ignore

    assert result(0) is True
    assert result(switchovers[-1] + 1) is False

    return result


@given(guess_targets())
def test_can_find_large_integers(f):

    i = find_integer(f)

    assert f(i)
    assert not f(i + 1)
    assert i >= f.switchovers[0]


triple = (
    st.lists(st.integers(), min_size=3, max_size=3)
    .map(sorted)
    .filter(lambda x: x[0] != x[-1])
    .map(tuple)
)


@given(guess_targets(), triple)
def test_can_binary_search_with_guess(f, t):
    lo, guess, hi = t
    assume(f(lo) != f(hi))

    i = binary_search_with_guess(f=f, lo=lo, guess=guess, hi=hi)
    assert f(i) == f(lo)
    assert f(i + 1) == f(hi)


@given(guess_targets(), st.integers(), st.integers())
def test_can_binary_search_with_guess_at_lo(f, lo, hi):
    lo, hi = sorted((lo, hi))
    assume(f(lo) != f(hi))

    i = binary_search_with_guess(f=f, lo=lo, hi=hi)
    assert f(i) == f(lo)
    assert f(i + 1) == f(hi)
