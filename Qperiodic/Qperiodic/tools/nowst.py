
from Qperiodic.utils.logger_custom import CustomLog

from typing import Literal, Callable
from functools import partial
from datetime import datetime
import time, traceback, threading, logging
import ntplib, pytz

class _core:
    offset:float = 0.0

    timezone = {
    "KST":pytz.timezone('Asia/Seoul'),
    "UTC":pytz.timezone('UTC')}

    @classmethod
    def now_stamp(cls)->float:
        """with offset"""
        now_timestamp = time.time() + _core.offset
        # now_timestamp = time.time() + _core.offset - _core.buffer
        return now_timestamp

    @classmethod
    def now_naive(cls, tz:Literal['KST','UTC']='KST')->datetime:
        """return naive"""
        now_timestamp = _core.now_stamp()
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=_core.timezone[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        return now_datetime_naive

class Nowst:
    """>>> #
    nowst = Nowst()

    nowst.fetch_offset()
    print(nowst.now_naive())
    print(nowst.now_stamp())

    nowst.start_daemon_thread(lambda:1)
    time.sleep(5)

    core = nowst.core()
    print(core.now_naive())
    print(core.now_stamp())
    """
    server_list = ["pool.ntp.org","kr.pool.ntp.org","time.windows.com" "time.nist.gov","ntp.ubuntu.com"]
    
    def __init__(self, logger:logging.Logger=None):
        self.custom = CustomLog(logger,'sync')
        self.custom.info.msg('Nowst')
        _core.offset = self.fetch_offset(msg=True, init=True)

    def core(self):
        return _core

    def now_stamp(self)->float:
        return _core.now_stamp()
    
    def now_naive(self, tz:Literal['KST','UTC']='KST')->datetime:
        return _core.now_naive(tz)

    def fetch_offset(self, msg=True, init=False):
        min_offset = None
        for server in self.server_list:
            try:
                response = self._fetch_NTPStats(server)
                if init: self._debug_response(response, server)
                offset = response.offset
                if min_offset is None :
                    min_offset, min_server = offset, server
                else :
                    if offset < min_offset:
                        min_offset, min_server = offset, server
            except Exception as e:
                pass

        if msg: self.custom.info.msg('min',f"{min_offset:.6f}", min_server)
        return min_offset

    def start_daemon_thread(self, timer:Callable=None, msg=True):
        """+ sync current time on background process (offset for now)
        + timer(Callable) return seconds to next synchronization
        """
        if timer is None: timer = lambda: 60

        def worker():
            while True:
                try:
                    time.sleep(timer())
                    _core.offset = self.fetch_offset(msg=msg)
                except Exception as e:
                    print(str(e))
                    traceback.print_exc()
                    time.sleep(1)
    
        daemon_thread = threading.Thread(name='BackGround',target=worker, daemon=True)
        daemon_thread.start()    

    def _dev_check_offset(self):
        for server in self.server_list:
            try:
                response = self._fetch_NTPStats(server)
                self._debug_response(response, server)
            except Exception as e:
                pass       

    def _fetch_NTPStats(self, server)->ntplib.NTPStats:
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return response

    def _debug_response(self, response, server):
        tsp_offset = response.offset
        kst_server = datetime.fromtimestamp(response.tx_time, tz=_core.timezone['KST'])
        kst_local = datetime.fromtimestamp(time.time(), tz=_core.timezone['KST'])
        print(f"  + offset({tsp_offset:.6f}) ::: server({kst_server}) - local({kst_local}) [{server}]")

if __name__=="__main__":
    from Qperiodic.utils.logger_color import ColorLog
    logg = ColorLog('main', 'green')
    nowst = Nowst(logg)

    # --------------------------------- nowst -------------------------------- #
    # nowst.fetch_offset()
    # print(nowst.now_naive())
    # print(nowst.now_stamp())

    # nowst.start_daemon_thread(lambda:1)
    # time.sleep(5)

    # --------------------------------- core --------------------------------- #
    core = nowst.core()
    print(core.now_naive())
    print(core.now_stamp())
