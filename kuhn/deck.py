"""Deck for Kuhn Poker."""

import random

from .card import Card


class Deck:
    """A deck of Kuhn Poker cards (J, Q, K)."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Reset and shuffle the deck."""
        self._cards = [Card.JACK, Card.QUEEN, Card.KING]
        random.shuffle(self._cards)

    def deal(self) -> Card:
        """Deal the next card from the deck."""
        return self._cards.pop()