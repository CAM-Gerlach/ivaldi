#!/usr/bin/env python3
"""
Measure a standard tipping bucket rain gauge in real time.
"""

# Standard library imports
import argparse
import signal
import threading
import time
import sys

# Third party imports
import gpiozero


# Rain gauge constants
MM_PER_TIP = 0.2
RAIN_PRECISION_MM = 1
RAIN_RATE_PRECISION_MM = 2
S_IN_HR = 3600

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


class TippingBucket():
    """
    A tipping bucket rain gauge, connected via simple hi/lo GPIO.

    Parameters
    ----------
    pin : int, optional
        The GPIO pin to use, in BCM numbering. The default is 26.
    mm_per_tip : float, optional
        The conversion factor between mm and tips. The default is 0.2.

    """

    def __init__(self, pin, mm_per_tip=MM_PER_TIP):
        self.pin = pin
        self.mm_per_tip = mm_per_tip
        self.tips = 0
        self.device = gpiozero.DigitalInputDevice(
            pin=self.pin, pull_up=True)
        self.device.when_activated = self._count_tip
        self.start_time = time.monotonic()

    def _count_tip(self):
        """Count a tip, incrementing the count by one. Used as a callback."""
        self.tips += 1

    @property
    def time_elapsed_s(self):
        """The time elapsed, in s, since the start time was last reset."""
        return time.monotonic() - self.start_time

    @property
    def rain_mm(self):
        """Total rain measured in mm. When set, rounds to nearest tip."""
        return round(self.tips * self.mm_per_tip, RAIN_PRECISION_MM)

    @rain_mm.setter
    def rain_mm(self, rain_mm):
        self.tips = round(rain_mm / self.mm_per_tip)

    def rain_rate_mm_h(self):
        """
        Get the calculated rain rate, in mm/hr, since the last reset.

        Returns
        -------
        rain_rate_mm_h : float
            Rain rate in mm/hr, averaged over the time since the last reset.

        """
        delta_s = time.monotonic() - self.start_time
        rain_rate_mm_h = 0 if delta_s <= 0 else round(
            (self.rain_mm / delta_s) * S_IN_HR, RAIN_RATE_PRECISION_MM)
        return rain_rate_mm_h

    def reset_count(self):
        """
        Reset just the tip count, leaving the start time intact.

        Returns
        -------
        None.

        """
        self.tips = 0

    def reset_time(self):
        """
        Reset just the start time, leaving the tip count intact.

        Returns
        -------
        None.

        """
        self.start_time = time.monotonic()

    def reset(self):
        """
        Reset both the tip count and start time.

        Returns
        -------
        None.

        """
        self.reset_count()
        self.reset_time()


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
    tipping_bucket = TippingBucket(pin=pin)
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
