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
    """ + server time = local time + Core.offset
    
    >>> # basic
    prod = Produce(logger)
    at_05_sec = prod.get_timer('minute_at_seconds',55,'KST',True)

    >>> # synchronize offset
    prod1 = Produce(logger)
    prod1.set_timer('minute_at_seconds',55)
    await prod1.loop_offset()

    >>> # peridoic divider
    prod2 = Produce(logger)
    prod2.set_timer('minute_at_seconds',0)
    await prod.loop_divider()

    >>> # prod loop_task
    prod3 = Produce(logger)
    await prod3.loop_produce([async_def1, async_def2])


    """
    def __init__(self, logger:logging.Logger = None):
        self._custom = CustomLog(logger,'async')
        self._custom.info.msg('Produce')
        self._timer = Timer(logger)
        self._nowst = Nowst(logger, init_offset= False)

        self._timer.set_core(Core)
        self._nowst.set_core(Core)

        self.msg_divider()
        self.timer=None
        self.works=None

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

    def set_timer(self, every:Literal['minute_at_seconds','hour_at_minutes','day_at_hours',
                                    'every_seconds','every_minutes','every_hours'], 
                at:float=5, tz:Literal['KST','UTC']='KST',msg=True):
        self.timer = self.get_timer(every,at,tz,msg)

    # ------------------------------------------------------------------------ #
    #                                  common                                  #
    # ------------------------------------------------------------------------ #
    def set_works(self, async_defs:List[Callable]):
        self.works = async_defs
    # ------------------------------------------------------------------------ #
    #                                 Produce                                 #
    # ------------------------------------------------------------------------ #
    # -------------------------------- divider ------------------------------- #
    def msg_divider(self):
        self._timer._dev_divider(offset=Core.offset)

    async def loop_divider(self):
        """print divider"""
        timer = self.timer
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._xadjust_offset(tgt_dtm)
            self.msg_divider()
            await self._xadjust_offset(tgt_dtm)

    # ----------------------------- synchronizer ----------------------------- #
    async def loop_settime(self):
        """+ synchronize offset"""
        self._nowst.sync_offset()
        timer = self.timer
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._xadjust_offset(tgt_dtm)
            await self._nowst.xsync_offset()
            await self._xadjust_offset(tgt_dtm)

    # ------------------------------- producer ------------------------------- #

    async def loop_produce(self, async_defs:List[Callable], timeout=None):
        """print task"""

        timer = self.timer
        while True:
            tot_sec, tgt_dtm = timer() 
            await asyncio.sleep(tot_sec)
            await self._xadjust_offset(tgt_dtm)
            for async_def in async_defs:
                if timeout is None: timeout = 50
                self._custom.msg('task', async_def.__name__, frame='produce', offset=Core.offset)
                asyncio.create_task(self._await_with_timeout(async_def,timeout))
            await self._xadjust_offset(tgt_dtm)

    async def _xadjust_offset(self, tgt_dtm):
        await self._nowst.xadjust_offset_change(tgt_dtm)

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
    log_blue = ColorLog('prod', 'blue')
    # log_green = ColorLog('prod', 'green')
    logger_y = ColorLog('work', 'yellow')

    async def work1():
        logger_y.info('worker1 start')
        await asyncio.sleep(1)
        logger_y.info('worker1 end')
    async def work2():
        logger_y.info('worker2 start')
        await asyncio.sleep(1)
        logger_y.info('worker2 end')
    
    # ------------------------------------------------------------------------ #
    #                                 sync test                                #
    # ------------------------------------------------------------------------ #
    prod1 =  Produce(log_blue)
    prod2 =  Produce(log_blue)
    prod3 =  Produce(log_blue)

    prod1.set_timer('minute_at_seconds',55)
    prod2.set_timer('minute_at_seconds',0)
    prod3.set_timer('minute_at_seconds',10)
    
    async def produce():
        task1 = asyncio.create_task(prod1.loop_settime())
        task2 = asyncio.create_task(prod2.loop_divider())
        task3 = asyncio.create_task(prod3.loop_produce([work1, work2]))
        await asyncio.gather(task1, task2, task3)

    asyncio.run(produce())


