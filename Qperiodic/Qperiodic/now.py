from datetime import datetime
from typing import Literal
import ntplib
import pytz
import time
import threading
from Qperiodic.tools.every import Every
from Qperiodic.utils.log_custom import CustomLog
import logging



class Now:
    """>>> #
    now.run_synchronize_thread(every='minute', at=0)
    now.fetch_timestamp()
    now.fetch_datetime()
    """

    tz_dict = {"KST":pytz.timezone('Asia/Seoul'),"UTC":pytz.timezone('UTC')}
    server_list = ["pool.ntp.org","time.windows.com" "time.nist.gov","ntp.ubuntu.com"]
    
    def __init__(self, logger:logging.Logger=None):
        self.custom = CustomLog(logger,'async')
        self.offset = self._fetch_offset()
    
    def run_synchronize_thread(self,every:Literal['minute','hour','day']='minute', at:int=0,):
        self.get_seconds_to_next_sync = Every().wrapper(every=every, at=at)
        self.thread_daemon = threading.Thread(target=self._synchronize_loop, daemon=True)
        self.thread_daemon.start()

    def fetch_timestamp(self):
        return time.time() + self.offset

    def fetch_datetime(self, tz:Literal['KST','UTC']='KST'):
        """timezone naive"""
        nowts = self.fetch_timestamp()
        timezone = self.tz_dict[tz]
        now = datetime.fromtimestamp(nowts,tz=timezone)     # aware
        now = now.replace(tzinfo=None)                      # naive
        return now


    # ------------------------------------------------------------------------ #
    #                                   inner                                  #
    # ------------------------------------------------------------------------ #
    def _synchronize_loop(self):
        while True:
            try:
                sec = self.get_seconds_to_next_sync()        
                time.sleep(sec)
                self.offset = self._fetch_offset()
                time.sleep(1) # buffer
            except:
                time.sleep(1) 

    def _fetch_offset(self):
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
        self.custom.info.msg('ok',msg)
        return rslt
            
    def _fetch_NTPStats(self, server):
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return response
    # ------------------------------------------------------------------------ #

if __name__ == "__main__":
    from Qlogger import Logger
    logger=Logger('test','head')
    now = Now(logger=logger)
    print(now.fetch_datetime())
    print(now.fetch_timestamp())

    
    time.sleep(5)
    print('end')
