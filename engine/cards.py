from enum import Enum
from dataclasses import dataclass

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

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
        rank = {
            2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'
        }[self.rank.value]

        return f"{rank}{self.suit.value}"

if __name__ == "__main__":
    card = Card(Rank.ACE, Suit.SPADE)
    print(card)