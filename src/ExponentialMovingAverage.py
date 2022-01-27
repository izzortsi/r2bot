"""Calculate the Exponential Moving Average."""
import numpy as np


class ExponentialMovingAverage:
    """Implementation of the Exponential Moving Average method."""

    def __init__(
        self, prices: np.array, period: int, smoothing_factor: int = 2
    ) -> None:
        """
        Initialize an AverageTrueRange object.

        Parameters
        ----------
        prices : np.array
            Prices for each interval of the period, e.g., closing prices.
        period : int
            Period size, e.g., 10 days.
        smoothing_factor : int
            Gives the most recent observations more weight.
            If the smoothing factor is increased, more
            recent observations have more influence on the EMA.
        """
        self.prices = prices
        self.period = period
        self.smoothing_factor = smoothing_factor
        self.simple_moving_average = None
        self.weighting_multiplier = None
        self.exponential_moving_average = None

    def _compute_simple_moving_average(self) -> None:
        """Calculate the simple moving average."""
        self.simple_moving_average = np.empty(self.prices.shape)
        self.simple_moving_average[: self.period - 1] = np.NaN
        for i in range(self.period - 1, len(self.prices)):
            self.simple_moving_average[i] = np.average(
                self.prices[i - self.period + 1 : i + 1]
            )

    def _compute_weighting_multiplier(self) -> None:
        """Calculate the weighting multiplier."""
        self.weighting_multiplier = self.smoothing_factor / (self.period + 1)

    def compute_exponential_moving_average(self) -> float:
        """
        Calculate the exponential moving average.

        Returns
        ----------
        exponential_moving_average : float
            The exponential moving average.
        """
        self._compute_simple_moving_average()
        self._compute_weighting_multiplier()
        self.exponential_moving_average = np.empty(self.prices.shape)
        self.exponential_moving_average[: self.period - 1] = np.NaN
        self.exponential_moving_average[self.period - 1] = self.simple_moving_average[
            self.period - 1
        ]
        for i in range(self.period, len(self.prices)):
            self.exponential_moving_average[i] = (
                self.weighting_multiplier
                * (self.prices[i] - self.exponential_moving_average[i - 1])
                + self.exponential_moving_average[i - 1]
            )
        return self.exponential_moving_average
