"""Multipliable scored sequence schemas.

This submodule provides a mechanism for defining scored schemas of sequences
(e.g. strings) which can be multiplied out such that a set of candidate sequences
is derived, each which has a score based on the compound of the schema's components it
was derived from.
"""
from typing import Sequence
from .matrices import Matrix


class Schema:
    """Implementation of Target Schemas."""

    __matrix: Matrix

    def __init__(self, length: int = 1, n_forms: int = 1):
        """Initialises a new Schema.

        Raises:
            ValueError: Raised if a length or number of forms below 1 is specified.
        """
        if length < 1 or n_forms < 1:
            raise ValueError("Length and forms must be integers greater than 0.")
        self.__matrix = Matrix(n_forms, length)

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
