from collections import defaultdict
from typing import Iterable


class Inconsistent(Exception):
    pass


class UnitPropagator:
    def __init__(self, clauses):
        self.__clauses = tuple(map(tuple, clauses))
        self.__watches = defaultdict(set)
        self.__watched_by = [set() for _ in self.__clauses]

        self.units = set()
        self.__dirty = set(range(len(clauses)))
        self.__clean_dirty_clauses()

    def add_units(self, units: Iterable[int]) -> None:
        assert not self.__dirty, self.__dirty
        for u in units:
            self.__enqueue_unit(u)
        self.__clean_dirty_clauses()

    def add_unit(self, unit: int) -> None:
        self.add_units((unit,))

    def __enqueue_unit(self, unit):
        if unit not in self.units:
            if -unit in self.units:
                raise Inconsistent(
                    f"Tried to add {unit} as a unit but {-unit} is already a unit."
                )
            self.units.add(unit)
            self.__dirty.update(self.__watches.pop(-unit, ()))

    def __clean_dirty_clauses(self):
        while self.__dirty:
            dirty = self.__dirty
            self.__dirty = set()

            for i in dirty:
                clause = self.__clauses[i]
                if not clause:
                    raise Inconsistent("Clauses contain an empty clause")
                if any(literal in self.units for literal in clause):
                    for literal in self.__watched_by[i]:
                        if literal in self.__watches:
                            self.__watches[literal].remove(i)
                    self.__watched_by[i].clear()
                else:
                    for literal in list(self.__watched_by[i]):
                        if -literal in self.units:
                            self.__watched_by[i].remove(literal)
                    for literal in clause:
                        if len(self.__watched_by[i]) == 2:
                            break
                        if -literal not in self.units:
                            self.__watches[literal].add(i)
                            self.__watched_by[i].add(literal)
                    if len(self.__watched_by[i]) == 0:
                        raise Inconsistent(
                            f"Clause {' '.join(map(str, clause))} can no longer be satisfied"
                        )
                    elif len(self.__watched_by[i]) == 1:
                        self.__enqueue_unit(*self.__watched_by[i])
