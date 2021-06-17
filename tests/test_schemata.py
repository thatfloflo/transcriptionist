"""Unit tests for the `schemata` submodule of `transcriptionist`."""
import unittest
from transcriptionist.schemata import Schema


class TestSchema(unittest.TestCase):
    """Unit tests for the `transcriptionist.schemata.Schema` class."""

    def test_schema_creation(self):
        """Tests initialisation of schemata with various dimensions."""
        s = Schema()
        self.assertEqual(s.length, 1)
        self.assertEqual(len(s), 1)
        self.assertEqual(s.n_forms, 1)
        self.assertEqual(s.n_alternants, 0)
        s = Schema(10, 2)
        self.assertEqual(s.length, 10)
        self.assertEqual(len(s), 10)
        self.assertEqual(s.n_forms, 2)
        self.assertEqual(s.n_alternants, 1)

    def test_set_and_read_base(self):
        """Tests assigning and reading the base form of a Schema."""
        s = Schema(5)
        base_seq = ["a", "b", "c", "d", "e"]
        # From list
        s.base = base_seq
        self.assertEqual(s.base, base_seq)
        # From tupel
        s.base = tuple(base_seq)
        self.assertEqual(s.base, base_seq)
        # Invalid, too short
        with self.assertRaises(ValueError):
            s.base = ["a", "b"]
        # Invalid, too long
        with self.assertRaises(ValueError):
            s.base = base_seq + ["f"]
        # Invalid, not a sequence type
        with self.assertRaises(TypeError):
            s.base = 2718

    def test_set_and_read_alternants(self):
        """Tests assigning and reading the alternants of a Schema."""
        s = Schema(2, 5)
        self.assertEqual(s.alternants, [[None, None] for _ in range(0, 4)])
        s.set_alternant(0, ["a", "b"])
        self.assertEqual(s.alternants[0], ["a", "b"])
        s.set_alternant(3, ["c", "d"])
        self.assertEqual(s.alternants[3], ["c", "d"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
