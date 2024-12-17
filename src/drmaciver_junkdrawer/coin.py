from fractions import Fraction


class Coin:
    """Implements a weighted coin."""

    def __init__(self, positive: int, negative: int):
        """``positive`` and ``negative`` should be integers.
        This coin will return True with probability positive / (positive + negative),
        using O(1) expected bits.
        """
        validate_weight(positive, "positive")
        validate_weight(negative, "negative")
        if max(positive, negative) == 0:
            raise ValueError("At least one weight must be non-zero")
        self.trail = [(positive, negative)]

    @property
    def probability(self):
        return Fraction(self.trail[0][0], sum(self.trail[0]))

    def toss(self, random):
        """Return True with the appopriate probability."""
        i = 0
        while True:
            if i == len(self.trail):
                a, b = self.trail[-1]
                assert a != b

                if a > b:
                    # p = a / (a + b) >= half. We've removed
                    # half from that so p_next = (p - 1/2) / (p - 1/2 + 1 - p)
                    # = 2p - 1. i.e. 2a / (a + b) - 1 = (2a - a - b) / (a + b)
                    # = (a - b) / (a + b). So a_next = a - b and b_next =
                    # (a + b - (a - b)) = 2b.
                    self.trail.append((a - b, 2 * b))
                else:
                    self.trail.append((2 * a, b - a))
            a, b = self.trail[i]
            assert a >= 0
            assert b >= 0
            if a == b:
                return bool(random.getrandbits(1))
            if random.getrandbits(1):
                return a > b
            i += 1


def validate_weight(weight, name):
    if weight < 0:
        raise ValueError(f"Expected non-negative value for {name} but got {weight}")
