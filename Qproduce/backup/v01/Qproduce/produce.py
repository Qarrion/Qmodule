from Qproduce.tools.timer import Timer
from Qproduce.tools.nowst import Nowst
from typing import Literal, Callable, List
import logging, asyncio

from Qproduce.utils.logger_custom import CustomLog

class Core:
    offset:float = 0.0
    buffer:float = 0.005
    name:str = 'Produce'

class Produce:
    """ >>> # basic
    prod = Produce()
    at_05_sec = prod.get_timer('minute_at_seconds',55,'KST',True)

    >>> # synchronize offset
    await prod.loop_offset(at_05_sec,msg=True)

    >>> # prod loop_task
    await prod.loop_task(min_at_00_sec,[async_def])

    >>> # peridoic divider (log)
    await prod.loop_divider(min_at_00_sec)

    """
    def __init__(self, logger:logging.Logger = None):
        self.logger = logger
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Consume')
        self._timer = Timer(self.logger)
        self._nowst = Nowst(self.logger)

        self._timer.set_core(Core)
        self._nowst.set_core(Core)
        self._div_divider()

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
    #                                 Produce                                 #
    # ------------------------------------------------------------------------ #
    # -------------------------------- divider ------------------------------- #
    def _div_divider(self):
        self._timer._dev_divider(offset=Core.offset)

    async def loop_divider(self, timer:Callable):
        """print divider"""
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._adjust_offset_change(tgt_dtm)
            self._div_divider()
            await self._adjust_offset_change(tgt_dtm)

    # ----------------------------- synchronizer ----------------------------- #
    async def loop_offset(self, timer:Callable, msg):
        """synchronize offset"""
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._adjust_offset_change(tgt_dtm)
            await self._nowst.async_offset(msg=msg)
            await self._adjust_offset_change(tgt_dtm)

    # ------------------------------- producer ------------------------------- #
    async def loop_task(self, timer:Callable, async_defs:List[Callable], timeout=None):
        """print task"""
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._adjust_offset_change(tgt_dtm)
            for async_def in async_defs:
                if timeout is None: timeout = 50
                asyncio.create_task(self._await_with_timeout(async_def,timeout))
            await self._adjust_offset_change(tgt_dtm)

    async def _adjust_offset_change(self, tgt_dtm):
        await self._nowst.adjust_offset_change(tgt_dtm)

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
    from Qproduce.utils.logger_color import ColorLog
    log_Produce = ColorLog('prod', 'blue')
    logger_y = ColorLog('work', 'yellow')

    async def work1():
        logger_y.info('worker1 start')
        await asyncio.sleep(1)
        logger_y.info('worker1 end')
    
    # ------------------------------------------------------------------------ #
    #                                 sync test                                #
    # ------------------------------------------------------------------------ #
    # prod =  Produce(log_Produce)
    
    # async def offset():
    #     min_at_00_sec = prod.get_timer('minute_at_seconds',0,'KST',True)
    #     await prod.loop_offset(min_at_00_sec,msg=False)

    # async def main():
    #     task_offset = asyncio.create_task(offset())
    #     await task_offset

    # asyncio.run(main())
    # ------------------------------------------------------------------------ #
    #                                   async                                  #
    # ------------------------------------------------------------------------ #
    # prod =  Produce(log_Produce)
    # async def divide():
        # min_at_10_sec = prod.get_timer('minute_at_seconds',10,'KST',True)
        # await prod._div_divider(min_at_10_sec)

    # async def produce():
    #     min_at_00_sec = prod.get_timer('minute_at_seconds',0,'KST',True)
    #     await prod.producer(min_at_00_sec,[work1])


    # async def offset():
    #     min_at_55_sec = prod.get_timer('minute_at_seconds',55,'KST',True)
    #     await prod.synchzr(min_at_55_sec,msg=False)


    # async def main():
        # task_liner = asyncio.create_task(divide())
        # task_produce = asyncio.create_task(produce())
        # task_offset = asyncio.create_task(offset())
        # await asyncio.gather(task_produce, task_offset, task_liner)

    # asyncio.run(main())

    # ------------------------------------------------------------------------ #
    #                                   test                                   #
    # ------------------------------------------------------------------------ #
    prod =  Produce(log_Produce)
    # prod._div_divider()
    async def divide():
        # min_at_10_sec = prod.get_timer('every_seconds',2,'KST',True)
        every_min = prod.get_timer('minute_at_seconds',0,'KST',False)
        await prod.loop_divider(every_min)
    async def main():
        task_liner = asyncio.create_task(divide())
        await asyncio.gather(task_liner)
    asyncio.run(main())