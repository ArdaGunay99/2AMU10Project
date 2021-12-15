from competitive_sudoku.sudoku import GameState, Move, SudokuBoard
from .Helper_Functions import find_legal_moves, score_move


class MinimaxTree():
    def __init__(self, game_state: GameState, move: Move, score: float, player_nr: int, maximize=True):
        self.game_state = game_state
        self.move = move
        self.score = score            # The score for the gamestate on this node
        self.player_nr = player_nr    # Remains the same for all tree nodes
        self.children = []            # contains a list of MinimaxTrees showing moves that can be played from here

        self.maximize = maximize

    def update_score(self):
        """
        Recursively updates child scores then takes them and either maximizes or minimizes score, flipping each layer of the tree.

        Uses self.maximize: whether to maximize (true) or minimize (false) the score on this node
               should be false for opponent move
        """

        if self.children == []:
            # recursion base: do nothing (using the score that was decided when the node was made)
            return
        else:
            # recursively update the scores of the current's node's children using this function
            scores = []
            for child in self.children:
                child.update_score()
                scores.append(child.score)
                
            # update the current node's score by replacing it with the maximum or minimum of the children's scores
            if self.maximize == False:
                self.score = min(scores)
            else:
                self.score = max(scores)

    def add_layer_here(self):
        """
        Adds a layer to the tree with moves that can be played now and their scores.
        """
        # find legal moves
        legal_moves = find_legal_moves(self.game_state)
        
        # Iterate ove the legal moves and add a child in the new layer for each
        for move in legal_moves:
            # score the move and find out what the new point balance would be after the move is made
            # the score is input for the new MinimaxTree, new_points is input for the new GameState.
            score, new_points = score_move(self.game_state, move, self.player_nr, not self.maximize)
            
            # create a copy of the SudokuBoard and apply the move to it, this is input for the new GameState
            new_board = SudokuBoard(self.game_state.board.m, self.game_state.board.n)
            new_board.squares = self.game_state.board.squares.copy()
            new_board.put(move.i, move.j, move.value)
            
            new_state = GameState(self.game_state.initial_board, new_board,
                                  self.game_state.taboo_moves.copy(), self.game_state.moves.copy(),
                                  new_points)

            # add the new MinimaxTree to the children of the current one
            self.children.append(MinimaxTree(new_state, move, score, self.player_nr, not self.maximize))

    def add_layer(self):
        """
        Goes to the bottom of the tree and adds a layer there
        """
        # recursively check if each node has children
        if len(self.children) > 0:
            for child in self.children:
                child.add_layer()
        # when a childless node is reached (the bottom of the tree), add children to it
        else:
            self.add_layer_here()

    def get_best_move(self) -> Move:
        """
        Gets the best move by updating the score of the entire tree,
        then suggesting the move made by the child with the best score.
        :return: Move
        """
        self.update_score()  # update the scores so children's scores are correct

        best_score = -99999999
        best_move = None
        # iterate over the children (current possible moves to make) and return the move with the highest score
        for child in self.children:
            if child.score > best_score:
                best_score = child.score
                best_move = child.move
        return(best_move)