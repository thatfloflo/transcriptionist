"""Multipliable scored sequence schemas.

This submodule provides a mechanism for defining scored schemas of sequences
(e.g. strings) which can be multiplied out such that a set of candidate sequences
is derived, each which has a score based on the compound of the schema's components it
was derived from.
"""
from __future__ import annotations
from typing import Any, Union, Sequence, Iterable
from multimethod import multimethod
from .matrices import Matrix, MatrixPointer
from collections import UserList


class TargetSegment:
    """Implementation of Target Segments.

    Target Segments are representations of individual segments of a Target Schema,
    consisting of the target segment itself and an associated score compounded into
    derived target sequences.
    """

    target: Any
    __score: Union[int, float]

    def __init__(self, target: Any = None, score: Union[int, float] = 0):
        """Initialises a new Target Segment.

        Args:
            target: The target segment.
            score: The numeric score associated with the target segment.

        Note:
            `TargetSegment` objects are hashable as long as the type of its `target`
            property is hashable.

        Returns:
            A new Target Segment instance.
        """
        self.target = target
        self.score = score

    @classmethod
    def from_pair(
        cls, pair: Union[list[Any, Union[int, float]], tuple[Any, Union[int, float]]]
    ) -> TargetSegment:
        """Instantiates a new Target Segment from a 2-tuple or list.

        Args:
            pair: A tuple or list of length two, where the first member is the target and
                the second member is a numeric score value.

        Returns:
            A new Target Segment instance.
        """
        target, score = list(pair)
        return cls(target, score)

    @property
    def score(self) -> Union[int, float]:
        """The score awarded for sequences including this Target Segment.

        Returns:
            The numeric score of the Target Segment.
        """
        return self.__score

    @score.setter
    def score(self, score: Union[int, float]) -> None:
        """Sets the score of the Target Segment.

        Args:
            score: A numeric value for the score of the Target Segment.
        """
        if not isinstance(score, (int, float)):
            raise TypeError(
                (
                    f"Target Segment score must be numeric (int or float), "
                    f"{type(score)} given."
                )
            )
        self.__score = score

    def __repr__(self) -> str:
        """Returns a parseable representation of a Target Segment.

        Returns:
            The parseable representation of the Segment.
        """
        return f"{type(self).__name__}({repr(self.target)}, {repr(self.score)})"

    def __str__(self) -> str:
        """Returns a human-readable representation of the Target Segment.

        Returns:
            The string representation of the Segment.
        """
        return f"({str(self.target)}, {str(self.score)})"

    def __eq__(self, other) -> bool:
        """Compares itself to another Target Segment or 2-tuple.

        Args:
            other: Another Segment, or a tuple or list of length 2.

        Returns:
            True if the other item matches the target and score of the Segment,
            False otherwise.
        """
        if isinstance(other, type(self)):
            return self.target == other.target and self.score == other.score
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return tuple(other) == (self.target, self.score)
        return NotImplemented


class TargetSchema(Matrix):
    """Implementation of Target Schemas."""

    @multimethod
    def __init__(self, length: int = 1, n_forms: int = 1):
        """Initialises a new Target Schema.

        Raises:
            ValueError: Raised if a length or number of forms below 1 is specified.
        """
        if length < 1 or n_forms < 1:
            raise ValueError("Length and forms must be integers greater than 0.")
        super().__init__(n_forms, length, default_value=TargetSegment())

    @multimethod
    def __init__(self, matrix: Matrix):  # noqa: F811
        """Instantiates a new TargetSchema from a matrix.

        Args:
            matrix: A Matrix representing a TargetSchema.

        Returns:
            A new TargetSchema instance.

        Raises:
            TypeError: Raised if the supplied argument is not a valid Matrix object.
            ValueError: Raised if the Matrix object contains cells that are not either
                TargetSegments or None.
        """
        if not isinstance(matrix, Matrix):
            raise TypeError(
                f"Supplied matrix must be an object of type Matrix, {type(matrix)} given."
            )
        super().__init__(matrix.n_rows, matrix.n_cols)
        for ptr, val in matrix.enumerator():
            self[ptr] = val

    @property
    def length(self):
        """The length of the Schema's forms (read-only)."""
        return self.n_cols

    @property
    def n_forms(self):
        """The number of forms (base + alternants) in the Schema."""
        return self.n_rows

    @property
    def n_alternants(self):
        """The number of alternant forms in the Schema."""
        return self.n_forms - 1

    def getbase(self) -> list:
        """Returns the base form of the TargetScheme."""
        return self.getform(0)

    def setbase(self, form: list[Union[TargetSegment, None]]) -> None:
        """Sets the base form to a list of TargetSegment objects."""
        self.setform(0, form)

    def getform(self, index) -> list:
        """Returns the form at the specified index."""
        return self.getrow(index)

    def setform(self, index, form: list[Union[TargetSegment, None]]) -> None:
        """Sets the form at the specified index to a list of TargetSegment objects."""
        self.setrow(index, form)

    def getalternants(self) -> list:
        """Returns a list containing the alternant forms of the TargetScheme."""
        return self.rows[1:]

    @multimethod
    def setitem(self, row: int, col: int, value: Union[TargetSegment, None]) -> None:
        """Sets the TargetSegment at the coordinates `row` and `col` to `value`.

        Sets the item stored in the underlying matrix cell indicated by the coordinates
        `row` and `col` to `value`.

        Args:
            row: Index of a row in the TargetScheme matrix.
            col: Intex of a column in the TargetScheme matrix.
            value: A TargetSegment or None.

        Raises:
            IndexError: Raised if `row` or `col` are out of the range of the matrix's
                dimensions.
            TypeError: Raised if `value` is not a TargetSegment or None.
        """
        if not isinstance(value, (TargetSegment, None)):
            raise TypeError(
                (
                    f"Supplied value must be either of type TargetSegment or None, "
                    f"{type(value)} given."
                )
            )
        super().setitem(row, col, value)

    @multimethod
    def setitem(  # noqa: F811
        self, ptr: MatrixPointer, value: Union[TargetSegment, None]
    ) -> None:
        """Sets the TargetSegment at the coordinates in `MatrixPointer` to `value`.

        Args:
            ptr: A `MatrixPointer` pointing to a cell in the matrix.
            value: A TargetSegment or None.

        Raises:
            IndexError: Raised if the coordinates of the supplied `MatrixPointer` are out
                of the range of the matrix's dimensions.
        """
        super().setitem(ptr.r, ptr.c, value)

    def setrow(self, row: int, values: list[Union[TargetSegment, None]]) -> None:
        """Sets the column values of a specified row in the matrix to a list of values.

        Args:
            row: Index of the row to be overwritten.
            values: A Sequence of an equal length to the matrix's columns containing the
                values to be assigned to each column in the specified row, each of which
                must be either a TargetSegment or None.

        Raises:
            IndexError: Raised if the specified row index is out of the range of the
                matrix's rows.
            ValueError: Raised if the length of the `values` sequence doesn't match the
                number of columns in the matrix.
            TypeError: Raised if the supplied list of values contains items that are not
                a TargetSegment or None.
        """
        for seg in values:
            if not isinstance(seg, (TargetSegment, type(None))):
                raise TypeError(
                    (
                        "Supplied values must be a list consisting only of TargetSegment "
                        "objects and None values."
                    )
                )
        try:
            super().setrow(row, values)
        except ValueError as exc:
            raise ValueError(
                "Supplied value list must have equal length as TargetScheme."
            ) from exc

    def setcol(self, col: int, values: list[Union[TargetSegment, None]]) -> None:
        """Sets the row values of a specified column in the matrix to list of values.

        Args:
            col: Index of the column to be overwritten.
            values: A Sequence of an equal length to the matrix's rows containing the
                values to be assigned to each row in the specified column.

        Raises:
            IndexError: Raised if the specified row index is out of the range of the
                matrix's columns.
            ValueError: Raised if the length of the `values` sequence doesn't match the
                number of rows in the matrix.
            TypeError: Raised if the supplied list of values contains items that are not
                a TargetSegment or None.
        """
        for seg in values:
            if not isinstance(seg, (TargetSegment, type(None))):
                raise TypeError(
                    (
                        "Supplied values must be a list consisting only of TargetSegment "
                        "objects and None values."
                    )
                )
        try:
            super().setcol(col, values)
        except ValueError as exc:
            raise ValueError(
                "Supplied value list must have equal length as TargetScheme."
            ) from exc

    def __compile(  # noqa: C901
        self, base: list, alts: list, debug: bool = False, debug_indent: int = 0
    ):
        """Internal method to recursively compile the scheme."""
        comp = set()
        if debug:
            print(" " * debug_indent, f"Base: {base}")
        comp.add(TargetSequence.from_segments(base))
        for i in range(0, len(alts)):
            if debug:
                print(" " * debug_indent, f"Alt: {alts[i]}")
            form = [TargetSegment() for _ in range(0, len(base))]
            for j in range(0, len(base)):
                if alts[i][j].target is not None:
                    form[j].target = alts[i][j].target
                    form[j].score = alts[i][j].score
                elif base[j].target is not None:
                    form[j].target = base[j].target
                    form[j].score = base[j].score
            if debug:
                print(" " * debug_indent, f"  --> {form}.")
            comp.add(TargetSequence.from_segments(form))
            new_alts = alts.copy()
            new_alts.pop(i)
            if len(new_alts) > 0:
                subcomp = self.__compile(
                    base=form, alts=new_alts, debug=debug, debug_indent=debug_indent + 2
                )
                comp.update(subcomp)
        return comp

    def compile(self, debug: bool = False) -> TargetCompilation:  # noqa: A003
        """Compiles the TargetSchema to a TargetCompilation of scored TargetSequences."""
        return TargetCompilation(
            self.__compile(self.getbase(), self.getalternants(), debug=debug)
        )


class TargetSequence:
    """Implments TargetSequence objects, which consist of a sequence and a score."""

    __sequence: tuple
    __flat: Union[str, None]
    __score: Union[int, float]

    def __init__(self, sequence: Sequence, score: Union[int, float]):
        """Initialises a new TargetSequence."""
        self.__sequence = tuple(sequence)
        self.__score = score
        self.__flat = self.flatten()

    @classmethod
    def from_segments(cls, sequence: Sequence[TargetSegment]):
        """Initialises a new TargetSequence from a list of TargetSegments."""
        clean = []
        score = 0
        for item in sequence:
            if not isinstance(item, TargetSegment):
                raise TypeError("Sequence must consist of TargetSegment objects.")
            clean.append(item.target)
            score += item.score
        return cls(clean, score)

    @property
    def sequence(self):
        """The ordered sequence of target items."""
        return self.__sequence

    @property
    def flat(self):
        """The target sequence flattened into a string; None if containing non-strings."""
        return self.__flat

    @property
    def score(self):
        """The score of the target sequence."""
        return self.__score

    def flatten(self):
        """Attempts to concatenate the individual segments if they are all strings."""
        try:
            return "".join(self.sequence)
        except TypeError:
            return None

    def __hash__(self):
        """Returns a hash based on the sequence and score."""
        return hash((self.sequence, self.score))

    def __eq__(self, other):
        """Compares itself to another TargetSequence."""
        if isinstance(other, type(self)):
            return (self.sequence, self.score) == (other.sequence, other.score)
        return NotImplemented

    def __str__(self):
        """Returns a string representation of the TargetSegment."""
        if self.flat is not None:
            return f"('{self.flat}', {self.score})"
        return f"({self.sequence!r}, {self.score})"

    def __repr__(self):
        """Returns a parseable representation of the TargetSegment."""
        return f"{type(self).__name__}({self.sequence!r}, {self.score!r})"

    def __iter__(self):
        """Returns its own sequence for iteration."""
        return iter(self.sequence)


class TargetCompilation(UserList):
    """A collection of TargetSequence objects generated from a TargetSchema."""

    def __init__(self, data: Iterable[TargetSequence] = None):
        """Initialises a new TargetCompilation."""
        super().__init__()
        if isinstance(data, Iterable):
            for x in data:
                self.append(x)

    def validate_item(self, x: Any) -> None:
        """Raises TypeError if `item` is not a TargetSequence."""
        if not isinstance(x, TargetSequence):
            raise TypeError(
                "A TargetCompilation may only contain items of type TargetSequence."
            )

    def append(self, x: TargetSequence) -> None:
        """Add an item to the end of the compilation."""
        self.validate_item(x)
        return self.data.append(x)

    def find(self, x: Union[str, Sequence, TargetSequence]):
        """Finds and returns the first instance of x, or ValueError."""
        return self.data[self.locate(x)]

    def locate(self, x: Union[str, Sequence, TargetSequence]):  # noqa: C901
        """Locates the first instance of x and returns its index, or ValueError."""
        for i in range(0, len(self.data)):
            if isinstance(x, TargetSequence):
                if self.data[i] == x:
                    return i
            elif isinstance(x, str):
                if self.data[i].flat == x:
                    return i
            elif isinstance(x, Sequence):
                if self.data[i].sequence == tuple(x):
                    return i
        raise ValueError(f"Item '{x}' was not found in the TargetCompilation.")

    def count(self, x: Union[str, Sequence, TargetSequence]):  # noqa: C901
        """Counts the number of times an item occurs in the TargetCompilation."""
        count = 0
        for sequence in self.data:
            if isinstance(x, TargetSequence):
                if sequence == x:
                    count += 1
            elif isinstance(x, str):
                if sequence.flat == x:
                    count += 1
            elif isinstance(x, Sequence):
                if sequence.sequence == tuple(x):
                    count += 1
        return count

    def __setitem__(self, i: Union[int, slice], x: TargetSequence) -> None:
        """Sets value of item at index `i`."""
        self.validate_item(x)
        self.data[i] = x

    def extend(self, iterable: Iterable) -> None:
        """Extend the TargetSequence with items from the iterable."""
        for item in iterable:
            self.validate_item(item)
        return self.data.extend(iterable)

    def insert(self, i: int, x: Any) -> None:
        """Insert an item at a given position."""
        self.validate_item(x)
        return self.data.insert(i, x)

    def __contains__(self, item: Any):  # noqa: C901
        """Checks whether the TargetCompilation contains an item."""
        if isinstance(item, TargetSequence):
            return item in self.data
        elif isinstance(item, str):
            for sequence in self.data:
                if sequence.flat == item:
                    return True
            return False
        elif isinstance(item, Sequence):
            for sequence in self.data:
                if sequence.sequence == tuple(item):
                    return True
            return False
        return NotImplemented

    def __str__(self):
        """Return a string representation of the TargetCompilation."""
        buf = ""
        last = len(self.data) - 1
        for i in range(0, len(self.data)):
            buf += f"{i}: {self.data[i]}"
            if i < last:
                buf += ",\n"
        return buf
