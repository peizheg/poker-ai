from engine.cards import Card, Suit, Rank
from engine.rng import RNG
from typing import TypeAlias

Deck: TypeAlias = tuple[Card, ...]

def create_deck() -> Deck:
    return tuple(Card(rank, suit) for rank in Rank for suit in Suit)

def shuffle_deck(deck: Deck, rng: RNG) -> Deck:
    temp_deck = list(deck)
    rng.shuffle(temp_deck)
    return tuple(temp_deck)

def deal_deck(deck: Deck, num_cards: int) -> tuple[Deck, Deck]:
    if num_cards > len(deck):
        raise ValueError("Not enough cards in deck")
    return deck[:num_cards], deck[num_cards:]


if __name__ == "__main__":
    import random

    deck: Deck = shuffle_deck(create_deck(), random.Random())
    hand, deck = deal_deck(deck, 2)
    print("Hand:", hand)
    print("Remaining deck size:", len(deck))