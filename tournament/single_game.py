from collections import defaultdict
from statistics import mean, pstdev

from engine.game import *
from bots.easy import EasyBot

def run_hands(num_hands: int, bots: list[Bot], rng: Random) -> None:
    n = len(bots)

    profit_history: dict[Bot, list[int]] = {b: [] for b in bots}
    win_counts: dict[Bot, int] = defaultdict(int)
    bust_counts: dict[Bot, int] = defaultdict(int)
    dealer_ev: dict[tuple[Bot, int], list[int]] = defaultdict(list)

    for hand_idx in range(num_hands):
        dealer = hand_idx % n
        initial_stacks = tuple([1000] * n)

        table = init_table(
            initial_stacks=initial_stacks,
            rng=rng,
            small_blind=10,
            big_blind=20,
            dealer_index=dealer,
        )

        shuffled_bots = rng.sample(bots, len(bots))

        table = play_hand(table, shuffled_bots, verbose=False)

        # sanity check
        assert sum(table.stacks) == sum(initial_stacks)

        for i, bot in enumerate(shuffled_bots):
            profit = table.stacks[i] - 1000
            profit_history[bot].append(profit)
            dealer_ev[(bot, i-dealer % len(bots))].append(profit)

            if profit > 0:
                win_counts[bot] += 1
            if table.stacks[i] == 0:
                bust_counts[bot] += 1

    print(f"{"Bot Name":16s} | {"Avg P&L (99% CI)":21s} | Win rate | Bust rate")
    print("-" * 64)
    for bot in bots:
        profits = profit_history[bot]
        print(f"{str(bot):16s} | {mean(profits):10.3f} ± {2.58 * pstdev(profits) / (num_hands) ** 0.5:8.2f} | {win_counts[bot] / num_hands:8.3f} | {bust_counts[bot] / num_hands:9.3f}")

    print("\n=== POSITIONAL EV (dealer-relative) ===")
    print(f"{"":14s} | " + " | ".join(f"D{str(j):15s}" for j in range(n)))
    for bot in bots:
        print(f"{str(bot):14s}", end="")
        for j in range(len(bots)):
            if dealer_ev[(bot, j)]:
                print(f" | {mean(dealer_ev[(bot, j)]):8.2f} ± {2.58 * pstdev(dealer_ev[(bot, j)]) / (len(dealer_ev[(bot, j)])) ** 0.5:8.2f} ", end="")
            else:
                print("N/A", end="\t")
        print()


if __name__ == "__main__":
    import random
    bots:list[Bot] = [RandomBot(seed=i) for i in range(3)]
    bots += [EasyBot()]

    rng = random.Random(42)
    run_hands(100000, bots, rng)