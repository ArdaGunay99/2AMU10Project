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
        root = MinimaxTree(game_state, game_state.moves[-1], 0) #note: move and score *should* not be used. Not sure though
        while True:
            root.add_layer()
            self.propose_move(root.get_best_move())




    def find_legal_moves(self, state: GameState) -> List[move]:
        """find legal moves (to be improved)"""
        return []

    def score_move(self, game_state: GameState, move: move) -> int:
        """scores a move (to be improved)"""
        return 0





class MinimaxTree():
    def __init__(self, game_state: GameState, move: Move, score: int):
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
            #recursion base: do nothing
            return
        else:
            #loop through children scores, update and get
            scores = []
            for child in self.children:
                child.update_score(not maximize)
                scores.append(child.score)
            if maximize == False:
                self.score = min(score)
            else:
                self.score = max(score)

    def add_layer_here(self):
        """
        Adds a layer to the tree with moves that can be played now and their scores.
        :return:
        """
        # find legal moves
        legal_moves = self.find_legal_moves(game_state)

        for move in legal_moves:
            #score move
            score = self.score_move(game_state, move)

            new_state = game_state.copy()
            new_state.put(*move)

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
        for child in children:
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

