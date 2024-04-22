from Qutils.logger_custom import CustomLog
from datetime import datetime, timedelta
from functools import partial
from datetime import datetime
from typing import Callable, Literal, Tuple

import time, logging, traceback, threading
import pytz

"""
return 되는 시간은 sleep에 시용 되는 것을 염두
최초 실행에서 목표로 하는 시간 보다 일찍 sleep이 끝날 경우
짧은 시간에 같은 목표 시간으로 여러번 반복 실행될 수 있음
core.offet에 의해 현재 시간이 조정될 수 있는 것에 의함
-> tot_seconds와 tgt_naive를 함께 출력하여 보완
"""

class _core:
    offset:float = 0.0
    buffer:float = 0.02
    name:str = 'default'

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
    >>> # basic
    timer = Timer()
    timer.minute_at_seconds(10,'KST')
    timer.hour_at_minutes(10,'KST')
    timer.day_at_hours(10,'KST')
    timer.every_seconds(10,'KST')
    timer.every_minutes(60,'KST')
    timer.every_hours(10,'KST')
    >>> # wrapper
    preset = timer.wrapper(every='minute_at_seconds', at=5, tz='KST', msg=True)
    >>> # utils
    timer.msg_divider(task=None,offset=None):
    >>> # core (default)
    timer.set_core(_core)
    class _core:
        offset = 0
        buffer = 0.02
        whoami = 'default'
    """
    timezone = {
    "KST":pytz.timezone('Asia/Seoul'),
    "UTC":pytz.timezone('UTC')}

    def __init__(self, logger:logging.Logger=None):
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Timer')

        self._core = _core
        self._buffer_ms_delta = timedelta(milliseconds=self._core.buffer*1000)
    # ------------------------------------------------------------------------ #
    #                                   core                                   #
    # ------------------------------------------------------------------------ #
    def set_core(self, core):
        #! core backup process
        self._core = core 
        name = self._core.name if hasattr(self._core, 'name') else 'none'
        self._buffer_ms_delta = timedelta(milliseconds=self._core.buffer*1000)
        offset = f"OFF({self._core.offset:+.3f})"
        buffer = f"BUF({self._core.buffer:+.3f})"
        
        self._custom.info.msg('Timer',f"({name})",offset,buffer,offset=self._core.offset)

    def wrapper(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        self._warning_default_core('wrapper()')
        self._custom.msg('Timer', f'at({at})', every,offset=self._core.offset)

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

    def msg_divider(self,task=None,offset=None):
        self._custom.div(task,offset)

    def _now_naive(self, tz:Literal['KST','UTC']='KST')->datetime:
        """return naive"""
        now_stamp = time.time() + self._core.offset
        now_dtime = datetime.fromtimestamp(now_stamp,tz= self.timezone[tz]) 
        now_dtime_naive = now_dtime.replace(tzinfo=None)

        return now_dtime_naive        
    
    def _get_debuging_seconds(self, tot_seconds, nxt_dtime):
        total_s = _format.seconds(tot_seconds,'hmsf')
        final_s = _format.datetime(nxt_dtime,'hmsf')
        core_s = f"OFF({self._core.offset:+.3f} {self._core.buffer:+.3f})"
        return (total_s, final_s, core_s)

    def _warning_default_core(self, where):
        if hasattr(self._core, 'name'):
            if self._core.name == 'default':
                print(f'\033[31m [Warning:{where}] core has not been set! ::: timer.set_core(core) \033[0m')

    def minute_at_seconds(self, seconds:float, tz:Literal['KST','UTC']='KST',msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 <= seconds < 60 , 'invalid seconds'
        now_dtime = self._now_naive(tz=tz) 
        nxt_dtime = (now_dtime + timedelta(minutes=1)) if now_dtime.second >= seconds else now_dtime
        nxt_dtime = nxt_dtime.replace(second=seconds,microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds() 
        if msg : 
            total_s,final_s,core_s= self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"clock s ({seconds})",total_s,final_s,frame=None,offset=self._core.offset)
        return tot_seconds, nxt_dtime
          
    def hour_at_minutes(self, minutes:float, tz:Literal['KST','UTC']='KST',msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 <= minutes < 60 , 'invalid minutes'
        now_dtime = self._now_naive(tz=tz) 
        nxt_dtime = (now_dtime + timedelta(hours=1)) if now_dtime.minute >= minutes else now_dtime
        nxt_dtime = nxt_dtime.replace(minute=minutes,second=0,microsecond=0) 
        nxt_dtime = nxt_dtime + self._buffer_ms_delta
        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg : 
            total_s,final_s,core_s= self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"clock m ({minutes})",total_s,final_s,frame=None,offset=self._core.offset)
        return tot_seconds, nxt_dtime

    def day_at_hours(self, hours:float, tz:Literal['KST','UTC']='KST',msg=True)  -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 <= hours < 24 , 'invalid hour'
        now_dtime = self._now_naive(tz=tz) 
        nxt_dtime = (now_dtime + timedelta(days=1)) if now_dtime.hour >= hours else now_dtime
    
        nxt_dtime = nxt_dtime.replace(hour=hours,minute=0,second=0,microsecond=0)
        nxt_dtime = nxt_dtime + self._buffer_ms_delta
        tot_seconds = (nxt_dtime-now_dtime).total_seconds()

        if msg : 
            total_s,final_s,core_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"clock h ({hours})",total_s,final_s,frame=None,offset=self._core.offset)  
        return tot_seconds, nxt_dtime

    def every_seconds(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 < value <= 60 , 'invalid seconds'
        now_dtime = self._now_naive(tz=tz) 
        unit_value_now = now_dtime.second
        unit_value_nxt = int((unit_value_now/value)+1.0)*value

        nxt_dtime = now_dtime + timedelta(seconds=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s,core_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"every s ({value})",total_s, final_s,frame=None,offset=self._core.offset)
        return tot_seconds, nxt_dtime

    def every_minutes(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 < value <= 60 , 'invalid minutes'
        now_dtime = self._now_naive(tz=tz) 
        unit_value_now = now_dtime.minute
        unit_value_nxt = int((unit_value_now/value)+1.0)*value

        nxt_dtime = now_dtime + timedelta(minutes=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(second=0, microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s,core_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"every m ({value})",total_s, final_s,frame=None,offset=self._core.offset)
        return tot_seconds + self._core.buffer , nxt_dtime

    def every_hours(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 < value <= 24 , 'invalid hour'
        now_dtime = self._now_naive(tz=tz) 
        unit_value_now = now_dtime.hour
        unit_value_nxt = int((unit_value_now/value)+1.0)*value
        
        nxt_dtime = now_dtime + timedelta(hours=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(minute=0, second=0, microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s,core_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._custom.debug.msg(core_s,f"every h ({value})",total_s, final_s,frame=None,offset=self._core.offset)

        return tot_seconds + self._core.buffer, nxt_dtime


if __name__=="__main__":
    a=datetime.now()
    from Qutils.logger_color import ColorLog
    logg = ColorLog('main', 'green')
    timer = Timer(logg)
    timer.msg_divider()

    # --------------------------------- timer -------------------------------- #
    # timer.minute_at_seconds(10,'KST')
    # timer.hour_at_minutes(10,'KST')
    # timer.day_at_hours(10,'KST')

    # timer.every_seconds(10,'KST')
    # timer.every_minutes(60,'KST')
    # timer.every_hours(10,'KST')

    # # -------------------------------- wrapper ------------------------------- #
    # get_total_seconds = timer.wrapper('minute_at_seconds',5,'KST')
    # get_total_seconds()

    class _core:
        offset = 0.4
        buffer = 0.05
        name = 'test core'

    timer.set_core(_core)
    get_total_seconds = timer.wrapper('every_seconds',2)
    get_total_seconds()
    
