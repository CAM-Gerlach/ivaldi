"""
Measure a standard tipping bucket rain gauge in real time.
"""

# Standard library imports
import time

# Third party imports
import gpiozero


# General constants
CONVERSION_FACTOR = 1
PRECISION_DEFAULT = 2
S_IN_HR = 3600

# Rain gauge constants
MM_PER_TIP = 0.2
RAIN_PRECISION_MM = 1
RAIN_RATE_PRECISION_MM = 2


class CountDevice():
    """
    A generic counter device, connected via simple hi/lo GPIO.

    Parameters
    ----------
    pin : int
        The GPIO pin to use, in BCM numbering.
    conversion_factor : float, optional
        The conversion factor between the count and the processed output.
        The default is 1.

    """

    def __init__(self, pin, conversion_factor=CONVERSION_FACTOR):
        """See class docstring for full details."""
        self.pin = pin
        self.conversion_factor = conversion_factor
        self.count = 0
        self.count_times = []
        self.device = gpiozero.DigitalInputDevice(
            pin=self.pin, pull_up=True)
        self.device.when_activated = self._count
        self.start_time = time.monotonic()

    def _count(self):
        """Count one transition. Used as a callback."""
        self.count += 1
        self.count_times.append(time.monotonic())

    @property
    def time_elapsed_s(self):
        """The time elapsed, in s, since the start time was last reset."""
        return time.monotonic() - self.start_time

    @property
    def output_value_total(self):
        """When set, rounds to nearest count."""
        return round(self.count * self.conversion_factor, PRECISION_DEFAULT)

    @output_value_total.setter
    def output_value_total(self, output_value_total):
        self.count = round(output_value_total / self.conversion_factor)

    def output_value_average(self, period_s=None):
        """
        Get the output value, in counts per second, since the last reset.

        Returns
        -------
        output_value_average : float
            Output value averaged over the time since the last reset.

        """
        delta_t = time.monotonic() - self.start_time
        if period_s is None:
            period_s = delta_t
            output_value_period = self.output_value_total
        output_value_period = sum([
            1 for t in self.count_times if t > (time.monotonic() - period_s)])
        output_value_average = 0 if period_s <= 0 else round(
            (output_value_period / min([period_s, delta_t])),
            PRECISION_DEFAULT)
        return output_value_average

    def reset_count(self):
        """
        Reset just the count, leaving the start time intact.

        Returns
        -------
        None.

        """
        self.count = 0

    def reset_time(self):
        """
        Reset just the start time, leaving the count intact.

        Returns
        -------
        None.

        """
        self.start_time = time.monotonic()

    def reset(self):
        """
        Reset both the count and start time.

        Returns
        -------
        None.

        """
        self.reset_count()
        self.reset_time()


class TippingBucketRainGauge(CountDevice):
    """
    A tipping bucket rain gauge, connected via simple hi/lo GPIO.

    Parameters
    ----------
    pin : int, optional
        The GPIO pin to use, in BCM numbering.

    conversion_factor : float, optional
        The conversion factor between the count and the processed output.
        The default is 0.2 mm/tip.

    """

    def __init__(self, **count_args):
        """See class docstring for full details."""
        super().__init__(**{**{"conversion_factor": MM_PER_TIP}, **count_args})

    def output_value_average(self, period_s=None):
        """
        Get the output value, in counts per second, since the last reset.

        Specific to rain gauges, produces results in mm per hour, not per s.

        Returns
        -------
        output_value_average : float
            Output value averaged over the time since either reset or passed.

        """
        return super().output_value_average(period_s=period_s) * S_IN_HR
