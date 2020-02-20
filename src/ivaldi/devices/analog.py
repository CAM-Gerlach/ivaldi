"""
Analog devices that need to be ADC converted.
"""

# Local imports
import ivaldi.devices.adafruit

# Wind direction constants
WIND_DEFAULT_OFFSET = 4.66
WIND_DEFAULT_SCALE = 0.013113

# Wind direction constants
SOIL_DEFAULT_OFFSET = 0
SOIL_DEFAULT_SCALE = 1


class AnalogMeasurementMixin():
    """
    Class for an analog measurement sensor device.

    Parameters
    ----------
    scale : numeric, optional
        The value to scale the output by. The default is 1.
    offset : numeric, optional
        The value to offset the output by. The default is 0.

    """

    def __init__(self, scale=1, offset=0, **adc_args):
        """See class docstring for full details."""
        super().__init__(**adc_args)
        self.scale = scale
        self.offset = offset

    @property
    def value(self):
        """The value of the quantity measured, in physical units."""
        return self.raw_value * self.scale + self.offset


class AnemometerDirection(AnalogMeasurementMixin,
                          ivaldi.devices.adafruit.AdafruitADS1115):
    """
    Class for an analog wind direction sensor.

    Parameters
    ----------
    scale : numeric, optional
        The value to scale the output by. The default is 0.013113.
    offset : numeric, optional
        The value to offset the output by. The default is 4.66.

    """

    def __init__(
            self,
            scale=WIND_DEFAULT_SCALE,
            offset=WIND_DEFAULT_OFFSET,
            **adc_args,
            ):  # pylint: disable=C0330
        """See class docstring for full details."""
        super().__init__(scale=scale, offset=offset, **adc_args)


class SoilMoisture(AnalogMeasurementMixin,
                   ivaldi.devices.adafruit.AdafruitADS1115):
    """
    Class for an analog soil moisture sensor.

    Parameters
    ----------
    scale : numeric, optional
        The value to scale the output by. The default is 1.
    offset : numeric, optional
        The value to offset the output by. The default is 0.

    """

    def __init__(
            self,
            scale=SOIL_DEFAULT_SCALE,
            offset=SOIL_DEFAULT_OFFSET,
            **adc_args,
            ):  # pylint: disable=C0330
        """See class docstring for full details."""
        super().__init__(scale=scale, offset=offset, **adc_args)
