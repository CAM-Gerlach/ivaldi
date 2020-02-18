#!/usr/bin/env python3
"""
Monitoring mainloop for Ivaldi.
"""

# Standard library imports
import argparse
import signal
import sys
import threading
import time

# Local imports
import ivaldi.devices.raingauge


# Script constants
EXIT_EVENT = threading.Event()
FREQ_DEFAULT = 10
SIGNALS_SET = ["SIG" + signame for signame in {"TERM", "HUP", "INT", "BREAK"}]
SLEEP_TICK_S = 0.5
SLEEP_TIME_MIN = 0.01


def _quit_handler(signo, _frame):
    """Signal handler that prints a message and sets an event."""
    print(f"\nInterrupted by signal {signo}; terminating.")
    EXIT_EVENT.set()


def _set_signal_handler(signal_handler, signals=SIGNALS_SET):
    """Helper function that sets a signal handler for the given signals."""
    for signal_type in signals:
        try:
            signal.signal(getattr(signal, signal_type), signal_handler)
        except AttributeError:  # Windows doesn't have SIGHUP
            continue


def monitor_raingauge(pin, frequency=FREQ_DEFAULT, log=False):
    """
    Mainloop for continously reporting key metrics from the rain gauge.

    Parameters
    ----------
    pin : int
        The GPIO pin to use, in BCM numbering.
    frequency : float, optional
        The frequency at which to update, in Hz. The default is 10 Hz.
    log : bool, optional
        If true, will log every update on a seperate line;
        updates one line otherwise. The default is False.

    Returns
    -------
    None.

    """
    # Calculate sleep time
    sleep_time = SLEEP_TIME_MIN if frequency == 0 else 1 / frequency

    # Set up quit signal handler
    _set_signal_handler(_quit_handler)

    # Mainloop to measure tipping bucket
    tipping_bucket = ivaldi.devices.raingauge.TippingBucket(pin=pin)
    while not EXIT_EVENT.is_set():
        output_strs = [
            f"{round(tipping_bucket.time_elapsed_s, 2):.2f} s elapsed",
            f"{tipping_bucket.tips} tips",
            f"{tipping_bucket.rain_mm:.1f} mm",
            f"{tipping_bucket.rain_rate_mm_h():.2f} mm/h",
            ]
        output_str = " | ".join(output_strs)
        if log:
            print(output_str)
        else:
            sys.stdout.write("\r" + output_str)
            sys.stdout.flush()

        time_tosleep = sleep_time
        while not EXIT_EVENT.is_set() and time_tosleep > 0:
            time.sleep(min(SLEEP_TICK_S, time_tosleep))
            time_tosleep -= SLEEP_TICK_S


def main():
    """
    Parse command line arguments and start the rain gauge monitor mainloop.

    Returns
    -------
    None.

    """
    arg_parser = argparse.ArgumentParser(
        description="Simple monitor of a tipping bucket rain gauge",
        argument_default=argparse.SUPPRESS)
    arg_parser.add_argument(
        "pin", type=int, help="GPIO pin to use, in SoC (Broadcom) numbering")
    arg_parser.add_argument(
        "--frequency", type=float, help=f"Update freq, default {FREQ_DEFAULT}")
    arg_parser.add_argument(
        "--log", action="store_true", help=f"Print every update to a new line")
    parsed_args = arg_parser.parse_args()

    monitor_raingauge(**vars(parsed_args))


if __name__ == "__main__":
    main()
