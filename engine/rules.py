from typing import List
from engine.actions import Action
from engine.table import Table

def legal_actions(table: Table) -> List[tuple[Action, int]]:
    idx = table.current_player

    # Skip folded or all-in players
    if table.folded[idx] or table.all_in[idx]:
        return []

    actions: list[tuple[Action, int]] = []

    to_call = table.max_bet - table.current_bets[idx]
    stack = table.stacks[idx]

    # FOLD is always available
    if table.max_bet > 0:
        actions.append((Action(Action.FOLD), 0))


    # CHECK available when no bet to match
    if to_call == 0:
        actions.append((Action(Action.CHECK), 0))
    elif stack >= to_call:
        # otherwise, CALL is available when able to match
        actions.append((Action(Action.CALL), 0))

    # BET (only if no bet yet)
    if table.max_bet == 0 and stack > 0:
        for amt in range(table.small_blind, stack + 1, table.small_blind):
            actions.append((Action.BET, amt))

    # RAISE (only if a bet exists)
    if table.max_bet > 0 and stack > to_call:
        for amt in range(table.prev_raise, stack - to_call + 1, table.small_blind):
            actions.append((Action.RAISE, amt))

    return actions
