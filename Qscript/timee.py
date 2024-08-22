
from datetime import datetime
from typing import Literal

delta = datetime.now() - datetime(2020,1,1,0,0,0)
# delta = datetime(2021,1,1,0,0,0) - datetime(2020,1,1,0,0,0)

total_minutes = delta.total_seconds() / 60

total_seconds = total_minutes / 200

print(f"{total_minutes = }")
print(f"{total_seconds = }")

hint = Literal['day','hour','minute']
def divider(dividend, divisor:int|hint):
    """
    + day = 1*60*60*24
    + hour = 1*60*60
    + minute = 1*60
    >>> # return quotient, remainder"""
    if isinstance(divisor,str): 
        time_dict = dict(
            day = 1*60*60*24,
            hour = 1*60*60,
            minute = 1*60 )
        divisor = time_dict[divisor]

    quotient = dividend // divisor
    remainder = dividend % divisor
    return quotient, remainder

print(divider(total_seconds,1*60*60*24))

days, d = divider(total_seconds,'day')
hours, d = divider(d,'hour')
minutes, seconds = divider(d,'minute')

print(f"{days}D {hours}H {minutes}M {seconds}S")