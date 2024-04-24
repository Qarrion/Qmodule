import asyncio

from Qperiodic.tools.timer import Timer
from Qperiodic.tools.nowst import Nowst

import logging
from typing import Literal, Coroutine, Callable, List
import signal
import time

class Core:
    offset:float = 0.0
    buffer:float = 0.005
    name:str = 'periodic'

class Periodic:
    """ >>> # basic
    periodic = Periodic()
    at_05_sec = periodic.get_timer('minute_at_seconds',55,'KST',True)

    >>> # synchronize asyncio
    await periodic.asyncio_sync_offset(at_05_sec,msg=True)

    >>> # periodic producer
    await periodic.producer(min_at_00_sec,[async_def])

    >>> # peridoic divider (log)
    await periodic.divider(min_at_00_sec)

    """
    def __init__(self, logger:logging.Logger = None):
        self.logger = logger
        
        self._nowst = Nowst(self.logger)
        self._timer = Timer(self.logger)

        self._nowst.set_core(Core)
        self._timer.set_core(Core)
        self.msg_divider()

    def _signal_handler(self, sig, frame):
        print('Ctrl + C Keyboard Interrupted')
        self._stop_event.set()

    # ------------------------------------------------------------------------ #
    #                                synchronize                               #
    # ------------------------------------------------------------------------ #
    def get_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        """ get timer preset"""
        return self._timer.wrapper(every,at,tz,msg)

    # -------------------------------- Asyncio ------------------------------- #
    async def synchronize_offset(self, timer:Callable, msg=True):
        """msg : @ fetch_offset...min """
        await self._nowst.sync_offset(timer,msg=msg)

    # ------------------------------------------------------------------------ #
    #                                 periodic                                 #
    # ------------------------------------------------------------------------ #
    # -------------------------------- divider ------------------------------- #
    def msg_divider(self):
        self._timer.msg_divider(offset=Core.offset)

    async def divider(self, timer:Callable):
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            self.msg_divider()
            await self._adjust_offset_chagne(tgt_dtm)

            # if (now_sec := self._nowst.now_naive(msg=False)) < tgt_dtm:
            #     buf_sec = (tgt_dtm-now_sec).total_seconds() + Core.buffer
            #     self._nowst._dev_sleep_buffer(buf_sec)
            #     await asyncio.sleep(buf_sec)

    # ----------------------------- synchronizer ----------------------------- #
    async def synchzr(self, timer:Callable, msg):
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._adjust_offset_chagne(tgt_dtm)
            await self._nowst.async_offset(msg=msg)
            await self._adjust_offset_chagne(tgt_dtm)

    # ------------------------------- producer ------------------------------- #
    async def producer(self, timer:Callable, async_defs:List[Callable], timeout=None):
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._adjust_offset_chagne(tgt_dtm)
            for async_def in async_defs:
                if timeout is None: timeout = 50
                asyncio.create_task(self._await_with_timeout(async_def,timeout))
            await self._adjust_offset_chagne(tgt_dtm)

    async def _adjust_offset_chagne(self, tgt_dtm):
        await self._nowst.adjust_offset_chagne(tgt_dtm)

    async def _await_with_timeout(self, async_def:Callable, timeout:int):
        try:
            await asyncio.wait_for(async_def(), timeout)

        except asyncio.TimeoutError:
            print(f'Timeout!')

        except Exception as e:
            print(str(e))
            print(e.__class__.__name__)


if __name__ == "__main__":
    # ------------------------------------------------------------------------ #
    #                                   base                                   #
    # ------------------------------------------------------------------------ #
    from Qlogger import Logger

    logger_g = Logger('newst', 'green')
    log_periodic = Logger('perio', 'blue')
    logger_y = Logger('work', 'yellow')

    async def work1():
        logger_y.info('worker1 start')
        await asyncio.sleep(1)
        logger_y.info('worker1 end')

    # perio =  Periodic(log_periodic)
    # min_at_00_sec = perio.get_timer('minute_at_seconds',0,'KST',True)
    # tot_sec, tgt_dtm = min_at_00_sec()
    # time.sleep(tot_sec)
    # perio._divider()
    # perio._nowst.seconds_to_adjust(tgt_dtm)


    # ------------------------------------------------------------------------ #
    #                                 sync test                                #
    # ------------------------------------------------------------------------ #
    # perio =  Periodic(log_periodic)

    # async def offset():
    #     min_at_00_sec = perio.get_timer('minute_at_seconds',0,'KST',True)
    #     await perio.synchzr(min_at_00_sec,msg=False)

    # async def main():
    #     task_offset = asyncio.create_task(offset())
    #     await task_offset

    # asyncio.run(main())
    # ------------------------------------------------------------------------ #
    #                                   async                                  #
    # ------------------------------------------------------------------------ #
    perio =  Periodic(log_periodic)

    async def divide():
        min_at_10_sec = perio.get_timer('minute_at_seconds',10,'KST',True)
        await perio.divider(min_at_10_sec)

    async def produce():
        min_at_00_sec = perio.get_timer('minute_at_seconds',0,'KST',True)
        await perio.producer(min_at_00_sec,[work1])


    async def offset():
        min_at_55_sec = perio.get_timer('minute_at_seconds',55,'KST',True)
        await perio.synchzr(min_at_55_sec,msg=False)


    async def main():
        task_liner = asyncio.create_task(divide())
        task_produce = asyncio.create_task(produce())
        task_offset = asyncio.create_task(offset())
        await asyncio.gather(task_produce, task_offset, task_liner)

    asyncio.run(main())
