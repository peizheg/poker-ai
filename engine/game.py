from dataclasses import replace
from typing import Tuple
from random import Random

from engine.actions import Action
from engine.cards import Card
from engine.deck import create_deck, shuffle_deck, deal_deck
from engine.hand_eval import hand_eval
from engine.table import Table, Street

from bots.base import Bot
from bots.random_bot import RandomBot

def init_table(initial_stacks: Tuple[int, ...], small_blind: int, big_blind: int, rng: Random) -> Table:
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

    raise ValueError("No active players remaining")

def _is_betting_round_complete(table: Table) -> bool:
    for i in range(len(table.hands)):
        if table.folded[i] or table.all_in[i]:
            continue

        if not table.acted[i] or table.current_bets[i] != table.max_bet:
            return False

    return True

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

    if _is_betting_round_complete(table):
        first_player = table.current_player
    else:
        first_player = _get_next_player(table, table.dealer_index)

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

            new_prev_raise = amount if action == Action.RAISE else total_bet

            new_table = replace(
                table,
                stacks=tuple(new_stacks),
                current_bets=tuple(new_current_bets),
                max_bet=new_current_bets[i],
                pot=table.pot + total_bet,
                acted=tuple(idx == i for idx in range(len(table.acted))),
                prev_raise=new_prev_raise,
            )

            if new_stacks[i] == 0:
                new_table = replace(
                    new_table,
                    all_in=tuple(idx == i or all_in for idx, all_in in enumerate(table.all_in)),
                )


    if _is_betting_round_complete(new_table):
        while _is_betting_round_complete(new_table) and new_table.street != Street.SHOWDOWN:
            new_table = advance_street(new_table)
        
        return new_table
    else:
        return replace(new_table, current_player=_get_next_player(new_table, i))


def finalize_hand(table: Table) -> Table:
    n = len(table.hands)

    active_players = [i for i, f in enumerate(table.folded) if not f]

    if not active_players:
        raise ValueError("No active players to evaluate at showdown")

    # Compute hand strengths for active players
    strengths = {i: hand_eval(table.hands[i], table.board) for i in active_players}
    max_strength = max(strengths.values())
    winners = [i for i, s in strengths.items() if s == max_strength]

    # Distribute pot evenly, remainder to first winner
    share = table.pot // len(winners)
    remainder = table.pot % len(winners)
    new_stacks = list(table.stacks)
    for idx, winner in enumerate(winners):
        new_stacks[winner] += share
        if idx == 0:
            new_stacks[winner] += remainder

    print(", ".join([f"Player {i}" for i in winners]), "win(s)!", table)

    # Reset table for next hand
    new_table = replace(
        table,

        deck=create_deck(),
        hands=tuple(() for _ in range(n)),
        stacks=tuple(new_stacks),
        current_bets=tuple(0 for _ in range(n)),

        folded=tuple(False for _ in range(n)),
        all_in=tuple(False for _ in range(n)),
        acted=tuple(False for _ in range(n)),

        board=(),
        street=Street.PRE_FLOP,
        pot=0,
        dealer_index=(table.dealer_index + 1) % n,  # rotate dealer

        winners=tuple(winners),

    )

    return new_table


def play_hand(table: Table, bots: list[Bot]) -> Table:
    if len(table.hands) != len(bots):
        raise ValueError("Number of bots must match number of players at the table")

    table = deal_hole_cards(table)
    table = post_blinds(table)

    while table.street != Street.SHOWDOWN:
        current_idx = table.current_player
        if table.folded[current_idx] or table.all_in[current_idx]:
            # skip inactive players
            table = replace(table, current_player=_get_next_player(table, current_idx))
            continue

        # Ask the bot for its action
        action, amount = bots[current_idx].decide(table)
        table = apply_action(table, action, amount)

        print(action, amount, table)

    # Hand finished, finalize winners
    table = finalize_hand(table)

    return table


if __name__ == "__main__":
    import random

    rng = random.Random(42)

    initial_stacks = (1000, 1000, 1000)
    table = init_table(initial_stacks, 10, 20, rng)

    play_hand(table, [RandomBot(seed=i) for i in range(len(initial_stacks))])
