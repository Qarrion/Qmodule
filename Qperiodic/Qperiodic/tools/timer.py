from Qperiodic.utils.logger_custom import CustomLog
from datetime import datetime, timedelta
from functools import partial
from datetime import datetime
from typing import Callable, Literal

import time, logging, traceback, threading
import ntplib, pytz


class _format:

    @staticmethod
    def seconds(seconds:float,fmt:Literal['hmsf','ms7f']='hmsf'):
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
    
    @staticmethod
    def datetime(datetime_naive:datetime, fmt:Literal['full','hmsf','ms7f']):
        assert datetime_naive.tzinfo is None, "aware invalid"
        if fmt == 'full':
            formatted_time = datetime_naive.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        elif fmt=='hmsf':
            formatted_time = datetime_naive.strftime('%H:%M:%S.%f')[:-3] 
        elif fmt=='ms7f':
            formatted_time = datetime_naive.strftime(':%S.%f') 
        return formatted_time

class Timer:
    """
    + (current local) + (offset) + [return sec] = (target server) + buffer
    + @ OFF(Local, Buffer)
    >>> # 
    timer = Timer()
    
    """
    timezone = {
    "KST":pytz.timezone('Asia/Seoul'),
    "UTC":pytz.timezone('UTC')}

    buffer = 0.005 #seconds

    def __init__(self, logger:logging.Logger=None):
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Timer', 'buffer', f"{self.buffer*1000} ms")

        self.registry = dict()
        self.core = None

        self._buffer_ms_delta = timedelta(milliseconds=self.buffer*1000)
    # ------------------------------------------------------------------------ #
    #                                   core                                   #
    # ------------------------------------------------------------------------ #
    def set_core(self, core):
        """+ core.now_naive()"""
        self._custom.info.msg('newst')
        self.core = core

    def now_naive(self, tz:Literal['KST','UTC']='KST')->datetime:
        """return naive"""

        if self.core is None : 
            now_stamp = time.time() 
            now_dtime = datetime.fromtimestamp(now_stamp,tz= self.timezone[tz]) 
            now_dtime_naive = now_dtime.replace(tzinfo=None)
        else : 
            now_dtime_naive = self.core.now_naive(tz=tz)

        return now_dtime_naive        
    
    # ------------------------------------------------------------------------ #
    #                               register time                              #
    # ------------------------------------------------------------------------ #
    def register(self, preset:Callable, pname):
        if pname is None : pname = preset.__name__ 
        self.registry[pname] = preset
        self._custom.info.msg('preset', pname, task=False)
    
    def execute(self, pname):
        return self.registry[pname]()

    def wrapper(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        
        if msg : self._custom.msg('every', f'at({at})', every)

        if every == 'minute_at_seconds':
            func = partial(self.minute_at_seconds,at,tz,msg)
        elif every == 'hour_at_minutes':
            func = partial(self.hour_at_minutes,at,tz,msg)
        elif every == 'day_at_hours':
            func = partial(self.day_at_hours,at,tz,msg)
        elif every == 'every_seconds':
            func = partial(self.every_seconds,at,tz,msg)
        elif every == 'every_minutes':
            func = partial(self.every_minutes,at,tz,msg)
        elif every == 'every_hours':
            func = partial(self.every_hours,at,tz,msg)

        return func

    def _get_debuging_seconds(self, tot_seconds, nxt_dtime):
        total_s = _format.seconds(tot_seconds,'hmsf')
        final_s = _format.datetime(nxt_dtime,'hmsf')
        offset = 0.0 if self.core is None else self.core.offset
        if offset >=0:
            core_s = f"OFF(+{offset:.3f} +{self.buffer:.3f})"
        else:
            core_s = f"OFF({offset:.3f} +{self.buffer:.3f})"

        return (total_s, final_s, core_s)
    
    def minute_at_seconds(self, seconds:float, tz:Literal['KST','UTC']='KST',msg=True) -> float:
        assert 0 <= seconds < 60 , 'invalid seconds'
        now_dtime = self.now_naive(tz=tz) 
        if now_dtime.second >= seconds : nxt_dtime = now_dtime + timedelta(minutes=1) 
        nxt_dtime = nxt_dtime.replace(second=seconds,microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds() 
        if msg : 
            total_s,final_s,core_s= self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"clock s ({seconds})",total_s,final_s,back=None)
        return tot_seconds
          
    def hour_at_minutes(self, minutes:float, tz:Literal['KST','UTC']='KST',msg=True) -> float:
        assert 0 <= minutes < 60 , 'invalid minutes'
        now_dtime = self.now_naive(tz=tz) 
        if now_dtime.minute >= minutes : nxt_dtime = now_dtime + timedelta(hours=1)
        nxt_dtime = nxt_dtime.replace(minute=minutes,second=0,microsecond=0) 
        nxt_dtime = nxt_dtime + self._buffer_ms_delta
        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg : 
            total_s,final_s,core_s= self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"clock m ({minutes})",total_s,final_s,back=None)
        return tot_seconds 

    def day_at_hours(self, hours:float, tz:Literal['KST','UTC']='KST',msg=True)  -> float:
        assert 0 <= hours < 24 , 'invalid hour'
        now_dtime = self.now_naive(tz=tz) 
        if now_dtime.hour >= hours : nxt_dtime = now_dtime + timedelta(days=1)
        try:
            nxt_dtime = nxt_dtime.replace(hour=hours,minute=0,second=0,microsecond=0)
            nxt_dtime = nxt_dtime + self._buffer_ms_delta
            tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        except Exception as e :
            print(str(e))
            print(e)
        if msg : 
            total_s,final_s,core_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"clock h ({hours})",total_s,final_s,back=None)        
        return tot_seconds 

    def every_seconds(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> float:
        assert 0 < value <= 60 , 'invalid seconds'
        now_dtime = self.now_naive(tz=tz) 
        unit_value_now = now_dtime.second
        unit_value_nxt = int((unit_value_now/value)+1.0)*value

        nxt_dtime = now_dtime + timedelta(seconds=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s,core_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"every s ({value})",total_s, final_s,back=None)  
        return tot_seconds 

    def every_minutes(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> float:
        assert 0 < value <= 60 , 'invalid minutes'
        now_dtime = self.now_naive(tz=tz) 
        unit_value_now = now_dtime.minute
        unit_value_nxt = int((unit_value_now/value)+1.0)*value

        nxt_dtime = now_dtime + timedelta(minutes=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(second=0, microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s,core_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"every m ({value})",total_s, final_s,back=None)  
        return tot_seconds + self.buffer  

    def every_hours(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> float:
        assert 0 < value <= 24 , 'invalid hour'
        now_dtime = self.now_naive(tz=tz) 
        unit_value_now = now_dtime.hour
        unit_value_nxt = int((unit_value_now/value)+1.0)*value
        
        nxt_dtime = now_dtime + timedelta(hours=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(minute=0, second=0, microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s,core_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"every h ({value})",total_s, final_s,back=None)  

        return tot_seconds + self.buffer 


if __name__=="__main__":
    from Qperiodic.utils.logger_color import ColorLog
    logg = ColorLog('main', 'green')
    # --------------------------------- wait --------------------------------- #
    timer = Timer(logg)
    timer.minute_at_seconds(10,'KST')
    timer.hour_at_minutes(10,'KST')
    timer.day_at_hours(10,'KST')

    timer.every_seconds(10,'KST')
    timer.every_minutes(60,'KST')
    timer.every_hours(10,'KST')

    # get_total_seconds = timer.wrapper('minute_at_seconds',5,'KST')
    # get_total_seconds()

    # get_total_seconds = timer.wrapper('every_seconds',2)
    # get_total_seconds()
    # evry.hours(24,'KST')
    
    # --------------------------------- Timer -------------------------------- #
    # timer = Timer(logg)

    # timer.get_offset(msg=True)
    # timer.now_naive(msg=True)
    # timer.now_stamp(msg=True)

    # timer.run_daemon_thread('every_seconds',3,'KST',True)

    # for i in range(20):
    #     time.sleep(1)
    #     timer.get_offset(msg=True)