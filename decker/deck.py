import random
from collections import deque
from enum import Enum, auto
from functools import total_ordering
from typing import Dict, List, Optional, Union


### HELPER FUNCTIONS ##########################################################

def default_court_mapping(aces_high: bool = True) -> Dict[int, str]:
    court_mapping = {11: 'J', 12: 'Q', 13: 'K'}
    if aces_high:
        court_mapping[14] = 'A'
    else:
        court_mapping[1] = 'A'
    return court_mapping


def shuffle(lst: Union[list, deque]) -> None:
    # Move through the list of cards backwards: start at last card, stop at
    # first card, -1 step.
    for i in range(len(lst) - 1, 0, -1):
        # Pick a random number to the left of our index position.
        r = random.randint(0, i)
        # Swap the two cards.
        lst[i], lst[r] = lst[r], lst[i]


### SUITS #####################################################################

class Color(Enum):
    RED = auto()
    BLACK = auto()

    def __str__(self):
        return self.name.capitalize()


@total_ordering
class Suit:
    def __init__(self, name: Optional[str], value: Optional[int] = None, color: Optional[Enum] = None) -> None:
        name = name.capitalize() if isinstance(name, str) else ''  # TODO: None?
        if not color:
            if name in {'Diamonds', 'Hearts'}:
                color = Color.RED
            elif name in {'Clubs', 'Spades'}:
                color = Color.BLACK
        value = int(value) if isinstance(value, int) else 0

        self.name = name
        self.value = value
        self.color = color
        self.short_name = self._shorten_name()

    def __repr__(self) -> str:
        return f'{self.name} ({self.value}), {self.color} {self.short_name}'

    def _shorten_name(self) -> Union[str, None]:
        conversion = {
            'Clubs': '\u2663',
            'Diamonds': '\u2666',
            'Hearts': '\u2665',
            'Spades': '\u2660',
            'Wands': '\u269A',
            'Coins': '\u235F',  # Alternative: '\u272A'
            'Cups': '\u222A',
            'Swords': '\u2694',
        }
        return conversion.get(self.name)

    def _is_valid_operand(self, other):
        return hasattr(other, "value")

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.value < other.value


# Fake enum of ordered suits for instantiating indvidual cards that compare
# correctly with those in the default PlayingCardDeck.
class Suits:
    CLUBS = Suit('Clubs', 1)
    DIAMONDS = Suit('Diamonds', 2)
    HEARTS = Suit('Hearts', 3)
    SPADES = Suit('Spades', 4)


### CARDS #####################################################################

class Card:
    def __init__(self) -> None:
        self.is_faceup = False

    def flip(self) -> None:
        self.is_faceup = not self.is_faceup

    def show(self) -> None:
        print(self)


@total_ordering
class PlayingCard(Card):
    def __init__(self, suit: Suit, value: int, court_mapping: Optional[Dict[int, str]] = None) -> None:
        self.suit = suit
        self.value = int(value)
        self.char_value = self._value_to_char(court_mapping)
        super().__init__()

    def __repr__(self) -> str:
        if not self.is_faceup:
            return 'XX'
        return self._get_str()

    def _get_str(self) -> str:
        value = self.char_value if self.char_value else self.value
        suit = self.suit.short_name if self.suit.short_name else self.suit.name
        if value != 'Jkr':
            spacer = '' if self.suit.short_name else ' of '
            return f'{value}{spacer}{suit}'
        else:
            return f'{self.suit.color} {value}'

    def show_reverse(self) -> None:
        print(self._get_str())

    def _value_to_char(self, court_mapping: Optional[Dict[int, str]]) -> Union[str, None]:
        if not court_mapping:
            court_mapping = dict()
        return court_mapping.get(self.value)

    def _is_valid_operand(self, other) -> bool:
        return (hasattr(other, "suit") and
                hasattr(other, "value"))

    def __eq__(self, other) -> bool:
        if not self._is_valid_operand(other):
            return NotImplemented
        return ((self.value, self.suit.value) ==
                (other.value, other.suit.value))

    def __lt__(self, other) -> bool:
        if not self._is_valid_operand(other):
            return NotImplemented
        return ((self.value, self.suit.value) <
                (other.value, other.suit.value))


### DECK ######################################################################

class Deck:
    def __init__(self) -> None:
        # TODO: Is a deque really the best data structure for this?
        # Concerns: shuffling involves a lot of look-ups by index, which
        # approximate O(n) toward the middle of the deque.
        self.cards = deque()

    def __len__(self) -> int:
        return len(self.cards)

    def show(self) -> None:
        print(self.cards)

    def shuffle(self) -> None:
        shuffle(self.cards)

    def peek(self) -> None:
        self.cards[0].show()

    def peek_bottom(self) -> None:
        self.cards[-1].show()

    def deal(self, n: int = 1) -> list:
        cards = []
        while n > 0:
            cards.append(self.cards.popleft())
            n -= 1
        return cards

    def take(self, card: Card) -> Union[Card, None]:
        try:
            i = self.cards.index(card)
        except ValueError:
            return None
        found_card = self.cards[i]
        self.remove(card)
        return found_card

    def remove(self, card: Card) -> None:
        self.cards.remove(card)


class PlayingCardDeck(Deck):
    def __init__(self, suits: Optional[List[Suit]] = None, court_mapping: Optional[Dict[int, str]] = None, aces_high: bool = True, include_jokers: bool = False):
        self.suits = [Suit(name=name, value=value) for value, name in enumerate(['Clubs', 'Diamonds', 'Hearts', 'Spades'], 1)] if not suits else suits
        self.court_mapping = default_court_mapping(aces_high) if not court_mapping else court_mapping
        self.aces_high = aces_high
        self.include_jokers = include_jokers
        super().__init__()
        self._build()

    def __repr__(self):
        return f'Deck of {len(self.cards)} cards. Suits: {self.suits} - Court mapping: {self.court_mapping} - Aces high? {self.aces_high} - Include jokers? {self.include_jokers}'

    def _build(self):
        min_range = 2 if self.aces_high else 1
        max_range = min_range + 13
        for suit in self.suits:
            for value in range(min_range, max_range):
                self.cards.append(PlayingCard(suit, value, self.court_mapping))
        if self.include_jokers:
            # Highest suit value and highest card value (for comparisons).
            jokers = [
                PlayingCard(Suit(name=None, value=len(self.suits) + 1, color=Color.RED), 16, {16: 'Jkr'}),
                PlayingCard(Suit(name=None, value=len(self.suits) + 1, color=Color.BLACK), 16, {16: 'Jkr'})
            ]
            self.cards.extend(jokers)


if __name__ == "__main__":
    deck = PlayingCardDeck()
    deck.shuffle()
    deck.show()
