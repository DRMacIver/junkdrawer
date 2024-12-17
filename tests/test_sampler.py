from random import Random

import pytest

from hypothesis import assume, example, given, settings, strategies as st
from drmaciver_junkdrawer.sampler import TreeSampler


@given(
    st.dictionaries(st.text(), st.integers(min_value=0)),
    st.randoms(use_true_random=False),
)
def test_samples_only_non_zero(weights, rnd):
    assume(sum(weights.values()) > 0)
    sampler = TreeSampler(weights)

    assert weights[sampler.sample(rnd)] > 0


@given(
    st.lists(st.tuples(st.integers(0, 5), st.integers(min_value=0))),
    st.randoms(use_true_random=False, note_method_calls=True),
)
def test_samples_only_non_zero_while_updating(weights, rnd):
    sampler = TreeSampler()

    model = {}

    for k, v in weights:
        model[k] = v
        sampler[k] = v
        if v > 0:
            assert sampler[k] == model[k]
        else:
            assert k not in sampler
        if sum(model.values()) > 0:
            s = sampler.sample(rnd)
            assert model[s] > 0


@given(st.randoms(use_true_random=True))
def test_sample_from_single(rnd):
    sampler = TreeSampler()
    sampler[0] = 1
    assert sampler.sample(rnd) == 0


@given(
    st.randoms(use_true_random=False),
    st.data(),
    st.dictionaries(st.text(), st.integers(min_value=1), min_size=2),
)
def test_can_delete_an_item(rnd, data, weights):
    keys = sorted(weights)
    sampler = TreeSampler(weights)
    key = data.draw(st.sampled_from(keys))
    del sampler[key]
    assert sampler.sample(rnd) != key


def test_empty_sample_is_error():
    rnd = Random(0)
    sampler = TreeSampler()
    with pytest.raises(IndexError):
        sampler.sample(rnd)
    sampler[1] = 1
    sampler[1] = 0
    with pytest.raises(IndexError):
        sampler.sample(rnd)


def test_non_empty_sampler_is_truthy():
    sampler = TreeSampler()
    assert not sampler
    sampler[0] = 1
    assert sampler
    del sampler[0]
    assert not sampler


@given(st.dictionaries(st.text(), st.integers(min_value=1)))
def test_iterates_as_dict(weights):
    sampler = TreeSampler(weights)
    assert sorted(sampler) == sorted(weights)
    assert sorted(sampler.items()) == sorted(weights.items())


def test_skips_zero_weights():
    sampler = TreeSampler({1: 1, 2: 0, 3: 1})
    assert sorted(sampler) == [1, 3]


def test_zero_weights_are_absent():
    sampler = TreeSampler()
    sampler[1] = 2
    assert sampler[1] == 2
    sampler[1] = 0
    with pytest.raises(KeyError):
        sampler[1]


def test_items_not_set_are_not_in_sampler():
    sampler = TreeSampler()
    assert 3 not in sampler


def test_heavily_samples_from_biggest_child():
    rnd = Random()
    sampler = TreeSampler()
    for i in range(10):
        sampler[i] = 1

    sampler[10] = 1000

    total = 1000
    count = 0
    for _ in range(total):
        if sampler.sample(rnd) == 10:
            count += 1
    assert count / total >= 0.9


def test_heavily_samples_from_biggest_child_with_floats():
    rnd = Random()
    sampler = TreeSampler()
    for i in range(10):
        sampler[i] = 1.0

    sampler[10] = 1000.0

    total = 1000
    count = 0
    for _ in range(total):
        if sampler.sample(rnd) == 10:
            count += 1
    assert count / total >= 0.9
