from typing import Tuple

from engine.cards import Card


def hand_eval(hole: Tuple[Card, ...], board: Tuple[Card, ...]) -> int:
    # TODO : Implement a proper poker hand evaluation algorithm
    return sum(int(card.rank.value) for card in hole + board)
