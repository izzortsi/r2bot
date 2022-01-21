"""Computes the true range for a given time t."""


class TrueRange:
    """Computes the true range for a given time t."""

    # noinspection PyMethodMayBeStatic
    def method1(self, current_high: float, current_low: float):
        """
        First method of true range, which computes the difference between the current high and the current low.

        Parameters
        ----------
        current_high : float
            Current high for a given time t.
        current_low : float
            Current low for a given time t.

        Returns
        -------
        _ : float
            Difference between current high and current low.
        """
        return current_high - current_low

    # noinspection PyMethodMayBeStatic
    def method2(self, current_high: float, previous_close: float):
        """
        Second method of true range, which computes the absolute difference between the current high and the previous close.

        Parameters
        ----------
        current_high : float
            Current high for a given time t.
        previous_close : float
            Close price for a given time t - 1.

        Returns
        -------
        _ : float
            Absolute difference between current high and previous close.
        """
        return abs(current_high - previous_close)

    # noinspection PyMethodMayBeStatic
    def method3(self, current_low: float, previous_close: float):
        """
        Third method of true range, which computes the absolute difference between the current low and the previous close.

        Parameters
        ----------
        current_low : float
            Current low for a given time t.
        previous_close : float
            Close price for a given time t - 1.

        Returns
        -------
        _ : float
            Absolute difference between current low and previous close.
        """
        return abs(current_low - previous_close)

    def true_range(
        self, current_high: float, current_low: float, previous_close: float
    ):
        """
        Compute the maximum between the 3 different methods above, which is the true range.

        Parameters
        ----------
        current_high : float
            Current high for a given time t.
        current_low : float
            Current low for a given time t.
        previous_close : float
            Close price for a given time t - 1.

        Returns
        -------
        _ : float
            Maximum value between the 3 methods above.
        """
        return max(
            self.method1(current_high, current_low),
            self.method2(current_high, previous_close),
            self.method3(current_low, previous_close),
        )
