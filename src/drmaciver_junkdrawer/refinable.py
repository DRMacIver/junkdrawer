from collections import Counter
from typing import Sequence

import numpy as np


class RefinablePartition:
    """Represents a refinable partition of the integers in
    [0, n), allowing for progressively splitting the values as
    new observations are made differentiating them."""

    def __init__(self, size):

        # All integers in [0, n), stored in an arbitrary order.
        self.__values = np.arange(size, dtype=int)

        # Reverse array for looking up indexes.
        # Invariant: values_indexes[values[i]] == i
        self.__values_indexes = np.arange(size, dtype=int)

        # Growable array (up to size n) of [start, end) pairs
        # of ranges in values each of which correspond to a single
        # partition.
        self.__n_partitions = 1
        self.__partitions = np.zeros(dtype=int, shape=(size, 2))
        self.__partitions[0, 1] = size

        # Index of which partition stores each index in values.
        # If start, end = partitions[i] then for start <= j < end
        # partitions_indexes[j] == i.
        self.__partitions_indexes = np.zeros(size, dtype=int)

    def __len__(self):
        return self.__n_partitions

    def __getitem__(self, i: int) -> Sequence[int]:
        i = self.__adjust_indices(i)
        u, v = self.__partitions[i]
        return self.__values[u:v]  # type: ignore

    def partition_of(self, i: int) -> int:
        """Returns the index of the partition this integer is in."""
        return self.__partitions_indexes[self.__values_indexes[i]]

    def mark(self, values):
        """Refine the partition so that every U in it is split into
        `U & values` and `U - values`. Runs in O(|values|)."""
        marked = Counter()
        for v in values:
            i = self.__values_indexes[v]
            partition = self.__partitions_indexes[i]
            marked[partition] += 1
            start, end = self.__partitions[partition]
            assert start <= i < end
            j = end - marked[partition]
            assert i <= j
            self.__values[i], self.__values[j] = self.__values[j], self.__values[i]
            self.__values_indexes[self.__values[i]] = i
            self.__values_indexes[self.__values[j]] = j

        for partition, mark_count in marked.items():
            start, end = self.__partitions[partition]
            # Entire partition was marked, nothing to do.
            if start + mark_count == end:
                continue
            new_partition = self.__n_partitions
            self.__n_partitions += 1
            self.__partitions[partition][1] = end - mark_count
            self.__partitions[new_partition][0] = end - mark_count
            self.__partitions[new_partition][1] = end
            for i in range(*self.__partitions[new_partition]):
                self.__partitions_indexes[i] = new_partition

    def __adjust_indices(self, i: int) -> int:
        if i < -len(self) or i >= len(self):
            raise IndexError(f"list index {i} out of range [-{len(self)}, {len(self)})")
        if i < 0:
            i += len(self)
        assert 0 <= i < len(self)
        return i

    def __check_invariants(self):
        for i, x in enumerate(self.__values):
            assert self.__values_indexes[x] == i
        for i, p in enumerate(self.__partitions_indexes):
            start, end = self.__partitions[p]
            assert start <= i <= end
