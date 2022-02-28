from enum import Enum, auto
from typing import List

from deck import PlayingCard, Suits, PlayingCardDeck, shuffle


class direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()


class CartaBoard:
    def __init__(self, rows: int, columns: int, goal_card: PlayingCard, starting_card: PlayingCard):
        self.grid: List[list] = [[None] * columns] * rows
        self.goal_card = goal_card
        self.starting_card = starting_card
        self.player_location = (-1, -1)
        self._build(rows, columns)

    def _build(self, rows, columns):
        deck = PlayingCardDeck(aces_high=False)
        deck.remove(self.starting_card)
        deck.remove(self.goal_card)
        deck.shuffle()
        grid_cards: List[PlayingCard] = deck.deal((rows * columns) - 2)
        grid_cards.append(self.goal_card)
        shuffle(grid_cards)
        for i in range(rows):
            row = []
            for j in range(columns):
                if grid_cards:
                    row.append(grid_cards.pop())
            self.grid[i] = row
        self.starting_card.is_faceup = True
        self.grid[-1].append(self.starting_card)

    def show(self):
        print('\n'.join(''.join(str(i).center(4) for i in row) for row in self.grid))

    def player_card(self):
        i, j = self.player_location
        print(f'You are at: {self.grid[i][j]}')


if __name__ == "__main__":
    goal_card = PlayingCard(Suits.HEARTS, 2)
    starting_card = PlayingCard(Suits.CLUBS, 2)
    board = CartaBoard(4, 6, goal_card, starting_card)
    board.show()
    board.player_card()
