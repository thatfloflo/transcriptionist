from __future__ import annotations
from typing import Any, Sequence, Union, Optional
from multimethod import multimethod
from .constants import Direction

Coordinate = Union[
    tuple[Optional[int], int],
    tuple[int, Optional[int]],
    list[Optional[int], int],
    list[int, Optional[int]],
    'MatrixPointer'
]

class Matrix:
    """Simple implementation of two-dimensional matrices of fixed dimensions."""

    default_value: Any
    __cells: dict[tuple[int, int], Any]
    __n_rows: int
    __n_cols: int
    __row_labels: Optional[Sequence]
    __col_labels: Optional[Sequence]
    __cell_width: Optional[int]

    def __init__(
        self,
        rows: int,
        cols: int,
        default_value: Any = None,
        row_labels: Optional[Sequence] = None,
        col_labels: Optional[Sequence] = None,
        cell_width: Optional[int] = 0
    ):
        """Creates a new matrix of specified dimensions.

        Creates a new matrix with dimensions as specified by 'rows' and 'cols' and
        initialises all cells with 'default_value'. The row and column labels and
        specified cell width are only used when the matrix is converted to a string,
        e.g. for printing."""
        if not isinstance(rows, int):
            raise TypeError("Argument `rows` must be of type int.")
        if not isinstance(cols, int):
            raise TypeError("Argument `cols` must be of type int.")
        if rows < 1 or cols < 1:
            raise ValueError(f"Matrix dimensions must be at least 1x1, {rows}x{cols} specified.")
        self.default_value = default_value
        self.__cells = {}
        self.__n_rows = rows
        self.__n_cols = cols
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                self.__cells[(r, c)] = self.default_value
        self.row_labels = row_labels
        self.col_labels = col_labels
        self.cell_width = cell_width

    def copy(self) -> Matrix:
        """Returns a shallow copy of itself."""
        m = Matrix(self.n_rows, self.n_cols, self.default_value, self.row_labels, self.col_labels, self.cell_width)
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                m[r, c] = self[r, c]
        return m

    def __copy__(self) -> Matrix:
        """Returns a shallow copy of itself."""
        return self.copy()

    @property
    def n_rows(self) -> int:
        """Returns the number of rows in the matrix."""
        return self.__n_rows

    @property
    def n_cols(self) -> int:
        """Returns the number of columns in the matrix."""
        return self.__n_cols

    @property
    def n_dim(self) -> tuple[int, int]:
        """Returns a tuple of the dimensions of the matrix in the form (rows, cols)."""
        return (self.n_rows, self.n_cols)

    @property
    def size(self) -> int:
        """Returns the total number of cells in the matrix."""
        return self.n_rows * self.n_cols

    @property
    def row_labels(self) -> Optional[Sequence]:
        """Returns the labels used for the columns."""
        return self.__row_labels

    @row_labels.setter
    def row_labels(self, row_labels: Optional[Sequence]):
        """Sets the row labels."""
        if row_labels is None:
            self.__row_labels = None
            return
        try:
            length = len(row_labels)
        except TypeError:
            raise TypeError("Row labels must be a either None or a sequence type with a length, object of type '{type(row_labels}' has no len().")
        if length is not self.n_rows:
            raise ValueError(f"Row labels must be the same length as number of rows in the matrix. Length of labels: {length}, number of rows: {self.n_rows}")
        self.__row_labels = row_labels

    @property
    def col_labels(self) -> Optional[Sequence]:
        """Returns the labels used for the y-axis (rows)."""
        return self.__col_labels

    @col_labels.setter
    def col_labels(self, col_labels: Optional[Sequence]):
        """Sets the column labels."""
        if col_labels is None:
            self.__col_labels = None
            return
        try:
            length = len(col_labels)
        except TypeError:
            raise TypeError("Column labels must be a either None or a sequence type with a length, object of type '{type(col_labels}' has no len().")
        if length is not self.n_cols:
            raise ValueError(f"Column labels must be the same length as number of columns in the matrix. Length of labels: {length}, number of columns: {self.n_cols}")
        self.__col_labels = col_labels

    @property
    def cell_width(self) -> int:
        """Returns the cell width used for str()/repr() alignment."""
        return self.__cell_width

    @cell_width.setter
    def cell_width(self, cell_width: int = 0):
        """Sets the cell width used for str()/repr() alignment."""
        cell_width = int(cell_width)
        if cell_width < 0:
            raise ValueError(f"Cell width must be greater than 0, {cell_width} specified.")
        self.__cell_width = cell_width

    @property
    def cols(self) -> list:
        """Returns a list of columns, each of which is a list containing row values."""
        buf = []
        for c in range(0, self.n_cols):
            buf.append(self.getcol(c))
        return buf

    @property
    def rows(self) -> list:
        """Returns a list of rows, each of which is a list containing column values."""
        buf = []
        for r in range(0, self.n_rows):
            buf.append(self.getrow(r))
        return buf

    def __wrap_row(self, row:int) -> int:
        """Wraps a negative row index back by substracting from n_rows."""
        if row < 0:
            return self.n_rows + row
        return row

    def __wrap_col(self, col: int) -> int:
        """Wraps a negative column index back by substracting from n_cols."""
        if col < 0:
            return self.n_cols + col
        return col

    def __validate_row_index(self, row: int):
        """Checks if given row index is in range, raises IndexError if not."""
        if row not in range(0, self.n_rows):
            raise IndexError(f"Trying to access row {row} of matrix with {self.n_rows} rows.")

    def __validate_col_index(self, col: int):
        """Checks if given column index is in range, raises IndexError if not."""
        if col not in range(0, self.n_cols):
            raise IndexError(f"Trying to access column {col} of matrix with {self.n_cols} columns.")

    @multimethod
    def getitem(self, row: int, col: int = None) -> Any:
        """Return item at coordinates (row, col)."""
        row = self.__wrap_row(row)
        self.__validate_row_index(row)
        col = self.__wrap_col(col)
        self.__validate_col_index(col)
        return self.__cells[(row, col)]

    @multimethod
    def getitem(self, ptr: MatrixPointer) -> Any:
        return self.getitem(ptr.r, ptr.c)

    @multimethod
    def setitem(self, row: int, col: int, value: Any):
        """Set item at coordinates to value."""
        row = self.__wrap_row(row)
        self.__validate_row_index(row)
        col = self.__wrap_col(col)
        self.__validate_col_index(col)
        self.__cells[(row, col)] = value

    @multimethod
    def setitem(self, ptr: MatrixPointer, value: Any):
        self.setitem(ptr.r, ptr.c, value)

    def getrow(self, row: int) -> list:
        """Get row at specified index and return as list."""
        row = self.__wrap_row(row)
        self.__validate_row_index(row)
        buf = []
        for col in range(0, self.n_cols):
            buf.append(self[row, col])
        return buf

    def setrow(self, row: int, values: Sequence):
        """Set row at specified index to be equal to a sequence of values."""
        row = self.__wrap_row(row)
        self.__validate_row_index(row)
        if len(values) != self.n_cols:
            raise ValueError("Sequence of supplied row values must have equal length to number of matrix columns.")
        for i in range(0, self.n_cols):
            self[row, i] = values[i]

    def getcol(self, col: int) -> list:
        """Get column at specified index and return as list."""
        col = self.__wrap_col(col)
        self.__validate_col_index(col)
        buf = []
        for row in range(0, self.n_rows):
            buf.append(self[row, col])
        return buf

    def setcol(self, col: int, values: Sequence):
        """Set column at specified index to be equal to a sequence of values."""
        col = self.__wrap_col(col)
        self.__validate_col_index(col)
        if len(values) != self.n_rows:
            raise ValueError("Sequence of supplied column values must have equal length to number of matrix rows.")
        for i in range(0, self.n_rows):
            self[i, col] = values[i]

    def __getitem__(self, key: Coordinate) -> Any:
        """Return item at coordinates (row, col).

        Call as m[row, col]. Row and col may be integers or None. m[row, None] will
        return a list with the entire row, m[None, col] will return a list with the
        entire column. m[None, None] will raise an IndexError.
        """
        if isinstance(key, MatrixPointer):
            key = (key.r, key.c)
        if isinstance(key, list):
            key = tuple(key)
        if isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], (int, type(None))) and isinstance(key[1], (int, type(None))):
            row, col = key
            if row is not None and col is not None:
                return self.getitem(row, col)
            if row is not None and col is None:
                return self.getrow(row)
            if row is None and col is not None:
                return self.getcol(col)
            if row is None and col is None:
                raise IndexError("At least one index value (row, col) must be supplied, (None, None) given.")
        raise KeyError(f"Key must be either of type tuple[int, int] or list[int, int].")

    def __setitem__(self, key: Coordinate, value: Union[Any, Sequence]):
        """Set item at coordinates (row, col) to value.

        Call as m[row, col] = value. Row and col may be integers or None. m[row, None] = values
        is equivalent to m.setrow(row, values), m[None, col] = values is equivalent to
        m.setcol(col, values). m[None, None] = value will raise an IndexError."""
        if isinstance(key, MatrixPointer):
            key = (key.r, key.c)
        if isinstance(key, list):
            key = tuple(key)
        if isinstance(key, tuple) and len(key) == 2 and isinstance(key[0], (int, type(None))) and isinstance(key[1], (int, type(None))):
            row, col = key
            if row is not None and col is not None:
                return self.setitem(row, col, value)
            if row is not None and col is None:
                return self.setrow(row, value)
            if row is None and col is not None:
                return self.setcol(col, value)
            if row is None and col is None:
                raise IndexError("At least one index value (row, col) must be supplied, (None, None) given.")
        raise KeyError(f"Key must be either of type tuple[int, int] or list[int, int].")


    def __bool__(self) -> bool:
        """Returns False if all the cells of the matrix are identical to the default_value, True otherwise."""
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                if self.__cells[(r, c)] is not self.default_value:
                    return True
        return False

    def stringify(
        self,
        row_labels: Optional[Sequence] = None,
        col_labels: Optional[Sequence] = None,
        cell_width: Optional[int] = 0
    ):
        """Returns an informative string representation of the matrix.

        The row_labels, col_labels parameters, if supplied, must match the dimensions of
        the matrix. cell_width is used to right-pad the cells for alignment purposes and
        ideally is the width of the widest string representation to be expected for any
        cell in the matrix."""
        buf = ""
        for r in range(0, self.n_rows):
            if r == 0 and col_labels is not None:
                if row_labels is not None:
                    buf += ''.ljust(cell_width) + " " # Empty cell
                buf += "  " # Cover distance of "[ "
                for label in col_labels:
                    buf += str(label).ljust(cell_width)
                    buf += "  " # Add space in lieu for ", "
            if r == 0:
                buf += "\n"
            if r > 0:
                buf += " ]\n"
            for c in range(0, self.n_cols):
                if c == 0:
                    if row_labels is not None:
                        if r < len(row_labels):
                            buf += str(row_labels[r]).ljust(cell_width) + " "
                        else:
                            buf += " " * cell_width + " "
                    buf += "[ "
                if c > 0:
                    buf += ", "
                buf += str(self[r, c]).ljust(cell_width)
        buf += " ]"
        return buf

    def __str__(self):
        """Returns an informative string representation of the matrix using object's default labels and cell width."""
        return self.stringify(
            row_labels=self.row_labels,
            col_labels=self.col_labels,
            cell_width=self.cell_width
        )

    def __repr__(self):
        """Returns a parseable representation of the matrix as a list of lists."""
        buf = "["
        for r in range(0, self.n_rows):
            if r > 0:
                buf += "],\n ["
            else:
                buf += "["
            for c in range(0, self.n_cols):
                if c > 0:
                    buf += ", "
                buf += repr(self[r, c]).ljust(self.cell_width)
        return buf + "]]"

    def mutate(self, func: callable) -> None:
        """Apply function 'func' to every cell in the matrix."""
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                self[r, c] = func(self[r, c])

    def map(self, func: callable) -> Matrix:
        """Return a new matrix with 'func' applied to every cell."""
        m = Matrix(self.n_rows, self.n_cols, self.default_value, self.row_labels, self.col_labels, self.cell_width)
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                m[r, c] = func(self[r, c])
        return m


class MatrixPointer:

    __r: int
    __c: int
    __m: Matrix

    def __init__(self, m: Matrix, r: int = 0, c: int = 0):
        if not isinstance(m, Matrix):
            raise TypeError(f"Argument 'm' must be of type 'Matrix', {type(m)} given.")
        self.__m = m
        self.r = r
        self.c = c

    def advance(self) -> bool:
        """Advance pointer one cell in the matrix.

        Advances the pointer to the next column of the current row in the matrix. Skips
        to next row if end of columns is reached. Returns True if pointer has been
        advanced, False otherwise (thus, False means the last cell of the matrix has
        been reached)."""
        try:
            self.c += 1
            return True
        except ValueError:
            try:
                self.r += 1
                self.c = 0
                return True
            except ValueError:
                return False

    @property
    def m(self) -> Matrix:
        return self.__m

    @property
    def r(self) -> int:
        return self.__r

    @r.setter
    def r(self, r: int):
        if r >= self.m.n_rows:
            raise ValueError(f"Attempt to assign value out of range of matrix dimensions: (r = {r}) >= {self.m.n_rows}")
        self.__r = int(r)

    @property
    def c(self) -> int:
        return self.__c

    @c.setter
    def c(self, c: int):
        if c >= self.m.n_cols:
            raise ValueError(f"Attempt to assign value out of range of matrix dimensions: (c = {c}) >= {self.m.n_cols}")
        self.__c = int(c)

    def __getitem__(self, key: int) -> int:
        if not isinstance(key, int):
            raise TypeError("Index on MatrixPointer is only defined for integers.")
        if key == 0:
            return self.r
        if key == 1:
            return self.c
        raise IndexError("Index for MatrixPointer must be in range [0, 1].")

    def __setitem__(self, key: int, value: int):
        if not isinstance(key, int):
            raise TypeError("Index on MatrixPointer is only defined for integers.")
        if not isinstance(value, int):
            raise ValueError("MatrixPointer coordinates can only be assigned integer values.")
        if key == 0:
            self.r = value
            return
        if key == 1:
            self.c = value
            return
        raise IndexError("Index for MatrixPointer must be in range [0, 1]")

    def __repr__(self):
        return f"[{self.r}, {self.c}]"

    def __str__(self):
        return f"[{self.r}, {self.c}]"

    def __eq__(self, other: Union[MatrixPointer, tuple[int, int], list[int, int]]) -> bool:
        if isinstance(other, MatrixPointer):
            other = (other.r, other.c)
        elif isinstance(other, list):
            other = tuple(other)
        if isinstance(other, tuple):
            if len(other) != 2:
                raise NotImplemented
            if (self.r, self.c) == other:
                return True
            else:
                return False
        raise NotImplemented

    def __hash__(self) -> int:
        return hash((self.r, self.c))

    def __len__(self) -> int:
        return 2

    def copy(self) -> MatrixPointer:
        """Returns a shallow copy of itself."""
        return MatrixPointer(self.m, self.r, self.c)

    def __copy__(self) -> MatrixPointer:
        """Returns a shallow copy of itself."""
        return self.copy()

    def mleft(self):
        """Moves pointer one cell to the left.

        Returns True on success, False if it is not possible to move leftward."""
        try:
            self.c -= 1
            return True
        except ValueError:
            return False

    def mright(self):
        """Moves pointer on cell to the right.

        Returns True on success, False if it is not possible to move rightward."""
        try:
            self.c += 1
            return True
        except ValueError:
            return False

    def mup(self):
        """Moves pointer one cell up.

        Returns True on success, False if it is not possible to move upward."""
        try:
            self.r -= 1
            return True
        except ValueError:
            return False

    def mupleft(self):
        """Moves pointer one cell up and left.

        Returns True on success, False if it is not possible to move up and leftward."""
        if (self.r - 1) < 0 or (self.c - 1) < 0:
            return False
        try:
            reset = (self.r, self.c)
            self.r -= 1
            self.c -= 1
            return True
        except ValueError:
            self.r = reset[0]
            self.c = reset[1]
            return False

    def mupright(self):
        """Moves pointer one cell up and right.

        Returns True on success, False if it is not possible to move up and rightward."""
        if (self.r - 1) < 0 or (self.c + 1) >= self.m.n_cols:
            return False
        try:
            reset = (self.r, self.c)
            self.r -= 1
            self.c += 1
            return True
        except ValueError:
            self.r = reset[0]
            self.c = reset[1]
            return False

    def mdown(self):
        """Moves pointer one cell down.

        Returns True on success, False if it is not possible to move downward."""
        try:
            self.r += 1
            return True
        except ValueError:
            return False

    def mdownleft(self):
        """Moves pointer one cell down and left.

        Returns True on success, False if it is not possible to move down and leftward."""
        if (self.r + 1) >= self.m.n_rows or (self.c - 1) < 0:
            return False
        try:
            reset = (self.r, self.c)
            self.r += 1
            self.c -= 1
            return True
        except ValueError:
            self.r = reset[0]
            self.c = reset[1]
            return False

    def mdownright(self):
        """Moves pointer one cell down and right.

        Returns True on success, False if it is not possible to move down and rightward."""
        if (self.r + 1) >= self.m.n_rows or (self.c + 1) >= self.m.n_cols:
            return False
        try:
            reset = (self.r, self.c)
            self.r += 1
            self.c += 1
            return True
        except ValueError:
            self.r = reset[0]
            self.c = reset[1]
            return False

    def cleft(self) -> Union[MatrixPointer, bool]:
        """Returns a copy with pointer moved one cell left.

        Returns MatrixPointer on success, False if it is not possible to move leftward."""
        c = self.copy()
        if c.mleft():
            return c
        return False

    def cright(self) -> Union[MatrixPointer, bool]:
        """Returns a copy with pointer moved one cell right.

        Returns MatrixPointer on success, False if it is not possible to move rightward."""
        c = self.copy()
        if c.mright():
            return c
        return False

    def cup(self) -> Union[MatrixPointer, bool]:
        """Returns a copy with pointer moved one cell up.

        Returns MatrixPointer on success, False if it is not possible to move upward."""
        c = self.copy()
        if c.mup():
            return c
        return False

    def cupleft(self) -> Union[MatrixPointer, bool]:
        """Returns a copy with pointer moved one cell up and left.

        Returns MatrixPointer on success, False if it is not possible to move up and leftward."""
        c = self.copy()
        if c.mupleft():
            return c
        return False

    def cupright(self) -> Union[MatrixPointer, bool]:
        """Returns a copy with pointer moved one cell up and right.

        Returns MatrixPointer on success, False if it is not possible to move up and rightward."""
        c = self.copy()
        if c.mupright():
            return c
        return False

    def cdown(self) -> Union[MatrixPointer, bool]:
        """Returns a copy with pointer moved one cell down.

        Returns MatrixPointer on success, False if it is not possible to move downward."""
        c = self.copy()
        if c.mdown():
            return c
        return False

    def cdownleft(self) -> Union[MatrixPointer, bool]:
        """Returns a copy with pointer moved one cell down and left.

        Returns MatrixPointer on success, False if it is not possible to move down and leftward."""
        c = self.copy()
        if c.mdownleft():
            return c
        return False

    def cdownright(self) -> Union[MatrixPointer, bool]:
        """Returns a copy with pointer moved one cell down and right.

        Returns MatrixPointer on success, False if it is not possible to move down and rightward."""
        c = self.copy()
        if c.mdownright():
            return c
        return False

    def directionto(self, other: MatrixPointer) -> Direction:
        dir = Direction.NONE
        if other.c < self.c:
            dir |= Direction.WEST
        elif other.c > self.c:
            dir |= Direction.EAST
        if other.r < self.r:
            dir |= Direction.NORTH
        elif other.r > self.r:
            dir |= Direction.SOUTH
        return dir

    def directionfrom(self, other: MatrixPointer) -> Direction:
        return other.directionto(self)
