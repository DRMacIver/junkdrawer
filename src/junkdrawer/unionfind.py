from collections import defaultdict


class UnionFind(object):
    """Implements a data structure for maintaining a
    partition into joint sets using the union find
    algorithm. Initially everything is assumed to be
    in a singleton set, and calls to merge will
    link two sets so they are in the same partition."""

    def __init__(self, partitions=()):
        self.table = {}
        for cls in partitions:
            self.merge_all(cls)

    def find(self, value):
        """Find a canonical representative for ``value``
        according to the current merges."""
        try:
            if self.table[value] == value:
                return value
        except KeyError:
            self.table[value] = value
            return value

        trail = []
        while value != self.table[value]:
            trail.append(value)
            value = self.table[value]
        for t in trail:
            self.table[t] = value
        assert value < trail[0]
        return value

    def merge(self, left, right):
        left = self.find(left)
        right = self.find(right)
        if left > right:
            right, left = left, right
        self.table[right] = left

    def merge_all(self, values):
        value = None
        for i, v in enumerate(values):
            if i == 0:
                value = v
            else:
                self.merge(v, value)

    def partitions(self):
        results = defaultdict(set)
        for k in self.table:
            results[self.find(k)].add(k)
        yield from results.values()

    def __repr__(self):
        return f"UnionFind({list(self.partitions())})"
