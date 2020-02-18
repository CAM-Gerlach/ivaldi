"""
Monitoring mainloop for Ivaldi.
"""

# Standard library imports
import sys

# Local imports
import ivaldi.devices.raingauge
import ivaldi.utils

# Script constants
FREQUENCY_DEFAULT = 10


def check_raingauge(raingauge_obj, log=False):
    """
    Get and print one sample from the rain gauge.

    Parameters
    ----------
    raingauge_obj : ivaldi.devices.raingauge.TippingBucket
        Initialized rain gauge instance to retrieve data from.
    log : bool, optional
        Whether to print every observation on a seperate line or update one.
        The default is False.

    Returns
    -------
    None.

    """
    output_strs = [
        f"{round(raingauge_obj.time_elapsed_s, 2):.2f} s elapsed",
        f"{raingauge_obj.tips} tips",
        f"{raingauge_obj.rain_mm:.1f} mm",
        f"{raingauge_obj.rain_rate_mm_h():.2f} mm/h",
        ]
    output_str = " | ".join(output_strs)
    if log:
        print(output_str)
    else:
        sys.stdout.write("\r" + output_str)
        sys.stdout.flush()


def monitor_raingauge(pin, frequency=FREQUENCY_DEFAULT, log=False):
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
    # Mainloop to measure tipping bucket
    tipping_bucket = ivaldi.devices.raingauge.TippingBucket(pin=pin)
    ivaldi.utils.run_periodic(check_raingauge)(
        raingauge_obj=tipping_bucket, frequency=frequency, log=log)
