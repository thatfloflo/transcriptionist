from enum import Flag, auto

class EditOperation(Flag):
    """Flaggable enumeration of string edit operations."""
    NONE = 0
    INSERT = auto()
    DELETE = auto()
    SUBSTITUTE = auto()
    TRANSPOSE = auto()

    def code(self) -> str:
        """Returns a string representation of the edit operation assigning a single character to each operation."""
        buf = ''
        for name, member in EditOperation.__members__.items():
            if self & member:
                buf += name[0]
        return buf

class Direction(Flag):
    """Flaggable enumeration of directions, eg. to move in a matrix."""
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
        """Returns a symbolic representation in the form of a pointing arrow."""
        if self == Direction.NORTHEAST:
            return '↗'
        if self == Direction.SOUTHEAST:
            return '↘'
        if self == Direction.SOUTHWEST:
            return '↙'
        if self == Direction.NORTHWEST:
            return '↖'
        if self == Direction.NORTH:
            return '↑'
        if self == Direction.EAST:
            return '→'
        if self == Direction.SOUTH:
            return '↓'
        if self == Direction.WEST:
            return '←'
        if self == Direction.NONE:
            return '○'
