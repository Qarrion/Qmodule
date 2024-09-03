# -------------------------------- ver 240511 -------------------------------- #
# tools
from Qlogger import Logger

from typing import Literal
from datetime import datetime, timedelta
import time, traceback, logging, asyncio
import ntplib, pytz

class _core:
    offset:float = 0.0
    buffer:float = 0.0
    name:str = 'default'

class Nowst:
    """>>> # basic
    nowst = Nowst()
    nowst.now_naive()
    nowst.now_stamp()
    nowst.now_kst(msg=True)

    >>> # synchronize
    nowst.fetch_offset()
    await nowst.xsync_offset()
    await nowst.xadjust(tgt)

    >>> # core (default)
    nowst.set_core(_core)
    class _core:
        offset = 0.0
        buffer = 0.0
        whoami = 'default'
    """
    timezone = {
        "KST":pytz.timezone('Asia/Seoul'),
        "UTC":pytz.timezone('UTC')}
    
    server_list = ["pool.ntp.org","kr.pool.ntp.org","ntp.ubuntu.com"]
    # server_list = ["pool.ntp.org","kr.pool.ntp.org","time.windows.com","time.nist.gov","ntp.ubuntu.com"]
    

    def __init__(self, name:str='nowst'):
        self._logger = Logger(name,clsname='Nowst',context='async')
        self.set_core(_core, msg=False)

    def set_core(self, core, msg=False):
        self.core = core 
        self._core_name = self.core.name if hasattr(self.core, 'name') else 'none'

        offset = f"OFF({self.core.offset:+.3f})"
        buffer = f"BUF({self.core.buffer:+.3f})"
        
        if msg: self._logger.info.msg(f"Core({self._core_name})",offset,buffer)
        
    def now_stamp(self, msg=False)->float:
        """with offset"""
        now_local = time.time()
        now_stamp = now_local + self.core.offset
        if msg: self._logger.debug.msg(f"Server({now_stamp:.5f})",widths=(3),  offset=self.core.offset)
        return now_stamp
    
    def now_naive(self, tz:Literal['KST','UTC']='KST', msg=False)->datetime:
        """return naive"""
        now_timestamp = self.now_stamp()
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=self.timezone[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        if msg: self._logger.debug.msg(f"Server({now_datetime_naive})",widths=(3), offset=self.core.offset)
        # if msg: self._custom.debug.msg(f"offset ({self._core.offset:+.6f})", f"Server({now_datetime_naive})", frame=None,offset=self._core.offset)
        return now_datetime_naive
    
    def now_kst(self, tz:Literal['KST','UTC']='KST', msg=False)->datetime:
        """return naive"""
        now_timestamp = self.now_stamp()
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=self.timezone[tz]) 
        if msg: self._logger.debug.msg(f"Server({now_datetime})",widths=(3), offset=self.core.offset)
        # if msg: self._custom.debug.msg(f"offset ({self._core.offset:+.6f})", f"Server({now_datetime_naive})", frame=None,offset=self._core.offset)
        return now_datetime

    def fetch_offset(self, msg=False, msg_debug=False):
        """
        + msg : INFO @    main . __init__.....Nowst | 
        + debug : + offset(float) = server(datetime) - local(datetime) [url]
        """
        min_offset = float('inf')
        for server in self.server_list:
            try:
                response = self._fetch_NTPStats(server)
                if msg_debug: self._debug_response(response, server)
                offset = response.offset
                if abs(offset) < abs(min_offset):
                    min_offset, min_server = offset, server
            except Exception as e:
                pass

        if min_offset == float('inf') : min_offset,min_server = self.core.offset, 'Na'
        if msg: self._logger.info.msg(f"{min_offset:.6f}", min_server,widths=(1,2), offset=self.core.offset)
        return min_offset

    def sync_offset(self, msg=True, to_thread=False):
        
        pre_offset = self.core.offset
        new_offset = (self.fetch_offset() + self.fetch_offset())/2
        self.core.offset = new_offset
        dif_offset = new_offset - pre_offset
        msg_offset = (f"pre({pre_offset:+.4f})",f"new({new_offset:+.4f})",f"dif({dif_offset:+.4f})")
        if msg : 
            if to_thread:
                self._logger.info.msg(*msg_offset,offset=self.core.offset,fname='xsync_offset')
                self._warning_default_core('nowst.xsync_offset()')
            else:
                self._logger.info.msg(*msg_offset,offset=self.core.offset)
                self._warning_default_core('nowst.sync_offset()')

    # ------------------------------------------------------------------------ #
    #                                   async                                  #
    # ------------------------------------------------------------------------ #
    async def xsync_offset(self,msg=False):
        try:
            await asyncio.wait_for(asyncio.to_thread(self.sync_offset,msg,True),10)
        except Exception as e:
            print(str(e))
            traceback.print_exc()

    async def xadjust(self,target_dtime:datetime, msg=True)->float:
        """sleep when if now_datetime(with offset) - target_datetime > core.buffer:
        + target_dtime : aware"""
        now_dtm = self.now_kst() 
        dif_sec = (target_dtime-now_dtm).total_seconds()

        if dif_sec > self.core.buffer:
            adjust_sec = dif_sec 
            if msg : 
                adjust = f"ADJ({adjust_sec:+.3f})"
                buffer = f"BUF({self.core.buffer:+.3f})"
                self._logger.debug.msg('xadjust', adjust,  buffer, offset=self.core.offset)
            await asyncio.sleep(adjust_sec)

    # ------------------------------------------------------------------------ #
    #                                   debug                                  #
    # ------------------------------------------------------------------------ #

    def _warning_default_core(self, where):
        if hasattr(self.core, 'name'):
            if self.core.name == 'default':
                print(f"\033[31m [Warning in '{where}'] core has not been set! \033[0m")

    def _dev_divider(self,offset=None):
        self._custom.info.div(offset)

    def _dev_check_offset(self):
        for server in self.server_list:
            try:
                response = self._fetch_NTPStats(server)
                self._debug_response(response, server)
            except Exception as e:
                self._debug_response(None, server)
     
    def _fetch_NTPStats(self, server)->ntplib.NTPStats:
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return response

    def _debug_response(self, response, server):
        #! fstring :+
        if response is None:
            kst_server = 'None'
            tsp_offset = 0.0
            sign = '-'
        else:
            tsp_offset = response.offset
            kst_server = datetime.fromtimestamp(response.tx_time, tz=self.timezone['KST'])
            sign = '+'

        kst_local = datetime.fromtimestamp(time.time(), tz=self.timezone['KST'])
        print(f"  {sign} offset({tsp_offset:+.6f}) = server({kst_server}) - local({kst_local}) [{server}]")

if __name__=="__main__":

    nowst = Nowst()
    # --------------------------------- base --------------------------------- #
    nowst._dev_divider()
    nowst._dev_check_offset()
    nowst.now_stamp(True)
    nowst.now_naive(msg=True)
    # --------------------------------- nowst -------------------------------- #
    # nowst._dev_divider()
    nowst.fetch_offset(msg=True,msg_debug=True)
    nowst.fetch_offset(False)

    # # --------------------------------- async -------------------------------- #
    # nowst._dev_divider()
    # async def main():
    #     await nowst.xsync_offset(msg=False)


    # asyncio.run(main())
    # # --------------------------------- core --------------------------------- #
    nowst._dev_divider()
    class _core:
        offset = 0.0
        buffer = 0.0
        name = 'test'

    async def main():
        nowst.set_core(_core)
        await nowst.xsync_offset(msg=False)


    asyncio.run(main())