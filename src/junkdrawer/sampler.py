import attr

from junkdrawer.coin import Coin, validate_weight


@attr.s(slots=True)
class TreeNode(object):
    item = attr.ib()
    weight = attr.ib()
    total_weight = attr.ib(default=None)

    own_coin = attr.ib(default=None)
    child_coin = attr.ib(default=None)


class Sampler(object):
    __slots__ = ("__items_to_indices", "__tree")

    def __init__(self, initial=()):
        self.__items_to_indices = {}
        self.__tree = []

        if isinstance(initial, dict):
            initial = initial.items()
        for k, v in initial:
            self.__set_weight(k, v)

        for i in range(len(self.__tree) - 1, -1, -1):
            self.__update_node(i)

    def __getitem__(self, item):
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

    def __contains__(self, item):
        try:
            i = self.__items_to_indices[item]
        except KeyError:
            return False
        return self.__tree[i].weight > 0

    def items(self):
        for t in self.__tree:
            if t.weight > 0:
                yield (t.item, t.weight)

    def __iter__(self):
        for k, _ in self.items():
            yield k

    def __bool__(self):
        return len(self.__tree) > 0 and self.__tree[0].total_weight > 0

    def sample(self, random):
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
