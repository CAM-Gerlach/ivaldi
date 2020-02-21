"""
General utility functions for Ivaldi.
"""

# Standard library imports
import functools
import signal
import threading
import time


EXIT_EVENT = threading.Event()
PERIOD_S_DEFAULT = 1
SIGNALS_SET = ["SIG" + signame for signame in {"TERM", "HUP", "INT", "BREAK"}]
SLEEP_TICK_S = 0.5
SLEEP_TIME_MINIMUM = 0.01


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
    def _run_periodic(*args, period_s=PERIOD_S_DEFAULT, **kwargs):

        # Set up quit signal handler
        _set_signal_handler(_quit_handler)

        # Mainloop to measure tipping bucket
        while not EXIT_EVENT.is_set():
            wakeup_time = time.monotonic() + period_s

            func(*args, **kwargs)

            if wakeup_time <= time.monotonic():
                wakeup_time = time.monotonic() + SLEEP_TIME_MINIMUM
            while not EXIT_EVENT.is_set() and wakeup_time > time.monotonic():
                time.sleep(max(
                    min(SLEEP_TICK_S, wakeup_time - time.monotonic()), 0))

    return _run_periodic
