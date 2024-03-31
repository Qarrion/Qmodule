from datetime import datetime, timedelta
from typing import Literal, Self
from functools import partial
from datetime import datetime
from typing import Literal
import ntplib
import pytz
import time
import threading
from Qperiodic.tools.every import Every
from Qperiodic.utils.log_custom import CustomLog
import logging

import traceback
class Timer:
    """
    timer = Timer()
    timer.run_daemon_thread
    """
    def __init__(self, logger:logging.Logger=None):
        self.custom = CustomLog(logger,'thread')
        self.sync = Sync(self.custom)
        self.next = Next(self.custom)
        
    def run_daemon_thread(self, every:Literal['minute','hour','day']='minute', 
                          at:int=5, tz:Literal['KST','UTC']='KST', add_offset=True):
        get_remaining_seconds = self.next.wrapper(every, at, tz, add_offset)
        self.thread_daemon = threading.Thread(name='background',
            target=self._worker, args=(get_remaining_seconds,), daemon=True)
        self.thread_daemon.start()

    def _worker(self, callback_seconds):
        while True:
            try:    
                seconds = callback_seconds()  
                time.sleep(seconds)
                Offset.value = self.sync.fetch_offset()
                time.sleep(1) 
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                time.sleep(1) 

class Offset:
    value:int = 0


class Sync:
    """>>> #
    sync = Sync()
    sync.fetch_offset()
    """
    
    server_list = ["pool.ntp.org","time.windows.com" "time.nist.gov","ntp.ubuntu.com"]
    
    def __init__(self, custom:CustomLog):
        self.custom = custom
        self.custom.info.msg('Sync')
        Offset.value = self.fetch_offset(False)

    def fetch_offset(self,debug=True):
        offset_list = []
        server_list = []
        for s in self.server_list:
            try:
                ntpstat = self._fetch_NTPStats(s)
                offset = round(ntpstat.offset,7)
                offset_list.append(offset)
                server_list.append(s)
            except Exception as e:
                pass

        rslt = max(offset_list)
        msg = f'max offset ({rslt}) {server_list} {offset_list}'
        if debug: self.custom.info.msg('ok',msg)
        return rslt
            
    def _fetch_NTPStats(self, server):
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return response


class Next:
    """ 
    >>> # basic
    next = Next()
    seconds = next.minute_at_seconds(seconds=5, tz='KST', add_offset=True)
    seconds = next.hour_at_minutes(minutes=5, tz='KST', add_offset=True)
    seconds = next.day_at_hours(hours=5, tz='KST', add_offset=True)

    >>> # wrapper
    next = Next()
    get_next_seconds = next.wrapper(every='minute', at=5, tz='KST')
    seconds = get_next_seconds()
    """
    tz_dict = {"KST":pytz.timezone('Asia/Seoul'),"UTC":pytz.timezone('UTC')}
    
    def __init__(self, custom:CustomLog):
        self.custom = custom
        self.custom.info.msg('Next')

    def wrapper(self, every:Literal['minute','hour','day']='minute', at:int=5, tz:Literal['KST','UTC']='KST',add_offset=True):
        if every == 'minute':
            # func = self.minute_at_seconds(seconds=at,tz=tz,add_offset=add_offset)
            func = partial(self.minute_at_seconds,at,tz,add_offset)
        elif every == 'hour':
            # func = self.hour_at_minutes(minutes=at,tz=tz,add_offset=add_offset)
            func = partial(self.hour_at_minutes,at,tz,add_offset)
        elif every == 'day':
            # func = self.day_at_hours(hours=at,tz=tz,add_offset=add_offset)
            func = partial(self.day_at_hours,at,tz,add_offset)
        return func

    def now_naive(self, tz:Literal['KST','UTC']='KST' , add_offset=True):
        now_timestamp = time.time() 
        now_timestamp += Offset.value if add_offset else 0
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=self.tz_dict[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        return now_datetime_naive

    def minute_at_seconds(self, seconds:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= seconds < 60 , 'invalid seconds'
        now = self.now_naive(tz)
        tgt = now + timedelta(minutes=1) if now.second >= seconds else now
        tgt = tgt.replace(second=seconds,microsecond=0)
        rslt = (tgt-now).total_seconds()
        return rslt 
          
    def hour_at_minutes(self, minutes:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= minutes < 60 , 'invalid minutes'
        now = self.now_naive(tz)
        tgt = now + timedelta(hours=1) if now.minute >= minutes else now
        tgt = tgt.replace(minute=minutes,second=0,microsecond=0)
        rslt = (tgt-now).total_seconds()
        return rslt       

    def day_at_hours(self, hours:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= hours < 24 , 'invalid hour'
        now = self.now_naive(tz)
        tgt = now + timedelta(days=1) if now.hour >= hours else now
        tgt = tgt.replace(hour=hours,minute=0,second=0,microsecond=0)
        rslt = (tgt-now).total_seconds()
        return rslt
    

if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('timer','head')

    timer = Timer(logger)
    timer.sync.fetch_offset()

    timer.run_daemon_thread('minute',10,'KST',False)
    
    for i in range(30):
        time.sleep(10)
        logger.debug('hi')

# class Next:

#     def day(self) -> Self:
#         tgt = now + timedelta(days=1) if now.hour >= hour else now
#         tgt = tgt.replace(hour=hour,minute=0,second=0,microsecond=0)
#         return self


#     # def wrapper(self, every:Literal['minute','hour','day']='minute', at:int=5):
#     #     if every == 'minute':
#     #         func = partial(self.minute, at)
#     #     elif every == 'hour':
#     #         func = partial(self.minute, at)
#     #     elif every == 'day':
#     #         func = partial(self.minute, at)

#     #     return func

#     def day(self, hour:int, now_naive:datetime=None)->float:
#         assert 0 <= hour < 24 , 'invalid hour'
#         now = datetime.now() if now_naive is None else now_naive

#         tgt = now + timedelta(days=1) if now.hour >= hour else now
#         tgt = tgt.replace(hour=hour,minute=0,second=0,microsecond=0)

#         rslt = (tgt-now).total_seconds()
#         return rslt


#     def hour(self,minute:int, now_naive:datetime=None)->float:
#         assert 0 <= minute < 60 , 'invalid minute'
#         now = datetime.now() if now_naive is None else now_naive
        
#         tgt = now + timedelta(hours=1) if now.minute >= minute else now
#         tgt = tgt.replace(minute=minute,second=0,microsecond=0)

#         rslt = (tgt-now).total_seconds()
#         return rslt
    
#     def minute(self, second:int, now_naive:datetime=None)->float:
#         assert 0 <= second < 60 , 'invalid second'
#         now = datetime.now() if now_naive is None else now_naive
            
#         tgt = now + timedelta(minutes=1) if now.second >= second else now
#         tgt = tgt.replace(second=second,microsecond=0)

#         rslt = (tgt-now).total_seconds()
#         return rslt



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