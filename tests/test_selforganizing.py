from hypothesis.stateful import (
    Bundle,
    RuleBasedStateMachine,
    initialize,
    multiple,
    rule,
)
from drmaciver_junkdrawer.selforganizing import SelfOrganisingList, Element, NotFound
from hypothesis import given, settings, strategies as st
from typing import Callable, Self
import pytest


@st.composite
def list_and_element(draw):
    ls = draw(st.lists(st.integers(), min_size=1))
    v = draw(st.sampled_from(ls))
    return (ls, v)


def find_and_gather(
    ls: SelfOrganisingList[Element], test: Callable[[Element], bool]
) -> list[Element]:
    result = []

    def f(x):
        result.append(x)
        return test(x)

    try:
        ls.find(f)
    except NotFound:
        pass
    return result


def never(x):
    return False


@given(list_and_element())
def test_reorders_the_list(lsv):
    ls, v = lsv

    target = SelfOrganisingList(ls)
    t1 = find_and_gather(target, lambda x: x == v)
    assert t1[-1] == v
    t2 = find_and_gather(target, lambda x: x == v)
    assert t2 == [v]

    t3 = find_and_gather(target, never)

    assert len(t3) == len(ls)
    assert t3[0] == v


@given(st.lists(st.integers()))
def test_reorders_on_missing(ls):
    target = SelfOrganisingList(ls)
    with pytest.raises(NotFound):
        target.find(never)


def always(x):
    return True


def test_can_add_to_list():
    target: SelfOrganisingList[int] = SelfOrganisingList()
    target.add(1)
    assert target.find(always) == 1


def test_not_found_on_empty():
    target: SelfOrganisingList[int] = SelfOrganisingList()
    with pytest.raises(NotFound):
        target.find(always)


@settings(report_multiple_bugs=False)
class SelfOrganisingListMachine(RuleBasedStateMachine):
    values = Bundle("values")

    @initialize(values=st.lists(st.integers()), target=values)
    def initial_values(self, values):
        self.target = SelfOrganisingList(values)
        return multiple(*values)

    @rule(value=st.integers(), target=values)
    def add(self, value):
        self.target.add(value)
        return value

    @rule(value=values)
    def find_present(self, value):
        assert self.target.find(lambda x: x == value) == value

    @rule(value=st.integers())
    def find_possibly_absent(self, value):
        try:
            self.target.find(lambda x: x == value)
        except NotFound:
            pass


TestModel = SelfOrganisingListMachine.TestCase
