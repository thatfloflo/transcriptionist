"""Mutable matrix objects for matrix based computations.

This submodule provides an object-oriented implementation of two-dimensional matrices.
"""
from __future__ import annotations
from typing import Any, Sequence, Union, Optional
from multimethod import multimethod
from .constants import Direction

Coordinate = Union[
    tuple[Optional[int], int],
    tuple[int, Optional[int]],
    list[Optional[int], int],
    list[int, Optional[int]],
    "MatrixPointer",
]
"""Compound type hint for methods that accept complex inputs for a coordinate in the form
of either a Matrix pointer, or a 2 member tuple or list where at least one value is an
integer and the other either None or an integer."""


class Matrix:
    """Simple implementation of two-dimensional matrices of specified dimensions.

    Attributes:
        default_value: The value to be inserted into new/empty cells. Also used as the
            basis for boolean conversion of a `Matrix`: if all the cells are identical to
            `default_value` then the `Matrix` evaluates to False; if any cells have
            a value not identical to `default_value` then the `Matrix` evaluates to True.
    """

    default_value: Any
    __data: list[list[Any]]
    __n_rows: int
    __n_cols: int
    __row_labels: Optional[Sequence]
    __col_labels: Optional[Sequence]
    __cell_width: Optional[int]

    @multimethod
    def __init__(
        self,
        rows: int,
        cols: int,
        default_value: Any = None,
        row_labels: Optional[Sequence] = None,
        col_labels: Optional[Sequence] = None,
        cell_width: Optional[int] = 0,
    ):
        """Creates a new matrix of specified dimensions.

        Creates a new matrix with dimensions as specified by `rows` and `cols` and
        initialises all cells with `default_value`. The row and column labels and
        specified cell width are only used when the matrix is converted to a string,
        e.g. for printing.

        Args:
            rows: The number of rows the matrix should have.
            cols: The number of columns the matrix should have.
            default_value: The default value with which new cells should be initialised.
            row_labels: An optional sequence of length `rows` to be used as row labels.
            col_labels: An optional sequence of length `cols` to be used as column labels.
            cell_width: The cell width to be used for alignment when the matrix is
                represented as a string.
        """
        if not isinstance(rows, int):
            raise TypeError("Argument `rows` must be of type int.")
        if not isinstance(cols, int):
            raise TypeError("Argument `cols` must be of type int.")
        if rows < 1 or cols < 1:
            raise ValueError(
                f"Matrix dimensions must be at least 1x1, {rows}x{cols} specified."
            )
        self.default_value = default_value
        self.__n_rows = rows
        self.__n_cols = cols
        self.__data = []
        for _r in range(0, self.n_rows):
            data_row = []
            for _c in range(0, self.n_cols):
                data_row.append(self.default_value)
            self.__data.append(data_row)
        self.row_labels = row_labels
        self.col_labels = col_labels
        self.cell_width = cell_width

    @multimethod
    def __init__(  # noqa: F811
        self,
        data: Sequence,
        default_value: Any = None,
        row_labels: Optional[Sequence] = None,
        col_labels: Optional[Sequence] = None,
        cell_width: Optional[int] = 0,
    ):
        """Creates a new matrix from a sequence.

        Creates a new matrix from a sequence of sequences (e.g. a list of lists), where
        the outer sequence represents rows and the inner sequence represents columns,
        the same format as is accessible via `Matrix.rows`. The row and column labels and
        specified cell width are only used when the matrix is converted to a string,
        e.g. for printing. The specified `default_value` will be used only if further rows
        or columns are added later.

        Args:
            data: A sequence of sequences, representing columns inside rows of data.
            default_value: The default value with which new cells should be initialised.
            row_labels: An optional sequence of length `rows` to be used as row labels.
            col_labels: An optional sequence of length `cols` to be used as column labels.
            cell_width: The cell width to be used for alignment when the matrix is
                represented as a string.

        Raises:
            TypeError: Raised if `data` is not a sequence containing a sequence.
        """
        if not isinstance(data, Sequence) or not isinstance(data[0], Sequence):
            raise TypeError("Argument `data` must be a sequence of sequences.")

        rows = len(data)
        cols = len(data[0])

        self.__init__(rows, cols, default_value, row_labels, col_labels, cell_width)

        for r in range(0, rows):
            self.setrow(r, data[r])

    def copy(self) -> Matrix:
        """Makes a shallow copy of itself.

        Returns:
            A new `Matrix` object with all the properties and cell values recursively
            assigned to the new object. Because this is shallow and the individual cell
            values are simply assigned to the new cell, it's important to note that where
            cell values reference specific objects (e.g. a `MatrixPointer`), changes to
            these in the new copy may also affect those in the original copy. If it is
            necessary to also carry out some operation on the cell values before copying
            them then `map` is a better choice. For example, to create a deep copy of
            a `Matrix` itself containing numeric matrices::

                >>> m = Matrix(1, 1, Matrix(1, 1, 0))
                [[[[0]]]]
                >>> shallow = m.copy()
                >>> shallow[0, 0][0, 0] = 1 # Affects inner matrix in both m and shallow
                >>> shallow
                [[[[1]]]]
                >>> m
                [[[[1]]]]
                >>> deep = m.map(Matrix.copy)
                >>> deep[0, 0][0, 0] = 2 # Won't affect inner matrix of m/shallow
                >>> deep
                [[[[2]]]]
                >>> m
                [[[[1]]]]
        """
        m = Matrix(
            self.n_rows,
            self.n_cols,
            self.default_value,
            self.row_labels,
            self.col_labels,
            self.cell_width,
        )
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                m[r, c] = self[r, c]
        return m

    def __copy__(self) -> Matrix:
        """Makes a shallow copy of itself, cf. `Matrix.copy` method."""
        return self.copy()

    @property
    def n_rows(self) -> int:
        """The number of rows in the matrix (read-only)."""
        return self.__n_rows

    @property
    def n_cols(self) -> int:
        """The number of columns in the matrix (read-only)."""
        return self.__n_cols

    @property
    def n_dim(self) -> tuple[int, int]:
        """A tuple of the matrix dimensions in the form `(rows, cols)` (read-only)."""
        return (self.n_rows, self.n_cols)

    @property
    def size(self) -> int:
        """The total number of cells in the matrix."""
        return self.n_rows * self.n_cols

    def __len__(self) -> int:
        """Returns the total number of cells in the matrix."""
        return self.size

    @property
    def row_labels(self) -> Optional[Sequence]:
        """The labels used for the rows.

        Can be reassigned, but assigned values are checked to be either None or
        a Sequence and they must match the number of rows in their length property.

        Raises:
            TypeError: Raised if assigned row labels are neither None nor a Sequence type.
            ValueError: Raised if the length of an assigned value does not match `n_rows`.
        """
        return self.__row_labels

    @row_labels.setter
    def row_labels(self, row_labels: Optional[Sequence]):
        if row_labels is None:
            self.__row_labels = None
            return
        try:
            length = len(row_labels)
        except TypeError as exc:
            raise TypeError(
                (
                    "Row labels must be a either None or a Sequence type with a length, "
                    " object of type '{type(row_labels}' has no len()."
                )
            ) from exc
        if length is not self.n_rows:
            raise ValueError(
                (
                    f"Row labels must be the same length as number of rows in the matrix."
                    f" Length of labels: {length}, number of rows: {self.n_rows}"
                )
            )
        self.__row_labels = row_labels

    @property
    def col_labels(self) -> Optional[Sequence]:
        """The labels used for the columns.

        Can be reassigned, but assigned values are checked to be either None or
        a Sequence and they must match the number of columns in their length property.

        Raises:
            TypeError: Raised if assigned row labels are neither None nor a Sequence type.
            ValueError: Raised if the length of an assigned value does not match `n_cols`.
        """
        return self.__col_labels

    @col_labels.setter
    def col_labels(self, col_labels: Optional[Sequence]):
        if col_labels is None:
            self.__col_labels = None
            return
        try:
            length = len(col_labels)
        except TypeError as exc:
            raise TypeError(
                (
                    f"Column labels must be a either None or a sequence type with a "
                    f"length, object of type '{type(col_labels)}' has no len()."
                )
            ) from exc
        if length is not self.n_cols:
            raise ValueError(
                (
                    f"Column labels must be the same length as number of columns in the "
                    f"matrix. Length of labels: {length}, number of columns: "
                    f"{self.n_cols}"
                )
            )
        self.__col_labels = col_labels

    @property
    def cell_width(self) -> int:
        """The cell width (>=0) to be used for str()/repr() alignment.

        Raises:
            ValueError: Raised if cell width is assigned a value below 0.
        """
        return self.__cell_width

    @cell_width.setter
    def cell_width(self, cell_width: int = 0):
        cell_width = int(cell_width)
        if cell_width < 0:
            raise ValueError(
                f"Cell width must be greater or equal to 0, {cell_width} specified."
            )
        self.__cell_width = cell_width

    @property
    def cols(self) -> list:
        """Provides list access to the matrix's columns.

        Provides list access to the matrix's columns, each of which is a list
        containing row values.

        Returns:
            A list containing the matrix's columns.
        """
        buf = []
        for c in range(0, self.n_cols):
            buf.append(self.getcol(c))
        return buf

    @property
    def rows(self) -> list:
        """Provides list access to the matrix's rows.

        Provides list access to the matrix's rows, each of which is a list containing
        column values.

        Returns:
            A list containing the matrix's rows.
        """
        return self.__data

    def __wrap_row(self, row: int) -> int:
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
        """Checks if given row index is in range, raises IndexError if not.

        Raises:
            IndexError: Raised if `row` is not inbetween 0 and the number of rows in the
            matrix.
        """
        if row not in range(0, self.n_rows):
            raise IndexError(
                f"Trying to access row {row} of matrix with {self.n_rows} rows."
            )

    def __validate_col_index(self, col: int):
        """Checks if given column index is in range, raises IndexError if not.

        Raises:
            IndexError: Raised if `col` is not inbetween 0 and the number of columns
                in the matrix.
        """
        if col not in range(0, self.n_cols):
            raise IndexError(
                f"Trying to access column {col} of matrix with {self.n_cols} columns."
            )

    @multimethod
    def getitem(self, row: int, col: int = None) -> Any:
        """Gets the item at the coordinates `row` and `col`.

        Returns the item stored in the matrix cell indicated by the coordinates `row`
        and `col`. If only a `row` value is provided, the entire row at that index is
        returned as a list of its column values (cf. `getrow`).

        Args:
            row: Index of a row in the matrix.
            col: Intex of a column in the matrix. If not supplied or None is given the
                call will be treated like `getrow(row)`.

        Raises:
            IndexError: Raised if `row` or `col` are out of the range of the matrix's
                dimensions.
        """
        row = self.__wrap_row(row)
        self.__validate_row_index(row)
        col = self.__wrap_col(col)
        self.__validate_col_index(col)
        return self.__data[row][col]

    @multimethod
    def getitem(self, ptr: MatrixPointer) -> Any:  # noqa: F811
        """Gets the item at the coordinates identified by the `MatrixPointer`.

        Args:
            ptr: A `MatrixPointer` pointing to a cell in the matrix.

        Raises:
            IndexError: Raised if the coordinates of the supplied `MatrixPointer` are out
                of the range of the matrix's dimensions.
        """
        return self.getitem(ptr.r, ptr.c)

    @multimethod
    def setitem(self, row: int, col: int, value: Any) -> None:
        """Sets the item at the coordinates `row` and `col` to `value`.

        Sets the item stored in the matrix cell indicated by the coordinates `row`
        and `col` to `value`.

        Args:
            row: Index of a row in the matrix.
            col: Intex of a column in the matrix.

        Raises:
            IndexError: Raised if `row` or `col` are out of the range of the matrix's
                dimensions.
        """
        row = self.__wrap_row(row)
        self.__validate_row_index(row)
        col = self.__wrap_col(col)
        self.__validate_col_index(col)
        self.__data[row][col] = value

    @multimethod
    def setitem(self, ptr: MatrixPointer, value: Any) -> None:  # noqa: F811
        """Sets the item at the coordinates identified by the `MatrixPointer` to `value`.

        Args:
            ptr: A `MatrixPointer` pointing to a cell in the matrix.

        Raises:
            IndexError: Raised if the coordinates of the supplied `MatrixPointer` are out
                of the range of the matrix's dimensions.
        """
        self.setitem(ptr.r, ptr.c, value)

    def getrow(self, row: int) -> list:
        """Gets row at specified index and returns a list of column values.

        Args:
            row: Index of the row to be returned.

        Raises:
            IndexError: Raised if the specified row index is out of the range of the
                matrix's rows.
        """
        row = self.__wrap_row(row)
        self.__validate_row_index(row)
        return self.__data[row]

    def setrow(self, row: int, values: Sequence):
        """Sets the column values of a specified row to the items of a given sequence.

        Args:
            row: Index of the row to be overwritten.
            values: A Sequence of an equal length to the matrix's columns containing the
                values to be assigned to each column in the specified row.

        Raises:
            IndexError: Raised if the specified row index is out of the range of the
                matrix's rows.
            ValueError: Raised if the length of the `values` sequence doesn't match the
                number of columns in the matrix.
        """
        row = self.__wrap_row(row)
        self.__validate_row_index(row)
        if len(values) != self.n_cols:
            raise ValueError(
                (
                    "Sequence of supplied row values must have equal length to number of "
                    "matrix columns."
                )
            )
        self.__data[row] = list(values)

    def getcol(self, col: int) -> list:
        """Gets column at specified index and returns a list of row values.

        Args:
            col: Index of the column to be returned.

        Raises:
            IndexError: Raised if the specified row index is out of the range of the
                matrix's columns.
        """
        col = self.__wrap_col(col)
        self.__validate_col_index(col)
        buf = []
        for row in range(0, self.n_rows):
            buf.append(self[row, col])
        return buf

    def setcol(self, col: int, values: Sequence):
        """Sets the row values of a specified column to the items of a given sequence.

        Args:
            col: Index of the column to be overwritten.
            values: A Sequence of an equal length to the matrix's rows containing the
                values to be assigned to each row in the specified column.

        Raises:
            IndexError: Raised if the specified row index is out of the range of the
                matrix's columns.
            ValueError: Raised if the length of the `values` sequence doesn't match the
                number of rows in the matrix.
        """
        col = self.__wrap_col(col)
        self.__validate_col_index(col)
        if len(values) != self.n_rows:
            raise ValueError(
                (
                    "Sequence of supplied column values must have equal length to number "
                    "of matrix rows."
                )
            )
        for i in range(0, self.n_rows):
            self[i, col] = values[i]

    def __mangle_coordinates(
        self, coords: Coordinate
    ) -> tuple[Optional[int], Optional[int]]:
        """Converts any acceptable Coordinates structure into a uniform 2-tuple.

        Returns:
            A tuple of length two containing the coordinates in the format `(row, col)`.

        Raises:
            TypeError: Raised if the given key does not match the Coordinate type hint.
        """
        if isinstance(coords, MatrixPointer):
            coords = (coords.r, coords.c)
        elif isinstance(coords, list):
            coords = tuple(coords)
        if (
            isinstance(coords, tuple)
            and len(coords) == 2
            and (
                isinstance(coords[0], (int, type(None)))
                or isinstance(coords[1], (int, type(None)))
            )
            and not (coords[0] is None and coords[1] is None)
        ):
            return coords
        raise ValueError(
            (
                "The supplied coordinate must be either a valid MatrixPointer, or match"
                "tuple[int, int] or list[int, int], where at most one occurence of int"
                "may be supplanted by None."
            )
        )

    def __getitem__(self, key: Coordinate) -> Any:
        """Gets item at coordinates `row` and `col`.

        Call as `m[row, col]`. Row and col may be integers or None. `m[row, None]` will
        return a list with the entire row, `m[None, col]` will return a list with the
        entire column. `m[None, None]` will raise an IndexError.

        May also be called with a `MatrixPointer` instead of row and column indeces, e.g.
        as `m[ptr]`, where `ptr` is a `MatrixPointer`.

        Raises:
            IndexError: Raised if either or both of the column or row indeces are out of
                range of the matrix's dimensions.
            TypeError: Raised if the given key does not match the Coordinate type hint.
        """
        row, col = self.__mangle_coordinates(key)
        if row is not None and col is not None:
            return self.getitem(row, col)
        if row is not None and col is None:
            return self.getrow(row)
        if row is None and col is not None:
            return self.getcol(col)

    def __setitem__(self, key: Coordinate, value: Union[Any, Sequence]):
        """Sets item at coordinates `row` and `col` to value.

        Call as `m[row, col] = value`. Row and col may be integers or `None`.
        `m[row, None] = values` is equivalent to `m.setrow(row, values)`,
        `m[None, col] = values` is equivalent to `m.setcol(col, values)`.
        `m[None, None] = value` will raise an IndexError.

        May also be called with a `MatrixPointer` instead of row and column indeces, e.g.
        as `m[ptr] = value`, where `ptr` is a `MatrixPointer`.

        Raises:
            IndexError: Raised if either or both of the column or row indeces are out of
                range of the matrix's dimensions.
            TypeError: Raised if the given key does not match the Coordinate type hint.
        """
        row, col = self.__mangle_coordinates(key)
        if row is not None and col is not None:
            return self.setitem(row, col, value)
        if row is not None and col is None:
            return self.setrow(row, value)
        if row is None and col is not None:
            return self.setcol(col, value)

    def insert_col(self, col: int, values: Optional[Sequence] = None) -> None:
        """Inserts a column into the matrix at a specified position.

        Inserts a new matrix column before the column specified by the index `col`.
        The new column is initialised with the sequene of values in `values` if specified,
        otherwise it is initialised with the matrix's `default_value`.

        Raises:
            ValueError: Raised if `len(values)` does not match the matrix's `n_rows`
            property.
        """
        if values is None:
            values = [self.default_value for _ in range(0, self.n_rows)]
        else:
            values = list(values)
            if len(values) != self.n_rows:
                raise ValueError(
                    (
                        "The supplied sequence of values much match the matrix's number "
                        " of rows in length."
                    )
                )
        for r in range(0, self.n_rows):
            self.__data[r].insert(col, values[r])
        self.__n_cols += 1

    def append_col(self, values: Optional[Sequence] = None) -> None:
        """Appends a new column at the end of the matrix.

        Appends a new column at the end of the matrix. The new column is initialised with
        the sequence in `values` if specified, otherwise it is initialised with the
        matrix's `default_value`.

        `m.append_col(v)` is equivalent to `m.insert_col(m.n_cols, v)`.

        Raises:
            ValueError: Raised if `len(values)` does not match the matrix's `n_rows`
            property.
        """
        self.insert_col(self.n_cols, values)

    def insert_row(self, row: int, values: Optional[Sequence] = None) -> None:
        """Inserts a row into the matrix at a specified position.

        Inserts a new matrix row before the row specified by the index `row`. The
        new row is initialised with the sequence in `values` if specified, otherwise
        it is initialised with the matrix's `default_value`.

        Raises:
            ValueError: Raised if `len(values)` does not match the matrix's `n_cols`
            property.
        """
        if values is None:
            values = [self.default_value for _ in range(0, self.n_cols)]
        else:
            values = list(values)
            if len(values) != self.n_cols:
                raise ValueError(
                    (
                        "The supplied sequence of values much match the matrix's number "
                        "of columns in length."
                    )
                )
        self.__data.insert(row, values)
        self.__n_rows += 1

    def append_row(self, values: Optional[Sequence] = None) -> None:
        """Appends a new row at the end of the matrix.

        Appends a new row at the end of the matrix. The new row is initialised with
        the sequence in `values` if specified, otherwise it is initialised with the
        matrix's `default_value`.

        `m.append_row(v)` is equivalent to `m.insert_row(m.n_rows, v)`.

        Raises:
            ValueError: Raised if `len(values)` does not match the matrix's `n_cols`
            property.
        """
        self.insert_row(self.n_rows, values)

    def __bool__(self) -> bool:
        """Converts matrix to bool.

        Returns:
            False if all the cells of the matrix are identical to `default_value`,
            True otherwise.
        """
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                if self[r, c] is not self.default_value:
                    return True
        return False

    def stringify(  # noqa: C901
        self,
        row_labels: Optional[Sequence] = None,
        col_labels: Optional[Sequence] = None,
        cell_width: Optional[int] = 0,
    ) -> str:
        """Returns an informative string representation of the matrix.

        The row_labels, col_labels parameters, if supplied, must match the dimensions of
        the matrix. cell_width is used to right-pad the cells for alignment purposes and
        ideally is the width of the widest string representation to be expected for any
        cell in the matrix.

        Args:
            row_labels: An optional sequence of an equal length to the matrix's rows to
                be used as row labels.
            col_labels: An optional sequence of an equal length to the matrix's columns to
                be used as column labels.
            cell_width: Optional cell width to be used for vertical alignment of columns.
        """
        buf = ""
        for r in range(0, self.n_rows):
            if r == 0 and col_labels is not None:
                if row_labels is not None:
                    buf += "".ljust(cell_width) + " "  # Empty cell
                buf += "  "  # Cover distance of "[ "
                if col_labels is not None:
                    for label in col_labels:
                        buf += str(label).ljust(cell_width)
                        buf += "  "  # Add space in lieu for ", "
                    buf += "\n"
            if r != 0:
                buf += "]\n"
            for c in range(0, self.n_cols):
                if c == 0:
                    if row_labels is not None:
                        if r < len(row_labels):
                            buf += str(row_labels[r]).ljust(cell_width)
                        else:
                            buf += " " * cell_width
                        buf += " "
                    buf += "[ "
                buf += ", " if c > 0 else ""
                buf += str(self[r, c]).ljust(cell_width)
        buf += "]"
        return buf

    def __str__(self) -> str:
        """Returns a human-readable string representation of the matrix."""
        return self.stringify(
            row_labels=self.row_labels,
            col_labels=self.col_labels,
            cell_width=self.cell_width,
        )

    def __repr__(self) -> str:  # noqa: C901
        """Returns a parseable representation of the matrix."""
        buf = "Matrix(["
        for r in range(0, self.n_rows):
            if r > 0:
                buf += "], ["
            else:
                buf += "["
            for c in range(0, self.n_cols):
                if c > 0:
                    buf += ", "
                buf += repr(self[r, c])
        buf += "]]"
        if self.default_value is not None:
            buf += f", default_value={self.default_value!r}"
        if self.row_labels is not None:
            buf += f", row_labels={self.row_labels!r}"
        if self.col_labels is not None:
            buf += f", col_labels={self.col_labels!r}"
        if self.cell_width != 0:
            buf += f", cell_width={self.cell_width!r}"
        return buf + ")"

    def __eq__(self, other: Any) -> bool:  # noqa: C901
        """Compares itself to another Matrix or sequence of sequences.

        Compares two matrixes (or a matrix and a sequence of sequence of identical
        dimensions) cell by cell, and returns True if all the cells are equal.

        Note:
            The comparison ignores everything except the actual cell values. Therefore,
            two matrices will compare equal if their cells have the same content even
            if, for example, their default value or labels are different.

        Args:
            other: Another Segment, or a tuple or list of length 2.

        Returns:
            True if all the cell values between the two objects compare equal,
            False otherwise.
        """
        if isinstance(other, type(self)) and self.n_dim == other.n_dim:
            for ptr, _ in self.enumerator():
                if self[ptr] != other[ptr]:
                    return False
            return True

        if isinstance(other, Sequence) and len(other) == self.n_rows:
            for r in range(0, self.n_rows):
                if self.rows[r] != list(other[r]):
                    return False
                return True

        return NotImplemented

    def mutate(self, function: callable) -> None:
        """Applies 'function' to every cell in the matrix (in situ mapping).

        Args:
            function: A callable to be applied to each cell in the matrix.
        """
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                self[r, c] = function(self[r, c])

    def map(self, function: callable) -> Matrix:  # noqa: A003
        """Returns a copy of the matrix with 'function' applied to every cell.

        Args:
            function: A callable to be applied to each cell in the copied matrix.

        Returns:
            A shallow copy of itself with `function` applied to every cell of the new copy
            of the matrix.
        """
        m = Matrix(
            self.n_rows,
            self.n_cols,
            self.default_value,
            self.row_labels,
            self.col_labels,
            self.cell_width,
        )
        for r in range(0, self.n_rows):
            for c in range(0, self.n_cols):
                m[r, c] = function(self[r, c])
        return m

    def __iter__(self) -> MatrixIterator:
        """Returns an iterator for the Natrix object."""
        return MatrixIterator(self)

    def enumerator(self) -> MatrixIterator:
        """Returns an enumerator for the Matrix object.

        As opposed to iterating through the Matrix object itself, iterating through
        Matrix.enumerate() returns not just the value of each cell, but rather a tuple
        containing a pointer to the current cell and the value of the cell.

        Example::

            m = Matrix(2, 2, default_value=1, cell_width=2)
            m.setrow(0, [1, 2])
            m.setrow(1, [3, 4])
            for ptr, val in m.enumerator():
                m[ptr] = val**2
            print(m)

        Output::

            [ 1 , 4  ]
            [ 9 , 16 ]

        Returns:
            A MatrixIterator object where next() returns a tuple of the MatrixPointer and
            the value of the current cell.
        """
        return MatrixIterator(self, enumeration=True)


class MatrixPointer:
    """Pointers pointing at a specific cell in a `Matrix`.

    This class provides a convenient way of keeping track of pointers to specific cells in
    a `Matrix` object, guarding against exceeding the associated matrix's row and column
    range and providing a number of convenince functions to traverse the matrix.
    """

    __r: int
    __c: int
    __m: Matrix

    def __init__(self, m: Matrix, r: int = 0, c: int = 0):
        """Creates a new `MatrixPointer` associated with the `Matrix` `m`.

        Args:
            m: The `Matrix` to which the `MatrixPointer` shall be affiliated.
            r: An optional row index the pointer should point to upon initialisation
                (default = 0).
            c: An optional column index the pointer should pont to upon initialisation
                (default = 0).

        Raises:
            TypeError: Raised if the argument `m` is not a `Matrix`.
            ValueError: Raised if `r` or `c` are out of the range of the matrix's
                dimensions.
        """
        if not isinstance(m, Matrix):
            raise TypeError(f"Argument 'm' must be of type 'Matrix', {type(m)} given.")
        self.__m = m
        self.r = r
        self.c = c

    def advance(self) -> bool:
        """Advances pointer to the next cell in the matrix.

        Advances the pointer to the next column of the current row in the matrix. Skips
        to next row if end of columns is reached.

        Returns:
            True if pointer has been advanced, False otherwise. A return value of False
            means the last cell of the matrix has been reached, meaning the return value
            of `advance` can be used to loop over a matrix in a while loop.
        """
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
        """The `Matrix` object the pointer is affiliated with (read-only)."""
        return self.__m

    @property
    def r(self) -> int:
        """The row index in the affiliated matrix which the pointer is pointing to.

        Raises:
            ValueError: Raised if attempting to assign a value which is out of range
                of the affiliated matrix's dimensions.
        """
        return self.__r

    @r.setter
    def r(self, r: int):
        if r >= self.m.n_rows:
            raise ValueError(
                (
                    f"Attempt to assign value out of range of matrix dimensions: "
                    f"(r = {r}) >= {self.m.n_rows}"
                )
            )
        self.__r = int(r)

    @property
    def c(self) -> int:
        """The column index in the affiliated matrix which the pointer is pointing to.

        Raises:
            ValueError: Raised if attempting to assign a value which is out of range
                of the affiliated matrix's dimensions.
        """
        return self.__c

    @c.setter
    def c(self, c: int):
        if c >= self.m.n_cols:
            raise ValueError(
                (
                    f"Attempt to assign value out of range of matrix dimensions: "
                    f"(c = {c}) >= {self.m.n_cols}"
                )
            )
        self.__c = int(c)

    def __getitem__(self, key: int) -> int:
        """Provides list access to the matrix coordinates that pointer is pointing to.

        References or assignments to `ptr[0]` are equivalent to `ptr.r`, and those to
        `ptr[1]` are equivalent to `ptr.c`.

        Args:
            key: An integer ranging from 0 to 1.

        Raises:
            TypeError: Raised if the provided key is not an integer.
            IndexError: Raised if the provided index is not in range [0, 1]
        """
        if not isinstance(key, int):
            raise TypeError("Index on MatrixPointer is only defined for integers.")
        if key == 0:
            return self.r
        if key == 1:
            return self.c
        raise IndexError("Index for MatrixPointer must be in range [0, 1].")

    def __setitem__(self, key: int, value: int):
        """Sets item at provided coordinates to `value`."""
        if not isinstance(key, int):
            raise TypeError("Index on MatrixPointer is only defined for integers.")
        if not isinstance(value, int):
            raise ValueError(
                "MatrixPointer coordinates can only be assigned integer values."
            )
        if key == 0:
            self.r = value
            return
        if key == 1:
            self.c = value
            return
        raise IndexError("Index for MatrixPointer must be in range [0, 1]")

    def __repr__(self) -> str:
        """Provides parseable representation of the MatrixPointer's coordinates.

        Note:
            Note that evaluating this representation will *not* recreate the
            MatrixPointer, since MatrixPointers are always tied to another Matrix object.
            Instead, repr() will return a tuple with the coordinates pointed to which
            can then be used to reconstruct a MatrixPointer manually.

        Returns:
            A parseable string representation of a tuple of the form `(row, col)`.
        """
        return f"({self.r}, {self.c})"

    def __str__(self) -> str:
        """Provides a human-readable string representation of the MatrixPointer.

        Returns:
            A string showing the coordinates pointed to by the MatrixPointer.
        """
        return f"({self.r}, {self.c})"

    def __eq__(
        self, other: Union[MatrixPointer, tuple[int, int], list[int, int]]
    ) -> bool:
        """Compares two `MatrixPointer` object's coordinates.

        Note that comparing two `MatrixPointer` objects does not compare them for
        identity, but rather two `MatrixPointers` are assumed to be equal iff they point
        to the same coordinates, irrespective of whether they point to the same `Matrix`
        object or now.

        `MatrixPointer` objects can also be compared to lists or tupels of length 2, where
        the first element will be treated as the row index and the second element as
        the column index.

        Returns:
            True if the objects compared both point to the same coordinates, False
            otherwise.
        """
        if isinstance(other, MatrixPointer):
            other = (other.r, other.c)
        elif isinstance(other, list):
            other = tuple(other)
        if isinstance(other, tuple):
            if len(other) != 2:
                return NotImplemented
            return bool((self.r, self.c) == other)
        return NotImplemented

    def __hash__(self) -> int:
        """Provides a hash based on the corrdinates pointed to by the pointer.

        Note:
            Note that the hash does not take into account the affiliated `Matrix` object,
            so the hashes of two `MatrixPointer` objects pointing to the same coordinates
            but in different `Matrix` objects will be identical.

        Returns:
            A numeric hash encoding the coordinates pointer is pointing to.
        """
        return hash((self.r, self.c))

    def __len__(self) -> int:
        """Returns the length of the `MatrixPointer` (always 2).

        Returns:
            Returns the integer `2`, since `MatrixPointer` objects have a fixed
            length of two.
        """
        return 2

    def copy(self) -> MatrixPointer:
        """Returns a shallow copy of itself.

        Returns:
            A new `MatrixPointer` pointing to the same coordinates and affiliated with
            the same `Matrix` object.
        """
        return MatrixPointer(self.m, self.r, self.c)

    def __copy__(self) -> MatrixPointer:
        """Returns a shallow copy of itself.

        Returns:
            A new `MatrixPointer` pointing to the same coordinates and affiliated with
            the same `Matrix` object.
        """
        return self.copy()

    def mleft(self) -> bool:
        """Moves pointer one cell to the left in the affiliated `Matrix`.

        Returns:
            True on success, False if it is not possible to move further leftward.
        """
        try:
            self.c -= 1
            return True
        except ValueError:
            return False

    def mright(self):
        """Moves pointer on cell to the right in the affiliated `Matrix`.

        Returns:
            True on success, False if it is not possible to move further rightward.
        """
        try:
            self.c += 1
            return True
        except ValueError:
            return False

    def mup(self):
        """Moves pointer one cell up in the affiliated `Matrix`.

        Returns:
            True on success, False if it is not possible to move further uptward.
        """
        try:
            self.r -= 1
            return True
        except ValueError:
            return False

    def mupleft(self):
        """Moves pointer one cell up and left in the affiliated `Matrix`.

        Returns:
            True on success, False if it is not possible to move further up and leftward.
        """
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
        """Moves pointer one cell up and right in the affiliated `Matrix`.

        Returns:
            True on success, False if it is not possible to move further up and rightward.
        """
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
        """Moves pointer one cell down in the affiliated `Matrix`.

        Returns:
            True on success, False if it is not possible to move further downward.
        """
        try:
            self.r += 1
            return True
        except ValueError:
            return False

    def mdownleft(self):
        """Moves pointer one cell down and left in the affiliated `Matrix`.

        Returns:
            True on success, False if it is not possible to move further down
            and leftward.
        """
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
        """Moves pointer one cell down and right in the affiliated `Matrix`.

        Returns:
            True on success, False if it is not possible to move further down
            and rightward.
        """
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
        """Returns a copy of itself with pointer moved one cell left.

        Returns:
            MatrixPointer on success, False if it is not possible to move leftward.
        """
        c = self.copy()
        if c.mleft():
            return c
        return False

    def cright(self) -> Union[MatrixPointer, bool]:
        """Returns a copy of itself with pointer moved one cell right.

        Returns:
            MatrixPointer on success, False if it is not possible to move rightward.
        """
        c = self.copy()
        if c.mright():
            return c
        return False

    def cup(self) -> Union[MatrixPointer, bool]:
        """Returns a copy of itself with pointer moved one cell up.

        Returns:
            MatrixPointer on success, False if it is not possible to move upward.
        """
        c = self.copy()
        if c.mup():
            return c
        return False

    def cupleft(self) -> Union[MatrixPointer, bool]:
        """Returns a copy of itself with pointer moved one cell up and left.

        Returns:
            MatrixPointer on success, False if it is not possible to move up and leftward.
        """
        c = self.copy()
        if c.mupleft():
            return c
        return False

    def cupright(self) -> Union[MatrixPointer, bool]:
        """Returns a copy of itself with pointer moved one cell up and right.

        Returns:
            MatrixPointer on success, False if it is not possible to move up
            and rightward.
        """
        c = self.copy()
        if c.mupright():
            return c
        return False

    def cdown(self) -> Union[MatrixPointer, bool]:
        """Returns a copy of itself with pointer moved one cell down.

        Returns:
            MatrixPointer on success, False if it is not possible to move downward.
        """
        c = self.copy()
        if c.mdown():
            return c
        return False

    def cdownleft(self) -> Union[MatrixPointer, bool]:
        """Returns a copy of itself with pointer moved one cell down and left.

        Returns:
            MatrixPointer on success, False if it is not possible to move down
            and leftward.
        """
        c = self.copy()
        if c.mdownleft():
            return c
        return False

    def cdownright(self) -> Union[MatrixPointer, bool]:
        """Returns a copy of itself with pointer moved one cell down and right.

        Returns:
            MatrixPointer on success, False if it is not possible to move down
            and rightward.
        """
        c = self.copy()
        if c.mdownright():
            return c
        return False

    def directionto(self, other: MatrixPointer) -> Direction:
        """Gets the direction in which another `MatrixPointer` points relative to itself.

        Compares the coordinates of itself with the coordinates of `other` to determine
        in which direction in the matrix the other pointer points relative to itself.
        Note that for non-adjacent cells the granularity of the returned direction may be
        below what is desired, for instance given a 3x3 matrix and a comparing a pointer
        from (2, 2) to (0, 0) we will get Direction.NORTHWEST as expected, however we will
        also get Direction.NORTHWEST comparing a pointer from (2, 2) to a pointer at
        (1, 0) or (0, 1).

        Returns:
            The direction from this pointer to the other pointer as a `Direction` flag.
        """
        direction = Direction.NONE
        if other.c < self.c:
            direction |= Direction.WEST
        elif other.c > self.c:
            direction |= Direction.EAST
        if other.r < self.r:
            direction |= Direction.NORTH
        elif other.r > self.r:
            direction |= Direction.SOUTH
        return direction

    def directionfrom(self, other: MatrixPointer) -> Direction:
        """Gets the direction from another `MatrixPointer` toward itself.

        A conviencence method providing the inverse of `directionto`, i.e.
        `self.directionfrom(other)` is equivalent to `other.directionto(self)`.

        Returns:
            The direction from this pointer to the other pointer as a `Direction` flag.

        """
        return other.directionto(self)


class MatrixIterator:
    """Iterator for Matrix objects."""

    matrix: Matrix
    ptr: MatrixPointer
    enumeration: bool
    end: bool

    def __init__(self, m: Matrix, enumeration: bool = False):
        """Initialises a new MatrixIterator on the Matrix `m`.

        The iterator walks through the matrix row by row, walking through each row column
        by column (i.e. a 2x2 matrix is walked through as (0,0) -> (0,1) -> (1,0) ->
        (1,1). Calling next() on a MatrixIterator normally returns the value of the cell,
        unless the MatrixIterator was instantiated with `enumeration=True`, in which case
        it will return a tuple with a pointer to the current cell as the first element,
        and its value as the second element.

        Args:
            m: A Matrix object.
            enumeration: Whether to return pointers to each cell.
        """
        self.matrix = m
        self.ptr = MatrixPointer(m)
        self.enumeration = enumeration
        self.end = False

    def __iter__(self) -> MatrixIterator:
        """Returns itself."""
        return self

    def __next__(self) -> Any:
        """Returns the next item of the Matrix."""
        if self.end:
            raise StopIteration
        value = self.matrix[self.ptr]
        ptr = self.ptr.copy()
        if not self.ptr.advance():
            self.end = True
        if self.enumeration:
            return (ptr, value)
        else:
            return value
