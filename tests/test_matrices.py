"""Unit tests for the `matrices` submodule of the `transcriptionist` package."""
import unittest
import random
from transcriptionist.matrices import Matrix, MatrixPointer


class TestMatrices(unittest.TestCase):
    """Unit tests for the `transcriptionist.matrices.Matrix` class."""

    def test_minimum_dimensions(self):
        """Checks that we cannot construct matrices smaller than 1x1."""
        with self.assertRaises(ValueError):
            Matrix(0, 0)

    def test_dimension_attributes(self):
        """Checks that the dimension attributes reflect matrix dimensions."""
        rows = random.randint(1, 20)  # noqa: S311
        cols = random.randint(1, 20)  # noqa: S311
        m = Matrix(rows, cols)
        self.assertEqual(m.n_dim, (rows, cols))
        self.assertEqual(m.n_rows, rows)
        self.assertEqual(m.n_cols, cols)

    def test_dimension_attribute_protection(self):
        """Ensures that the dimension attributes of a matrix cannot be overwritten."""
        m = Matrix(1, 1)
        with self.assertRaises(AttributeError):
            m.n_dim = (10, 20)
        with self.assertRaises(AttributeError):
            m.n_rows = 10
        with self.assertRaises(AttributeError):
            m.n_cols = 10

    def test_default_values(self):
        """Checks that all cells are initialised with the specified default value."""
        value = random.random()  # noqa: S311
        m = Matrix(2, 2, default_value=value)
        for r in range(0, m.n_rows):
            for c in range(0, m.n_cols):
                self.assertEqual(m[r, c], value)

    def test_set_and_get_items(self):
        """Tests the setting and getting of individual cell values."""
        row = random.randrange(1, 20, 1)  # noqa: S311
        col = random.randrange(1, 20, 1)  # noqa: S311
        value = random.random()  # noqa: S311
        m = Matrix(20, 20)
        m[row, col] = value
        self.assertEqual(m[row, col], value)
        m = Matrix(20, 20)
        m.setitem(row, col, value)
        self.assertEqual(m.getitem(row, col), value)

    def test_set_and_get_rows(self):
        """Tests the setting and getting of entire matrix rows."""
        row = random.randrange(1, 20, 1)  # noqa: S311
        values = [random.random() for x in range(0, 20)]  # noqa: S311
        m = Matrix(20, 20)
        m[row, None] = values
        self.assertEqual(m[row, None], values)
        m = Matrix(20, 20)
        m.setrow(row, values)
        self.assertEqual(m.getrow(row), values)

    def test_set_and_get_columns(self):
        """Tests the setting and getting of entire matrix columns."""
        col = random.randrange(1, 20, 1)  # noqa: S311
        values = [random.random() for x in range(0, 20)]  # noqa: S311
        m = Matrix(20, 20)
        m[None, col] = values
        self.assertEqual(m[None, col], values)
        m = Matrix(20, 20)
        m.setcol(col, values)
        self.assertEqual(m.getcol(col), values)

    def test_boolification(self):
        """Tests the correct coversion of matrices to booleans."""
        m = Matrix(5, 5)
        self.assertFalse(bool(m))
        m[1, 1] = random.random()  # noqa: S311
        self.assertTrue(bool(m))

    def test_indeces(self):
        """Tests that indeces assign to the correct row and column."""
        m = Matrix(10, 10)
        m[0, 0] = "a"
        m[0, 9] = "b"
        m[9, 0] = "x"
        m[9, 9] = "y"
        self.assertEqual(m.getitem(0, 0), "a")
        self.assertEqual(m.getitem(0, 9), "b")
        self.assertEqual(m.getitem(9, 0), "x")
        self.assertEqual(m.getitem(9, 9), "y")

    def test_index_wrapping(self):
        """Tests that negative indeces are wrapped around correctly."""
        m = Matrix(10, 10)
        m[-10, -10] = "a"
        m[-10, -1] = "b"
        m[-1, -10] = "x"
        m[-1, -1] = "y"
        self.assertEqual(m.getitem(0, 0), "a")
        self.assertEqual(m.getitem(0, 9), "b")
        self.assertEqual(m.getitem(9, 0), "x")
        self.assertEqual(m.getitem(9, 9), "y")

    def test_index_range(self):
        """Tests raising of IndexError if exceeding matrix indices."""
        m = Matrix(3, 5)
        with self.assertRaises(IndexError):
            m[-10, 2]
        with self.assertRaises(IndexError):
            m[0, -6]
        with self.assertRaises(IndexError):
            m[3, 2]
        with self.assertRaises(IndexError):
            m[2, 6]

    def test_repr(self):
        """Tests that matrix cells survive reconstruction from repr()."""
        value = random.random()  # noqa: S311
        m = Matrix(3, 3)
        m[2, 1] = value
        n = []
        out = repr(m)
        n = eval(out)  # noqa: S307
        self.assertEqual(m[2, 1], n[2, 1])
        self.assertEqual(n[2, 1], value)

    def test_listification(self):
        """Ensures that list and row access properties are consistently of type `list`."""
        m = Matrix(3, 3)
        rows = m.rows
        self.assertIsInstance(rows, list)
        for item in rows:
            self.assertIsInstance(item, list)
        cols = m.cols
        self.assertIsInstance(cols, list)
        for item in cols:
            self.assertIsInstance(item, list)

    def test_row_access(self):
        """Tests correct position of cells via list-of-row access method."""
        m = Matrix(3, 3)
        m[1, 0] = 0
        m[1, 1] = 1
        m[1, 2] = 2
        self.assertSequenceEqual(m[1, None], [0, 1, 2])
        self.assertSequenceEqual(m.getrow(1), [0, 1, 2])
        self.assertSequenceEqual(m.rows[1], [0, 1, 2])

    def test_col_access(self):
        """Tests correct position of cells via list-of-columns access method."""
        m = Matrix(3, 3)
        m[0, 1] = 0
        m[1, 1] = 1
        m[2, 1] = 2
        self.assertSequenceEqual(m[None, 1], [0, 1, 2])
        self.assertSequenceEqual(m.getcol(1), [0, 1, 2])
        self.assertSequenceEqual(m.cols[1], [0, 1, 2])

    def test_row_insertion_dimensions(self):
        """Tests correctness of dimensions after inserting new rows."""
        m = Matrix(3, 3)
        self.assertEqual(m.n_rows, 3)
        m.insert_row(0)
        self.assertEqual(m.n_rows, 4)
        m.insert_row(2)
        self.assertEqual(m.n_rows, 5)
        m.append_row()
        self.assertEqual(m.n_rows, 6)
        # Check that correct row counts are also reflected in other relevant places
        self.assertEqual(len(m.rows), m.n_rows)
        self.assertEqual(m.n_dim, (6, 3))

    def test_column_insertion_dimensions(self):
        """Tests correctness of dimensions after inserting new columns."""
        m = Matrix(3, 3)
        self.assertEqual(m.n_cols, 3)
        m.insert_col(0)
        self.assertEqual(m.n_cols, 4)
        m.insert_col(2)
        self.assertEqual(m.n_cols, 5)
        m.append_col()
        self.assertEqual(m.n_cols, 6)
        # Check that correct column counts are also reflected in other relevant places
        self.assertEqual(len(m.cols), m.n_cols)
        self.assertEqual(m.n_dim, (3, 6))

    def test_insert_row_data(self):
        """Tests that newly inserted rows are initialised with the correct values."""
        # Default values
        m = Matrix(2, 2)
        m.setrow(0, [1, 1])
        m.setrow(1, [1, 1])
        m.insert_row(1)
        self.assertEqual(m.getrow(1), [None, None])
        # Changing default values before insertion
        m = Matrix(2, 2, default_value=1)
        m.default_value = 0
        m.insert_row(1)
        self.assertEqual(m.getrow(1), [0, 0])
        # Supplied values
        m = Matrix(2, 2)
        m.insert_row(1, [1, 2])
        self.assertEqual(m.getrow(1), [1, 2])

    def test_insert_column_data(self):
        """Tests that newly inserted columns are initialised with the correct values."""
        # Default values
        m = Matrix(2, 2)
        m.setcol(0, [1, 1])
        m.setcol(1, [1, 1])
        m.insert_col(1)
        self.assertEqual(m.getcol(1), [None, None])
        # Changing default values before insertion
        m = Matrix(2, 2, default_value=1)
        m.default_value = 0
        m.insert_col(1)
        self.assertEqual(m.getcol(1), [0, 0])
        # Supplied values
        m = Matrix(2, 2)
        m.insert_col(1, [1, 2])
        self.assertEqual(m.getcol(1), [1, 2])

    def test_insert_row_value_validity(self):  # noqa: C901
        """Tests that `insert_row()` accepts only valid value sequences as argument."""
        m = Matrix(3, 3)
        valid = ([1, 2, 3], "abc", (4, 5, 6), {7, 8, 9})
        too_short = ([1, 2], "ab", (3, 4), {7, 8})
        too_long = ([1, 2, 3, 4], "abcd", (3, 4, 5, 6), {7, 8, 9, 10})
        non_seq = (123, False, str)
        for item in valid:
            try:
                m.append_row(item)
            except ValueError:
                self.fail("append_row() raised ValueError when given valid arguments.")
        for item in too_long:
            with self.assertRaises(
                ValueError, msg=f"Too-long item: {item} should raise ValueError."
            ):
                m.append_row(item)
        for item in too_short:
            with self.assertRaises(
                ValueError, msg=f"Too-short item: {item} should raise ValueError."
            ):
                m.append_row(item)
        for item in non_seq:
            with self.assertRaises(
                TypeError, msg=f"Non-sequence item: {item} should raise TypeError."
            ):
                m.append_row(item)

    def test_insert_column_value_validity(self):  # noqa: C901
        """Tests that `insert_row()` accepts only valid value sequences as argument."""
        m = Matrix(3, 3)
        valid = ([1, 2, 3], "abc", (4, 5, 6), {7, 8, 9})
        too_short = ([1, 2], "ab", (3, 4), {7, 8})
        too_long = ([1, 2, 3, 4], "abcd", (3, 4, 5, 6), {7, 8, 9, 10})
        non_seq = (123, False, str)
        for item in valid:
            try:
                m.append_col(item)
            except ValueError:
                self.fail("append_col() raised ValueError when given valid arguments.")
        for item in too_long:
            with self.assertRaises(
                ValueError, msg=f"Too-long item: {item} should raise ValueError."
            ):
                m.append_col(item)
        for item in too_short:
            with self.assertRaises(
                ValueError, msg=f"Too-short item: {item} should raise ValueError."
            ):
                m.append_col(item)
        for item in non_seq:
            with self.assertRaises(
                TypeError, msg=f"Non-sequence item: {item} should raise TypeError."
            ):
                m.append_col(item)


class TestMatrixIterator(unittest.TestCase):
    """Unit tests for the `transcriptionist.matrices.MatrixIterator` class."""

    def test_iteration_order(self):
        """Tests that Matrix objects are iterated through in the correct order."""
        m = Matrix(2, 2)
        m.setrow(0, [0, 1])
        m.setrow(1, [2, 3])
        i = 0
        for cell in m:
            self.assertEqual(cell, i)
            i += 1

    def test_iteration_range(self):
        """Tests that iter(Matrix) iterates exhaustively through all cells."""
        m = Matrix(3, 5, default_value=1)
        total = 0
        for cell in m:
            total += cell
        self.assertEqual(total, 15)

    def test_enumeration_pointers(self):
        """Tests that the pointers in an enumeration point to the correct cells."""
        m = Matrix(2, 2)
        m.setrow(0, [0, 1])
        m.setrow(1, [2, 3])
        i = 0
        for ptr, cell in m.enumerator():
            self.assertEqual(m[ptr], cell)
            self.assertEqual(cell, i)
            i += 1


class TestMatrixPointers(unittest.TestCase):
    """Unit tests for the `transcriptionist.matrices.MatrixPointer` class."""

    def test_set_and_get_by_pointer(self):
        """Checks addressing of specific `Matrix` cells by `MatrixPointer`."""
        value = random.random()  # noqa: S311
        m = Matrix(20, 20)
        p = MatrixPointer(m)
        p.r = random.randrange(1, 20, 1)  # noqa: S311
        p.c = random.randrange(1, 20, 1)  # noqa: S311
        m[p] = value
        self.assertEqual(m[p], value)
        self.assertEqual(m[p.r, p.c], value)
        m = Matrix(20, 20)
        p = MatrixPointer(m)
        p.r = random.randrange(1, 20, 1)  # noqa: S311
        p.c = random.randrange(1, 20, 1)  # noqa: S311
        m.setitem(p, value)
        self.assertEqual(m.getitem(p), value)
        self.assertEqual(m.getitem(p.r, p.c), value)

    def test_pointer_default_coordinates(self):
        """Checks that `MatrixPointer` is initialised with correct default coordinates."""
        m = Matrix(5, 5)
        p = MatrixPointer(m)
        self.assertEqual(p[0], 0)
        self.assertEqual(p[1], 0)
        self.assertEqual(p.r, 0)
        self.assertEqual(p.c, 0)
        p = MatrixPointer(m, 2, 3)
        self.assertEqual(p[0], 2)
        self.assertEqual(p[1], 3)
        self.assertEqual(p.r, 2)
        self.assertEqual(p.c, 3)

    def test_pointer_range(self):
        """Checks that pointer cannot be set out of the range of the associated matrix."""
        m = Matrix(5, 2)
        with self.assertRaises(ValueError):
            p = MatrixPointer(m, 5, 1)
        with self.assertRaises(ValueError):
            p = MatrixPointer(m, 2, 2)
        p = MatrixPointer(m)
        with self.assertRaises(ValueError):
            p.r = 5
        with self.assertRaises(ValueError):
            p[0] = 5
        with self.assertRaises(ValueError):
            p.c = 2
        with self.assertRaises(ValueError):
            p[1] = 2

    def test_pointer_equality(self):
        """Ensures pointers with same coordinates but different matrices compare True."""
        m = Matrix(5, 5)
        p1 = MatrixPointer(m, 2, 3)
        p2 = MatrixPointer(m, 2, 3)
        self.assertEqual(p1, p2)
        self.assertEqual(p1, [2, 3])
        self.assertEqual(p1, (2, 3))
        p2.advance()
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p2, [2, 3])
        self.assertNotEqual(p2, (2, 3))


if __name__ == "__main__":
    unittest.main(verbosity=2)
