import unittest
from validator import validate


class TestValidator(unittest.TestCase):
    def test_pass_case(self):
        params = {"n": 7, "k": 6, "j": 5, "s": 5}
        samples = [1, 2, 3, 4, 5, 6, 7]
        groups = [
            [2, 3, 4, 5, 6, 7],
            [1, 3, 4, 5, 6, 7],
            [1, 2, 4, 5, 6, 7],
            [1, 2, 3, 5, 6, 7],
            [1, 2, 3, 4, 6, 7],
            [1, 2, 3, 4, 5, 7],
            [1, 2, 3, 4, 5, 6],
        ]
        r = validate(params, samples, groups)
        self.assertTrue(r["pass"])
        self.assertEqual(r["failed_J_count"], 0)
        self.assertGreaterEqual(r["min_coverage"], 5)

    def test_fail_case(self):
        params = {"n": 7, "k": 6, "j": 5, "s": 5}
        samples = [1, 2, 3, 4, 5, 6, 7]
        groups = [[1, 2, 3, 4, 5, 6]]
        r = validate(params, samples, groups)
        self.assertFalse(r["pass"])
        self.assertGreater(r["failed_J_count"], 0)
        self.assertLess(r["min_coverage"], 5)


if __name__ == "__main__":
    unittest.main()
