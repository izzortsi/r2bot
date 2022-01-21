"""Calculate the Average True Range."""
import numpy as np


class AverageTrueRange:
    """Implementation of the Average True Range method."""

    def __init__(self, high: np.array, low: np.array, close: np.array) -> None:
        """
        Initialize an AverageTrueRange object.

        Parameters
        ----------
        high : np.array
            Highest price for each interval of the period.
        low : np.array
            Lowest price for each interval of the period.
        close : np.array
            Close price for each interval of the period.
        """
        self.high = high
        self.low = low
        self.close = close
        self.high_minus_low = None
        self.high_minus_previous_close = None
        self.low_minus_previous_close = None
        self.true_range = None
        self.average_true_range = None

    def _compute_high_minus_low(self) -> None:
        """Calculate the high - low column."""
        self.high_minus_low = self.high - self.low

    def _compute_high_minus_previous_close(self) -> None:
        """Calculate the high - previous close column."""
        self.high_minus_previous_close = np.empty(self.high.shape)
        self.high_minus_previous_close[0] = np.NaN
        self.high_minus_previous_close[1:] = np.absolute(
            self.high[1:] - self.close[0 : len(self.close) - 1]
        )

    def _compute_low_minus_previous_close(self) -> None:
        """Calculate the low - previous close column."""
        self.low_minus_previous_close = np.empty(self.low.shape)
        self.low_minus_previous_close[0] = np.NaN
        self.low_minus_previous_close[1:] = np.absolute(
            self.low[1:] - self.close[0 : len(self.close) - 1]
        )

    def _compute_true_range(self) -> None:
        """Calculate the true range column."""
        self._compute_high_minus_low()
        self._compute_high_minus_previous_close()
        self._compute_low_minus_previous_close()
        self.true_range = np.empty(self.high_minus_low.shape)
        self.true_range[0] = self.high_minus_low[0]
        self.true_range[1:] = np.maximum.reduce(
            [
                self.high_minus_low[1:],
                self.high_minus_previous_close[1:],
                self.low_minus_previous_close[1:],
            ]
        )

    def compute_average_true_range(self, smoothing_period: int = 14) -> None:
        """
        Calculate the average true range.

        Parameters
        ----------
        smoothing_period : int, default=14
            Smoothing period.
        """
        self._compute_true_range()
        self.average_true_range = np.empty(self.high.shape)
        self.average_true_range[: smoothing_period - 1] = np.NaN
        self.average_true_range[smoothing_period - 1] = np.average(
            self.true_range[:smoothing_period]
        )
        # TODO: replace for loop with something more efficient from numpy
        for i in range(smoothing_period, len(self.average_true_range)):
            self.average_true_range[i] = (
                self.average_true_range[i - 1] * (smoothing_period - 1)
                + self.true_range[i]
            ) / smoothing_period
