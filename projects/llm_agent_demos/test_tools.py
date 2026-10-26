import unittest

from tools import multiply


class MultiplyTests(unittest.TestCase):
    def test_multiplies_numbers(self):
        self.assertEqual(multiply(18, 24), 432)

    def test_accepts_boundaries(self):
        self.assertEqual(multiply(0, 24), 0)
        self.assertEqual(
            multiply(1_000_000, 1_000_000),
            1_000_000_000_000,
        )

    def test_rejects_non_integer_inputs(self):
        cases = [("18", 24), (18, 24.5), (True, 24), (18, None)]
        for a, b in cases:
            with self.subTest(a=a, b=b):
                with self.assertRaises(ValueError):
                    multiply(a, b)

    def test_rejects_out_of_range_inputs(self):
        cases = [(-1, 24), (18, -1), (1_000_001, 24), (18, 1_000_001)]
        for a, b in cases:
            with self.subTest(a=a, b=b):
                with self.assertRaises(ValueError):
                    multiply(a, b)


if __name__ == "__main__":
    unittest.main()