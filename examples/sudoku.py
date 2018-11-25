import math
import itertools

from cscl.interfaces import *
from cscl.cardinality_constraint_encoders import *


class SudokuBoard:
    """Representation of a Sudoku board."""

    @staticmethod
    def __parse_valid_board(sanitized_lines):
        board_size = len(sanitized_lines[0])
        board = []
        for line in sanitized_lines:
            board_row = []
            for char in line:
                if char == 'x':
                    board_row.append(None)
                elif char.isdigit():
                    digit = int(char)
                    if digit == 0 or digit > board_size:
                        return None
                    board_row.append(digit)
                else:
                    return None  # illegal character
            board.append(board_row)
        return board

    @staticmethod
    def create_from_string(textual_representation: str):
        """
        Translates a textual Sudoku board representation to a SudokuBoard object.

        Let n be an arbitrary positive, nonzero integer. A textual
        representation of a Sudoku board is a string that, after removing whitespace,
        empty lines and the characters '+', '-', '|', ' ' consists
        of n lines, with each line containing n characters of ['1', '2', ..., '9', 'x'][:n].
        The 'x' character signifies an empty cell.

        Example board:

        +--+--+
        |1x|xx|
        |x2|xx|
        +--+--+
        |xx|x3|
        |3x|xx|
        +--+--+

        :param textual_representation: The board's textual representation.
        :return: If textual_representation is a valid Sudoku board, the SudokuBoard object matching
                 textual_representation is returned. Otherwise, None is returned.
        """

        sanitizer_table = dict.fromkeys(map(ord, '+-| '), None)
        sanitized_repr = textual_representation.translate(sanitizer_table)

        lines = [x.strip() for x in sanitized_repr.splitlines() if x.strip() != ""]
        if len(lines) == 0:
            return None

        board_size = len(lines[0])

        if len(lines) != board_size or any(len(line) != board_size for line in lines):
            return None
        board = SudokuBoard.__parse_valid_board(lines)
        return SudokuBoard(board) if board is not None else None

    def __init__(self, board):
        self.board = board

    def __check_coordinate_validity(self, row: int, col: int):
        if not (isinstance(row, int) and isinstance(row, int)):
            raise IndexError()
        if row not in range(0, self.get_size()) or col not in range(0, self.get_size()):
            raise IndexError()

    def get(self, row: int, col: int):
        """
        Returns the symbol at cell (row, col), with row being the index of the cell's row index
        and col being the index of the cell's column index. Indices are counted from 0.

        :param row: An integer in range(0, get_size())
        :param col: An integer in range(0, get_size())
        :return: The setting of the cell with index (row, col). If the cell has a setting, the setting's
                 integer representation is returned. If the cell has no setting, None is returned.
        """
        self.__check_coordinate_validity(row, col)
        return self.board[row][col]

    def set(self, row: int, col: int, value):
        """
        Sets the value of the cell at coordinates (row, col).

        :param row: An integer in range(0, get_size())
        :param col: An integer in range(0, get_size())
        :param value: The new value. value must be None or contained in range(1, get_size()+1).
        :return: None
        """
        self.__check_coordinate_validity(row, col)
        if value is not None:
            if not isinstance(value, int) or (value < 1 or value > self.get_size()):
                raise ValueError("Value out of range")

        self.board[row][col] = value

    def get_size(self):
        """
        Returns the width of the board.

        :return: The width of the board.
        """
        return len(self.board)

    def clone(self):
        """
        Clones the board.

        :return: A clone of this object.
        """
        cloned_board = []
        for row in self.board:
            cloned_board.append(row[:])
        return SudokuBoard(cloned_board)


    @staticmethod
    def __create_separator_string(box_size: int) -> str:
        result = ""
        for i in range(0, box_size):
            if i != 0:
                result += "+"
            for j in range(0, box_size):
                result += "-"
        return result

    @staticmethod
    def __row_to_string(row, box_size):
        result = ""
        col_counter = 0
        for col in row:
            if col_counter % box_size == 0 and col_counter != 0:
                result += "|"
            result += str(col) if col is not None else 'x'
            col_counter += 1
        return result

    def to_string(self):
        """
        Returns a string representation of the board.

        :return: A string representation of the board.
        """
        result = ""
        box_size = int(math.sqrt(self.get_size()))
        row_counter = 0
        for row in self.board:
            if row_counter % box_size == 0 and row_counter != 0:
                result += self.__create_separator_string(box_size) + "\n"

            result += self.__row_to_string(row, box_size)

            if row_counter != self.get_size() - 1:
                result += "\n"
            row_counter += 1
        return result


def solution_to_board(solver: SatSolver, problem_instance, variable_board) -> SudokuBoard:
    # variable_board[i][j][sym]: SAT variable for cell(i,j) has symbol sym
    result = problem_instance.clone()
    n_symbols = len(variable_board)
    for i, j, sym in itertools.product(range(0, n_symbols), range(0, n_symbols), range(0, n_symbols)):
        sat_result = solver.get_assignment(variable_board[i][j][sym])
        if sat_result is None:
            result.set(i, j, 'x')
        elif sat_result:
            result.set(i, j, sym+1)
    return result


def encode_sudoku(clause_consumer: ClauseConsumer,
                  variable_factory: CNFVariableFactory,
                  board: SudokuBoard):
    n_symbols = board.get_size()
    at = []
    for i in range(0, n_symbols):
        row = []
        for j in range(0, n_symbols):
            col = []
            for k in range(0, n_symbols):
                col.append(variable_factory.create_variable())
            row.append(col)
        at.append(row)
    # Now: at[row][col][sym] :<-> cell (row,col) has symbol sym

    def __encode_at_most_1_constraint(constrained_lits):
        for clause in encode_at_most_k_constraint_binomial(variable_factory, 1, constrained_lits):
            clause_consumer.consume_clause(clause)

    # Constraint: Each field may have at most one symbol
    for i in range(0, n_symbols):
        for j in range(0, n_symbols):
            __encode_at_most_1_constraint(at[i][j])

    # Constraint: In each row, each symbol must appear exactly once
    for row in range(0, n_symbols):
        for sym in range(0, n_symbols):
            symbols_in_row = []
            for col in range(0, n_symbols):
                symbols_in_row.append(at[row][col][sym])

            # At-most-1:
            __encode_at_most_1_constraint(symbols_in_row)
            # At-least-1:
            clause_consumer.consume_clause(symbols_in_row)

    # Constraint: In each column, each symbol must appear exactly once
    for col in range(0, n_symbols):
        for sym in range(0, n_symbols):
            symbols_in_col = []
            for row in range(0, n_symbols):
                symbols_in_col.append(at[row][col][sym])

            # At-most-1:
            __encode_at_most_1_constraint(symbols_in_col)
            # At-least-1:
            clause_consumer.consume_clause(symbols_in_col)

    # In each box, each symbol must appear exactly once
    n_boxes = int(math.sqrt(n_symbols))

    def __box_min(box):
        return box * n_boxes

    def __box_max(box):
        return (box+1) * n_boxes

    for box_i, box_j, sym in itertools.product(range(0, n_boxes), range(0, n_boxes), range(0, n_symbols)):
        places = []
        box_i_coord_range = range(__box_min(box_i), __box_max(box_i))
        box_j_coord_range = range(__box_min(box_j), __box_max(box_j))

        for i, j in itertools.product(box_i_coord_range, box_j_coord_range):
            places.append(at[i][j][sym])

        # At-most-1:
        __encode_at_most_1_constraint(places)
        # At-least-1:
        clause_consumer.consume_clause(places)

    # Fixed settings:
    for i, j in itertools.product(range(0, n_symbols), range(0, n_symbols)):
        sym = board.get(i, j)
        if sym is not None:
            clause_consumer.consume_clause([at[i][j][sym-1]])

    return at