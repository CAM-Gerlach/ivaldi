"""
Send and recieve sensor data over a serial link.
"""

# Standard library imports
import struct

# Third party imports
import serial

# Local imports
import ivaldi.devices.adafruit
import ivaldi.devices.raingauge
import ivaldi.monitor
import ivaldi.utils


DATA_FORMAT = "!fIfffffff"
END_BYTE = b"\n"

FREQUENCY_SEND = 10

SERIAL_PARAMS = {
    "baudrate": 9600,
    "parity": serial.PARITY_NONE,
    "stopbits": serial.STOPBITS_ONE,
    "bytesize": serial.EIGHTBITS,
    "timeout": 0.1,
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
    recieved_data = serial_port.read_until(END_BYTE).strip()
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
        if output_path is not None:
            with open(output_path, mode="a",
                      encoding="utf-8", newline="") as out_file:
                ivaldi.utils.run_periodic(recieve_data_packet)(
                    serial_port=serial_port,
                    output_file=out_file,
                    log=log,
                    )
        else:
            ivaldi.utils.run_periodic(recieve_data_packet)(
                serial_port=serial_port,
                log=log,
                )


def send_data_packet(raingauge_obj, pressure_obj, humidity_obj, serial_port):
    """
    Send an indiviudal data packet to a serial port.

    Parameters
    ----------
    raingauge_obj : ivaldi.devices.raingauge.TippingBucket
        Initialized rain gauge instance to retrieve data from.
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
        raingauge_obj.tips,
        raingauge_obj.rain_mm,
        raingauge_obj.rain_rate_mm_h(),
        pressure_obj.temperature,
        pressure_obj.pressure,
        pressure_obj.altitude,
        humidity_obj.temperature,
        humidity_obj.relative_humidity,
        ]
    data_packet = struct.pack(DATA_FORMAT, *data_to_pack) + END_BYTE
    serial_port.write(data_packet)


def send_monitoring_data(
        pin, serial_device="/dev/ttyAMA0", frequency=FREQUENCY_SEND):
    """
    Send continous monitoring data to a serial port.

    Parameters
    ----------
    pin : int
        The GPIO pin to use, in BCM numbering.
    serial_device : str, optional
        The serial device to read from. The default is "/dev/ttyAMA1".
    frequency : float, optional
        The frequency at which to update, in Hz. The default is 10 Hz.

    Returns
    -------
    None.

    """
    tipping_bucket = ivaldi.devices.raingauge.TippingBucket(pin=pin)
    pressure_sensor = ivaldi.devices.adafruit.AdafruitBMP280()
    humidity_sensor = ivaldi.devices.adafruit.AdafruitSHT31D()
    print("Sending data...")
    with serial.Serial(serial_device, **SERIAL_PARAMS) as serial_port:
        ivaldi.utils.run_periodic(send_data_packet)(
            raingauge_obj=tipping_bucket,
            pressure_obj=pressure_sensor,
            humidity_obj=humidity_sensor,
            serial_port=serial_port,
            frequency=frequency,
            )