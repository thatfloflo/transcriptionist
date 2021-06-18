"""Unit tests for the `schemata` submodule of `transcriptionist`."""
import unittest
from transcriptionist.schemata import TargetSegment, TargetSchema


class TestTargetSegment(unittest.TestCase):
    """Unit tests for the `transcriptionist.schemata.TargetSegment` class."""

    def test_segment_creation(self):
        """Tests initialisation of target segments with various values."""
        seg = TargetSegment()
        self.assertEqual(seg.target, None)
        self.assertEqual(seg.score, 0)
        seg = TargetSegment("a", 7)
        self.assertEqual(seg.target, "a")
        self.assertEqual(seg.score, 7)
        seg = TargetSegment([1, 2, 3], 6)
        self.assertEqual(seg.target, [1, 2, 3])
        self.assertEqual(seg.score, 6)

    def test_segment_from_tuple(self):
        """Tests that segments can be initialised from a 2-tuple."""
        seg = TargetSegment.from_pair(("a", 4))
        self.assertEqual(seg.target, "a")
        self.assertEqual(seg.score, 4)

    def test_segment_from_list(self):
        """Tests that segments can be initialised from a 2-member list."""
        seg = TargetSegment.from_pair(["b", 3])
        self.assertEqual(seg.target, "b")
        self.assertEqual(seg.score, 3)

    def test_set_segment_target(self):
        """Tests reassigning a segment's target value after initialisation."""
        seg = TargetSegment()
        seg.target = "d"
        self.assertEqual(seg.target, "d")
        seg.target = (1, 2, 3)
        self.assertEqual(seg.target, (1, 2, 3))

    def test_set_segment_score(self):
        """Tests reassigning a segment's score value after initialisation."""
        seg = TargetSegment()
        seg.score = 16
        self.assertEqual(seg.score, 16)
        seg.score = 3.14
        self.assertEqual(seg.score, 3.14)

    def test_set_invalid_score(self):
        """Tests that only numeric values can be assigned as score."""
        # On initialisation
        with self.assertRaises(TypeError):
            seg = TargetSegment(score="hi")
        # Post-initialisation
        seg = TargetSegment()
        with self.assertRaises(TypeError):
            seg.score = "string"
        with self.assertRaises(TypeError):
            seg.score = ("t", "u", "p", "l", "e")

    def test_repr(self):
        """Tests that TargetSegment can be reconstructed from it's repr()."""
        seg1 = TargetSegment("foo", 42)
        out = repr(seg1)
        seg2 = eval(out)  # noqa: S307
        self.assertEqual(seg1.target, seg2.target)
        self.assertEqual(seg1.score, seg2.score)

    def test_to_string(self):
        """Tests that str() returns valid string on TargetSegment."""
        seg = TargetSegment("foo", 42)
        out = str(seg)
        self.assertIsInstance(out, str)
        self.assertEqual(out, "(foo, 42)")

    def test_hashes(self):
        """Tests that hash() values are equal to (target, score) tuples."""
        seg = TargetSegment("foo", 42)
        self.assertEqual(hash(seg), hash(("foo", 42)))
        seg.score += 1
        self.assertEqual(hash(seg), hash(("foo", 43)))
        seg.target = (1, 2, 3)
        self.assertEqual(hash(seg), hash(((1, 2, 3), 43)))
        self.assertNotEqual(hash(seg), hash(("foo", 43)))

    def test_hashability(self):
        """Tests raising of exceptions when trying to hash with non-hashable targets."""
        seg = TargetSegment()
        try:
            hash(seg)
            seg.target = "Hawai'i"
            hash(seg)
            seg.target = 12
            hash(seg)
            seg.target = (1, 2, "c")
            hash(seg)
        except TypeError:
            self.fail(
                "hash() of TargetSegment raises TypeError even though target is hashable."
            )
        with self.assertRaises(TypeError):
            seg.target = [1, 2, 3]
            hash(seg)
        with self.assertRaises(TypeError):
            seg.target = {1, 2, 3}
            hash(seg)
        with self.assertRaises(RecursionError):
            seg.target = seg
            hash(seg)

    def test_equality(self):
        """Tests equality comparisons of two TargetSegment objects."""
        seg1 = TargetSegment("one", 1)
        seg2 = TargetSegment("two", 2)
        self.assertFalse(seg1 == seg2)
        seg2.target = "one"
        self.assertFalse(seg1 == seg2)
        seg2.score = 1
        self.assertTrue(seg1 == seg2)

    def test_equality_to_tuple(self):
        """Tests equality comparison of TargetSegment and tuples/lists."""
        seg = TargetSegment("one", 1)
        self.assertTrue(seg == ("one", 1))
        self.assertTrue(seg == ["one", 1])
        self.assertFalse(seg == ("one", 2))
        self.assertFalse(seg == ["one", 2])
        self.assertFalse(seg == ("one", 1, 2))
        self.assertFalse(seg == ["one", 1, 2])
        self.assertFalse(seg == (1))
        self.assertFalse(seg == ["one"])


class TestTargetSchema(unittest.TestCase):
    """Unit tests for the `transcriptionist.schemata.TargetSchema` class."""

    def test_schema_creation(self):
        """Tests initialisation of schemata with various dimensions."""
        s = TargetSchema()
        self.assertEqual(s.length, 1)
        self.assertEqual(len(s), 1)
        self.assertEqual(s.n_forms, 1)
        self.assertEqual(s.n_alternants, 0)
        s = TargetSchema(10, 2)
        self.assertEqual(s.length, 10)
        self.assertEqual(len(s), 10)
        self.assertEqual(s.n_forms, 2)
        self.assertEqual(s.n_alternants, 1)

    def test_set_and_read_base(self):
        """Tests assigning and reading the base form of a Schema."""
        s = TargetSchema(5)
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
        s = TargetSchema(2, 5)
        self.assertEqual(s.alternants, [[None, None] for _ in range(0, 4)])
        s.set_alternant(0, ["a", "b"])
        self.assertEqual(s.alternants[0], ["a", "b"])
        s.set_alternant(3, ["c", "d"])
        self.assertEqual(s.alternants[3], ["c", "d"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
