from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from engine.cards import Card
from engine.deck import Deck

class Street(Enum):
    PRE_FLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4

@dataclass(frozen=True)
class Table:
    deck: Deck
    hands: Tuple[Tuple[Card, ...], ...]
    stacks: Tuple[int, ...]
    current_bets: Tuple[int, ...]

    small_blind: int
    big_blind: int

    folded: Tuple[bool, ...]
    all_in: Tuple[bool, ...]
    acted: Tuple[bool, ...]

    board: Tuple[Card, ...] = ()
    street: Street = Street.PRE_FLOP
    pot: int = 0
    dealer_index: int = 0
    current_player: int = 0
    max_bet: int = 0
    prev_raise: int = 0

    winners: Tuple[int, ...] = ()

    def __repr__(self) -> str:
        from engine.hand_eval import hand_eval

        n = len(self.hands)
        lines: list[str] = []

        for i in range(n):
            status: list[str] = []

            if i in self.winners or self.street != Street.SHOWDOWN and self.current_player == i:
                status.append("->")

            if i == self.dealer_index:
                status.append("[D]")
            elif i == (self.dealer_index + 1) % n:
                status.append("[SB]")
            elif i == (self.dealer_index + 2) % n:
                status.append("[BB]")

            if self.folded[i]:
                status.append("(F)")
            if self.all_in[i]:
                status.append("(AI)")

            lines.append(
                f"Player {i} {' '.join(status):<10} | "
                f"Hand: {' '.join(str(c) for c in self.hands[i])} (str: {hand_eval(self.hands[i], self.board)}) | "
                f"Stack: {self.stacks[i]:<4} | "
                f"Bet: {self.current_bets[i]}"
            )

        return (
            f"\nStreet: {self.street.name}\n"
            f"Pot: {self.pot}\n"
            f"Board: {' '.join(str(c) for c in self.board)}\n"
            f"Max bet: {self.max_bet}\n\n"
            + "\n".join(lines)
            +"\n"
        )
