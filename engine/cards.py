from enum import Enum
from dataclasses import dataclass

class Rank(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

class Suit(Enum):
    HEART = "♥"
    CLUBS = "♣"
    DIAMOND = "♦"
    SPADE = "♠"

@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __repr__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"

if __name__ == "__main__":
    card = Card(Rank.ACE, Suit.SPADE)
    print(card)