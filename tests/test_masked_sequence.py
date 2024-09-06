from drmaciver_junkdrawer.maskedsequence import MaskedSequence
from drmaciver_junkdrawer.poprandom import pop_random
from hypothesis import strategies as st, given
from hypothesis.stateful import (
    RuleBasedStateMachine,
    invariant,
    rule,
    initialize,
    Bundle,
    precondition,
)
import pytest


indexes = st.runner().flatmap(
    lambda self: (
        st.integers(-len(self.model), len(self.model) - 1)
        if self.model
        else st.nothing()
    )
)


class MaskedSequenceStateMachine(RuleBasedStateMachine):
    values = Bundle("values")

    @initialize(values=st.lists(st.integers()).map(tuple))
    def create_model(self, values):
        self.target = MaskedSequence(values)
        self.model = list(values)

    @rule(v=st.integers(), target=values)
    def int_values(self, v):
        return v

    @invariant()
    def lengths_are_equal(self):
        assert len(self.target) == len(self.model)

    @precondition(lambda self: len(self.model) > 0)
    @rule(target=values)
    def pop(self):
        v = self.model.pop()
        assert self.target.pop() == v
        return v

    @rule(v=values)
    def append(self, v):
        self.model.append(v)
        self.target.append(v)

    @rule(i=indexes)
    def check_value(self, i):
        assert self.model[i] == self.target[i]


TestMaskedSequence = MaskedSequenceStateMachine.TestCase


def test_errors_on_out_of_bounds_access():
    with pytest.raises(IndexError):
        MaskedSequence([1, 2])[2]

    with pytest.raises(IndexError):
        MaskedSequence([1, 2])[-3]


@given(
    st.lists(st.integers()), st.randoms(use_true_random=False, note_method_calls=True)
)
def test_errors_on_empty_pop(values, random):
    target = MaskedSequence(values)
    for _ in values:
        pop_random(target, random)
    assert len(target) == 0
    with pytest.raises(IndexError):
        target.pop()
