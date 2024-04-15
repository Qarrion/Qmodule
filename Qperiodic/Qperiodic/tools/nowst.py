
from Qperiodic.utils.logger_custom import CustomLog

from typing import Literal, Callable
from functools import partial
from datetime import datetime
import time, traceback, threading, logging
import ntplib, pytz

class _core:
    offset:float = 0.0

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
    timezone = {
        "KST":pytz.timezone('Asia/Seoul'),
        "UTC":pytz.timezone('UTC')}
    server_list = ["pool.ntp.org","kr.pool.ntp.org","time.windows.com" "time.nist.gov","ntp.ubuntu.com"]
    
    def __init__(self, logger:logging.Logger=None):
        self.custom = CustomLog(logger,'sync')
        self.custom.info.msg('Nowst')
        _core.offset = self.fetch_offset(msg=True, init=True)

    @property
    def core(self):
        return _core

    def now_stamp(self, msg=False)->float:
        """with offset"""
        now_local = time.time()
        now_stamp = now_local + _core.offset
        if msg: self.custom.debug.msg(f"offset ({_core.offset:+.6f})", f"L({now_local:.5f})",f"S({now_stamp:.5f})", back=None)
        return now_stamp
    
    def now_naive(self, tz:Literal['KST','UTC']='KST', msg=False)->datetime:
        """return naive"""
        now_timestamp = self.now_stamp()
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=self.timezone[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        if msg: self.custom.debug.msg(f"offset ({_core.offset:+.6f})", f"Server({now_datetime_naive})", back=None)
        return now_datetime_naive

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
        kst_server = datetime.fromtimestamp(response.tx_time, tz=self.timezone['KST'])
        kst_local = datetime.fromtimestamp(time.time(), tz=self.timezone['KST'])
        print(f"  + offset({tsp_offset:+.6f}) = server({kst_server}) - local({kst_local}) [{server}]")
        # if tsp_offset >=0:
        # else:
        #     print(f"  + offset({tsp_offset:.6f}) = server({kst_server}) - local({kst_local}) [{server}]")

if __name__=="__main__":
    from Qperiodic.utils.logger_color import ColorLog
    logg = ColorLog('main', 'green')
    nowst = Nowst(logg)

    # --------------------------------- nowst -------------------------------- #
    nowst.fetch_offset()
    nowst.now_stamp(True)
    nowst.now_naive(msg=True)

    nowst.start_daemon_thread(lambda:1)
    time.sleep(5)

    # --------------------------------- core --------------------------------- #
    core = nowst.core
    print(core.offset)
    # print(core.now_naive())
    # print(core.now_stamp())
