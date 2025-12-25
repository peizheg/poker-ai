from dataclasses import dataclass, replace
from enum import Enum
from typing import Tuple

from engine.cards import Card
from engine.deck import *
from engine.eval import eval_hand

class Street(Enum):
    PRE_FLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4

class Action(Enum):
    FOLD = 0
    CHECK = 1
    CALL = 2
    BET = 3
    RAISE = 4

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

    winners: Tuple[int, ...] = ()

    def __repr__(self) -> str:
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
                f"Hand: {' '.join(str(c) for c in self.hands[i])} | "
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

        

def init_table(initial_stacks: Tuple[int, ...], small_blind: int, big_blind: int, rng: RNG) -> Table:
    if len(initial_stacks) < 2:
        raise ValueError("At least two players required")
    
    n = len(initial_stacks)

    return Table(
        deck=shuffle_deck(create_deck(), rng),
        hands=tuple(() for _ in range(n)),
        stacks=initial_stacks,
        current_bets=tuple(0 for _ in range(n)),

        small_blind=small_blind,
        big_blind=big_blind,

        folded=tuple(False for _ in range(n)),
        all_in=tuple(False for _ in range(n)),
        acted=tuple(False for _ in range(n)),
    )

def deal_hole_cards(table: Table, num_hole_cards: int = 2) -> Table:
    if (len(table.deck) < num_hole_cards * len(table.hands)):
        raise ValueError("Not enough cards in deck to deal hole cards")
    
    dealt, new_deck = deal_deck(table.deck, num_hole_cards * len(table.hands))
    
    new_hands: Tuple[Tuple[Card, ...], ...] = tuple(
        tuple(dealt[i * num_hole_cards + j] for j in range(num_hole_cards))
        for i in range(len(table.hands))
    )

    return replace(
        table,
        deck=new_deck,
        hands=new_hands,
    )

def post_blinds(table: Table) -> Table:
    n = len(table.hands)
    if n == 2:
        sb_idx = table.dealer_index
        bb_idx = (table.dealer_index + 1) % n
    else:
        sb_idx = (table.dealer_index + 1) % n
        bb_idx = (table.dealer_index + 2) % n

    new_stacks = list(table.stacks)
    new_current_bets = [0] * n
    pot_increase = 0

    # Post small blind
    sb_amt = min(table.small_blind, new_stacks[sb_idx])
    new_stacks[sb_idx] -= sb_amt
    new_current_bets[sb_idx] += sb_amt
    pot_increase += sb_amt

    # Post big blind
    bb_amt = min(table.big_blind, new_stacks[bb_idx])
    new_stacks[bb_idx] -= bb_amt
    new_current_bets[bb_idx] += bb_amt
    pot_increase += bb_amt

    return replace(
        table,
        stacks=tuple(new_stacks),
        current_bets=tuple(new_current_bets),
        pot=table.pot + pot_increase,
        current_player=(bb_idx + 1) % n,
        max_bet=bb_amt,
    )

def _get_next_player(table: Table, start: int) -> int:
    n = len(table.hands)
    for offset in range(1, n):
        next_i = (start + offset) % n
        if not table.folded[next_i] and not table.all_in[next_i]:
            return next_i

    return start  # no active players remain

def advance_street(table: Table) -> Table:
    n = len(table.hands)

    next_street, cards_to_deal = {
        Street.PRE_FLOP: (Street.FLOP, 3),
        Street.FLOP: (Street.TURN, 1),
        Street.TURN: (Street.RIVER, 1),
        Street.RIVER: (Street.SHOWDOWN, 0),
    }[table.street]

    dealt, new_deck = deal_deck(table.deck, cards_to_deal)
    new_board = table.board + dealt

    first_player = _get_next_player(table, table.dealer_index)

    if next_street == Street.SHOWDOWN:
        active_players = [i for i, folded in enumerate(table.folded) if not folded]

        if not active_players:
            raise ValueError("No active players to evaluate at showdown")

        # Compute hand strengths
        strengths = {i: eval_hand(table.hands[i], new_board) for i in active_players}

        # Find best hand
        max_strength = max(strengths.values())
        winners = [i for i, s in strengths.items() if s == max_strength]

        # Distribute pot
        share = table.pot // len(winners)
        remainder = table.pot % len(winners)

        new_stacks = list(table.stacks)
        for idx, winner in enumerate(winners):
            new_stacks[winner] += share
            if idx == 0:
                new_stacks[winner] += remainder
    
        return replace(
            table,
            street=next_street,
            stacks=tuple(new_stacks),
            current_bets=tuple(0 for _ in range(n)),
            current_player=first_player,
            max_bet=0,
            pot=0,
            acted=tuple(False for _ in range(n)),
            winners=tuple(winners),
        )

    return replace(
        table,
        deck=new_deck,
        board=new_board,
        street=next_street,
        current_bets=tuple(0 for _ in range(n)),
        current_player=first_player,
        max_bet=0,
        acted=tuple(False for _ in range(n)),
    )


def apply_action(table: Table, action: Action, amount: int = 0) -> Table:
    def _is_betting_round_complete(table: Table) -> bool:
        for i in range(len(table.hands)):
            if table.folded[i] or table.all_in[i]:
                continue

            if not table.acted[i] or table.current_bets[i] != table.max_bet:
                return False

        return True

    i = table.current_player

    if table.folded[i] or table.all_in[i]:
        raise ValueError("Player cannot act, already folded or all-in")

    match action:
        case Action.FOLD:
            new_table = replace(
                table,
                folded=tuple(idx == i or folded for idx, folded in enumerate(table.folded)),
                acted=tuple(idx == i or acted for idx, acted in enumerate(table.acted)),
            )
    
        case Action.CHECK:
            if table.current_bets[i] < table.max_bet:
                raise ValueError("Cannot check when there is a bet to call")
            new_table = replace(
                table,
                acted=tuple(idx == i or acted for idx, acted in enumerate(table.acted)),
            )

    
        case Action.CALL:
            to_call = table.max_bet - table.current_bets[i]
            call_amount = min(to_call, table.stacks[i])

            new_stacks = list(table.stacks)
            new_current_bets = list(table.current_bets)
            new_stacks[i] -= call_amount
            new_current_bets[i] += call_amount

            new_table = replace(
                table,
                stacks=tuple(new_stacks),
                current_bets=tuple(new_current_bets),
                pot=table.pot + call_amount,
                acted=tuple(idx == i or acted for idx, acted in enumerate(table.acted)),
            )
            
            if new_stacks[i] == 0:
                new_table = replace(
                    new_table,
                    all_in=tuple(idx == i or all_in for idx, all_in in enumerate(table.all_in)),
                )

        case Action.BET | Action.RAISE:
            if action == Action.BET and table.max_bet != 0:
                raise ValueError("Cannot bet when a bet already exists")

            if action == Action.RAISE and table.max_bet == 0:
                raise ValueError("Cannot raise when no bet exists")

            to_call = table.max_bet - table.current_bets[i]
            total_bet = to_call + amount
            if total_bet > table.stacks[i]:
                raise ValueError("Bet/Raise amount exceeds player's stack")

            new_stacks = list(table.stacks)
            new_current_bets = list(table.current_bets)
            new_stacks[i] -= total_bet
            new_current_bets[i] += total_bet

            new_table = replace(
                table,
                stacks=tuple(new_stacks),
                current_bets=tuple(new_current_bets),
                max_bet=new_current_bets[i],
                pot=table.pot + total_bet,
                acted=tuple(idx == i for idx in range(len(table.acted))),
            )

            if new_stacks[i] == 0:
                new_table = replace(
                    new_table,
                    all_in=tuple(idx == i or all_in for idx, all_in in enumerate(table.all_in)),
                )
    
    new_current_player = _get_next_player(new_table, i)

    if _is_betting_round_complete(new_table):
        return advance_street(new_table)
    else:
        return replace(new_table, current_player=new_current_player)


if __name__ == "__main__":
    import random

    rng = random.Random(42)

    initial_stacks = (1000, 1000, 1000)
    table = init_table(initial_stacks, 10, 20, rng)
    table = deal_hole_cards(table)
    table = post_blinds(table)


    print("=== After blinds ===", table)

    # === PREFLOP ===
    table = apply_action(table, Action.CALL)
    print("=== Dealer calls ===", table)

    table = apply_action(table, Action.CALL)
    print("=== SB calls ===", table)

    table = apply_action(table, Action.CHECK)
    print("=== BB checks -> preflop ends ===", table)


    # === FLOP ===
    table = apply_action(table, Action.CHECK)
    print("=== SB checks ===", table)

    table = apply_action(table, Action.BET, amount=50)
    print("=== BB bets 50 ===", table)

    table = apply_action(table, Action.FOLD)
    print("=== dealer folds ===", table)

    table = apply_action(table, Action.CALL)
    print("=== p1 calls -> flop ends ===", table)


    # === TURN ===
    table = apply_action(table, Action.CHECK)
    table = apply_action(table, Action.CHECK)
    print("=== Everyone checks -> turn ends ===", table)


    # === RIVER ===
    table = apply_action(table, Action.BET, amount=100)
    print("=== SB bets 100 ===", table)

    table = apply_action(table, Action.FOLD)
    print("=== BB folds -> river ends ===", table)
