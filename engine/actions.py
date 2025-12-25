from enum import Enum

class Action(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"

    def __repr__(self) -> str:
        return self.value