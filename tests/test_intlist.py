from hypothesis.stateful import (
    rule,
    invariant,
    RuleBasedStateMachine,
    initialize,
    Bundle,
)
from hypothesis import strategies as st
from drmaciver_junkdrawer.intlist import IntList
import pytest

from hypothesis import assume, given, strategies as st


indexes = st.runner().flatmap(
    lambda self: (
        st.integers(-len(self.model), len(self.model) - 1)
        if self.model
        else st.nothing()
    )
)


bitwidth = st.shared(st.integers(0, 128))

bounded_integer = bitwidth.flatmap(lambda n: st.integers(0, 2**n - 1))


class IntListStateMachine(RuleBasedStateMachine):
    values = Bundle("values")

    @initialize(values=st.lists(bounded_integer))
    def create_model(self, values):
        self.target = IntList(values)
        self.model = list(values)

    @rule(value=bounded_integer)
    def push(self, value):
        self.model.append(value)
        self.target.append(value)

    @rule(i=indexes)
    def delete(self, i):
        del self.model[i]
        del self.target[i]

    @rule(i=indexes, v=bounded_integer)
    def set(self, i, v):
        self.model[i] = v
        self.target[i] = v

    @rule(i=indexes, v=bounded_integer)
    def insert(self, i, v):
        self.model.insert(i, v)
        self.target.insert(i, v)

    @rule(v=values | st.integers())
    def count(self, v):
        assert self.target.count(v) == self.model.count(v)

    @invariant()
    def check_all(self):
        assert len(self.model) == len(self.target)
        for i in range(-len(self.model), len(self.model)):
            assert self.target[i] == self.model[i]


TestIntLists = IntListStateMachine.TestCase

non_neg_lists = st.lists(st.integers(min_value=0, max_value=2**63 - 1))


@given(non_neg_lists)
def test_intlist_is_equal_to_itself(ls):
    assert IntList(ls) == IntList(ls)


@given(non_neg_lists, non_neg_lists)
def test_distinct_int_lists_are_not_equal(x, y):
    assume(x != y)
    assert IntList(x) != IntList(y)


def test_basic_equality():
    x = IntList([1, 2, 3])
    assert x == x
    t = x != x
    assert not t
    assert x != "foo"

    s = x == "foo"
    assert not s


def test_error_on_invalid_value():
    with pytest.raises(ValueError):
        IntList([-1])


def test_extend_by_too_large():
    x = IntList()
    ls = [1, 10**6]
    x.extend(ls)
    assert list(x) == ls


def test_int_list_cannot_contain_negative():
    with pytest.raises(ValueError):
        IntList([-1])


def test_int_list_can_contain_arbitrary_size():
    n = 2**65
    assert list(IntList([n])) == [n]


def test_int_list_of_length():
    assert list(IntList.of_length(10)) == [0] * 10


def test_int_list_equality():
    ls = [1, 2, 3]
    x = IntList(ls)
    y = IntList(ls)

    assert ls != x
    assert x != ls
    assert not (x == ls)  # noqa
    assert x == x
    assert x == y


def test_int_list_extend():
    x = IntList.of_length(3)
    n = 2**64 - 1
    x.extend([n])
    assert list(x) == [0, 0, 0, n]


def test_int_list_slice():
    x = IntList([1, 2])
    assert x[:1] == IntList([1])
    assert x[0:2] == IntList([1, 2])
    assert x[1:] == IntList([2])


def test_int_list_del():
    x = IntList([1, 2])
    del x[0]
    assert x == IntList([2])


@given(st.lists(st.integers(min_value=0)))
def test_int_lists_can_contain_arbitrary_integers(ls):
    assert list(IntList(ls)) == ls


@given(st.lists(st.integers(min_value=0)))
def test_int_lists_can_contain_arbitrary_integers_incremental(ls):
    x = IntList()
    for v in ls:
        x.append(v)
    assert list(x) == ls


@given(st.lists(st.integers(min_value=0)))
def test_int_lists_can_contain_arbitrary_integers_extend(ls):
    x = IntList()
    x.extend(ls)
    assert list(x) == ls


@given(st.lists(st.integers(min_value=0)))
def test_int_lists_can_contain_arbitrary_integers_setitem(ls):
    x = IntList([0] * len(ls))
    for i, v in enumerate(ls):
        x[i] = v
    assert list(x) == ls


def test_intlist_upgrades_on_insert():
    x = IntList([0])
    x.insert(0, 2**64)
    assert x[0] == 2**64
