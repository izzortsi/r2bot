import numpy as np
import unittest
from src.AverageTrueRange import AverageTrueRange


class TestAverageTrueRange(unittest.TestCase):
    high = np.array(
        [
            48.70,
            48.72,
            48.90,
            48.87,
            48.82,
            49.05,
            49.20,
            49.35,
            49.92,
            50.19,
            50.12,
            49.66,
            49.88,
            50.19,
            50.36,
            50.57,
            50.65,
            50.43,
            49.63,
            50.33,
            50.29,
            50.17,
            49.32,
            48.50,
            48.32,
            46.80,
            47.80,
            48.39,
            48.66,
            48.79,
        ]
    )
    low = np.array(
        [
            47.79,
            48.14,
            48.39,
            48.37,
            48.24,
            48.64,
            48.94,
            48.86,
            49.50,
            49.87,
            49.20,
            48.90,
            49.43,
            49.73,
            49.26,
            50.09,
            50.30,
            49.21,
            48.98,
            49.61,
            49.20,
            49.43,
            48.08,
            47.64,
            41.55,
            44.28,
            47.31,
            47.20,
            47.90,
            47.73,
        ]
    )
    close = np.array(
        [
            48.16,
            48.61,
            48.75,
            48.63,
            48.74,
            49.03,
            49.07,
            49.32,
            49.91,
            50.13,
            49.53,
            49.50,
            49.75,
            50.03,
            50.31,
            50.52,
            50.41,
            49.34,
            49.37,
            50.23,
            49.24,
            49.93,
            48.43,
            48.18,
            46.57,
            45.41,
            47.77,
            47.72,
            48.62,
            47.85,
        ]
    )
    smoothing_period = 14

    def test_compute_high_minus_low(self):
        ground_truth = np.array(
            [
                0.91,
                0.58,
                0.51,
                0.50,
                0.58,
                0.41,
                0.26,
                0.49,
                0.42,
                0.32,
                0.92,
                0.76,
                0.45,
                0.46,
                1.10,
                0.48,
                0.35,
                1.22,
                0.65,
                0.72,
                1.09,
                0.74,
                1.24,
                0.86,
                6.77,
                2.52,
                0.49,
                1.19,
                0.76,
                1.06,
            ]
        )
        average_true_range = AverageTrueRange(self.high, self.low, self.close)
        average_true_range._compute_high_minus_low()
        result = average_true_range.high_minus_low
        np.testing.assert_array_almost_equal(ground_truth, result)

    def test_compute_high_minus_previous_close(self):
        ground_truth = np.array(
            [
                np.NaN,
                0.56,
                0.29,
                0.12,
                0.19,
                0.31,
                0.17,
                0.28,
                0.60,
                0.28,
                0.01,
                0.13,
                0.38,
                0.44,
                0.33,
                0.26,
                0.13,
                0.02,
                0.29,
                0.96,
                0.06,
                0.93,
                0.61,
                0.07,
                0.14,
                0.23,
                2.39,
                0.62,
                0.94,
                0.17,
            ]
        )
        average_true_range = AverageTrueRange(self.high, self.low, self.close)
        average_true_range._compute_high_minus_previous_close()
        result = average_true_range.high_minus_previous_close
        np.testing.assert_array_almost_equal(ground_truth, result)

    def test_compute_low_minus_previous_close(self):
        ground_truth = np.array(
            [
                np.NaN,
                0.02,
                0.22,
                0.38,
                0.39,
                0.10,
                0.09,
                0.21,
                0.18,
                0.04,
                0.93,
                0.63,
                0.07,
                0.02,
                0.77,
                0.22,
                0.22,
                1.20,
                0.36,
                0.24,
                1.03,
                0.19,
                1.85,
                0.79,
                6.63,
                2.29,
                1.90,
                0.57,
                0.18,
                0.89,
            ]
        )
        average_true_range = AverageTrueRange(self.high, self.low, self.close)
        average_true_range._compute_low_minus_previous_close()
        result = average_true_range.low_minus_previous_close
        np.testing.assert_array_almost_equal(ground_truth, result)

    def test_compute_true_range(self):
        ground_truth = [
            0.91,
            0.58,
            0.51,
            0.50,
            0.58,
            0.41,
            0.26,
            0.49,
            0.60,
            0.32,
            0.93,
            0.76,
            0.45,
            0.46,
            1.10,
            0.48,
            0.35,
            1.22,
            0.65,
            0.96,
            1.09,
            0.93,
            1.85,
            0.86,
            6.77,
            2.52,
            2.39,
            1.19,
            0.94,
            1.06,
        ]
        average_true_range = AverageTrueRange(self.high, self.low, self.close)
        average_true_range._compute_true_range()
        result = average_true_range.true_range
        np.testing.assert_array_almost_equal(ground_truth, result)

    def test_compute_average_true_range(self):
        ground_truth = [
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            np.NaN,
            0.5550,
            0.5939,
            0.5858,
            0.5689,
            0.6155,
            0.6179,
            0.6424,
            0.6743,
            0.6928,
            0.7754,
            0.7815,
            1.2092,
            1.3026,
            1.3803,
            1.3667,
            1.3362,
            1.3165,
        ]
        average_true_range = AverageTrueRange(
            self.high, self.low, self.close, self.smoothing_period
        )
        result = average_true_range.compute_average_true_range()
        decimal = 3
        np.testing.assert_array_almost_equal(ground_truth, result, decimal)
