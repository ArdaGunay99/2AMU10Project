#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)
import random

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard
import competitive_sudoku.sudokuai
from .Helper_Functions import moves_left, find_legal_moves
from .Endgame import find_taboo_move
from .MCTS import MonteCarloNode
import copy
#import time

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    Uses a basic minimax tree.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        
        # Create a copy of the game_state instance, this is input for the MinimaxTree
        board_copy = SudokuBoard(game_state.board.m, game_state.board.n)
        board_copy.squares = game_state.board.squares.copy()
        game_copy = GameState(game_state.initial_board, board_copy,
                              game_state.taboo_moves.copy(), game_state.moves.copy(),
                              game_state.scores.copy())

        #play a random move so we don't get disqualified
        # self.propose_move(find_legal_moves(game_state, True))
        self.propose_move(find_legal_moves(game_state, give_first=True))

        # Check whether we are the first or the second player, also input for the MCTS
        if len(game_copy.moves) % 2 == 0:
            player_nr = 0
        else:
            player_nr = 1

        #find out how many points we are ahead/behind
        if player_nr == 0:
            current_score_difference = game_state.scores[0] - game_state.scores[1]
        else:  # player_nr == 2:
            current_score_difference = game_state.scores[1] - game_state.scores[0]

        moves_tbd = moves_left(board_copy)
        min_score = -999999 # minimum score for a move before we actually suggest it

        # if few moves are left, play using endgame mode rather than normal tactics:
        # try to play a taboo move on purpose to get the final move
        # we increase min_score so we don't undo this for a 1 point gain but do for eg. a 3 or 7 point gain
        if moves_tbd <= 2*board_copy.N + 1 - board_copy.N**0.5 and moves_tbd >= 3:
            #print(f"this might be the last choice, {moves_tbd} moves left")
            if moves_tbd % 2 == 0:
                #print("and we should taboo")
                taboo_move = find_taboo_move(game_state)
                if taboo_move is not None:
                    self.propose_move(taboo_move)
                min_score = 3
        best_moves, mediocre_moves, bad_moves = find_legal_moves(game_copy)
        # choose which lists of moves to consider, based on how many there are in each list
        if len(best_moves) > 1:
            moves = best_moves
        if len(best_moves) <= 1 and len(mediocre_moves) > 1:
            moves = best_moves+mediocre_moves
        else:
            moves = best_moves+mediocre_moves+bad_moves

        root = MonteCarloNode(self, game_copy, player_nr, moves)

        best_node = root.best_node()

        self.propose_move(best_node.parent_move)
