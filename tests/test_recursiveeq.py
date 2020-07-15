import attr
import pytest

from junkdrawer.recursiveeq import recursive_eq


def test_equal_self_referenced_lists():
    x = []
    x.append(x)
    y = []
    y.append(y)

    assert recursive_eq(x, y)


def test_equal_mutually_referenced_lists():
    x = []
    y = []
    x.append(y)
    y.append(x)

    assert recursive_eq(x, y)


def test_differing_structures():
    x = [[]]
    x[0].append(x)
    y = []
    y.append(y)
    assert recursive_eq(x, y)


def test_unequal_self_referenced_lists_with_values():
    x = [1]
    x.append(x)
    y = [2]
    y.append(y)

    assert not recursive_eq(x, y)


def test_equal_self_referenced_lists_with_values():
    x = [1]
    x.append(x)
    y = [1]
    y.append(y)

    assert recursive_eq(x, y)


def test_equal_self_referenced_lists_with_values_of_different_type():
    x = [1]
    x.append(x)
    y = [1]
    y.append(y)

    assert recursive_eq(x, y)


def test_equal_primitives():
    x = bytes(1000)
    y = bytes(bytearray(x))
    assert x is not y

    assert recursive_eq([x], [y])


def test_equal_mispatch_compound_and_primitive():
    assert not recursive_eq([[], []], [(), ()])


def test_different_lengths():
    assert not recursive_eq((), ((),))


@attr.s()
class Foo(object):
    x = attr.ib()
    y = attr.ib(default=None)


@attr.s()
class Bar(object):
    x = attr.ib()
    y = attr.ib(default=None)


def test_recurse_through_attrs():
    a = Foo(1)
    a.y = a
    b = Foo(1)
    b.y = a

    assert recursive_eq(a, b)


def test_recurse_through_attrs_different_values():
    a = Foo(1)
    a.y = a
    b = Foo(2)
    b.y = b

    assert not recursive_eq(a, b)


def test_different_attrs_classes():
    a = Foo(1)
    a.y = a
    b = Bar(1)
    b.y = b

    assert not recursive_eq(a, b)


class Baz(object):
    pass


def test_needs_implementation():
    x = Baz()
    y = Baz()
    with pytest.raises(NotImplementedError):
        recursive_eq(x, y)
