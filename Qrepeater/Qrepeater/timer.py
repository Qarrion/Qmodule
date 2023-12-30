
import logging
from typing import Literal
from datetime import datetime, timedelta

from Qrepeater.msg import Msg



class Timer:
    def __init__(self, value:float, unit:Literal['second','minute'], logger:logging.Logger=None):
        self.msg = Msg(logger, 'thread')
        self.interval = value
        self.unit = unit

    def remaining_seconds(self, debug=False):
        datetime_now = datetime.now()

        unit_value_now = self._unit_value(datetime_now)
        unit_value_next = int((unit_value_now/self.interval)+1)*self.interval

        unit_delta_next = self._unit_timedelta(unit_value_next-unit_value_now)    #? from now to next
        datetime_next = self._unit_floor(datetime_now+unit_delta_next)

        timedelta_ms = datetime_next - datetime_now
        if debug:
            self.msg.debug.strm_timer_wait(datetime_next, timedelta_ms)
        return timedelta_ms.total_seconds()

    def _unit_value(self,datetime_now:datetime)->int:
        if self.unit == 'second':
            unit_value = datetime_now.second
        elif self.unit == 'minute':
            unit_value = datetime_now.minute
        return unit_value

    def _unit_timedelta(self,unit_value:int)->timedelta:
        if self.unit == 'second':
            unit_delta = timedelta(seconds=unit_value)
        elif self.unit == 'minute':
            unit_delta = timedelta(minutes=unit_value)
        return unit_delta

    def _unit_floor(self, date_time:datetime)->datetime:
        if self.unit == 'second':
            on_time = date_time.replace(microsecond=0)
        elif self.unit == 'minute':
            on_time = date_time.replace(second=0,microsecond=0)
        return on_time
    
if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('test','level')
    timer = Timer(20, 'second', logger)
    print(timer.remaining_seconds())
