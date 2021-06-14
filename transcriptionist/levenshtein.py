"""Module for calculation of the Levenshtein edit distance of two sequences.

This module provides an object-oriented implementation of the Wagner-Fischer algorithm
to compute the Levenshtein distance between two Sequence objects (e.g. strings). The
object representation allows for stepwise computation and inspection of the distance
matrix, and the specific implementation allows the assignment of custom costs for the
three operations permitted by Levenshtein distance: insertion, deletion, and substitution.
A shortcut function `levdist` is provided to directly get the levenshtein distance
between two sequences without having to construct and compute a `Levenshtein` object first.

Example:
    ld = Levenshtein("ABC", "ABxC")
    ld.compute()
    print(f"The Levenshtein distance between 'ABC' and 'ABxC' is: {ld.distance}.")
    print("The shortest edit sequence between the two strings is as follows:")
    print(ld.visualise())
"""
from __future__ import annotations
from typing import Union, Sequence, Optional
from .matrices import Matrix, MatrixPointer
from .constants import Direction, EditOperation as EdOp

Numeric = Union[int, float]
"""Generic type hint accepting either `int` or `float`."""

class Levenshtein:
    """An object-oriented implementation of the Wagner-Fischer algorithm for the
    Levenshtein distance.

    Attributes:
        insert_cost: The cost of insert operations on the sequence.
        delete_cost: The cost of delete operations on the sequence.
        substitute_cost: The cost of substitute operations on the sequence.
        computed: Boolean indicating whether the distance matrix has been fully computed
            or not. This is set to True automatically by `step` and `compute` if they
            reach the last cell of the matrix, but can also be (re)set manually.
    """
    __source: Sequence
    __target: Sequence
    insert_cost: Numeric
    delete_cost: Numeric
    subsitute_cost: Numeric
    computed: bool = False
    __dmatrix: Matrix      # Distance matrix
    __pmatrix: Matrix      # Pointer matrix (edit path)
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
        """Creates a new Levenshtein object for calculating levenshtein distance.

        Args:
            source: The source sequence that is being edited to fit a target.
            target: The target sequence that source is edited to match.
            insert_cost: The cost of insert operations on the sequence.
            delete_cost: The cost of delete operations on the sequence.
            subsitute_cost: The cost of substitute operations on the sequence.
        """
        self.__source = source
        self.__target = target
        self.insert_cost = insert_cost
        self.delete_cost = delete_cost
        self.substitute_cost = substitute_cost
        self.__dmatrix = self.initialise_matrix()
        self.__pmatrix = self.initialise_matrix()
        self.__ematrix = self.initialise_matrix()
        self.__ptr = MatrixPointer(self.dmatrix)

    def initialise_matrix(self) -> Matrix:
        """Initialises an empty `Matrix` with correct dimensions and labels based on the
        `source` and `target` sequences.
        """
        return Matrix(
            len(self.source) + 1,
            len(self.target) + 1,
            default_value = 0,
            row_labels = [''] + list(self.source),
            col_labels = [''] + list(self.target),
            cell_width = 1
        )

    def advance(self) -> bool:
        """Advances the internal matrix pointer to next cell.

        This method can be called if stepping through the matrix to calculate
        the values of each cell manually. It should be noted that if the method is called
        without carrying out the required operations on the current cell (e.g. by calling
        the `calculate` method) then the current cell will be left as initialised which
        may result in unwanted behaviour.

        Returns:
            True if the matrix pointer has been advanced to the next cell successfully,
            False otherwise. Under normal circumstances False as a return value will
            indicate that the last cell in the matrix has been reached.
        """
        return self.ptr.advance()

    def matrix_assign(self, dvalue: Numeric, pvalue: MatrixPointer, evalue: EdOp) -> None:
        """Makes parallel assignment at current position in distance, pointer, and edit matrices.

        Args:
            dvalue: The numeric value to be assigned to the current cell in the distance
                matrix (i.e. the `dmatrix`).
            pvalue: A `MatrixPointer` to the cell of origin to be assigned to the current
                cell in the pointer matrix (i.e. the `pmatrix`).
            evalue: An `EditOperation` to be assigned to the current cell in the edit
                matrix (i.e. the `ematrix`).
        """
        self.dmatrix[self.ptr] = dvalue
        self.pmatrix[self.ptr] = pvalue
        self.ematrix[self.ptr] = evalue

    def calculate(self) -> None:
        """Calculates the Levenshtein distance for the current cell.

        This method will apply the Wagner-Fischer algorithm to calculate the Levenshtein
        distance for the current cell, using `insert_cost`, `delete_cost`, and
        `substitute_cost` to calculate the cheapest path to the current cell. It will then
        assign the calculated cost to the distance martrix (`dmatrix`), the operation that
        has been applied to the edit matrix (`ematrix`), and a `MatrixPointer` pointing to
        the cell of origin to the pointer matrix (`pmatrix`), so that inspection of the
        current cell in these matrices after `calculate` can be used to reconstruct the
        steps that have taken place.

        Raises:
            ValueError: The distance for the current cell could not be computed for some
                reason. This is always unexpected and if it occurs likely due to a bug in
                the implementation which should be reported as an issue.
        """
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
        raise ValueError(("It seems you've found a bug in the calculation algorithm. "
                          "The calculation algorithm should never get to this point..."))

    def step(self) -> bool:
        """Calculates the current cell and moves the pointer to next cell.

        This is essentially equivalent to calling `calculate` followed by `advance`,
        however, it will also set the `computed` flag to True if no further steps are
        necessary to fill the matrix.

        Returns:
            True if there are further calculation steps until the calculation of the full
            Levenshtein distance is complete, False once computation is completed. This
            allows iteration of `step` in a while loop, for example:

            while ld.step():
                print(f"Cell {ld.ptr} has been assigned the value {ld.dmatrix[ld.ptr]}.")
        """
        self.calculate()
        if not self.advance():
            self.computed = True
            return False
        return True

    def compute(self) -> None:
        """Computes the remainder of the matrix from the current pointer position up to
        and including the last cell in the matrix."""
        while self.step():
            pass
        self.computed = True

    @property
    def ptr(self) -> MatrixPointer:
        """A `MatrixPointer` pointing to the current cell in `dmatrix`. This is also
        used to refer to the position in `pmatrix` and `ematrix`.

        While the `ptr` property is read-only (i.e. you cannot assign a different
        `MatrixPointer` object to it), the pointer position can be manipulated via the
        methods of the `MatrixPointer` object itself if that is desired."""
        return self.__ptr

    @property
    def source(self) -> Sequence:
        """The source sequence that is being edited to fit a target (read-only)."""
        return self.__source

    @property
    def source_len(self) -> int:
        """The length of the source sequence (read-only)."""
        return len(self.source)

    @property
    def target(self) -> Sequence:
        """The target sequence that source is edited to match (read-only)."""
        return self.__target

    @property
    def target_len(self) -> int:
        """The length of the target sequence (read-only)."""
        return len(self.target)

    @property
    def dmatrix(self) -> Matrix:
        """The distance matrix containing the edit cost of the subproblems in each cell
        according to the Wagner-Fischer algorithm.

        While the `dmatrix` property is read-only (i.e. you cannot assign a different
        `Matrix` object to it), the matrix itself can be manipulated via the normal
        methods available for `Matrix` objects if this is desired.

        Note:
            If the distance matrix is manipulated manually, the user is responsible for
            ensuring that it continues to fit the dimensions of the `source` and `target`
            sequences and that the properties of `dmatrix`, `pmatrix`, and `ematrix`
            remain identical. If the three matrices are resized to different dimensions
            the behaviour of other operations on them may become unpredictable.
        """
        return self.__dmatrix

    @property
    def pmatrix(self) -> Matrix:
        """The pointer matrix containing `MatrixPointer`s pointing to the cell of origin
        based on which a cell's edit cost was calculated according to the Wagner-Fischer
        algorithm.

        While the `dmatrix` property is read-only (i.e. you cannot assign a different
        `Matrix` object to it), the matrix itself can be manipulated via the normal
        methods available for `Matrix` objects if this is desired.

        Note:
            If the distance matrix is manipulated manually, the user is responsible for
            ensuring that it continues to fit the dimensions of the `source` and `target`
            sequences and that the properties of `dmatrix`, `pmatrix`, and `ematrix`
            remain identical. If the three matrices are resized to different dimensions
            the behaviour of other operations on them may become unpredictable.
        """
        return self.__pmatrix

    @property
    def ematrix(self) -> Matrix:
        """The distance matrix containing the edit cost of the subproblems in each cell
        according to the Wagner-Fischer algorithm. While the `dmatrix` property is
        read-only (i.e. you cannot assign a different `Matrix` object to it), the matrix
        itself can be manipulated via the normal methods available for `Matrix` objects
        if this is desired.

        Note:
            If the distance matrix is manipulated manually, the user is responsible for
            ensuring that it continues to fit the dimensions of the `source` and `target`
            sequences and that the properties of `dmatrix`, `pmatrix`, and `ematrix`
            remain identical. If the three matrices are resized to different dimensions
            the behaviour of other operations on them may become unpredictable.
        """
        return self.__ematrix

    @property
    def distance(self) -> Optional[Numeric]:
        """The numeric Levenshtein distance between `source` and `target`. None if the
        full distance has not been computed yet as indicated by `computed`."""
        if self.computed:
            return self.dmatrix[self.dmatrix.n_rows - 1, self.dmatrix.n_cols - 1]
        return None

    @property
    def esequence(self) -> Optional[list[EdOp]]:
        """The sequence of edits to get from `source` to `target` in the form of a list of
        `EditOperation` flags. None if the full edit sequence has not been computed yet
        as indicated by `computed`.

        Todo:
            * Implement checks in loop to handle (1) incomplete paths (e.g. `computed` has
              been wrongly set to True), (2) broken paths where a default value (not a
              MatrixPointer) is encountered.
            * Perhaps implement some check or fallback to detect/handle a pointer loop?
        """
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
        """The sequence of individual operation costs to get from `source` to `target` in
        the form of a list of numeric values. Aligns with `esequence`. None if the full
        edit sequence has not been computed yet as indicated by `computed`.

        Todo:
            * Implement checks in loop to handle (1) incomplete paths (e.g. `computed` has
              been wrongly set to True), (2) broken paths where a default value (not a
              MatrixPointer) is encountered.
            * Perhaps implement some check or fallback to detect/handle a pointer loop?
        """
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
        """The sequence of pointers to the prior sub-prefix of edit operations to get from
        `source` to `target` in the form of a list of `MatrixPointer` objects. Aligns with
        `esequence`. None if the full edit sequence has not been computed yet as indicated
        by `computed`.

        Todo:
            * Implement checks in loop to handle (1) incomplete paths (e.g. `computed` has
              been wrongly set to True), (2) broken paths where a default value (not a
              MatrixPointer) is encountered.
            * Perhaps implement some check or fallback to detect/handle a pointer loop?
        """
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
        """A sequence of cardinal directions to the cell of the prior sub-prefix of edit
        operations to get from `source` to `target` in the form of a list of `Direction`
        flags. Aligns with `esequence`. None if the full edit sequence has not been
        computed yet as indicated by `computed`.

        Todo:
            * Implement checks in loop to handle (1) incomplete paths (e.g. `computed` has
              been wrongly set to True), (2) broken paths where a default value (not a
              MatrixPointer) is encountered.
            * Perhaps implement some check or fallback to detect/handle a pointer loop?
        """
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
        """A matrix of cardinal directions pointing to the cell of the prior sub-prefix
        of edit operations based on which each cell was computed. Generated dynamically
        so any manipulations of `dirmatrix` based on the methods of the `Matrix` object
        returned will not have a permanent effect (unlike manipulations of the `Matrix`
        object for `dmatrix`, `pmatrix`, and `ematrix`)."""
        dirmatrix = self.pmatrix.copy()
        dirptr = MatrixPointer(dirmatrix, 0, 0)
        dirmatrix[0, 0] = Direction.NONE # By definition
        while dirptr.advance():
            dirmatrix[dirptr] = dirptr.directionto(dirmatrix[dirptr])
        return dirmatrix

    def visualise(self) -> str:
        """Returns a text-based visualisation of the edit distance and its derivation.

        If the matrix has not been fully computed yet, it will be computed first."""
        if not self.computed:
            self.compute()
        source = list(map(str, self.source))
        target = list(map(str, self.target))
        if len(source) == 0:
            source = ['']
        if len(target) == 0:
            target = ['']
        costs = self.esequence
        edits = list(map(EdOp.code, self.esequence))
        for i in range(0, len(costs)):
            if costs[i] == EdOp.INSERT:
                costs[i] = str(self.insert_cost)
                source.insert(i, '')
            elif costs[i] == EdOp.DELETE:
                costs[i] = str(self.delete_cost)
                target.insert(i, '')
            elif costs[i] == EdOp.SUBSTITUTE:
                costs[i] = str(self.substitute_cost)
            else: # == EdOp.NONE
                costs[i] = '0'
        width: int = 1
        for sequence in (source, target, costs): # Edits are always width 1
            for item in sequence:
                if len(item) > width:
                    width = len(item)
        width += 2 # Padding
        buf: str = ''
        length = max(
            len(source),
            len(target),
            len(costs),
            len(edits)
        )
        def row(header: str, cells: Sequence, length: int = length, width: int = width) -> str:
            return "|" + header.ljust(8) + ''.join(["|" + cells[i].center(width) for i in range(0, len(cells))]) + "|\n"
        divider = "+--------" + ''.join(["+" + "-" * width for i in range(0, length)]) + "+\n"
        buf += divider
        buf += row("Source", source)
        buf += divider
        buf += row("Target", target)
        buf += divider
        buf += row("Edits", edits)
        buf += divider
        buf += row("Costs", costs)
        buf += divider
        return buf


def levdist(
    source: Sequence,
    target: Sequence,
    insert_cost: Numeric = 1,
    delete_cost: Numeric = 1,
    substitute_cost: Numeric = 1
) -> Numeric:
    """Shortcut to build a Levenshtein object and return numeric Levenshtein distance."""
    ld = Levenshtein(source, target, insert_cost, delete_cost, substitute_cost)
    ld.compute()
    return ld.distance
