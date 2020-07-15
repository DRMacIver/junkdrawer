from collections import defaultdict

from hypothesis import assume, given, strategies as st
from junkdrawer.unionfind import UnionFind


@given(st.data())
def test_arbitrary_merges(data):
    colouring = data.draw(st.dictionaries(st.integers(), st.integers(0, 5), min_size=2))
    partitions = defaultdict(list)
    for k, v in colouring.items():
        partitions[v].append(k)

    for v in partitions.values():
        v.sort()

    partitions = sorted(partitions.values())

    values = sorted(colouring)

    a_merge = st.sampled_from(partitions).flatmap(
        lambda p: st.lists(st.sampled_from(p), min_size=2)
    )

    table = UnionFind()

    to_merge = data.draw(st.lists(a_merge))

    for merger in to_merge:
        table.merge_all(merger)

    for v in colouring:
        assert colouring[table.find(v)] == colouring[v]

    for merged in to_merge:
        assert len(set(map(table.find, merged))) == 1

    for p in table.partitions():
        assert len(set(map(colouring.__getitem__, p))) == 1

    from_repr = eval(repr(table))

    for v in colouring:
        assert table.find(v) == from_repr.find(v)
