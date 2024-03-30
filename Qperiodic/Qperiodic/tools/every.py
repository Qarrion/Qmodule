from datetime import datetime, timedelta
from typing import Literal
from functools import partial




class Every:

    """
    every = Every()
    every.day()
    """

    def _str_from_datetime(self, dtime:datetime):        
        return dtime.strftime("%Y-%m-%d %H:%M:%S.%f")
         

    
    def wrapper(self, every:Literal['minute','hour','day']='minute', at:int=5):
        if every == 'minute':
            func = partial(self.minute, at)
        elif every == 'hour':
            func = partial(self.minute, at)
        elif every == 'day':
            func = partial(self.minute, at)

        return func

    def day(self, hours:int, now_naive:datetime=None)->float:
        assert 0 <= hours < 24 , 'invalid hour'
        now = datetime.now() if now_naive is None else now_naive

        tgt = now + timedelta(days=1) if now.hour >= hours else now
        tgt = tgt.replace(hour=hours,minute=0,second=0,microsecond=0)

        rslt = (tgt-now).total_seconds()
        return rslt


    def hour(self,minutes:int, now_naive:datetime=None)->float:
        assert 0 <= minutes < 60 , 'invalid minute'
        now = datetime.now() if now_naive is None else now_naive
        
        tgt = now + timedelta(hours=1) if now.minute >= minutes else now
        tgt = tgt.replace(minute=minutes,second=0,microsecond=0)

        rslt = (tgt-now).total_seconds()
        return rslt
    
    def minute(self, second:int, now_naive:datetime=None)->float:
        assert 0 <= second < 60 , 'invalid second'
        now = datetime.now() if now_naive is None else now_naive
            
        tgt = now + timedelta(minutes=1) if now.second >= second else now
        tgt = tgt.replace(second=second,microsecond=0)

        rslt = (tgt-now).total_seconds()
        return rslt



# seconds = 12321.1231242
# _hours = int(seconds // 3600)
# _minutes = int((seconds % 3600) // 60)
# _seconds = int(seconds % 60)
# remain = seconds - _hours*3600 - _minutes*60 - _seconds
# _milliseconds = int(remain*10**7)
# f"{_hours:02d}:{_minutes:02d}:{_seconds:02d}.{_milliseconds}"

# hours = int(seconds // 3600)
# minutes = int((seconds % 3600) // 60)
# seconds = seconds-hours*3600-minutes*60
# millisecond = int((seconds - int(seconds))*10**7)
# f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millisecond}"