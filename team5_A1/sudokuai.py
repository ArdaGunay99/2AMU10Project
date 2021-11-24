#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        def possible(i, j, value):
            return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves

        all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(i, j, value)]
        move = random.choice(all_moves)
        self.propose_move(move)
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(all_moves))
            
#=====================================================================================
            
def score_move(board_state: SudokuBoard, move: Move) -> float:
    '''
    Parameters
    ----------
    board_state : SudokuBoard
        State of the current board BEFORE move is executed.
    move : Move
        Move to be executed, assumed to be legal.

    Returns
    -------
    float
        A measure of how likely the move is to lead to a new point.
        Should be in the range of [-1,1], with 1 definitely leading to a new point 
        and -1 very likely leading to the opponent scoring a new point.
    '''
    #apply move to the board, get new board
    #new_board = game_state.board.copy()
    new_board = SudokuBoard(board_state.m, board_state.n)
    new_board.squares = board_state.squares.copy()
    new_board.put(move.i,move.j,move.value)
    
    #count empty cells present in column, row, and block of the new move
    #column, just loop over all values with the correct column index and count empty values
    col_empty = 0
    move_col = move.j
    
    for i in range(new_board.N):
        if new_board.get(i,move_col) == new_board.empty:
            col_empty += 1
    
    #row, same strategy as for column
    row_empty = 0
    move_row = move.i
    
    for j in range(new_board.N):
        if new_board.get(move_row,j) == new_board.empty:
            row_empty += 1
    
    #block, figure out where the edges of the block reside by calculating the remainder of 
    #the fractions with block-width and -length
    block_empty = 0
    
    remainder_width = move_row % new_board.m
    left_border = move_row - remainder_width     #first index of current block
    right_border = left_border + new_board.m     #first index of next block
    
    remainder_length = move_col % new_board.n
    top_border = move_col - remainder_length     #first index of current block
    bottom_border = top_border + new_board.n     #first index of next block
    
    for i in range(left_border, right_border):
        for j in range(top_border, bottom_border):
            if new_board.get(i,j) == new_board.empty:
                block_empty += 1
    
    #compute column, row and block scores according to the heuristic
    if col_empty%2 == 0: #if there's an even number of empty cells
        col_score = 1 / (col_empty + 1)
    else: #if there's an uneven number of empty cells
        col_score = - (1 / col_empty)
        
    if row_empty%2 == 0:
        row_score = 1 / (row_empty + 1)
    else:
        row_score = - (1 / row_empty)
        
    if block_empty%2 == 0:
        block_score = 3 / (block_empty + 1)
    else:
        block_score = - (1 / block_empty)
        
    
    final_score = (col_score + row_score + block_score) / 3
                
    return final_score
    
