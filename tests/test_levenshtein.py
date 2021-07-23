"""Unit tests for the `levenshtein` submodule of `transcriptionist`."""
import unittest
from transcriptionist.levenshtein import Levenshtein


class TestLevenshtein(unittest.TestCase):
    """Unit tests for the `transcriptionist.levenshtein.Levenshtein` class."""

    def test_levenshtein_unweighted(self):
        """Checks the edit distances for some strings with default weightings."""
        unweighted = {
            ("sitten", "kitten"): 1,  # subsitute s->k
            ("sitten", "kittens"): 2,  # subsitute s->k, delete or insert final s
            (
                "sitting",
                "kitten",
            ): 3,  # substitute s->k, subsitute i->e, delete or insert final g
            ("Saturday", "Sunday"): 3,  # delete a, delete t, substitute r->n
            ("", ""): 0,  # equal
            ("abcdefg", "abcdefg"): 0,  # equal
            ("abcdefg", ""): 7,  # delete/insert a, b, c, d, e, f, g
            ("abc", "xyz"): 3,  # subsititue a->x, b->y, c->z
            ("ABxC", "ABC"): 1,
            ("abc", "abXc"): 1,
        }
        for (str1, str2), dist in unweighted.items():
            ld = Levenshtein(str1, str2)
            ld.compute()
            # print(f"Comparing: '{str1}', '{str2}':")
            # print(f"Edit distance: {dist}")
            # print(ld.visualise())
            # print("-" * 80)
            self.assertEqual(
                ld.distance,
                dist,
                msg=f'ld("{str1}", "{str2}") should equal {dist}, but is {ld.distance}',
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
