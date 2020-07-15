from collections.abc import Collection
from functools import singledispatch

import attr
from attr.exceptions import NotAnAttrsClassError


def recursive_eq(a, b):
    """Determines if a and b are equal in a way that handles
    recursive data correctly."""
    table = {}
    stack = [(a, b)]

    def find(v):
        trail = [id(v)]
        while True:
            v_next = table.get(id(v), v)
            if v_next is v:
                break
            else:
                trail.append(id(v_next))
                v = v_next
        for i in trail:
            table[i] = v
        return v

    while stack:
        a, b = stack.pop()
        if a is b:
            continue
        if type(a) in PRIMITIVE_TYPES or type(b) in PRIMITIVE_TYPES:
            if a != b:
                return False
        if type(a) != type(b):
            return False
        a = find(a)
        b = find(b)
        if a is b:
            continue
        table[id(b)] = a
        ac = as_collection(a)
        bc = as_collection(b)
        if len(ac) != len(bc):
            return False
        stack.extend(zip(ac, bc))
    return True


PRIMITIVE_TYPES = {
    bool,
    int,
    float,
    bytes,
    str,
    bytearray,
    complex,
    type(None),
}


@singledispatch
def as_collection(v):
    if isinstance(v, Collection):
        return v
    try:
        return attr.astuple(v, recurse=False)
    except NotAnAttrsClassError:
        raise NotImplementedError() from None
