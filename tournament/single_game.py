from collections import defaultdict
from statistics import mean, pstdev

from engine.game import *
from bots.easy import EasyBot

def run_hands(num_hands: int, bots: list[Bot], rng: Random) -> None:
    n = len(bots)

    profit_history: dict[int, list[int]] = {i: [] for i in range(n)}
    win_counts: dict[int, int] = defaultdict(int)
    bust_counts: dict[int, int] = defaultdict(int)
    dealer_ev: dict[tuple[int, int], list[int]] = defaultdict(list)

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

        table = play_hand(table, bots)

        # sanity check
        assert sum(table.stacks) == sum(initial_stacks)

        for i in range(n):
            profit = table.stacks[i] - 1000
            profit_history[i].append(profit)
            dealer_ev[(i, dealer)].append(profit)

            if profit > 0:
                win_counts[i] += 1
            if table.stacks[i] == 0:
                bust_counts[i] += 1



    print(f"{"Bot Name":16s} | {"Avg P&L (99% CI)":21s} | Win rate | Bust rate")
    print("-" * 64)
    for i, bot in enumerate(bots):
        profits = profit_history[i]
        print(f"{str(bot):16s} | {mean(profits):10.3f} ± {2.58 * pstdev(profits) / (num_hands) ** 0.5:8.2f} | {win_counts[i] / num_hands:8.3f} | {bust_counts[i] / num_hands:9.3f}")

    print("\n=== POSITIONAL EV (dealer-relative) ===")
    print(f"{"":5s} | " + " | ".join(f"D{str(j):15s}" for j in range(n)))
    for i in range(len(bots)):
        print(f"P{str(i):4s}", end="")
        for j in range(len(bots)):
            if dealer_ev[(i, j)]:
                print(f" | {mean(dealer_ev[(i, j)]):8.2f} ± {2.58 * pstdev(dealer_ev[(i, j)]) / (len(dealer_ev[(i, j)])) ** 0.5:8.2f} ", end="")
            else:
                print("N/A", end="\t")
        print()


if __name__ == "__main__":
    import random
    bots:list[Bot] = [RandomBot(seed=i) for i in range(4)]
    bots += [EasyBot()]

    rng = random.Random(42)
    run_hands(100000, bots, rng)