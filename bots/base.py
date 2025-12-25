from abc import ABC, abstractmethod
from typing import Tuple

from engine.table import Table
from engine.actions import Action

class Bot(ABC):
    """
    Base class for all poker bots.
    Must implement `decide` method.
    """

    @abstractmethod
    def decide(self, table: Table) -> Tuple[Action, int]:
        """
        Given the current table state, return the next action and optional amount.

        Returns:
            action: Action (FOLD, CALL, CHECK, BET, RAISE)
            amount: int (for BET or RAISE; 0 otherwise)
        """
        pass
