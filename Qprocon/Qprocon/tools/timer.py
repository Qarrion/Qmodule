# -------------------------------- ver 240511 -------------------------------- #
# tools

from Qlogger import Logger
from Qprocon.utils import dtime_print
from datetime import datetime, timedelta
from typing import Literal, Tuple
from functools import partial
from datetime import datetime

import time, logging
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
    buffer:float = 0.0
    name:str = 'default'

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

    def __init__(self, name:str='timer'):
        self._logger = Logger(name,clsname='Timer',context='async')
        self.set_core(_core, msg=False)

    # ------------------------------------------------------------------------ #
    #                                   core                                   #
    # ------------------------------------------------------------------------ #
    def set_core(self, core, msg=False):
        #! core backup process
        self.core = core 
        self._core_name = self.core.name if hasattr(self.core, 'name') else 'none'
        self._buffer_ms_delta = timedelta(milliseconds=self.core.buffer*1000)
        
        offset = f"OFF({self.core.offset:+.3f})"
        buffer = f"BUF({self.core.buffer:+.3f})"
        
        if msg: self._logger.info.msg(f"'{self._core_name}'",offset,buffer, offset=self.core.offset)

    def wrapper(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        """+ return (tot_seconds, nxt_dtime)"""
        self._warning_default_core('timer.wrapper()')
        if msg : self._logger.info.msg(f'({at}) unit', every, widths=(1,2))

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

    def minute_at_seconds(self, seconds:float, tz:Literal['KST','UTC']='KST',msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 <= seconds < 60 , 'invalid seconds'
        now_dtime = self._now_kst(tz=tz) 
        nxt_dtime = (now_dtime + timedelta(minutes=1)) if now_dtime.second >= seconds else now_dtime
        nxt_dtime = nxt_dtime.replace(second=seconds,microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds() 
        if msg : 
            total_s,final_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._logger.debug.msg(f'({seconds}) seconds',total_s,final_s,fname="time_at",offset=self.core.offset)
        return tot_seconds, nxt_dtime
          
    def hour_at_minutes(self, minutes:float, tz:Literal['KST','UTC']='KST',msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 <= minutes < 60 , 'invalid minutes'
        now_dtime = self._now_kst(tz=tz) 
        nxt_dtime = (now_dtime + timedelta(hours=1)) if now_dtime.minute >= minutes else now_dtime
        nxt_dtime = nxt_dtime.replace(minute=minutes,second=0,microsecond=0) 
        nxt_dtime = nxt_dtime + self._buffer_ms_delta
        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg : 
            total_s,final_s= self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._logger.debug.msg(f'({minutes}) minutes',total_s,final_s,fname="time_at",offset=self.core.offset)
        return tot_seconds, nxt_dtime

    def day_at_hours(self, hours:float, tz:Literal['KST','UTC']='KST',msg=True)  -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 <= hours < 24 , 'invalid hour'
        now_dtime = self._now_kst(tz=tz) 
        nxt_dtime = (now_dtime + timedelta(days=1)) if now_dtime.hour >= hours else now_dtime
    
        nxt_dtime = nxt_dtime.replace(hour=hours,minute=0,second=0,microsecond=0)
        nxt_dtime = nxt_dtime + self._buffer_ms_delta
        tot_seconds = (nxt_dtime-now_dtime).total_seconds()

        if msg : 
            total_s,final_s= self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._logger.debug.msg(f'({hours}) hours',total_s,final_s,fname="time_at",offset=self.core.offset)
        return tot_seconds, nxt_dtime

    def every_seconds(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 < value <= 60 , 'invalid seconds'
        now_dtime = self._now_kst(tz=tz) 
        unit_value_now = now_dtime.second
        unit_value_nxt = int((unit_value_now/value)+1.0)*value

        nxt_dtime = now_dtime + timedelta(seconds=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._logger.debug.msg(f"({value}) seconds",total_s, final_s,fname='every',offset=self.core.offset)
        return tot_seconds, nxt_dtime

    def every_minutes(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 < value <= 60 , 'invalid minutes'
        now_dtime = self._now_kst(tz=tz) 
        unit_value_now = now_dtime.minute
        unit_value_nxt = int((unit_value_now/value)+1.0)*value

        nxt_dtime = now_dtime + timedelta(minutes=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(second=0, microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._logger.debug.msg(f"({value}) minutes",total_s, final_s,fname='every',offset=self.core.offset)
        return tot_seconds + self.core.buffer , nxt_dtime

    def every_hours(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> Tuple[float, float]:
        """+ return (total seconds , target datetime)"""
        assert 0 < value <= 24 , 'invalid hour'
        now_dtime = self._now_kst(tz=tz) 
        unit_value_now = now_dtime.hour
        unit_value_nxt = int((unit_value_now/value)+1.0)*value
        
        nxt_dtime = now_dtime + timedelta(hours=unit_value_nxt - unit_value_now)
        nxt_dtime = nxt_dtime.replace(minute=0, second=0, microsecond=0)
        nxt_dtime = nxt_dtime+ self._buffer_ms_delta 

        tot_seconds = (nxt_dtime-now_dtime).total_seconds()
        if msg:
            total_s,final_s = self._get_debuging_seconds(tot_seconds, nxt_dtime)
            self._logger.debug.msg(f"({value}) hours",total_s, final_s,fname='every',offset=self.core.offset)

        return tot_seconds + self.core.buffer, nxt_dtime

    # ------------------------------------------------------------------------ #
    #                                   utils                                  #
    # ------------------------------------------------------------------------ #
    def _now_kst(self, tz:Literal['KST','UTC']='KST')->datetime:
        """return naive"""
        now_stamp = time.time() + self.core.offset
        now_dtime = datetime.fromtimestamp(now_stamp,tz= self.timezone[tz]) 
        # now_dtime_naive = now_dtime.replace(tzinfo=None)
        return now_dtime        
    
    def _get_debuging_seconds(self, tot_seconds, nxt_dtime):
        total_s = dtime_print.from_sec(tot_seconds,'hmsf')
        final_s = dtime_print.from_dtime(nxt_dtime,'hmsf')
        # core_s = f"OFF({self._core.offset:+.3f} {self._core.buffer:+.3f})"
        return (total_s, final_s)

    def _warning_default_core(self, where):
        if hasattr(self.core, 'name'):
            if self.core.name == 'default':
                print(f"\033[31m [Warning in '{where}'] core has not been set! \033[0m")

if __name__=="__main__":
    a=datetime.now()

    timer = Timer()

    # --------------------------------- timer -------------------------------- #
    timer.minute_at_seconds(10,'KST')
    timer.hour_at_minutes(10,'KST')
    timer.day_at_hours(10,'KST')

    timer.every_seconds(10,'KST')
    timer.every_minutes(60,'KST')
    timer.every_hours(10,'KST')
    # -------------------------------- wrapper ------------------------------- #
    get_total_seconds = timer.wrapper('minute_at_seconds',5,'KST')
    get_total_seconds()
    # -------------------------------- wrapper ------------------------------- #

    class _core:
        offset = 0.4
        buffer = 0.05
        name = 'test'

    timer.set_core(_core,msg=True)
    get_total_seconds = timer.wrapper('every_seconds',2)
    get_total_seconds()
    
