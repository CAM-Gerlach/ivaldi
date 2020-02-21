"""
Send and recieve sensor data over a serial link.
"""

# Standard library imports
import struct

# Third party imports
import serial

# Local imports
import ivaldi.devices.adafruit
import ivaldi.devices.analog
import ivaldi.devices.counter
import ivaldi.monitor
import ivaldi.utils


DATA_FORMAT = "!12fI"

PERIOD_S_DEFAULT = 1

SERIAL_PARAMS = {
    "baudrate": 9600,
    "parity": serial.PARITY_NONE,
    "stopbits": serial.STOPBITS_ONE,
    "bytesize": serial.EIGHTBITS,
    "timeout": 1,
    }


def recieve_data_packet(serial_port, output_file=None, log=False):
    """
    Recieve and print an individual data packet from a serial port.

    Parameters
    ----------
    serial_port : serial.Serial
        The serial port object to read from.
    output_file : io.IOBase or None
        File object to output the data to. If None, prints to the screen.
    log : bool, optional
        If true, will log every update on a seperate line;
        updates one line otherwise. The default is False.

    Returns
    -------
    unpacked_data : tuple or None
        The unpacked and decoded data recieved, if any; else None.

    """
    recieved_data = serial_port.read(size=struct.calcsize(DATA_FORMAT))
    if not recieved_data:
        return None
    try:
        unpacked_data = struct.unpack(DATA_FORMAT, recieved_data)
    # Ignore errors reading the data and continue
    except struct.error:
        pass
    else:
        ivaldi.monitor.pretty_print_data(*unpacked_data, log=log)

        sensor_data_dict = {
            key: value for key, value in zip(
                ivaldi.monitor.VARIABLE_NAMES, unpacked_data)}

        if output_file is not None:
            ivaldi.output.write_line_csv(
                sensor_data_dict, out_file=output_file)

        return sensor_data_dict


def recieve_monitoring_data(
        serial_device="/dev/ttyAMA1", output_path=None, log=False):
    """
    Recieve continous monitoring data from a serial port.

    Parameters
    ----------
    serial_device : str, optional
        The serial device to read from. The default is "/dev/ttyAMA1".
    output_path : str or pathlib.Path
        Path to output the data to. If None, prints to the screen.
    log : bool, optional
        If true, will log every update on a seperate line;
        updates one line otherwise. The default is False.

    Returns
    -------
    None.

    """
    print("Recieving data...")
    with serial.Serial(serial_device, **SERIAL_PARAMS) as serial_port:
        recieve_args = {
            "serial_port": serial_port,
            "period_s": 0,
            "log": log
            }
        if output_path is not None:
            with open(output_path, mode="a",
                      encoding="utf-8", newline="") as out_file:
                ivaldi.utils.run_periodic(recieve_data_packet)(
                    output_file=out_file, **recieve_args)
        else:
            ivaldi.utils.run_periodic(recieve_data_packet)(**recieve_args)


def send_data_packet(raingauge_obj, windspeed_obj, winddir_obj,
                     soiltemperature_obj, soilmoisture_obj,
                     pressure_obj, humidity_obj,
                     serial_port):
    """
    Send an indiviudal data packet to a serial port.

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
    serial_port : serial.Serial
        The serial port object to read from.

    Returns
    -------
    None.

    """
    data_to_pack = [
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
    data_packet = struct.pack(DATA_FORMAT, *data_to_pack)
    serial_port.write(data_packet)


def send_monitoring_data(
        pin_rain, pin_wind, channel_wind, channel_soil,
        serial_device="/dev/ttyAMA0",
        period_s=PERIOD_S_DEFAULT,
        ):
    """
    Send continous monitoring data to a serial port.

    Parameters
    ----------
    pin_rain : int
        The GPIO pin to use for the rain gauge, in BCM numbering.
    pin_wind : int
        The GPIO pin to use for the anemometer, in BCM numbering.
    serial_device : str, optional
        The serial device to read from. The default is "/dev/ttyAMA1".
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
    print("Sending data...")
    with serial.Serial(serial_device, **SERIAL_PARAMS) as serial_port:
        ivaldi.utils.run_periodic(send_data_packet)(
            raingauge_obj=rain_gauge,
            windspeed_obj=anemometer_speed,
            winddir_obj=anemometer_direction,
            soiltemperature_obj=soil_temperature,
            soilmoisture_obj=soil_moisture,
            pressure_obj=pressure_sensor,
            humidity_obj=humidity_sensor,
            serial_port=serial_port,
            period_s=period_s,
            )
