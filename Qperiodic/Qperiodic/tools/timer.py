from Qperiodic.utils.logger_custom import CustomLog
from datetime import datetime, timedelta
from functools import partial
from datetime import datetime
from typing import Literal

import time, logging, traceback, threading
import ntplib, pytz





class _core:
    offset:float = 0.0
    buffer = timedelta(seconds=0.05)

    timezone = {
    "KST":pytz.timezone('Asia/Seoul'),
    "UTC":pytz.timezone('UTC')
    }
    @classmethod
    def now_stamp(self)->float:
        """with offset"""
        now_timestamp = time.time() + _core.offset
        return now_timestamp

    @classmethod
    def now_naive(cls, tz:Literal['KST','UTC']='KST')->datetime:
        """return naive"""
        now_timestamp = _core.now_stamp()
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=_core.timezone[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        return now_datetime_naive

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
    >>> #
    timer = Timer()
    timer.offset
    timer.now_naive()
    timer.now_stamp()
    """
    def __init__(self, logger:logging.Logger=None):
        self.custom = CustomLog(logger,'async')
        self.custom.info.msg('Timer')

        self.sync = Sync(self.custom)
        self.every = Every(self.custom)

    def now_naive(self, tz: Literal['KST', 'UTC'] = 'KST', msg=False):
        now_naive = _core.now_naive(tz)
        if msg: self.custom.info.msg('', str(now_naive))
        return now_naive
    
    def now_stamp(self, msg=False):
        now_stamp = _core.now_stamp()
        if msg: self.custom.info.msg('', now_stamp)
        return now_stamp

    def get_offset(self,msg=False):
        offset = _core.offset
        if msg:self.custom.info.msg('',offset)
        return offset

    def run_daemon_thread(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                    'seconds','minutes','hours'], at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        get_total_seconds = self.every.wrapper(every,at,tz,msg=False)
        def worker():
            while True:
                try:
                    time.sleep(get_total_seconds())
                    _core.offset = self.sync.fetch_offset(msg=msg)
                except Exception as e:
                    print(str(e))
                    traceback.print_exc()
                    time.sleep(1)
        self.daemon_thread = threading.Thread(name='BackGround',target=worker, daemon=True)
        self.daemon_thread.start()            



class Sync:
    """>>> #
    sync = Sync()
    sync.fetch_offset()
    sync.check_offset()
    """
    server_list = ["pool.ntp.org","kr.pool.ntp.org","time.windows.com" "time.nist.gov","ntp.ubuntu.com"]
    
    def __init__(self, custom:CustomLog):
        self.custom = custom
        self.custom.info.msg('Sync')

        self.check_offset()
        _core.offset = self.fetch_offset(True)
        # self.check()

    def fetch_offset(self, msg=True):
        max_offset = None
        for server in self.server_list:
            try:
                offset = self._fetch_NTPStats(server).offset
                if max_offset is None :
                    max_offset, max_server = offset, server
                else :
                    if offset > max_offset:
                        max_offset, max_server = offset, server
            except Exception as e:
                pass
        if msg: self.custom.info.msg('ok',f"{max_offset:.6f}", max_server)
        return max_offset
            
    def _fetch_NTPStats(self, server)->ntplib.NTPStats:
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return response

    def check_offset(self):
        for server in self.server_list:
            try:
                response = self._fetch_NTPStats(server)
                tsp_offset = response.offset
                kst_server = datetime.fromtimestamp(response.tx_time, tz=_core.timezone['KST'])
                kst_local = datetime.fromtimestamp(time.time(), tz=_core.timezone['KST'])
                print(f"  ::: offset({tsp_offset:.6f}), server({kst_server}) - local({kst_local}) [{server}]")
            except Exception as e:
                pass        

class Every:
    """>>> # every times on the clock 
    every = Every()
    every.hours(5)
    every.minutes(5)
    every.seconds(5,add_offset=True)
    """
    def __init__(self, custom:CustomLog):
        
        self.custom = custom
        self.custom.info.msg('Every')

    def wrapper(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'seconds','minutes','hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        
        if msg : self.custom.msg('every', f'at({at})', every)

        if every == 'minute_at_seconds':
            func = partial(self.minute_at_seconds,at,tz,msg)
        elif every == 'hour_at_minutes':
            func = partial(self.hour_at_minutes,at,tz,msg)
        elif every == 'day_at_hours':
            func = partial(self.day_at_hours,at,tz,msg)
        elif every == 'seconds':
            func = partial(self.seconds,at,tz,msg)
        elif every == 'minutes':
            func = partial(self.minutes,at,tz,msg)
        elif every == 'hours':
            func = partial(self.hours,at,tz,msg)

        return func

    def _get_total_and_final_sec(self, tot_seconds, nxt_datetime):
        total_sec = _format.seconds(tot_seconds,'hmsf')
        final_sec = _format.datetime(nxt_datetime,'hmsf')
        return (total_sec, final_sec)

    def minute_at_seconds(self, seconds:float, tz:Literal['KST','UTC']='KST',msg=True) -> float:
        assert 0 <= seconds < 60 , 'invalid seconds'
        now_datetime = _core.now_naive(tz=tz) + _core.buffer
        nxt_datetime = now_datetime + timedelta(minutes=1) if now_datetime.second >= seconds else now_datetime
        nxt_datetime = nxt_datetime.replace(second=seconds,microsecond=0)
        tot_seconds = (nxt_datetime-now_datetime).total_seconds()
        if msg : 
            total_sec , final_sec = self._get_total_and_final_sec(tot_seconds, nxt_datetime)
            self.custom.debug.msg('at_seconds',f"s ({seconds})",total_sec, final_sec,back=None)
        return tot_seconds 
          
    def hour_at_minutes(self, minutes:float, tz:Literal['KST','UTC']='KST',msg=True) -> float:
        assert 0 <= minutes < 60 , 'invalid minutes'
        now_datetime = _core.now_naive(tz=tz) + _core.buffer
        nxt_datetime = now_datetime + timedelta(hours=1) if now_datetime.minute >= minutes else now_datetime
        nxt_datetime = nxt_datetime.replace(minute=minutes,second=0,microsecond=0)
        tot_seconds = (nxt_datetime-now_datetime).total_seconds()
        if msg : 
            total_sec , final_sec = self._get_total_and_final_sec(tot_seconds, nxt_datetime)
            self.custom.debug.msg('at_minutes',f"m ({minutes})",total_sec, final_sec,back=None)
        return tot_seconds       

    def day_at_hours(self, hours:float, tz:Literal['KST','UTC']='KST',msg=True)  -> float:
        assert 0 <= hours < 24 , 'invalid hour'
        now_datetime = _core.now_naive(tz=tz) + _core.buffer
        nxt_datetime = now_datetime + timedelta(days=1) if now_datetime.hour >= hours else now_datetime
        nxt_datetime = nxt_datetime.replace(hour=hours,minute=0,second=0,microsecond=0)
        tot_seconds = (nxt_datetime-now_datetime).total_seconds()
        if msg : 
            total_sec , final_sec = self._get_total_and_final_sec(tot_seconds, nxt_datetime)
            self.custom.debug.msg('at_hours',f"h ({hours})",total_sec, final_sec,back=None)
        return tot_seconds

    def hours(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> float:
        assert 0 < value <= 24 , 'invalid hour'
        now_datetime = _core.now_naive(tz=tz) + _core.buffer
        unit_value_now = now_datetime.hour
        unit_value_nxt = int((unit_value_now/value)+1.0)*value
        
        nxt_datetime = now_datetime + timedelta(hours=unit_value_nxt - unit_value_now)
        nxt_datetime = nxt_datetime.replace(minute=0, second=0, microsecond=0)
        tot_seconds = (nxt_datetime-now_datetime).total_seconds()

        if msg:
            total_sec , final_sec = self._get_total_and_final_sec(tot_seconds, nxt_datetime)
            self.custom.debug.msg('every hours',f"h ({value})", total_sec, final_sec,back=None)

        return tot_seconds  

    def minutes(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> float:
        assert 0 < value <= 60 , 'invalid minutes'
        now_datetime = _core.now_naive(tz=tz) + _core.buffer
        unit_value_now = now_datetime.minute
        unit_value_nxt = int((unit_value_now/value)+1.0)*value

        nxt_datetime = now_datetime + timedelta(minutes=unit_value_nxt - unit_value_now)
        nxt_datetime = nxt_datetime.replace(second=0, microsecond=0)
        tot_seconds = (nxt_datetime-now_datetime).total_seconds()

        if msg:
            total_sec , final_sec = self._get_total_and_final_sec(tot_seconds, nxt_datetime)
            self.custom.debug.msg('every minutes',f"m ({value})", total_sec, final_sec,back=None)
        return tot_seconds  

    def seconds(self, value:float, tz:Literal['KST','UTC']='KST', msg=True) -> float:
        assert 0 < value <= 60 , 'invalid seconds'
        now_datetime = _core.now_naive(tz=tz) + _core.buffer
        unit_value_now = now_datetime.second
        unit_value_nxt = int((unit_value_now/value)+1.0)*value

        nxt_datetime = now_datetime + timedelta(seconds=unit_value_nxt - unit_value_now)
        nxt_datetime = nxt_datetime.replace(microsecond=0)
        tot_seconds = (nxt_datetime-now_datetime).total_seconds()

        if msg:
            total_sec , final_sec = self._get_total_and_final_sec(tot_seconds, nxt_datetime)
            self.custom.debug.msg('every seconds',f"s ({value})", total_sec, final_sec,back=None)
        return tot_seconds  




if __name__=="__main__":
    from Qperiodic.utils.logger_color import ColorLog
    logg = ColorLog('main', 'green')
    cust = CustomLog(logg,'async')

    # --------------------------------- core --------------------------------- #
    # print(_core.now_stamp())
    # print(_core.now_naive())
    # print(_core.now_naive('UTC'))
    # --------------------------------- sync --------------------------------- #
    # sync = Sync(cust)

    # --------------------------------- evry --------------------------------- #
    # every = Every(cust)
    # every.minute_at_seconds(10,'KST')
    # every.hour_at_minutes(57,'KST')
    # every.day_at_hours(10,'KST')

    # every.seconds(5,'KST')
    # every.minutes(60,'KST')
    # every.hours(5,'KST')

    # get_total_seconds = every.wrapper('minute_at_seconds',5,'KST')
    # get_total_seconds()
    # # evry.hours(24,'KST')
    
    # --------------------------------- Timer -------------------------------- #
    timer = Timer(logg)

    # timer.get_offset(msg=True)
    # timer.now_naive(msg=True)
    # timer.now_stamp(msg=True)

    timer.run_daemon_thread('seconds',3,'KST',True)

    for i in range(20):
        time.sleep(1)
        timer.get_offset(msg=True)