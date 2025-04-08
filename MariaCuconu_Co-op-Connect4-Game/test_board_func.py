from domain.board import Board
from service.board_func import Board_Service,str_board,drop_piece
import unittest

class Board_func_Tests(unittest.TestCase):
    def setUp(self):
        self._board=Board(6,7)
        self._service=Board_Service(self._board)

    def test_ROW_COUNT_getter(self):
        self.assertEqual(self._service.ROW_COUNT,6)

    def test_COLUMN_COUNT_getter(self):
        self.assertEqual(self._service.ROW_COUNT,6)

    def test_board_getter(self):
        self.assertEqual(self._service.board,self._board.board)

    def test_is_valid_location(self):
        self.assertEqual(self._service.is_valid_location(self._board.board,-1),False)
        self.assertEqual(self._service.is_valid_location(self._board.board, None), False)
        self.assertEqual(self._service.is_valid_location(self._board.board, 0), True)
        self._board.board[5][0]=1
        self.assertEqual(self._service.is_valid_location(self._board.board, 0), False)

    def test_get_next_open_row(self):
        self.assertEqual(self._service.get_next_open_row(self._board.board,0),0)
        self._board.board[0][0] = 1
        self.assertEqual(self._service.get_next_open_row(self._board.board, 0), 1)
        self._board.board[1][0] = 1
        self._board.board[2][0] = 1
        self._board.board[3][0] = 1
        self._board.board[4][0] = 1
        self._board.board[5][0] = 1
        self.assertEqual(self._service.get_next_open_row(self._board.board, 0), None)

    def test_print_board(self):
        self.assertEqual(self._service.print_board(),'0 1 2 3 4 5 6\n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n')

    def test_evaluate_window(self):
        window=[2,2,2,2]
        self.assertEqual(self._service.evaluate_window(window,2),100)
        window = [2, 2, 2, 0]
        self.assertEqual(self._service.evaluate_window(window, 2), 10)
        window = [2, 2, 0, 0]
        self.assertEqual(self._service.evaluate_window(window, 2), 2)
        window = [1, 1, 1, 0]
        self.assertEqual(self._service.evaluate_window(window, 2), -50)
        window=[2,2,2,0]
        self.assertEqual(self._service.evaluate_window(window,1),-50)

    def test_str_board(self):
        self.assertEqual(str_board(self._board.board),
                         '0 1 2 3 4 5 6\n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n')

    def test_drop_piece(self):
        self.assertEqual(self._board.board[0][0],0)
        drop_piece(self._board.board,0,0,1)
        self.assertEqual(self._board.board[0][0], 1)

