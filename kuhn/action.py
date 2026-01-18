"""Actions available in Kuhn Poker."""

from enum import Enum


class Action(Enum):
    """The four possible actions in Kuhn Poker."""
    CHECK = "check"
    BET = "bet"
    CALL = "call"
    FOLD = "fold"