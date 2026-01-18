"""Kuhn Poker game engine."""

from .action import Action
from .deck import Deck
from .state import GameState
from .player import Player


class KuhnPoker:
    """Kuhn Poker game for 2 players."""

    def __init__(self):
        self._deck = Deck()
        self._current_player: int = 0
        self.reset()

    def reset(self) -> None:
        """Start a new hand."""
        self._deck.reset()
        self._cards = [self._deck.deal(), self._deck.deal()]
        self._history: list[Action] = []
        self._pot = 2  # Both players ante 1
        self._current_player = 0

    def get_state(self, player: int) -> GameState:
        """Get the game state from a player's perspective."""
        return GameState(
            card=self._cards[player],
            history=self._history.copy(),
            pot=self._pot,
            player=self._current_player
        )
    
    def is_terminal(self) -> bool:
        """Check if the game is over."""
        return self.get_state(0).is_terminal()

    def apply_action(self, action: Action) -> None:
        """Apply an action to the game."""
        state = self.get_state(self._current_player)

        if state.is_terminal():
            raise ValueError("Game is already over")

        if action not in state.legal_actions():
            raise ValueError(f"Illegal action: {action}")

        self._history.append(action)

        if action == Action.BET:
            self._pot += 1
        elif action == Action.CALL:
            self._pot += 1

        # Switch player
        self._current_player = not self._current_player

    def get_payoffs(self) -> tuple[int, int]:
        """Get the payoffs for each player."""
        if not self.is_terminal():
            raise ValueError("Game is not over")

        last_action = self._history[-1]

        if last_action == Action.FOLD:
            # After fold, _current_player points to the winner
            winner = self._current_player
            winnings = 1  # Folder loses their ante
        else:
            # Showdown - higher card wins
            if self._cards[0] > self._cards[1]:
                winner = 0
            else:
                winner = 1
            winnings = self._pot // 2
        if winner == 0:
            return (winnings, -winnings)
        else:
            return (-winnings, winnings)

    def play(self, players: list[Player], verbose: bool = False) -> tuple[int, int]:
        """Play a full game with the given players. Returns payoffs."""
        self.reset()

        if verbose:
            print(f"Cards dealt: P0={self._cards[0]}, P1={self._cards[1]}")

        while not self.is_terminal():
            current = self._current_player
            state = self.get_state(current)
            action = players[current].get_action(state)
            if verbose:
                print(f"Player {current} ({self._cards[current]}): {action.value}")
            self.apply_action(action)

        payoffs = self.get_payoffs()
        if verbose:
            print(f"Result: P0={payoffs[0]:+d}, P1={payoffs[1]:+d}")

        return payoffs

    def __str__(self) -> str:
        history_str = "-".join(a.value for a in self._history) if self._history else "start"
        return f"P0:{self._cards[0]} P1:{self._cards[1]} | {history_str} | pot:{self._pot}"