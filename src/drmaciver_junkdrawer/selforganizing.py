import heapq
from typing import Callable, Generic, Iterable, TypeVar

Element = TypeVar("Element")


class NotFound(Exception):
    pass


class SelfOrganisingList(Generic[Element]):
    """A self-organising list: That is, a collection of elements,
    sorted in a way that when you search for something it's likely
    to quickly be the one you need.

    The heuristic we use is that we try values in order of how often
    they have been the correct answer, preferring ones that have more
    recently been correct.
    """

    def __init__(self, values: Iterable[Element] = ()) -> None:
        self.__values = [((0, 0), v) for v in values]
        heapq.heapify(self.__values)
        self.__counter = 0

    def __repr__(self) -> str:
        return f"SelfOrganisingList({self.__values!r})"

    def add(self, value: Element) -> None:
        """Add a value to this list."""
        heapq.heappush(self.__values, ((0, -self.__counter), value))
        self.__counter += 1

    def find(self, condition: Callable[[Element], bool]) -> Element:
        """Returns some value in this list such that ``condition(value)`` is
        True. If no such value exists raises ``NotFound``."""
        if not self.__values:
            raise NotFound()

        if condition(self.__values[0][1]):
            return self.__values[0][1]

        to_return = [heapq.heappop(self.__values)]
        while self.__values:
            t = heapq.heappop(self.__values)
            (score, _), value = t
            if condition(value):
                to_return.append(((score - 1, -self.__counter), value))
                self.__counter += 1
                for t in to_return:
                    heapq.heappush(self.__values, t)
                return value
            else:
                to_return.append(t)
        else:
            self.__values = to_return
            heapq.heapify(self.__values)
        raise NotFound("No values satisfying condition")
