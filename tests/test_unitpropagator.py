from hypothesis.stateful import (
    rule,
    invariant,
    RuleBasedStateMachine,
    initialize,
    precondition,
)
from hypothesis import given, strategies as st, settings, HealthCheck
from drmaciver_junkdrawer.sat.unitpropagator import Inconsistent, UnitPropagator
from hypothesis import settings, assume
from pysat.solvers import Glucose4
import operator
import pytest


def is_satisfiable(clauses):
    return Glucose4(clauses).solve()


def find_solution(clauses):
    solver = Glucose4(clauses)
    if not solver.solve():
        return None
    return solver.get_model()


@st.composite
def sat_clauses(draw, min_clause_size=1):
    n_variables = draw(st.integers(min_clause_size, min(10, min_clause_size * 2)))
    variables = range(1, n_variables + 1)

    literal = st.builds(
        operator.mul, st.sampled_from(variables), st.sampled_from((-1, 1))
    )

    return draw(
        st.lists(st.lists(literal, unique_by=abs, min_size=min_clause_size), min_size=1)
    )


@st.composite
def unsatisfiable_clauses(draw, min_clause_size=1):
    clauses = draw(sat_clauses(min_clause_size=min_clause_size))
    assume(clauses)

    while True:
        sol = find_solution(clauses)
        if sol is None:
            return clauses
        assert len(sol) >= min_clause_size, (sol, clauses)
        subset = draw(
            st.lists(st.sampled_from(sol), min_size=min_clause_size, unique=True)
        )
        clauses.append([-n for n in subset])


@st.composite
def has_unique_solution(draw):
    clauses = draw(sat_clauses(min_clause_size=2))
    sol = find_solution(clauses)
    assume(sol is not None)
    assert sol is not None
    assert is_satisfiable(clauses)

    while True:
        other_sol = find_solution(clauses + [[-literal for literal in sol]])
        if other_sol is None:
            assert is_satisfiable(clauses)
            return clauses

        missing = sorted(set(sol) - set(other_sol))
        if len(missing) == 1:
            clauses.append(list(missing))
        else:
            subset = draw(
                st.lists(
                    st.sampled_from(missing),
                    min_size=2,
                    unique=True,
                )
            )
            clauses.append(subset)


good_sat_clauses = sat_clauses().filter(is_satisfiable) | has_unique_solution()


@st.composite
def possible_units(draw):
    self = draw(st.runner())
    return draw(
        st.lists(st.sampled_from(sorted(self.free)), unique_by=abs, min_size=1).filter(
            lambda attempt: is_satisfiable(self.clauses_left + [[v] for v in attempt])
        )
    )


@settings(report_multiple_bugs=False, suppress_health_check=list(HealthCheck))
class UnitPropagatorMachine(RuleBasedStateMachine):
    @initialize(clauses=good_sat_clauses)
    def initial_clauses(self, clauses):
        self.units = set()
        self.neg_units = set()
        self.clauses_left = clauses
        self.propagator = UnitPropagator(clauses)
        self.variables = {abs(l) for clause in clauses for l in clause}
        self.free = (
            (self.variables | {-l for l in self.variables})
            - self.units
            - self.neg_units
        )
        self.__run_shitty_unit_propagation()

    @precondition(lambda self: self.free)
    @rule(units=possible_units())
    def add_new_unit(self, units):
        self.propagator.add_units(units)
        self.clauses_left.extend([[v] for v in units])
        self.__run_shitty_unit_propagation()

    # Dumb hack to shut Hypothesis up about us having no progress possible
    # left.
    @precondition(lambda self: not self.free)
    @rule()
    def done(self): ...

    @invariant()
    def unit_propagator_agrees_on_units(self):
        assert frozenset(self.units) == self.propagator.units

    def __run_shitty_unit_propagation(self):
        prev = -1
        while prev != len(self.units):
            prev = len(self.units)
            new_clauses = set()

            for clause in self.clauses_left:
                clause = tuple(sorted(set(clause) - self.neg_units))
                assert clause
                if len(clause) == 1:
                    (v,) = clause
                    self.units.add(v)
                    self.neg_units.add(-v)
                    self.free.discard(v)
                    self.free.discard(-v)
                else:
                    new_clauses.add(clause)
            self.clauses_left = sorted(new_clauses)


UnitPropagatorTests = UnitPropagatorMachine.TestCase


def test_unit_propagator_updates_watches():
    up = UnitPropagator([[-2, 3, -1]])
    assert not up.units
    up.add_unit(-3)
    assert up.units == {-3}
    up.add_unit(1)
    assert up.units == {1, -2, -3}


def test_add_all_as_units():
    up = UnitPropagator([[-2, 3, 1]])
    up.add_units([-2, -3, 1])
    assert up.units == {-2, -3, 1}


@given(st.data())
def test_any_assignment_of_unsatisfiable_clauses_is_eventually_inconsistent(data):
    clauses = data.draw(unsatisfiable_clauses())
    variables = sorted(abs(l) for clause in clauses for l in clause)
    signs = data.draw(
        st.lists(
            st.sampled_from((-1, 1)), min_size=len(variables), max_size=len(variables)
        )
    )
    assignment = data.draw(st.permutations([s * v for s, v in zip(signs, variables)]))

    with pytest.raises(Inconsistent):
        propagator = UnitPropagator(clauses)
        for v in assignment:  # pragma: no branch
            propagator.add_unit(v)


def test_errors_on_empty_clause():
    with pytest.raises(Inconsistent):
        UnitPropagator([[]])
