#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from typing import List
import math


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    Uses a basic minimax tree.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        board_copy = SudokuBoard(game_state.board.m, game_state.board.n)
        board_copy.squares = game_state.board.squares.copy()
        game_copy = GameState(game_state.initial_board, board_copy,
                              game_state.taboo_moves.copy(), game_state.moves.copy(),
                              game_state.scores.copy())
        root = MinimaxTree(game_copy, (0, 0, 0), 0)  # note: move and score *should* not be used. Not sure though
        while True:
            root.add_layer()
            self.propose_move(root.get_best_move())

def possible(i, j, value, game_state):
    return not TabooMove(i, j, value) in game_state.taboo_moves

# gets the values of non-empty cells in a row
def get_row(i, board):
    N = board.N
    row = []
    for j in range(N):
        if board.get(i, j) != SudokuBoard.empty:
            row.append(board.get(i, j))
    return row

# gets the values of non-empty cells in a column
def get_column(j, board):
    N = board.N
    column = []
    for i in range(N):
        if board.get(i, j) != SudokuBoard.empty:
            column.append(board.get(i, j))
    return column

# gets the values of non-empty cells in a block
def get_block(i, j, board):
    N = board.N
    block = []
    start_row = math.floor(i / board.m) * board.m
    start_col = math.floor(j / board.n) * board.n

    for row in range(start_row, start_row + board.m):
        for col in range(start_col, start_col + board.n):
            if board.get(row, col) != board.empty:
                block.append(board.get(row, col))
    return block

# finds all possible legal moves in a given game state
def find_legal_moves(game_state):
    board = game_state.board
    N = board.N
    legal_moves = []
    for i in range(N):
        row = get_row(i, board)
        for j in range(N):
            if board.get(i, j) == board.empty:
                column = get_column(j, board)
                block = get_block(i, j, board)
                for value in range(1, N + 1):
                    if possible(i, j, value, game_state):
                        if value in block or value in column or value in row:
                            continue
                        else:
                            legal_moves.append(Move(i, j, value))

    return legal_moves


def score_move(game_state: GameState, move: Move, opponent: bool=False) -> float:
    '''
    Parameters
    ----------
    board_state : SudokuBoard
        State of the current board BEFORE move is executed.
    move : Move
        Move to be executed, assumed to be legal.
    opponent : bool
        Boolean indicating whether the move is being executed by us or by our
        opponent. When True, scores are multiplied by -1 before being returned.

    Returns
    -------
    float
        A measure of how likely the move is to lead to a new point for us and no
        new point for our opponent.
    '''
    board_state = game_state.board
    #create a copy of the board and apply the move to it
    new_board = SudokuBoard(board_state.m, board_state.n)
    new_board.squares = board_state.squares.copy()
    new_board.put(move.i,move.j,move.value)
    
    #count the empty cells present in the column, row, and block of the new move
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
    
    #block...
    block_empty = 0
    
    #first find out where the borders of the block reside
    remainder_width = move_row % new_board.m
    left_border = move_row - remainder_width     #first index of current block
    right_border = left_border + new_board.m     #first index of next block
    
    remainder_length = move_col % new_board.n
    top_border = move_col - remainder_length     #first index of current block
    bottom_border = top_border + new_board.n     #first index of next block
    
    #then use the borders to loop over each tile in the block and count the emptys.
    for i in range(left_border, right_border):
        for j in range(top_border, bottom_border):
            if new_board.get(i,j) == new_board.empty:
                block_empty += 1
    
    #compute column, row and block scores by applying the weighting function (see report)
    if col_empty%2 == 0: #if there's an even number of empty cells
        col_score = 3 / (col_empty + 1)
    else: #if there's an uneven number of empty cells
        col_score = - (3 / col_empty)
        
    if row_empty%2 == 0:
        row_score = 3 / (row_empty + 1)
    else:
        row_score = - (3 / row_empty)
        
    if block_empty%2 == 0:
        block_score = 3 / (block_empty + 1)
    else:
        block_score = - (3 / block_empty)
        
    
    final_score = (col_score + row_score + block_score) / 3
    
    #return the negative of the final score if the opponent is the one executing it.
    if opponent:
        return -final_score
                
    return final_score
  

class MinimaxTree():
    def __init__(self, game_state: GameState, move: Move, score: float):
        self.game_state = game_state
        self.move = move
        self.score = score
        self.children = [] #contains a list of trees showing moves that can be played from here

    def update_score(self, maximize: bool):
        """
        Recursively updates child scores then takes them and either maximizes or minimizes score, flipping each turn.

        :param maximize: whether to maximize (true) or minimize (false) the score on this node
        :return: None
        """

        if self.children == []:
            # recursion base: do nothing (using the score that was decided when the node was made)
            return
        else:
            # loop through children scores, update and get
            scores = []
            for child in self.children:
                child.update_score(not maximize) #note: this still needs editing, probably?
                scores.append(child.score)
            if maximize == False:
                self.score = min(scores)
            else:
                self.score = max(scores)

    def add_layer_here(self):
        """
        Adds a layer to the tree with moves that can be played now and their scores.
        :return:
        """
        # find legal moves
        legal_moves = find_legal_moves(self.game_state)

        for move in legal_moves:
            #score move
            score = score_move(self.game_state, move)

            new_board = SudokuBoard(self.game_state.board.m, self.game_state.board.n)
            new_board.squares = self.game_state.board.squares.copy()
            new_board.put(move.i, move.j, move.value)
            new_state = GameState(self.game_state.initial_board, new_board,
                                  self.game_state.taboo_moves.copy(), self.game_state.moves.copy(),
                                  self.game_state.scores.copy())

            #add it to the children
            self.children.append(MinimaxTree(new_state, move, score))

    def add_layer(self):
        """
        Goes to the bottom of the tree and adds a layer there
        :return: None
        """

        if len(self.children) > 0:
            for child in self.children:
                child.add_layer()
        else:
            self.add_layer_here()

    def get_best_move(self) -> Move:
        """
        Gets the best move by updating the score of the entire tree,
        then suggesting the move made by the child with the best score.
        :return: Move
        """
        self.update_score(True)

        best_score = -99999999
        best_move = None
        for child in self.children:
            if child.score > best_score:
                best_score = child.score
                best_move = child.move
        return(best_move)







#to write:
#function: find_legal_moves
#function: score_state, providing state
#idea: make moves that do not give winning move to your opponent
#after your move, even nr cells to a scoring move as much as possible, lower even is better, higher odd is less bad
#function: minimax_tree: given gamestate, returns a list of tuples with: gamestate after, move played, score after it was played
#function: compute best move

#minimax tree shape:
#dict
##keys: tuple[gamestate, move, int]
##values: list[minimax_tree]

            

    

