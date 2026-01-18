"""Player interfaces for Kuhn Poker."""

import random
from abc import ABC, abstractmethod

from .action import Action
from .state import GameState


class Player(ABC):
    """Abstract base class for Kuhn Poker players."""

    @abstractmethod
    def get_action(self, state: GameState) -> Action:
        """Choose an action given the current game state."""
        pass


class RandomPlayer(Player):
    """Player that chooses randomly from legal actions."""

    def get_action(self, state: GameState) -> Action:
        return random.choice(state.legal_actions())


class HumanPlayer(Player):
    """Interactive human player."""

    def get_action(self, state: GameState) -> Action:
        print(f"\nYour card: {state.card.name.title()}")
        print(f"Pot: {state.pot}")

        if state.history:
            history_str = " -> ".join(a.value for a in state.history)
            print(f"History: {history_str}")

        actions = state.legal_actions()
        print(f"Legal actions: {[a.value for a in actions]}")

        while True:
            choice = input("Your action: ").strip().lower()
            for action in actions:
                if action.value == choice:
                    return action
            print(f"Invalid action. Choose from: {[a.value for a in actions]}")