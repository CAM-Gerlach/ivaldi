"""
Monitoring mainloop for Ivaldi.
"""

# Standard library imports
import sys

# Local imports
import ivaldi.devices.adafruit
import ivaldi.devices.analog
import ivaldi.devices.counter
import ivaldi.devices.onewire
import ivaldi.output
import ivaldi.utils


PERIOD_S_DEFAULT = 1

VARIABLES = {
    "time_elapsed_s": "{:.1f}s",
    "temperature_bmp280_C": "{:.2f}C",
    "pressure_hPa": "{:.2f}hPa",
    "altitude_m": "{:.2f}m",
    "temperature_sht31d_C": "{:.2f}C",
    "relative_humidity": "{:.2f}%",
    "wind_gust_m_s_3s": "{:.2f}m/s(3s)",
    "wind_sustained_m_s_10min": "{:.2f}m/s(10min)",
    "wind_direction_deg_n": "{:.1f}deg",
    "rain_mm": "{:.1f}mm",
    "rain_rate_mm_h": "{:.2f}mm/h(5min)",
    "soil_temperature_C": "{:.2f}C",
    "soil_moisture_raw": "{}",
    }


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
    output_str = "|".join(VARIABLES.values())
    output_str = output_str.format(*data_to_print)

    if log:
        print(output_str)
    else:
        sys.stdout.write("\r" + output_str)
        sys.stdout.flush()

    return output_str


def get_sensor_data(raingauge_obj, windspeed_obj, winddir_obj,
                    soiltemperature_obj, soilmoisture_obj,
                    pressure_obj, humidity_obj):
    """
    Get observations from each sensor.

    Parameters
    ----------
    raingauge_obj : ivaldi.devices.counter.TippingBucketRainGauge
        Initialized rain gauge instance to retrieve data from.
    windspeed_obj : ivaldi.devices.counter.AnemometerSpeed
        Initialized anemometer speed instance to retrieve data from.
    winddir_obj : ivaldi.devices.analog.AnemometerDirection
        Initialized anemometer direction instance to retrieve data from.
    soiltemperature_obj : ivaldi.devices.onewire.MaximDS18B20
        Initialized soil temperature sensor instance to retrieve data from.
    soilmoisture_obj : ivaldi.devices.analog.SoilMoisture
        Initialized soil moisture sensor instance to retrieve data from.
    pressure_obj : ivaldi.devices.adafruit.AdafruitBMP280
        Initialized adafruit pressure sensor to retrieve data from.
    humidity_obj : ivaldi.devices.adafruit.AdafruitSHT31D
        Initialized adafruit humidity sensor to retrieve data from.

    Returns
    -------
    None.

    """
    sensor_data = [
        raingauge_obj.time_elapsed_s,
        pressure_obj.temperature,
        pressure_obj.pressure,
        pressure_obj.altitude,
        humidity_obj.temperature,
        humidity_obj.relative_humidity,
        windspeed_obj.output_value_average(period_s=3),
        windspeed_obj.output_value_average(period_s=60 * 10),
        winddir_obj.value,
        raingauge_obj.output_value_total,
        raingauge_obj.output_value_average(),
        soiltemperature_obj.value,
        soilmoisture_obj.value,
        ]

    sensor_data = {
        key: value for key, value in zip(VARIABLES.keys(), sensor_data)}

    return sensor_data


def get_monitoring_data(output_file=None, log=False, **sensor_kwargs):
    """
    Get and print one sample from the sensors.

    Parameters
    ----------
    output_file : io.IOBase or None
        File object to output the data to. If None, prints to the screen.
    log : bool, optional
        Whether to print every observation on a seperate line or update one.
        The default is False.

    Returns
    -------
    None.

    """
    sensor_data = get_sensor_data(**sensor_kwargs)

    pretty_print_data(log=log, *list(sensor_data.values()))

    if output_file is not None:
        ivaldi.output.write_line_csv(sensor_data, out_file=output_file)

    return sensor_data


def setup_sensors(pin_rain, pin_wind, channel_wind, channel_soil,
                  period_s=PERIOD_S_DEFAULT):
    """
    Mainloop for continously reporting key metrics from the rain gauge.

    Parameters
    ----------
    pin_rain : int
        The GPIO pin to use for the rain gauge, in BCM numbering.
    pin_wind : int
        The GPIO pin to use for the anemometer, in BCM numbering.
    channel_wind : int
        The ADC channel (0-3) to use for the wind direction sensor.
    channel_soil : int
        The ADC channel (0-3) to use for the soil moisture sensor.
    period_s : float, optional
        The period at which to update, in s. The default is 1 s.

    Returns
    -------
    None.

    """
    rain_gauge = ivaldi.devices.counter.TippingBucketRainGauge(pin=pin_rain)
    anemometer_speed = ivaldi.devices.counter.AnemometerSpeed(pin=pin_wind)
    anemometer_direction = ivaldi.devices.analog.AnemometerDirection(
        channel=channel_wind)
    soil_temperature = ivaldi.devices.onewire.MaximDS18B20()
    soil_moisture = ivaldi.devices.analog.SoilMoisture(
        channel=channel_soil)
    pressure_sensor = ivaldi.devices.adafruit.AdafruitBMP280()
    humidity_sensor = ivaldi.devices.adafruit.AdafruitSHT31D()

    sensor_args = {
        "raingauge_obj": rain_gauge,
        "windspeed_obj": anemometer_speed,
        "winddir_obj": anemometer_direction,
        "soiltemperature_obj": soil_temperature,
        "soilmoisture_obj": soil_moisture,
        "pressure_obj": pressure_sensor,
        "humidity_obj": humidity_sensor,
        "period_s": period_s,
        }

    return sensor_args


def start_monitoring(output_path=None, log=False, **sensor_kwargs):
    """
    Mainloop for continously reporting key metrics from the rain gauge.

    Parameters
    ----------
    output_path : str or pathlib.Path
        Path to output the data to. If None, prints to the screen.
    log : bool, optional
        If true, will log every update on a seperate line;
        updates one line otherwise. The default is False.

    Returns
    -------
    None.

    """
    # Mainloop to measure tipping bucket
    sensor_args = setup_sensors(**sensor_kwargs)
    sensor_args["log"] = log
    if output_path is not None:
        with open(output_path, "a", encoding="utf-8", newline="") as out_file:
            ivaldi.utils.run_periodic(get_monitoring_data)(
                **sensor_args, output_file=out_file)
    else:
        ivaldi.utils.run_periodic(get_monitoring_data)(**sensor_args)
