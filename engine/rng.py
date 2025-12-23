from typing import Protocol, TypeVar

T = TypeVar("T")

class RNG(Protocol):
    def shuffle(self, x: list[T]) -> None:
        ...
        