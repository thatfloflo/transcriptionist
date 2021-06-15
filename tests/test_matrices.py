import unittest
import random
from transcriptionist.matrices import Matrix, MatrixPointer


class TestMatrices(unittest.TestCase):
    def test_minimum_dimensions(self):
        with self.assertRaises(ValueError):
            m = Matrix(0, 0)

    def test_dimension_attributes(self):
        rows = random.randint(1, 20)
        cols = random.randint(1, 20)
        m = Matrix(rows, cols)
        self.assertEqual(m.n_dim, (rows, cols))
        self.assertEqual(m.n_rows, rows)
        self.assertEqual(m.n_cols, cols)

    def test_dimension_attribute_protection(self):
        m = Matrix(1, 1)
        with self.assertRaises(AttributeError):
            m.n_dim = (10, 20)
        with self.assertRaises(AttributeError):
            m.n_rows = 10
        with self.assertRaises(AttributeError):
            m.n_cols = 10

    def test_default_values(self):
        value = random.random()
        m = Matrix(2, 2, default_value=value)
        for r in range(0, m.n_rows):
            for c in range(0, m.n_cols):
                self.assertEqual(m[r, c], value)

    def test_set_and_get_items(self):
        row = random.randrange(1, 20, 1)
        col = random.randrange(1, 20, 1)
        value = random.random()
        m = Matrix(20, 20)
        m[row, col] = value
        self.assertEqual(m[row, col], value)
        m = Matrix(20, 20)
        m.setitem(row, col, value)
        self.assertEqual(m.getitem(row, col), value)

    def test_set_and_get_rows(self):
        row = random.randrange(1, 20, 1)
        values = [random.random() for x in range(0, 20)]
        m = Matrix(20, 20)
        m[row, None] = values
        self.assertEqual(m[row, None], values)
        m = Matrix(20, 20)
        m.setrow(row, values)
        self.assertEqual(m.getrow(row), values)

    def test_set_and_get_columns(self):
        col = random.randrange(1, 20, 1)
        values = [random.random() for x in range(0, 20)]
        m = Matrix(20, 20)
        m[None, col] = values
        self.assertEqual(m[None, col], values)
        m = Matrix(20, 20)
        m.setcol(col, values)
        self.assertEqual(m.getcol(col), values)

    def test_boolification(self):
        m = Matrix(5, 5)
        self.assertFalse(bool(m))
        m[1, 1] = random.random()
        self.assertTrue(bool(m))

    def test_indeces(self):
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
        value = random.random()
        m = Matrix(3, 3)
        m[2, 2] = value
        n = []
        out = repr(m)
        n = eval(out)
        self.assertEqual(m[2, 2], n[2][2])

    def test_listification(self):
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
        m = Matrix(3, 3)
        m[1, 0] = 0
        m[1, 1] = 1
        m[1, 2] = 2
        self.assertSequenceEqual(m[1, None], [0, 1, 2])
        self.assertSequenceEqual(m.getrow(1), [0, 1, 2])
        self.assertSequenceEqual(m.rows[1], [0, 1, 2])

    def test_col_access(self):
        m = Matrix(3, 3)
        m[0, 1] = 0
        m[1, 1] = 1
        m[2, 1] = 2
        self.assertSequenceEqual(m[None, 1], [0, 1, 2])
        self.assertSequenceEqual(m.getcol(1), [0, 1, 2])
        self.assertSequenceEqual(m.cols[1], [0, 1, 2])


class TestMatrixPointers(unittest.TestCase):
    def test_set_and_get_by_pointer(self):
        value = random.random()
        m = Matrix(20, 20)
        p = MatrixPointer(m)
        p.r = random.randrange(1, 20, 1)
        p.c = random.randrange(1, 20, 1)
        m[p] = value
        self.assertEqual(m[p], value)
        self.assertEqual(m[p.r, p.c], value)
        m = Matrix(20, 20)
        p = MatrixPointer(m)
        p.r = random.randrange(1, 20, 1)
        p.c = random.randrange(1, 20, 1)
        m.setitem(p, value)
        self.assertEqual(m.getitem(p), value)
        self.assertEqual(m.getitem(p.r, p.c), value)

    def test_pointer_defaults(self):
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
