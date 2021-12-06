#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard
import competitive_sudoku.sudokuai
from .MinimaxTree import MinimaxTree
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
        
        # Check whether we are the first or the second player, also input for the Minimaxtree
        if len(game_copy.moves) % 2 == 0:
            player_nr = 1
        else:
            player_nr = 2
        
        # Use the Minimaxtree to get the best move, as described in the report
        root = MinimaxTree(game_copy, Move(0, 0, 0), 0, player_nr)
        moves_ahead = 0
        moves_tbd = moves_left(board_copy)
        while moves_ahead < moves_tbd:
            moves_ahead += 1
            # repeatedly look further into the future and get the best move found
            #start = time.time()
            root.add_layer()
            self.propose_move(root.get_best_move())
            print(f"layer {moves_ahead} added")

        #endgame mode: when <x moves left, try to make it so an odd number of moves left in duration of game, if even try to make taboo move