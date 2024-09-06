from hypothesis.stateful import rule, invariant, RuleBasedStateMachine, initialize
from hypothesis import strategies as st
from drmaciver_junkdrawer.refinable import RefinablePartition
from hypothesis import settings


@settings(report_multiple_bugs=False)
class RefinablePartitionMachine(RuleBasedStateMachine):
    @initialize(size=st.integers(1, 1000))
    def setup_model(self, size):
        self.size = size
        self.model = frozenset({frozenset(range(size))})
        self.target = RefinablePartition(size)

    @invariant()
    def check_model_matches(self):
        self.target._RefinablePartition__check_invariants()  # type: ignore
        assert len(self.model) == len(self.target)
        assert set(map(frozenset, self.target)) == frozenset(self.model)

    @rule(
        values=st.runner().flatmap(
            lambda self: st.frozensets(st.integers(0, self.size - 1), min_size=1)
        )
    )
    def refine(self, values):
        self.target.mark(values)
        new_model = set()
        for v in self.model:
            new_model.add(v & values)
            new_model.add(v - values)
        new_model.discard(frozenset())
        self.model = frozenset(new_model)

    @rule(i=st.runner().flatmap(lambda self: st.integers(0, len(self.target) - 1)))
    def partitions_contain_right_values(self, i):
        assert i in self.target[self.target.partition_of(i)]


TestRefinablePartition = RefinablePartitionMachine.TestCase


def test_basic_marking_1():
    p = RefinablePartition(2)
    assert list(p[0]) == [0, 1]
    p.mark({0})
    assert sorted(map(sorted, p)) == [[0], [1]]


def test_basic_marking_2():
    p = RefinablePartition(3)
    p.mark({0})
    assert sorted(map(sorted, p)) == [[0], [1, 2]]


def test_remarking_1():
    p = RefinablePartition(2)
    p.mark({0})
    p.mark({0})
    assert sorted(map(sorted, p)) == [[0], [1]]


def test_negative_indexes():
    p = RefinablePartition(5)
    p.mark({0, 1})
    p.mark({1, 2, 3})
    assert list(p[-1]) == list(p[len(p) - 1])
