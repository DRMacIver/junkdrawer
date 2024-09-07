from collections import defaultdict, deque
from typing import Iterable


class Inconsistent(Exception):
    pass


class UnitPropagator:
    def __init__(self, clauses):
        self.__clauses = tuple(map(tuple, clauses))
        self.__watches = defaultdict(set)
        self.__watched_by = [set() for _ in self.__clauses]

        self.__known_units = set()
        self.__unit_queue = deque()

        for i, clause in enumerate(self.__clauses):
            if not clause:
                raise Inconsistent("Clauses contain an empty clause")
            if len(clause) == 1:
                self.__enqueue_unit(clause[0])
            else:
                self.__watches[clause[0]].add(i)
                self.__watches[clause[1]].add(i)
                self.__watched_by[i].update(clause[:2])
        self.__process_queue()

    @property
    def units(self) -> frozenset[int]:
        return frozenset(self.__known_units)

    def add_units(self, units: Iterable[int]) -> frozenset[int]:
        assert not self.__unit_queue, self.__unit_queue
        for u in units:
            self.__enqueue_unit(u)
        return frozenset(self.__process_queue())

    def add_unit(self, unit: int) -> frozenset[int]:
        return self.add_units((unit,))

    def __enqueue_unit(self, unit):
        if unit not in self.__known_units:
            if -unit in self.__known_units:
                raise Inconsistent(
                    f"Tried to add {unit} as a unit but {-unit} is already a unit."
                )
            self.__known_units.add(unit)
            self.__unit_queue.append(unit)

    def __process_queue(self):
        processed = set()
        while self.__unit_queue:
            new_unit = self.__unit_queue.popleft()
            processed.add(new_unit)
            self.__watches.pop(new_unit, None)
            killed = -new_unit
            need_checking = self.__watches.pop(killed, ())
            for i in need_checking:
                self.__watched_by[i].remove(killed)
                (remaining_watch,) = self.__watched_by[i]
                if remaining_watch in self.__known_units:
                    self.__watched_by[i].clear()
                    continue
                for literal in self.__clauses[i]:
                    if literal == remaining_watch:
                        continue
                    if literal in self.__known_units:
                        # If this clause is already satisfied we don't need to
                        # watch it any more
                        self.__watches[remaining_watch].remove(i)
                        self.__watched_by[i].clear()
                        break
                    elif -literal not in self.__known_units:
                        # Otherwise, we need to find some new literal in the
                        # clause to watch it from.
                        self.__watched_by[i].add(literal)
                        self.__watches[literal].add(i)
                        break
                else:
                    # remaining_watch is the only literal left in this
                    # clause, so must be a unit.
                    self.__enqueue_unit(remaining_watch)
        assert not self.__unit_queue
        return processed
