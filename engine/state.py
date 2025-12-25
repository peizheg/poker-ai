from dataclasses import dataclass, replace
from enum import Enum
from typing import Tuple

from engine.cards import Card
from engine.deck import *

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
class GameState:
    deck: Deck
    hands: Tuple[Tuple[Card, ...], ...]
    stacks: Tuple[int, ...]
    current_bets: Tuple[int, ...]

    small_blind: int
    big_blind: int

    folded: Tuple[bool, ...]
    all_in: Tuple[bool, ...]

    board: Tuple[Card, ...] = ()
    street: Street = Street.PRE_FLOP
    pot: int = 0
    dealer_index: int = 0
    current_player: int = 0
    max_bet: int = 0

def init_state(initial_stacks: Tuple[int, ...], small_blind: int, big_blind: int, rng: RNG) -> GameState:
    if len(initial_stacks) < 2:
        raise ValueError("At least two players required")
    
    n = len(initial_stacks)

    return GameState(
        deck=shuffle_deck(create_deck(), rng),
        hands=tuple(() for _ in range(n)),
        stacks=initial_stacks,
        current_bets=tuple(0 for _ in range(n)),

        small_blind=small_blind,
        big_blind=big_blind,

        folded=tuple(False for _ in range(n)),
        all_in=tuple(False for _ in range(n)),
    )

def deal_hole_cards(state: GameState, num_hole_cards: int = 2) -> GameState:
    if (len(state.deck) < num_hole_cards * len(state.hands)):
        raise ValueError("Not enough cards in deck to deal hole cards")
    
    dealt, new_deck = deal_deck(state.deck, num_hole_cards * len(state.hands))
    
    new_hands: Tuple[Tuple[Card, ...], ...] = tuple(
        tuple(dealt[i * num_hole_cards + j] for j in range(num_hole_cards))
        for i in range(len(state.hands))
    )

    return replace(
        state,
        deck=new_deck,
        hands=new_hands,
    )

def post_blinds(state: GameState) -> GameState:
    n = len(state.hands)
    if n == 2:
        sb_idx = state.dealer_index
        bb_idx = (state.dealer_index + 1) % n
    else:
        sb_idx = (state.dealer_index + 1) % n
        bb_idx = (state.dealer_index + 2) % n

    new_stacks = list(state.stacks)
    new_current_bets = [0] * n
    pot_increase = 0

    # Post small blind
    sb_amt = min(state.small_blind, new_stacks[sb_idx])
    new_stacks[sb_idx] -= sb_amt
    new_current_bets[sb_idx] += sb_amt
    pot_increase += sb_amt

    # Post big blind
    bb_amt = min(state.big_blind, new_stacks[bb_idx])
    new_stacks[bb_idx] -= bb_amt
    new_current_bets[bb_idx] += bb_amt
    pot_increase += bb_amt

    return replace(
        state,
        stacks=tuple(new_stacks),
        current_bets=tuple(new_current_bets),
        pot=state.pot + pot_increase,
        current_player=(bb_idx + 1) % n,
    )

def advance_street(state: GameState) -> GameState:
    n = len(state.hands)

    next_street, cards_to_deal = {
        Street.PRE_FLOP: (Street.FLOP, 3),
        Street.FLOP: (Street.TURN, 1),
        Street.TURN: (Street.RIVER, 1),
        Street.RIVER: (Street.SHOWDOWN, 0),
    }[state.street]

    dealt, new_deck = deal_deck(state.deck, cards_to_deal)
    new_board = state.board + dealt

    first_player = (state.dealer_index + 1) % n

    return replace(
        state,
        deck=new_deck,
        board=new_board,
        street=next_street,
        current_bets=tuple(0 for _ in range(n)),
        current_player=first_player,
    )

def _get_next_player(state: GameState, start: int) -> int:
    n = len(state.hands)
    for offset in range(1, n + 1):
        next_i = (start + offset) % n
        if not state.folded[next_i] and not state.all_in[next_i]:
            return next_i
    return 0  # no active players remain


def apply_action(state: GameState, action: Action, amount: int = 0) -> GameState:
    i = state.current_player

    if state.folded[i] or state.all_in[i]:
        raise ValueError("Player cannot act, already folded or all-in")

    match action:
        case Action.FOLD:
            new_folded = list(state.folded)
            new_folded[i] = True
            new_state = replace(state, folded=tuple(new_folded))
    
        case Action.CHECK:
            if state.current_bets[i] < state.max_bet:
                raise ValueError("Cannot check when there is a bet to call")
            new_state = state
    
        case Action.CALL:
            to_call = state.max_bet - state.current_bets[i]
            call_amount = min(to_call, state.stacks[i])

            new_stacks = list(state.stacks)
            new_current_bets = list(state.current_bets)
            new_stacks[i] -= call_amount
            new_current_bets[i] += call_amount

            new_state = replace(
                state,
                stacks=tuple(new_stacks),
                current_bets=tuple(new_current_bets),
                pot=state.pot + call_amount
            )
            
            if new_stacks[i] == 0:
                new_all_in = list(state.all_in)
                new_all_in[i] = True
                new_state = replace(new_state, all_in=tuple(new_all_in))

        case Action.BET | Action.RAISE:
            if action == Action.BET and state.max_bet != 0:
                raise ValueError("Cannot bet when a bet already exists")

            if action == Action.RAISE and state.max_bet == 0:
                raise ValueError("Cannot raise when no bet exists")

            to_call = state.max_bet - state.current_bets[i]
            total_bet = to_call + amount
            if total_bet > state.stacks[i]:
                raise ValueError("Bet/Raise amount exceeds player's stack")

            new_stacks = list(state.stacks)
            new_current_bets = list(state.current_bets)
            new_stacks[i] -= total_bet
            new_current_bets[i] += total_bet

            new_state = replace(
                state,
                stacks=tuple(new_stacks),
                current_bets=tuple(new_current_bets),
                max_bet=new_current_bets[i],
                pot=state.pot + total_bet
            )

            if new_stacks[i] == 0:
                new_all_in = list(state.all_in)
                new_all_in[i] = True
                new_state = replace(new_state, all_in=tuple(new_all_in))

    return replace(new_state, current_player=_get_next_player(new_state, i))


if __name__ == "__main__":
    import random
    rng = random.Random()

    initial_stacks = (1000, 1000, 1000)
    state = init_state(initial_stacks, 10, 20, rng)
    state = deal_hole_cards(state)

    print("Initial GameState:")
    print("Deck size:", len(state.deck))
    print("Hands:", state.hands)
    print()

    state = post_blinds(state)
    print("After posting blinds:")
    print("Stacks:", state.stacks)
    print("Current Bets:", state.current_bets)
    print("Pot:", state.pot)
    print("Current Player Index:", state.current_player)
    print()

    state = advance_street(state)
    print("After advancing to Flop:")
    print("Board:", state.board)
    print("Street:", state.street)
    print("Current Player Index:", state.current_player)
    print()
    
    state = advance_street(state)
    print("After advancing to Turn:")
    print("Board:", state.board)
    print("Street:", state.street)
    print("Current Player Index:", state.current_player)
    print()

    state = advance_street(state)
    print("After advancing to River:")
    print("Board:", state.board)
    print("Street:", state.street)
    print("Current Player Index:", state.current_player)
    print()

    state = advance_street(state)
    print("After advancing to Showdown:")
    print("Board:", state.board)
    print("Street:", state.street)
    print("Current Player Index:", state.current_player)
