"""
Adafruit I2C weather sensor devices.
"""

# Third party imports
import board
import busio
import adafruit_bmp280
import adafruit_sht31d


class AdafruitBMP280(adafruit_bmp280.Adafruit_BMP280_I2C):
    """A thin shim on top of the Adafruit BMP280 pressure sensor class."""

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        super().__init__(i2c)


class AdafruitSHT31D(adafruit_sht31d.SHT31D):
    """A thin shim on top of the Adafruit SHT31 humidity sensor class."""

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        super().__init__(i2c)
