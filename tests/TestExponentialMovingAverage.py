import numpy as np
import unittest
from src.ExponentialMovingAverage import ExponentialMovingAverage


class TestExponentialMovingAverage(unittest.TestCase):
    prices = np.array(
        [
            22.27,
            22.19,
            22.08,
            22.17,
            22.18,
            22.13,
            22.23,
            22.43,
            22.24,
            22.29,
            22.15,
            22.39,
            22.38,
            22.61,
            23.36,
            24.05,
            23.75,
            23.83,
            23.95,
            23.63,
            23.82,
            23.87,
            23.65,
            23.19,
            23.10,
            23.33,
            22.68,
            23.10,
            22.40,
            22.17,
        ]
    )
    period = 10

    def test_compute_simple_moving_average(self):
        ground_truth = np.array(
            [
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                22.22,
                22.21,
                22.23,
                22.26,
                22.31,
                22.42,
                22.61,
                22.77,
                22.91,
                23.08,
                23.21,
                23.38,
                23.53,
                23.65,
                23.71,
                23.69,
                23.61,
                23.51,
                23.43,
                23.28,
                23.13,
            ]
        )
        decimal = 2
        exponential_moving_average = ExponentialMovingAverage(self.prices, self.period)
        exponential_moving_average._compute_simple_moving_average()
        result = exponential_moving_average.simple_moving_average
        np.testing.assert_array_almost_equal(ground_truth, result, decimal)

    def test_compute_weighting_multiplier_1(self):
        ground_truth = 0.1818
        decimal = 4
        exponential_moving_average = ExponentialMovingAverage(self.prices, self.period)
        exponential_moving_average._compute_weighting_multiplier()
        result = exponential_moving_average.weighting_multiplier
        self.assertAlmostEqual(ground_truth, result, decimal)

    def test_compute_weighting_multiplier_2(self):
        ground_truth = 0.0952
        period = 20
        decimal = 4
        exponential_moving_average = ExponentialMovingAverage(self.prices, period)
        exponential_moving_average._compute_weighting_multiplier()
        result = exponential_moving_average.weighting_multiplier
        self.assertAlmostEqual(ground_truth, result, decimal)

    def test_compute_exponential_moving_average(self):
        ground_truth = np.array(
            [
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                np.NaN,
                22.22,
                22.21,
                22.24,
                22.27,
                22.33,
                22.52,
                22.80,
                22.97,
                23.13,
                23.28,
                23.34,
                23.43,
                23.51,
                23.54,
                23.47,
                23.40,
                23.39,
                23.26,
                23.23,
                23.08,
                22.92,
            ]
        )
        decimal = 2
        exponential_moving_average = ExponentialMovingAverage(self.prices, self.period)
        result = exponential_moving_average.compute_exponential_moving_average()
        np.testing.assert_array_almost_equal(ground_truth, result, decimal)
