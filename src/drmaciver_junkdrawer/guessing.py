def find_integer(f):
    """Finds a (hopefully large) integer n such that f(n) is True and f(n + 1)
    is False. Runs in O(log(n)).

    f(0) is assumed to be True and will not be checked. May not terminate unless
    f(n) is False for all sufficiently large n.
    """
    # We first do a linear scan over the small numbers and only start to do
    # anything intelligent if f(4) is true. This is because it's very hard to
    # win big when the result is small. If the result is 0 and we try 2 first
    # then we've done twice as much work as we needed to!
    for i in range(1, 5):
        if not f(i):
            return i - 1

    # We now know that f(4) is true. We want to find some number for which
    # f(n) is *not* true.
    # lo is the largest number for which we know that f(lo) is true.
    lo = 4

    # Exponential probe upwards until we find some value hi such that f(hi)
    # is not true. Subsequently we maintain the invariant that hi is the
    # smallest number for which we know that f(hi) is not true.
    hi = 5
    while f(hi):
        lo = hi
        hi *= 2

    # Now binary search until lo + 1 = hi. At that point we have f(lo) and not
    # f(lo + 1), as desired..
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if f(mid):
            lo = mid
        else:
            hi = mid
    return lo


def binary_search_with_guess(f, lo, hi, guess=None):
    """Find n such that lo <= n < hi and f(lo) == f(n) != f(n + 1). It is
    assumed that f(hi) != f(lo) and will not be checked.

    ``guess`` is a prediction of the value of n and defaults to lo.
    This function runs in O(log(abs(guess - n))).
    """

    if guess is None:
        guess = lo

    good = f(lo)

    if f(guess) == good:
        # Our guess was equivalent to lo, so we want to find some point after it.
        k = find_integer(lambda k: guess + k < hi and f(guess + k) == good)
        return guess + k
    else:
        # Our guess was equivalent to hi , so we want to find some point before it.
        k = find_integer(lambda k: guess - k >= lo and f(guess - k) != good)
        return guess - k - 1
