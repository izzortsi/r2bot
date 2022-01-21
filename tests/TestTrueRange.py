import unittest

from src.TrueRange import TrueRange


class TestTrueRange(unittest.TestCase):
    # Tests based on https://www.tororadar.com.br/investimento/analise-tecnica/medias-moveis
    def test_method1(self):
        true_range = TrueRange()
        self.assertAlmostEqual(true_range.method1(48.70, 47.79), 0.91, 3)
        self.assertAlmostEqual(true_range.method1(49.20, 48.94), 0.26, 3)
        self.assertAlmostEqual(true_range.method1(50.19, 49.87), 0.32, 3)
        self.assertAlmostEqual(true_range.method1(50.36, 49.26), 1.10, 3)
        self.assertAlmostEqual(true_range.method1(48.32, 41.55), 6.77, 3)

    def test_method2(self):
        true_range = TrueRange()
        self.assertAlmostEqual(true_range.method2(48.72, 48.16), 0.56, 3)
        self.assertAlmostEqual(true_range.method2(50.12, 50.13), 0.01, 3)
        self.assertAlmostEqual(true_range.method2(50.65, 50.52), 0.13, 3)
        self.assertAlmostEqual(true_range.method2(46.80, 46.57), 0.23, 3)
        self.assertAlmostEqual(true_range.method2(48.79, 48.62), 0.17, 3)

    def test_method3(self):
        true_range = TrueRange()
        self.assertAlmostEqual(true_range.method3(48.14, 48.16), 0.02, 3)
        self.assertAlmostEqual(true_range.method3(48.24, 48.63), 0.39, 3)
        self.assertAlmostEqual(true_range.method3(49.20, 50.13), 0.93, 3)
        self.assertAlmostEqual(true_range.method3(49.21, 50.41), 1.20, 3)
        self.assertAlmostEqual(true_range.method3(41.55, 48.18), 6.63, 3)

    def test_true_range(self):
        true_range = TrueRange()
        self.assertAlmostEqual(true_range.true_range(48.72, 48.14, 48.16), 0.58, 3)
        self.assertAlmostEqual(true_range.true_range(49.20, 48.94, 49.03), 0.26, 3)
        self.assertAlmostEqual(true_range.true_range(50.12, 49.20, 50.13), 0.93, 3)
        self.assertAlmostEqual(true_range.true_range(50.29, 49.20, 50.23), 1.09, 3)
        self.assertAlmostEqual(true_range.true_range(48.32, 41.55, 48.18), 6.77, 3)
