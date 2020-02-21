#!/usr/bin/env python3
"""
Command line interface for the Ivaldi IoT scientific sensor client.
"""

# Standard library imports
import argparse
import sys

# Local imports
import ivaldi
import ivaldi.monitor
import ivaldi.link


def generate_arg_parser():
    """
    Generate the argument parser for Ivaldi.

    Returns
    -------
    arg_parser : argparse.ArgumentParser
        The generated argument parser instance.

    """
    parser_main = argparse.ArgumentParser(
        description="A lightweight client for monitoring IoT sensors.",
        argument_default=argparse.SUPPRESS)
    parser_main.add_argument(
        "--version", action="store_true",
        help="Print the Ivaldi version and exit")
    subparsers = parser_main.add_subparsers(
        title="Commands", help="Subcommand to execute", metavar="Command")

    parser_monitor = subparsers.add_parser(
        "monitor", help="Monitor the sensor status and print to the terminal",
        argument_default=argparse.SUPPRESS)
    parser_monitor.set_defaults(func=ivaldi.monitor.monitor_sensors)

    parser_send = subparsers.add_parser(
        "send", help="Monitor the connected sensor and send the data via UART",
        argument_default=argparse.SUPPRESS)
    parser_send.set_defaults(func=ivaldi.link.send_monitoring_data)

    parser_recieve = subparsers.add_parser(
        "recieve", help="Recieve and print the IoT sensor data via UART",
        argument_default=argparse.SUPPRESS)
    parser_recieve.set_defaults(func=ivaldi.link.recieve_monitoring_data)

    for parser in [parser_monitor, parser_send]:
        parser.add_argument(
            "pin_rain", type=int,
            help="GPIO pin to use for rain gauge, in BCM (Broadcom) numbering")
        parser.add_argument(
            "pin_wind", type=int,
            help="GPIO pin to use for wind speed, in BCM (Broadcom) numbering")
        parser.add_argument(
            "channel_wind", type=int,
            help="ADC channel (0-3) to use for the wind direction sensor")
        parser.add_argument(
            "channel_soil", type=int,
            help="ADC channel (0-3) to use for the soil moisture sensor")
        parser.add_argument(
            "--period-s", type=float, help="Update period, in s")

    for parser in [parser_monitor, parser_recieve]:
        parser.add_argument(
            "--output-path", help="CSV file to output to, none if not passed")
        parser.add_argument(
            "--log", action="store_true",
            help="Print every update to a new line")

    for parser in [parser_send, parser_recieve]:
        parser.add_argument(
            "--serial-device",
            help="The UART device to use (e.g. '/dev/ttyAMA0')")

    return parser_main


def main():
    """
    Parse command line arguments and start the sensor monitor mainloop.

    Returns
    -------
    None.

    """
    arg_parser = generate_arg_parser()
    parsed_args = arg_parser.parse_args()

    if getattr(parsed_args, "version", None):
        print(f"Ivaldi version {ivaldi.__version__}")
        sys.exit()

    func_to_dispatch = parsed_args.func
    del parsed_args.func
    func_to_dispatch(**vars(parsed_args))


if __name__ == "__main__":
    main()
