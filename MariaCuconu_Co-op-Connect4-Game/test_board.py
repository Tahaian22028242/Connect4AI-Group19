import unittest

from domain.board import Board

class Board_Tests(unittest.TestCase):
    def setUp(self):
        self._board=Board(6,7)

    def test_ROW_COUNT_getter(self):
        self.assertEqual(self._board.ROW_COUNT,6)

    def test_COLUMN_COUNT_getter(self):
        self.assertEqual(self._board.COLUMN_COUNT,7)

    def test_board_getter(self):
        self.assertEqual(self._board.board,[[0 for i in range(7)] for i in range(6)])

    def test__str__(self):
        self.assertEqual(str(self._board),'0 1 2 3 4 5 6\n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 \n')

