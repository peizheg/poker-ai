from typing import Tuple

from engine.cards import Card


def eval_hand(hole: Tuple[Card, ...], board: Tuple[Card, ...]) -> int:
    # TODO : Implement a proper poker hand evaluation algorithm
    return sum(int(card.rank.value) for card in hole + board)
