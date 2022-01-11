#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

from random import choice
import warnings

class Cell:
    '''
    class to keep track of different properties of a cell in a board.
    '''
    def __init__(self, i:int, j:int):
        self.i = i #row index
        self.j = j #column index
        self.regions = []  #regions the cell belongs to (3 regions : row, column and block)
        self.point_regions = [] #regions for which the current is the only empty one left, filling it results in points
        self.penalty_regions = [] #regions for which the current is one of two empty cells left, filling it results in opening a move that scores points to the opponent
        self.values = set()   #legal (non-taboo) values the cell can take


class AnaBoard(competitive_sudoku.sudoku.SudokuBoard):
    '''
    child of SudokuBoard. A board class with methods that will analyze the board and find the best move.
    '''
    def __init__(self, m:int, n:int, taboo_moves):
        super().__init__(m, n)
        self.taboo_moves = taboo_moves   #taboo moves from the gamestate
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
                block = f'b{c.i//self.n},{c.j//self.m}' #block: 'bx,y'. e.g. Upperleft block is b0,0
                c.regions = [row, col, block] 
                self.empty_cells.append(c)
                
                #update region_dict
                if row in self.region_dict:
                    if self.region_dict[row][0] < 3:
                        self.region_dict[row][0] += 1
                        self.region_dict[row][1].append(c)
                else:
                    self.region_dict[row] = [1,[c]]
                    
                if col in self.region_dict:
                    if self.region_dict[col][0] < 3:
                        self.region_dict[col][0] += 1
                        self.region_dict[col][1].append(c)
                else:
                    self.region_dict[col] = [1,[c]]
                    
                if block in self.region_dict:
                    if self.region_dict[block][0] < 3:
                        self.region_dict[block][0] += 1
                        self.region_dict[block][1].append(c)
                else:
                    self.region_dict[block] = [1,[c]]
            
        #update count            
        self.empty_cell_count = count
            
        
    def get_best_move(self):
        '''
        divide the cells into four categories depending on how many regions they fill: 3, 2, 1 or none.
        '''
        #divide the empty cells into categories depending on how effective the moves would be
        reg3 = [] #moves that fill up three regions
        reg2 = [] #moves that fill up two regions
        reg1 = [] #moves that fill up one region
        reg0 = [] #moves that fill up no regions AND create no region-filling moves for the opponent
        bad = []  #moves that fill up no regions AND create region-filling move(s) for the opponent (hence, bad)
        
        for c in self.empty_cells:
            region_fills = 0
            creates_moves = False
            for r in c.regions:
                if self.region_dict[r][0] == 1:
                    region_fills += 1
                    c.point_regions.append(r)
                elif self.region_dict[r][0] == 2:
                    creates_moves = True
                    c.penalty_regions.append(r)
            
            if region_fills == 3:
                reg3.append(c)
            elif region_fills == 2:
                reg2.append(c)
            elif region_fills == 1:
                reg1.append(c)
            elif not creates_moves:
                reg0.append(c)
            else:
                bad.append(c)
        
        #now choose the best move from the best category
        #if there is at least one move that fills three regions, take it. Doesn't matter which
        if len(reg3) > 0:
            return choice(reg3) #select one randomly
        
        #if there are no three-region moves, and at least one two-region move, check if it's worth taking...
        if len(reg2) > 0:
            pen2 = []      #moves that open up a three-region move for the opponent
            no_pen2 = []   #moves that don't open up a three-region move for the opponent
            for c1 in reg2:
                if len(c1.penalty_regions) > 0:       #if there's a penalty region for this move...
                    pr = c1.penalty_regions[0]        #there is only one as the other two are point-regions
                    for c2 in self.region_dict[pr][1]:  
                        if c2 != c1:                      #find the other empty cell in that region
                            #start with a value of 1, as pr will be a region filled but is still in region_dict as having 2 empty cells
                            region_fills = 1
                            for r in c2.regions:
                                if self.region_dict[r][0] == 1: #keep track of how many regions that move would fill
                                    region_fills += 1
                            if region_fills == 3:        #if it fills three regions, it's a no-go
                                pen2.append(c1)
                            else:
                                no_pen2.append(c1)
                else:
                    no_pen2.append(c1) #if the move doesn't open up any new moves it's also no-penalty
            
            if len(no_pen2) > 0: 
                #if there are moves that fill two regions and don't create three-region moves for the opponent
                return choice(no_pen2) #select one randomly
        
        #if there are no two- or three-region moves, and at least one one-region move, check if it's worth taking...
        if len(reg1) > 0:
            #procedure for one-region moves is almost the same as for two-region moves
            pen12 = []
            pen13 = []
            no_pen1 = []
            for c1 in reg1:
                if len(c1.penalty_regions) > 0:
                    for pr in c1.penalty_regions:           #we actually loop now because there could be more than 1 penalty region
                        for c2 in self.region_dict[pr][1]:
                            if c2 != c1:
                                region_fills += 1
                                for r in c2.regions:
                                    if self.region_dict[r][0] == 1:
                                        region_fills += 1
                                if region_fills == 2: #if it fills two or three regions, it's a no-go
                                    pen12.append(c1)
                                elif region_fills == 3:
                                    pen13.append(c1)
                                else:
                                    no_pen1.append(c1)
                else:
                    no_pen1.append(c1)
            
            if len(no_pen1) > 0:
                return choice(no_pen1)
        
        #if there are no moves at all that score points and are worth taking, take a neutral move
        if len(reg0) > 0:
            return choice(reg0)
        
        #if there isn't even a neutral move, we cut our losses as best we can
        #we divide the remaining moves into categories as above, based on their penalties
        pen01 = []
        pen02 = []
        pen03 = []
        
        for c1 in bad:
            for pr in c1.penalty_regions:
                for c2 in self.region_dict[pr][1]:
                    if c2 != c1:
                        region_fills = 1
                        for r in c2.regions:
                            if self.region_dict[r][0] == 1:
                                region_fills += 1
                        if region_fills == 3:
                            pen03.append(c1)
                        elif region_fills == 2:
                            pen02.append(c1)
                        elif region_fills == 1:
                            pen01.append(c1)
                        else:
                            raise Exception(f"Something is wrong with the region_fills: {region_fills}")
        
        #we try to find a move with the lowest penalty, taking into account the points we would earn ourselves as well
        if len(pen01) > 0:
            return choice(pen01)
        if len(pen12) > 0:
            return choice(pen12)
        if len(pen02) > 0:
            return choice(pen02)
        if len(pen2) > 0:
            return choice(pen2)
        if len(pen13) > 0:
            return choice(pen13)
        if len(pen03) > 0:
            return choice(pen03)
        
    def find_legal_values(self, c: Cell):
        '''
        finds a legal value for empty cell c. NOTE: does not take taboo-ness into account beyond checking the
        given list of TabooMoves
        
        :param c: the empty cell for which a legal value must be found
        :return: list of legal values for the given cell
        '''
        N = self.N
        all_values = set(range(1,N+1))
        illegal = set()

        
        #check values in row
        row_idx = int(c.regions[0][1])
        for j in range(N):
            illegal.add(self.get(row_idx,j))
        
        #check values in column
        col_idx = int(c.regions[1][1])
        for i in range(N):
            illegal.add(self.get(i,col_idx))
            
        #check values in block
        topleft_row = int(c.regions[2][1])*self.n
        topleft_col = int(c.regions[2][-1])*self.m
        for i in range(topleft_row, topleft_row + self.n):
            for j in range(topleft_col, topleft_col + self.m):
                illegal.add(self.get(i,j))
        
        if len(all_values - illegal) == 1:
            return list(all_values - illegal)
        
        for v in list(all_values - illegal):
            if TabooMove(c.i, c.j, v) in self.taboo_moves:
                illegal.add(v)
        
        return list(all_values - illegal)
    
    def find_nontaboo_values(self, c: Cell):
        '''
        finds values for the given cell c that are most likely not taboo. If cell c already has a values attribute,
        then only values in that list will be taken into account.
        
        :param c: the cell for which values need to be returned
        :return: a list of values for cell c
        '''
        
    
    def find_taboo_values(self, c: Cell):
        '''
        finds values for the given cell c that ARE likely taboo. If cell c already has a values attribute,
        then only values in that list will be taken into account.
        
        :param c: the cell for which values need to be returned
        :return: a list of values for cell c
        '''
        
        
        

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        board_copy = AnaBoard(m = game_state.board.m, n = game_state.board.n, taboo_moves = game_state.taboo_moves)
        board_copy.squares = game_state.board.squares #no need to use .copy() as we're not going to change anything
        
        board_copy.find_empty_cells()
        best_cell = board_copy.get_best_move()
        legal_values = board_copy.find_legal_values(best_cell)
        best_cell.values = legal_values
        
        best_move = Move(best_cell.i, best_cell.j, choice(legal_values))
        
        self.propose_move(best_move)
