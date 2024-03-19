
import logging
from typing import Literal
from datetime import datetime, timedelta

from Qrepeater.msg import Msg



class Timer:
    def __init__(self, value:float, unit:Literal['second','minute','hour'], msg:Msg):
        self.msg = msg
        self.interval = value
        self.unit = unit
        
    def remaining_seconds(self)->float:
        now_time = datetime.now()
        now_unit = self._to_unit(now_time)
        nxt_unit = int((now_unit/self.interval)+1)*self.interval
        nxt_time = self._to_floor(now_time+self._to_delta(nxt_unit-now_unit))
        tgt_time = nxt_time-now_time
        self.msg.info.timer(nxt_time, tgt_time)
        return tgt_time.total_seconds()

    def _to_unit(self, time:datetime)->int:
        if self.unit == 'second':
            unit_value = time.second
        elif self.unit == 'minute':
            unit_value = time.minute
        elif self.unit == 'hour':
            unit_value = time.hour
        return unit_value

    def _to_delta(self, delta:int)->timedelta:
        if self.unit == 'second':
            unit_delta = timedelta(seconds=delta)
        elif self.unit == 'minute':
            unit_delta = timedelta(minutes=delta)
        elif self.unit == 'hour':
            unit_delta = timedelta(hours=delta)
        return unit_delta

    def _to_floor(self, date_time:datetime)->datetime:
        if self.unit == 'second':
            on_time = date_time.replace(microsecond=0)
        elif self.unit == 'minute':
            on_time = date_time.replace(second=0,microsecond=0)
        elif self.unit == 'hour':
            on_time = date_time.replace(minute=0,second=0,microsecond=0)
        return on_time
    
if __name__ == "__main__":
    # from Qrepeater.utils.log_color import ColorLog
    from Qlogger import Logger

    logger = Logger('test','green')
    msg = Msg(logger,'async')
    timer = Timer(5, 'minute', msg)
    print(timer.remaining_seconds())
