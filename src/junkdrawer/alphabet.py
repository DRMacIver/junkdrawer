from functools import total_ordering


@total_ordering
class Alphabet(object):
    """Represents an alphabet of integers as a list of
    compressed ranges."""

    __slots__ = ("ranges", "__size")

    def __init__(self, contents):
        contents = [(i, i + 1) if isinstance(i, int) else i for i in contents]
        merged = []
        for u, v in sorted(contents):
            if u == v:
                continue
            if merged and merged[-1][-1] >= u:
                merged[-1][-1] = max(merged[-1][-1], v)
            else:
                merged.append([u, v])
        self.ranges = tuple(map(tuple, merged))
        self.__size = sum([v - u for u, v in self.ranges])

    def __repr__(self):
        return f"Alphabet({self.ranges})"

    def __eq__(self, other):
        if not isinstance(other, Alphabet):
            return NotImplemented
        return self.ranges == other.ranges

    def __lt__(self, other):
        if not isinstance(other, Alphabet):
            return NotImplemented

        for u, v in zip(self, other):
            if u < v:
                return True
            if u > v:
                return False
        return len(self) < len(other)

    def __hash__(self):
        return hash(self.ranges)

    def __iter__(self):
        for u, v in self.ranges:
            yield from range(u, v)

    def __len__(self):
        return self.__size

    def __getitem__(self, i):
        if not (-len(self) <= i < len(self)):
            raise IndexError(f"Index {i} out of range [{-len(self)}, len(self))")
        if i < 0:
            i += len(self)
        assert i >= 0
        for u, v in self.ranges:
            x = u + i
            if x < v:
                return x
            i -= v - u
        assert False
