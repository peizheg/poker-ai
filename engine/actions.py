from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ActionType(Enum):
    FOLD = 0
    CHECK = 1
    CALL = 2
    BET = 3
    RAISE = 4

@dataclass(frozen=True)
class Action:
    type: ActionType
    amount: Optional[int] = None
