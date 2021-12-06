import math
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove


def possible(i: int, j: int, value: int, game_state: GameState) -> bool:
    '''
    checks if a move is in the list of taboo moves.
    
    :param i: type int. Row index of the move.
    :param j: type int. Column index of the move.
    :param value: type int. Value of the move.
    :param game_state: type GameState. The current game state.
    
    :return: type bool. True if the move is NOT a taboo move, False if it is.
    '''
    return not TabooMove(i, j, value) in game_state.taboo_moves


def get_row(i: int, board: SudokuBoard) -> set:
    '''
    gets the values of non-empty cells in a row.
    
    :param i: type int. Row index.
    :param board: type SudokuBoard. The current board.
    
    :return: type set. All values in given row that are not 0.
    '''
    N = board.N
    row = set([])
    for j in range(N):
        if board.get(i, j) != SudokuBoard.empty:
            row.add(board.get(i, j))
    return row


def get_column(j: int, board: SudokuBoard) -> set:
    '''
    gets the values of non-empty cells in a column
    
    :param j: type int. Column index.
    :param board: type SudokuBoard. The current board.
    
    :return: type set. All values in given column that are not 0.
    '''
    N = board.N
    column = set([])
    for i in range(N):
        if board.get(i, j) != SudokuBoard.empty:
            column.add(board.get(i, j))
    return column


# 
def get_block(i: int, j: int, board: SudokuBoard) -> set:
    '''
    gets the values of non-empty cells in a block
    
    :param i: type int. Row index.
    :param j: type int. Column index.
    :param board: type SudokuBoard. The current board.
    
    :return: type set. All values in given block that are not 0.
    '''
    block = set([])
    # row index of the top left cell of the block
    start_row = math.floor(i / board.m) * board.m
    # column index of the top left cell of the block
    start_col = math.floor(j / board.n) * board.n

    for row in range(start_row, start_row + board.m):
        for col in range(start_col, start_col + board.n):
            if board.get(row, col) != board.empty:
                block.add(board.get(row, col))
    return block


def find_legal_moves(game_state: GameState) -> list:
    ''' 
    finds all possible legal moves in a given game state
    
    :param game_state: type GameState. the current GameState.
    
    :return: type list. A list of all legal moves possible in the current GameState
    '''
    board = game_state.board
    N = board.N
    legal_moves = []
    
    # loop over all positions on the board
    for i in range(N):
        row = get_row(i, board)
        for j in range(N):
            if board.get(i, j) == board.empty:
                column = get_column(j, board)
                block = get_block(i, j, board)
                for value in range(1, N + 1):
                    # on each position and for each value, check that the move is not a taboo move
                    if possible(i, j, value, game_state):
                        # and check that the current value is not already present in one of the current board positions regions
                        if value in block or value in column or value in row:
                            continue
                        else:
                            legal_moves.append(Move(i, j, value))

    return legal_moves


def score_move(game_state: GameState, move: Move, player_nr: int, opponent: bool=False):
    '''
    Calculates a score to indicate how likely a move performed in a given GameState may lead to victory, as well as
    the new score balance if the move were to be executed.
    
    :param game_state: type GameState. The gamestate Before the move is executed.
    :param move: type Move. The move that is being scored, assumed to be legal.
    :param player_nr: type int. 1 if our agent is player 1, 2 if our agent is player 2.
    :param opponent: type bool. if True, the move is assumed to be executed by our opponent. If False, the move is assumed to
    be executed by our agent.
    
    :return: type float. The score given to the move when performed in the current GameState.
    :return: type list. The new score balance ([score-player1, score-player2]) if the move were to be executed in the current GameState
    '''
    #first calculate the current difference in scores (our score - opponent's score)
    if player_nr == 1:
        current_score_difference = game_state.scores[0] - game_state.scores[1]
    elif player_nr == 2:
        current_score_difference = game_state.scores[1] - game_state.scores[0]
     
        
    board_state = game_state.board
    #create a copy of the board and apply the move to it
    new_board = SudokuBoard(board_state.m, board_state.n)
    new_board.squares = board_state.squares.copy()
    new_board.put(move.i, move.j, move.value)
    
    #count the empty cells present in the column, row, and block of the new move
    
    #first the column, just loop over all values with the correct column index and count empty values:
    col_empty = 0
    move_col = move.j
    
    for i in range(new_board.N):
        if new_board.get(i,move_col) == new_board.empty:
            col_empty += 1
    
    #row, same strategy as for column:
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
    
    #then use the borders to loop over each tile in the block and count the empty cells.
    for i in range(left_border, right_border):
        for j in range(top_border, bottom_border):
            if new_board.get(i,j) == new_board.empty:
                block_empty += 1
    
    regions = 0 #variable to keep track of any points that may be scored by performing the move
    
    #compute column, row and block scores by applying formula 1 from the report to each region
    #start with column
    if col_empty%2 == 0: #if there's an even number of empty cells
        col_score = 1 / (col_empty + 1)
        if col_empty == 0: #if no empty cells remain in any region, that region is conquered.
            regions += 1
    else: #if there's an uneven number of empty cells
        col_score = - (1 / col_empty)
    
    #repeat for row and block
    if row_empty%2 == 0:
        row_score = 1 / (row_empty + 1)
        if row_empty == 0:
            regions += 1
    else:
        row_score = - (1 / row_empty)
        
    if block_empty%2 == 0:
        block_score = 1 / (block_empty + 1)
        if block_empty == 0:
            regions += 1
    else:
        block_score = - (1 / block_empty)
        
    # calculate the points earned by making the move, based on the regions conquered.
    if regions == 0 or regions == 1:
        points = regions
    elif regions == 2:
        points = 3
    elif regions == 3:
        points = 7
    
    # create a new score balance based on the points earned
    if (player_nr == 1 and opponent) or (player_nr == 2 and not opponent):
        new_points = [game_state.scores[0], game_state.scores[1] + points]
    elif (player_nr == 1 and not opponent) or (player_nr == 2 and opponent):
        new_points = [game_state.scores[0] + points, game_state.scores[1]]
        
    # the first half of formula 2 of the report
    final_score = ((col_score + row_score + block_score) / 3) + 2*points
    
    # the second half of formula 2 of the report
    if opponent:
        # return the negative of the final score if the opponent is the one executing it
        return -final_score + current_score_difference, new_points
                
    return final_score + current_score_difference, new_points

def moves_left(board : SudokuBoard):
    """
    :param board: A Sudoku board
    :return: The number of empty squares that are still left on the sudoku board
    """

    counter = 0
    for i in range(board.N):
        for j in range(board.N):
            if board.get(i,j) == board.empty:
                counter += 1
    return counter