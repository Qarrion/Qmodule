from datetime import datetime, timezone,timedelta
from typing import Literal
import pytz

class TimeFormat:
    
    kst = timezone(timedelta(hours=9))

    @classmethod
    def seconds(cls, seconds:float,fmt:Literal['hmsf','ms7f']='hmsf'):
        seconds_sign = '+' if seconds >= 0 else '-'
        assert seconds_sign == '+', 'invalid sign'
        seconds_hms = abs(seconds)
        seconds_hours, remainder = divmod(seconds_hms, 3600)
        seconds_minutes, seconds = divmod(remainder, 60)
        seconds_seconds, microsecond = divmod(seconds, 1)
        if fmt == 'hmsf':
            microsecond = round(microsecond * 1000,0)
            secondsTimeFormatted = (
                # f"{seconds_sign}{int(seconds_hours):02}:{int(seconds_minutes):02}:"
                f"{int(seconds_hours):02}:{int(seconds_minutes):02}:"
                f"{int(seconds_seconds):02}.{int(microsecond):03}"
            )
        elif fmt =='ms7f':
            microsecond = round(microsecond * 1000000,0)
            secondsTimeFormatted = (
                # f"{seconds_sign}{int(seconds_hours):02}:{int(seconds_minutes):02}:"
                f":{int(seconds_seconds):02}.{int(microsecond):06}"
            )
        return secondsTimeFormatted
    
    @classmethod
    def datetime(cls, datetime_naive:datetime, fmt:Literal['full','hmsf','ms7f','short']):
        assert datetime_naive.tzinfo is None, "aware invalid"
        if fmt == 'full':
            formatted_time = datetime_naive.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        elif fmt=='short':
            formatted_time = datetime_naive.strftime("%y.%m.%d %H:%M") 
        elif fmt=='hmsf':
            formatted_time = datetime_naive.strftime('%H:%M:%S.%f')[:-3] 
        elif fmt=='ms7f':
            formatted_time = datetime_naive.strftime(':%S.%f') 
        return formatted_time
    
    @classmethod    
    def timestamp(cls, timestamp:datetime, fmt:Literal['full','hmsf','ms7f','short']):
        datetime_naive = cls._from_stamp(timestamp).replace(tzinfo=None)
        return cls.datetime(datetime_naive, fmt)
    
    @classmethod
    def _from_stamp(cls, stamp:float):
        stamp = cls._to_ten_digit(stamp)
        date_time = datetime.fromtimestamp(stamp, cls.kst)
        return date_time

    def _to_ten_digit(stamp_like:float):
        num_digits = len(str(int(stamp_like))) 
        if num_digits <= 10:
            stamp = stamp_like
        else :
            divisor = 10 ** (num_digits - 10)
            stamp = stamp_like / divisor
        return stamp  


if __name__ =='__main__':
    import time
    print("="*50)
    sec = 2.4342
    print(sec)
    print(TimeFormat.seconds(sec,'hmsf'))
    print(TimeFormat.seconds(sec,'ms7f'))

    print("="*50)
    now = datetime.now()
    print(now)
    print(TimeFormat.datetime(now,'full'))
    print(TimeFormat.datetime(now,'short'))
    print(TimeFormat.datetime(now,'hmsf'))
    print(TimeFormat.datetime(now,'ms7f'))

    print("="*50)
    tsp = time.time()
    print(tsp)
    print(TimeFormat.timestamp(tsp,'full'))
    print(TimeFormat.timestamp(tsp,'short'))
    print(TimeFormat.timestamp(tsp,'hmsf'))
    print(TimeFormat.timestamp(tsp,'ms7f'))









    # print(TimeFormat._from_stamp(tsp,'KST'))
    # print(TimeFormat._from_stamp(tsp,'UTC'))
    # print(TimeFormat._from_stamp(tsp))