import math

from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
from .Helper_Functions import find_legal_moves, score_move, find_actual_moves
import time
from typing import List

class MinimaxTree():
    def __init__(self, game_state: GameState, move: Move, score: float, player_nr: int,  maximize=True):
        self.game_state = game_state
        self.move = move
        self.score = score            # The score for the gamestate on this node
        self.player_nr = player_nr    # Remains the same for all tree nodes
        self.children = []            # contains a list of MinimaxTrees showing moves that can be played from here


        self.maximize = maximize
        self.active = True            # False if the tree is pruned. No new levels will be added to this

    def update_score(self):
        """
        Recursively updates child scores then takes them and either maximizes or minimizes score, flipping each layer of the tree.

        Uses self.maximize: whether to maximize (true) or minimize (false) the score on this node
               should be false for opponent move
        """

        if not self.children:
            # recursion base: do nothing (using the score that was decided when the node was made)
            return
        else:
            # recursively update the scores of the current's node's children using this function
            scores = []
            for child in self.children:
                child.update_score()
                scores.append(child.score)
                
            # update the current node's score by replacing it with the maximum or minimum of the children's scores
            if not self.maximize:
                self.score = min(scores)
            else:
                self.score = max(scores)

    def add_layer_here(self):
        """
        Adds a layer to the tree with moves that can be played now and their scores.
        Obsolete, replaced by smart_add_layer_here
        """
        # start = time.time()
        # find legal moves
        board_copy = SudokuBoard(self.game_state.board.m, self.game_state.board.n)
        board_copy.squares = self.game_state.board.squares.copy()
        legal_moves = find_actual_moves(board_copy, self.game_state)
        if len(legal_moves) == 0:
            self.active = False
        # Iterate ove the legal moves and add a child in the new layer for each
        for move in legal_moves:
            # score the move and find out what the new point balance would be after the move is made
            # the score is input for the new MinimaxTree, new_points is input for the new GameState.
            score, new_points, taboo = score_move(self.game_state, move, self.player_nr, not self.maximize)
            
            # create a copy of the SudokuBoard and apply the move to it, this is input for the new GameState

            new_board = SudokuBoard(self.game_state.board.m, self.game_state.board.n)
            new_board.squares = self.game_state.board.squares.copy()

            if not taboo: #if the move is not taboo, the board will change
                new_board.put(move.i, move.j, move.value)
            
            new_state = GameState(self.game_state.initial_board, new_board,
                                  self.game_state.taboo_moves.copy(), self.game_state.moves.copy(),
                                  new_points)

            # add the new MinimaxTree to the children of the current one
            self.children.append(MinimaxTree(new_state, move, score, self.player_nr, not self.maximize))

    def add_layer(self, indent = ""):
        """
        Goes to the bottom of the tree and adds a layer there.
        Uses A-B Pruning to decrease work
        Obsolete, replaced by smart_add_layer

        :param: indent: Used for debug printing to show the tree stucture.
        """
        # prune reporting
        i = 0
        j = 0
        start = time.time()
        # prevent doing unneeded work by ab pruning the tree before adding a layer
        self.prune()
        # recursively check if each node has children
        if len(self.children) > 0:
            for child in self.children:
                if child.active: # do not go down pruned branches
                    child.add_layer(indent + "  ")
                else: # prune reporting
                    i += 1
                j += 1
            # prints how much got pruned
            #print(f"{indent} {int((time.time()-start)*1000)} ms      {i} out of {j} Pruned")
        # when a childless node is reached (the bottom of the tree), add children to it
        else:
            self.add_layer_here()

    def get_best_move(self) -> Move:
        """
        Gets the best move that can be played now by updating the score of the entire tree,
        then suggesting the move made by the child with the best score.
        :return: Move
        """
        self.update_score()  # update the scores so children's scores are correct

        best_score = -math.inf
        best_move = None
        # iterate over the children (current possible moves to make) and return the move with the highest score
        for child in self.children:
            if child.score > best_score and child.active:
                best_score = child.score
                best_move = child.move
        return(best_move, best_score)

    def prune(self, a=-math.inf, b=math.inf, prune_min_dif=1):
        """
        Prunes branches that will not impact final analysis of score for this layer.
        This pruning also means these moves are not explored further.
        This requires stricter requirements, since some moves may seem bad but turn out good later.
        Thus prune_min_dif can be used to decide when to not explore moves anymore.

        """
        if len(self.children) == 0:
            return self.score
        elif self.maximize:
            maxEva = -9999
            for child in self.children:
                if a < b:
                    eva = child.prune(a, b)
                    maxEva = max(maxEva, eva)
                    a = max(a, eva)
                elif a + prune_min_dif < b: #if needs to be pruned
                    child.active = False
            return maxEva
        elif not self.maximize:
            minEva = 9999
            for child in self.children:
                if a  < b:
                    eva = child.prune( a, b)
                    minEva = min(minEva, eva)
                    b = min(b, eva)
                elif a + prune_min_dif < b: #if needs to be pruned
                    child.active = False
            return minEva
        else:
            raise Exception("How did you get here????")

    def smart_add_layer(self, board_states = {}, indent=""):
        """
        Goes to the bottom of the tree and adds a layer there.
        Uses A-B Pruning to decrease work,
        as well as preventing going down places where the same board state
        has already been seen with a better score.

        :param board_states: Dictionary that shows for board_state, player combinations
        what the best score we have seen for that combo is. Used to prevent going down the same path twice.
        """
        # prune reporting
        i = 0
        j = 0
        k = 0
        start = time.time()
        # prevent doing unneeded work by ab pruning the tree before adding a layer. Only do it once
        if board_states == {}:
            self.prune()
        # recursively check if each node has children
        if len(self.children) > 0:
            for child in self.children:
                if child.active:  # do not go down pruned branches
                    try:
                        board_score = board_states[(tuple(child.game_state.board.squares), child.maximize)]
                    except KeyError:
                        board_score = -999999
                    # do not go down branches where the same board position has already been encountered
                    # but with a better score for us
                    if board_score < child.score:
                        board_states[(tuple(child.game_state.board.squares), child.maximize)] = child.score
                        board_states = child.smart_add_layer(board_states, indent + "  ")
                    else:
                        child.active = False
                        #print(f"{indent} deactivating branch {j}")
                        k += 1
                else:  # prune reporting
                    i += 1
                j += 1
            if k + i >= j and j > 0:
                #if all children are invactive, deactivate this branch
                self.active = False
            # notes how many branches got pruned or had already been pruned,
            # and how many got deactivated for being a double board
            #print(f"{indent} {int((time.time() - start) * 1000)} ms      {i} out of {j} Pruned, {k} deactivated as double boards")
        # when a childless node is reached (the bottom of the tree), add children to it
        else:
            board_states = self.smart_add_layer_here(board_states)
        return board_states

    def smart_add_layer_here(self, board_states) -> dict:
        """
        Adds a layer to the tree with moves that can be played now and their scores.
        Returns the board_states, to allow setting certain boards to inactive
        """
        # start = time.time()
        # find legal moves
        board_copy = SudokuBoard(self.game_state.board.m, self.game_state.board.n)
        board_copy.squares = self.game_state.board.squares.copy()
        best_moves, mediocre_moves, bad_moves = find_legal_moves(self.game_state)

        #choose which lists of moves to consider, based on how many there are in each list
        if len(best_moves) > 1:
            moves = best_moves
        if len(best_moves) <= 1 and len(mediocre_moves) > 1:
            moves = best_moves+mediocre_moves
        else:
            moves = best_moves+mediocre_moves+bad_moves

        # Iterate over the legal moves we decided to consider and add a child in the new layer for each
        for move in moves:
            # score the move and find out what the new point balance would be after the move is made
            # the score is input for the new MinimaxTree, new_points is input for the new GameState.
            # taboo is used to decide if we should change the board for the new gamestate
            score, new_points, taboo = score_move(self.game_state, move, self.player_nr, not self.maximize)


            # create a copy of the SudokuBoard and apply the move to it, this is input for the new GameState
            new_board = SudokuBoard(self.game_state.board.m, self.game_state.board.n)
            new_board.squares = self.game_state.board.squares.copy()
            new_taboo = self.game_state.taboo_moves.copy()
            new_moves_played = self.game_state.moves.copy()
            if not taboo:  # if the move is not taboo, the board will change
                new_board.put(move.i, move.j, move.value)
                new_moves_played.append(move)
            else: # if the move is taboo, it is added to the moves and taboomoves
                new_taboo.append(TabooMove(move.i, move.j, move.value))
                new_moves_played.append(TabooMove(move.i, move.j, move.value))

            # only do the move if it does not result in a board_state that has already been seen with the same score or better
            try:
                board_score = board_states[(tuple(new_board.squares), not self.maximize)]
            except:
                board_score = -math.inf
            if score > board_score-10:
                new_state = GameState(self.game_state.initial_board, new_board,
                                      new_taboo, new_moves_played,
                                      new_points)
                #print(move, [str(i) for i in self.moves], [str(i) for i in new_moves])
                # add the new MinimaxTree to the children of the current one
                self.children.append(MinimaxTree(new_state, move, score, self.player_nr, not self.maximize))

                #update the saved board_score
                board_states[(tuple(new_board.squares), not self.maximize)] = score

        return board_states

    def print_move_scores(self):
        """
        Prints the move-score combo of each child move. Useful for debugging.
        :return:
        """
        max_score = -math.inf
        for child in self.children:
            print(f"{child.move} : {child.score}, {child.active}")
            if child.score > max_score:
                max_score = child.score
                best_move = child
        print(self.print_best_move_path())

    def print_best_move_path(self) -> List[Move]:
        """
        returns the path of moves that are the moves minimax thinks a rational agent & opponent will make
        (useful for debugging when the AI makes seemingly bad decisions)
        :return: List[move]
        """
        if not self.children:
            return [("end", self.score)]
        if self.maximize:
            best_score = -math.inf
            best_move = None
            best_child = None
            # iterate over the children (current possible moves to make) and return the move with the highest score
            for child in self.children:
                if child.score > best_score and child.active:
                    best_score = child.score
                    best_move = child.move
                    best_child = child

        else:
            best_score = math.inf
            best_move = None
            best_child = None
            # iterate over the children (current possible moves to make) and return the move with the lowest score
            for child in self.children:
                if child.score < best_score and child.active:
                    best_score = child.score
                    best_move = child.move
                    best_child = child
        if best_child != None:
            return [str(best_move)] + best_child.print_best_move_path()
        else:
            return ["error: reached inactive node"]

