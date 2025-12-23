from dataclasses import dataclass
from typing import Tuple
from engine.cards import Card

@dataclass(frozen=True)
class GameState:
    stacks: Tuple[int, ...]
    pot: int
    board: Tuple[Card, ...]
    hands: Tuple[Tuple[Card, Card], ...]
    current_player: int
    street: str
    is_terminal: bool
