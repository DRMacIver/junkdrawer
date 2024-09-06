from drmaciver_junkdrawer.selforganizing import SelfOrganisingList, Element, NotFound
from hypothesis import given, strategies as st
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


@given(list_and_element())
def test_reorders_the_list(lsv):
    ls, v = lsv

    target = SelfOrganisingList(ls)
    t1 = find_and_gather(target, lambda x: x == v)
    assert t1[-1] == v
    t2 = find_and_gather(target, lambda x: x == v)
    assert t2 == [v]

    t3 = find_and_gather(target, lambda x: False)

    assert len(t3) == len(ls)
    assert t3[0] == v


@given(st.lists(st.integers()))
def test_reorders_on_missing(ls):
    target = SelfOrganisingList(ls)
    with pytest.raises(NotFound):
        target.find(lambda x: False)


def test_can_add_to_list():
    target: SelfOrganisingList[int] = SelfOrganisingList()
    target.add(1)
    assert target.find(lambda x: True) == 1
