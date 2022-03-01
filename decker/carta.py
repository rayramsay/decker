from enum import Enum, auto
from typing import List, Optional, Union

from deck import Card, Deck, PlayingCard, PlayingCardDeck, Suit, shuffle


class Direction(Enum):
    N = auto()
    NW = auto()
    NE = auto()
    S = auto()
    SW = auto()
    SE = auto()
    E = auto()
    W = auto()


class CartaBoard:
    CartaGrid = List[List[Union[bool, Card]]]

    @staticmethod
    def create_grid(rows: int, columns: int) -> CartaGrid:
        grid = list()
        for _i in range(rows):
            row = list()
            for _j in range(columns):
                row.append(True)
            grid.append(row)
        return grid

    @classmethod
    def is_valid_grid(cls, grid: CartaGrid) -> bool:
        first_row_len = len(grid[0])
        for row in grid:
            if len(row) != first_row_len:
                return False
            for elem in row:
                if not isinstance(elem, bool):
                    return False
        return True

    def __init__(
        self,
        deck: Deck,
        grid: CartaGrid,
        goal_card: Card,
        starting_card: Card,
        allowed_directions: Optional[List[Enum]] = None  # TODO
    ) -> None:
        if not self.is_valid_grid(grid):
            raise ValueError(f'Invalid grid: {grid}')
        self.grid = grid
        self.goal_card = goal_card
        self.starting_card = starting_card
        self.starting_card.is_faceup = True
        self._build(deck)

    def _build(self, deck: Deck):
        deck.remove(self.starting_card)
        deck.remove(self.goal_card)
        deck.shuffle()

        grid_cards: List[Card] = deck.deal((self._available_slots_in_grid() - 2))
        grid_cards.append(self.goal_card)
        shuffle(grid_cards)

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if self.grid[i][j] is True:
                    if grid_cards:
                        self.grid[i][j] = grid_cards.pop()
                    else:
                        # When out of grid cards, place starting card and set marker.
                        self.grid[i][j] = self.starting_card
                        self.player_location = (i, j)

    def _available_slots_in_grid(self) -> int:
        num_true = 0
        for row in self.grid:
            for elem in row:
                if elem is True:
                    num_true += 1
        return num_true

    def show(self) -> None:
        print('\n'.join(''.join(str(i).center(5) for i in row) for row in self.grid))

    def player_card(self) -> None:
        i, j = self.player_location
        print(f'You are at: {self.grid[i][j]}')


if __name__ == "__main__":
    deck = PlayingCardDeck(aces_high=False)
    grid = CartaBoard.create_grid(4, 6)
    goal_card = PlayingCard(Suit('Hearts'), 2)
    starting_card = PlayingCard(Suit('Clubs'), 2)
    board = CartaBoard(deck, grid, goal_card, starting_card)
    board.show()
    board.player_card()
