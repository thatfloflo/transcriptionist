"""Unit tests for the `schemata` submodule of `transcriptionist`."""
import unittest
from transcriptionist.schemata import TargetSegment, TargetSchema
from transcriptionist.matrices import Matrix


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

    @unittest.skip("We shouldn't hash mutable objects.")
    def test_hashes(self):
        """Tests that hash() values are equal to (target, score) tuples."""
        seg = TargetSegment("foo", 42)
        self.assertEqual(hash(seg), hash(("foo", 42)))
        seg.score += 1
        self.assertEqual(hash(seg), hash(("foo", 43)))
        seg.target = (1, 2, 3)
        self.assertEqual(hash(seg), hash(((1, 2, 3), 43)))
        self.assertNotEqual(hash(seg), hash(("foo", 43)))

    @unittest.skip("We shouldn't hash mutable objects.")
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
        self.assertEqual(len(s), 10 * 2)
        self.assertEqual(s.n_forms, 2)
        self.assertEqual(s.n_alternants, 1)

    def test_schema_creation_from_matrix(self):
        """Tests initialisation of schemata by passing a matrix."""
        m = Matrix(3, 3)
        s1 = TargetSchema(3, 3)
        for ptr, _ in m.enumerator():
            m[ptr] = TargetSegment(f"{ptr.r}:{ptr.c}")
            s1[ptr] = TargetSegment(f"{ptr.r}:{ptr.c}")
        s2 = TargetSchema(m)
        self.assertEqual(s1, s2)

    def test_set_and_read_base(self):
        """Tests assigning and reading the base form of a Schema."""
        s = TargetSchema(5)
        base_seq = ["a", "b", "c", "d", "e"]
        for i in range(0, len(base_seq)):
            base_seq[i] = TargetSegment(base_seq[i])
        # From list
        s.setbase(base_seq)
        self.assertEqual(s.getbase(), base_seq)
        # From tupel
        s.setbase(tuple(base_seq))
        self.assertEqual(s.getbase(), base_seq)
        # Invalid, too short
        with self.assertRaises(ValueError):
            s.setbase([TargetSegment("a"), TargetSegment("b")])
        # Invalid, too long
        with self.assertRaises(ValueError):
            s.setbase(base_seq + [TargetSegment("f")])
        # Invalid, not a sequence type
        with self.assertRaises(TypeError):
            s.setbase(2718)

    def test_schema_compilation(self):
        """Tests the compilation of a TargetSchema to a TargetCompilation."""
        s = TargetSchema(4, 8)
        s[0, 0] = TargetSegment("??", 1.0)
        s[0, 1] = TargetSegment("a", 1.0)
        s[0, 2] = TargetSegment("??", 1.0)
        s[0, 3] = TargetSegment("a", 1.0)
        s[1, 0] = TargetSegment("x??", 1.0)
        s[2, 0] = TargetSegment("xw", 1.0)
        s[3, 1] = TargetSegment("??", 1.0)
        s[3, 3] = TargetSegment("??", 1.0)
        s[4, 0] = TargetSegment("w", 0.5)
        s[5, 0] = TargetSegment("x", 0.5)
        s[6, 2] = TargetSegment("??", 0.5)
        s[7, 2] = TargetSegment("??", 0.5)
        c = s.compile(debug=False)
        expected = (
            ("wa??a", 3.0),
            ("xw??????", 3.5),
            ("xw??????", 3.5),
            ("x????????", 4.0),
            ("w??????", 3.5),
            ("xwa??a", 4.0),
            ("xwa??a", 3.5),
            ("xa??a", 3.0),
            ("xwa??a", 3.5),
            ("x????????", 3.5),
            ("w??????", 3.0),
            ("wa??a", 3.5),
            ("x??????", 3.0),
            ("??a??a", 3.5),
            ("????????", 3.5),
            ("x??a??a", 3.5),
            ("????????", 3.5),
            ("x??a??a", 3.5),
            ("??a??a", 4.0),
            ("x????????", 3.5),
            ("xa??a", 3.0),
            ("xw??????", 4.0),
            ("x??????", 3.0),
            ("w??????", 3.0),
            ("????????", 4.0),
            ("??a??a", 3.5),
            ("xa??a", 3.5),
            ("x??????", 3.5),
            ("wa??a", 3.0),
            ("x??a??a", 4.0),
        )
        self.assertEqual(len(c), len(expected))
        for expected_item in expected:
            self.assertIn(expected_item[0], c)
        print("\n" + "-" * 80)
        print("TargetSchema:\n")
        print(s.stringify(cell_width=9))
        print("Compilation:\n", c)
        print("Expected:\n", expected)
        print("-" * 80)


if __name__ == "__main__":
    unittest.main(verbosity=2)
