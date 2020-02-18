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


def pretty_print_raingauge(
        time_elapsed_s, tips, rain_mm, rain_rate_mm_h, log=False):
    """
    Pretty print the raingauge data to the terminal.

    Parameters
    ----------
    time_elapsed_s : numeric
        Seconds elapsed since the beginning of observations.
    tips : int
        Number of rain gauge bucket tips.
    rain_mm : numeric
        Rain recorded, in mm.
    rain_rate_mm_h : numeric
        Average rain rate over observing period, in mm/h.
    log : bool, optional
        Log every observation instead of just updating one line.
        The default is False.

    Returns
    -------
    output_str : str
        Pretty-printed output string.

    """
    output_strs = [
        f"{time_elapsed_s:.2f} s elapsed",
        f"{tips} tips",
        f"{rain_mm:.1f} mm",
        f"{rain_rate_mm_h:.2f} mm/h",
        ]
    output_str = " | ".join(output_strs)
    if log:
        print(output_str)
    else:
        sys.stdout.write("\r" + output_str)
        sys.stdout.flush()

    return output_str


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
    pretty_print_raingauge(
        time_elapsed_s=raingauge_obj.time_elapsed_s,
        tips=raingauge_obj.tips,
        rain_mm=raingauge_obj.rain_mm,
        rain_rate_mm_h=raingauge_obj.rain_rate_mm_h(),
        log=log,
        )


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
        raingauge_obj=tipping_bucket,
        frequency=frequency,
        log=log,
        )
