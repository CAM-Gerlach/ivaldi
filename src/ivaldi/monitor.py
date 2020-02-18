"""
Monitoring mainloop for Ivaldi.
"""

# Standard library imports
import sys

# Local imports
import ivaldi.devices.adafruit
import ivaldi.devices.raingauge
import ivaldi.utils

# Script constants
FREQUENCY_DEFAULT = 10


def pretty_print_data(*data_to_print, log=False):
    """
    Pretty print the raingauge data to the terminal.

    Parameters
    ----------
    log : bool, optional
        Log every observation instead of just updating one line.
        The default is False.
    data_to_print : dict
        The keys to pass to the data printing function.

    Returns
    -------
    output_str : str
        Pretty-printed output string.

    """
    output_strs = [
        "{:.2f} s",
        "{} tips",
        "{:.1f} mm",
        "{:.2f} mm/h",
        "{:.2f} C",
        "{:.2f} hPa",
        "{:.2f} m",
        "{:.2f} C",
        "{:.2f} %",
        ]
    output_str = " | ".join(output_strs)
    output_str = output_str.format(*data_to_print)

    if log:
        print(output_str)
    else:
        sys.stdout.write("\r" + output_str)
        sys.stdout.flush()

    return output_str


def get_sensor_data(raingauge_obj, pressure_obj, humidity_obj, log=False):
    """
    Get and print one sample from the sensors.

    Parameters
    ----------
    raingauge_obj : ivaldi.devices.raingauge.TippingBucket
        Initialized rain gauge instance to retrieve data from.
    pressure_obj : ivaldi.devices.adafruit.AdafruitBMP280
        Initialized adafruit pressure sensor to retrieve data from.
    humidity_obj : ivaldi.devices.adafruit.AdafruitSHT31D
        Initialized adafruit humidity sensor to retrieve data from.
    log : bool, optional
        Whether to print every observation on a seperate line or update one.
        The default is False.

    Returns
    -------
    None.

    """
    sensor_data = [
        raingauge_obj.time_elapsed_s,
        raingauge_obj.tips,
        raingauge_obj.rain_mm,
        raingauge_obj.rain_rate_mm_h(),
        pressure_obj.temperature,
        pressure_obj.pressure,
        pressure_obj.altitude,
        humidity_obj.temperature,
        humidity_obj.relative_humidity,
        ]

    pretty_print_data(log=log, *sensor_data)

    return sensor_data


def monitor_sensors(pin, frequency=FREQUENCY_DEFAULT, log=False):
    """
    Mainloop for continously reporting key metrics from the rain gauge.

    Parameters
    ----------
    pin : int
        The GPIO pin to use for the rain gauge, in BCM numbering.
    frequency : float, optional
        The frequency at which to update, in Hz. The default is 10 Hz.
    log : bool, optional
        If true, will log every update on a seperate line;
        updates one line otherwise. The default is False.

    Returns
    -------
    None.

    """
    # Mainloop to measure tipping bucket
    tipping_bucket = ivaldi.devices.raingauge.TippingBucket(pin=pin)
    pressure_sensor = ivaldi.devices.adafruit.AdafruitBMP280()
    humidity_sensor = ivaldi.devices.adafruit.AdafruitSHT31D()
    ivaldi.utils.run_periodic(get_sensor_data)(
        raingauge_obj=tipping_bucket,
        pressure_obj=pressure_sensor,
        humidity_obj=humidity_sensor,
        frequency=frequency,
        log=log,
        )
