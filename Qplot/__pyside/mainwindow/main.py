import argparse
import pandas as pd
import os

from PySide6.QtCore import QDateTime, QTimeZone


def transform_date(utc, timezone=None):
    utc_fmt = "yyyy-MM-ddTHH:mm:ss.zzzZ"
    new_date = QDateTime().fromString(utc, utc_fmt)
    if timezone:
        new_date.setTimeZone(timezone)
    return new_date

def read_data(fname):
    base = r'C:\Users\qarrion\Code\Qmodule\Qplot\__pyside\mainwindow'
    path = os.path.join(base,fname)
    # return pd.read_csv(path)
    
    df = pd.read_csv(path)
    # Remove wrong magnitudes
    df = df.drop(df[df.mag < 0].index)
    magnitudes = df["mag"]

    # My local timezone
    timezone = QTimeZone(b"Europe/Berlin")

    # Get timestamp transformed to our timezone
    times = df["time"].apply(lambda x: transform_date(x, timezone))

    return times, magnitudes

if __name__ == "__main__":
    options = argparse.ArgumentParser()
    options.add_argument("-f", "--file", type=str, required=True)
    args = options.parse_args()
    data = read_data(args.file)
    print(data)
