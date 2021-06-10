from typing import Union, Sequence, Optional
from .matrices import Matrix, MatrixPointer
from .constants import EditOperation as EdOp

Numeric = Union[int, float]

class Levenshtein:
    """An object oriented implementation of the Wagner-Fischer algorithm for the Levenshtein distance."""

    __source: Sequence
    __target: Sequence
    insert_cost: Numeric
    delete_cost: Numeric
    subsitute_cost: Numeric
    __computed: bool
    __dmatrix: Matrix      # Distance matrix
    __pmatrix: Matrix      # Pointer matrix (path)
    __ematrix: Matrix      # Edit matrix
    __ptr: MatrixPointer

    def __init__(
        self,
        source: Sequence,
        target: Sequence,
        insert_cost: Numeric = 1,
        delete_cost: Numeric = 1,
        substitute_cost: Numeric = 1
    ) -> None:
        """Creates a new Levenshtein object which can be used to calculate levenshtein distance."""
        self.source = source
        self.target = target
        self.insert_cost = insert_cost
        self.delete_cost = delete_cost
        self.substitute_cost = substitute_cost
        self.__computed = False
        self.__dmatrix = self.initialise_matrix()
        self.__pmatrix = self.initialise_matrix()
        self.__ematrix = self.initialise_matrix()
        self.__ptr = MatrixPointer(self.dmatrix)

    def initialise_matrix(self) -> Matrix:
        return Matrix(
            len(self.source) + 1,
            len(self.target) + 1,
            default_value = 0,
            row_labels = [''] + list(self.source),
            col_labels = [''] + list(self.target),
            cell_width = 1
        )

    def advance(self) -> bool:
        """Advances matrix pointer to next cell."""
        return self.ptr.advance()

    def calculate(self) -> None:
        """Calculate value of current cell."""
        # Special cases
        if self.ptr == (0, 0):
            self.dmatrix[self.ptr] = 0
            self.pmatrix[self.ptr] = self.ptr.copy()
            self.ematrix[self.ptr] = EdOp.NONE
            return
        if self.ptr.r == 0:
            self.dmatrix[self.ptr] = self.dmatrix[self.ptr.cleft()] + self.delete_cost
            self.pmatrix[self.ptr] = self.ptr.cleft()
            self.ematrix[self.ptr] = EdOp.DELETE
            return
        if self.ptr.c == 0:
            self.dmatrix[self.ptr] = self.dmatrix[self.ptr.cup()] + self.insert_cost
            self.pmatrix[self.ptr] = self.ptr.cup()
            self.ematrix[self.ptr] = EdOp.INSERT
            return
        # Get values for surrounding three cells
        vup = self.dmatrix[self.ptr.cup()]
        vleft = self.dmatrix[self.ptr.cleft()]
        vupleft = self.dmatrix[self.ptr.cupleft()]
        # Substituting like for like should be free
        if self.dmatrix.row_labels[self.ptr.r] == self.dmatrix.col_labels[self.ptr.c]:
            substitute_cost = 0
            substitute_edop = EdOp.NONE
        else:
            substitute_cost = self.substitute_cost
            substitute_edop = EdOp.SUBSTITUTE
        # Add cheapest path + operation cost to current cell
        deletion = self.dmatrix[self.ptr.cleft()] + self.delete_cost
        insertion = self.dmatrix[self.ptr.cup()] + self.insert_cost
        substitution = self.dmatrix[self.ptr.cupleft()] + substitute_cost
        if deletion < insertion and deletion < substitution:
            self.dmatrix[self.ptr] = deletion
            self.pmatrix[self.ptr] = self.ptr.cleft()
            self.ematrix[self.ptr] = EdOp.DELETE
            return
        if insertion < deletion and insertion < substitution:
            self.dmatrix[self.ptr] = insertion
            self.pmatrix[self.ptr] = self.ptr.cup()
            self.ematrix[self.ptr] = EdOp.INSERT
            return
        if substitution <= deletion and substitution <= insertion:
            self.dmatrix[self.ptr] = substitution
            self.pmatrix[self.ptr] = self.ptr.cupleft()
            self.ematrix[self.ptr] = substitute_edop
            return
        raise Exception("You've found a bug in the calculation algorithm. We should never ever have got here...")

    def step(self) -> bool:
        """Calculate current cell and move pointer to next cell."""
        self.calculate()
        if not self.advance():
            self.__computed = True
            return False
        return True

    def compute(self) -> None:
        """Compute the remainder of the matrix until the last cell."""
        while self.step():
            pass
        self.__computed = True

    @property
    def ptr(self) -> MatrixPointer:
        return self.__ptr

    @property
    def source_len(self) -> int:
        return len(self.source)

    @property
    def target_len(self) -> int:
        return len(self.target)

    @property
    def computed(self) -> bool:
        return self.__computed

    @property
    def dmatrix(self) -> Matrix:
        return self.__dmatrix

    @property
    def pmatrix(self) -> Matrix:
        return self.__pmatrix

    @property
    def ematrix(self) -> Matrix:
        return self.__ematrix

    @property
    def distance(self) -> Optional[int]:
        if self.computed:
            return self.dmatrix[self.dmatrix.n_rows - 1, self.dmatrix.n_cols - 1]
        return None


def levdist(
    source: Sequence,
    target: Sequence,
    insert_cost: Numeric = 1,
    delete_cost: Numeric = 1,
    substitute_cost: Numeric = 1
) -> Numeric:
    """Shortcut to build a Levenshtein object and return Levenshtein distance."""
    ld = Levenshtein(source, target, insert_cost, delete_cost, substitute_cost)
    ld.compute()
    return ld.distance
