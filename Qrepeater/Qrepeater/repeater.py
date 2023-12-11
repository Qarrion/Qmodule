import logging
from typing import Literal

from datetime import datetime, timedelta
from Qrepeater import Msg


unit = Literal['second','minute']

class Timer:
    def __init__(self, value:float, unit:unit, logger:logging.Logger=None):
        self.msg = Msg(logger, 'thread')
        self.interval = value
        self.unit = unit

    def total_seconds(self):
        # TODO  get
        datetime_now = datetime.now()

        unit_value_now = self._unit_value(datetime_now)
        unit_value_next = int((unit_value_now/self.interval)+1)*self.interval

        unit_delta_next = self._unit_timedelta(unit_value_next-unit_value_now)    #? from now to next
        datetime_next = self._unit_floor(datetime_now+unit_delta_next)

        timedelta_ms = datetime_next - datetime_now

        self.log.info.wait(datetime_next, timedelta_ms, self.interval, self.unit)
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

class Repeater:

    def __init__(self, value:float, unit:unit, logger:logging.Logger):
        self.msg = Msg(logger, 'thread')

    



if __name__ == "__main__":
    rp = Repeater(20, 'second')