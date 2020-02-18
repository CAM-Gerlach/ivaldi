"""
Functions to write out collected monitoring data to a CSV file.
"""

# Standard library imports
import csv


CSV_PARAMS = {
    "extrasaction": "ignore",
    "dialect": "unix",
    "delimiter": ",",
    "quoting": csv.QUOTE_MINIMAL,
    "strict": False,
    }


def write_line_csv(data, out_file):
    """
    Write a line of data to a cSV, including the header if not already present.

    Parameters
    ----------
    data : dict
        Data to write to the CSV.
    out_file : io.IOBase
        An open file object to write to.

    Returns
    -------
    None.

    """
    csv_writer = csv.DictWriter(
        out_file, fieldnames=data.keys(), **CSV_PARAMS)
    if not out_file.tell():
        csv_writer.writeheader()
    csv_writer.writerow(data)
