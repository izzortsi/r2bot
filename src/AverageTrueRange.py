"""Calculate the Average True Range."""
import numpy as np


class AverageTrueRange:
    """Implementation of the Average True Range method."""

    def __init__(
        self,
        highest_prices: np.array,
        lowest_prices: np.array,
        closing_prices: np.array,
        smoothing_period: int = 14,
    ) -> None:
        """
        Initialize an AverageTrueRange object.

        Parameters
        ----------
        highest_prices : np.array
            Highest price for each interval of the period.
        lowest_prices : np.array
            Lowest price for each interval of the period.
        closing_prices : np.array
            Closing price for each interval of the period.
        smoothing_period : int, default=14
            Smoothing period.
        """
        self.highest_prices = highest_prices
        self.lowest_prices = lowest_prices
        self.closing_prices = closing_prices
        self.smoothing_period = smoothing_period
        self.high_minus_low = None
        self.high_minus_previous_close = None
        self.low_minus_previous_close = None
        self.true_range = None
        self.average_true_range = None

    def _compute_high_minus_low(self) -> None:
        """Calculate the high - low column."""
        self.high_minus_low = self.highest_prices - self.lowest_prices

    def _compute_high_minus_previous_close(self) -> None:
        """Calculate the high - previous close column."""
        self.high_minus_previous_close = np.empty(self.highest_prices.shape)
        self.high_minus_previous_close[0] = np.NaN
        self.high_minus_previous_close[1:] = np.absolute(
            self.highest_prices[1:]
            - self.closing_prices[0 : len(self.closing_prices) - 1]
        )

    def _compute_low_minus_previous_close(self) -> None:
        """Calculate the low - previous close column."""
        self.low_minus_previous_close = np.empty(self.lowest_prices.shape)
        self.low_minus_previous_close[0] = np.NaN
        self.low_minus_previous_close[1:] = np.absolute(
            self.lowest_prices[1:]
            - self.closing_prices[0 : len(self.closing_prices) - 1]
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

    def compute_average_true_range(self) -> float:
        """
        Calculate the average true range.

        Returns
        ----------
        average_true_range : float
            The average true range.
        """
        self._compute_true_range()
        self.average_true_range = np.empty(self.highest_prices.shape)
        self.average_true_range[: self.smoothing_period - 1] = np.NaN
        self.average_true_range[self.smoothing_period - 1] = np.average(
            self.true_range[: self.smoothing_period]
        )
        for i in range(self.smoothing_period, len(self.average_true_range)):
            self.average_true_range[i] = (
                self.average_true_range[i - 1] * (self.smoothing_period - 1)
                + self.true_range[i]
            ) / self.smoothing_period
        return self.average_true_range
