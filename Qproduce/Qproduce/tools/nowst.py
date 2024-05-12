from Qproduce.utils.logger_custom import CustomLog

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

    >>> # synchronize
    nowst.fetch_offset()
    await nowst.async_offset(timer=None)

    >>> # core (default)
    nowst.set_core(_core)
    class _core:
        offset = 0
        buffer = 0.02
        whoami = 'default'
    """
    timezone = {
        "KST":pytz.timezone('Asia/Seoul'),
        "UTC":pytz.timezone('UTC')}
    server_list = ["pool.ntp.org","kr.pool.ntp.org","ntp.ubuntu.com"]
    # server_list = ["pool.ntp.org","kr.pool.ntp.org","time.windows.com","time.nist.gov","ntp.ubuntu.com"]
    
    def __init__(self, logger:logging.Logger=None, init_offset=True):
        self._custom = CustomLog(logger,'sync')
        self._frame = '<nowst>'
        # self._custom.info.msg(self._frame)

        self._core = _core
        if init_offset :
            self._core.offset = self.fetch_offset(msg=True, debug=False)

    def set_core(self, core, msg=False):
        temp_offset = self._core.offset
        self._core = core 
        self._core.offset = temp_offset
        name = self._core.name if hasattr(self._core, 'name') else 'none'
        offset = f"OFF({self._core.offset:+.3f})"
        buffer = f"BUF({self._core.buffer:+.3f})"
        
        if msg: self._custom.info.msg('set_core',f"({name})",offset,buffer,frame=self._frame)
        
    def now_stamp(self, msg=False)->float:
        """with offset"""
        now_local = time.time()
        now_stamp = now_local + self._core.offset
        if msg: self._custom.debug.msg(f"stamp", f"L({now_local:.5f})",f"S({now_stamp:.5f})", frame=self._frame, offset=self._core.offset)
        # if msg: self._custom.debug.msg(f"offset ({self._core.offset:+.6f})", f"L({now_local:.5f})",f"S({now_stamp:.5f})", frame=self._frame, offset=self._core.offset)
        return now_stamp
    
    def now_naive(self, tz:Literal['KST','UTC']='KST', msg=False)->datetime:
        """return naive"""
        now_timestamp = self.now_stamp()
        now_datetime = datetime.fromtimestamp(now_timestamp,tz=self.timezone[tz]) 
        now_datetime_naive = now_datetime.replace(tzinfo=None)
        if msg: self._custom.debug.msg(f"naive", f"Server({now_datetime_naive})", offset=self._core.offset,frame=self._frame)
        # if msg: self._custom.debug.msg(f"offset ({self._core.offset:+.6f})", f"Server({now_datetime_naive})", frame=None,offset=self._core.offset)
        return now_datetime_naive

    def fetch_offset(self, msg=False, debug=False):
        """
        + msg : INFO @    main . __init__.....Nowst | 
        + debug : + offset(float) = server(datetime) - local(datetime) [url]
        """
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
        if msg: self._custom.info.msg('offset',f"{min_offset:.6f}", min_server, offset=self._core.offset, frame=self._frame)
        return min_offset

    def sync_offset(self, msg=True):
        self._warning_default_core('nowst.sync_offset()')
        pre_offset = self._core.offset
        new_offset = self.fetch_offset()
        self._core.offset = new_offset
        dif_offset = new_offset - pre_offset
        msg_offset = (f"pre({pre_offset:+.4f})",f"new({new_offset:+.4f})",f"dif({dif_offset:+.4f})")
        if msg : self._custom.info.msg('sync',*msg_offset,offset=self._core.offset, frame=self._frame)

    def _warning_default_core(self, where):
        if hasattr(self._core, 'name'):
            if self._core.name == 'default':
                print(f"\033[31m [Warning in '{where}'] limiter has not been set! \033[0m")

    def _default_timer(self):
        return 5, datetime.now() + timedelta(seconds=5)
    # ------------------------------------------------------------------------ #
    #                                   async                                  #
    # ------------------------------------------------------------------------ #

    async def xsync_offset(self,msg=False):
        self._warning_default_core('nowst.async_offset()')
        # loop = asyncio.get_running_loop()
        try:
            pre_offset = self._core.offset
            # new_offset = await asyncio.wait_for(loop.run_in_executor(None,self.fetch_offset,msg),10)
            new_offset = await asyncio.wait_for(asyncio.to_thread(self.fetch_offset,False, False),10)
            self._core.offset = new_offset
            dif_offset = new_offset - pre_offset
            msg_offset = (f"pre({pre_offset:+.4f})",f"new({new_offset:+.4f})",f"dif({dif_offset:+.4f})")
            self._custom.info.msg('xsync',*msg_offset,offset=self._core.offset,frame=self._frame)
        except Exception as e:
            print(str(e))
            traceback.print_exc()

    async def xadjust_offset_change(self,tgt_dtm:datetime, msg=True)->float:
        """return seconds when if now_datetime(with offset) - target_datetime > 0:"""
        now_dtm = self.now_naive() 
        dif_sec = (tgt_dtm-now_dtm).total_seconds()

        if dif_sec > self._core.buffer:
            adjust_sec = dif_sec 
            if msg : self._custom.debug.msg('xadjust', f"offset_change",f"s ({adjust_sec:+.4f})", frame=self._frame, offset=self._core.offset)
            await asyncio.sleep(adjust_sec)

    # ------------------------------------------------------------------------ #
    #                                   debug                                  #
    # ------------------------------------------------------------------------ #

    def _dev_divider(self,task=None,offset=None):
        self._custom.info.div(task,offset)

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
    from Qproduce.utils.logger_color import ColorLog
    logg = ColorLog('main', 'green')
    nowst = Nowst(logg)
    # --------------------------------- base --------------------------------- #
    nowst._dev_divider()
    nowst._dev_check_offset()
    nowst.now_stamp(True)
    nowst.now_naive(msg=True)
    # --------------------------------- nowst -------------------------------- #
    nowst._dev_divider()
    nowst.fetch_offset(msg=True,debug=True)
    nowst.fetch_offset(False)

    # --------------------------------- async -------------------------------- #
    nowst._dev_divider()
    async def main():
        rslt = await nowst.xsync_offset(msg=False)
        print(rslt)

    asyncio.run(main())
    # --------------------------------- core --------------------------------- #
    nowst._dev_divider()
    class _core:
        offset = 0.0
        buffer = 0.0
        name = 'test'

    async def main():
        nowst.set_core(_core)
        rslt = await nowst.xsync_offset(msg=False)
        print(rslt)

    asyncio.run(main())