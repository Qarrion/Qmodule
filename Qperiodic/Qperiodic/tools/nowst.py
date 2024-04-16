
from math import inf
from Qperiodic.utils.logger_custom import CustomLog

from typing import Literal, Callable
from functools import partial
from datetime import datetime
import time, traceback, threading, logging
import ntplib, pytz


class _core:
    offset:float = 0.0
    buffer:float = 0.02
    name:str = 'default'

class Nowst:
    """>>> # synchronize
    nowst = Nowst()
    nowst.now_naive()
    nowst.now_stamp()
    nowst.fetch_offset()
    nowst.start_daemon_thread(timer=None)


    >>> # core (default)
    class _core:
        offset = 0
        buffer = 0.02
        whoami = 'default'

    nowst.set_core(_core)
    """
    timezone = {
        "KST":pytz.timezone('Asia/Seoul'),
        "UTC":pytz.timezone('UTC')}
    server_list = ["pool.ntp.org","kr.pool.ntp.org","time.windows.com" "time.nist.gov","ntp.ubuntu.com"]
    
    def __init__(self, logger:logging.Logger=None):
        self._custom = CustomLog(logger,'sync')
        self._custom.info.msg('Nowst')
        self._core = _core
        self._core.offset = self.fetch_offset(msg=True, debug=False)

    def set_core(self, core):
        #! core backup process
        temp_offset = self._core.offset
        self._core = core 
        self._core.offset = temp_offset
        name = self._core.name if hasattr(self._core, 'name') else 'none'
        offset = f"OFF({self._core.offset:+.3f})"
        buffer = f"BUF({self._core.buffer:+.3f})"
        self._custom.info.msg('name',f"({name})",offset,buffer)

    def now_stamp(self, msg=False)->float:
        """with offset"""
        now_local = time.time()
        now_stamp = now_local + self._core.offset
        if msg: self._custom.debug.msg(f"offset ({self._core.offset:+.6f})", f"L({now_local:.5f})",f"S({now_stamp:.5f})", back=None)
        return now_stamp
    
    def now_naive(self, tz:Literal['KST','UTC']='KST', msg=False)->datetime:
        """return naive"""
        now_timestamp = self.now_stamp()
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=self.timezone[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        if msg: self._custom.debug.msg(f"offset ({self._core.offset:+.6f})", f"Server({now_datetime_naive})", back=None)
        return now_datetime_naive

    def fetch_offset(self, msg=True, debug=False):
        min_offset = float('inf')
        for server in self.server_list:
            try:
                response = self._fetch_NTPStats(server)
                if debug: self._debug_response(response, server)
                offset = response.offset
                if offset < min_offset:
                    min_offset, min_server = offset, server
            except Exception as e:
                pass

        if min_offset == float('inf') : min_offset,min_server = self._core.offset, 'Na'
        if msg: self._custom.info.msg('min',f"{min_offset:.6f}", min_server)
        return min_offset

    def _warning_default_core(self):
        if hasattr(self._core, 'name'):
            if self._core.name == 'default':
                print('\033[31m [Warning] core has not been set! ::: nowst.set_core(core) \033[0m')

    def _default_timer(self):
        return 5, datetime.now()

    def start_daemon_thread(self, timer:Callable=None, msg=True):
        """+ sync current time on background process (offset for now)
        + timer(Callable) return seconds to next synchronization
        """
        self._warning_default_core()
        repeat_timer  = timer if timer is not None else self._default_timer

        def worker():
            while True:
                tot_sec, tgt_dtm = repeat_timer() 
                
                try:
                    time.sleep(tot_sec)
                    self._core.offset = self.fetch_offset(msg=msg)

                except Exception as e:
                    print(str(e))
                    traceback.print_exc()
                    time.sleep(1)

                finally:
                    #! just a bit short exception
                    if (now_sec := self.now_naive()) < tgt_dtm:
                        buf_sec = (tgt_dtm-now_sec).total_seconds()+0.002
                        time.sleep(buf_sec)

    
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
        #! fstring :+
        tsp_offset = response.offset
        kst_server = datetime.fromtimestamp(response.tx_time, tz=self.timezone['KST'])
        kst_local = datetime.fromtimestamp(time.time(), tz=self.timezone['KST'])
        print(f"  + offset({tsp_offset:+.6f}) = server({kst_server}) - local({kst_local}) [{server}]")

if __name__=="__main__":
    from Qperiodic.utils.logger_color import ColorLog
    logg = ColorLog('main', 'green')
    nowst = Nowst(logg)

    # --------------------------------- nowst -------------------------------- #
    # nowst.fetch_offset()
    # nowst.now_stamp(True)
    # nowst.now_naive(msg=True)

    # nowst.start_daemon_thread()
    # for _ in range(20):
    #     time.sleep(1)
    #     print(nowst._core.offset)

    # --------------------------------- core --------------------------------- #
    class _core:
        offset = 0
        buffer = 0.02
        name = 'test'
    nowst.set_core(_core)

    nowst.start_daemon_thread()
    for _ in range(20):
        time.sleep(1)
        print(nowst._core.offset)