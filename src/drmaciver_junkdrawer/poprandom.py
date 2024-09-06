from random import Random
from typing import Any


def pop_random(seq: Any, random: Random) -> Any:
    """Remove a single element, chosen uniformly at random, from
    seq and return it. Elements of seq are left in an arbitrary
    order."""
    # seq is morally a MutableSequence, but implementing the full
    # MutableSequence protocol is a pain and we mostly want to use
    # this with MaskedSequence.
    if not seq:
        raise IndexError(f"Pop from empty sequence {seq}")
    if len(seq) == 1:
        return seq.pop()
    i = random.randrange(0, len(seq))
    j = len(seq) - 1
    seq[i], seq[j] = seq[j], seq[i]
    return seq.pop()
