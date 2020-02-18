"""
Measure a standard tipping bucket rain gauge in real time.
"""

# Standard library imports
import time

# Third party imports
import gpiozero


# Rain gauge constants
MM_PER_TIP = 0.2
RAIN_PRECISION_MM = 1
RAIN_RATE_PRECISION_MM = 2
S_IN_HR = 3600


class TippingBucket():
    """
    A tipping bucket rain gauge, connected via simple hi/lo GPIO.

    Parameters
    ----------
    pin : int, optional
        The GPIO pin to use, in BCM numbering. The default is 26.
    mm_per_tip : float, optional
        The conversion factor between mm and tips. The default is 0.2.

    """

    def __init__(self, pin, mm_per_tip=MM_PER_TIP):
        """See class docstring for full details."""
        self.pin = pin
        self.mm_per_tip = mm_per_tip
        self.tips = 0
        self.device = gpiozero.DigitalInputDevice(
            pin=self.pin, pull_up=True)
        self.device.when_activated = self._count_tip
        self.start_time = time.monotonic()

    def _count_tip(self):
        """Count a tip, incrementing the count by one. Used as a callback."""
        self.tips += 1

    @property
    def time_elapsed_s(self):
        """The time elapsed, in s, since the start time was last reset."""
        return time.monotonic() - self.start_time

    @property
    def rain_mm(self):
        """Total rain measured in mm. When set, rounds to nearest tip."""
        return round(self.tips * self.mm_per_tip, RAIN_PRECISION_MM)

    @rain_mm.setter
    def rain_mm(self, rain_mm):
        self.tips = round(rain_mm / self.mm_per_tip)

    def rain_rate_mm_h(self):
        """
        Get the calculated rain rate, in mm/hr, since the last reset.

        Returns
        -------
        rain_rate_mm_h : float
            Rain rate in mm/hr, averaged over the time since the last reset.

        """
        delta_s = time.monotonic() - self.start_time
        rain_rate_mm_h = 0 if delta_s <= 0 else round(
            (self.rain_mm / delta_s) * S_IN_HR, RAIN_RATE_PRECISION_MM)
        return rain_rate_mm_h

    def reset_count(self):
        """
        Reset just the tip count, leaving the start time intact.

        Returns
        -------
        None.

        """
        self.tips = 0

    def reset_time(self):
        """
        Reset just the start time, leaving the tip count intact.

        Returns
        -------
        None.

        """
        self.start_time = time.monotonic()

    def reset(self):
        """
        Reset both the tip count and start time.

        Returns
        -------
        None.

        """
        self.reset_count()
        self.reset_time()
