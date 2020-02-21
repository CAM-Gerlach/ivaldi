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
                ivaldi.monitor.VARIABLES.keys(), unpacked_data)}

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


def send_data_packet(serial_port, **sensor_kwargs):
    """
    Send an indiviudal data packet to a serial port.

    Parameters
    ----------
    serial_port : serial.Serial
        The serial port object to read from.

    Returns
    -------
    data_packet : bytes
        The encoded binary data send to the serial port.

    """
    data_to_pack = ivaldi.monitor.get_sensor_data(**sensor_kwargs)
    data_packet = struct.pack(DATA_FORMAT, *list(data_to_pack.values()))
    serial_port.write(data_packet)
    return data_packet


def send_monitoring_data(serial_device="/dev/ttyAMA0", **sensor_kwargs):
    """
    Send continous monitoring data to a serial port.

    Parameters
    ----------
    serial_device : str, optional
        The serial device to write to. The default is "/dev/ttyAMA0".

    Returns
    -------
    None.

    """
    sensor_args = ivaldi.monitor.setup_sensors(**sensor_kwargs)

    print("Sending data...")
    with serial.Serial(serial_device, **SERIAL_PARAMS) as serial_port:
        ivaldi.utils.run_periodic(send_data_packet)(
            **sensor_args, serial_port=serial_port)
