from random import Random

from engine.actions import Action
from engine.rules import legal_actions
from engine.game import Table
from bots.base import Bot


class EasyBot(Bot):
    """
    Simple heuristic-based poker bot. Does not use hand strength evaluation.
    """

    def __init__(
        self,
        tightness: float = 0.5,
        aggression: float = 0.5,
        seed: int = 42,
    ):
        self.tightness = tightness
        self.aggression = aggression
        self.rng: Random = Random(seed)

    def __repr__(self) -> str:
        return "EasyBot"

    def decide(self, table: Table) -> tuple[Action, int]:
        legal = legal_actions(table)

        # fallback in case desired action not found
        def choose(action_type: Action, amount: int = 0) -> tuple[Action, int]:
            for action in legal:
                if action == (action_type, amount):
                    return action
            return legal[-1]

        idx = table.current_player
        stack = table.stacks[idx]
        to_call = table.max_bet - table.current_bets[idx]
        pot = table.pot

        if to_call > 0:
            if to_call > stack * self.tightness:
                return choose(Action.FOLD)
            return choose(Action.CALL)

        # occasionally bets if no current bets
        if self.aggression > self.rng.random():
            return choose(Action.BET, round(int(pot * 0.6), table.small_blind))

        return choose(Action.CHECK)
