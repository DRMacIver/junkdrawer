from fractions import Fraction
from random import Random
from hypothesis import given, strategies as st, example

from drmaciver_junkdrawer.aliassampler import VoseAliasSampler

weightings = st.lists(st.fractions(min_value=0) | st.integers(min_value=0), min_size=1).filter(lambda x: sum(x) > 0)

@example([Fraction(1)])
@example(weights=[1])
@example(weights=[0, 1])
@example(weights=[0, 1, 1]).via("discovered failure")
@given(weightings)
def test_alias_sampler_gives_correct_probabilities(weights):
    total = sum(weights)
    true_probabilities = [Fraction(x) / total for x in weights]

    sampler = VoseAliasSampler(weights)

    calculated_probabilities = [Fraction(0)] * len(weights)

    for i in range(len(weights)):
        p = sampler._probabilities[i]
        assert type(p) is Fraction
        calculated_probabilities[i] += p
        calculated_probabilities[sampler._alias[i]] += (1 - p)
    for i in range(len(weights)):
        calculated_probabilities[i] /= len(weights)

    assert true_probabilities == calculated_probabilities


@given(
    weights=weightings,
    seed=st.integers(),
    repetitions=st.integers(0, 100)
)
@example(
    weights=[1, 2],
    seed=1,
    repetitions=1,
)
@example(
    weights=[1],
    seed=0,
    repetitions=1,
)
@example(weights=[0, 1], seed=1, repetitions=1)
def test_alias_sampler_does_not_sample_zero_weights(weights, seed, repetitions):
    sampler = VoseAliasSampler(weights)
    random = Random(seed)

    for _ in range(repetitions):
        i = sampler.sample(random)
        assert weights[i] > 0
