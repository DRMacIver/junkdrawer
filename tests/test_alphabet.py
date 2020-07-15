import pytest

from hypothesis import given, settings, strategies as st
from junkdrawer.alphabet import Alphabet


@st.composite
def ranges(draw):
    m = draw(st.integers())
    n = draw(st.integers(m, m + 10))
    return (m, n)


contents = st.lists(st.integers() | ranges())


@given(contents)
def test_alphabet_gives_right_values(contents):
    alphabet = Alphabet(contents)

    values = set()
    for i in contents:
        if isinstance(i, int):
            values.add(i)
        else:
            values.update(range(*i))
    values = sorted(values)

    assert len(values) == len(alphabet)
    assert list(alphabet) == values
    for i, v in enumerate(values):
        assert alphabet[i] == v


@given(contents)
def test_alphabet_equals_itself(contents):
    x = Alphabet(contents)
    assert x == x
    y = Alphabet(contents)
    assert x == y

    assert hash(x) == hash(y)


@given(contents)
def test_alphabet_only_equals_other_alphabets(contents):
    assert Alphabet(contents) != contents
    b = Alphabet(contents) == contents
    assert not b


def test_out_of_range():
    alpha = Alphabet([1])
    assert alpha[0] == 1
    assert alpha[-1] == 1
    with pytest.raises(IndexError):
        alpha[1]
    with pytest.raises(IndexError):
        alpha[-2]


alphabets = contents.map(Alphabet)


@given(alphabets, alphabets)
def test_sorts_as_contents(x, y):
    assert (x <= y) == (list(x) <= list(y))


def test_not_comparable_to_other_types():
    x = [1]
    y = Alphabet(x)

    with pytest.raises(TypeError):
        x < y
