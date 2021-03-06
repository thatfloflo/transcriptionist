"""Module containing a number of useful constants/enums for the transcriptionist package.

This submodule provides a number of enums used by other submodules in the transcriptionist
package.
"""
from enum import Flag, auto


class EditOperation(Flag):
    """Flaggable enumeration of string edit operations.

    Attributes:
        NONE: Indicates that no edit operation has taken place.
        INSERT: Indicates that an insert operation has taken place.
        DELETE: Indicates that a delete operation has taken place.
        SUBSTITUTE: Indicates that a substitute operation has taken place.
        TRANSPOSE: Indicates that a transpose operation has taken place.
    """

    NONE = 0
    INSERT = auto()
    DELETE = auto()
    SUBSTITUTE = auto()
    TRANSPOSE = auto()

    def code(self) -> str:
        """Returns a single character string representation of the flag.

        Returns:
            A single character string representation of the flag.
        """
        buf = ""
        for name, member in EditOperation.__members__.items():
            if self & member:
                buf += name[0]
        return buf


class Direction(Flag):
    """Flaggable enumeration of directions, e.g. to move in a matrix.

    Flags can be combined to create composite directions, and some of the flags provided
    themselves are composites. This means specific directions can be tested for with
    equality checks, and compound directions can be checked for with bit operations.

    Example:
        >>> dir = Direction.NORTHWEST
        >>> dir == Direction.NORTHWEST
        True
        >>> dir == Direction.NORTH
        False
        >>> bool(dir & Direction.NORTHWEST)
        True
        >>> bool(dir & Direction.NORTH)
        True
        >>> bool(dir & Direction.SOUTH)
        False

    Attributes:
        NONE: Indicates the absence of any direction.
        NORTH: Indicates a move northward/upward.
        EAST: Indicates a move eastward/rightward.
        SOUTH: Indicates a move southward/downward.
        WEST: Indicates a move westward/leftward.
        NORTHEAST: Compound direction indicating a move notheastward, identical to
            `Direction.NORTH | Direction.EAST`.
        SOUTHEAST: Compound direction indicating a move southeastward, identical to
            `Direction.SOUTH | Direction.EAST`.
        SOUTHWEST: Compound direction indicating a move southwestward, identical to
            `Direction.SOUTH | Direction.WEST`.
        NORTHWEST: Compound direction indicating a move southwestward, identical to
            `Direction.NORTH | Direction.WEST`.
    """

    NONE = 0
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
    NORTHEAST = NORTH | EAST
    SOUTHEAST = SOUTH | EAST
    SOUTHWEST = SOUTH | WEST
    NORTHWEST = NORTH | WEST

    def symbol(self) -> str:
        """Returns a symbolic representation of the flag.

        Returns a unicode pointing arrow glyph pointing in the direction indicated by
        the flag, or a small hollow bullet glyph in the case no direction is indicated.

        Note:
            Glyph representations are only provided for the predefined flags,
            and not for other potential compound directions such as
            `Direction.NORTH | Direction.SOUTH`.

        Returns:
            A signle character string representation of the flag.
        """
        mapping = {
            Direction.NORTHEAST: "???",
            Direction.SOUTHEAST: "???",
            Direction.SOUTHWEST: "???",
            Direction.NORTHWEST: "???",
            Direction.NORTH: "???",
            Direction.EAST: "???",
            Direction.SOUTH: "???",
            Direction.WEST: "???",
            Direction.NONE: "???",
        }
        if self in mapping:
            return mapping[self]
        else:
            return None
