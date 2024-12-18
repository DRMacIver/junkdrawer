from random import Random
from typing import Any, Iterator

import attr

from drmaciver_junkdrawer.coin import Coin, validate_weight


class TreeSampler:
    """Implements an updatable sampler with integer weights.

    Behaves like a dict except the values must be integers >= 0
    and it has the additional sample() method which picks a random
    key with probability proportional to its weight.

    Updates and sampling are both log(n)
    """

    __slots__ = ("__items_to_indices", "__tree")

    def __init__(self, initial=()):
        self.__items_to_indices = {}
        # We store values in a binary tree unpacked as a list.
        # When modifying a weight we modify up to log(n) ancestors
        # in the tree to maintain an updated total weight.
        self.__tree = []

        if isinstance(initial, dict):
            initial = initial.items()
        for k, v in initial:
            self.__set_weight(k, v)

        for i in range(len(self.__tree) - 1, -1, -1):
            self.__update_node(i)

    def __getitem__(self, item) -> int:
        i = self.__items_to_indices[item]
        weight = self.__tree[i].weight
        if weight == 0:
            raise KeyError(item)
        return weight

    def __setitem__(self, item, weight):
        i = self.__set_weight(item, weight)
        self.__fix_tree(i)

    def __delitem__(self, item):
        self[item] = 0

    def __contains__(self, item) -> bool:
        try:
            i = self.__items_to_indices[item]
        except KeyError:
            return False
        return self.__tree[i].weight > 0

    def items(self) -> Iterator[tuple[int, int]]:
        for t in self.__tree:
            if t.weight > 0:
                yield (t.item, t.weight)

    def __iter__(self):
        for k, _ in self.items():
            yield k

    def __bool__(self):
        return len(self.__tree) > 0 and self.__tree[0].total_weight > 0

    def sample(self, random: Random):
        if not self.__tree or self.__tree[0].total_weight == 0:
            raise IndexError("Cannot sample from empty tree")
        i = 0
        while True:
            node = self.__tree[i]
            j1 = 2 * i + 1
            j2 = 2 * i + 2
            if j1 >= len(self.__tree):
                return node.item
            if node.weight > 0:
                if node.own_coin is None:
                    node.own_coin = Coin(node.weight, node.total_weight - node.weight)
                if node.own_coin.toss(random):
                    return node.item
            if j2 >= len(self.__tree):
                return self.__tree[j1].item
            if node.child_coin is None:
                node.child_coin = Coin(
                    self.__tree[j1].total_weight, self.__tree[j2].total_weight
                )
            if node.child_coin.toss(random):
                i = j1
            else:
                i = j2

    def __set_weight(self, item, weight):
        validate_weight(weight, "weight")
        try:
            i = self.__items_to_indices[item]
            self.__tree[i].weight = weight
        except KeyError:
            i = len(self.__items_to_indices)
            assert i == len(self.__tree)
            self.__items_to_indices[item] = i
            self.__tree.append(TreeNode(item, weight))
        return i

    def __update_node(self, i):
        node = self.__tree[i]
        node.total_weight = node.weight
        for j in (2 * i + 1, 2 * i + 2):
            if j < len(self.__tree):
                node.total_weight += self.__tree[j].total_weight
        node.own_coin = None
        node.child_coin = None

    def __fix_tree(self, i):
        while True:
            self.__update_node(i)
            if i == 0:
                break
            i = (i - 1) // 2


@attr.s(slots=True)
class TreeNode:
    item: int = attr.ib()
    weight: Any = attr.ib()
    total_weight: Any | None = attr.ib(default=None)

    own_coin: Coin | None = attr.ib(default=None)
    child_coin: Coin | None = attr.ib(default=None)
