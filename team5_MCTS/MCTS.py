import numpy as np
from collections import defaultdict
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
from competitive_sudoku.sudokuai import SudokuAI
from .Helper_Functions import find_legal_moves, score_move, moves_left, is_only_empty_in_col, is_only_empty_in_row, is_only_empty_in_block
from copy import deepcopy


class MonteCarloNode:
    def __init__(self, sudokuAI: SudokuAI, game_state: GameState, player_number: int, legal_moves: list, parent=None, parent_move=None):
        self.game_state = game_state
        self.parent = parent
        self.parent_move = parent_move
        self.children = []
        self.number_of_visits = 0
        self.results = defaultdict(int)
        self.results[1] = 0
        self.results[0] = 0
        self.results[-1] = 0
        self.legal_moves = legal_moves
        self.player_number = player_number
        self.sudokuAI = sudokuAI
        return

    def q(self):
        wins = self.results[1]
        loses = self.results[-1]
        return wins - loses

    def n(self):
        return self.number_of_visits

    def expand(self):
        # move = self.legal_moves.pop()
        move = self.legal_moves[-1]
        moves_to_remove = []

        for i in range(len(self.legal_moves)):
            if self.legal_moves[i].i == move.i and self.legal_moves[i].j == move.j:
                moves_to_remove.append(self.legal_moves[i])

        for i in range(len(moves_to_remove)):
            self.legal_moves.remove(moves_to_remove[i])

        next_state = deepcopy(self.game_state)
        next_state.board.put(move.i, move.j, move.value)
        child_node = MonteCarloNode(self.sudokuAI, next_state, self.player_number, self.legal_moves, parent=self, parent_move=move)

        self.children.append(child_node)
        return child_node

    def is_end_node(self):
        return moves_left(self.game_state.board) == 0

    def calculate_move_score(self, game_state: GameState, move: Move):
        total = 0
        board = game_state.board
        if is_only_empty_in_row(move.i, board):
            total += 1
        if is_only_empty_in_col(move.j, board):
            total += 1
        if is_only_empty_in_block(move.i, move.j, board):
            total += 1
        if total == 0:
            return 0
        elif total == 1:
            return 1
        elif total == 2:
            return 3
        elif total == 3:
            return 7

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]

    def rollout(self):
        current_rollout_state = self.game_state

        if self.player_number == 0:
            agent_score = current_rollout_state.scores[self.player_number]
            opponent_score = current_rollout_state.scores[1]
        else:
            agent_score = current_rollout_state.scores[self.player_number]
            opponent_score = current_rollout_state.scores[0]

        # possible_moves = find_legal_moves(game_state=current_rollout_state, return_all=True)
        possible_moves = self.legal_moves
        moves_made = 0
        while not len(possible_moves) == 0:

            move = self.rollout_policy(possible_moves)
            # possible_moves.remove(move)
            moves_to_remove = []
            for i in range(len(possible_moves)):
                if possible_moves[i].i == move.i and possible_moves[i].j == move.j:
                    moves_to_remove.append(possible_moves[i])

            for i in range(len(moves_to_remove)):
                possible_moves.remove(moves_to_remove[i])

            if moves_made % 2 == 0:
                agent_score += self.calculate_move_score(current_rollout_state, move)
            else:
                opponent_score += self.calculate_move_score(current_rollout_state, move)

            current_rollout_state = deepcopy(self.game_state)
            current_rollout_state.board.put(move.i, move.j, move.value)
        if agent_score > opponent_score:
            return 1
        elif opponent_score > agent_score:
            return -1
        elif opponent_score == agent_score:
            return 0

    def backpropagate(self, result):
        self.number_of_visits += 1.
        self.results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.legal_moves) == 0

    def best_child(self, c_param=0.1):
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def _tree_policy(self):

        current_node = self
        while not current_node.is_end_node():

            if not current_node.is_fully_expanded():
                return current_node.expand()
            elif len(current_node.children) != 0:
                current_node = current_node.best_child()
        return current_node

    def best_node(self):
        simulation_no = 50

        for i in range(simulation_no):
            v = self._tree_policy()
            reward = v.rollout()
            print("reward calculated")
            v.backpropagate(reward)
            print("backpropagated")
            self.sudokuAI.propose_move(self.best_child(c_param=np.sqrt(2)).parent_move)
            print("a move is proposed")

        return self.best_child(c_param=0.1)
