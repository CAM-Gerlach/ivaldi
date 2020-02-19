"""
Analog devices that need to be ADC converted.
"""

# Third party imports
import adafruit_ads1x15.ads1115
import adafruit_ads1x15.analog_in

# Local imports
import ivaldi.devices.adafruit


WIND_DEFAULT_OFFSET = 4.66
WIND_DEFAULT_SCALE = 0.013113


class AnemometerDirection():
    """
    Class for an analog wind direction sensor.

    Parameters
    ----------
    scale : numeric, optional
        The value to scale the output by. The default is 0.013113.
    offset : numeric, optional
        The value to offset the output by. The default is 4.66.

    Returns
    -------
    None.

    """

    def __init__(self, scale=WIND_DEFAULT_SCALE, offset=WIND_DEFAULT_OFFSET):
        """See class docstring for full details."""
        self.scale = scale
        self.offset = offset
        self._adc = adafruit_ads1x15.analog_in.AnalogIn(
            ivaldi.devices.adafruit.AdafruitADS1115(),
            adafruit_ads1x15.ads1115.P0)

    @property
    def voltage(self):
        """The voltage reported by the ADC, in volts."""
        return self._adc.voltage

    @property
    def value_raw(self):
        """The raw value reported by the ADC, as a 16-bit integer."""
        return self._adc.value

    @property
    def value(self):
        """The value of the direction, in degrees from north."""
        return self._adc.value * self.scale + self.offset
