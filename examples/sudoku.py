import math
import itertools


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
