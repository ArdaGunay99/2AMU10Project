#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

from itertools import filterfalse


class Cell:
    '''
    class to keep track of different properties of a cell in a board.
    '''
    def __init__(self, i:int, j:int):
        self.row_index = i #row index
        self.col_index = j #column index
        self.regions = []  #regions the cell belongs to (3 regions : row, column and block)
        self.values = []   #legal (non-taboo) values the cell can take, only used in specific scenarios


class AnaBoard(competitive_sudoku.sudoku.SudokuBoard):
    '''
    child of SudokuBoard. A board class with methods that will analyze the board and find the best move.
    '''
    def __init__(self, m:int = 3, n:int = 3):
        super().__init__(m, n)
        self.empty_cell_count = -1       #to keep track of how many turns remain
        self.region_dict = dict()        #to keep track of which regions have empty cells left and how many
        self.empty_cells = []            #to keep track of possible moves
        #anything else we need
        
    def find_empty_cells(self):
        '''
        loops over the board and updates the empty_cells list, as well empty_cell_count and region_dict
        '''
        N = self.N
        count = 0
        for f in range(N*N):
            if self.squares[f] == SudokuBoard.empty:
                #update count
                count += 1
                
                #add cell to empty_cells
                ij = self.f2rc(f)
                c = Cell(*ij)
                row = f'r{c.i}'  #row: 'ri'
                col = f'c{c.j}'  #column: 'cj'
                block = f'b{c.i//self.region_width()},{c.j//self.region_height()}' #block: 'bx,y'. e.g. Upperleft block is b0,0
                c.regions = [row, col, block] 
                self.empty_cells.append(c)
                
                #update region_dict
                if row in self.region_dict:
                    self.region_dict[row][0] += 1
                    if self.region_dict[row][0] < 3:
                        self.region_dict[row][1].append(c)
                else:
                    self.region_dict[row] = [1,[c]]
        #update count            
        self.empty_cell_count = count
        
        
    def get_best_move(self):
        '''
        divide the cells into four categories depending on how many regions they fill: 3, 2, 1 or none.
            
        -if there's a three-region move, take it.
        -if there's a two-region move, take it unless it opens up three regions.
            -if there's an even amount of two-region moves, prefer moves that open up another two-regions.
            -if there's an uneven amount of two-region moves, prefer moves that open up one or no regions.
        -if there's a one-region move, take it unless it opens up two or three regions.
            -if there's an even amount of one-region moves, prefer moves that open up another one-region move.
            -if there's an uneven amount of one-region moves, prefer moves that open up no regions.
        -if there's only moves that fill up no regions, take one that opens up no regions. If we are not set to have
         the endmove, try to taboo it.
        -if there's only moves that fill up no regions but do open up one or more regions, take the move that
         opens up the least regions. If we are not set to have the endmove, try to taboo it. If we ARE set to have
         the endmove, try to taboo it only if the only other option is opening up a three-region move.
         If then we can't taboo it, check one- and two-region moves that open up three-regions.
        '''
        
        

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

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
