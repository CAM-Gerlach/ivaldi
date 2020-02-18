"""
General utility functions for Ivaldi.
"""

# Standard library imports
import functools
import signal
import threading
import time


EXIT_EVENT = threading.Event()
FREQUENCY_DEFAULT = 1
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


def run_periodic(func):
    """Decorator to run a function at a periodic interval w/signal handling."""
    @functools.wraps(func)
    def _run_periodic(*args, frequency=FREQUENCY_DEFAULT, **kwargs):
        # Calculate sleep time
        sleep_time = SLEEP_TIME_MIN if frequency == 0 else 1 / frequency

        # Set up quit signal handler
        _set_signal_handler(_quit_handler)

        # Mainloop to measure tipping bucket
        while not EXIT_EVENT.is_set():
            func(*args, **kwargs)

            time_tosleep = sleep_time
            while not EXIT_EVENT.is_set() and time_tosleep > 0:
                time.sleep(min(SLEEP_TICK_S, time_tosleep))
                time_tosleep -= SLEEP_TICK_S

    return _run_periodic
