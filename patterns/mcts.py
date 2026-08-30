from typing import Generic, TypeVar, Optional, Callable
import math
import random

Move = TypeVar('Move')

class Game(Generic[Move]):
    """
    Abstract class
    """
    def copy(self) -> "Game[Move]":
        raise NotImplementedError()

    def all_moves(self) -> list[Move]:
        raise NotImplementedError()

    def do_move(self, move: Move) -> None:
        raise NotImplementedError()

    def first_player_turn(self) -> bool:
        raise NotImplementedError()

    def ended(self) -> bool:
        raise NotImplementedError()

    def winner(self) -> Optional[bool]:
        raise NotImplementedError()

class _Node(Generic[Move]):
    def __init__(self,
                 parent: Optional["_Node[Move]"],
                 game: Game[Move],
                 move: Optional[Move],
                 first_player: bool) -> None:
        self.parent = parent
        self.game = game
        self.move = move
        self.first_player = first_player

        self.children: list["_Node[Move]"] = []

        self.visits = 0
        self.value = 0.

        self.untried = game.all_moves()

    def terminal(self) -> bool:
        return self.game.ended()

    def fully_expanded(self) -> bool:
        return len(self.untried) == 0

    def expand(self) -> "_Node[Move]":
        new_move = random.choice(self.untried)
        self.untried.remove(new_move)

        new_game = self.game.copy()
        new_game.do_move(new_move)

        new_first_player = not self.first_player

        new_node = _Node(self, new_game, new_move, new_first_player)

        self.children.append(new_node)

        return new_node

    def backpropagate(self, score: float) -> None:
        curr = self

        while curr is not None:
            curr.visits += 1
            curr.value += score

            curr = curr.parent
            score = -score

def uct(node: _Node[Move], c: float) -> float:
    if node.visits == 0:
        return float('inf')

    exploitation = -node.value / node.visits
    exploration = c * math.sqrt(math.log(node.parent.visits) / node.visits)

    return exploitation + exploration

def rand_simulation(node: _Node[Move]) -> float:
    sim_game = node.game.copy()

    while not sim_game.ended():
        move = random.choice(sim_game.all_moves())

        sim_game.do_move(move)

    winner = sim_game.winner()

    if winner is None:
        return 0.

    if winner == node.first_player:
        return 1.

    return -1.

def make_root(game: Game[Move], first_player: bool) -> _Node[Move]:
    return _Node(None, game.copy(), None, first_player)

class MCTS(Generic[Move]):
    def __init__(self,
                 root: _Node[Move],
                 c: float,
                 simulation: Callable[[_Node[Move]], float],
                 n_iterations: int) -> None:
        self.root = root
        self.c = c
        self.simulation = simulation
        self.n_iterations = n_iterations

    def select(self) -> _Node[Move]:
        curr = self.root

        while not curr.terminal() and curr.fully_expanded():
            curr = max(curr.children, key = lambda node: uct(node, self.c))

        return curr

    def update(self) -> None:
        selected = self.select()

        if selected.terminal():
            winner = selected.game.winner()

            if winner is None:
                selected.backpropagate(0.)
                return

            score = -1.

            if selected.first_player == winner:
                score = 1.

            selected.backpropagate(score)
            return

        expanded = selected.expand()

        score = self.simulation(expanded)

        expanded.backpropagate(score)

    def find_move(self) -> Move:
        for _ in range(self.n_iterations):
            self.update()

        result =  max(self.root.children, key = lambda node: node.visits)

        return result.move

def find_move(game: Game[Move],
                   first_player: bool,
                   c: float,
                   simulation: Callable[[_Node[Move]], float],
                   n_iterations: int) -> Move:
    root = make_root(game, first_player)

    mcts = MCTS(root, c, simulation, n_iterations)

    return mcts.find_move()