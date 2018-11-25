import unittest
import itertools
from examples.sudoku import *


class TestSudokuBoard(unittest.TestCase):
    def test_create_from_empty_string_yields_no_board(self):
        under_test = SudokuBoard.create_from_string("")
        assert under_test is None

    def test_create_from_string_with_illegal_symbols_yields_no_board(self):
        under_test = SudokuBoard.create_from_string("""
                                                +--+--+
                                                |1x|xx|
                                                |x2|?x|
                                                +--+--+
                                                |xx|x3|
                                                |3x|xx|
                                                +--+--+
                                                """)
        assert under_test is None

    def test_create_from_string_with_line_missing_yields_no_board(self):
        under_test = SudokuBoard.create_from_string("""
                                                +--+--+
                                                |1x|xx|
                                                |x2|xx|
                                                +--+--+
                                                |xx|x3|
                                                +--+--+
                                                """)
        assert under_test is None

    def test_create_from_string_with_column_missing_yields_no_board(self):
        under_test = SudokuBoard.create_from_string("""
                                                +--+-+
                                                |1x|x|
                                                |x2|x|
                                                +--+-+
                                                |xx|3|
                                                |3x|x|
                                                +--+-+
                                                """)
        assert under_test is None

    def test_create_from_string_with_cell_0_yields_no_board(self):
        under_test = SudokuBoard.create_from_string("""
                                                +--+--+
                                                |1x|0x|
                                                |x2|xx|
                                                +--+--+
                                                |xx|x3|
                                                |3x|xx|
                                                +--+--+
                                                """)
        assert under_test is None

    def test_create_from_string_with_too_large_number_yields_no_board(self):
        under_test = SudokuBoard.create_from_string("""
                                                +--+--+
                                                |1x|1x|
                                                |x5|xx|
                                                +--+--+
                                                |xx|x3|
                                                |3x|xx|
                                                +--+--+
                                                """)
        assert under_test is None

    def test_create_from_string_with_missing_box_yields_no_board(self):
        under_test = SudokuBoard.create_from_string("""
                                                +--+--+
                                                |1x|1x|
                                                |x5|xx|
                                                +--+--+
                                                |xx|
                                                |3x|
                                                +--+
                                                """)
        assert under_test is None

    board_2x2 = """1x|2x
x4|xx
--+--
xx|x3
3x|1x"""

    def test_create_2x2_board_from_string(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        assert under_test is not None
        expected = [[1,    None, 2,    None],
                    [None, 4,    None, None],
                    [None, None, None, 3],
                    [3,    None, 1,    None]]
        for row, col in itertools.product(range(0, 4), range(0, 4)):
            assert under_test.get(row, col) == expected[row][col], "Error at coordinates " + str((row, col))

    board_3x3 = """x1x|xx7|xxx
5xx|xxx|xxx
xx8|xxx|13x
---+---+---
xxx|xxx|xxx
xxx|xxx|xxx
xxx|xxx|xxx
---+---+---
xxx|xxx|xxx
xxx|xxx|xxx
xxx|xxx|2x3"""

    def test_create_3x3_board_from_string(self):
        under_test = SudokuBoard.create_from_string(self.board_3x3)
        assert under_test is not None
        expected = {(0, 1): 1,
                    (0, 5): 7,
                    (1, 0): 5,
                    (2, 2): 8,
                    (2, 6): 1,
                    (2, 7): 3,
                    (8, 6): 2,
                    (8, 8): 3}
        for row, col in itertools.product(range(0, 9), range(0, 9)):
            assert under_test.get(row, col) == expected.get((row, col)), "Error at coordinates " + str((row, col))

    def test_get_size_2x2(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        result = under_test.get_size()
        assert result == 4, "Invalid size " + str(result)
        
    def test_set_valid_digit(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        under_test.set(0, 0, 3)
        assert under_test.get(0, 0) == 3

    def test_set_none(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        under_test.set(0, 0, None)
        assert under_test.get(0, 0) is None

    def test_set_invalid_digit(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        self.assertRaises(ValueError, under_test.set, 0, 0, 0)
        self.assertRaises(ValueError, under_test.set, 0, 0, 5)

    def test_set_fails_for_invalid_coords(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        self.assertRaises(IndexError, under_test.set, 4, 0, 2)
        self.assertRaises(IndexError, under_test.set, 0, 4, 2)
        self.assertRaises(IndexError, under_test.set, -1, 0, 2)
        self.assertRaises(IndexError, under_test.set, 0, -1, 2)

    def test_get_fails_for_invalid_coords(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        self.assertRaises(IndexError, under_test.get, 4, 0)
        self.assertRaises(IndexError, under_test.get, 0, 4)
        self.assertRaises(IndexError, under_test.get, -1, 0)
        self.assertRaises(IndexError, under_test.get, 0, -1)

    def test_clone(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        clone = under_test.clone()
        assert under_test.get_size() == clone.get_size()
        for i, j in itertools.product(range(0, 4), range(0, 4)):
            assert under_test.get(i, j) == clone.get(i, j), "Error at coordinates " + str((i, j))

    def test_to_string_3x3(self):
        under_test = SudokuBoard.create_from_string(self.board_3x3)
        result = under_test.to_string()
        assert result == self.board_3x3, "Invalid string representation:\n" + result + "\nExpected:\n" + self.board_3x3

    def test_to_string_2x2(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        result = under_test.to_string()
        assert result == self.board_2x2, "Invalid string representation:\n" + result + "\nExpected:\n" + self.board_2x2
