import unittest
import itertools
import math
from cscl_examples.sudoku import SudokuBoard, SudokuSolver
from cscl_tests.testutils.trivial_sat_solver import TrivialSATSolver


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

    def test_set_fails_for_invalid_indices(self):
        under_test = SudokuBoard.create_from_string(self.board_2x2)
        self.assertRaises(IndexError, under_test.set, 4, 0, 2)
        self.assertRaises(IndexError, under_test.set, 0, 4, 2)
        self.assertRaises(IndexError, under_test.set, -1, 0, 2)
        self.assertRaises(IndexError, under_test.set, 0, -1, 2)

    def test_get_fails_for_invalid_indices(self):
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


# TODO: test SudokuSolver and SudokuEncoder independently
class TestSudokuSolver(unittest.TestCase):
    @staticmethod
    def __is_completion_of(solution: SudokuBoard, problem_instance: SudokuBoard):
        idx_range = range(0, solution.get_size())
        for i, j in itertools.product(idx_range, idx_range):
            if problem_instance.get(i, j) is not None and problem_instance.get(i, j) != solution.get(i, j):
                print("Solution has illegal value at " + str((i, j)))
                return False
            if solution.get(i, j) is None:
                print("Solution has no value at " + str((i, j)))
                return False
        return True

    @staticmethod
    def __all_rows_have_distinct_elements(board: SudokuBoard):
        idx_range = range(0, board.get_size())
        for row in idx_range:
            col = [board.get(row, col) for col in idx_range]
            if len(col) != len(set(col)):
                print("Row " + str(row) + " does not have distinct elements")
                return False
        return True

    @staticmethod
    def __all_cols_have_distinct_elements(board: SudokuBoard):
        idx_range = range(0, board.get_size())
        for col in idx_range:
            row = [board.get(row, col) for row in idx_range]
            if len(row) != len(set(row)):
                print("Column " + str(col) + " does not have distinct elements: " + str(row))
                return False
        return True

    @staticmethod
    def __all_boxes_have_distinct_elements(board: SudokuBoard):
        box_size = int(math.sqrt(board.get_size()))

        def box_indices(boxrow, boxcol):
            return itertools.product(range(box_size * boxrow, (box_size+1) * boxrow),
                                     range(box_size * boxcol, (box_size+1) * boxcol))

        for box_row, box_col in itertools.product(range(0, box_size), range(0, box_size)):
            box = [board.get(i, j) for i, j in box_indices(box_row, box_col)]
            if len(box) != len((set(box))):
                print("Box " + str((box_row, box_col)) + " does not have distinct elements: " + str(box))
                return False
        return True

    @staticmethod
    def __is_valid_solution(solution: SudokuBoard, problem_instance: SudokuBoard):
        if solution.get_size() != problem_instance.get_size():
            print("Board sizes differ, solution: " + solution.get_size()
                  + " vs. problem instance " + problem_instance.get_size())
            return False

        valid = TestSudokuSolver.__is_completion_of(solution, problem_instance)\
            and TestSudokuSolver.__all_cols_have_distinct_elements(solution)\
            and TestSudokuSolver.__all_rows_have_distinct_elements(solution)

        return valid

    @staticmethod
    def __bad_solution_err_msg(solution: SudokuBoard, problem_instance: SudokuBoard):
        return "Bad solution:\n" + solution.to_string() + "\nfor problem instance:\n" + problem_instance.to_string()

    @staticmethod
    def __solve_and_check(problem_instance_txt: str):
        problem_instance = SudokuBoard.create_from_string(problem_instance_txt)
        sat_solver = TrivialSATSolver()
        under_test = SudokuSolver(problem_instance.get_size(), sat_solver)
        solution = under_test.solve(problem_instance)
        assert solution is not None
        assert TestSudokuSolver.__is_valid_solution(solution, problem_instance),\
            TestSudokuSolver.__bad_solution_err_msg(solution, problem_instance)

    # Unfortunately, the simple testing SAT solver is not powerful enough for solving 3x3
    # instances in a reasonable amount of time, and a full-fledged  IPASIR solver
    # would be too heavyweight to be a testing dependency, so testing is limited to 2x2 boards
    # for now (though the encoder supports arbitrarily large boards):

    def test_2x2_constrained(self):
        board_2x2_constrained = """x2|xx
                                   xx|2x
                                   --+--
                                   4x|1x
                                   xx|xx"""
        TestSudokuSolver.__solve_and_check(board_2x2_constrained)

    def test_2x2_unconstrained(self):
        board_2x2_empty = """xx|xx
                             xx|xx
                             --+--
                             xx|xx
                             xx|xx"""
        TestSudokuSolver.__solve_and_check(board_2x2_empty)

    @staticmethod
    def __check_unsolvability(problem_instance_txt: str):
        problem_instance = SudokuBoard.create_from_string(problem_instance_txt)
        sat_solver = TrivialSATSolver()
        under_test = SudokuSolver(problem_instance.get_size(), sat_solver)
        solution = under_test.solve(problem_instance)
        assert solution is None, "Board has a solution, but should not:\n" + problem_instance_txt

    def test_2x2_has_box_constraint(self):
        TestSudokuSolver.__check_unsolvability("""1x|xx
                                                  x1|xx
                                                  --+--
                                                  xx|xx
                                                  xx|xx""")

    def test_2x2_has_row_constraint(self):
        TestSudokuSolver.__check_unsolvability("""1x|x1
                                                  xx|xx
                                                  --+--
                                                  xx|xx
                                                  xx|xx""")

    def test_2x2_has_col_constraint(self):
        TestSudokuSolver.__check_unsolvability("""1x|xx
                                                  xx|xx
                                                  --+--
                                                  1x|xx
                                                  xx|xx""")

    def test_2x2_overconstrained(self):
        TestSudokuSolver.__check_unsolvability("""1x|xx
                                                  xx|4x
                                                  --+--
                                                  x3|x1
                                                  xx|2x""")
