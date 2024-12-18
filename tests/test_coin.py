from fractions import Fraction
from random import Random

import pytest

from hypothesis import assume, example, given, settings, strategies as st
from drmaciver_junkdrawer.coin import Coin


@example(1, 3, Random(0))
@example(1, 2, Random(0))
@settings(report_multiple_bugs=False)
@given(
    st.integers(min_value=0),
    st.integers(min_value=0),
    st.randoms(use_true_random=False),
)
def test_coins_have_right_probability_calculations(m, n, rnd):
    assume(min(m, n) > 0)
    coin = Coin(m, n)

    for _ in range(10):
        coin.toss(rnd)

    desired_p = Fraction(m, n + m)

    p = Fraction(0)

    for i, (a, b) in enumerate(coin.trail):
        if a >= b:
            p += Fraction(1, 2 ** (i + 1))

    remainder = 1 - Fraction(1, 2 ** len(coin.trail))

    assert p <= desired_p <= p + remainder


def test_validates_weights():
    with pytest.raises(ValueError):
        Coin(-1, 1)
    with pytest.raises(ValueError):
        Coin(0, 0)


def test_probability_of_float_coin_is_fraction():
    assert Coin(0.5, 0.5).probability == Fraction(1, 2)
