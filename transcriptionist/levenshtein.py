from __future__ import annotations
from typing import Union, Sequence, Optional
from .matrices import Matrix, MatrixPointer
from .constants import Direction, EditOperation as EdOp

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

    def matrix_assign(self, dvalue: int, pvalue: MatrixPointer, evalue: EdOp) -> None:
        """Make parallel assignment at current position in distance, pointer, and edit matrices."""
        self.dmatrix[self.ptr] = dvalue
        self.pmatrix[self.ptr] = pvalue
        self.ematrix[self.ptr] = evalue

    def calculate(self) -> None:
        """Calculate value of current cell."""
        # Special cases
        if self.ptr == (0, 0):
            self.matrix_assign(
                0,
                self.ptr.copy(),
                EdOp.NONE
            )
            return
        if self.ptr.r == 0:
            self.matrix_assign(
                self.dmatrix[self.ptr.cleft()] + self.insert_cost,
                self.ptr.cleft(),
                EdOp.INSERT
            )
            return
        if self.ptr.c == 0:
            self.matrix_assign(
                self.dmatrix[self.ptr.cup()] + self.delete_cost,
                self.ptr.cup(),
                EdOp.DELETE
            )
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
        insertion = self.dmatrix[self.ptr.cleft()] + self.insert_cost
        deletion = self.dmatrix[self.ptr.cup()] + self.delete_cost
        substitution = self.dmatrix[self.ptr.cupleft()] + substitute_cost
        if insertion < deletion and insertion < substitution:
            self.matrix_assign(
                insertion,
                self.ptr.cleft(),
                EdOp.INSERT
            )
            return
        if deletion < insertion and deletion < substitution:
            self.matrix_assign(
                deletion,
                self.ptr.cup(),
                EdOp.DELETE
            )
            return
        if substitution <= insertion and substitution <= deletion:
            self.matrix_assign(
                substitution,
                self.ptr.cupleft(),
                substitute_edop
            )
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

    @property
    def esequence(self) -> Optional[list[OpEd]]:
        if self.computed:
            end = MatrixPointer(self.dmatrix, self.dmatrix.n_rows - 1, self.dmatrix.n_cols - 1)
            start = MatrixPointer(self.dmatrix, 0, 0)
            cur = end
            edits = []
            while True:
                edits.insert(0, self.ematrix[cur])
                cur = self.pmatrix[cur]
                if cur == start:
                    break
            return edits
        return None

    @property
    def dsequence(self) -> Optional[list[Numeric]]:
        if self.computed:
            end = MatrixPointer(self.dmatrix, self.dmatrix.n_rows - 1, self.dmatrix.n_cols - 1)
            start = MatrixPointer(self.dmatrix, 0, 0)
            cur = end
            costs = []
            while True:
                costs.insert(0, self.dmatrix[cur])
                cur = self.pmatrix[cur]
                if cur == start:
                    break
            return costs
        return

    @property
    def psequence(self) -> Optional[list[MatrixPointer]]:
        if self.computed:
            end = MatrixPointer(self.dmatrix, self.dmatrix.n_rows - 1, self.dmatrix.n_cols - 1)
            start = MatrixPointer(self.dmatrix, 0, 0)
            cur = end
            pointers = []
            while True:
                pointers.insert(0, self.pmatrix[cur].copy())
                cur = self.pmatrix[cur]
                if cur == start:
                    break
            return pointers
        return None

    @property
    def dirsequence(self) -> Optional[list[Direction]]:
        if self.computed:
            end = MatrixPointer(self.dmatrix, self.dmatrix.n_rows - 1, self.dmatrix.n_cols - 1)
            start = MatrixPointer(self.dmatrix, 0, 0)
            cur = end
            pointers = []
            while True:
                pointers.insert(0, cur.directionto(self.pmatrix[cur]))
                cur = self.pmatrix[cur]
                if cur == start:
                    break
            return pointers
        return None

    @property
    def dirmatrix(self) -> Matrix:
        dirmatrix = self.pmatrix.copy()
        dirptr = MatrixPointer(dirmatrix, 0, 0)
        dirmatrix[0, 0] = Direction.NONE # By definition
        while dirptr.advance():
            dirmatrix[dirptr] = dirptr.directionto(dirmatrix[dirptr])
        return dirmatrix

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
