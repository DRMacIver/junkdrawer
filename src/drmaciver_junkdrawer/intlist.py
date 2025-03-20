# This file is originally part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis/
#
# Copyright the Hypothesis Authors.
# Individual contributors are listed in AUTHORS.rst and the git log.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.


import array
from typing import Iterable, Iterator, Sequence, TypeVar, Union, overload

ARRAY_CODES = ["B", "H", "I", "L", "Q", "O"]

T = TypeVar("T")


def array_or_list(
    code: str, contents: Iterable[int]
) -> Union[list[int], array.ArrayType[int]]:
    if code == "O":
        return list(contents)
    return array.array(code, contents)


NEXT_ARRAY_CODE = dict(zip(ARRAY_CODES, ARRAY_CODES[1:]))


class IntList(Sequence[int]):
    """Class for storing a list of non-negative integers compactly.

    We store them as the smallest size integer array we can get
    away with. When we try to add an integer that is too large,
    we upgrade the array to the smallest word size needed to store
    the new value."""

    __slots__ = ("__underlying",)

    __underlying: Union[list[int], array.ArrayType[int]]

    def __init__(self, values: Sequence[int] = ()):
        for code in ARRAY_CODES:
            try:
                underlying = array_or_list(code, values)
                break
            except OverflowError:
                pass
        else:  # pragma: no cover
            raise AssertionError(f"Could not create storage for {values!r}")
        if isinstance(underlying, list):
            for v in underlying:
                if not isinstance(v, int) or v < 0:
                    raise ValueError(f"Could not create IntList for {values!r}")
        self.__underlying = underlying

    @classmethod
    def of_length(cls, n: int) -> "IntList":
        return cls(array_or_list("B", [0]) * n)

    def count(self, value: int) -> int:
        return self.__underlying.count(value)

    def __repr__(self) -> str:
        return f"IntList({list(self.__underlying)!r})"

    def __len__(self) -> int:
        return len(self.__underlying)

    @overload
    def __getitem__(self, i: int) -> int: ...  # pragma: no cover

    @overload
    def __getitem__(self, i: slice) -> "IntList": ...  # pragma: no cover

    def __getitem__(self, i: Union[int, slice]) -> "Union[int, IntList]":
        if isinstance(i, slice):
            return IntList(self.__underlying[i])
        return self.__underlying[i]

    def __delitem__(self, i: int) -> None:
        del self.__underlying[i]

    def insert(self, i: int, v: int) -> None:
        while True:
            try:
                self.__underlying.insert(i, v)
                return
            except OverflowError:
                assert i <= 5
                assert v > 0
                self.__upgrade()

    def __iter__(self) -> Iterator[int]:
        return iter(self.__underlying)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, IntList):
            return NotImplemented
        return self.__underlying == other.__underlying

    def __ne__(self, other: object) -> bool:
        if self is other:
            return False
        if not isinstance(other, IntList):
            return NotImplemented
        return self.__underlying != other.__underlying

    def append(self, n: int) -> None:
        i = len(self)
        self.__underlying.append(0)
        self[i] = n

    def __setitem__(self, i: int, n: int) -> None:
        while True:
            try:
                self.__underlying[i] = n
                return
            except OverflowError:
                assert n > 0
                self.__upgrade()

    def extend(self, ls: Iterable[int]) -> None:
        for n in ls:
            self.append(n)

    def __upgrade(self) -> None:
        assert isinstance(self.__underlying, array.array)
        code = NEXT_ARRAY_CODE[self.__underlying.typecode]
        self.__underlying = array_or_list(code, self.__underlying)
