"""Game state representation for Kuhn Poker."""

from dataclasses import dataclass

from .action import Action
from .card import Card


@dataclass
class GameState:
    """What a player can see during the game."""
    card: Card             # Player's card
    history: list[Action]  # Actions taken so far
    pot: int               # Current pot size
    player: int            # Whose turn (0 or 1)

    def is_terminal(self) -> bool:
        """Check if the game is over."""
        if not self.history:
            return False

        last = self.history[-1]

        # Fold ends the game
        if last == Action.FOLD:
            return True

        # Check-Check ends the game
        if len(self.history) >= 2 and self.history[-2:] == [Action.CHECK, Action.CHECK]:
            return True

        # Bet-Call ends the game
        if len(self.history) >= 2 and self.history[-2:] == [Action.BET, Action.CALL]:
            return True

        # Check-Bet-Call ends the game
        if len(self.history) >= 3 and self.history[-3:] == [Action.CHECK, Action.BET, Action.CALL]:
            return True

        return False

    def legal_actions(self) -> list[Action]:
        """Return legal actions for the current player."""
        if self.is_terminal():
            return []

        if not self.history:
            # First action: check or bet
            return [Action.CHECK, Action.BET]

        last = self.history[-1]

        if last == Action.CHECK:
            # After check: check or bet
            return [Action.CHECK, Action.BET]

        if last == Action.BET:
            # After bet: fold or call
            return [Action.FOLD, Action.CALL]

        return []