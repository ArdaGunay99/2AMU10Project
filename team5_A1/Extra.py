import itertools
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

def get_block_topleft(i: int, j: int, width: int, height: int) -> tuple:
    '''
    gets the position of the topleft cell of the block which contains the given move.

    :param i: type int. Row index of the given move.
    :param j: type int. Column index of the given move.
    :param width: type int. The width of the blocks for the map on which the move is played.
    :param height: type int. The height of the blocks for the map on which the move is played.

    :return: type tuple. The position of the topleft cell (row_index, column_index).
    '''
    #get the distance from the left boarder by dividing the row index by the block width and taking the remainder
    dist_from_left_border = i % width
    topleft_row = i - dist_from_left_border

    #get he distance from the top border by dividing the column index by the block height and taking the remainder
    dist_from_top_border = j % height
    topleft_col = j - dist_from_top_border

    return topleft_row, topleft_col


def get_block(i: int, j: int, board: SudokuBoard) -> set:
    '''
    gets the values of non-empty cells in a block
    
    :param i: type int. Row index.
    :param j: type int. Column index.
    :param board: type SudokuBoard. The current board.
    
    :return: type set. All values in given block that are not 0.
    '''
    block = set([])
    start_row, start_col = get_block_topleft(i,j,board.m,board.n)

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


def retrieve_empty_cells(i: int, j: int, region: str, board: SudokuBoard) -> set:
    '''
    Retrieves all positions of empty cells in the given region of the given cell

    :param i: type int. row index of the given cell.
    :param j: type int. column index of the given cell.
    :param region: type string. 'row','col', or 'block'. Specifies the region of the given cell that should be checked for empty
    cells.
    :param board: type SudokuBoard. the board which contains the given cell.

    :return: type list. A list of tuples (i,j) containing the row index i and column index j of all empty cells in the given region.
    '''
    empty_pos = set([])

    if region=='row':
        for x in itertools.filterfalse(lambda y: board.get(i,y)!=board.empty, range(board.N)):
            empty_pos.add((i,x))

        return empty_pos

    if region=='column':
        for x in itertools.filterfalse(lambda y: board.get(y,j)!=board.empty, range(board.N)):
            empty_pos.add((x,j))

        return empty_pos

    if region=='block':
        left_border, top_border = get_block_topleft(i,j,board.m,board.n)
        block_indices = itertools.product(range(left_border,left_border+board.m),range(top_border,top_border+board.n))
        for pos in itertools.filterfalse(lambda y: board.get(y[0],y[1])!=board.empty, block_indices):
            empty_pos.add((pos[0],pos[1]))

        return empty_pos

    else:
        raise ValueError("region attribute should be 'block', 'column', or 'row'. {} given".format(region))



def calc_taboo_prob(move: Move, board: SudokuBoard, empty_row: set, empty_col: set, empty_block: set) -> float:
    '''
    Calculates a probability that the move will be labeled a taboo move if played.

    :param move: type Move. The move to be tested, assumed to be legal.
    :param board: type SudokuBoard. The board on which the move will be played (so before it is actually played!).
    :param empty_row: positions of empty cells in the row, excluding the cell we're performing the move on

    :return: type float. A probability (in the range [0,1]) of the move being taboo.
    '''
    #For each region, retrieve the empty cells (these are, for each region, potential cells the value of the move could end up in)

    potential_cells_row = len(empty_row) + 1 #keep track of the number of potential cells
    potential_cells_col = len(empty_col) + 1
    potential_cells_block = len(empty_block) + 1


    #eliminate the cells that can't have the value, by checking for each empty cell if its other regions already include the value
    #do this per region, starting with row
    for pos in empty_row:
        #retrieve sets
        col_values = get_column(pos[1], board)
        block_values = get_block(pos[0], pos[1], board)

        if move.value in col_values.union(block_values):  #check if the value was already present in the column or block of this cell
            potential_cells_row -= 1                      #eliminate the cell from potential cells if so

        #if the cell was not eliminated, check if this cell is guaranteed to have the current move's value, in which case our move
        #is guaranteed to be taboo, and a taboo probability of 1.0 should be returned.
        elif len(col_values) == board.N-1 or len(block_values) == board.N-1: #if only one empty cell was left in either region
            return 1.0

    if potential_cells_row == 1: #if there is only one potential cell left it is the cell for the current move
        return 0.0               #and the probability of the move being taboo is 0 (move is guaranteed correct)

    #repeat for column and block
    for pos in empty_col:
        row_values = get_row(pos[0],board)
        block_values = get_block(pos[0],pos[1],board)

        if move.value in row_values.union(block_values):
            potential_cells_col -= 1

        elif len(row_values) == board.N-1 or len(block_values) == board.N-1:
            return 1.0

    if potential_cells_col == 1:
        return 0.0

    for pos in empty_block:
        row_values = get_row(pos[0],board)
        col_values = get_column(pos[1],board)

        if move.value in row_values.union(col_values):
            potential_cells_block -= 1

        elif len(row_values) == board.N-1 or len(col_values) == board.N-1:
            return 1.0

    if potential_cells_block == 1:
        return 0.0

    #calculate for each region that the cell of the current move will end up with the value of the current move
    #by taking 1 divided by the total number of potential cells for that region
    prob_row = 1/potential_cells_row
    prob_col = 1/potential_cells_col
    prob_block = 1/potential_cells_block

    #return the probability that the cell of the current move will NOT end up with the value of the current move
    return 1 - max(prob_row, prob_col, prob_block)


def score_move(game_state: GameState, move: Move, player_nr: int, opponent: bool=False) -> tuple:
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
    :return type bool. The expected tabooness of the move.
    '''
    #first calculate the current difference in scores (our score - opponent's score)
    if player_nr == 1:
        current_score_difference = game_state.scores[0] - game_state.scores[1]
    else: # player_nr == 2:
        current_score_difference = game_state.scores[1] - game_state.scores[0]

    board_state = game_state.board
    #create a copy of the board and apply the move to it
    new_board = SudokuBoard(board_state.m, board_state.n)
    new_board.squares = board_state.squares.copy()
    new_board.put(move.i, move.j, move.value)
    
    #count the empty cells present in the column, row, and block of the new move
    col_empty_pos = retrieve_empty_cells(move.i, move.j, region='column', board=new_board)
    row_empty_pos = retrieve_empty_cells(move.i, move.j, region='row', board=new_board)
    block_empty_pos = retrieve_empty_cells(move.i, move.j, region='block', board=new_board)
    
    col_empty_count = len(col_empty_pos)
    row_empty_count = len(row_empty_pos)
    block_empty_count = len(block_empty_pos)
    
    #calculate the probability that the move we're trying to play will be taboo
    taboo_prob = calc_taboo_prob(move, game_state.board, row_empty_pos, col_empty_pos, block_empty_pos)
    
    #if the move will (almost) certainly be taboo, it will result in no move played at all and there's no point evaluating it further
    if taboo_prob > 0.8:
        return current_score_difference, game_state.scores, True #True to indicate the move is likely taboo

    regions = 0 #variable to keep track of conquered regions
    
    #compute heuristic values for column, row and block by applying formula 1 from the A1 report to each region
    #start with column
    if col_empty_count%2 == 0: #if there's an even number of empty cells
        col_heur = 1 / (col_empty_count + 1)
        if col_empty_count == 0: #if no empty cells remain in a region, that region is conquered.
            regions += 1
    else: #if there's an uneven number of empty cells
        col_heur = - (1 / col_empty_count)
    
    #repeat for row and block
    if row_empty_count%2 == 0:
        row_heur = 1 / (row_empty_count + 1)
        if row_empty_count == 0:
            regions += 1
    else:
        row_heur = - (1 / row_empty_count)
        
    if block_empty_count%2 == 0:
        block_heur = 1 / (block_empty_count + 1)
        if block_empty_count == 0:
            regions += 1
    else:
        block_heur = - (1 / block_empty_count)

    position_heur_score = (col_heur+row_heur+block_heur) / 3

    # calculate the points earned by making the move, based on the regions conquered.
    if regions == 0 or regions == 1:
        points = regions
    elif regions == 2:
        points = 3
    elif regions == 3:
        points = 7
    
    # update the score balance based on the points earned
    if (player_nr == 1 and opponent) or (player_nr == 2 and not opponent):
        new_points = [game_state.scores[0], game_state.scores[1] + points]
    elif (player_nr == 1 and not opponent) or (player_nr == 2 and opponent):
        new_points = [game_state.scores[0] + points, game_state.scores[1]]
        
    # the first half of formula 2 of the report
    final_score = 2*position_heur_score + points
    
    # the second half of formula 2 of the report
    if opponent:
        # return the negative of the final score if the opponent is the one executing it
        return -final_score + current_score_difference, new_points, False
                
    return final_score + current_score_difference, new_points, False #return False to indicate the move is likely not taboo

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