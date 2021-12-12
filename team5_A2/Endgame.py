from competitive_sudoku.sudoku import GameState, Move, SudokuBoard
from .Extra import get_block, get_column, get_row
import time

def find_taboo_move(game_state):
    """
    tries to find a move that will be declared taboo
    :param game_state: The current game_state
    :return:
    """

    board = game_state.board
    N = board.N

    for i in range(N):
        for j in range(N):
            #check if square is empty & has only 1 choice
            if board.get(i, j) == board.empty:
                value = None
                for k in range(1, N+1):
                    if possible(i, j, k, board, game_state):
                        if value == None:
                            value = k
                        else:
                            value = None
                            break
                if value == None:
                    #the square has multiple options. We will skip it
                    continue
                #see if we can find a taboo move in this same row, column or block
                for row_nr in range(N):
                    if i == row_nr:
                        #this is the current coordinate already
                        continue
                    elif board.get(row_nr, j) == board.empty:
                        if possible(row_nr, j, value, board, game_state):
                            return Move(row_nr, j, value)
                for col_nr in range(N):
                    if j == col_nr:
                        #this is the current coordinate already
                        continue
                    elif board.get(i, col_nr) == board.empty:
                        if possible(i, col_nr, value, board, game_state):
                            return Move(i, col_nr, value)
                #blocks suck btw
                start_row = math.floor(i / board.m) * board.m
                # column index of the top left cell of the block
                start_col = math.floor(j / board.n) * board.n
                # check block for the value
                for row in range(start_row, start_row + board.m):
                    for col in range(start_col, start_col + board.n):
                        if row == i and col == j:
                            continue
                        elif board.get(row, col) == board.empty:
                            if possible(row, col, value, board, game_state):
                                return Move(row, col, value)

    # find a region with a forced move (eg. a row with 1 open field)
    # find an open field that shares a region with it
    # see if you can play the number needed in the forced move in this field
    #     1     2     3     4
    #   ╔═════╤═════╦═════╤═════╗
    # 1 ║  -  │  -  ║  3  │  1  ║
    # 2 ║  -  │  -  ║  2  │  4  ║
    #   ╠═════╪═════╬═════╪═════║
    # 3 ║  4  │  2  ║  1  │  3  ║
    # 4 ║  -  │  3  ║  4  │  2  ║
    #   ╚═════╧═════╩═════╧═════╝
    # eg.: here play (2,1) -> 1, to prevent the forced move on the bottom row

    #finding a forced move:
    #this probably implemented by rozanne!


