#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import math


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    # N.B. This is a very naive implementation.
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N
        board = game_state.board

        def possible(i, j, value):
            return board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves

        # gets the values of non-empty cells in a row
        def get_row(i):
            row = []
            for j in range(N):
                if board.get(i, j) != SudokuBoard.empty:
                    row.append(board.get(i, j))
            return row

        # gets the values of non-empty cells in a column
        def get_column(j):
            column = []
            for i in range(N):
                if board.get(i, j) != SudokuBoard.empty:
                    column.append(board.get(i, j))
            return column

        # gets the values of non-empty cells in a block
        def get_block(i, j):
            block = []
            start_row = math.floor(i / board.m) * board.m
            start_col = math.floor(j / board.n) * board.n

            for row in range(start_row, start_row+board.m):
                for col in range(start_col, start_col+board.n):
                    if board.get(row, col) != board.empty:
                        block.append(board.get(row, col))
            return block

        # finds all possible legal moves in a given game state
        def find_legal_moves():
            N = board.N
            legal_moves = []
            for i in range(N):
                row = get_row(i)
                for j in range(N):
                    if board.get(i, j) == board.empty:
                        column = get_column(j)
                        block = get_block(i, j)
                        for value in range(1, N+1):
                            if possible(i, j, value):
                                if value in block or value in column or value in row:
                                    continue
                                else:
                                    legal_moves.append(Move(i, j, value))

            return legal_moves

        # all_moves = [Move(i, j, value) for i in range(N) for j in range(N) for value in range(1, N+1) if possible(i, j, value)]
        all_moves = find_legal_moves()
        move = random.choice(all_moves)
        self.propose_move(move)
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(all_moves))


