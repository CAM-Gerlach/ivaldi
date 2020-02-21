"""
Sensor devices using the 1-wire communications protocol.
"""

# Standard library imports
from pathlib import Path


# General constants
EQUALS_STRING = "="
ONEWIRE_BASE_PATH = Path("/sys/bus/w1/devices")
SLAVE_DIR = Path("w1_slave")
YES_OFFSET_END = -3
YES_STRING = "YES"

# DS18B20 temperature sensor  constants
DS18B20_FAMILY = 28
DS18B20_OFFSET = 0
DS18B20_SCALE = 1 / 1000


class OneWireDevice:
    """
    A 1-wire scientific sensor device.

    Parameters
    ----------
    family : int or str
        Integeger or string with the device family ID to search for.
    index : int, optional
        The index number of the onewire device to find. The default is 0.
    scale : numeric, optional
        The value to scale the raw output by. The default is 1.
    offset : numeric, optional
        The value to offset the raw output by. The default is 0.

    """

    def __init__(self, family, index=0, scale=1, offset=0):
        """See class docstring for full information."""
        self._device_path = (
            list(ONEWIRE_BASE_PATH.glob(str(family) + "*"))[index]
            / SLAVE_DIR)
        self.scale = scale
        self.offset = offset

    def _get_raw_data(self):
        """Get the raw data recieved from the device as a list of strings."""
        with open(self._device_path, "r", encoding="utf-8") as device_file:
            raw_data = device_file.readlines()
        return raw_data

    @property
    def raw_value(self):
        """The raw value reported by the sensor, as a 16-bit integer."""
        raw_data = self._get_raw_data()
        if raw_data[0].strip()[YES_OFFSET_END:] != YES_STRING:
            return None
        raw_data_split = raw_data[1].split(EQUALS_STRING)
        if len(raw_data_split) != 2:
            return None
        raw_value = float(raw_data_split[1].strip())
        return raw_value

    @property
    def value(self):
        """The value of the quantity measured, in physical units."""
        return self.raw_value * self.scale + self.offset


class MaximDS18B20(OneWireDevice):
    """
    A Maxim DS18B20 soil temperature sensor.

    Parameters
    ----------
    family : int or str
        Integeger or string with the device family ID to search for.
        The default is 28.
    index : int, optional
        The index number of the onewire device to find. The default is 0.
    scale : numeric, optional
        The value to scale the raw output by. The default is 0.001.
    offset : numeric, optional
        The value to offset the raw output by. The default is 0.

    """

    def __init__(self, family=DS18B20_FAMILY,
                 scale=DS18B20_SCALE, offset=DS18B20_SCALE, **onewire_kwargs):
        """See class docstring."""
        super().__init__(
            family=family, scale=scale, offset=offset, **onewire_kwargs)
