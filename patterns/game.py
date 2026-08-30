from typing import Any, Optional, Generator

def two_deep_copy(l: list[list[Any]]) -> list[list[Any]]:
    result = []

    for row in l:
        result.append(row.copy())

    return result

def three_deep_copy(l: list[list[list[Any]]]) -> list[list[list[Any]]]:
    result = []

    for tile in l:
        result.append(two_deep_copy(tile))

    return result

def is_subpattern(board: list[list[Optional[bool]]], tile: list[list[bool]], pos: tuple[int, int]) -> bool:
    y, x = pos

    for j, row in enumerate(tile):
        for i, e in enumerate(row):
            yp = y + j
            xp = x + i

            if not (0 <= xp < len(board[0]) and 0 <= yp < len(board)):
                return False

            if e != board[yp][xp]:
                return False

    return True

def get_subpatterns(board: list[list[Optional[bool]]], tile: list[list[bool]]) -> Generator[tuple[int, int], None, None]:
    for j in range(len(board)):
        for i in range(len(board[0])):
            if is_subpattern(board, tile, (j, i)):
                yield (j, i)

def count_subpatterns(board: list[list[Optional[bool]]], tile: list[list[bool]]) -> int:
    return len(list(get_subpatterns(board, tile)))

class Patterns:
    """
    Representation invariant:
    - self.first_tiles, self.second_tiles contain rectangular tiles
    """
    def __init__(self, n: int, m: int, first_tiles: list[list[list[bool]]], second_tiles: list[list[list[bool]]]) -> None:
        self.first_tiles = first_tiles
        self.second_tiles = second_tiles

        self.n = n
        self.m = m

        self.board: list[list[Optional[bool]]] = []

        for _ in range(m):
            new_row = []

            for _ in range(n):
                new_row.append(None)

            self.board.append(new_row)

        self.first = True

    def __str__(self) -> str:
        result = []

        for row in self.board:
            new_row = []

            for e in row:
                if e is None:
                    new_row.append('*')

                elif e:
                    new_row.append('o')

                else:
                    new_row.append('x')

            result.append(''.join(new_row))

        return '\n'.join(result)

    def copy(self) -> "Patterns":
        new_game = Patterns(self.n, self.m, three_deep_copy(self.first_tiles), three_deep_copy(self.second_tiles))

        new_game.board = two_deep_copy(self.board)
        new_game.first = self.first

        return new_game

    def all_moves(self) -> list[tuple[int, int]]:
        result = []

        for i, row in enumerate(self.board):
            for j, e in enumerate(row):
                if e is None:
                    result.append((i, j))

        return result

    def do_move(self, move: tuple[int, int]) -> None:
        y, x = move

        self.board[y][x] = self.first

        self.first = not self.first

    def first_player_turn(self) -> bool:
        return self.first

    def ended(self) -> bool:
        for row in self.board:
            for e in row:
                if e is None:
                    return False

        return True

    def score(self) -> tuple[int, int]:
        s1 = 0
        
        for tile in self.first_tiles:
            s1 += count_subpatterns(self.board, tile)

        s2 = 0

        for tile in self.second_tiles:
            s2 += count_subpatterns(self.board, tile)

        return s1, s2

    def winner(self) -> Optional[bool]:
        s1, s2 = self.score()

        if s1 == s2:
            return None

        return s1 > s2

TILES_1_1 = [
    [[True, False],
     [True, False]],
    [[False, True],
     [True, False]],
    [[True, False],
     [True, True]]
]

TILES_1_2 = [
    [[False, False],
     [True, True]],
    [[True, False],
     [False, True]],
    [[False, False],
     [True, False]]
]