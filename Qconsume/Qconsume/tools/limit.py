import time
from Qconsume.utils.logger_custom import CustomLog

from typing import Callable, Literal
import asyncio, logging
from datetime import datetime, timezone,timedelta


# TODO
class _format:

    tz_dict = {
        "KST":timezone(timedelta(hours=9)),

    }
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
            seconds_formatted = (
                # f"{seconds_sign}{int(seconds_hours):02}:{int(seconds_minutes):02}:"
                f"{int(seconds_hours):02}:{int(seconds_minutes):02}:"
                f"{int(seconds_seconds):02}.{int(microsecond):03}"
            )
        elif fmt =='ms7f':
            microsecond = round(microsecond * 1000000,0)
            seconds_formatted = (
                # f"{seconds_sign}{int(seconds_hours):02}:{int(seconds_minutes):02}:"
                f":{int(seconds_seconds):02}.{int(microsecond):06}"
            )
        return seconds_formatted
    
    @classmethod
    def datetime(cls, datetime_naive:datetime, fmt:Literal['full','hmsf','ms7f']):
        assert datetime_naive.tzinfo is None, "aware invalid"
        if fmt == 'full':
            formatted_time = datetime_naive.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        elif fmt=='hmsf':
            formatted_time = datetime_naive.strftime('%H:%M:%S.%f')[:-3] 
        elif fmt=='ms7f':
            formatted_time = datetime_naive.strftime(':%S.%f') 
        return formatted_time
    
    @classmethod    
    def timestamp(cls, timestamp:datetime, fmt:Literal['full','hmsf','ms7f']):
        datetime_naive = cls._from_stamp(timestamp,'KST').replace(tzinfo=None)
        return cls.datetime(datetime_naive, fmt)
    
    @classmethod
    def _from_stamp(cls, stamp:float, tz:Literal['KST','UTC']):
        stamp = cls._to_ten_digit(stamp)
        date_time = datetime.fromtimestamp(stamp, cls.tz_dict[tz])
        return date_time

    def _to_ten_digit(stamp_like:float):
        num_digits = len(str(int(stamp_like))) 
        if num_digits <= 10:
            stamp = stamp_like
        else :
            divisor = 10 ** (num_digits - 10)
            stamp = stamp_like / divisor
        return stamp  

class Limit:

    def __init__(self, logger:logging.Logger=None):
        self._custom = CustomLog(logger,'async')

    def set_rate(self, max_worker:int, seconds:float, limit:Literal['inflow','outflow']):
        self._max_worker = max_worker
        self._seconds = seconds
        self._limit_type = limit

        self._semaphore = asyncio.Semaphore(max_worker)
        self._custom.info.msg(limit,f"max({max_worker})",f"sec({seconds})")

    def _wrapper_throttle(self, async_def:Callable):
        async def wrapper(*args):
            propagate_exception = None

            async with self._semaphore:
                self._msg_semaphore('acquire',async_def.__name__)
                # ------------------------------------------------------------ #
                try: 
                    tsp_start = time.time()     
                    result = await async_def(*args)

                except Exception as e:
                    self._custom.error.msg('job',async_def.__name__,str(args))
                    propagate_exception = e
                # ------------------------------------------------------------ #
                finally:
                    tsp_finish = time.time()
                    await self._wait_reset(tsp_start, tsp_finish)
                    self._msg_semaphore('release',async_def.__name__)
                    #? propagate exception to retry
                    if propagate_exception:
                        raise propagate_exception
        return wrapper
    
    def _msg_semaphore(self, context:Literal['acquire','release'], fname):
        if context=="acquire":
            queue = f">s({self._semaphore._value}/{self._max_worker})"
            var01 = f"{queue:<11}<"
        elif context =="release":
            queue = f"s({self._semaphore._value+1}/{self._max_worker})<"
            var01 = f">{queue:>11}"
        self._custom.debug.msg(context,fname,var01,frame='sema',task=True)

    async def _wait_reset(self, tsp_start:float, tsp_finish):
        #! TODO msg replace with methods _msg_xxx
        if self._limit_type == 'inflow':
            tsp_ref = tsp_start
        elif self._limit_type == 'outflow':
            tsp_ref = tsp_finish
        elif self._limit_type == 'midflow':
            tsp_ref = (tsp_start+tsp_finish)/2

        seconds = tsp_ref + self._seconds - time.time()
        seconds = max(seconds, 0.0)

        msg_sec = _format.seconds(seconds,'hmsf')
        msg_ref = _format.timestamp(tsp_ref,'hmsf')

        self._custom.debug.msg(self._limit_type,f"unit s ({self._seconds})",msg_ref,msg_sec,task=True)
        
        if seconds > 0.0:
            await asyncio.sleep(seconds)

        # if seconds > 0:
        #     #?  tsp_ref 여기 출력 양식 변경
        #     self._custom.debug.msg(self._limit_type, tsp_ref, seconds,frame='wait',task=True)
        #     await asyncio.sleep(seconds)
        # else:
        #     self._custom.debug.msg(self._limit_type, tsp_ref, 0,frame='wait',task=True)

