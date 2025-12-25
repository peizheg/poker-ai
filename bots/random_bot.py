from random import Random
from typing import Tuple

from engine.actions import Action
from engine.table import Table
from engine.rules import legal_actions
from bots.base import Bot

class RandomBot(Bot):
    """
    Chooses a legal action at random.
    """

    def __init__(self, seed: int = 42) -> None:
        self.rng: Random = Random(seed)

    def decide(self, table: Table) -> Tuple[Action, int]:
        action = self.rng.choice(legal_actions(table))
        return action
