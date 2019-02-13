import math
import itertools

from cscl.interfaces import SatSolver, ClauseConsumer, CNFLiteralFactory
from cscl.cardinality_constraint_encoders import encode_at_most_k_constraint_binomial


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


def positive_int_square(i: int):
    """
    Computes the square root of a square number i, in log(i) time.

    :param i: A square number.
    :return: The square root of i.
    :raises ValueError if i is not a square number.
    """

    # TODO: implementation
    return int(math.sqrt(i))


class SudokuProblemEncoder:
    """
    A SAT encoder for Sudoku problems given as SudokuBoard objects representing partial solutions.
    """

    def __init__(self,
                 clause_consumer: ClauseConsumer,
                 lit_factory: CNFLiteralFactory,
                 num_symbols: int,
                 encode_at_most_k_constraint_fn=encode_at_most_k_constraint_binomial):
        """
        Initializes a SudokuProblemEncoder object.

        The encoding is computed and added to the clause consumer during the first call to a public method of the
        constructed object.

        :param clause_consumer: The ClauseConsumer which will receive the encoding's clauses.
        :param lit_factory: The CNFLiteralFactory used to create SAT literals.
        :param num_symbols: The number of distinct symbols that may occur on the Sudoku board. For a K x K board, this
                            is K. num_symbols must be a square number.
        :param encode_at_most_k_constraint_fn: An encode_at_most_k_constraint_* function from the
                                               cscl.cardinality_constraint_encoders package. By default, the binomial
                                               encoder is used.
        :raises ValueError if num_symbols is not a non-zero square integer.
        """
        self.__clause_consumer = clause_consumer
        self.__lit_factory = lit_factory
        self.__num_symbols = num_symbols

        # Set up an at-most-1 constraint encoder:
        def __encode_at_most_1_constraint(constrained_lits):
            for clause in encode_at_most_k_constraint_fn(lit_factory, 1, constrained_lits):
                clause_consumer.consume_clause(clause)
        self.__encode_at_most_1_constraint = __encode_at_most_1_constraint

        # __at is either None or a 3-dimensional array at[0...num_symbols-1][0...num_symbols-1][0...num_symbols-1]
        # filled with literals with literals with distinct SAT variables.
        # Encoding: __at[row][col][sym] is true :<=> cell (row,col) has symbol sym+1
        # This variable is initialized by self.__lazy_encode_general_sudoku_constraints().
        self.__at = None

        # Flag signifying whether self.__lazy_encode_general_sudoku_constraints() has been called.
        self.__has_created_general_sudoku_constraints = False

        try:
            self.__box_size = positive_int_square(num_symbols)
        except ValueError:
            raise ValueError("num_symbols must be a non-zero square number.")

    def __lazy_encode_general_sudoku_constraints(self):
        """
        On its first call, encodes the general Sudoku board constraints for a sudoku board with size K x K with
        K = self.__num_symbols. On subsequent calls, this method is a no-op.

        Post-conditions:
        __at is a 3-dimensional array at[0...__num_symbols-1][0...__num_symbols-1][0...__num_symbols-1]
        filled with literals with distinct SAT variables such that the following holds wrt. the SAT encoding:
        __at[row][col][sym] is true <=> cell (row,col) has symbol sym+1

        :return: None
        """
        if self.__has_created_general_sudoku_constraints:
            return

        num_symbols = self.__num_symbols
        self.__at = []
        for i in range(0, num_symbols):
            row = [[self.__lit_factory.create_literal() for _ in range(0, num_symbols)]
                   for _ in range(0, num_symbols)]
            self.__at.append(row)

        # Constraint: Each field may have at most one symbol
        for row, col in itertools.product(range(0, num_symbols), range(0, num_symbols)):
            self.__encode_at_most_1_constraint(self.__at[row][col])
            # self.__at[row][col] is the list of symbol-variables for cell (row,col)

        # Constraint: In each row, each symbol must appear exactly once
        for row, sym in itertools.product(range(0, num_symbols), range(0, num_symbols)):
            symbols_in_row = [self.__at[row][col][sym] for col in range(0, num_symbols)]
            self.__encode_at_most_1_constraint(symbols_in_row)
            self.__clause_consumer.consume_clause(symbols_in_row)

        # Constraint: In each column, each symbol must appear exactly once
        for col, sym in itertools.product(range(0, num_symbols), range(0, num_symbols)):
            symbols_in_col = [self.__at[row][col][sym] for row in range(0, num_symbols)]
            self.__encode_at_most_1_constraint(symbols_in_col)
            self.__clause_consumer.consume_clause(symbols_in_col)

        # Constraint: In each box, each symbol must appear exactly once
        num_boxes = self.__box_size

        def __box_indices(box_row, box_col):
            return itertools.product(range(box_row * self.__box_size, (box_row+1) * self.__box_size),
                                     range(box_col * self.__box_size, (box_col+1) * self.__box_size))

        for box_i, box_j, sym in itertools.product(range(0, num_boxes), range(0, num_boxes), range(0, num_symbols)):
            symbols_in_box = [self.__at[i][j][sym] for i, j in __box_indices(box_i, box_j)]
            self.__encode_at_most_1_constraint(symbols_in_box)
            self.__clause_consumer.consume_clause(symbols_in_box)

        self.__has_created_general_sudoku_constraints = True

    def get_symbol_literal(self, row, col, symbol):
        """
        Gets the SAT literal for the fact "The cell with indices (`row`, `col`) contains the symbol `symbol`"

        :param row: The cell's row index, an int in range(0, num_symbols)
        :param col: The cell's column index, an int in range(0, num_symbols)
        :param symbol: The symbol, an int in range(1, num_symbols+1)
        :raises ValueError if row, col or symbol are out of bounds.
        :return: The SAT literal as described above.
        """
        if row not in range(0, self.__num_symbols)\
                or col not in range(0, self.__num_symbols)\
                or symbol not in range(1, self.__num_symbols+1):
            raise ValueError("Index out of bounds")
        self.__lazy_encode_general_sudoku_constraints()
        return self.__at[row][col][symbol-1]

    def get_required_fixed_assignments(self, board: SudokuBoard):
        """
        Gets a list of SAT literals representing the facts (i.e. the non-None fields) contained in the given
        Sudoku problem instance board. If the Sudoku problem encoding has not been passed to the clause consumer
        yet, only the problem-instance-independent part of the Sudoku problem encoding is passed to the
        clause consumer. To solve the Sudoku instance, the literals returned by this function must be
        added to the problem as unary clauses, or passed to the SAT solver as assumptions.

        :param board: A Sudoku board of size num_symbols x num_symbols
        :raises ValueError if the board has an illegal size.
        :return: A list of SAT literals as described above.
        """
        if board.get_size() != self.__num_symbols:
            raise ValueError("Illegal board size")

        self.__lazy_encode_general_sudoku_constraints()
        board_indices = itertools.product(range(0, board.get_size()), range(0, board.get_size()))
        return [self.__at[i][j][board.get(i, j)-1] for i, j in board_indices if board.get(i, j) is not None]


class SudokuSolver:

    def __init__(self,
                 num_symbols: int,
                 sat_solver: SatSolver,
                 sudoku_problem_encoder=None):
        """
        Initializes the SudokuSolver object.

        :param num_symbols: The number of distinct symbols that may occur on the Sudoku board. For a K x K board, this
                            is K. num_symbols must be a square number.
        :param sat_solver: A SAT solver that has no clauses.
        :param sudoku_problem_encoder: The Sudoku SAT problem encoder. If None, a SudokuProblemEncoder is used to create
                                       the SAT encoding.
        :raises ValueError if num_symbols is not a non-zero square integer.
        """
        self.__sat_solver = sat_solver
        self.__num_symbols = num_symbols

        if sudoku_problem_encoder is None:
            self.__encoder = SudokuProblemEncoder(sat_solver, sat_solver, num_symbols)
        else:
            self.__encoder = sudoku_problem_encoder

    def solve(self, board: SudokuBoard):
        """
        Solves a Sudoku problem instance.

        If the given partial Sudoku solution can be completed, its completion is returned in the form of a SudokuBoard.
        Otherwise, None is returned.

        :param board: A Sudoku board of size num_symbols x num_symbols
        :raises ValueError if the board has an illegal size.
        :return: A SudokuBoard or None, as described above.
        """
        if board.get_size() != self.__num_symbols:
            raise ValueError("Illegal board size")

        fixed_assignments = self.__encoder.get_required_fixed_assignments(board)
        is_sat = self.__sat_solver.solve(fixed_assignments)
        if not is_sat:
            return None
        return self.__solution_to_board(board)

    def __solution_to_board(self, problem_instance: SudokuBoard) -> SudokuBoard:
        result = problem_instance.clone()
        n_symbols = problem_instance.get_size()
        for i, j, sym in itertools.product(range(0, n_symbols), range(0, n_symbols), range(1, n_symbols+1)):
            sat_result = self.__sat_solver.get_assignment(self.__encoder.get_symbol_literal(i, j, sym))
            if sat_result is None:
                result.set(i, j, 'x')
            elif sat_result:
                result.set(i, j, sym)
        return result
