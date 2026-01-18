"""Card representation for Kuhn Poker."""

from enum import IntEnum


class Card(IntEnum):
    """Kuhn Poker uses only 3 cards: Jack, Queen, King."""
    JACK = 0
    QUEEN = 1
    KING = 2

    def __str__(self) -> str:
        return self.name[0]  # J, Q, K