"""Multipliable scored sequence schemas.

This submodule provides a mechanism for defining scored schemas of sequences
(e.g. strings) which can be multiplied out such that a set of candidate sequences
is derived, each which has a score based on the compound of the schema's components it
was derived from.
"""
from __future__ import annotations
from typing import Any, Union
from multimethod import multimethod
from .matrices import Matrix, MatrixPointer


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

    def __init__(self, length: int = 1, n_forms: int = 1):
        """Initialises a new Target Schema.

        Raises:
            ValueError: Raised if a length or number of forms below 1 is specified.
        """
        if length < 1 or n_forms < 1:
            raise ValueError("Length and forms must be integers greater than 0.")
        super().__init__(n_forms, length)

    @classmethod
    def from_matrix(cls, matrix: Matrix) -> TargetSchema:
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
        ts = cls(matrix.n_cols, matrix.n_cols)
        for ptr, val in matrix.enumerator():
            ts[ptr] = val
        return ts

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
