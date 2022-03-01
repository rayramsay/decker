import sys
from enum import Enum, auto
from typing import List, Optional, Tuple, Union

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
    Q = 100
    QUIT = 100
    EXIT = 100

    def __repr__(self):
        return self.name


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
        allowed_directions: Optional[List[Enum]] = None
    ) -> None:
        if not self.is_valid_grid(grid):
            raise ValueError(f'Invalid grid: {grid}')
        self.grid = grid
        self.goal_card = goal_card
        self.starting_card = starting_card
        self.starting_card.is_faceup = True
        if not allowed_directions:
            self.allowed_diections = [
                Direction.N,
                Direction.S,
                Direction.E,
                Direction.W
            ]
        else:
            self.allowed_diections = allowed_directions
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
                        self.grid[i][j] = self.starting_card
                        self.player_location = (i, j)

    def _available_slots_in_grid(self) -> int:
        num_true = 0
        for row in self.grid:
            for elem in row:
                if elem is True:
                    num_true += 1
        return num_true

    def start(self) -> None:
        self.show()
        self.show_player_location()
        # TODO: Keep moving until...? Reach goal card?
        counter = 5
        while counter > 0:
            self._move()
            counter -= 1

    def _move(self) -> None:
        while True:
            try:
                direction = self._parse_input_direction(
                    input("Which direction do you want to move in? ")
                )
                if self._is_valid_move(direction):
                    self.player_location = self._new_location(direction)
                    i, j = self.player_location
                    self.grid[i][j].is_faceup = True
            except ValueError as e:
                print(e)
                continue
            break
        self.show()
        self.show_player_location()

    def _parse_input_direction(self, input: str) -> Enum:
        try:
            direction = Direction[input.upper()]
            if direction == Direction.Q:
                print('Goodbye!')
                sys.exit(0)
            assert direction in self.allowed_diections
            return direction
        except (KeyError, AssertionError):
            raise ValueError(f'Direction must be one of: {self.allowed_diections}')

    def _new_location(self, direction: Enum) -> Tuple[int, int]:
        ns, we = self.player_location
        if direction == Direction.N:
            ns -= 1
        elif direction == Direction.S:
            ns += 1
        elif direction == Direction.W:
            we -= 1
        elif direction == Direction.E:
            we += 1
        else:
            # TODO: NW, NE, SE, SW
            raise NotImplementedError
        return (ns, we)

    def _is_valid_move(self, direction: Enum) -> bool:
        ns, we = self._new_location(direction)
        try:
            self.grid[ns][we]
            assert (ns >= 0) and (we >= 0)
            assert isinstance(self.grid[ns][we], Card)
        except (IndexError, AssertionError):
            raise ValueError("You can't go off the map.")
        return True

    def show(self) -> None:
        # TODO: How to represent grids with empty spaces?
        print('\n'.join(''.join(str(i).center(5) for i in row) for row in self.grid))

    def show_player_location(self) -> None:
        i, j = self.player_location
        print(f'You are at: {self.grid[i][j]}')


if __name__ == "__main__":
    deck = PlayingCardDeck(aces_high=False)
    grid = CartaBoard.create_grid(4, 6)
    goal_card = PlayingCard(Suit('Hearts'), 2)
    starting_card = PlayingCard(Suit('Clubs'), 2)
    board = CartaBoard(deck, grid, goal_card, starting_card)
    board.start()
