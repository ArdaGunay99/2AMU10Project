from team5_A2.sudokuai import SudokuAI

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, load_sudoku_from_text
from pathlib import Path
import copy

#this file is used to test our AI using very specific circumstances.
#we manually make a gamestate by loading in a board
#and run the ai on the gamestate


board_text = Path("../boards/hard-3x3.txt").read_text()
board = load_sudoku_from_text(board_text)


game_state = GameState(board, copy.deepcopy(board), [], [], [0, 0])
player = SudokuAI()

player.compute_best_move(game_state)