from competitive_sudoku.sudoku import SudokuBoard, print_board, Move
from team5_A1.sudokuai import score_move

test_board = SudokuBoard()
test_board.put(0,0,9)
test_board.put(0,7,6)
test_board.put(1,0,4)
test_board.put(1,1,1)
test_board.put(1,2,2)
test_board.put(1,5,7)
test_board.put(2,1,5)
test_board.put(2,3,1)
test_board.put(2,5,4)
test_board.put(3,2,5)
test_board.put(3,4,7)
test_board.put(3,5,9)
test_board.put(3,7,4)
test_board.put(4,2,6)
test_board.put(4,3,4)
test_board.put(4,5,3)
test_board.put(4,6,5)
test_board.put(5,1,9)
test_board.put(5,3,5)
test_board.put(5,4,8)
test_board.put(5,6,6)
test_board.put(6,3,3)
test_board.put(6,5,8)
test_board.put(6,7,5)
test_board.put(7,3,7)
test_board.put(7,6,9)
test_board.put(7,7,3)
test_board.put(7,8,8)
test_board.put(8,1,4)
test_board.put(8,8,1)

#moves made in order based on the scores
test_board.put(3,3,6)
test_board.put(1,4,6)
test_board.put(0,6,1)
test_board.put(0,8,4)
test_board.put(6,8,6)
test_board.put(1,8,5)
test_board.put(2,0,6)
test_board.put(1,6,3)

print(print_board(test_board))

possible_moves = [(3,0,1),(1,8,5),(7,1,6),(0,2,4),(1,7,8)]

for m in possible_moves:
    print(score_move(test_board,Move(*m),True))
    


