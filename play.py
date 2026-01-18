"""Example script to play Kuhn Poker."""

from kuhn.game import KuhnPoker
from kuhn.player import Player, RandomPlayer


def main():
    game = KuhnPoker()

    # Two random bots playing against each other
    players: list[Player] = [RandomPlayer(), RandomPlayer()]

    print("=== Kuhn Poker Demo ===\n")
    print("Running 1000 games between two random players...\n")

    total_payoffs = [0, 0]
    for _ in range(1000):
        payoffs = game.play(players)
        total_payoffs[0] += payoffs[0]
        total_payoffs[1] += payoffs[1]

    print(f"Player 0 total: {total_payoffs[0]:+d}")
    print(f"Player 1 total: {total_payoffs[1]:+d}")
    print(f"\nAverage per game: P0={total_payoffs[0]/1000:+.3f}, P1={total_payoffs[1]/1000:+.3f}")

    # Play a single game with verbose output
    print("\n\n=== Single Game Example ===\n")
    game.play(players, verbose=True)


if __name__ == "__main__":
    main()