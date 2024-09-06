from typing import Generic, Sequence, TypeVar

Elt = TypeVar("Elt")


class MaskedSequence(Generic[Elt]):
    def __init__(self, values: Sequence[Elt]):
        self.__underlying = values
        self.__len = len(values)
        self.__mask = {}

    def __len__(self) -> int:
        return self.__len

    def __getitem__(self, i: int) -> Elt:
        i = self.__adjust_indices(i)
        try:
            return self.__mask[i]
        except KeyError:
            return self.__underlying[i]

    def __setitem__(self, i: int, v: Elt):
        i = self.__adjust_indices(i)
        self.__mask[i] = v

    def pop(self) -> Elt:
        if len(self) == 0:
            raise IndexError("pop from empty list")
        i = len(self) - 1
        result = self[i]
        self.__mask.pop(i, None)
        self.__len -= 1
        return result

    def append(self, v: Elt):
        i = len(self)
        self.__mask[i] = v
        self.__len += 1

    def __adjust_indices(self, i: int) -> int:
        if i < -len(self) or i >= len(self):
            raise IndexError(f"list index {i} out of range [-{len(self)}, {len(self)})")
        if i < 0:
            i += len(self)
        assert 0 <= i < len(self)
        return i
