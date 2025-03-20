from fractions import Fraction

from drmaciver_junkdrawer.coin import Coin


class VoseAliasSampler:
    """Samples values from a weighted distribution using Vose's algorithm for
    the Alias Method.

    See http://www.keithschwarz.com/darts-dice-coins/ for details.

    """

    def __init__(self, weights):
        assert any(weights)
        assert all(w >= 0 for w in weights)
        weights = list(map(Fraction, weights))

        n = len(weights)

        total = sum(weights)

        weights = tuple(w / total for w in weights)

        self._alias = [None] * len(weights)
        probabilities = [Fraction(-1)] * len(weights)

        self._size = total

        small = []
        large = []

        ps = [w * n for w in weights]

        for i, p in enumerate(ps):
            if p < 1:
                small.append(i)
            else:
                large.append(i)

        while small and large:
            lesser = small.pop()
            greater = large.pop()
            assert ps[greater] >= 1 >= ps[lesser]
            probabilities[lesser] = ps[lesser]
            self._alias[lesser] = greater
            ps[greater] = (ps[lesser] + ps[greater]) - 1
            if ps[greater] < 1:
                small.append(greater)
            else:
                large.append(greater)
        for q in [small, large]:
            while q:
                greater = q.pop()
                probabilities[greater] = Fraction(1)
                self._alias[greater] = greater

        assert None not in self._alias
        assert Fraction(-1) not in probabilities

        self.__coins = [
            Coin(x.numerator, x.denominator - x.numerator) for x in probabilities
        ]

    @property
    def _probabilities(self):
        return [coin.probability for coin in self.__coins]

    def sample(self, random):
        i = random.randrange(0, len(self.__coins))

        if self.__coins[i].toss(random):
            return i
        else:
            return self._alias[i]

    def __repr__(self):
        return f"VoseAliasSampler({list(zip(range(len(self._probabilities)), self._probabilities, self._alias))!r})"
