import numpy as np


class AverageTrueRange:
    def __init__(self, high, low, close):
        self.high = high
        self.low = low
        self.close = close
        self.high_minus_low = None
        self.high_minus_previous_close = None
        self.low_minus_previous_close = None
        self.true_range = None
        self.average_true_range = None

    def compute_high_minus_low(self) -> None:
        self.high_minus_low = self.high - self.low

    def compute_high_minus_previous_close(self) -> None:
        self.high_minus_previous_close = np.empty(self.high.shape)
        self.high_minus_previous_close[0] = np.NaN
        self.high_minus_previous_close[1:] = np.absolute(
            self.high[1:] - self.close[0 : len(self.close) - 1]
        )

    def compute_low_minus_previous_close(self) -> None:
        self.low_minus_previous_close = np.empty(self.low.shape)
        self.low_minus_previous_close[0] = np.NaN
        self.low_minus_previous_close[1:] = np.absolute(
            self.low[1:] - self.close[0 : len(self.close) - 1]
        )

    def compute_true_range(self) -> None:
        self.compute_high_minus_low()
        self.compute_high_minus_previous_close()
        self.compute_low_minus_previous_close()
        self.true_range = np.empty(self.high_minus_low.shape)
        self.true_range[0] = self.high_minus_low[0]
        self.true_range[1:] = np.maximum.reduce(
            [
                self.high_minus_low[1:],
                self.high_minus_previous_close[1:],
                self.low_minus_previous_close[1:],
            ]
        )

    def compute_average_true_range(self, period) -> None:
        self.compute_true_range()
        self.average_true_range = np.empty(self.high.shape)
        self.average_true_range[: period - 1] = np.NaN
        self.average_true_range[period - 1] = np.average(self.true_range[:period])
        # TODO: replace for loop with something more efficient from numpy
        for i in range(period, len(self.average_true_range)):
            self.average_true_range[i] = (
                self.average_true_range[i - 1] * (period - 1) + self.true_range[i]
            ) / period
