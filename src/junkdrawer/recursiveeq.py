from collections.abc import Collection
from functools import singledispatch

import attr
from attr.exceptions import NotAnAttrsClassError


def recursive_eq(a, b):
    """Determines if a and b are equal in a way that handles
    recursive data correctly.
    
    This is currently loosely based on the naive union-find
    based approach described in "Adams, Michael D., and R.
    Kent Dybvig. "Efficient nondestructive equality checking
    for trees and graphs." Proceedings of the 13th ACM SIGPLAN
    international conference on Functional programming. 2008."
    (https://legacy.cs.indiana.edu/~dyb/pubs/equal.pdf).

    I could implement the full algorithm from that paper but
    I'm lazy and I haven't. Also I wanted to understand the
    union find version and it was easier to understand it
    by writing code than not.
    """

    # We maintain a union-find table mapping IDs to values.
    # We use this to implement equality by asserting the
    # equality of ``a`` and ``b``, following through all
    # of the implications, and if we never hit a
    # contradiction then they must be equivalent and thus
    # equal.
    table = {}

    # Initially we just assume that (a, b) are equal.
    stack = [(a, b)]

    def find(v):
        """Standard union/find lookup, specialised
        to the fact that we look up by reference
        equality."""
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
        if type(a) != type(b):
            return False
        if type(a) in PRIMITIVE_TYPES or type(b) in PRIMITIVE_TYPES:
            if a == b:
                continue
            else:
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

        # If two collections are to be equal then they must pairwise
        # be equal at their corresponding elements.
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
