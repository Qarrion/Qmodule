import threading, traceback, time, logging
import ntplib,pytz

from datetime import datetime, timedelta
from functools import partial
from datetime import datetime
from typing import Literal

from Qperiodic.utils.logger_custom import CustomLog

class Timer:
    """>>> #
    timer = Timer()
    timer.run_daemon_thread(every='minute',at=5,tz='KST',add_offset=True)
    timer.now_timestamp(add_offset=True)
    timer.now_datetime(add_offset=True, tz='KST')

    """
    def __init__(self, logger:logging.Logger=None):
        self.custom = CustomLog(logger,'thread')
        self.sync = Sync(self.custom)
        self.next = Next(self.custom)
        self.every = Every(self.custom)
        
    def run_daemon_thread(self, every:Literal['minute','hour','day']='minute', 
                          at:int=5, tz:Literal['KST','UTC']='KST', add_offset=True):
        """every(next) minute at N seconds, hour at N minutes, day at N hours"""
        get_remaining_seconds = self.next.wrapper(every, at, tz, add_offset)
        self.thread_daemon = threading.Thread(name='background',
            target=self._worker, args=(get_remaining_seconds,), daemon=True)
        self.thread_daemon.start()

    def _worker(self, callback_seconds):
        while True:
            try:    
                seconds = callback_seconds()  
                time.sleep(seconds)
                Shared.offset = self.sync.fetch_offset()
                self.sync.check()
                time.sleep(1) 
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                time.sleep(1) 

    def now_timestamp(self, add_offset=True):
        now_timestamp = time.time() 
        now_timestamp += Shared.offset if add_offset else 0
        return now_timestamp

    def now_datetime(self, add_offset=True, tz:Literal['KST','UTC']='KST'):
        """now_datetime_naive"""
        now_timestamp = self.now_timestamp(add_offset)
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=Shared.timezone[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        return now_datetime_naive

class Shared:
    
    offset:float = 0.0
    timezone = {
        "KST":pytz.timezone('Asia/Seoul'),
        "UTC":pytz.timezone('UTC')
        }
    
    @classmethod
    def now_timestamp(self, add_offset=True)->float:
        now_timestamp = time.time() 
        now_timestamp += Shared.offset if add_offset else 0
        return now_timestamp

    @classmethod
    def now_datetime(cls, tz:Literal['KST','UTC']='KST' , add_offset=True)->datetime:
        """return naive"""
        now_timestamp = Shared.now_timestamp(add_offset)
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=Shared.timezone[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        return now_datetime_naive

    @staticmethod
    def fmt_seconds(seconds:float,fmt:Literal['hmsf','ms7f']='hmsf'):
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
    def fmt_datetime(datetime_naive:datetime, fmt:Literal['full','hmsf','ms7f']):
        assert datetime_naive.tzinfo is None, "aware invalid"
        if fmt == 'full':
            formatted_time = datetime_naive.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] # 마지막 세 자리를 제거하여 밀리초(microsecond)를 한 자리만 포함시킵니다.
        elif fmt=='hmsf':
            formatted_time = datetime_naive.strftime('%H:%M:%S.%f')[:-3] # 마지막 세 자리를 제거하여 밀리초(microsecond)를 한 자리만 포함시킵니다.
        elif fmt=='ms7f':
            formatted_time = datetime_naive.strftime(':%S.%f') # 마지막 세 자리를 제거하여 밀리초(microsecond)를 한 자리만 포함시킵니다.

        return formatted_time



class Sync:
    """>>> #
    sync = Sync()
    sync.fetch_offset()
    sync.check()
    """
    server_list = ["pool.ntp.org","kr.pool.ntp.org","time.windows.com" "time.nist.gov","ntp.ubuntu.com"]
    
    def __init__(self, custom:CustomLog):
        self.custom = custom
        self.custom.info.msg('Sync')
        Shared.offset = self.fetch_offset(True)
        # self.check()

    def fetch_offset(self, debug=True):
        max_offset = None
        for server in self.server_list:
            try:
                response = self._fetch_NTPStats(server)
                offset = round(response.offset,7)
                if max_offset is None :
                    max_offset, max_server = offset, server
                else :
                    if offset > max_offset:
                        max_offset, max_server = offset, server

            except Exception as e:
                pass
        if debug: self.custom.info.msg('ok',max_offset, max_server)
        return max_offset
            
    def _fetch_NTPStats(self, server):
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return response

    def check(self):
        t_fmt = "D%d %H:%M:%S.%f"
        for server in self.server_list:
            try:
                response = self._fetch_NTPStats(server)
                tsp_offset = response.offset
                kst_server = datetime.fromtimestamp(response.tx_time, tz=Shared.timezone['KST'])
                kst_local = datetime.fromtimestamp(time.time(), tz=Shared.timezone['KST'])
                str_offset = f"offset({tsp_offset:.6f}) = sever({kst_server.strftime(t_fmt)}) - local({kst_local.strftime(t_fmt)})"
                print(f"{str_offset} | [{server}]")
            except Exception as e:
                pass
            
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
            self.custom.msg('every', 'minute', 'at_seconds', at)
            func = partial(self.minute_at_seconds,at,tz,add_offset)
        elif every == 'hour':
            self.custom.msg('every', 'hour', 'at_minutes', at)
            func = partial(self.hour_at_minutes,at,tz,add_offset)
        elif every == 'day':
            self.custom.msg('every', 'day', 'at_hours', at)
            func = partial(self.day_at_hours,at,tz,add_offset)
        return func

    def minute_at_seconds(self, seconds:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= seconds < 60 , 'invalid seconds'
        now_datetime = Shared.now_datetime(tz=tz, add_offset=add_offset)
        tgt_datetime = now_datetime + timedelta(minutes=1) if now_datetime.second >= seconds else now_datetime
        tgt_datetime = tgt_datetime.replace(second=seconds,microsecond=0)
        total_seconds = (tgt_datetime-now_datetime).total_seconds()
        return total_seconds 
          
    def hour_at_minutes(self, minutes:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= minutes < 60 , 'invalid minutes'
        now_datetime = Shared.now_datetime(tz=tz, add_offset=add_offset)
        tgt_datetime = now_datetime + timedelta(hours=1) if now_datetime.minute >= minutes else now_datetime
        tgt_datetime = tgt_datetime.replace(minute=minutes,second=0,microsecond=0)
        total_seconds = (tgt_datetime-now_datetime).total_seconds()
        return total_seconds       

    def day_at_hours(self, hours:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= hours < 24 , 'invalid hour'
        now_datetime = Shared.now_datetime(tz=tz, add_offset=add_offset)
        tgt_datetime = now_datetime + timedelta(days=1) if now_datetime.hour >= hours else now_datetime
        tgt_datetime = tgt_datetime.replace(hour=hours,minute=0,second=0,microsecond=0)
        total_seconds = (tgt_datetime-now_datetime).total_seconds()
        return total_seconds

class Every:
    def __init__(self, custom:CustomLog):
        self.buffer = timedelta(seconds=0.05)
        self.custom = custom
        self.custom.info.msg('Every')

    def th_hour(self, value:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= value < 24 , 'invalid hour'
        now_datetime = Shared.now_datetime(tz=tz, add_offset=add_offset) + self.buffer
        unit_value_now = now_datetime.hour
        unit_value_nxt = int((unit_value_now/value)+1.0)*value
        nxt_datetime = now_datetime + timedelta(hours=unit_value_nxt - unit_value_now)
        nxt_datetime = nxt_datetime.replace(minute=0, second=0, microsecond=0)
        total_seconds = (nxt_datetime-now_datetime).total_seconds()

        fmt_seconds = Shared.fmt_seconds(total_seconds)
        fmt_datetime = Shared.fmt_datetime(nxt_datetime,'hmsf')
        self.custom.debug.msg('every',f"({value})th hour", fmt_seconds, fmt_datetime)
        return total_seconds  

    def th_minute(self, value:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= value < 60 , 'invalid minutes'
        now_datetime = Shared.now_datetime(tz=tz, add_offset=add_offset) + self.buffer
        unit_value_now = now_datetime.minute
        unit_value_nxt = int((unit_value_now/value)+1.0)*value
        nxt_datetime = now_datetime + timedelta(minutes=unit_value_nxt - unit_value_now)
        nxt_datetime = nxt_datetime.replace(second=0, microsecond=0)
        total_seconds = (nxt_datetime-now_datetime).total_seconds()

        fmt_seconds = Shared.fmt_seconds(total_seconds)
        fmt_datetime = Shared.fmt_datetime(nxt_datetime,'hmsf')
        self.custom.debug.msg('every',f"({value})th min", fmt_seconds,fmt_datetime)
        return total_seconds  

    def th_second(self, value:int, tz:Literal['KST','UTC']='KST', add_offset=True) -> float:
        assert 0 <= value < 60 , 'invalid seconds'
        now_datetime = Shared.now_datetime(tz=tz, add_offset=add_offset) + self.buffer
        _now_datetime = datetime.now()
        unit_value_now = now_datetime.second
        unit_value_nxt = int((unit_value_now/value)+1.0)*value
        nxt_datetime = now_datetime + timedelta(seconds=unit_value_nxt - unit_value_now)
        nxt_datetime = nxt_datetime.replace(microsecond=0)
        total_seconds = (nxt_datetime-now_datetime).total_seconds()

        # # ------------------------------- debug ------------------------------ #
        # print('debug--------------------------------------------')
        # print(f"{add_offset=:}")
        # print(Shared.fmt_datetime(now_datetime,fmt='full'))
        # print('loc',Shared.fmt_datetime(_now_datetime,fmt='ms7f'))
        # print('off',Shared.fmt_seconds(Shared.offset,fmt='ms7f'))
        # print('now',Shared.fmt_datetime(now_datetime,fmt='ms7f'))
        # print('sec',Shared.fmt_seconds(total_seconds,fmt='ms7f'))
        # print('nxt',Shared.fmt_datetime(nxt_datetime,fmt='ms7f'))
        # print('--------------------------------------------debug')
        # # ------------------------------- debug ------------------------------ #

        fmt_seconds = Shared.fmt_seconds(total_seconds)
        fmt_datetime = Shared.fmt_datetime(nxt_datetime,'hmsf')
        self.custom.debug.msg('every',f"({value})th sec", fmt_seconds, fmt_datetime)
        return total_seconds  


if __name__ == "__main__":
    from Qlogger import Logger
    logger = Logger('timer','head')

    timer = Timer(logger)

    # --------------------------------- every -------------------------------- #
    # timer.every.th_hour(5)
    # timer.every.th_minute(5)
    timer.every.th_second(5,add_offset=True)



    # --------------------------------- sync --------------------------------- #
    # timer.sync.check()
    # timer.sync.fetch_offset()

    # --------------------------------- next --------------------------------- #
    # print(timer.next.day_at_hours(5))
    # print(timer.next.hour_at_minutes(5))
    # print(timer.next.minute_at_seconds(5))

    # --------------------------------- timer -------------------------------- #
    # timer.run_daemon_thread('minute',10,'KST',True)
    # for i in range(30):
    #     time.sleep(10)
    #     logger.debug('hi')

    