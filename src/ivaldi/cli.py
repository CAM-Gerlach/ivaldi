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
    parser_monitor.add_argument(
        "pin", type=int, help="GPIO pin to use, in SoC (Broadcom) numbering")
    parser_monitor.add_argument(
        "--frequency", type=float, help=f"Update frequency, in Hz")
    parser_monitor.add_argument(
        "--log", action="store_true", help=f"Print every update to a new line")
    parser_monitor.set_defaults(fn=ivaldi.monitor.monitor_raingauge)

    return parser_main


def main():
    """
    Parse command line arguments and start the rain gauge monitor mainloop.

    Returns
    -------
    None.

    """
    arg_parser = generate_arg_parser()
    parsed_args = arg_parser.parse_args()

    if getattr(parsed_args, "version", None):
        print(f"Ivaldi version {ivaldi.__version__}")
        sys.exit()

    fn_to_dispatch = parsed_args.fn
    del parsed_args.fn
    fn_to_dispatch(**vars(parsed_args))


if __name__ == "__main__":
    main()
