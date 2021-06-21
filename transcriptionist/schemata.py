"""Multipliable scored sequence schemas.

This submodule provides a mechanism for defining scored schemas of sequences
(e.g. strings) which can be multiplied out such that a set of candidate sequences
is derived, each which has a score based on the compound of the schema's components it
was derived from.
"""
from __future__ import annotations
from typing import Any, Sequence, Union
from .matrices import Matrix


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


class TargetSchema:
    """Implementation of Target Schemas."""

    __matrix: Matrix

    def __init__(self, length: int = 1, n_forms: int = 1):
        """Initialises a new Target Schema.

        Raises:
            ValueError: Raised if a length or number of forms below 1 is specified.
        """
        if length < 1 or n_forms < 1:
            raise ValueError("Length and forms must be integers greater than 0.")
        self.__matrix = Matrix(n_forms, length)

    @classmethod
    def from_matrix(cls, matrix: Matrix) -> TargetSchema:
        """Instantiates a new TargetSchema from a matrix.

        Args:
            matrix: A Matrix representing a TargetSchema.

        Returns:
            A new TargetSchema instance.
        """
        ts = cls(matrix.n_cols, matrix.n_cols)
        ts.__matrix = matrix.copy()
        return ts

    @property
    def length(self):
        """The length of the Schema's forms."""
        return self.__matrix.n_cols

    def __len__(self):
        """Returns the length of the Schema's forms."""
        return self.length

    @property
    def n_forms(self):
        """The number of forms (base + alternants) in the Schema."""
        return self.__matrix.n_rows

    @property
    def n_alternants(self):
        """The number of alternant forms in the Schema."""
        return self.n_forms - 1

    @property
    def base(self) -> Sequence:
        """The base form of the Schema."""
        return self.__matrix.getrow(0)

    @property
    def alternants(self) -> Sequence:
        """List containing the alternant forms of the Schema (read-only)."""
        return self.__matrix.rows[1:]

    def set_alternant(self, index: int, form: list) -> None:
        """Set the alternant form at a specified index."""
        self.__matrix.setrow(index + 1, form)

    @base.setter
    def base(self, value: Sequence) -> None:
        """Sets the base form of the Schema."""
        if len(value) != self.length:
            raise ValueError("The supplied sequence must match the Schema's length.")
        self.__matrix.setrow(0, value)

    def __str__(self):
        """Returns a human-readable string representation of a Schema."""
        return str(self.__matrix)
