from competitive_sudoku.sudoku import GameState, Move, SudokuBoard
from .Extra import find_legal_moves, score_move
import time

def endgame(game_state):
    """
    tries to find a move that will be declared taboo
    :param game_state: The current gamestate
    :return:
    """

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
